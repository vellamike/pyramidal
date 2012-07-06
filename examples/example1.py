import neuroml.morphology as ml
import neuroml.kinetics as kinetics
import neuroml.loaders as loaders
import pyramidal.environments as envs
from neuron import h

doc = loaders.NeuroMLLoader.load_neuroml('/home/mike/dev/libNeuroML/testFiles/NML2_FullCell.nml')
cell = doc.cells[0]
morph = cell.morphology

#this step is currently not implemented
morph[0].insert(kinetics.IClamp(0.1,200,100))

env = envs.NeuronEnv()

env.import_cell(cell)

sim = envs.NeuronSimulation(env.sections[0])

sim.go()
sim.show()
