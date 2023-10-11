.. _how-to:

#############
How-To Guides
#############

.. _how-to:install_automated:

Automated install
=================

The easiest way to install a pseudopotential family with ``aiida-pseudo`` is by using the command line interface.
For example, to install a configuration of the `Standard solid-state pseudopotentials (SSSP) <https://www.materialscloud.org/discover/sssp/table/efficiency>`_, just run:

.. code-block:: console

    $ aiida-pseudo install sssp

The version, functional, and protocol can be controlled with various options; use ``aiida-pseudo install sssp --help`` to see their description.

Besides the `SSSP`_, the pseudopotentials from the `Pseudo Dojo`_ library are also supported for automated installation:

.. code-block:: console

    $ aiida-pseudo install pseudo-dojo

Similar to the `SSSP`_ pseudopotential family, the options can be used to set version, functional, and protocol.
Moreover, the format of the pseudopotentials can be specified, as well as the default stringency.
Use ``aiida-pseudo install pseudo-dojo --help`` for more information.

.. note::

    In case you are unable to use these automated commands because of connection issues, please consult the :ref:`troubleshooting section <troubleshooting:automated-fail>`.

.. _how-to:install_archive:

Installing from archive or folder
=================================

In case the pseudopotential family you want to use is not supported, you can install the pseudopotential family manually with the following command:

.. code-block:: console

    $ aiida-pseudo install family <ARCHIVE_OR_FOLDER> <LABEL>

where ``<ARCHIVE_OR_FOLDER>`` should be replaced with the archive or folder that contains the pseudopotential files and ``<LABEL>`` with the label to give to the family.

The unpacked archive should contain nothing else besides the pseudopotential files (i.e. no other files or folders) and the pseudopotentials should be present at the top level (not nested in subfolders).
The command expects pseudopotential files to have the format ``ELEMENT.EXTENSION`` such that it can automatically parse the element for each pseudopotential.
If the files do not respect this naming convention, the following error message is displayed:

.. code-block:: console

    Critical: ``PseudoPotentialData`` constructor did not define the element and could not parse a valid element symbol from the filename `{filename}` either.
    It should have the format ``ELEMENT.EXTENSION``.

Instead of renaming the files, specify the format of the pseudopotentials so the command can attempt to parse the element from the file itself, as explained :ref:`here <how-to:install_archive:pseudopotential_format>`.

The command will attempt to automatically detect the compression format of the archive.
If this fails, you can specify the format manually with the ``--archive-format/-f`` option, for example, for a ``.tar.gz`` archive:

.. code-block:: console

    $ aiida-pseudo install family <ARCHIVE> <LABEL> -f gztar

The valid archive formats are those defined by the `shutil.unpack_archive <https://docs.python.org/3/library/shutil.html#shutil.unpack_archive>`_ function of the standard Python library.

.. _how-to:install_archive:pseudopotential_format:

Pseudopotential format
----------------------

By default, the pseudopotentials will be installed as ``PseudoPotentialData`` data types.
However, often plugins will require pseudopotentials to adhere to a specific format, such as UPF, PSF, PSML or PSP8.
This format can be specified using the ``--pseudo-type/-P`` option, for example to install the pseudopotentials in the UPF format:

.. code-block:: console

    $ aiida-pseudo install family <ARCHIVE> <LABEL> -P pseudo.upf

The available formats can be shown with the command:

.. code-block:: console

    $ verdi plugin list aiida.data | grep pseudo

.. _how-to:install_archive:family_type:

Pseudopotential family type
---------------------------

By default, the command will create a family of the base pseudopotential family type ``PseudoPotentialFamily``.
If you want to create a more specific family, for example an ``CutoffsPseudoPotentialFamily``, you can provide the corresponding entry point to the ``--family-type/-F`` option:

.. code-block:: console

    $ aiida-pseudo install family <ARCHIVE> <LABEL> -F pseudo.family.cutoffs

The available pseudopotential family classes can be listed with the command:

.. code-block:: console

    $ verdi plugin list aiida.groups | grep pseudo.family

.. important::

    The ``pseudo.family.sssp`` and ``pseudo.family.pseudo_dojo`` family types are blacklisted since they have their own :ref:`dedicated install commands <how-to:install_automated>` in ``aiida-pseudo install sssp`` and ``aiida-pseudo install pseudo-dojo``, respectively.
    In case you are unable to use these commands because of connection issues, please consult the :ref:`troubleshooting section <troubleshooting:automated-fail>`.

Adding recommended cutoffs
--------------------------

The functionality of some plugins, such as the workflow protocols of ``aiida-quantumespresso``, may rely on recommended cutoffs to be defined for the pseudopotential family.
Unlike the automated install methods for those family types, manually installing a pseudopotential family from an archive or folder will not define recommended cutoffs and as a result it may not be usable for these specific functionalities.

Recommended cutoffs can be manually defined for existing pseudopotential families using:

.. code-block:: console

    $ aiida-pseudo family cutoffs set -s <STRINGENCY> <FAMILY> <CUTOFFS>

where ``<STRINGENCY>`` is a string that defines the recommended cutoffs, ``<FAMILY>`` is the identifier of the pseudopotential family group and ``<CUTOFFS>`` is the path to a ``.json`` file that has the following structure:

.. code-block::

    {
        "Ag": {
            "cutoff_wfc": 50.0,
            "cutoff_rho": 200.0
        },
        ...
    }

.. important::

    The ``PseudoPotentialFamily`` base family type does not support setting recommended cutoffs.
    To be able to use this feature for a manually installed family, install it as a ``CutoffsPseudoPotentialFamily`` as expained :ref:`here <how-to:install_archive:family_type>`.


.. _how-to:install_archive:migrate-legacy:

Migrate from legacy ``UpfData`` from ``aiida-core``
---------------------------------------------------

Since the earliest versions, ``aiida-core`` provided its own data plugin ``UpfData`` (with the entry point ``core.upf``) to support UPF pseudopotentials as well as a concept of a pseudopotential family.
That ``aiida.orm.nodes.data.upf`` module which defined the ``UpfData`` class and the ``verdi data core.upf`` command of ``aiida-core`` are now deprecated.
This migration guide provides instructions how to replace the deprecated functionality with ``aiida-pseudo``.

``UpfData``
...........

The ``UpfData`` class is replaced by the class of the same name from the ``aiida-pseudo`` package.
The import ``from aiida.orm.nodes.data.upf import UpfData`` can be replaced by ``from aiida_pseudo.data.pseudo import UpfData``.
The constructor of the two classes is almost identical, so this should be a drop-in replacement.

``verdi data core.upf``
.......................

====================================    ===============================
Deprecated                              Replacement
====================================    ===============================
``verdi data core.upf uploadfamily``    ``aiida-pseudo install family``
``verdi data core.upf listfamilies``    ``aiida-pseudo list``
``verdi data core.upf exportfamily``    Not yet implemented
``verdi data core.upf import``          Not yet implemented
``verdi data core.upf export``          Not yet implemented
====================================    ===============================


Migrating existing families
...........................

To migrate an existing UPF family from ``aiida-core``, use the following snippet:

.. code-block:: python

    from aiida.orm import load_group
    from aiida_pseudo.data.pseudo.upf import UpfData
    from aiida_pseudo.groups.family import PseudoPotentialFamily

    label = 'family-legacy'  # Replace this with the label of the family you want to migrate
    label_new = 'family-migrated' # This will be the label of the migrated family

    legacy_family = load_group(label)
    family = PseudoPotentialFamily(label=label_new).store()
    pseudos = []

    for legacy_pseudo in legacy_family.nodes:
        with legacy_pseudo.open(mode='rb') as handle:
            pseudos.append(UpfData(handle, filename=legacy_pseudo.filename).store())

    family.add_nodes(pseudos)
    print(f'Migrated `{legacy_family}` to `{family}`.')

If the snippet finishes successfully, you can run ``verdi group list -a`` which should show the original and migrated groups:

.. code-block::

    user@machine$ verdi group list -a
      PK  Label                       Type string         User
    ----  --------------------------  ------------------  ----------------------
       1  family-legacy               core.upf            user@email.com
       2  family-migrated             pseudo.family       user@email.com

.. tip::

    It is recommended to use a different label for the migrated family.
    Although it is possible to use the same label (since the type string is different and the uniqueness constraint will not be violated) the groups can no longer be distinguished solely by their label.
    This means, for example, that ``load_group('family-legacy')`` will raise a ``MultipleObjectsError`` since both groups will be matched.


.. _SSSP: https://www.materialscloud.org/discover/sssp/table/efficiency
.. _Pseudo Dojo: http://www.pseudo-dojo.org/
