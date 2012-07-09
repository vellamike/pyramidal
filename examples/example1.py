import neuroml.morphology as ml
import neuroml.kinetics as kinetics
import neuroml.loaders as loaders
import pyramidal.environments as envs
from neuron import h

iseg=ml.Segment(length=10,proximal_diameter=1,distal_diameter=2)
myelin1=ml.Segment(length=100,proximal_diameter=3,distal_diameter=4)
node1=ml.Segment(length=10,proximal_diameter=5,distal_diameter=6)
myelin2=ml.Segment(length=100,proximal_diameter=7,distal_diameter=8)
node2=ml.Segment(length=10.0,proximal_diameter=9,distal_diameter=10)

print iseg._backend.connectivity
iseg.attach(myelin1)
print iseg._backend.connectivity
myelin1.attach(node1)
print iseg._backend.connectivity
node1.attach(myelin2)
print iseg._backend.connectivity
myelin2.attach(node2)
print iseg._backend.connectivity

doc = loaders.NeuroMLLoader.load_neuroml('/home/mike/dev/libNeuroML/testFiles/NML2_FullCell.nml')
cell = doc.cells[0]
morph = cell.morphology

morph[0].attach(iseg) #attach to the root

new_morphology=morph.morphology

print new_morphology._backend.connectivity
#this step is currently not implemented, inject a current into the root segment
new_morphology[0].insert(kinetics.IClamp(0.1,200,100))

print new_morphology._backend.connectivity
print '\nAfter attaching axon:'
for i,seg in enumerate(new_morphology):
    print 'segment '+str(i)+' distal diameter:' + str(seg.distal_diameter)

env = envs.NeuronEnv()

env.import_cell(new_morphology)

sim = envs.NeuronSimulation(env.sections[0])

sim.go()
sim.show()
