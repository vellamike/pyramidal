"""
Simulation of a current injection into a passive compartment
"""

import neuroml.morphology as ml
import neuroml.kinetics as kinetics
import pyramidal.environments as envs
from matplotlib import pyplot as plt
import numpy as np

#First build a compartment:
compartment = ml.Segment(length=500,proximal_diameter=500,distal_diameter=500)

#Create a PassiveProperties object:
passive = kinetics.PassiveProperties(init_vm=-0.0,
                                     rm=1/0.3,
                                     cm=1.0,
                                     ra=0.03)

#Create a LeakCurrent object:
leak = kinetics.LeakCurrent(em=10.0)


#get a Morphology object from the compartment:
morphology = compartment.morphology

#insert the passive properties and leak current into the morphology:
morphology.passive_properties = passive
morphology.leak_current = leak

#create a current clamp stimulus:
stim = kinetics.IClamp(current=0.1,
                       delay=5.0,
                       duration=40.0)

#insert the stimulus into the morphology:
morphology[0].insert(stim)

#create the MOOSE environmet:
moose_env = envs.MooseEnv(sim_time=100,
                          dt=1e-2)

#import morphology into environment:
moose_env.import_cell(morphology)

#Run the MOOSE simulation:
moose_env.run_simulation()

#plot simulation results:
#moose_env.show_simulation()

#create the NEURON environment
neuron_env = envs.NeuronEnv(sim_time=100,dt=1e-2)

#import morphology into environment:
neuron_env.import_cell(morphology)

#run the NEURON simulation
print 'About to run simulation'
neuron_env.run_simulation()

neuron_voltage = neuron_env.rec_v
neuron_time_vector  = neuron_env.rec_t

moose_voltage = moose_env.rec_v
moose_time_vector  = np.linspace(0, moose_env.t_final, len(moose_env.rec_v))

#Plotting results:
moose_plot, = plt.plot(moose_time_vector,moose_voltage)
neuron_plot, = plt.plot(neuron_time_vector,neuron_voltage)
plt.xlabel("Time in ms")
plt.ylabel("Voltage in mV")
plt.legend([moose_plot,neuron_plot],["MOOSE","NEURON"])
plt.show()
