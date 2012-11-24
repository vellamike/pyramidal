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

import numpy as np
import neuroml.loaders as loaders
import os
import math

#import simulator libraries:
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

        self.sim_time = sim_time
        self.dt = dt # 1e3Factor needed here because of NEURON units
        self.simulation_initialized = False

    def import_cell(self,cell):

        self.segments_sections_dict={}
        self.sections = []
        self.cell = cell

        #this is a clumsy but necessary step:
        self._precompile_mod_files()

        import neuron
        self.neuron = neuron
        
        try:
            self.passive = True
            self.em = cell.leak_current.em
            self.init_vm = cell.passive_properties.init_vm
            self.rm = cell.passive_properties.rm *1e2 #UNIT conversion factor, these all need to be checked
            self.cm = cell.passive_properties.cm *1e1 #UNIT conversion factor, these all need to be checked
            self.ra = cell.passive_properties.ra
        except:
            self.passive = False

        for index,seg in enumerate(cell.morphology):
            section = self.neuron.h.Section()
            section.diam=seg.proximal_diameter #fix

             #temporary hack:
            if seg.length > 0:
                section.L=seg.length
            else:
                section.L=0.1

            try:
                self.passive = True
                section.cm = self.cm
                section.Ra = self.ra

                section.insert('pas')
                for neuron_seg in section:
                    neuron_seg.pas.e = cell.leak_current.em
                    neuron_seg.pas.g = 1 / self.rm #I *think* this is right - is a 1e8 factor needed?
                
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
            except:
                print("Connecting NEURON sections failure")
                pass

        #Kinetic components:
        for component_segment_pair in cell.morphology._backend.observer.kinetic_components:
            component = component_segment_pair[0]
            segment_index = component_segment_pair[1]
            neuron_section = self.segments_sections_dict[segment_index]

            #Here we will need to introduce another method, eventually will need
            #to get a smarter way of doing this where the name of the component
            #calls the method responsible for dealing with it
            if component.type == 'IClamp':
                stim = self.neuron.h.IClamp(neuron_section(0.5))
                stim.delay = component.delay
                stim.amp = component.amp*1e4
                stim.dur = component.dur
                self.stim = stim

            if component.type == 'NMODL':
                print 'Inserting ion channel:' + component.name
                neuron_section.insert(component.name)

                for attribute in component.attribute_values:
                    self.__set_mechanism(neuron_section,
                                         component.name,
                                         attribute, 
                                         component.attribute_values[attribute])

            if component.type == 'HHChannel':
                self._insert_hh_channel(component,neuron_section)

    def _nmodl_compile(self):
        import subprocess

        subprocess.check_call("nrnivmodl")
        
    def _precompile_mod_files(self):
        """
        loop through all components
        """

        import neuronutils        

        mod_files_exist = False
        for component_segment_pair in self.cell.morphology._backend.observer.kinetic_components:
            component = component_segment_pair[0]
            if component.type == 'HHChannel':
                writer = neuronutils.HHNMODLWriter(component)
                writer.write()
                mod_files_exist = True
                
        #compile the mod files:
        if mod_files_exist:
            self._nmodl_compile()
         
    def _insert_hh_channel(self,hh_channel,neuron_section):
       neuron_section.insert(hh_channel.channel_name)
        
    @property
    def topology(self):
        print('connected topology:')
        print(self.neuron.h.topology())

    def set_VClamp(self,dur1=100,amp1=0,dur2=0,amp2=0,dur3=0,amp3=0,):
        """
        Initializes values for a Voltage clamp.

        Techincally this is an SEClamp in neuron, which is a
        three-stage current clamp.
        """
        stim = self.neuron.h.SEClamp(self.recording_section(0.5))
        
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
        stim = self.neuron.h.IClamp(self.recording_section(0.5))
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
        self.rec_t = self.neuron.h.Vector()
        self.rec_t.record(self.neuron.h._ref_t)
        # Record Voltage
        self.rec_v = self.neuron.h.Vector()
        self.rec_v.record(self.recording_section(0.5)._ref_v)

    def get_recording(self):
        time = np.array(self.rec_t)
        voltage = np.array(self.rec_v)
        return time, voltage

    def __init_simulation(self):

        self.set_recording()
        self.neuron.h.dt = self.dt
        self.neuron.h.finitialize(self.init_vm)
        self.neuron.init()
        self.simulation_initialized = True
    
    def run_simulation(self,sim_time=None):
        if not self.simulation_initialized:
            self.__init_simulation()
        if sim_time:
            self.neuron.run(sim_time)
        else:
            self.neuron.run(self.sim_time)
        self.go_already = True
        
    def advance_simulation(self,increment):
        if not self.simulation_initialized:
            self.__init_simulation()
        t_now = self.neuron.h.t
        while self.neuron.h.t < t_now + increment:
            self.neuron.h.fadvance()
        
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

    def __set_mechanism(self,neuron_section, mech, mech_attribute, mech_value):
        """
        Insert NMODL ion channels
        """
        for seg in neuron_section:
            setattr(getattr(seg, mech), mech_attribute, mech_value)

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
        self.channels = []

        try:
            cm_factor = 1e-8
            self.passive = True
            self.em = cell.leak_current.em
            self.init_vm = cell.passive_properties.init_vm
            self.rm = cell.passive_properties.rm / cm_factor
            self.cm = cell.passive_properties.cm * cm_factor
            self.ra = cell.passive_properties.ra * cm_factor #may need to check this is definitely correct
        except:
            self.passive = False
            
        # This is a container for the model
        model = moose.Neutral('/model') 

        print('Creating MOOSE compartments:')
        for index,seg in enumerate(cell.morphology):
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
        
        for i,seg in enumerate(cell.morphology):
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

            if component.type == 'IClamp':
                self.current_clamp = moose.PulseGen('/pulsegen')
                self.current_clamp.delay[0] = component.delay
                self.current_clamp.delay[1] = 1e15 #Ensures first pulse won't repeat
                self.current_clamp.width[0] = component.dur
                self.current_clamp.level[0] = component.amp
                moose.connect(self.current_clamp, 'outputOut', compartment, 'injectMsg')

            if component.type == 'HHChannel':
                self._insert_hh_channel(component,compartment)
                
    def _insert_hh_channel(self,component,compartment):

        import moosecomponents as mc

        channel = mc.IonChannel(component.channel_name,
                                compartment,
                                component.specific_gbar,
                                component.e_rev,
                                Xpower=component.x_power,
                                Ypower=component.y_power,
                                Zpower=component.z_power)

        #setup the alphas and the betas
        try:
            channel.setupAlpha('X',
                               component.x_gate.params,
                               component.x_gate.vdivs,
                               component.x_gate.vmin,
                               component.x_gate.vmax)
        except:
            print 'No X Gate'

        try:
            channel.setupAlpha('Y',
                               component.y_gate.params,
                               component.y_gate.vdivs,
                               component.y_gate.vmin,
                               component.y_gate.vmax)
        except:
            print 'No Y Gate'

        try:
            channel.setupAlpha('Z',
                               component.z_gate.params,
                               component.z_gate.vdivs,
                               component.z_gate.vmin,
                               component.z_gate.vmax)
        except:
            print 'No Z Gate'

        #need to do this for all channels:    
        self.channels.append(channel)

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
        moose.setClock(4,self.dt)

        #quite a hack:
        current_clamp = self.current_clamp
        
        # useClock: First argument is clock no.
        # Second argument is a wildcard path matching all elements of type Compartment
        # Last argument is the processing function to be executed at each tick of clock 0 
        moose.useClock(0, '/model/#[TYPE=Compartment]', 'init') 
        moose.useClock(1, '/model/#[TYPE=Compartment]', 'process')
        moose.useClock(2, Vm.path, 'process')
        moose.useClock(3, current_clamp.path, 'process')
        moose.useClock(4, '/model/#/#[TYPE=HHChannel]', 'process')
    
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
        pylab.plot(pylab.linspace(0, self.t_final, len(self.rec_v)), self.rec_v)
        pylab.show()
