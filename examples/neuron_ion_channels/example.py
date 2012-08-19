import neuroml.morphology as ml
import neuroml.kinetics as kinetics
import neuroml.loaders as loaders
import pyramidal.environments as envs
from neuron import h

#iseg=ml.Segment(length=10,proximal_diameter=1,distal_diameter=2)
#myelin1=ml.Segment(length=100,proximal_diameter=3,distal_diameter=4)
#node1=ml.Segment(length=10,proximal_diameter=5,distal_diameter=6)
#myelin2=ml.Segment(length=100,proximal_diameter=7,distal_diameter=8)
#node2=ml.Segment(length=10.0,proximal_diameter=9,distal_diameter=10)
#iseg.attach(myelin1)
#myelin1.attach(node1)
#node1.attach(myelin2)
#myelin2.attach(node2)
#doc = loaders.NeuroMLLoader.load_neuroml('/home/mike/dev/libNeuroML/testFiles/NML2_FullCell.nml')
#doc = loaders.NeuroMLLoader.load_neuroml('/home/mike/dev/libNeuroML/testFiles/Purk2M9s.nml')
#cell = doc.cells[0]
#morph = cell.morphology
#morph[0].attach(iseg) #attach to the root
#new_morphology=morph.morphology


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
