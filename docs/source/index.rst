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
   dev
   autoapi/index.rst
   cli

.. _SSSP: https://www.materialscloud.org/discover/sssp/table/efficiency

Acknowledgements
================

If you use this plugin and/or AiiDA for your research, please cite the following work:

* Sebastiaan. P. Huber, Spyros Zoupanos, Martin Uhrin, Leopold Talirz, Leonid Kahle, Rico Häuselmann, Dominik Gresch, Tiziano Müller, Aliaksandr V. Yakutovich, Casper W. Andersen, Francisco F. Ramirez, Carl S. Adorf, Fernando Gargiulo, Snehal Kumbhar, Elsa Passaro, Conrad Johnston, Andrius Merkys, Andrea Cepellotti, Nicolas Mounet, Nicola Marzari, Boris Kozinsky, and Giovanni Pizzi, |AiiDA main paper|_, Scientific Data **7**, 300 (2020)

* Martin Uhrin, Sebastiaan. P. Huber, Jusong Yu, Nicola Marzari, and Giovanni Pizzi, |AiiDA engine paper|_, Computational Materials Science **187**, 110086 (2021)

.. rst-class:: bigfont

    We acknowledge support from:

.. list-table::
    :widths: 60 40
    :class: logo-table
    :header-rows: 0

    * - The `NCCR MARVEL`_ funded by the Swiss National Science Foundation.
      - |marvel|
    * - The EU Centre of Excellence "`MaX – Materials Design at the Exascale`_" (Horizon 2020 EINFRA-5, Grant No. 676598).
      - |max|
    * - The `swissuniversities P-5 project "Materials Cloud"`_.
      - |swissuniversities|

.. |marvel| image:: images/MARVEL.png
    :width: 100%

.. |max| image:: images/MaX.png
    :width: 100%

.. |swissuniversities| image:: images/swissuniversities.png
    :width: 100%

.. |AiiDA main paper| replace:: *AiiDA 1.0, a scalable computational infrastructure for automated reproducible workflows and data provenance*
.. _AiiDA main paper: https://doi.org/10.1038/s41597-020-00638-4

.. |AiiDA engine paper| replace:: *Workflows in AiiDA: Engineering a high-throughput, event-based engine for robust and modular computational workflows*
.. _AiiDA engine paper: https://doi.org/10.1016/j.commatsci.2020.110086

.. _NCCR MARVEL: http://nccr-marvel.ch/
.. _MaX – Materials Design at the Exascale: http://www.max-centre.eu/
.. _`swissuniversities P-5 project "Materials Cloud"`: https://www.materialscloud.org/swissuniversities
