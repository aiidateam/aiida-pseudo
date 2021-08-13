# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""Tests for `aiida-pseudo install`."""
import json
import pathlib

import pytest

from aiida.orm import QueryBuilder

from aiida_pseudo.cli import install
from aiida_pseudo.cli import cmd_install_family, cmd_install_sssp, cmd_install_pseudo_dojo
from aiida_pseudo.data.pseudo.upf import UpfData
from aiida_pseudo.groups.family import PseudoPotentialFamily
from aiida_pseudo.groups.family.pseudo_dojo import PseudoDojoFamily, PseudoDojoConfiguration
from aiida_pseudo.groups.family.sssp import SsspFamily, SsspConfiguration


@pytest.fixture
def run_monkeypatched_install_sssp(run_cli_command, get_pseudo_potential_data, monkeypatch, tmpdir):
    """Fixture to monkeypatch the ``aiida_pseudo.cli.install.download_sssp`` method and call the install cmd."""

    def download_sssp(
        configuration: SsspConfiguration,
        filepath_archive: pathlib.Path,
        filepath_metadata: pathlib.Path,
        traceback: bool = False
    ) -> None:
        # pylint: disable=unused-argument
        """Download the pseudopotential archive and metadata for an SSSP configuration to a path on disk.

        :param configuration: the SSSP configuration to download.
        :param filepath_archive: absolute filepath to write the pseudopotential archive to.
        :param filepath_metadata: absolute filepath to write the metadata file to.
        :param traceback: boolean, if true, print the traceback when an exception occurs.
        """
        import hashlib
        import shutil

        element = 'Ar'
        pseudo = get_pseudo_potential_data(element)
        filepath = tmpdir / pseudo.filename

        with pseudo.open(mode='rb') as handle:
            md5 = hashlib.md5(handle.read()).hexdigest()
            handle.seek(0)
            filepath.write_binary(handle.read())

        filename_archive = shutil.make_archive('temparchive', 'gztar', root_dir=tmpdir, base_dir='.')
        shutil.move(pathlib.Path.cwd() / filename_archive, filepath_archive)

        with open(filepath_metadata, 'w') as handle:
            data = {element: {'md5': md5, 'cutoff_wfc': 60.0, 'cutoff_rho': 240.0}}
            json.dump(data, handle)
            handle.flush()

    def _run_monkeypatched_install_sssp(options=None, raises=None):
        monkeypatch.setattr(install, 'download_sssp', download_sssp)
        return run_cli_command(cmd_install_sssp, options, raises)

    return _run_monkeypatched_install_sssp


@pytest.fixture
def run_monkeypatched_install_pseudo_dojo(run_cli_command, get_pseudo_potential_data, monkeypatch, tmpdir):
    """Fixture to monkeypatch the ``aiida_pseudo.cli.install.download_pseudo_dojo`` method and call the install cmd."""

    def download_pseudo_dojo(
        configuration: PseudoDojoConfiguration,
        filepath_archive: pathlib.Path,
        filepath_metadata: pathlib.Path,
        traceback: bool = False
    ) -> None:
        # pylint: disable=unused-argument
        """Download the pseudopotential archive and metadata for a PseudoDojo configuration to a path on disk.

        :param configuration: the PseudoDojo configuration to download.
        :param filepath_archive: absolute filepath to write the pseudopotential archive to.
        :param filepath_metadata: absolute filepath to write the metadata archive to.
        :param traceback: boolean, if true, print the traceback when an exception occurs.
        """
        import hashlib
        import shutil

        element = 'Ar'
        pseudo = get_pseudo_potential_data(element, entry_point='jthxml')
        filepath = tmpdir / pseudo.filename

        with pseudo.open(mode='rb') as handle:
            md5 = hashlib.md5(handle.read()).hexdigest()
            handle.seek(0)
            filepath.write_binary(handle.read())

        filename_archive = shutil.make_archive('temparchive', 'gztar', root_dir=tmpdir, base_dir='.')
        shutil.move(pathlib.Path.cwd() / filename_archive, filepath_archive)

        data = {'hints': {'high': {'ecut': 20.00}, 'low': {'ecut': 20.00}, 'normal': {'ecut': 20.00}}, 'md5': md5}

        filepath_djrepo = tmpdir / f'{element}.djrepo'

        with open(filepath_djrepo, 'w') as handle:
            json.dump(data, handle)
            handle.flush()

        filename_metadata = shutil.make_archive('tempmetadata', 'gztar', root_dir=tmpdir, base_dir='.')
        shutil.move(pathlib.Path.cwd() / filename_metadata, filepath_metadata)

    def _run_monkeypatched_install_pseudo_dojo(options=None, raises=None):
        monkeypatch.setattr(install, 'download_pseudo_dojo', download_pseudo_dojo)
        return run_cli_command(cmd_install_pseudo_dojo, options, raises)

    return _run_monkeypatched_install_pseudo_dojo


@pytest.mark.usefixtures('clear_db')
def test_install_family(run_cli_command, get_pseudo_archive):
    """Test ``aiida-pseudo install family``."""
    label = 'family'
    description = 'description'
    filepath_archive = next(get_pseudo_archive())
    options = ['-D', description, filepath_archive, label]

    result = run_cli_command(cmd_install_family, options)
    assert f'installed `{label}`' in result.output
    assert PseudoPotentialFamily.objects.count() == 1

    family = PseudoPotentialFamily.objects.get(label=label)
    assert family.__class__ is PseudoPotentialFamily
    assert family.description == description
    assert len(family.pseudos) != 0


@pytest.mark.usefixtures('clear_db')
def test_install_family_folder(run_cli_command, filepath_pseudos):
    """Test ``aiida-pseudo install family` from folder`."""
    label = 'family_test'
    description = 'description'
    dirpath = filepath_pseudos()
    options = ['-D', description, dirpath, label]

    result = run_cli_command(cmd_install_family, options)
    assert f'installed `{label}`' in result.output
    assert PseudoPotentialFamily.objects.count() == 1

    family = PseudoPotentialFamily.objects.get(label=label)
    assert family.__class__ is PseudoPotentialFamily
    assert family.description == description
    assert len(family.pseudos) != 0


@pytest.mark.usefixtures('clear_db')
def test_install_family_url(run_cli_command):
    """Test ``aiida-pseudo install family`` when installing from a URL.

    When a URL is passed, the parameter converts it into a ``http.client.HTTPResponse``, which is not trivial to mock so
    instead we use an actual URL, which is slow, but is anyway already tested indirectly in ``test_install_sssp``.
    """
    label = 'SSSP/1.0/PBE/efficiency'
    description = 'description'
    filepath_archive = 'https://legacy-archive.materialscloud.org/file/2018.0001/v4/SSSP_1.0_PBE_efficiency.tar.gz'
    options = ['-D', description, filepath_archive, label, '-P', 'pseudo.upf']

    result = run_cli_command(cmd_install_family, options)
    assert f'installed `{label}`' in result.output
    assert PseudoPotentialFamily.objects.count() == 1

    family = PseudoPotentialFamily.objects.get(label=label)
    assert isinstance(family.pseudos['Si'], UpfData)
    assert family.__class__ is PseudoPotentialFamily
    assert family.description == description
    assert len(family.pseudos) != 0


@pytest.mark.usefixtures('clear_db')
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


@pytest.mark.usefixtures('clear_db')
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


@pytest.mark.usefixtures('clear_db')
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
    assert SsspFamily.objects.count() == 1

    family = SsspFamily.objects.get(label=label)
    assert family.label == label


@pytest.mark.usefixtures('clear_db')
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
    assert PseudoDojoFamily.objects.count() == 1

    family = PseudoDojoFamily.objects.get(label=label)
    assert family.label == label


@pytest.mark.usefixtures('clear_db', 'chtmpdir')
def test_install_sssp_download_only(run_monkeypatched_install_sssp):
    """Test the ``aiida-pseudo install sssp`` command with the ``--download-only`` option."""
    options = ['--download-only']
    result = run_monkeypatched_install_sssp(options=options)

    assert SsspFamily.objects.count() == 0
    assert 'written to the current directory.' in result.output


@pytest.mark.usefixtures('clear_db', 'chtmpdir')
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

    assert SsspFamily.objects.count() == 1
    assert 'written to the current directory.' in result.output


@pytest.mark.usefixtures('clear_db', 'chtmpdir')
def test_install_pseudo_dojo_download_only(run_monkeypatched_install_pseudo_dojo):
    """Test the ``aiida-pseudo install pseudo-dojo`` command with the ``--download-only`` option."""
    options = ['--download-only']
    result = run_monkeypatched_install_pseudo_dojo(options=options)

    assert PseudoDojoFamily.objects.count() == 0
    assert 'written to the current directory.' in result.output


@pytest.mark.usefixtures('clear_db', 'chtmpdir')
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
        '--download-only', '-v', version, '-x', functional, '-r', relativistic, '-p', protocol, '-f', pseudo_format
    ]
    result = run_monkeypatched_install_pseudo_dojo(options=options)

    assert PseudoDojoFamily.objects.count() == 1
    assert 'written to the current directory.' in result.output
