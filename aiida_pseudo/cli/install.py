# -*- coding: utf-8 -*-
"""Command to install a pseudo potential family."""
import os

import click

from aiida.cmdline.utils import decorators, echo
from aiida.cmdline.params import options as options_core

from .params import options
from .root import cmd_root

URL_SSSP_BASE = 'https://legacy-archive.materialscloud.org/file/2018.0001/v4/'


@cmd_root.group('install')
def cmd_install():
    """Install pseudo potential families."""


@cmd_install.command('family')
@options_core.DESCRIPTION(help='Description for the family.')
@options.FAMILY_TYPE()
@options.TRACEBACK()
@click.argument('filepath_archive', type=click.Path(exists=True))
@click.argument('label', type=click.STRING)
@decorators.with_dbenv()
def cmd_install_family(description, family_type, traceback, filepath_archive, label):
    """Install a standard pseudo potential family."""
    from .utils import attempt, create_family_from_archive

    with attempt('unpacking archive and parsing pseudos... ', include_traceback=traceback):
        family = create_family_from_archive(family_type, label, filepath_archive)

    family.description = description
    echo.echo_success('installed `{}` containing {} pseudo potentials'.format(label, family.count()))


@cmd_install.command('sssp')
@options.VERSION(type=click.Choice(['1.0', '1.1']), default='1.1')
@options.FUNCTIONAL(type=click.Choice(['PBE', 'PBEsol']), default='PBE')
@options.PROTOCOL(type=click.Choice(['efficiency', 'precision']), default='efficiency')
@options.TRACEBACK()
@decorators.with_dbenv()
def cmd_install_sssp(version, functional, protocol, traceback):
    """Install an SSSP configuration.

    The SSSP configuration will be automatically downloaded from the Materials Cloud Archive entry to create a new
    `SsspFamily`.
    """
    # pylint: disable=too-many-locals
    import requests
    import tempfile

    from aiida.common.files import md5_file
    from aiida.orm import QueryBuilder

    from aiida_pseudo import __version__
    from aiida_pseudo.groups.family import SsspConfiguration, SsspFamily
    from .utils import attempt, create_family_from_archive

    configuration = SsspConfiguration(version, functional, protocol)
    label = SsspFamily.format_configuration_label(configuration)
    description = 'SSSP v{} {} {} installed with aiida-pseudo v{}'.format(*configuration, __version__)

    if configuration not in SsspFamily.valid_configurations:
        echo.echo_critical('{} {} {} is not a valid SSSP configuration'.format(*configuration))

    if QueryBuilder().append(SsspFamily, filters={'label': label}).first():
        echo.echo_critical('{}<{}> is already installed'.format(SsspFamily.__name__, label))

    with tempfile.TemporaryDirectory() as dirpath:

        url_archive = '{}/SSSP_{}_{}_{}.tar.gz'.format(URL_SSSP_BASE, version, functional, protocol)
        filepath_archive = os.path.join(dirpath, 'archive.tar.gz')

        with attempt('downloading selected pseudo potentials archive... ', include_traceback=traceback):
            response = requests.get(url_archive)
            response.raise_for_status()
            with open(filepath_archive, 'wb') as handle:
                handle.write(response.content)
                handle.flush()
                description += '\nArchive pseudos md5: {}'.format(md5_file(filepath_archive))

        with attempt('unpacking archive and parsing pseudos... ', include_traceback=traceback):
            family = create_family_from_archive(SsspFamily, label, filepath_archive)

        family.description = description
        echo.echo_success('installed `{}` containing {} pseudo potentials'.format(label, family.count()))
