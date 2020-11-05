# -*- coding: utf-8 -*-
"""Tests for the :mod:`aiida_pseudo.groups.mixins.cutoffs` module."""
import copy

import pytest

from aiida.orm.groups import GroupMeta
from aiida_pseudo.groups.family import PseudoPotentialFamily
from aiida_pseudo.groups.mixins import RecommendedCutoffMixin


class FixtureGroupMeta(GroupMeta):
    """Meta class for `aiida.orm.groups.Group` to automatically set the `type_string` attribute."""

    def __new__(mcs, name, bases, namespace, **kwargs):  # pylint: disable=bad-mcs-classmethod-argument
        """Construct new instance of the class."""
        newcls = GroupMeta.__new__(mcs, name, bases, namespace, **kwargs)  # pylint: disable=too-many-function-args
        newcls._type_string = 'test'  # pylint: disable=protected-access
        return newcls


class CutoffFamily(RecommendedCutoffMixin, PseudoPotentialFamily, metaclass=FixtureGroupMeta):
    """Test class for the ``RecommendedCutoffMixin``."""


@pytest.mark.usefixtures('clear_db')
def test_set_cutoffs(get_pseudo_family):
    """Test the `RecommendedCutoffMixin.set_cutoffs` method."""
    elements = ['Ar', 'He']
    family = get_pseudo_family(label='SSSP/1.0/PBE/efficiency', cls=CutoffFamily, elements=elements)
    cutoffs = {element: {'cutoff_wfc': 1.0, 'cutoff_rho': 2.0} for element in elements}
    family.set_cutoffs(cutoffs)

    assert family.get_cutoffs() == cutoffs

    with pytest.raises(ValueError, match=r'cutoffs defined for unsupported elements: .*'):
        cutoffs_invalid = copy.copy(cutoffs)
        cutoffs_invalid['C'] = {'cutoff_wfc': 1.0, 'cutoff_rho': 2.0}
        assert family.set_cutoffs(cutoffs_invalid)

    with pytest.raises(ValueError, match=r'cutoffs not defined for all family elements: .*'):
        cutoffs_invalid = copy.copy(cutoffs)
        cutoffs_invalid.pop('He')
        assert family.set_cutoffs(cutoffs_invalid)

    with pytest.raises(ValueError, match=r'invalid cutoff keys for element .*: .*'):
        cutoffs_invalid = copy.copy(cutoffs)
        cutoffs_invalid['He'] = {'cutoff_wfc': 1.0}
        assert family.set_cutoffs(cutoffs_invalid)

    with pytest.raises(ValueError, match=r'invalid cutoff keys for element .*: .*'):
        cutoffs_invalid = copy.copy(cutoffs)
        cutoffs_invalid['He'] = {'cutoff_wfc': 1.0, 'cutoff_rho': 2.0, 'cutoff_extra': 3.0}
        assert family.set_cutoffs(cutoffs_invalid)

    with pytest.raises(ValueError, match=r'invalid cutoff values for element .*: .*'):
        cutoffs_invalid = copy.copy(cutoffs)
        cutoffs_invalid['He'] = {'cutoff_wfc': 1.0, 'cutoff_rho': 'string'}
        assert family.set_cutoffs(cutoffs_invalid)


@pytest.mark.usefixtures('clear_db')
def test_get_cutoffs(get_pseudo_family):
    """Test the `RecommendedCutoffMixin.get_cutoffs` method."""
    elements = ['Ar', 'He']
    family = get_pseudo_family(label='SSSP/1.0/PBE/efficiency', cls=CutoffFamily, elements=elements)
    cutoffs = {element: {'cutoff_wfc': 1.0, 'cutoff_rho': 2.0} for element in elements}

    assert family.get_cutoffs() is None

    family.set_cutoffs(cutoffs)
    assert family.get_cutoffs() == cutoffs


@pytest.mark.usefixtures('clear_db')
def test_get_recommended_cutoffs(get_pseudo_family, generate_structure):
    """Test the `RecommendedCutoffMixin.get_recommended_cutoffs` method."""
    elements = ['Ar', 'He']
    cutoffs = {
        'Ar': {
            'cutoff_wfc': 1.0,
            'cutoff_rho': 2.0
        },
        'He': {
            'cutoff_wfc': 3.0,
            'cutoff_rho': 8.0
        },
    }
    family = get_pseudo_family(label='SSSP/1.0/PBE/efficiency', cls=CutoffFamily, elements=elements)
    family.set_cutoffs(cutoffs)
    structure = generate_structure(elements=elements)

    with pytest.raises(ValueError):
        family.get_recommended_cutoffs(elements=None, structure=None)

    with pytest.raises(ValueError):
        family.get_recommended_cutoffs(elements='Ar', structure=structure)

    with pytest.raises(TypeError):
        family.get_recommended_cutoffs(elements=False, structure=None)

    with pytest.raises(TypeError):
        family.get_recommended_cutoffs(elements=None, structure='Ar')

    expected = cutoffs['Ar']
    assert family.get_recommended_cutoffs(elements='Ar') == (expected['cutoff_wfc'], expected['cutoff_rho'])
    assert family.get_recommended_cutoffs(elements=('Ar',)) == (expected['cutoff_wfc'], expected['cutoff_rho'])

    expected = cutoffs['He']
    assert family.get_recommended_cutoffs(elements=('Ar', 'He')) == (expected['cutoff_wfc'], expected['cutoff_rho'])

    expected = cutoffs['He']
    assert family.get_recommended_cutoffs(structure=structure) == (expected['cutoff_wfc'], expected['cutoff_rho'])

    # Try structure with multiple kinds with the same element
    expected = cutoffs['He']
    structure = generate_structure(elements=['He1', 'He2'])
    assert family.get_recommended_cutoffs(structure=structure) == (expected['cutoff_wfc'], expected['cutoff_rho'])
