
.. _troubleshooting:

###############
Troubleshooting
###############

.. _troubleshooting:automated-fail:

The automated install commands fail
===================================

These failures are often due to unstable internet connections causing the download of the pseudopotential archive from the web to fail.
In this case, it is possible to download an ``.aiida_pseudo`` archive of the established family on a machine with a stable internet connection, transfer it to the machine where the pseudopotentials need to be installed and install directly from the archive.
To download the archive, use the ``--download-only`` option:

.. code-block:: console

    $ aiida-pseudo install sssp --download-only
    Report: downloading patch versions information...  [OK]
    Report: downloading selected pseudopotentials archive...  [OK]
    Report: downloading selected pseudopotentials metadata...  [OK]
    Success: Pseudopotential archive written to: SSSP_1.1_PBE_efficiency.aiida_pseudo

The downloaded archive can be installed through the ``--from-download`` option of the corresponding install command:

.. code-block:: console

    $ aiida-pseudo install sssp --from-download SSSP_1.1_PBE_efficiency.aiida_pseudo
    Report: unpacking archive and parsing pseudos...  [OK]
    Success: installed `SSSP/1.1/PBE/efficiency` containing 85 pseudopotentials.
