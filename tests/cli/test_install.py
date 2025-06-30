"""Tests for `aiida-pseudo install`."""
import contextlib
import json
import pathlib

import pytest
from aiida.manage.configuration.config import Config
from aiida.orm import QueryBuilder
from aiida_pseudo.cli import cmd_install_family, cmd_install_pseudo_dojo, cmd_install_sssp, install
from aiida_pseudo.data.pseudo.upf import UpfData
from aiida_pseudo.groups.family import PseudoPotentialFamily
from aiida_pseudo.groups.family.pseudo_dojo import PseudoDojoConfiguration, PseudoDojoFamily
from aiida_pseudo.groups.family.sssp import SsspConfiguration, SsspFamily


@contextlib.contextmanager
def empty_config() -> Config:
    """Provide a temporary empty configuration.

    This creates a temporary directory with a clean `.aiida` folder and basic configuration file. The currently loaded
    configuration and profile are stored in memory and are automatically restored at the end of this context manager.

    :return: a new empty config instance.
    """
    import os
    import tempfile

    from aiida.manage import configuration, get_manager
    from aiida.manage.configuration import settings

    current_config = configuration.CONFIG
    current_config_path = pathlib.Path(current_config.dirpath)
    current_profile = configuration.get_profile()
    current_path_variable = os.environ.get(settings.DEFAULT_AIIDA_PATH_VARIABLE, None)

    manager = get_manager()
    manager.unload_profile()

    with tempfile.TemporaryDirectory() as dirpath:
        dirpath_config = pathlib.Path(dirpath) / 'config'
        os.environ[settings.DEFAULT_AIIDA_PATH_VARIABLE] = str(dirpath_config)
        settings.AiiDAConfigDir.set(dirpath_config)
        configuration.CONFIG = configuration.load_config(create=True)

        try:
            yield configuration.CONFIG
        finally:
            if current_path_variable is None:
                os.environ.pop(settings.DEFAULT_AIIDA_PATH_VARIABLE, None)
            else:
                os.environ[settings.DEFAULT_AIIDA_PATH_VARIABLE] = current_path_variable

            settings.AiiDAConfigDir.set(current_config_path)
            configuration.CONFIG = current_config

            if current_profile:
                get_manager().load_profile(current_profile.name, allow_switch=True)


@pytest.fixture
def run_monkeypatched_install_sssp(run_cli_command, filepath_pseudos, monkeypatch, tmp_path):
    """Fixture to monkeypatch the ``aiida_pseudo.cli.install.download_sssp`` method and call the install cmd."""

    def download_sssp(
        configuration: SsspConfiguration,
        filepath_archive: pathlib.Path,
        filepath_metadata: pathlib.Path,
        traceback: bool = False,
    ) -> None:
        """Download the pseudopotential archive and metadata for an SSSP configuration to a path on disk.

        :param configuration: the SSSP configuration to download.
        :param filepath_archive: absolute filepath to write the pseudopotential archive to.
        :param filepath_metadata: absolute filepath to write the metadata file to.
        :param traceback: boolean, if true, print the traceback when an exception occurs.
        """
        import hashlib
        import shutil

        element = 'Ar'
        entry_point = 'upf'
        filepath_pseudo = filepath_pseudos(entry_point) / f'{element}.{entry_point}'
        (tmp_path / filepath_pseudo.name).write_bytes(filepath_pseudo.read_bytes())
        md5 = hashlib.md5(filepath_pseudo.read_bytes()).hexdigest()

        filename_archive = shutil.make_archive('temparchive', 'gztar', root_dir=tmp_path, base_dir='.')
        shutil.move(pathlib.Path.cwd() / filename_archive, filepath_archive)

        with open(filepath_metadata, 'w', encoding='utf-8') as handle:
            data = {element: {'md5': md5, 'cutoff_wfc': 60.0, 'cutoff_rho': 240.0}}
            json.dump(data, handle)
            handle.flush()

    def _run_monkeypatched_install_sssp(options=None, raises=None):
        monkeypatch.setattr(install, 'download_sssp', download_sssp)
        return run_cli_command(cmd_install_sssp, options, raises)

    return _run_monkeypatched_install_sssp


@pytest.fixture
def run_monkeypatched_install_pseudo_dojo(run_cli_command, filepath_pseudos, monkeypatch, tmp_path):
    """Fixture to monkeypatch the ``aiida_pseudo.cli.install.download_pseudo_dojo`` method and call the install cmd."""

    def download_pseudo_dojo(
        configuration: PseudoDojoConfiguration,
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
        import hashlib
        import shutil

        element = 'Ar'
        entry_point = 'jthxml'
        filepath_pseudo = filepath_pseudos(entry_point) / f'{element}.{entry_point}'
        (tmp_path / filepath_pseudo.name).write_bytes(filepath_pseudo.read_bytes())
        md5 = hashlib.md5(filepath_pseudo.read_bytes()).hexdigest()

        filename_archive = shutil.make_archive('temparchive', 'gztar', root_dir=tmp_path, base_dir='.')
        shutil.move(pathlib.Path.cwd() / filename_archive, filepath_archive)

        data = {'hints': {'high': {'ecut': 20.00}, 'low': {'ecut': 20.00}, 'normal': {'ecut': 20.00}}, 'md5': md5}

        filepath_djrepo = tmp_path / f'{element}.djrepo'

        with open(filepath_djrepo, 'w', encoding='utf-8') as handle:
            json.dump(data, handle)
            handle.flush()

        filename_metadata = shutil.make_archive('tempmetadata', 'gztar', root_dir=tmp_path, base_dir='.')
        shutil.move(pathlib.Path.cwd() / filename_metadata, filepath_metadata)

    def _run_monkeypatched_install_pseudo_dojo(options=None, raises=None):
        monkeypatch.setattr(install, 'download_pseudo_dojo', download_pseudo_dojo)
        return run_cli_command(cmd_install_pseudo_dojo, options, raises)

    return _run_monkeypatched_install_pseudo_dojo


@pytest.mark.usefixtures('aiida_profile_clean')
def test_install_family(run_cli_command, get_pseudo_archive):
    """Test ``aiida-pseudo install family``."""
    label = 'family'
    description = 'description'
    filepath = get_pseudo_archive()
    options = ['-D', description, str(filepath), label]

    result = run_cli_command(cmd_install_family, options)
    assert f'installed `{label}`' in result.output
    assert PseudoPotentialFamily.collection.count() == 1

    family = PseudoPotentialFamily.collection.get(label=label)
    assert family.__class__ is PseudoPotentialFamily
    assert family.description == description
    assert len(family.pseudos) != 0


@pytest.mark.usefixtures('aiida_profile_clean')
def test_install_family_folder(run_cli_command, filepath_pseudos):
    """Test ``aiida-pseudo install family` from folder`."""
    label = 'family_test'
    description = 'description'
    dirpath = filepath_pseudos()
    options = ['-D', description, str(dirpath), label]

    result = run_cli_command(cmd_install_family, options)
    assert f'installed `{label}`' in result.output
    assert PseudoPotentialFamily.collection.count() == 1

    family = PseudoPotentialFamily.collection.get(label=label)
    assert family.__class__ is PseudoPotentialFamily
    assert family.description == description
    assert len(family.pseudos) != 0


@pytest.mark.usefixtures('aiida_profile_clean')
def test_install_family_url(run_cli_command, get_pseudo_archive, monkeypatch):
    """Test ``aiida-pseudo install family`` when installing from a URL.

    Testing this functionality by actually retrieving from a URL has two main downsides: it will be potentially slow
    by having to download data from the web, but most importantly it is susceptible to random failures if the remote
    URL is (temporarily) not availabe, or even permanently goes offline, or even the content changes. That is why we
    monkeypatch the ``PathOrUrl`` instead to simply return the content of an archive that is created on the fly on the
    local disk. The command expects that the parameter type returns an object that contains the content of the archive
    under the ``content`` attribute. To mimick this, we construct a namedtuple with a ``content`` attribute on the fly.
    """
    from aiida_pseudo.cli.params.types import PathOrUrl

    fmt = 'gztar'
    label = 'SSSP/1.0/PBE/efficiency'
    description = 'description'
    filepath_archive = 'https://archive.materialscloud.org/record/file?filename=fake-url'
    options = ['-D', description, '-P', 'pseudo.upf', '-f', fmt, filepath_archive, label]

    def convert(*_, **__):
        from collections import namedtuple

        Archive = namedtuple('Archive', ['content'])
        archive = Archive(get_pseudo_archive(fmt=fmt).read_bytes())
        return archive

    monkeypatch.setattr(PathOrUrl, 'convert', convert)

    result = run_cli_command(cmd_install_family, options)
    assert f'installed `{label}`' in result.output
    assert PseudoPotentialFamily.collection.count() == 1

    family = PseudoPotentialFamily.collection.get(label=label)
    assert isinstance(family.pseudos['Ar'], UpfData)
    assert family.__class__ is PseudoPotentialFamily
    assert family.description == description
    assert len(family.pseudos) != 0


@pytest.mark.usefixtures('aiida_profile_clean')
def test_install_sssp(run_cli_command):
    """Test the ``aiida-pseudo install sssp`` command."""
    from aiida_pseudo import __version__

    result = run_cli_command(cmd_install_sssp)
    assert 'installed `SSSP/' in result.output
    assert QueryBuilder().append(SsspFamily).count() == 1

    family = QueryBuilder().append(SsspFamily).one()[0]
    assert family.get_cutoffs is not None
    assert f'PBE efficiency installed with aiida-pseudo v{__version__}' in family.description
    assert 'Archive pseudos md5: ' in family.description
    assert 'Pseudo metadata md5: ' in family.description

    result = run_cli_command(cmd_install_sssp, raises=SystemExit)
    assert 'is already installed' in result.output


@pytest.mark.usefixtures('aiida_profile_clean')
def test_install_pseudo_dojo(run_cli_command):
    """Test the ``aiida-pseudo install pseudo-dojo`` command."""
    from aiida_pseudo import __version__

    result = run_cli_command(cmd_install_pseudo_dojo)
    assert 'installed `PseudoDojo/' in result.output
    assert QueryBuilder().append(PseudoDojoFamily).count() == 1

    family = QueryBuilder().append(PseudoDojoFamily).one()[0]
    assert family.get_cutoffs is not None
    assert f'PseudoDojo v0.4 PBE SR standard psp8 installed with aiida-pseudo v{__version__}' in family.description
    assert 'Archive pseudos md5: a43737369e8a0a4417ccf364397298b3' in family.description
    assert 'Pseudo metadata md5: d0c0057f16cb905bb2d43382146ffad2' in family.description

    result = run_cli_command(cmd_install_pseudo_dojo, raises=SystemExit)
    assert 'is already installed' in result.output


@pytest.mark.usefixtures('aiida_profile_clean')
def test_install_sssp_monkeypatched(run_monkeypatched_install_sssp):
    """Test the ``aiida-pseudo install sssp`` command with a monkeypatched download function.

    This circumvents the actual download from Materials Cloud archive and substitutes it with a simple archive of a
    single pseudo potential. We are merely verifying that the various configuration options are respected and are
    reflected in the label of the created family.
    """
    version = '1.1'
    functional = 'PBEsol'
    protocol = 'precision'
    configuration = SsspConfiguration(version, functional, protocol)
    label = SsspFamily.format_configuration_label(configuration)

    options = ['-v', version, '-x', functional, '-p', protocol]
    result = run_monkeypatched_install_sssp(options=options)
    assert f'installed `{label}`' in result.output
    assert SsspFamily.collection.count() == 1

    family = SsspFamily.collection.get(label=label)
    assert family.label == label


@pytest.mark.usefixtures('aiida_profile_clean')
@pytest.mark.filterwarnings('ignore:filename .* does not have a supported extension.:UserWarning')
def test_install_pseudo_dojo_monkeypatched(run_monkeypatched_install_pseudo_dojo):
    """Test the ``aiida-pseudo install pseudo-dojo`` command with a monkeypatched download function.

    This circumvents the actual download from the Pseudo Dojo website and substitutes it with a simple archive of a
    single pseudo potential. We are merely verifying that the various configuration options are respected and are
    reflected in the label of the created family.
    """
    version = '1.0'
    functional = 'LDA'
    protocol = 'stringent'
    pseudo_format = 'jthxml'
    configuration = PseudoDojoConfiguration(version, functional, 'SR', protocol, pseudo_format)
    label = PseudoDojoFamily.format_configuration_label(configuration)

    options = ['-v', version, '-x', functional, '-p', protocol, '-f', pseudo_format]
    result = run_monkeypatched_install_pseudo_dojo(options=options)
    assert f'installed `{label}`' in result.output
    assert PseudoDojoFamily.collection.count() == 1

    family = PseudoDojoFamily.collection.get(label=label)
    assert family.label == label


@pytest.mark.usefixtures('aiida_profile_clean', 'chdir_tmp_path')
def test_install_sssp_download_only(run_monkeypatched_install_sssp):
    """Test the ``aiida-pseudo install sssp`` command with the ``--download-only`` option.

    The command should be callable with the ``--download-only`` option even if no profiles are defined for the current
    AiiDA instance. To test this, the ``empty_config`` context manager temporarily unloads the profile that is loaded
    for the test suite and replaces the config with an empty one. To verify that the ``empty_config`` context does its
    job the command is first called without the ``--download-only`` option which should then raise. Then the command
    is called again, this time with the option.
    """
    with empty_config():
        result = run_monkeypatched_install_sssp(raises=True)

    with empty_config():
        result = run_monkeypatched_install_sssp(options=['--download-only'])

    assert SsspFamily.collection.count() == 0
    assert 'Success: Pseudopotential archive written to:' in result.output


@pytest.mark.usefixtures('aiida_profile_clean', 'chdir_tmp_path')
def test_install_sssp_download_only_exists(run_monkeypatched_install_sssp, get_pseudo_family):
    """Test the ``aiida-pseudo install sssp`` command with the ``--download-only`` option.

    The files should be downloadable even if the corresponding configuration is already installed.
    """
    version = '1.1'
    functional = 'PBEsol'
    protocol = 'precision'

    # Generate a family with the same label as we will install through the CLI
    label = SsspFamily.format_configuration_label(SsspConfiguration(version, functional, protocol))
    get_pseudo_family(cls=SsspFamily, pseudo_type=UpfData, label=label)

    options = ['--download-only', '-v', version, '-x', functional, '-p', protocol]
    result = run_monkeypatched_install_sssp(options=options)

    assert SsspFamily.collection.count() == 1
    assert 'Success: Pseudopotential archive written to:' in result.output


@pytest.mark.parametrize('configuration', SsspFamily.valid_configurations)
@pytest.mark.usefixtures('aiida_profile_clean', 'chdir_tmp_path')
def test_install_sssp_from_download(run_monkeypatched_install_sssp, configuration):
    """Test the ``aiida-pseudo install sssp`` command with the ``--from-download`` option."""
    options = [
        '--download-only',
        '-v',
        configuration.version,
        '-x',
        configuration.functional,
        '-p',
        configuration.protocol,
    ]
    result = run_monkeypatched_install_sssp(options=options)

    label = SsspFamily.format_configuration_label(configuration).replace('/', '_')
    filepath = pathlib.Path.cwd() / f'{label}.aiida_pseudo'
    options = ['--from-download', str(filepath)]

    result = run_monkeypatched_install_sssp(options=options)
    assert SsspFamily.collection.count() == 1
    assert 'Success: installed `SSSP/' in result.output


@pytest.mark.usefixtures('aiida_profile_clean', 'chdir_tmp_path')
def test_install_pseudo_dojo_download_only(run_monkeypatched_install_pseudo_dojo):
    """Test the ``aiida-pseudo install pseudo-dojo`` command with the ``--download-only`` option.

    The command should be callable with the ``--download-only`` option even if no profiles are defined for the current
    AiiDA instance. To test this, the ``empty_config`` context manager temporarily unloads the profile that is loaded
    for the test suite and replaces the config with an empty one. To verify that the ``empty_config`` context does its
    job the command is first called without the ``--download-only`` option which should then raise. Then the command
    is called again, this time with the option.
    """
    with empty_config():
        result = run_monkeypatched_install_pseudo_dojo(raises=True)

    with empty_config():
        result = run_monkeypatched_install_pseudo_dojo(options=['--download-only'])

    assert PseudoDojoFamily.collection.count() == 0
    assert 'Success: Pseudopotential archive written to:' in result.output


@pytest.mark.usefixtures('aiida_profile_clean', 'chdir_tmp_path')
def test_install_pseudo_dojo_download_only_exists(run_monkeypatched_install_pseudo_dojo, get_pseudo_family):
    """Test the ``aiida-pseudo install pseudo_dojo`` command with the ``--download-only`` option.

    The files should be downloadable even if the corresponding configuration is already installed.
    """
    version = '1.0'
    functional = 'LDA'
    relativistic = 'SR'
    protocol = 'stringent'
    pseudo_format = 'jthxml'

    # Generate a family with the same label as we will install through the CLI
    configuration = PseudoDojoConfiguration(version, functional, relativistic, protocol, pseudo_format)
    label = PseudoDojoFamily.format_configuration_label(configuration)
    get_pseudo_family(cls=PseudoDojoFamily, pseudo_type=UpfData, label=label)

    options = [
        '--download-only',
        '-v',
        version,
        '-x',
        functional,
        '-r',
        relativistic,
        '-p',
        protocol,
        '-f',
        pseudo_format,
    ]
    result = run_monkeypatched_install_pseudo_dojo(options=options)

    assert PseudoDojoFamily.collection.count() == 1
    assert 'Success: Pseudopotential archive written to:' in result.output


@pytest.mark.usefixtures('aiida_profile_clean', 'chdir_tmp_path')
def test_install_pseudo_dojo_from_download(run_monkeypatched_install_pseudo_dojo):
    """Test the ``aiida-pseudo install pseudo-dojo`` command with the ``--from-download`` option."""
    version = '1.0'
    functional = 'LDA'
    relativistic = 'SR'
    protocol = 'stringent'
    pseudo_format = 'jthxml'
    configuration = PseudoDojoConfiguration(version, functional, relativistic, protocol, pseudo_format)
    options = [
        '--download-only',
        '-v',
        version,
        '-x',
        functional,
        '-r',
        relativistic,
        '-p',
        protocol,
        '-f',
        pseudo_format,
    ]
    result = run_monkeypatched_install_pseudo_dojo(options=options)

    label = PseudoDojoFamily.format_configuration_label(configuration).replace('/', '_')
    filepath = pathlib.Path.cwd() / f'{label}.aiida_pseudo'
    options = ['--from-download', str(filepath)]

    result = run_monkeypatched_install_pseudo_dojo(options=options)
    assert PseudoDojoFamily.collection.count() == 1
    assert 'Success: installed `PseudoDojo' in result.output
