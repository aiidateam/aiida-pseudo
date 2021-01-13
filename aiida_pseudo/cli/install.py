# -*- coding: utf-8 -*-
"""Command to install a pseudo potential family."""
import json
import os
import shutil
import tempfile

import click

from aiida.cmdline.utils import decorators, echo
from aiida.cmdline.params import options as options_core
from aiida.cmdline.params import types

from .params import options
from .root import cmd_root

URL_SSSP_BASE = 'https://legacy-archive.materialscloud.org/file/2018.0001/v4/'


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
@options.VERSION(type=click.Choice(['1.0', '1.1']), default='1.1', show_default=True)
@options.FUNCTIONAL(type=click.Choice(['PBE', 'PBEsol']), default='PBE', show_default=True)
@options.PROTOCOL(type=click.Choice(['efficiency', 'precision']), default='efficiency', show_default=True)
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
    from aiida_pseudo.common import units
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

            # Cutoffs are in Rydberg but need to be stored in the family in electronvolt.
            cutoffs[element] = {
                'cutoff_wfc': values['cutoff_wfc'] * units.RY_TO_EV,
                'cutoff_rho': values['cutoff_rho'] * units.RY_TO_EV,
            }

        family.description = description
        family.set_cutoffs({'normal': cutoffs})

        echo.echo_success(f'installed `{label}` containing {family.count()} pseudo potentials')


@cmd_install.command('pseudo-dojo')
@options.VERSION(type=click.Choice(['0.4', '1.0']), default='0.4', show_default=True)
@options.FUNCTIONAL(type=click.Choice(['PBE', 'PBEsol', 'LDA']), default='PBE', show_default=True)
@options.RELATIVISTIC(type=click.Choice(['SR', 'SR3plus', 'FR']), default='SR', show_default=True)
@options.PROTOCOL(type=click.Choice(['standard', 'stringent']), default='standard', show_default=True)
@options.PSEUDO_FORMAT(type=click.Choice(['psp8', 'upf', 'psml', 'jthxml']), default='psp8', show_default=True)
@options.DEFAULT_STRINGENCY(type=click.Choice(['low', 'normal', 'high']), default='normal', show_default=True)
@options.TRACEBACK()
@decorators.with_dbenv()
def cmd_install_pseudo_dojo(version, functional, relativistic, protocol, pseudo_format, default_stringency, traceback):
    """Install a PseudoDojo configuration.

    The PseudoDojo configuration will be automatically downloaded from pseudo-dojo.org to create a new
    `PseudoDojoFamily` subclass instance based on the specified pseudopotential format.
    """
    # pylint: disable=too-many-locals,too-many-arguments,too-many-statements
    import requests

    from aiida.common.files import md5_file
    from aiida.orm import Group, QueryBuilder
    from aiida_pseudo import __version__
    from aiida_pseudo.data.pseudo import JthXmlData, Psp8Data, PsmlData, UpfData
    from aiida_pseudo.groups.family import PseudoDojoConfiguration, PseudoDojoFamily

    from .utils import attempt, create_family_from_archive

    pseudo_type_mapping = {
        'jthxml': JthXmlData,
        'psp8': Psp8Data,
        'psml': PsmlData,
        'upf': UpfData,
    }

    # yapf: disable
    paw_configurations = (
        PseudoDojoConfiguration('1.0', 'PBE', 'SR', 'standard', 'jthxml'),
        PseudoDojoConfiguration('1.0', 'PBE', 'SR', 'stringent', 'jthxml'),
        PseudoDojoConfiguration('1.0', 'LDA', 'SR', 'standard', 'jthxml'),
        PseudoDojoConfiguration('1.0', 'LDA', 'SR', 'stringent', 'jthxml')
    )
    # yapf: enable

    try:
        pseudo_type = pseudo_type_mapping[pseudo_format]
    except KeyError:
        echo.echo_critical(f'{pseudo_format} is not a valid PseudoDojo pseudopotential format')

    configuration = PseudoDojoConfiguration(version, functional, relativistic, protocol, pseudo_format)
    label = PseudoDojoFamily.format_configuration_label(configuration)
    description = 'PseudoDojo v{} {} {} {} {} installed with aiida-pseudo v{}'.format(*configuration, __version__)

    if configuration not in PseudoDojoFamily.valid_configurations:
        echo.echo_critical('{} {} {} {} {} is not a valid PseudoDojo configuration'.format(*configuration))

    if QueryBuilder().append(PseudoDojoFamily, filters={'label': label}).first():
        echo.echo_critical(f'{PseudoDojoFamily.__name__}<{label}> is already installed')

    with tempfile.TemporaryDirectory() as dirpath:

        url_archive = PseudoDojoFamily.get_url_archive(label)
        url_metadata = PseudoDojoFamily.get_url_metadata(label)

        filepath_archive = os.path.join(dirpath, 'archive.tgz')
        filepath_metadata = os.path.join(dirpath, 'metadata.tgz')

        with attempt('downloading selected pseudo potentials archive... ', include_traceback=traceback):
            response = requests.get(url_archive)
            response.raise_for_status()
            with open(filepath_archive, 'wb') as handle:
                handle.write(response.content)
                handle.flush()
                description += f'\nArchive pseudos md5: {md5_file(filepath_archive)}'

        with attempt('unpacking archive and parsing pseudos... ', include_traceback=traceback):
            family = create_family_from_archive(PseudoDojoFamily, label, filepath_archive, pseudo_type=pseudo_type)

        with attempt('downloading selected pseudo potentials metadata archive... ', include_traceback=traceback):
            response = requests.get(url_metadata)
            response.raise_for_status()
            with open(filepath_metadata, 'wb') as handle:
                handle.write(response.content)
                handle.flush()
                description += f'\nPseudo metadata archive md5: {md5_file(filepath_metadata)}'

        with attempt('unpacking metadata archive and parsing metadata...', include_traceback=traceback):
            md5s, cutoffs = PseudoDojoFamily.parse_djrepos_from_archive(filepath_metadata, pseudo_type=pseudo_type)

        for element, md5 in md5s.items():
            if family.get_pseudo(element).md5 != md5:
                Group.objects.delete(family.pk)
                msg = f'md5 of pseudo for element {element} does not match that of the metadata {md5}'
                echo.echo_critical(msg)

        # The PAW configurations have missing cutoffs for the Lanthanides, which have ben replaced with a placeholder
        # value of `-1`. We replace these with the 1.5 * the maximum cutoff from the same stringency so that these
        # potentials are still usable, but this should be taken as a _rough_ approximation.
        # We check only the `cutoff_wfc` because `cutoff_rho` is not provided by PseudoDojo and is therefore
        # locally calculated in `PseudoDojoFamily.parse_djrepos_from_archive` as `2.0 * cutoff_wfc` for PAW.
        if configuration in paw_configurations:
            adjusted_cutoffs = {}
            for stringency, str_cutoffs in cutoffs.items():
                adjusted_cutoffs[stringency] = []
                max_cutoff_wfc = max([str_cutoffs[element]['cutoff_wfc'] for element in str_cutoffs])
                filler_cutoff_wfc = max_cutoff_wfc * 1.5
                for element, cutoff in str_cutoffs.items():
                    if cutoff['cutoff_wfc'] <= 0:
                        cutoffs[stringency][element]['cutoff_wfc'] = filler_cutoff_wfc
                        cutoffs[stringency][element]['cutoff_rho'] = 2.0 * filler_cutoff_wfc
                        adjusted_cutoffs[stringency].append(element)

            for stringency, elements in adjusted_cutoffs.items():
                msg = f'stringency `{stringency}` has missing recommended cutoffs for elements ' \
                    f'{", ".join(elements)}: as a substitute, 1.5 * the maximum cutoff of the stringency ' \
                    'was set for these elements. USE WITH CAUTION!'
                echo.echo_warning(msg)

        family.description = description
        family.set_cutoffs(cutoffs, default_stringency=default_stringency)

        echo.echo_success(f'installed `{label}` containing {family.count()} pseudo potentials')
