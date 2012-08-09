# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Copyright (c) 2012 Michael Vella
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are meet:
# 
#  - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#-------------------------------------------------------------------------------

"""
NOTE: This is still at an early test stage. Most of this code
will be completely rewritten.
"""

import neuron
import numpy as np
from neuron import h
import neuroml.loaders as loaders
import os
import moose
  

class NeuronSimulation(object):
    """
    Simulation classes allow an environment to be simulated. The most important
    method in these classes is the run method which calls the underlying
    simulator run loop.

    Objects of this class control a current clamp simulation. Example of use:
    >>> cell = Cell()
    >>> sim = Simulation(cell)
    >>> sim.go()
    >>> sim.show()
    """

    def __init__(self, recording_section, sim_time=1000, dt=0.05, v_init=-60):

        #h.load_file("stdrun.hoc") # Standard run, which contains init and run
        self.recording_section = recording_section
        self.sim_time = sim_time
        self.dt = dt
        self.go_already = False
        self.v_init=v_init

    def set_VClamp(self,dur1=100,amp1=0,dur2=0,amp2=0,dur3=0,amp3=0,):
        """
        Initializes values for a Voltage clamp.

        techincally this is an SEClamp in neuron, which is a
        three-stage current clamp.
        """
        stim = h.SEClamp(self.recording_section(0.5))
        
        stim.rs=0.1
        stim.dur1 = dur1
        stim.amp1 = amp1
        stim.dur2 = dur2
        stim.amp2 = amp2
        stim.dur3 = dur3
        stim.amp3 = amp3

        self.Vstim = stim

    def set_IClamp(self, delay=5, amp=0.1, dur=1000):
        """
        Initializes values for current clamp.
        
        Default values:
          
          delay = 5 [ms]
          amp   = 0.1 [nA]
          dur   = 1000 [ms]
        """
        stim = h.IClamp(self.recording_section(0.5))
        stim.delay = delay
        stim.amp = amp
        stim.dur = dur
        self.stim = stim

    def show(self):
        from matplotlib import pyplot as plt
        if self.go_already:
            x = np.array(self.rec_t)
            y = np.array(self.rec_v)
            plt.plot(x, y)
            #plt.title("Hello World")
            plt.xlabel("Time [ms]")
            plt.ylabel("Voltage [mV]")
            #plt.axis(ymin=-120, ymax=-50)
        else:
            print("""First you have to `go()` the simulation.""")
        plt.show()
    
    def set_recording(self):
        # Record Time
        self.rec_t = h.Vector()
        self.rec_t.record(h._ref_t)
        # Record Voltage
        self.rec_v = h.Vector()
        self.rec_v.record(self.recording_section(0.5)._ref_v)

    def get_recording(self):
        time = np.array(self.rec_t)
        voltage = np.array(self.rec_v)
        return time, voltage

    def go(self, sim_time=None):
        self.set_recording()
        h.dt = self.dt
        h.finitialize(h.E)
        
        h.finitialize(self.v_init)
        neuron.init()
        if sim_time:
            neuron.run(sim_time)
        else:
            neuron.run(self.sim_time)
        self.go_already = True

    def get_tau_eff(self, ip_flag=False, ip_resol=0.01):
        time, voltage = self.get_recording()
        vsa = np.abs(voltage - voltage[0]) #vsa: voltage shifted and absolut
        v_max = np.max(vsa)
        exp_val = (1 - 1 / np.exp(1)) * v_max # 0.6321 * v_max
        ix_tau = np.where(vsa > (exp_val))[0][0] 
        tau = time[ix_tau] - self.stim.delay 
        return tau
  
    def get_Rin(self):
        """
        This function returnes the input resistance.
        """
        _, voltage = self.get_recording()
        volt_diff = max(voltage) - min(voltage)
        Rin = np.abs(float(volt_diff / self.stim.amp))
        return Rin


class SimulatorEnv(object):
    """
    Base class for simulator-specific environments which express
    a model in simulator-specific types.
    """

    def __set_mechanism(sec, mech, mech_attribute, mech_value):
        """
        Insert NMODL ion channels
        """
        for seg in sec:
            setattr(getattr(seg, mech), mech_attribute, mech_value)

    def __init__(self):
        self.segments_sections_dict={}
        self.sections = []

    def import_cell(self,cell):
        raise(NotImplementedError)

   
class NeuronEnv(SimulatorEnv):
    """
    NEURON-simulator environment, loads NeuroML-specified
    model into a NEURON-specific in-memory representation.
    """

    def __init__(self):
        self.segments_sections_dict={}
        self.sections = []

    def import_cell(self,cell):
        #experimental:
        for index,seg in enumerate(cell.morphology):
            section = h.Section()
            section.diam=seg.proximal_diameter #fix
            if seg.length > 0:
                section.L=seg.length
            else:
                section.L=0.1 #temporary hack
           
#           h.pt3dadd(seg.proximal.x,
#                     seg.proximal.y,
#                     seg.proximal.z,
#                     seg.proximal_diameter,
#                     sec = section)
            
            self.segments_sections_dict[seg._index] = section
            self.sections.append(section)

        #connect them all together:
        for i,seg in enumerate(cell.morphology):
            section = self.segments_sections_dict[seg._index]
            try:
                parent_section = self.segments_sections_dict[seg.parent._index]
                section.connect(parent_section)
            except:
                pass

        #this is the component bit...
        for component_segment_pair in cell.morphology._backend.observer.kinetic_components:
            component = component_segment_pair[0]
            segment_index = component_segment_pair[1]
            neuron_section = self.segments_sections_dict[segment_index]
            
            if component.name == 'IClamp':
               stim = h.IClamp(neuron_section(0.5))
               stim.delay = component.delay
               stim.amp = component.amp
               stim.dur = component.dur
               self.stim = stim

            if component.name == 'NMODL':
                print 'inserting ion channel:' + component.name
                neuron_section.insert(component.name)
                for attribute in component.attributes:
                    self.__set_mechanism(neuron_section, 
                                        attribute.name, 
                                        attribute.value)
                           
    @property
    def topology(self):
        print('connected topology:')
        print(h.topology())


class MooseEnv(SimulatorEnv):
    """
    MOOSE-simulator environment

    Loads NeuroML-specified model into a 
    MOOSE-specific in-memory representation.
    """

    def __init__(self):
        self.segments_compartments_dict={}
        self.compartments = []

    def import_cell(self,cell):
        model = moose.Neutral('/model') # This is a container for the model
        
        print('Creating MOOSE compartments:')
        for index,seg in enumerate(cell.morphology):
            print(index)
            compartment = moose.Compartment('/model/' + str(index))
            #temporary, for testing purposes, this information
            #will be extracted from the segments
            compartment.Em = -65e-3 # Leak potential
            compartment.initVm = -65e-3 # Initial membrane potential
            compartment.Rm = 5e9 # Total membrane resistance of the compartment
            compartment.Cm = 1e-12 # Total membrane capacitance of the compartment
            compartment.Ra = 1e6 # Total axial resistance of the compartment

            self.segments_compartments_dict[seg._index] = compartment
            self.compartments.append(compartment)
        
        print('Connecting MOOSE compartments:')
        for i,seg in enumerate(cell.morphology):
            print i
            compartment = self.segments_compartments_dict[seg._index]
            try:
                parent_compartment = self.segments_compartments_dict[seg.parent._index]
                moose.connect(parent_compartment, 'raxial', compartment, 'axial')
            except:
                pass

        #component loading:
        for component_segment_pair in cell.morphology._backend.observer.kinetic_components:
            component = component_segment_pair[0]
            segment_index = component_segment_pair[1]
            compartment = self.segments_compartments_dict[segment_index]
            
            if component.name == 'IClamp':
                print 'IClamp detected'
                self.current_clamp = moose.PulseGen('/pulsegen')
                self.current_clamp.delay[0] = component.delay # ms
                self.current_clamp.width[0] = component.dur # ms
                self.current_clamp.level[0] = component.amp*1e-12 #pA
                moose.connect(self.current_clamp, 'outputOut', compartment, 'injectMsg')               

class MooseSimulation(object):

    def __init__(self, environment, sim_time=1000):
        self.recording_compartment = environment.compartments[0]
        self.sim_time = sim_time
        self.go_already = False
        self.environment = environment

    def go(self,simdt=1e-6):

        current_clamp = self.environment.current_clamp

        # Setup data recording
        data = moose.Neutral('/data')
        Vm = moose.Table('/data/Vm')
        moose.connect(Vm, 'requestData', self.recording_compartment, 'get_Vm')

        # Now schedule the sequence of operations and time resolutions
        moose.setClock(0,simdt)
        moose.setClock(1,simdt)
        moose.setClock(2,simdt)
        moose.setClock(3,simdt)

        # useClock: First argument is clock no.
        # Second argument is a wildcard path matching all elements of type Compartment
        # Last argument is the processing function to be executed at each tick of clock 0 
        moose.useClock(0, '/model/#[TYPE=Compartment]', 'init') 
        moose.useClock(1, '/model/#[TYPE=Compartment]', 'process')
        moose.useClock(2, Vm.path, 'process')
        moose.useClock(3, current_clamp.path, 'process')

        # Now initialize everything and get set
        moose.reinit()
        moose.start(self.sim_time)
        
        #handle to the global clock:
        clock = moose.Clock('/clock')

        #vectors:
        self.rec_v = Vm.vec
        self.t_final = clock.currentTime

    def show(self):
        import pylab
        pylab.plot(pylab.linspace(0, self.t_final, len(self.rec_v)), self.rec_v)
        pylab.show()
