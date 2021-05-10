
.. _troubleshooting:

###############
Troubleshooting
###############

.. _troubleshooting:automated-fail:

The automated install commands fail
===================================

These failures are often due to unstable internet connections causing the download of the pseudopotential archive from the web to fail.
In this case, it is possible to download the archive and metadata of the established family, transfer them to the machine where the pseudopotentials need to be installed and install from a directory.

.. TODO: Complete this section once we're settled on the implementation.

.. install the family manually from an archive that is already available on the local file system.

.. we provide the ``--download-only`` option, as well as the ``--archive`` and ``--metadata`` options which both have to be specified to install the pseudopotential family.
