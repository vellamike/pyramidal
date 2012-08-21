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

#attatch all the segments together, in the right order:
iseg.attach(myelin1)
myelin1.attach(node1)
node1.attach(myelin2)
myelin2.attach(node2)

#load a cell from a neuroml file
doc = loaders.NeuroMLLoader.load_neuroml('./Purk2M9s.nml')
cell = doc.cells[0]
morph = cell.morphology

#attach iseg to the soma of loaded cell:
morph[0].attach(iseg)

#obtain the new morphology object:
new_morphology=morph.morphology
