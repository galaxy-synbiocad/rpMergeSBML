rpMergeSBML's Documentation
===========================

Indices and tables
##################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Introduction
############

.. _rpBase: https://github.com/Galaxy-SynBioCAD/rpBase
.. _rpCache: https://github.com/Galaxy-SynBioCAD/rpCache

Welcome to the rpMergeSBML documentation. This project merges two or more SBMLs or rpSBMLs to a SBML file. The program checks for each species against all the possible species in the target SBML, and selects the closest member. If no match is found, the species is created in the target SBML. The groups are also merged together or created if they do not exist in the target.

Usage
#####

First build the rpBase_ and rpCache_ dockers before building the local one:

.. code-block:: bash

   docker build -t brsynth/rpmergesbml-standalone:v2 .

The docker can be called locally using the following commands. To merge a single sbml file to a sbml file:

.. code-block:: bash

   python run.py -sourcefile /path/to/source.sbml -inout_format sbml -target_sbml /path/to/target.sbml -output output.sbml

To merge a collection of rpSBML to a SBML file:

.. code-block:: bash

   python run.py -sourcefile /path/to/source.tar -inout_format tar -target_sbml /path/to/target.sbml -output output.tar

API
###

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. currentmodule:: rpTool

.. autoclass:: mergeSBML_hdd
    :show-inheritance:
    :members:
    :inherited-members:

.. currentmodule:: rpToolServe

.. autoclass:: main
    :show-inheritance:
    :members:
    :inherited-members:

.. currentmodule:: run

.. autoclass:: main
    :show-inheritance:
    :members:
    :inherited-members:
