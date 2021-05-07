###################
AiiDA pseudo plugin
###################

The ``aiida-pseudo`` package is an AiiDA plugin that simplifies working with pseudopotentials when running calculations or workflows using AiiDA.

Installation
============

You can install ``aiida-pseudo`` in your Python environment using ``pip``:

.. code-block:: console

   $ pip install aiida-pseudo

Getting Started
===============

The easiest way of getting started using ``aiida-pseudo`` is to use the command line interface that ships with it.
For example, to install a configuration of the `SSSP`_, just run:

.. code-block:: console

    $ aiida-pseudo install sssp

The version, functional, and protocol can be controlled with various options; use ``aiida-pseudo install sssp --help`` to see their description.
If you are experiencing problems with this automated install method, see the :ref:`Troubleshooting section <troubleshooting>` for help.
Installed pseudopotential families can be listed using:

.. code-block:: console

    $ aiida-pseudo list

Any pseudopotential family installed can be loaded like any other ``Group`` using the ``load_group`` utility from ``aiida-core``.
Once loaded, it is easy to get the pseudopotentials for a given element or set of elements.
Open a ``verdi shell`` and run:

.. code-block:: python

    family = load_group('SSSP/1.1/PBE/efficiency')
    pseudo = family.get_pseudo(element='Ga')  # Returns a single pseudo
    pseudos = family.get_pseudos(elements=('Ga', 'As'))  # Returns a dictionary of pseudos where the keys are the elements

If you have a ``StructureData`` node, the ``get_pseudos`` method also accepts that as an argument to automatically retrieve all the pseudopotentials required for that structure:

.. code-block:: python

    structure = load_node(<IDENTIFIER>)  # Load the structure from database or create one
    pseudos = family.get_pseudos(structure=structure)

If you use the ``aiida-quantumespresso`` plugin, the ``pseudos`` dictionary returned by ``get_pseudos`` can be directly used as an input for a ``PwCalculation``.

Contents
========

.. toctree::
   :maxdepth: 2

   design
   howto
   troubleshooting
   autoapi/index.rst
   cli

.. _SSSP: https://www.materialscloud.org/discover/sssp/table/efficiency
