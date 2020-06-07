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
    options = ['-D', description, get_pseudo_archive, label]

    result = run_cli_command(cmd_install_family, options)
    assert 'installed `{}`'.format(label) in result.output
    assert PseudoPotentialFamily.objects.count() == 1

    family = PseudoPotentialFamily.objects.get(label=label)
    assert type(family) is PseudoPotentialFamily  # pylint: disable=unidiomatic-typecheck
    assert type(family) is not UpfFamily  # pylint: disable=unidiomatic-typecheck
    assert family.description == description
    assert len(family.pseudos) != 0


@pytest.mark.usefixtures('clear_db')
def test_install_family_upf(run_cli_command, get_pseudo_archive):
    """Test `aiida-pseudo install family` to install a `UpfFamily`."""
    label = 'family'
    description = 'description'
    options = ['-D', description, '-T', 'pseudo.family.upf', get_pseudo_archive, label]

    result = run_cli_command(cmd_install_family, options)
    assert 'installed `{}`'.format(label) in result.output
    assert UpfFamily.objects.count() == 1

    family = UpfFamily.objects.get(label=label)
    assert type(family) is not PseudoPotentialFamily  # pylint: disable=unidiomatic-typecheck
    assert type(family) is UpfFamily  # pylint: disable=unidiomatic-typecheck
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
    assert 'SSSP v1.1 PBE efficiency installed with aiida-pseudo v{}'.format(__version__) in family.description
    assert 'Archive pseudos md5: 4803ce9fd1d84c777f87173cd4a2de33' in family.description

    result = run_cli_command(cmd_install_sssp, raises=SystemExit)
    assert 'is already installed' in result.output
