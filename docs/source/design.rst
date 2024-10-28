
.. _design:

######
Design
######

The plugin is centered around two concepts: pseudopotentials and pseudopotential families.
The two concepts are further explained below, especially focusing on how they are implemented in ``aiida-pseudo``, what assumptions are made, and what the limitations are.

Pseudopotentials
================

Pseudopotentials are implemented as `data plugins <https://aiida-core.readthedocs.io/en/latest/topics/data_types.html#creating-a-data-plugin>`_, and the base class is :py:class:`~aiida_pseudo.data.pseudo.PseudoPotentialData`.
Pseudopotentials are assumed to be defined by a single file on disk and represent a single chemical element.
As such, each pseudopotential node, *has* to have two attributes: the md5 of the file that it represents and the symbol of chemical element that the pseudopotential describes.
The latter follows IUPAC naming conventions defined as ``elements`` in the module ``aiida.common.constants`` of ``aiida-core``.

:py:class:`~aiida_pseudo.data.pseudo.PseudoPotentialData` functions as a base class and does not represent an actual existing pseudopotential format.
It *is* possible to create a family of :py:class:`~aiida_pseudo.data.pseudo.PseudoPotentialData` nodes, but since the element cannot be parsed from the file content itself, it will have to be done from the *filename*, so the filename *has* to have the format ``CHEMICAL_SYMBOL.EXTENSION``, for example ``Ar.pseudo``.
Since the :py:class:`~aiida_pseudo.data.pseudo.PseudoPotentialData` class does not have any features tailored to specific formats, as do the classes which inherit from it (e.g. :py:class:`~aiida_pseudo.data.pseudo.UpfData` for UPF-formatted pseudopotentials), this class is mostly useful for development.

The plugin comes with a variety of pseudopotential subtypes that represent various common pseudopotential formats, such as UPF, PSF, PSML and PSP8.
The corresponding data plugins implement how the element and other data are parsed from a pseudopotential file with such a format.
A new pseudopotential node can be created by instantiating the corresponding plugin class:

.. code-block:: python

    from aiida import plugins

    UpfData = plugins.DataFactory('pseudo.upf')

    with open('path/to/pseudo.upf', 'rb') as stream:
        pseudo = UpfData(stream)

Note, the pseudopotential constructor expects a stream of bytes, so be sure to open the file handle with the ``'rb'`` mode.
Alternatively, you can also use the ``get_or_create`` classmethod, which will first search the database to check if a pseudopotential of the exact same type and content already exists.
If that is the case, that node is returned, otherwise a new instance is created:

.. code-block:: python

    from aiida import plugins

    UpfData = plugins.DataFactory('pseudo.upf')

    with open('path/to/pseudo.upf', 'rb') as stream:
        pseudo = UpfData.get_or_create(stream)

If a new node was created, it will be unstored.
Note that if more than one pseudopotential in the database is matched, a random one is selected and returned.

Families
========

Having loose pseudopotentials floating around is not very practical, so groups of related pseudopotentials can be organized into "families", which are implemented as group plugins with the base class :py:class:`~aiida_pseudo.groups.family.PseudoPotentialFamily`.

.. tip::

    Since a :py:class:`~aiida_pseudo.groups.family.PseudoPotentialFamily` is a subclass of AiiDA's :py:class:`~aiida.orm.groups.Group`, they share the same API.
    That means you can use `AiiDA's group API <https://aiida.readthedocs.io/projects/aiida-core/en/latest/howto/data.html#organizing-data>`_ as well as the ``verdi group`` CLI to work with families of ``aiida-pseudo``.

A family class can in principle support many pseudopotential formats, however, a family instance can only contain pseudopotentials of a single format.
For example, the :py:class:`~aiida_pseudo.groups.family.PseudoPotentialFamily` class supports all of the pseudopotential formats that are supported by this plugin.
However, any instance can only contain pseudopotentials of the same format (e.g. *all* UPF or *all* PSP8, not a mixture).
In contrast, the :py:class:`~aiida_pseudo.groups.family.SsspFamily` only supports the :py:class:`~aiida_pseudo.data.pseudo.UpfData` format.

A pseudopotential family can be constructed manually, by first constructing the class instance and then adding pseudopotential data nodes to it:

.. code-block:: python

    from aiida import plugins

    UpfData = plugins.DataFactory('pseudo.upf')
    PseudoPotentialFamily = plugins.GroupFactory('pseudo.family')

    pseudos = []

    for filepath in ['Ga.upf', 'As.upf']:
        with open(filepath, 'rb') as stream:
            pseudo = UpfData(stream)
            pseudos.append(pseudo.store())

    family = PseudoPotentialFamily(label='pseudos/upf').store()
    family.add_nodes(pseudos)

Note that as with any :py:class:`~aiida.orm.Group`, it has to be stored before nodes can be added.
If you have a folder on disk that contains various pseudopotentials for different elements, there is an even easier way to create the family automatically:

.. code-block:: python

    from aiida import plugins

    UpfData = plugins.DataFactory('pseudo.upf')
    PseudoPotentialFamily = plugins.GroupFactory('pseudo')

    family = PseudoPotentialFamily('path/to/pseudos', 'pseudos/upf', pseudo_type=UpfData)

The plugin is not able to reliably deduce the format of the pseudopotentials contained in the folder, so one should indicate what data type to use with the ``pseudo_type`` argument.
The exception is when the family class only supports a single pseudo type, such as for the :py:class:`~aiida_pseudo.groups.family.SsspFamily`, in which case that type will automatically be selected.
Subclasses of supported pseudo types are also accepted.
For example, the base class :py:class:`~aiida_pseudo.groups.family.PseudoPotentialFamily` supports pseudopotentials of the :py:class:`~aiida_pseudo.data.pseudo.PseudoPotentialData` type.
Because all more specific pseudopotential types are subclasses of py:class:`~aiida_pseudo.data.pseudo.PseudoPotentialData`, the :py:class:`~aiida_pseudo.groups.family.PseudoPotentialFamily` class accepts all of them.

Established families
--------------------

When it comes to pseudopotential families, ``aiida-pseudo`` makes a clear distinction between families that are *established* and those that are not.
A pseudopotential family is only considered to be *established* when it has a comprehensive set of rigorously tested pseudopotentials with convergence tests, both of which have been published and are publicly available.

Only a pseudopotential family that is *established* will receive support for automated installs with its own class (e.g. :py:class:`~aiida_pseudo.groups.family.SsspFamily`/:py:class:`~aiida_pseudo.groups.family.PseudoDojoFamily`) and command line interface (CLI) commands (e.g. ``install sssp``/``install pseudo-dojo``).
To make sure these families represent the official ones, they can only be installed with their supported CLI commands, and there are strict checks on the format of these files to make sure they correspond to the official ones.
Based on the same principle of preserving the integrity of these established pseudopotentials, the ``family cutoffs set`` command cannot be used to set the recommended cutoffs of an established family.

To install a set of *non-established* pseudopotentials and configure their recommended cutoffs, install them from the archive using ``install family`` as a :py:class:`~aiida_pseudo.groups.family.CutoffsPseudoPotentialFamily` as described in the :ref:`corresponding how-to section <how-to:install_archive>`.

Recommended cutoffs
===================

Certain pseudopotential family types, such as the :py:class:`~aiida_pseudo.groups.family.SsspFamily`, provide recommended cutoff values for wave functions and charge density in plane-wave codes.
These cutoffs can be defined in any unit supported by the |pint|_ package.
The recommended cutoffs for a set of elements or a :py:class:`~aiida.orm.StructureData` can be retrieved from the family as follows:

.. code-block:: python

    family = load_group('SSSP/1.1/PBE/efficiency')
    cutoffs = family.get_recommended_cutoffs(elements=('Ga', 'As'))  # From a tuple or list of element symbols
    cutoffs = family.get_recommended_cutoffs(structure=load_node(<IDENTIFIER>))  # From a `StructureData` node

To obtain the recommended cutoffs in a specific unit, you can pass the string identifier of that unit:

.. code-block:: ipython

    In [1]: pseudo_family = load_group('SSSP/1.1/PBE/efficiency')

    In [2]: family.get_recommended_cutoffs(elements=('Ga', 'As'), unit='Ry')
    Out[2]: (70.0, 560.0)

    In [3]: family.get_recommended_cutoffs(elements=('Ga', 'As'), unit='eV')
    Out[3]: (952.3985186095965, 7619.188148876772)

.. |pint| replace:: ``pint``
.. _pint: https://pint.readthedocs.io/en/stable/index.html
