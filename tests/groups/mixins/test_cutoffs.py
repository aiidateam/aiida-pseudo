# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
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


@pytest.fixture
def get_cutoffs():
    """Return a cutoffs dictionary."""

    def _get_cutoffs(family, stringencies=('default',)):
        cutoffs = {}

        for element in family.elements:
            cutoffs[element] = {
                'cutoff_wfc': 1.0,
                'cutoff_rho': 2.0,
            }

        return {stringency: cutoffs for stringency in stringencies}

    return _get_cutoffs


@pytest.mark.usefixtures('clear_db')
def test_get_cutoffs_private(get_pseudo_family, get_cutoffs):
    """Test the ``RecommendedCutoffMixin._get_cutoffs`` method."""
    family = get_pseudo_family(cls=CutoffFamily)
    assert family._get_cutoffs() == {}  # pylint: disable=protected-access

    family.set_cutoffs(get_cutoffs(family), 'default')
    assert family._get_cutoffs() == get_cutoffs(family)  # pylint: disable=protected-access


@pytest.mark.usefixtures('clear_db')
def test_validate_stringency(get_pseudo_family, get_cutoffs):
    """Test the ``RecommendedCutoffMixin.validate_stringency`` method."""
    family = get_pseudo_family(cls=CutoffFamily)

    with pytest.raises(ValueError, match=r'stringency `.*` is not defined for this family.'):
        family.validate_stringency('default')

    cutoffs = get_cutoffs(family)
    stringency = list(cutoffs.keys())[0]
    family.set_cutoffs(cutoffs, stringency)

    with pytest.raises(ValueError, match=r'stringency `.*` is not defined for this family.'):
        family.validate_stringency(stringency + 'non-existing')

    family.validate_stringency(stringency)


@pytest.mark.usefixtures('clear_db')
def test_get_default_stringency(get_pseudo_family, get_cutoffs):
    """Test the ``RecommendedCutoffMixin.get_default_stringency`` method."""
    family = get_pseudo_family(cls=CutoffFamily)

    with pytest.raises(ValueError, match='no default stringency has been defined.'):
        family.get_default_stringency()

    cutoffs = get_cutoffs(family)
    stringency = list(cutoffs.keys())[0]
    family.set_cutoffs(cutoffs, stringency)

    assert family.get_default_stringency() == stringency


@pytest.mark.usefixtures('clear_db')
def test_get_cutoff_stringencies(get_pseudo_family, get_cutoffs):
    """Test the ``RecommendedCutoffMixin.get_cutoff_stringencies`` method."""
    family = get_pseudo_family(cls=CutoffFamily)
    assert family.get_cutoff_stringencies() == ()

    stringencies = ('low', 'normal', 'high')
    cutoffs = get_cutoffs(family, stringencies)
    family.set_cutoffs(cutoffs, stringencies[0])

    assert sorted(family.get_cutoff_stringencies()) == sorted(stringencies)


@pytest.mark.usefixtures('clear_db')
def test_set_cutoffs(get_pseudo_family):
    """Test the `RecommendedCutoffMixin.set_cutoffs` method."""
    elements = ['Ar', 'He']
    family = get_pseudo_family(label='SSSP/1.0/PBE/efficiency', cls=CutoffFamily, elements=elements)
    cutoffs = {'default': {element: {'cutoff_wfc': 1.0, 'cutoff_rho': 2.0} for element in elements}}
    family.set_cutoffs(cutoffs, 'default')

    assert family.get_cutoffs() == cutoffs['default']

    with pytest.raises(ValueError, match=r'cutoffs defined for unsupported elements: .*'):
        cutoffs_invalid = copy.deepcopy(cutoffs)
        cutoffs_invalid['default']['C'] = {'cutoff_wfc': 1.0, 'cutoff_rho': 2.0}
        family.set_cutoffs(cutoffs_invalid, 'default')

    with pytest.raises(ValueError, match=r'cutoffs not defined for all family elements: .*'):
        cutoffs_invalid = copy.deepcopy(cutoffs)
        cutoffs_invalid['default'].pop('He')
        family.set_cutoffs(cutoffs_invalid, 'default')

    with pytest.raises(ValueError, match=r'invalid cutoff keys for stringency `default` and element .*: .*'):
        cutoffs_invalid = copy.deepcopy(cutoffs)
        cutoffs_invalid['default']['He'] = {'cutoff_wfc': 1.0}
        family.set_cutoffs(cutoffs_invalid, 'default')

    with pytest.raises(ValueError, match=r'invalid cutoff keys for stringency `default` and element .*: .*'):
        cutoffs_invalid = copy.deepcopy(cutoffs)
        cutoffs_invalid['default']['He'] = {'cutoff_wfc': 1.0, 'cutoff_rho': 2.0, 'cutoff_extra': 3.0}
        family.set_cutoffs(cutoffs_invalid, 'default')

    with pytest.raises(ValueError, match=r'invalid cutoff values for stringency `default` and element .*: .*'):
        cutoffs_invalid = copy.deepcopy(cutoffs)
        cutoffs_invalid['default']['He'] = {'cutoff_wfc': 1.0, 'cutoff_rho': 'string'}
        family.set_cutoffs(cutoffs_invalid, 'default')


@pytest.mark.usefixtures('clear_db')
def test_set_cutoffs_auto_default(get_pseudo_family):
    """Test the `RecommendedCutoffMixin.set_cutoffs` method when not specifying explicit default.

    If the cutoffs specified only contain a single set, the `default_stringency` is determined automatically.
    """
    elements = ['Ar']
    family = get_pseudo_family(label='SSSP/1.0/PBE/efficiency', cls=CutoffFamily, elements=elements)
    values = {element: {'cutoff_wfc': 1.0, 'cutoff_rho': 2.0} for element in elements}
    cutoffs = {'default': values}

    with pytest.raises(ValueError, match='specify a default stringency when specifying multiple cutoff sets.'):
        family.set_cutoffs({'low': values, 'hi': values})

    family.set_cutoffs(cutoffs)
    assert family.get_cutoffs() == cutoffs['default']
    assert family.get_default_stringency() == 'default'


@pytest.mark.usefixtures('clear_db')
def test_get_cutoffs(get_pseudo_family):
    """Test the `RecommendedCutoffMixin.get_cutoffs` method."""
    elements = ['Ar', 'He']
    family = get_pseudo_family(label='SSSP/1.0/PBE/efficiency', cls=CutoffFamily, elements=elements)
    cutoffs = {'default': {element: {'cutoff_wfc': 1.0, 'cutoff_rho': 2.0} for element in elements}}

    with pytest.raises(ValueError, match='no default stringency has been defined.'):
        family.get_cutoffs()

    family.set_cutoffs(cutoffs, 'default')

    with pytest.raises(ValueError, match=r'stringency `.*` is not defined for this family.'):
        family.get_cutoffs('non-existing')

    assert family.get_cutoffs() == cutoffs['default']


@pytest.mark.usefixtures('clear_db')
def test_get_recommended_cutoffs(get_pseudo_family, generate_structure):
    """Test the `RecommendedCutoffMixin.get_recommended_cutoffs` method."""
    elements = ['Ar', 'He']
    cutoffs = {
        'default': {
            'Ar': {
                'cutoff_wfc': 1.0,
                'cutoff_rho': 2.0
            },
            'He': {
                'cutoff_wfc': 3.0,
                'cutoff_rho': 8.0
            },
        }
    }
    family = get_pseudo_family(label='SSSP/1.0/PBE/efficiency', cls=CutoffFamily, elements=elements)
    family.set_cutoffs(cutoffs, 'default')
    structure = generate_structure(elements=elements)

    with pytest.raises(ValueError):
        family.get_recommended_cutoffs(elements=None, structure=None)

    with pytest.raises(ValueError):
        family.get_recommended_cutoffs(elements='Ar', structure=structure)

    with pytest.raises(TypeError):
        family.get_recommended_cutoffs(elements=False, structure=None)

    with pytest.raises(TypeError):
        family.get_recommended_cutoffs(elements=None, structure='Ar')

    expected = cutoffs['default']['Ar']
    assert family.get_recommended_cutoffs(elements='Ar') == (expected['cutoff_wfc'], expected['cutoff_rho'])
    assert family.get_recommended_cutoffs(elements=('Ar',)) == (expected['cutoff_wfc'], expected['cutoff_rho'])

    expected = cutoffs['default']['He']
    assert family.get_recommended_cutoffs(elements=('Ar', 'He')) == (expected['cutoff_wfc'], expected['cutoff_rho'])

    expected = cutoffs['default']['He']
    assert family.get_recommended_cutoffs(structure=structure) == (expected['cutoff_wfc'], expected['cutoff_rho'])

    # Try structure with multiple kinds with the same element
    expected = cutoffs['default']['He']
    structure = generate_structure(elements=['He1', 'He2'])
    assert family.get_recommended_cutoffs(structure=structure) == (expected['cutoff_wfc'], expected['cutoff_rho'])
