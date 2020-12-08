# `aiida-pseudo`

AiiDA plugin that simplifies working with pseudo potentials.

[![PyPI version](https://badge.fury.io/py/aiida-pseudo.svg)](https://badge.fury.io/py/aiida-pseudo)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/aiida-pseudo.svg)](https://pypi.python.org/pypi/aiida-pseudo/)
[![Build Status](https://github.com/aiidateam/aiida-pseudo/workflows/continuous-integration/badge.svg?event=push)](https://github.com/aiidateam/aiida-pseudo/actions)
[![Docs status](https://readthedocs.org/projects/aiida-pseudo/badge)](http://aiida-pseudo.readthedocs.io/)


## Getting started

The easiest way of getting started using `aiida-pseudo` is to use the command line interface that ships with it.
For example, to install a configuration of the [SSSP](https://www.materialscloud.org/discover/sssp/table/efficiency), just run:

    aiida-pseudo install sssp

The version, functional, and protocol can be controlled with various options; use `aiida-pseudo install sssp --help` to see their description.
Installed pseudopotential families can be listed using:

    aiida-pseudo list

Any pseudopotential family installed can be loaded like any other `Group` using the `load_group` utility from `aiida-core`.
Once loaded, it is easy to get the pseudopotentials for a given element or set of elements:

```python
from aiida.orm import load_group
family = load_group('SSSP/1.1/PBE/efficiency')
pseudo = family.get_pseudo(element='Ga')  # Returns a single pseudo
pseudos = family.get_pseudos(elements=('Ga', 'As'))  # Returns a dictionary of pseudos where the keys are the elements
```

If you have a `StructureData` node, the `get_pseudos` method also accepts that as an argument to automatically retrieve all the pseudopotentials required for that structure:

    structure = load_node()  # Load the structure from database or create one
    pseudos = family.get_pseudos(structure=structure)

If you use `aiida-quantumespresso` the `pseudos` dictionary returned by `get_pseudos` can be directly used as an input for `PwCalculation`s.

## Design

The plugin is centered around two concepts: pseudopotentials and pseudopotential families.
The two concepts are further explained below, especially focusing on how they are implemented in `aiida-pseudo`, what assumptions are made, and what the limitations are.

### Pseudopotentials

Pseudopotentials are implemented as [data plugins](https://aiida-core.readthedocs.io/en/latest/topics/data_types.html#creating-a-data-plugin), and the base class is `PseudoPotentialData`.
Pseudopotentials are assumed to be defined by a single file on disk and represent a single chemical element.
As such, each pseudopotential node, _has_ to have two attributes: the md5 of the file that it represents and the symbol of chemical element that the pseudopotential describes.
The latter follows IUPAC naming conventions as used in the module `aiida.common.constants.elements` of `aiida-core`.

The `PseudoPotentialData` functions as a base class and does not represent an actual existing pseudopotential format.
It _is_ possible to create a family of `PseudoPotentialData` nodes, but since the element cannot be parsed from the file content itself, it will have to be done from the _filename_, so the filename _has_ to have the format `CHEMICAL_SYMBOL.EXTENSION`, for example `Ar.pseudo`.
Since the `PseudoPotentialData` class does not have any features tailored to specific formats, as do the classes which inherit from it (e.g. `UpfData` for UPF-formatted pseudopotentials), this class is mostly useful for development.

The plugin comes with a variety of pseudopotential subtypes that represent various common pseudopotential formats, such as UPF, PSF, PSML and PSP8.
The corresponding data plugins implement how the element and other data are parsed from a pseudopotential file with such a format.
A new pseudopotential node can be created by instantiating the corresponding plugin class:

```python
from aiida import plugins

UpfData = plugins.DataFactory('pseudo.upf')

with open('path/to/pseudo.upf', 'rb') as stream:
    pseudo = UpfData(stream)
```

Note, the pseudopotential constructor expects a stream of bytes, so be sure to open the file handle with the `'rb'` mode.
Alternatively, you can also use the `get_or_create` classmethod, which will first search the database to check if a pseudopotential of the exact same type and content already exists.
If that is the case, that node is returned, otherwise a new instance is created:

```python
from aiida import plugins

UpfData = plugins.DataFactory('pseudo.upf')

with open('path/to/pseudo.upf', 'rb') as stream:
    pseudo = UpfData.get_or_create(stream)
```

If a new node was created, it will be unstored.
Note that if more than one pseudopotential in the database is matched, a random one is selected and returned.


### Families

Having loose pseudopotentials floating around is not very practical, so groups of related pseudopotentials can be organized into "families", which are implemented as group plugins with the base class  `PseudoPotentialFamily`.
A family class can in principle support many pseudopotential formats, however, a family instance can only contain pseudopotentials of a single format.
For example, the `PseudoPotentialFamily` class supports all of the pseudopotential formats that are supported by this plugin.
However, any instance can only contain pseudopotentials of the same format (e.g. _all_ UPF or _all_ PSP8, not a mixture).
In contrast, the `SsspFamily` only supports the `UpfData` format.

A pseudopotential family can be constructed manually, by first constructing the class instance and then adding pseudopotential data nodes to it:

```python
from aiida import plugins

UpfData = plugins.DataFactory('pseudo.upf')
PseudoPotentialFamily = plugins.GroupFactory('pseudo')

pseudos = []

for filepath in ['Ga.upf', 'As.upf']:
    with open(filepath, 'rb') as stream:
        pseudo = UpfData(stream)
        pseudos.append(pseudo)

family = PseudoPotentialFamily(label='pseudos/upf').store()
family.append(pseudos)
```

Note that as with any `Group`, it has to be stored before nodes can be added.
If you have a folder on disk that contains various pseudopotentials for different elements, there is an even easier way to create the family automatically:

```python
from aiida import plugins

UpfData = plugins.DataFactory('pseudo.upf')
PseudoPotentialFamily = plugins.GroupFactory('pseudo')

family = PseudoPotentialFamily('path/to/pseudos', 'pseudos/upf', pseudo_type=UpfData)
```

The plugin is not able to reliably deduce the format of the pseudopotentials contained in the folder, so one should indicate what data type to use with the `pseudo_type` argument.
The exception is when the family class only supports a single pseudo type, such as for the `SsspFamily`, in which case that type will automatically be selected.
Subclasses of supported pseudo types are also accepted.
For example, the base class `PseudoPotentialFamily` supports pseudopotentials of the `PseudoPotentialData` type.
Because all more specific pseudopotential types are subclasses of `PseudoPotentialData`, the `PseudoPotentialFamily` class accepts all of them.


### Recommended cutoffs

Certain pseudopotential family types, such as the `SsspFamily`, provide recommended cutoff values for wave functions and charge density in plane-wave codes.
These cutoffs are always in units of electronvolt.
The recommended cutoffs for a set of elements or a `StructureData` can be retrieved from the family as follows:

```python
family = load_group('SSSP/1.1/PBE/efficiency')
cutoffs = family.get_recommended_cutoffs(elements=('Ga', 'As'))  # From a tuple or list of element symbols
cutoffs = family.get_recommended_cutoffs(structure=load_node(<IDENTIFIER>))  # From a `StructureData` node
```
