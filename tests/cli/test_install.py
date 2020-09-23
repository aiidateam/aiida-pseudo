# -*- coding: utf-8 -*-
"""Tests for `aiida-pseudo install`."""
import pytest

from aiida.orm import QueryBuilder

from aiida_pseudo.cli import cmd_install_family, cmd_install_sssp
from aiida_pseudo.groups.family import PseudoPotentialFamily, UpfFamily


@pytest.mark.usefixtures('clear_db')
def test_install_family(run_cli_command, get_pseudo_archive):
    """Test `aiida-pseudo install family`."""
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
def test_install_family_url(run_cli_command):
    """Test `aiida-pseudo install family` when installing from a URL.

    When a URL is passed, the parameter converts it into a `http.client.HTTPResponse`, which is not trivial to mock so
    instead we use an actual URL, which is slow, but is anyway already tested indirectly in `test_install_sssp`.
    """
    label = 'family'
    description = 'description'
    filepath_archive = 'https://legacy-archive.materialscloud.org/file/2018.0001/v4/SSSP_1.0_PBE_efficiency.tar.gz'
    options = ['-D', description, filepath_archive, label, '-T', 'pseudo.family.upf']

    result = run_cli_command(cmd_install_family, options)
    assert f'installed `{label}`' in result.output
    assert UpfFamily.objects.count() == 1

    family = UpfFamily.objects.get(label=label)
    assert family.__class__ is UpfFamily
    assert family.description == description
    assert len(family.pseudos) != 0


@pytest.mark.usefixtures('clear_db')
def test_install_family_upf(run_cli_command, get_pseudo_archive):
    """Test `aiida-pseudo install family` to install a `UpfFamily`."""
    label = 'family'
    description = 'description'
    filepath_archive = next(get_pseudo_archive())
    options = ['-D', description, '-T', 'pseudo.family.upf', filepath_archive, label]

    result = run_cli_command(cmd_install_family, options)
    assert f'installed `{label}`' in result.output
    assert UpfFamily.objects.count() == 1

    family = UpfFamily.objects.get(label=label)
    assert family.__class__ is UpfFamily
    assert family.description == description
    assert len(family.pseudos) != 0


@pytest.mark.usefixtures('clear_db')
def test_install_sssp(run_cli_command):
    """Test the `aiida-pseudo install sssp` command."""
    from aiida_pseudo import __version__
    from aiida_pseudo.groups.family import SsspFamily

    result = run_cli_command(cmd_install_sssp)
    assert 'installed `SSSP/' in result.output
    assert QueryBuilder().append(SsspFamily).count() == 1

    family = QueryBuilder().append(SsspFamily).one()[0]
    assert family.get_cutoffs is not None
    assert f'SSSP v1.1 PBE efficiency installed with aiida-pseudo v{__version__}' in family.description
    assert 'Archive pseudos md5: 4803ce9fd1d84c777f87173cd4a2de33' in family.description
    assert 'Pseudo metadata md5: 0d5d6c2c840383c7c4fc3a99b5dc3001' in family.description

    result = run_cli_command(cmd_install_sssp, raises=SystemExit)
    assert 'is already installed' in result.output
