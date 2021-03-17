# -*- coding: utf-8 -*-
# pylint: disable=unused-argument
"""Tests for the command `aiida-pseudo show`."""
import json
import pytest

from aiida_pseudo.cli.family import cmd_family_cutoffs_set
from aiida_pseudo.groups.family import CutoffsFamily


@pytest.mark.usefixtures('clear_db')
def test_family_cutoffs_set(run_cli_command, get_pseudo_family, tmp_path):
    """Test the `aiida-pseudo family cutoffs set` command."""
    family = get_pseudo_family(cls=CutoffsFamily)
    cutoffs = {
        'normal': {},
        'high': {},
    }

    for element in family.elements:
        cutoffs['normal'][element] = {'cutoff_wfc': 1.0, 'cutoff_rho': 2.0}
        cutoffs['high'][element] = {'cutoff_wfc': 3.0, 'cutoff_rho': 6.0}

    # Set only the normal cutoffs for the family
    family.set_cutoffs({'normal': cutoffs['normal']}, 'normal')

    filepath = tmp_path / 'cutoffs.json'

    # Invalid JSON
    filepath.write_text('invalid content')
    result = run_cli_command(cmd_family_cutoffs_set, [family.label, str(filepath)], raises=True)
    assert "Error: Missing option '-s' / '--stringency'" in result.output

    # Invalid cutoffs structure
    filepath.write_text(json.dumps({'Ar': {'cutoff_rho': 300}}))
    result = run_cli_command(cmd_family_cutoffs_set, [family.label, str(filepath), '-s', 'high'], raises=True)
    assert 'Error: Invalid value for CUTOFFS:' in result.output

    # Set correct stringency
    stringency = 'high'
    filepath.write_text(json.dumps(cutoffs['high']))
    result = run_cli_command(cmd_family_cutoffs_set, [family.label, str(filepath), '-s', stringency])
    assert 'Success: set cutoffs for' in result.output
    assert stringency in family.get_cutoff_stringencies()
    assert family.get_cutoffs(stringency) == cutoffs[stringency]
