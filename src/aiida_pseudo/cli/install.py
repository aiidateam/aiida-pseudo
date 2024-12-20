"""Command to install a pseudo potential family."""
import json
import pathlib
import sys
import tarfile
import tempfile
import typing as t

import click
import requests
import yaml
from aiida.cmdline.params import options as options_core
from aiida.cmdline.utils import decorators, echo

from .params import options, types
from .root import cmd_root

if t.TYPE_CHECKING:
    from aiida_pseudo.data.pseudo import PseudoPotentialData
    from aiida_pseudo.groups.family import PseudoDojoConfiguration, PseudoDojoFamily, SsspConfiguration


@cmd_root.group('install')
def cmd_install():
    """Install pseudo potential families."""


@cmd_install.command('family')
@click.argument('archive', type=types.PathOrUrl(exists=True, file_okay=True, path_type=pathlib.Path))
@click.argument('label', type=click.STRING)
@options_core.DESCRIPTION(help='Description for the family.')
@options.ARCHIVE_FORMAT()
@options.FAMILY_TYPE(
    type=types.PseudoPotentialFamilyTypeParam(blacklist=('pseudo.family.sssp', 'pseudo.family.pseudo_dojo'))
)
@options.PSEUDO_TYPE()
@options.TRACEBACK()
@decorators.with_dbenv()
def cmd_install_family(archive, label, description, archive_format, family_type, pseudo_type, traceback):
    """Install a standard pseudopotential family from an ARCHIVE.

    The ARCHIVE can be a (compressed) archive of a directory containing the pseudopotentials on the local file system or
    provided by an HTTP URL. Alternatively, it can be a normal directory on the local file system. The (unarchived)
    directory should only contain the pseudopotential files and they cannot be in any subdirectory. In addition,
    depending on the chosen pseudopotential type (see the option `-P/--pseudo-type`) there can be additional
    requirements on the pseudopotential file and filename format.

    If the ARCHIVE corresponds to a (compressed) archive, the command will attempt to infer the archive format from the
    filename extension of the ARCHIVE. If this fails, the archive format can be specified explicitly with the archive
    format option `-f/--archive-format`, which will also display which formats are supported. These format suffixes
    follow the naming of the `shutil.unpack_archive` standard library method.

    Once the ARCHIVE is downloaded, uncompressed and unarchived into a directory on the local file system, the command
    will create a `PseudoPotentialFamily` instance where the type of the pseudopotential data nodes that are stored
    within it is set through the `-P/--pseudo-type` option. If the default, `pseudo` (which corresponds to the data
    plugin `PseudoPotentialData`), is used, the pseudopotential files in the archive *have* to have filenames that
    strictly follow the format `ELEMENT.EXTENSION`, or the creation of the family will fail. This is because for the
    default pseudopotential type, the format of the file is unknown and the family requires the element to be known,
    which in this case can then only be parsed from the filename.

    The pseudopotential family type that is created can also be changed with the `-F/--family-type` option. Note,
    however, that not all values are accepted. For example, the `pseudo.family.sssp` and `pseudo.family.pseudo_dojo` are
    blacklisted since they have their own dedicated commands in `install sssp` and `install pseudo-dojo`, respectively.
    """
    from .utils import attempt, create_family_from_archive

    if isinstance(archive, pathlib.Path) and archive.is_dir():
        with attempt(f'creating a pseudopotential family from directory `{archive}`...', include_traceback=traceback):
            family = family_type.create_from_folder(archive, label, pseudo_type=pseudo_type)
    elif isinstance(archive, pathlib.Path) and archive.is_file():
        with attempt('unpacking archive and parsing pseudos... ', include_traceback=traceback):
            family = create_family_from_archive(
                family_type, label, archive, fmt=archive_format, pseudo_type=pseudo_type
            )
    else:
        # At this point, we can assume that it is not a valid filepath on disk, but rather a URL and the ``archive``
        # variable will contain the result objects from the ``requests`` library. The validation of the URL will already
        # have been done by the ``PathOrUrl`` parameter type and will already have retrieved the content. The content of
        # the URL must be copied to a local temporary file because `create_family_from_archive` does currently not
        # accept filelike objects, because in turn the underlying `shutil.unpack_archive` does not.
        with tempfile.NamedTemporaryFile(mode='w+b') as handle:
            handle.write(archive.content)
            handle.flush()

            with attempt('unpacking archive and parsing pseudos... ', include_traceback=traceback):
                family = create_family_from_archive(
                    family_type, label, pathlib.Path(handle.name), fmt=archive_format, pseudo_type=pseudo_type
                )

    family.description = description
    echo.echo_success(f'installed `{label}` containing {family.count()} pseudopotentials')


def download_sssp(
    configuration: 'SsspConfiguration',
    filepath_archive: pathlib.Path,
    filepath_metadata: pathlib.Path,
    traceback: bool = False,
) -> str:
    """Download the pseudopotential archive and metadata for an SSSP configuration to a path on disk.

    :param configuration: the SSSP configuration to download.
    :param filepath_archive: absolute filepath to write the pseudopotential archive to.
    :param filepath_metadata: absolute filepath to write the metadata file to.
    :param traceback: boolean, if true, print the traceback when an exception occurs.
    :return: Latest patch version of the requested minor version
    """
    from aiida_pseudo.groups.family import SsspFamily

    from .utils import attempt

    # The ``parent_id=19`` points to the SSSP entry on the Materials Cloud. Using ``parent_id`` will fetch the latest
    # version of the SSSP archive record.
    url_template = 'https://archive.materialscloud.org/record/file?filename={filename}&parent_id=19'

    # Download the dictionary mapping of the minor versions to the latest corresponding patch versions. Since patch
    # releases of the SSSP only contain bug fixes, there is no reason to have the user install an outdated patch
    # version. So, the latest patch version of the minor version that is specified by the user is always installed.
    with attempt('downloading patch versions information... ', include_traceback=traceback):
        response = requests.get(url_template.format(filename='versions.yaml'), timeout=30)
        response.raise_for_status()
        # The `version_mapping` is a dictionary that maps each minor version (key) to the latest patch version (value)
        version_mapping = yaml.load(response.content, Loader=yaml.SafeLoader)
        patch_version = version_mapping[configuration.version]

    echo.echo_info(f'Latest patch version found: {patch_version}')

    archive_filename = SsspFamily.format_configuration_filename(configuration, 'tar.gz', patch_version)
    metadata_filename = SsspFamily.format_configuration_filename(configuration, 'json', patch_version)

    url_archive = url_template.format(filename=archive_filename)
    url_metadata = url_template.format(filename=metadata_filename)

    with attempt('downloading selected pseudopotentials archive... ', include_traceback=traceback):
        response = requests.get(url_archive, timeout=30)
        response.raise_for_status()
        with open(filepath_archive, 'wb') as handle:
            handle.write(response.content)
            handle.flush()

    with attempt('downloading selected pseudopotentials metadata... ', include_traceback=traceback):
        response = requests.get(url_metadata, timeout=30)
        response.raise_for_status()
        with open(filepath_metadata, 'wb') as handle:
            handle.write(response.content)
            handle.flush()

    return patch_version


def install_sssp(
    filepath_archive: pathlib.Path,
    filepath_metadata: pathlib.Path,
    label: str,
    description: str = '',
    traceback: bool = False,
) -> None:
    """Install the ``SsspFamily`` and set the recommended cutoffs.

    :param filepath_archive: path to the pseudopotential archive.
    :param filepath_metadata: path to the metadata file.
    :param label: label of the pseudopotential family group.
    :param description: description of the pseudopotential family group.
    :param traceback: boolean, if true, print the traceback when an exception occurs.
    """
    from aiida.orm import Group

    from aiida_pseudo.groups.family.sssp import SsspFamily

    from .utils import attempt, create_family_from_archive

    metadata = json.loads(filepath_metadata.read_text())

    with attempt('unpacking archive and parsing pseudos... ', include_traceback=traceback):
        family = create_family_from_archive(SsspFamily, label, filepath_archive)

    cutoffs = {}

    for element, values in metadata.items():
        if family.get_pseudo(element).md5 != values['md5']:
            Group.collection.delete(family.pk)
            msg = f"md5 of pseudo for element {element} does not match that of the metadata {values['md5']}"
            echo.echo_critical(msg)

        cutoffs[element] = {'cutoff_wfc': values['cutoff_wfc'], 'cutoff_rho': values['cutoff_rho']}

    family.description = description
    family.set_cutoffs(cutoffs, 'normal', unit='Ry')

    echo.echo_success(f'installed `{label}` containing {family.count()} pseudopotentials.')


@cmd_install.command('sssp')
@options.VERSION(type=click.Choice(['1.0', '1.1', '1.2', '1.3']), default='1.3', show_default=True)
@options.FUNCTIONAL(type=click.Choice(['PBE', 'PBEsol']), default='PBE', show_default=True)
@options.PROTOCOL(type=click.Choice(['efficiency', 'precision']), default='efficiency', show_default=True)
@options.DOWNLOAD_ONLY()
@options.FROM_DOWNLOAD()
@options.TRACEBACK()
def cmd_install_sssp(version, functional, protocol, download_only, from_download, traceback):
    """Install an SSSP configuration.

    The SSSP configuration will be automatically downloaded from the Materials Cloud Archive entry to create a new
    `SsspFamily`.
    """

    from aiida import load_profile
    from aiida.common.exceptions import ConfigurationError
    from aiida.common.files import md5_file
    from aiida.orm import QueryBuilder

    from aiida_pseudo import __version__
    from aiida_pseudo.groups.family.sssp import SsspConfiguration, SsspFamily

    if download_only and from_download is not None:
        raise click.BadParameter(
            'cannot specify both `--download-only` and `--from-download`.',
            param_hint="'--download-only' / '--from-download'",
        )

    configuration = SsspConfiguration(version, functional, protocol)
    label = SsspFamily.format_configuration_label(configuration)

    if configuration not in SsspFamily.valid_configurations:
        echo.echo_critical(f'{version} {functional} {protocol} is not a valid SSSP configuration')

    with tempfile.TemporaryDirectory() as tmppath:
        dirpath = pathlib.Path(tmppath)

        filepath_archive = dirpath / 'archive.tar.gz'
        filepath_metadata = dirpath / 'metadata.json'
        filepath_configuration = dirpath / 'configuration.json'

        if download_only:
            tarball_path = pathlib.Path.cwd() / f'{label}.aiida_pseudo'.replace('/', '_')

            if tarball_path.exists():
                echo.echo_critical(f'the file `{tarball_path}` already exists.')

            download_sssp(configuration, filepath_archive, filepath_metadata, traceback)

            with filepath_configuration.open('w') as handle:
                handle.write(json.dumps(configuration._asdict()))

            with tarfile.open(tarball_path, 'w') as tarball_file:
                for filepath in [filepath_configuration, filepath_metadata, filepath_archive]:
                    tarball_file.add(filepath, filepath.name)

            echo.echo_success(f'Pseudopotential archive written to: {tarball_path.name}')
            return

        if from_download is not None:
            tarball_path = pathlib.Path(from_download).absolute()
            with tarfile.open(tarball_path, 'r') as handle:
                handle.extractall(dirpath)

            for filepath in (filepath_archive, filepath_metadata, filepath_configuration):
                if not filepath.exists():
                    echo.echo_critical(
                        f'archive `{from_download}` did not contain required file `{filepath_archive.name}`'
                    )

            with filepath_configuration.open('r') as handle:
                configuration = SsspConfiguration(**json.load(handle))

            label = SsspFamily.format_configuration_label(configuration)

            if configuration not in SsspFamily.valid_configurations:
                echo.echo_critical(f'{version} {functional} {protocol} is not a valid SSSP configuration')

        try:
            load_profile()
        except ConfigurationError:
            echo.echo_critical(
                'Could not load a valid AiiDA profile. Check `verdi profile list` to make sure you have one defined.'
            )

        if QueryBuilder().append(SsspFamily, filters={'label': label}).first():
            echo.echo_report(f'{SsspFamily.__name__}<{label}> is already installed')
            sys.exit(1)

        if not from_download:
            download_sssp(configuration, filepath_archive, filepath_metadata, traceback)

        description = (
            f'SSSP v{configuration.version} {configuration.functional} {configuration.protocol} '
            f'installed with aiida-pseudo v{__version__}'
        )
        description += f'\nArchive pseudos md5: {md5_file(filepath_archive)}'
        description += f'\nPseudo metadata md5: {md5_file(filepath_metadata)}'

        install_sssp(filepath_archive, filepath_metadata, label, description, traceback)


def download_pseudo_dojo(
    configuration: 'PseudoDojoConfiguration',
    filepath_archive: pathlib.Path,
    filepath_metadata: pathlib.Path,
    traceback: bool = False,
) -> None:
    """Download the pseudopotential archive and metadata for a PseudoDojo configuration to a path on disk.

    :param configuration: the PseudoDojo configuration to download.
    :param filepath_archive: absolute filepath to write the pseudopotential archive to.
    :param filepath_metadata: absolute filepath to write the metadata archive to.
    :param traceback: boolean, if true, print the traceback when an exception occurs.
    """
    from ..groups.family.pseudo_dojo import PseudoDojoFamily
    from .utils import attempt

    label = PseudoDojoFamily.format_configuration_label(configuration)
    url_archive = PseudoDojoFamily.get_url_archive(label)
    url_metadata = PseudoDojoFamily.get_url_metadata(label)

    with attempt('downloading selected pseudopotentials archive... ', include_traceback=traceback):
        response = requests.get(url_archive, timeout=30, verify=False)
        response.raise_for_status()
        with open(filepath_archive, 'wb') as handle:
            handle.write(response.content)
            handle.flush()

    with attempt('downloading selected pseudopotentials metadata archive... ', include_traceback=traceback):
        response = requests.get(url_metadata, timeout=30, verify=False)
        response.raise_for_status()
        with open(filepath_metadata, 'wb') as handle:
            handle.write(response.content)
            handle.flush()


def install_pseudo_dojo(
    configuration: 'PseudoDojoConfiguration',
    filepath_archive: pathlib.Path,
    filepath_metadata: pathlib.Path,
    pseudo_type: 'PseudoPotentialData',
    label: str,
    description: str = '',
    traceback: bool = False,
) -> 'PseudoDojoFamily':
    """Install the ``PseudoDojoFamily`` and set the recommended cutoffs.

    :param filepath_archive: path to the pseudopotential archive.
    :param filepath_metadata: path to the metadata file.
    :param label: label of the pseudopotential family group.
    :pseudo_type: type of the pseudopotentials (psp8, upf, ...).
    :param description: description of the pseudopotential family group.
    :param traceback: boolean, if true, print the traceback when an exception occurs.
    """

    from aiida.orm import Group

    from aiida_pseudo.groups.family.pseudo_dojo import PseudoDojoConfiguration, PseudoDojoFamily

    from .utils import attempt, create_family_from_archive

    with attempt('unpacking archive and parsing pseudos... ', include_traceback=traceback):
        family = create_family_from_archive(PseudoDojoFamily, label, filepath_archive, pseudo_type=pseudo_type)

    with attempt('unpacking metadata archive and parsing metadata...', include_traceback=traceback):
        md5s, cutoffs = PseudoDojoFamily.parse_djrepos_from_archive(filepath_metadata, pseudo_type=pseudo_type)

    for element, md5 in md5s.items():
        if family.get_pseudo(element).md5 != md5:
            Group.collection.delete(family.pk)
            msg = f'md5 of pseudo for element {element} does not match that of the metadata {md5}'
            echo.echo_critical(msg)

    paw_configurations = (
        PseudoDojoConfiguration('1.0', 'PBE', 'SR', 'standard', 'jthxml'),
        PseudoDojoConfiguration('1.0', 'PBE', 'SR', 'stringent', 'jthxml'),
        PseudoDojoConfiguration('1.0', 'LDA', 'SR', 'standard', 'jthxml'),
        PseudoDojoConfiguration('1.0', 'LDA', 'SR', 'stringent', 'jthxml'),
    )

    # The PAW configurations have missing cutoffs for the Lanthanides, which have ben replaced with a placeholder
    # value of `-1`. We replace these with the 1.5 * the maximum cutoff from the same stringency so that these
    # potentials are still usable, but this should be taken as a _rough_ approximation.
    # We check only the `cutoff_wfc` because `cutoff_rho` is not provided by PseudoDojo and is therefore
    # locally calculated in `PseudoDojoFamily.parse_djrepos_from_archive` as `2.0 * cutoff_wfc` for PAW.
    if configuration in paw_configurations:
        adjusted_cutoffs = {}
        for stringency, str_cutoffs in cutoffs.items():
            adjusted_cutoffs[stringency] = []
            max_cutoff_wfc = max(cutoffs['cutoff_wfc'] for cutoffs in str_cutoffs.values())
            filler_cutoff_wfc = max_cutoff_wfc * 1.5
            for element, cutoff in str_cutoffs.items():
                if cutoff['cutoff_wfc'] <= 0:
                    cutoffs[stringency][element]['cutoff_wfc'] = filler_cutoff_wfc
                    cutoffs[stringency][element]['cutoff_rho'] = 2.0 * filler_cutoff_wfc
                    adjusted_cutoffs[stringency].append(element)

        for stringency, elements in adjusted_cutoffs.items():
            msg = (
                f'stringency `{stringency}` has missing recommended cutoffs for elements '
                f'{", ".join(elements)}: as a substitute, 1.5 * the maximum cutoff of the stringency '
                'was set for these elements. USE WITH CAUTION!'
            )
            echo.echo_warning(msg)

    family.description = description
    for stringency, cutoff_values in cutoffs.items():
        family.set_cutoffs(cutoff_values, stringency, unit='Eh')

    echo.echo_success(f'installed `{label}` containing {family.count()} pseudopotentials.')

    return family


@cmd_install.command('pseudo-dojo')
@options.VERSION(type=click.Choice(['0.4', '0.5', '1.0']), default='0.4', show_default=True)
@options.FUNCTIONAL(type=click.Choice(['PBE', 'PBEsol', 'LDA']), default='PBE', show_default=True)
@options.RELATIVISTIC(type=click.Choice(['SR', 'SR3plus', 'FR']), default='SR', show_default=True)
@options.PROTOCOL(type=click.Choice(['standard', 'stringent']), default='standard', show_default=True)
@options.PSEUDO_FORMAT(type=click.Choice(['psp8', 'upf', 'psml', 'jthxml']), default='psp8', show_default=True)
@options.DEFAULT_STRINGENCY(type=click.Choice(['low', 'normal', 'high']), default='normal', show_default=True)
@options.DOWNLOAD_ONLY()
@options.FROM_DOWNLOAD()
@options.TRACEBACK()
def cmd_install_pseudo_dojo(
    version,
    functional,
    relativistic,
    protocol,
    pseudo_format,
    default_stringency,
    download_only,
    from_download,
    traceback,
):
    """Install a PseudoDojo configuration.

    The PseudoDojo configuration will be automatically downloaded from pseudo-dojo.org to create a new
    `PseudoDojoFamily` subclass instance based on the specified pseudopotential format.
    """

    from aiida import load_profile
    from aiida.common.exceptions import ConfigurationError
    from aiida.common.files import md5_file
    from aiida.orm import QueryBuilder

    from aiida_pseudo import __version__
    from aiida_pseudo.data.pseudo import JthXmlData, PsmlData, Psp8Data, UpfData
    from aiida_pseudo.groups.family.pseudo_dojo import PseudoDojoConfiguration, PseudoDojoFamily

    if download_only and from_download is not None:
        raise click.BadParameter(
            'cannot specify both `--download-only` and `--from-download`.',
            param_hint="'--download-only' / '--from-download'",
        )

    pseudo_type_mapping = {
        'jthxml': JthXmlData,
        'psp8': Psp8Data,
        'psml': PsmlData,
        'upf': UpfData,
    }
    pseudo_type = pseudo_type_mapping[pseudo_format]

    configuration = PseudoDojoConfiguration(version, functional, relativistic, protocol, pseudo_format)
    label = PseudoDojoFamily.format_configuration_label(configuration)

    if configuration not in PseudoDojoFamily.valid_configurations:
        echo.echo_critical(f'{configuration} is not a valid configuration')

    with tempfile.TemporaryDirectory() as tmppath:
        dirpath = pathlib.Path(tmppath)

        filepath_archive = dirpath / 'archive.tgz'
        filepath_metadata = dirpath / 'metadata.tgz'
        filepath_configuration = dirpath / 'configuration.json'

        if download_only:
            tarball_path = pathlib.Path.cwd() / f'{label}.aiida_pseudo'.replace('/', '_')

            if tarball_path.exists():
                echo.echo_critical(f'the file `{tarball_path}` already exists.')

            download_pseudo_dojo(configuration, filepath_archive, filepath_metadata, traceback)

            with filepath_configuration.open('w') as handle:
                handle.write(json.dumps(configuration._asdict()))

            with tarfile.open(tarball_path, 'w') as tarball_file:
                for filepath in [filepath_configuration, filepath_metadata, filepath_archive]:
                    tarball_file.add(filepath, filepath.name)

            echo.echo_success(f'Pseudopotential archive written to: {tarball_path.name}')
            return

        if from_download is not None:
            tarball_path = pathlib.Path(from_download).absolute()
            with tarfile.open(tarball_path, 'r') as handle:
                handle.extractall(dirpath)

            with filepath_configuration.open('r') as handle:
                configuration = PseudoDojoConfiguration(**json.load(handle))
                pseudo_type = pseudo_type_mapping[configuration.pseudo_format]

            label = PseudoDojoFamily.format_configuration_label(configuration)

            if configuration not in PseudoDojoFamily.valid_configurations:
                echo.echo_critical(f'{configuration} is not a valid configuration')

        try:
            load_profile()
        except ConfigurationError:
            echo.echo_critical(
                'Could not load a valid AiiDA profile. Check `verdi profile list` to make sure you have one defined.'
            )

        if QueryBuilder().append(PseudoDojoFamily, filters={'label': label}).first():
            echo.echo_report(f'{PseudoDojoFamily.__name__}<{label}> is already installed')
            sys.exit(1)

        if not from_download:
            download_pseudo_dojo(configuration, filepath_archive, filepath_metadata, traceback)

        description = f'{configuration} installed with aiida-pseudo v{__version__}'
        description += f'\nArchive pseudos md5: {md5_file(filepath_archive)}'
        description += f'\nPseudo metadata md5: {md5_file(filepath_metadata)}'

        family = install_pseudo_dojo(
            configuration, filepath_archive, filepath_metadata, pseudo_type, label, description, traceback
        )
        family.set_default_stringency(default_stringency)
