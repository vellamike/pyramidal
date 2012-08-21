import neuroml.morphology as ml
import neuroml.kinetics as kinetics
import neuroml.loaders as loaders
import pyramidal.environments as envs
from neuron import h

#build some compartments:
compartment = ml.Segment(length=500,proximal_diameter=500,distal_diameter=500)
#compartment_2 = ml.Segment(length=10,proximal_diameter=10,distal_diameter=10)
#compartment.attach(compartment_2)

#get the morphology:
morphology = compartment.morphology

#create passive properties container
passive = kinetics.PassiveProperties(init_vm=-60.0,#squid
                                     rm=1/0.3,#squid
                                     cm=1.0,#squid
                                     ra=0.03) #squid -this actually needs xarea

#create a leak current:
leak = kinetics.LeakCurrent(em=-60.0)

#insert passive properties and leak current into the morphology:
morphology.passive_properties = passive
morphology.leak_current = leak

#make a current clamp object:
stim = kinetics.IClamp(current=0.15,
                       delay=5.0,
                       duration=180.0)

#insert it into the morphology
morphology[0].insert(stim)

#make some channels:
kv_attributes = {'gbar':10000}
kv = kinetics.Nmodl('kv',kv_attributes)

sodium_attributes = {'gbar':100000}
na = kinetics.Nmodl('na',sodium_attributes)

#insert the channels:
morphology[0].insert(kv)
morphology[0].insert(na)

#create a NEURON environment:
neuron_env = envs.NeuronEnv(sim_time=200,
                            dt=1e-2)

#import morpholgoy into environment:
neuron_env.import_cell(morphology)

#run the NEURON simulation
neuron_env.run_simulation()

#plot the simulation results:
neuron_env.show_simulation()
