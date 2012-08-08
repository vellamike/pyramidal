import neuroml.morphology as ml
import neuroml.kinetics as kinetics
import neuroml.loaders as loaders
import pyramidal.environments as envs
from neuron import h

#Create an axon:
iseg=ml.Segment(length=10,proximal_diameter=1,distal_diameter=2)
myelin1=ml.Segment(length=100,proximal_diameter=3,distal_diameter=4)
node1=ml.Segment(length=10,proximal_diameter=5,distal_diameter=6)
myelin2=ml.Segment(length=100,proximal_diameter=7,distal_diameter=8)
node2=ml.Segment(length=10.0,proximal_diameter=9,distal_diameter=10)
iseg.attach(myelin1)
myelin1.attach(node1)
node1.attach(myelin2)
myelin2.attach(node2)

#load a cell:
doc = loaders.NeuroMLLoader.load_neuroml('/home/mike/dev/libNeuroML/testFiles/Purk2M9s.nml')
cell = doc.cells[0]
morph = cell.morphology

#attach iseg to the soma of loaded cell:
morph[0].attach(iseg)

#obtain the new morphology object:
new_morphology=morph.morphology

#create the current clamp stimulus:
stim = kinetics.IClamp(0.1,200,100)

#insert the stimulus:
new_morphology[0].insert(stim)

#create the MOOSE environment
env = envs.MooseEnv()
env.import_cell(new_morphology)

#create the NEURON environment
env = envs.NeuronEnv()
env.import_cell(new_morphology)

#create the simulation from the environment:
sim = envs.NeuronSimulation(env.sections[0])

print 'topology:'
print env.topology

sim.go()
sim.show()
