"""
Simulation of passive properties in NEURON and MOOSE
"""

import neuroml.morphology as ml
import neuroml.kinetics as kinetics
import pyramidal.environments as envs
from matplotlib import pyplot as plt
import numpy as np

#First build a compartment:
compartment = ml.Segment(length=500,
                         proximal_diameter=500,
                         distal_diameter=500)

#Create a PassiveProperties object:
passive = kinetics.PassiveProperties(init_vm=-0.0,
                                     rm=1/0.3,
                                     cm=1.0,
                                     ra=0.03)

#Create a LeakCurrent object:
leak = kinetics.LeakCurrent(em=10.0)

#Get the Morphology object which the compartment is part of:
morph = compartment.morphology

#insert the passive properties and leak current into the morphology:
morph.passive_properties = passive
morph.leak_current = leak

#create a current clamp stimulus:
stim = kinetics.IClamp(current=0.1,
                       delay=5.0,
                       duration=40.0)

#insert the stimulus into the morphology, note that unlike with the passive and leak currents which were
#inserted into the morphology as a whole, the current clamp, being a point current, is inserted into a segment,
#hence the morph[0] statement - this means the first segment in the morphology (in our case slightly irrelevant
#as the morphology only contains one segment anyway)
morph[0].insert(stim)

#We're now ready to run some simulations of a neuron with a leak current:

#Create the MOOSE environmet:
moose_env = envs.MooseEnv(sim_time=100,
                          dt=1e-2)

#import morphology into environment:
moose_env.import_cell(morph)

#Run the MOOSE simulation:
moose_env.run_simulation()

#Now do the same for NEURON:

#create the NEURON environment
neuron_env = envs.NeuronEnv(sim_time=100,dt=1e-2)

#import morphology into environment:
neuron_env.import_cell(morph)

#run the NEURON simulation
neuron_env.run_simulation()

#Get the voltage traces:
neuron_voltage = neuron_env.rec_v
neuron_time_vector  = neuron_env.rec_t

moose_voltage = moose_env.rec_v
moose_time_vector  = np.linspace(0, moose_env.t_final, len(moose_env.rec_v))

#Plot the results:
moose_plot, = plt.plot(moose_time_vector,moose_voltage)
neuron_plot, = plt.plot(neuron_time_vector,neuron_voltage)
plt.xlabel("Time in ms")
plt.ylabel("Voltage in mV")
plt.legend([moose_plot,neuron_plot],["MOOSE","NEURON"])
plt.show()
