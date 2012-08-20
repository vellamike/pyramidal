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
Some very early testing
"""
import neuron
import numpy as np
from neuron import h
import neuroml.loaders as loaders

class NeuronSimulation(object):

    """
    Simulation class mainly taken from Philipp Rautenberg, this class has been
    modified slightly by Mike Vella to accept a section rather than a cell as the 
    object passed to the set_IClamp method of the class.
    see http://www.paedia.info/neuro/intro_pydesign.html

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


class NeuronEnv(object):
    def __init__(self):
        #dict of neuroml segments to NEURON sections
        self.segments_sections_dict={}

    def import_cell(self,cell):
        #experimental:
        for index,seg in enumerate(cell.morphology):
            section=h.Section()
            section.diam=seg.proximal_diameter #fix
            section.L=seg.length
            self.segments_sections_dict[seg] = section

#need to build a hash map here - ideally directly 
            #from the morphology arrays rather
            #than by constructing segment objects from scratch
            #this can be accomplished by having the Section
            #object instantiable by passing it a segment object
            #a dictionary will be used to keep track of whether
            #or not a section has been instantiated

            #there's some thought that needs to go into this - if the segment is virtual then the distal node index in the backend is itself the id of the segment, if not then its parent is the correct one. It might be a lot wiser to use hashes, but how would I do that?





