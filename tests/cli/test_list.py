# -*- coding: utf-8 -*-
# pylint: disable=unused-argument
"""Tests for the command `aiida-pseudo list`."""
from aiida_pseudo.cli import cmd_list
from aiida_pseudo.cli.list import PROJECTIONS_VALID
from aiida_pseudo.data.pseudo import UpfData
from aiida_pseudo.groups.family import PseudoPotentialFamily, SsspFamily


def test_list(clear_db, run_cli_command, get_pseudo_family):
    """Test the `aiida-pseudo list` command."""
    result = run_cli_command(cmd_list)
    assert 'no pseudo potential families have been installed yet: use `aiida-pseudo install`.' in result.output

    label = 'SSSP/1.0/PBE/efficiency'
    family = get_pseudo_family(label=label)
    result = run_cli_command(cmd_list)

    assert family.label in result.output


def test_list_raw(clear_db, run_cli_command, get_pseudo_family):
    """Test the `-r/--raw` option."""
    get_pseudo_family()

    for option in ['-r', '--raw']:
        result = run_cli_command(cmd_list, [option])
        assert len(result.output_lines) == 1


def test_list_project(clear_db, run_cli_command, get_pseudo_family):
    """Test the `-p/--project` option."""
    family = get_pseudo_family()

    # Test that all `PROJECTIONS_VALID` can actually be projected and don't except
    for option in ['-P', '--project']:
        run_cli_command(cmd_list, [option] + list(PROJECTIONS_VALID))

    result = run_cli_command(cmd_list, ['--raw', '-P', 'label'])
    assert len(result.output_lines) == 1
    assert family.label in result.output


def test_list_filter(clear_db, run_cli_command, get_pseudo_family):
    """Test the filtering option `-F`."""
    family_base = get_pseudo_family(label='Pseudo potential family', cls=PseudoPotentialFamily)
    family_sssp = get_pseudo_family(label='SSSP/1.0/PBE/efficiency', cls=SsspFamily, pseudo_type=UpfData)

    assert PseudoPotentialFamily.objects.count() == 2

    result = run_cli_command(cmd_list, ['--raw'])
    assert len(result.output_lines) == 2
    assert family_base.label in result.output
    assert family_sssp.label in result.output

    result = run_cli_command(cmd_list, ['--raw', '-F', 'pseudo.family.sssp'])
    assert len(result.output_lines) == 1
    assert family_base.label not in result.output
    assert family_sssp.label in result.output


def test_list_filter_no_result(clear_db, run_cli_command, get_pseudo_family):
    """Test the filtering option `-F` for a type for which no families exist."""
    get_pseudo_family(label='Pseudo potential family', cls=PseudoPotentialFamily)

    result = run_cli_command(cmd_list, ['--raw', '-F', 'pseudo.family.sssp'])
    assert 'no pseudo potential families found that match the filtering criteria.' in result.output
