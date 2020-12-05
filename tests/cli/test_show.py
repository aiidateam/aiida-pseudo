# -*- coding: utf-8 -*-
# pylint: disable=unused-argument
"""Tests for the command `aiida-pseudo show`."""
from aiida.orm import Group
from aiida_pseudo.cli import cmd_show
from aiida_pseudo.groups.family import PseudoPotentialFamily


def test_show(clear_db, run_cli_command, get_pseudo_family):
    """Test the `aiida-pseudo show` command."""
    family = get_pseudo_family()
    result = run_cli_command(cmd_show, [family.label])
    for node in family.nodes:
        assert node.md5 in result.output
        assert node.element in result.output
        assert node.filename in result.output


def test_show_argument_type(clear_db, run_cli_command, get_pseudo_family):
    """Test that `aiida-pseudo show` only accepts instances of `PseudoPotentialFamily` or subclasses as argument."""
    pseudo_family = get_pseudo_family(label='pseudo-family', cls=PseudoPotentialFamily)
    normal_group = Group('normal-group').store()

    run_cli_command(cmd_show, [pseudo_family.label])
    run_cli_command(cmd_show, [normal_group.label], raises=SystemExit)


def test_show_raw(clear_db, run_cli_command, get_pseudo_family):
    """Test the `-r/--raw` option."""
    family = get_pseudo_family()

    for option in ['-r', '--raw']:
        result = run_cli_command(cmd_show, [option, family.label])
        assert len(result.output_lines) == len(family.nodes)
