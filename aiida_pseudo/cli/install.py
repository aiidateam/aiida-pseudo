# -*- coding: utf-8 -*-
"""Command to install a pseudo potential family."""
import json
import os
import pathlib
import shutil
import tempfile

import click

from aiida.cmdline.utils import decorators, echo
from aiida.cmdline.params import options as options_core
from aiida.cmdline.params import types

from aiida_pseudo.groups.family import PseudoDojoConfiguration, SsspConfiguration
from .params import options
from .root import cmd_root


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
            family = create_family_from_archive(family_type, label, pathlib.Path(handle.name), fmt=archive_format)

    family.description = description
    echo.echo_success(f'installed `{label}` containing {family.count()} pseudo potentials')


def download_sssp(
    configuration: SsspConfiguration,
    filepath_archive: pathlib.Path,
    filepath_metadata: pathlib.Path,
    traceback: bool = False
) -> None:
    """Download the pseudopotential archive and metadata for an SSSP configuration to a path on disk.

    :param configuration: the SSSP configuration to download.
    :param filepath_archive: absolute filepath to write the pseudopotential archive to.
    :param filepath_metadata: absolute filepath to write the metadata file to.
    :param traceback: boolean, if true, print the traceback when an exception occurs.
    """
    import requests

    from aiida_pseudo.groups.family import SsspFamily
    from .utils import attempt

    url_sssp_base = 'https://legacy-archive.materialscloud.org/file/2018.0001/v4/'
    url_archive = f"{url_sssp_base}/{SsspFamily.format_configuration_filename(configuration, 'tar.gz')}"
    url_metadata = f"{url_sssp_base}/{SsspFamily.format_configuration_filename(configuration, 'json')}"

    with attempt('downloading selected pseudo potentials archive... ', include_traceback=traceback):
        response = requests.get(url_archive)
        response.raise_for_status()
        with open(filepath_archive, 'wb') as handle:
            handle.write(response.content)
            handle.flush()

    with attempt('downloading selected pseudo potentials metadata... ', include_traceback=traceback):
        response = requests.get(url_metadata)
        response.raise_for_status()
        with open(filepath_metadata, 'wb') as handle:
            handle.write(response.content)
            handle.flush()


def download_pseudo_dojo(
    configuration: SsspConfiguration,
    filepath_archive: pathlib.Path,
    filepath_metadata: pathlib.Path,
    traceback: bool = False
) -> None:
    """Download the pseudopotential archive and metadata for a PseudoDojo configuration to a path on disk.

    :param configuration: the PseudoDojo configuration to download.
    :param filepath_archive: absolute filepath to write the pseudopotential archive to.
    :param filepath_metadata: absolute filepath to write the metadata archive to.
    :param traceback: boolean, if true, print the traceback when an exception occurs.
    """
    import requests

    from aiida_pseudo.groups.family import PseudoDojoFamily
    from .utils import attempt

    label = PseudoDojoFamily.format_configuration_label(configuration)
    url_archive = PseudoDojoFamily.get_url_archive(label)
    url_metadata = PseudoDojoFamily.get_url_metadata(label)

    with attempt('downloading selected pseudo potentials archive... ', include_traceback=traceback):
        response = requests.get(url_archive)
        response.raise_for_status()
        with open(filepath_archive, 'wb') as handle:
            handle.write(response.content)
            handle.flush()

    with attempt('downloading selected pseudo potentials metadata archive... ', include_traceback=traceback):
        response = requests.get(url_metadata)
        response.raise_for_status()
        with open(filepath_metadata, 'wb') as handle:
            handle.write(response.content)
            handle.flush()


@cmd_install.command('sssp')
@options.VERSION(type=click.Choice(['1.0', '1.1']), default='1.1', show_default=True)
@options.FUNCTIONAL(type=click.Choice(['PBE', 'PBEsol']), default='PBE', show_default=True)
@options.PROTOCOL(type=click.Choice(['efficiency', 'precision']), default='efficiency', show_default=True)
@options.DOWNLOAD_ONLY()
@options.TRACEBACK()
@decorators.with_dbenv()
def cmd_install_sssp(version, functional, protocol, download_only, traceback):
    """Install an SSSP configuration.

    The SSSP configuration will be automatically downloaded from the Materials Cloud Archive entry to create a new
    `SsspFamily`.
    """
    # pylint: disable=too-many-locals
    from aiida.common.files import md5_file
    from aiida.orm import Group, QueryBuilder

    from aiida_pseudo import __version__
    from aiida_pseudo.groups.family import SsspFamily
    from .utils import attempt, create_family_from_archive

    configuration = SsspConfiguration(version, functional, protocol)
    label = SsspFamily.format_configuration_label(configuration)
    description = f'SSSP v{version} {functional} {protocol} installed with aiida-pseudo v{__version__}'

    if configuration not in SsspFamily.valid_configurations:
        echo.echo_critical(f'{version} {functional} {protocol} is not a valid SSSP configuration')

    if not download_only and QueryBuilder().append(SsspFamily, filters={'label': label}).first():
        echo.echo_critical(f'{SsspFamily.__name__}<{label}> is already installed')

    with tempfile.TemporaryDirectory() as dirpath:

        dirpath = pathlib.Path(dirpath)
        filepath_archive = dirpath / 'archive.tar.gz'
        filepath_metadata = dirpath / 'metadata.json'

        download_sssp(configuration, filepath_archive, filepath_metadata, traceback)

        description += f'\nArchive pseudos md5: {md5_file(filepath_archive)}'
        description += f'\nPseudo metadata md5: {md5_file(filepath_metadata)}'

        if download_only:
            for filepath in [filepath_archive, filepath_metadata]:
                filepath_target = pathlib.Path.cwd() / filepath.name
                if filepath_target.exists():
                    echo.echo_warning(f'the file `{filepath_target}` already exists, skipping.')
                else:
                    # Cannot use ``pathlib.Path.rename`` because this will fail if it moves across file systems.
                    shutil.move(filepath, filepath_target)
                    echo.echo_success(f'`{filepath_target.name}` written to the current directory.')
            return

        with open(filepath_metadata, 'rb') as handle:
            handle.seek(0)
            metadata = json.load(handle)

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
        family.set_cutoffs(cutoffs, 'normal', unit='Ry')

        echo.echo_success(f'installed `{label}` containing {family.count()} pseudo potentials')


@cmd_install.command('pseudo-dojo')
@options.VERSION(type=click.Choice(['0.4', '1.0']), default='0.4', show_default=True)
@options.FUNCTIONAL(type=click.Choice(['PBE', 'PBEsol', 'LDA']), default='PBE', show_default=True)
@options.RELATIVISTIC(type=click.Choice(['SR', 'SR3plus', 'FR']), default='SR', show_default=True)
@options.PROTOCOL(type=click.Choice(['standard', 'stringent']), default='standard', show_default=True)
@options.PSEUDO_FORMAT(type=click.Choice(['psp8', 'upf', 'psml', 'jthxml']), default='psp8', show_default=True)
@options.DEFAULT_STRINGENCY(type=click.Choice(['low', 'normal', 'high']), default='normal', show_default=True)
@options.DOWNLOAD_ONLY()
@options.TRACEBACK()
@decorators.with_dbenv()
def cmd_install_pseudo_dojo(
    version, functional, relativistic, protocol, pseudo_format, default_stringency, download_only, traceback
):
    """Install a PseudoDojo configuration.

    The PseudoDojo configuration will be automatically downloaded from pseudo-dojo.org to create a new
    `PseudoDojoFamily` subclass instance based on the specified pseudopotential format.
    """
    # pylint: disable=too-many-locals,too-many-arguments,too-many-branches,too-many-statements
    from aiida.common.files import md5_file
    from aiida.orm import Group, QueryBuilder
    from aiida_pseudo import __version__
    from aiida_pseudo.data.pseudo import JthXmlData, Psp8Data, PsmlData, UpfData
    from aiida_pseudo.groups.family import PseudoDojoFamily

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

    if not download_only and QueryBuilder().append(PseudoDojoFamily, filters={'label': label}).first():
        echo.echo_critical(f'{PseudoDojoFamily.__name__}<{label}> is already installed')

    with tempfile.TemporaryDirectory() as dirpath:

        dirpath = pathlib.Path(dirpath)
        filepath_archive = dirpath / 'archive.tgz'
        filepath_metadata = dirpath / 'metadata.tgz'

        download_pseudo_dojo(configuration, filepath_archive, filepath_metadata, traceback)

        description += f'\nArchive pseudos md5: {md5_file(filepath_archive)}'
        description += f'\nPseudo metadata md5: {md5_file(filepath_metadata)}'

        if download_only:
            for filepath in [filepath_archive, filepath_metadata]:
                filepath_target = pathlib.Path.cwd() / filepath.name
                if filepath_target.exists():
                    echo.echo_warning(f'the file `{filepath_target}` already exists, skipping.')
                else:
                    # Cannot use ``pathlib.Path.rename`` because this will fail if it moves across file systems.
                    shutil.move(filepath, filepath_target)
                    echo.echo_success(f'`{filepath_target.name}` written to the current directory.')
            return

        with attempt('unpacking archive and parsing pseudos... ', include_traceback=traceback):
            family = create_family_from_archive(PseudoDojoFamily, label, filepath_archive, pseudo_type=pseudo_type)

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
        for stringency, cutoff_values in cutoffs.items():
            family.set_cutoffs(cutoff_values, stringency, unit='Eh')
        family.set_default_stringency(default_stringency)

        echo.echo_success(f'installed `{label}` containing {family.count()} pseudo potentials')
