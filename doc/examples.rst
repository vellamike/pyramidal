Examples
========

All these examples are located in the /examples folder

Example 1 - A passive neuron
----------------------------
This example serves as an introduction to pyramidal usage. Let's jump straight in and examine the code.

We have the following interesting import statements:

.. code-block:: python

    import neuroml.morphology as ml
    import neuroml.kinetics as kinetics
    import pyramidal.environments as envs

* The neuroml morphology module provides support for dealing with compartments - their dimensions and their connectivity. 
* The neuroml kinetics module provides objects with a time-dependent element to their behaviour. This includes things like point currents.
* The pyramidal environments module provides support for interfacing with different simulators. An "environment" in this context can be thought of an entire simulator contained within an object.

The syntax for making a compartment is intuitive:

.. code-block:: python

    compartment = ml.Segment(length=500,
                             proximal_diameter=500,
                             distal_diameter=500)

The PassiveProperties and LeakCurrent objects are created, which we will then associate with our compartment.

.. code-block:: python

   #Create a PassiveProperties object:
   passive = kinetics.PassiveProperties(init_vm=-0.0,
                                        rm=1/0.3,
                                        cm=1.0,
                                        ra=0.03)
   
   #Create a LeakCurrent object:
   leak = kinetics.LeakCurrent(em=10.0)

The morphology of a compartment is an object with all the other compartments connected to it. So for instance, if I had a compartment 'iseg' which was part of a much larger morphology including an axon and a whole cell, iseg.morphology would be the whole morphology. We need this object to pass to our simulators later on. Additionally, as shown here, the passive properties and leak current are passed to a whole morphology. It is currently not possible to set these per compartment (though this feature can be introduced if there is demand for it).

.. code-block:: python

    #Get the Morphology object which the compartment is part of:
    morph = compartment.morphology

    #insert the passive properties and leak current into the morphology:
    morph.passive_properties = passive
    morph.leak_current = leak

We now use the neuroml kinetics module to create a current clamp stimulus. Otherwise the simulation would be a very boring one indeed. We insert the stimulus into the morphology, note that unlike with the passive and leak currents which were inserted into the morphology as a whole, the current clamp, being a point current, is inserted into a segment,hence the morph[0] statement - this means the first segment in the morphology (in our case slightly irrelevant  as the morphology only contains one segment anyway)

.. code-block:: python
    #create a current clamp stimulus:
    stim = kinetics.IClamp(current=0.1,
                           delay=5.0,
                           duration=40.0)
    
    morph[0].insert(stim)

All that now remains is to create the MOOSE and NEURON environments and run the simulations, the syntax is the same for both environments. Here's MOOSE:

.. code-block:: python

    #Create the MOOSE environmet:
    moose_env = envs.MooseEnv(sim_time=100,
                              dt=1e-2)
    
    #import morphology into environment:
    moose_env.import_cell(morph)
    
    #Run the MOOSE simulation:
    moose_env.run_simulation()

And NEURON:

.. code-block:: python

    #create the NEURON environment
    neuron_env = envs.NeuronEnv(sim_time=100,
                                dt=1e-2)
    
    #import morphology into environment:
    neuron_env.import_cell(morph)
    
    #run the NEURON simulation
    neuron_env.run_simulation()

The final part of the example simply runs some plotting routines to visualise the result of our simulation. Assuming the example runs correctly, you should get a plot looking like this:

.. figure:: /figs/example1.png
   :scale: 100 %
   :alt: passive_simulation

As can be seen, the result of this passive, single-compartment similation are so similar in NEURON and MOOSE that it is almost impossible to tell there is more than one plot.

Example 2 - Hodgkin-Huxley single compartmental simulations
-----------------------------------------------------------

This example is the same as Example 1 except that we are now going to use the neuroml kinetics module to add some Hodgkin-Huxely channels. This will allow us to see some action potentials! The libNeuroML type "HHChannel" is used to insert some kinetics. Appropriately, this example roughly recreates Hodgkin and Huxley Squid giant axon model.

Just as in example 1 we created a current clamp stimulus, we are now going to create sodium and potassium ion channel objects:

.. code-block:: python

    #create Na ion channel:
    na_channel = kinetics.HHChannel(name = 'na',
                                    specific_gbar = 120.0,
                                    ion = 'na',
                                    e_rev = 115.0, #115 for squid
                                    x_power = 3.0,
                                    y_power = 1.0)
    
    #create K ion channel:
    k_channel = kinetics.HHChannel(name = 'kv',
                                   specific_gbar = 36.0, #36.0 specific Gna in squid model
                                   ion = 'k',
                                   e_rev = -12.0, #calculated from squid demo in moose -e-3 factor removed
                                   x_power = 4.0,
                                   y_power = 0.0)
    
Here the xpower and ypower signify the power to which activating("m") and inactivating("h") components of the channel should be raised. The next thing we need to do is set the coefficients which determine the gating parameters governing the alpha and beta opening and closing rates of each gate, the snippet here is for the sodium m gate:

.. code-block:: python

    na_m_params = {'A_A':0.1 * (25.0),
                   'A_B': -0.1,
                   'A_C': -1.0,
                   'A_D': -25.0,
                   'A_F':-10.0,
                   'B_A': 4.0,
                   'B_B': 0.0,
                   'B_C': 0.0,
                   'B_D': 0.0,
                   'B_F': 18.0}

Once these parameters have beend decided, the setup_alpha method is run on each channel, specifying whether coefficients for the X or Y gate are being set, in this snippet we do this for the activating and inacticvating gates:

.. code-block:: python

    #setup the channel gating parameters:
    na_channel.setup_alpha(gate = 'X',
                           params = na_m_params,
                           vdivs = 150,
                           vmin = -30,
                           vmax = 120)
    
    na_channel.setup_alpha(gate = 'Y',
                           params = na_h_params,
                           vdivs = 150,
                           vmin = -30,
                           vmax = 120)

Just like the current clamp stimulus in example 1, the ion channel is inserted into a specific segment:

.. code-block:: python

    morphology[0].insert(na_channel)
    morphology[0].insert(k_channel)

The MOOSE and NEURON environments are created and morphology imported just as before. Once the simulation is run you should get a plot looking something like this:

.. figure:: /figs/example2.png
   :scale: 100 %
   :alt: hodgkin_huxely_simulation

Example 3 -
---------
Example 1 (./examples/example1.py) is an example of manually building an axon from libneuroml objects, loading a cell from file, attaching the axon initial segment to the loaded cell soma and running the same simulation NEURON and MOOSE, please run the file look at the inline comments of example1.py file. This should be the first example to show the same simulation produced by NEURON and MOOSE. Currently however there are some issues which have not been resolved:

* Passive properties of the neurons are different currently different. This issue should be easy to resolve.
* The MOOSE current clamp (PulseGen in MOOSE-Speak) object behaves differently to the NEURON object. In MOOSE the current is reinjected periodically after a period of 'PulseGen.delay'. This issue should be easy to resolve
* In MOOSE the segment connectivity is accounted for, but as yet segment dimensions are not.
    
Example 4 - 
---------
Example 2 is incomplete - the aim of this example will be to show visualisation using NeuronVisio.


Example 5 - Mutli-compartmental models
--------------------------------------

.. note::
    As of 21/08/12 mutli-compartmental modelling is still buggy. This is thought to be down to some unresolved issues in setting axial resistance which will soon be resolved.
 
