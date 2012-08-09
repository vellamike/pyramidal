Installing pyramidal
=====================

pyramidal has the following strong dependencies:

* NEURON (Python module, for installation instructions see 
  http://www.davison.webfactional.com/notes/installation-neuron-python/ )

* pyMOOSE (for installation instructions see below)

* libNeuroML (for installation see below)

* numpy ( http://numpy.scipy.org/ )

pyMOOSE instllation
-------------------

The latest version of MOOSE with a Python interface can be installed as follows:

::

    svn co http://moose.svn.sourceforge.net/svnroot/moose/moose/branches/dh_branch moose
    cd moose
    make pymoose
    sudo cp -r python/moose /usr/lib/python2.7/dist-packages


Get a read only copy of libNeuroML
----------------------------------

Install `git`_ and type:

::

    git clone git://github.com/NeuralEnsemble/libNeuroML.git


More details about the git repository and making your own branch/fork are `here <how_to_contribute.html>`_.



.. _Git: http://rogerdudler.github.com/git-guide/


Install libNeuroML
------------------

Use the standard install method for Python packages:


::

    sudo python setup.py install


Get a read only copy of pyramidal
----------------------------------

::

    git clone https://github.com/vellamike/pyramidal.git


Install pyramidal
------------------

Use the standard install method for Python packages:


::

    sudo python setup.py install
