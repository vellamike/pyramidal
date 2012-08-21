Examples
========

Example 1 - Passive properties
------------------------------

Example 2 - Hodgkin Huxley single compartmental simulations
-----------------------------------------------------------

In this example a single compartment is created and the libNeuroML type "HHChannel" is used to insert some kinetics. Appropriately, this example roughly recreates Hodgkin and Huxley Squid giant axon model.

Example 3 -
---------
Example 1 (./examples/example1.py) is an example of manually building an axon from libneuroml objects, loading a cell from file, attaching the axon initial segment to the loaded cell soma and running the same simulation NEURON and MOOSE, please run the file look at the inline comments of example1.py file. This should be the first example to show the same simulation produced by NEURON and MOOSE. Currently however there are some issues which have not been resolved:

    *Passive properties of the neurons are different currently different. This issue should be easy to resolve.
    *The MOOSE current clamp (PulseGen in MOOSE-Speak) object behaves differently to the NEURON object. In MOOSE the current is reinjected periodically after a period of 'PulseGen.delay'. This issue should
     be easy to resolve
    *In MOOSE the segment connectivity is accounted for, but as yet segment dimensions are not.
    
Example 4 - 
---------
Example 2 is incomplete - the aim of this example will be to show visualisation using NeuronVisio.


Example 5 - Mutli-compartmental models
--------------------------------------

.. note::
    As of 21/08/12 mutli-compartmental modelling is still buggy. This is thought to be down to some unresolved issues in setting axial resistance which will soon be resolved.
 
