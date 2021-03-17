# -*- coding: utf-8 -*-
# pylint: disable=unused-argument
"""Tests for the command `aiida-pseudo show`."""
from numpy.testing import assert_almost_equal

from aiida.orm import Group
from aiida_pseudo.cli import cmd_show
from aiida_pseudo.groups.family import PseudoPotentialFamily, CutoffsFamily


def test_show(clear_db, run_cli_command, get_pseudo_family):
    """Test the `aiida-pseudo show` command."""
    family = get_pseudo_family()
    result = run_cli_command(cmd_show, [family.label])
    for node in family.nodes:
        assert node.md5 in result.output
        assert node.element in result.output
        assert node.filename in result.output


def test_show_recommended_cutoffs(clear_db, run_cli_command, get_pseudo_family):
    """Test the `aiida-pseudo show` command for a family with recommended cutoffs."""
    family = get_pseudo_family(cls=CutoffsFamily)
    cutoffs = {
        'normal': {},
        'high': {},
    }

    for element in family.elements:
        cutoffs['normal'][element] = {'cutoff_wfc': 1.0, 'cutoff_rho': 2.0}
        cutoffs['high'][element] = {'cutoff_wfc': 3.0, 'cutoff_rho': 6.0}

    family.set_cutoffs(cutoffs, 'normal')

    # Test the command prints an error for a non-existing stringency
    result = run_cli_command(cmd_show, [family.label, '--stringency', 'non-existing'], raises=True)
    assert 'Invalid value for stringency: `non-existing` is not defined' in result.output

    # Test the command for default and explicit stringency
    for stringency in [None, 'high']:

        if stringency is not None:
            result = run_cli_command(cmd_show, [family.label, '--stringency', stringency, '--raw'])
        else:
            result = run_cli_command(cmd_show, [family.label, '--raw'])

        for index, node in enumerate(sorted(family.nodes, key=lambda pseudo: pseudo.element)):
            fields = result.output_lines[index].split()
            cutoffs = family.get_recommended_cutoffs(elements=node.element, stringency=stringency)
            assert node.element in fields[0]
            assert node.filename in fields[1]
            assert node.md5 in fields[2]
            assert_almost_equal(cutoffs[0], float(fields[3]))
            assert_almost_equal(cutoffs[1], float(fields[4]))


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
