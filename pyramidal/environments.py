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
"""

import neuron
import numpy as np
import neuroml.loaders as loaders
import os
import math

#import simulator libraries:
from neuron import h
import moose


class SimulatorEnv(object):
    """
    Base class for simulator-specific environments which express
    a model in simulator-specific types.
    Simulation classes allow an environment to be simulated. The most important
    method in these classes is the run method which calls the underlying
    simulator run loop.

    Objects of this class control a current clamp simulation. Example of use:
    >>> cell = Cell()
    >>> sim = Simulation(cell)
    >>> sim.go()
    >>> sim.show()


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

    def __init__(self,sim_time=1,dt=1e-4):
        self.sim_time = sim_time*10**3
        self.dt=dt*10**3

    def import_cell(self,cell):

#        print("In the NEURON ENV cell importing routine")
        
        self.segments_sections_dict={}
        self.sections = []

        try:
            self.passive = True
            self.em = cell.leak_current.em
            self.init_vm = cell.passive_properties.init_vm * 1000
            self.rm = cell.passive_properties.rm
            self.cm = cell.passive_properties.cm
            self.ra = cell.passive_properties.ra
        except:
            self.passive = False

        for index,seg in enumerate(cell.morphology):
            section = h.Section()
            section.diam=seg.proximal_diameter #fix

             #temporary hack:
            if seg.length > 0:
                section.L=seg.length
            else:
                section.L=0.1
           
            try:
                self.passive = True
                print("Setting NEURON passive properties")
                section.cm = cell.passive_properties.cm * 10e13 #conversions from SI to NEURON-compatibe(check)
                section.Ra = cell.passive_properties.ra * 1e-8 #conversions from SI to NEURON-compatibe(check)

                section.insert('pas')
                for neuron_seg in section:
                    print 'setting'
                    print neuron_seg.pas.e
                    print neuron_seg.pas.g
                    neuron_seg.pas.e = cell.leak_current.em * 1e3 # convert to mV
                    neuron_seg.pas.g = 1 / cell.passive_properties.rm * 1e8 #I *think* this is right
                
            except:
                print("Setting passive properties failed")
                self.passive = False

            self.segments_sections_dict[seg._index] = section
            self.sections.append(section)

          #this will be required for visualisation but I still don't fully understand
          #how it needs to be implemented:
          # h.pt3dadd(seg.proximal.x,
          #           seg.proximal.y,
          #           seg.proximal.z,
          #           seg.proximal_diameter,
          #           sec = section)

        #temporary, user needs to be able to define which sections
        #will be recorded from
        self.recording_section=self.sections[0] 
        
        #connect them all together:
        for i,seg in enumerate(cell.morphology):
            section = self.segments_sections_dict[seg._index]
            try:
                parent_section = self.segments_sections_dict[seg.parent._index]
                section.connect(parent_section)
                print("Connection made")
            except:
                print("Connecting NEURON sections failure")
                pass

        #Kinetic components:
        for component_segment_pair in cell.morphology._backend.observer.kinetic_components:
            component = component_segment_pair[0]
            segment_index = component_segment_pair[1]
            neuron_section = self.segments_sections_dict[segment_index]
            
            if component.name == 'IClamp':
               stim = h.IClamp(neuron_section(0.5))
               stim.delay = component.delay*1000 #convert to ms
               stim.amp = component.amp*1e9 #convert to nA
               stim.dur = component.dur *1000 #convert to ms
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

    def set_VClamp(self,dur1=100,amp1=0,dur2=0,amp2=0,dur3=0,amp3=0,):
        """
        Initializes values for a Voltage clamp.

        Techincally this is an SEClamp in neuron, which is a
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

    def show_simulation(self):
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

    def run_simulation(self,sim_time=None):

        self.set_recording()
        h.dt = self.dt
        h.finitialize(self.init_vm)

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

class MooseEnv(SimulatorEnv):
    """
    MOOSE-simulator environment

    * Loads NeuroML-specified model into a 
      MOOSE-specific in-memory representation.

    * Provides methods to run a simulation based
      on the model imported
    """

    def __init__(self,sim_time=1,dt=1e-4):
        self.sim_time = sim_time
        self.dt=dt
        
    def import_cell(self,cell):
        """
        Import a cell from libNeuroML into MOOSE objects
        """

        self.segments_compartments_dict={}
        self.compartments = []

        try:
            self.passive = True
            self.em = cell.leak_current.em
            self.init_vm = cell.passive_properties.init_vm
            self.rm = cell.passive_properties.rm
            self.cm = cell.passive_properties.cm
            self.ra = cell.passive_properties.ra
        except:
            self.passive = False
            
        # This is a container for the model
        model = moose.Neutral('/model') 
        
        print('Creating MOOSE compartments:')
        for index,seg in enumerate(cell.morphology):
            print(index)
            path = '/model/' + str(index)

            if self.passive:
                compartment = self._make_compartment(path,
                                                     self.ra,
                                                     self.rm,
                                                     self.cm,
                                                     self.em,
                                                     seg.proximal_diameter,
                                                     seg.length)
                compartment.initVm = self.init_vm
            else:
                raise(NotImplementedError,"Currently not supporting non-passive cells")
                
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
                self.current_clamp.delay[0] = component.delay
                self.current_clamp.delay[1] = 10 #temp hack
                self.current_clamp.width[0] = component.dur
                self.current_clamp.level[0] = component.amp
                moose.connect(self.current_clamp, 'outputOut', compartment, 'injectMsg')

            elif component.name != 'IClamp':
                raise(NotImplementedError)
            
    def _make_compartment(self,path, ra, rm, cm, em, diameter, length):
        """
        Uses compartment dimensions to set passive and leak properties
        """
        Ra = 4.0 * length * ra / ( math.pi * diameter * diameter )
        Rm = rm / ( math.pi * diameter * length )
        Cm = cm * math.pi * diameter * length

        compartment = moose.Compartment(path)
        compartment.Ra = Ra
        compartment.Rm = Rm
        compartment.Cm = Cm
        compartment.Em = em
        compartment.length = length
        compartment.diameter = diameter
        compartment.initVm = em
        
        return compartment
            
    def run_simulation(self):

        # Setup data recording
        data = moose.Neutral('/data')
        Vm = moose.Table('/data/Vm')
        moose.connect(Vm, 'requestData', self.compartments[0], 'get_Vm')

        # Now schedule the sequence of operations and time resolutions
        moose.setClock(0,self.dt)
        moose.setClock(1,self.dt)
        moose.setClock(2,self.dt)
        moose.setClock(3,self.dt)

        #quite a hack:
        current_clamp = self.current_clamp
        
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

    def show_simulation(self):
        import pylab
        pylab.xlabel("Time in ms")
        pylab.ylabel("Voltage in mV")
        pylab.plot(pylab.linspace(0, self.t_final*1000, len(self.rec_v)), self.rec_v*1000)
        pylab.show()
