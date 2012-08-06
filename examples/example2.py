"""
Same as example 1 but now lets use neuronvisio
"""
import neuroml.morphology as ml
import neuroml.kinetics as kinetics
import neuroml.loaders as loaders
import pyramidal.environments as envs

from neuronvisio.controls import Controls
controls = Controls()   # starting the GUI

iseg=ml.Segment(length=10,proximal_diameter=1,distal_diameter=2)
myelin1=ml.Segment(length=100,proximal_diameter=3,distal_diameter=4)
node1=ml.Segment(length=10,proximal_diameter=5,distal_diameter=6)
myelin2=ml.Segment(length=100,proximal_diameter=7,distal_diameter=8)
node2=ml.Segment(length=10.0,proximal_diameter=9,distal_diameter=10)

iseg.attach(myelin1)
myelin1.attach(node1)
node1.attach(myelin2)
myelin2.attach(node2)

#doc = loaders.NeuroMLLoader.load_neuroml('/home/mike/dev/libNeuroML/testFiles/NML2_FullCell.nml')
#doc = loaders.NeuroMLLoader.load_neuroml('/home/mike/dev/libNeuroML/testFiles/Purk2M9s.nml')
#cell = doc.cells[0]
#morph = cell.morphology

#morph[0].attach(iseg) #attach to the root

#new_morphology=morph.morphology

#insert a current clamp:
#new_morphology[3].insert(kinetics.IClamp(0.1,200,100))

#env = envs.NeuronEnv()

#env.import_cell(new_morphology)
#


#sim = envs.NeuronSimulation(env.sections[0])
#print 'topology:'
#print env.topology
#sim.go()
#sim.show()


