# -*- coding: utf-8 -*-
"""Command to install a pseudo potential family."""
import json
import os
import shutil
import tempfile

import click
from aiida.cmdline.params import options as options_core
from aiida.cmdline.params import types
from aiida.cmdline.utils import decorators, echo

from .params import options
from .root import cmd_root

URL_SSSP_BASE = 'https://legacy-archive.materialscloud.org/file/2018.0001/v4/'
URL_PSEUDODOJO_BASE = 'http://www.pseudo-dojo.org/pseudos/'
URL_PSEUDODOJO_METADATA_BASE = 'https://raw.githubusercontent.com/abinit/pseudo_dojo/master/pseudo_dojo/pseudos/'


@cmd_root.group('install')
def cmd_install():
    """Install pseudo potential families."""


@cmd_install.command('family')
@click.argument('archive', type=types.FileOrUrl(mode='rb'))
@click.argument('label', type=click.STRING)
@options_core.DESCRIPTION(help='Description for the family.')
@options.ARCHIVE_FORMAT()
@options.FAMILY_TYPE()
@options.TRACEBACK()
@decorators.with_dbenv()
def cmd_install_family(archive, label, description, archive_format, family_type, traceback):  # pylint: disable=too-many-arguments
    """Install a standard pseudo potential family from an ARCHIVE on the local file system or from a URL.

    The command will attempt to infer the archive format from the filename extension of the ARCHIVE. If this fails, the
    archive format can be specified explicitly with the archive format option, which will also display which formats
    are supported.

    By default, the command will create a base `PseudoPotentialFamily`, but the type can be changed with the family
    type option. If the base type is used, the pseudo potential files in the archive *have* to have filenames that
    strictly follow the format `ELEMENT.EXTENSION`, because otherwise the element cannot be determined automatically.
    """
    from .utils import attempt, create_family_from_archive

    # The `archive` is now either a `http.client.HTTPResponse` or a normal filelike object, so we get the original file
    # name in a different way.
    try:
        suffix = os.path.basename(archive.url)
    except AttributeError:
        suffix = os.path.basename(archive.name)

    # Write the content of the archive to a temporary file, because `create_family_from_archive` does currently not
    # accept filelike objects because the underlying `shutil.unpack_archive` does not. Likewise, `unpack_archive` will
    # attempt to deduce the archive format from the filename extension, so it is important we maintain the original
    # filename. Of course if this fails, users can specify the archive format explicitly wiht the corresponding option.
    with tempfile.NamedTemporaryFile(mode='w+b', suffix=suffix) as handle:
        shutil.copyfileobj(archive, handle)
        handle.flush()

        with attempt('unpacking archive and parsing pseudos... ', include_traceback=traceback):
            family = create_family_from_archive(family_type, label, handle.name, fmt=archive_format)

    family.description = description
    echo.echo_success(f'installed `{label}` containing {family.count()} pseudo potentials')


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
    from aiida.common.files import md5_file
    from aiida.orm import Group, QueryBuilder
    from aiida_pseudo import __version__
    from aiida_pseudo.groups.family import SsspConfiguration, SsspFamily

    from .utils import attempt, create_family_from_archive

    configuration = SsspConfiguration(version, functional, protocol)
    label = SsspFamily.format_configuration_label(configuration)
    description = f'SSSP v{version} {functional} {protocol} installed with aiida-pseudo v{__version__}'

    if configuration not in SsspFamily.valid_configurations:
        echo.echo_critical(f'{version} {functional} {protocol} is not a valid SSSP configuration')

    if QueryBuilder().append(SsspFamily, filters={'label': label}).first():
        echo.echo_critical(f'{SsspFamily.__name__}<{label}> is already installed')

    with tempfile.TemporaryDirectory() as dirpath:

        url_archive = f'{URL_SSSP_BASE}/SSSP_{version}_{functional}_{protocol}.tar.gz'
        filepath_archive = os.path.join(dirpath, 'archive.tar.gz')

        url_metadata = f'{URL_SSSP_BASE}/SSSP_{version}_{functional}_{protocol}.json'
        filepath_metadata = os.path.join(dirpath, 'metadata.json')

        with attempt('downloading selected pseudo potentials archive... ', include_traceback=traceback):
            response = requests.get(url_archive)
            response.raise_for_status()
            with open(filepath_archive, 'wb') as handle:
                handle.write(response.content)
                handle.flush()
                description += f'\nArchive pseudos md5: {md5_file(filepath_archive)}'

        with attempt('downloading selected pseudo potentials metadata... ', include_traceback=traceback):
            response = requests.get(url_metadata)
            response.raise_for_status()
            with open(filepath_metadata, 'a+b') as handle:
                handle.write(response.content)
                handle.flush()
                handle.seek(0)
                metadata = json.load(handle)
                description += f'\nPseudo metadata md5: {md5_file(filepath_metadata)}'

        with attempt('unpacking archive and parsing pseudos... ', include_traceback=traceback):
            family = create_family_from_archive(SsspFamily, label, filepath_archive)

        cutoffs = {}

        for element, values in metadata.items():
            if family.get_pseudo(element).md5 != values['md5']:
                Group.objects.delete(family.pk)
                msg = f"md5 of pseudo for element {element} does not match that of the metadata {values['md5']}"
                echo.echo_critical(msg)

            cutoffs[element] = {'cutoff_wfc': values['cutoff_wfc'], 'cutoff_rho': values['cutoff_rho']}

        family.description = description
        family.set_cutoffs({'normal': cutoffs})

        echo.echo_success(f'installed `{label}` containing {family.count()} pseudo potentials')


@cmd_install.command('pseudo-dojo')
@options.VERSION(type=click.Choice(['03', '04']), default='04')
@options.FUNCTIONAL(type=click.Choice(['pbe', 'pbesol', 'lda']), default='pbe')
@options.RELATIVISTIC(type=click.Choice(['sr', 'sr3plus', 'fr']), default='sr')
@options.PROTOCOL(type=click.Choice(['standard', 'stringent']), default='standard')
@options.PSEUDO_FORMAT(type=click.Choice(['psp8', 'upf', 'psml']), default='psp8')
@options.TRACEBACK()
@decorators.with_dbenv()
def cmd_install_pseudo_dojo(version, functional, relativistic, protocol, pseudo_format, traceback):
    """Install a PseudoDojo configuration.

    The PseudoDojo configuration will be automatically downloaded from pseudo-dojo.org to create a new
    `PseudoDojoFamily` subclass instance based on the specified pseudopotential format.
    """
    # pylint: disable=too-many-locals,too-many-arguments,too-many-statements
    import requests
    from aiida.common.files import md5_file
    from aiida.orm import Group, QueryBuilder
    from aiida_pseudo import __version__
    from aiida_pseudo.groups.family import (
        PseudoDojoConfiguration, PseudoDojoPsmlFamily, PseudoDojoPsp8Family, PseudoDojoUpfFamily
    )

    from .utils import attempt, create_family_from_archive

    cls_mapping = {
        'psp8': PseudoDojoPsp8Family,
        'psml': PseudoDojoPsmlFamily,
        'upf': PseudoDojoUpfFamily,
    }

    metadata_urls = {
        'nc-sr-04_pbe_standard': 'ONCVPSP-PBE-PDv0.4/standard.djson',
        'nc-sr-04_pbe_stringent': 'ONCVPSP-PBE-PDv0.4/stringent.djson',
        'nc-sr-04_pbesol_standard': 'ONCVPSP-PBEsol-PDv0.4/standard.djson',
        'nc-sr-04_pbesol_stringent': 'ONCVPSP-PBEsol-PDv0.4/stringent.djson',
        # 'nc-fr-04_pbe_standard': 'ONCVPSP-PBE-FR-PDv0.4/standard.djson',  # md5 does not match
        # 'nc-fr-04_pbe_stringent': 'ONCVPSP-PBE-FR-PDv0.4/stringent.djson'  # missing elements
    }

    try:
        cls = cls_mapping[pseudo_format]
    except KeyError:
        echo.echo_critical(f'{pseudo_format} is not a valid PseudoDojo pseudopotential format')

    configuration = PseudoDojoConfiguration(version, functional, relativistic, protocol)
    label = cls.format_configuration_label(configuration)
    description = f'PseudoDojo v{version} {functional} {relativistic} {protocol} {pseudo_format} ' + \
        f'installed with aiida-pseudo v{__version__}'

    if configuration not in cls.valid_configurations:
        echo.echo_critical(
            f'{version} {functional} {relativistic} {protocol}is not a valid PseudoDojo configuration for {cls}'
        )

    if QueryBuilder().append(cls, filters={'label': label}).first():
        echo.echo_critical(f'{cls.__name__}<{label}> is already installed')

    with tempfile.TemporaryDirectory() as dirpath:

        if relativistic == 'sr3plus':
            url_archive = f'{URL_PSEUDODOJO_BASE}/nc-sr-{version}-3plus_{functional}_{protocol}_{pseudo_format}.tgz'
        else:
            url_archive = f'{URL_PSEUDODOJO_BASE}/nc-{relativistic}-{version}_{functional}_{protocol}_' + \
                f'{pseudo_format}.tgz'

        filepath_archive = os.path.join(dirpath, 'archive.tgz')

        with attempt('downloading selected pseudo potentials archive... ', include_traceback=traceback):
            response = requests.get(url_archive)
            response.raise_for_status()
            with open(filepath_archive, 'wb') as handle:
                handle.write(response.content)
                handle.flush()
                description += f'\nArchive pseudos md5: {md5_file(filepath_archive)}'

        with attempt('unpacking archive and parsing pseudos... ', include_traceback=traceback):
            family = create_family_from_archive(cls, label, filepath_archive)

        family.description = description
        label_metadata = f'nc-{relativistic}-{version}_{functional}_{protocol}'

        if label_metadata in metadata_urls:
            url_metadata = f'{URL_PSEUDODOJO_METADATA_BASE}/{metadata_urls[label_metadata]}'
            filepath_metadata = os.path.join(dirpath, 'metadata.json')

            with attempt('downloading selected pseudo potentials metadata... ', include_traceback=traceback):
                response = requests.get(url_metadata)
                response.raise_for_status()
                with open(filepath_metadata, 'a+b') as handle:
                    handle.write(response.content)
                    handle.flush()
                    handle.seek(0)
                    metadata = json.load(handle)
                    description += f'\nPseudo metadata md5: {md5_file(filepath_metadata)}'

            cutoffs = {}

            for element, values in metadata['pseudos_metadata'].items():

                if family.get_pseudo(element).md5 != values['md5']:
                    Group.objects.delete(family.pk)
                    msg = f"md5 of pseudo for element {element} does not match that of the metadata {values['md5']}"
                    echo.echo_critical(msg)

                for stringency, element_cutoffs in values['hints'].items():
                    # All supported PseudoDojo potentials are NC, so we take dual of 8.0
                    cutoffs.setdefault(stringency, {})[element] = {
                        'cutoff_wfc': element_cutoffs['ecut'],
                        'cutoff_rho': element_cutoffs['ecut'] * 8.0
                    }

            family.set_cutoffs(cutoffs=cutoffs, default_stringency='normal')

        echo.echo_success(f'installed `{label}` containing {family.count()} pseudo potentials')
