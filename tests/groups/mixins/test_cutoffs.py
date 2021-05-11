# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""Tests for the :mod:`aiida_pseudo.groups.mixins.cutoffs` module."""
import copy

import pytest

from aiida_pseudo.groups.family import CutoffsPseudoPotentialFamily


@pytest.mark.usefixtures('clear_db')
def test_get_cutoffs_dict(get_pseudo_family, generate_cutoffs_dict):
    """Test the ``CutoffsPseudoPotentialFamily._get_cutoffs_dict`` method."""
    family = get_pseudo_family(cls=CutoffsPseudoPotentialFamily)
    assert family._get_cutoffs_dict() == {}  # pylint: disable=protected-access

    for stringency, cutoffs in generate_cutoffs_dict(family).items():
        family.set_cutoffs(cutoffs, stringency)
    assert family._get_cutoffs_dict() == generate_cutoffs_dict(family)  # pylint: disable=protected-access


@pytest.mark.usefixtures('clear_db')
def test_get_cutoffs_unit_dict(get_pseudo_family, generate_cutoffs_dict):
    """Test the ``CutoffsPseudoPotentialFamily._get_cutoffs_unit_dict`` method."""
    family = get_pseudo_family(cls=CutoffsPseudoPotentialFamily)
    assert family._get_cutoffs_unit_dict() == {}  # pylint: disable=protected-access

    default_units_dict = {}
    for stringency, cutoffs in generate_cutoffs_dict(family).items():
        family.set_cutoffs(cutoffs, stringency)
        default_units_dict[stringency] = CutoffsPseudoPotentialFamily.DEFAULT_UNIT

    assert family._get_cutoffs_unit_dict() == default_units_dict  # pylint: disable=protected-access


@pytest.mark.usefixtures('clear_db')
def test_validate_cutoffs_unit():
    """Test the ``CutoffsPseudoPotentialFamily.validate_cutoffs_unit`` method."""
    with pytest.raises(TypeError):
        CutoffsPseudoPotentialFamily.validate_cutoffs_unit(10)

    with pytest.raises(ValueError, match=r'`invalid` is not a valid unit.'):
        CutoffsPseudoPotentialFamily.validate_cutoffs_unit('invalid')

    with pytest.raises(ValueError, match=r'`watt` is not a valid energy unit.'):
        CutoffsPseudoPotentialFamily.validate_cutoffs_unit('watt')


@pytest.mark.usefixtures('clear_db')
def test_validate_stringency(get_pseudo_family, generate_cutoffs):
    """Test the ``CutoffsPseudoPotentialFamily.validate_stringency`` method."""
    family = get_pseudo_family(cls=CutoffsPseudoPotentialFamily)

    with pytest.raises(ValueError, match=r'stringency `.*` is not one of the available cutoff stringencies for this'):
        family.validate_stringency('default')

    cutoffs = generate_cutoffs(family)
    stringency = 'default'
    family.set_cutoffs(cutoffs, stringency)

    with pytest.raises(ValueError, match=r'stringency `.*` is not one of the available cutoff stringencies for this'):
        family.validate_stringency(stringency + 'non-existing')

    family.validate_stringency(stringency)


@pytest.mark.usefixtures('clear_db')
def test_get_default_stringency(get_pseudo_family, generate_cutoffs):
    """Test the ``CutoffsPseudoPotentialFamily.get_default_stringency`` method."""
    family = get_pseudo_family(cls=CutoffsPseudoPotentialFamily)

    with pytest.raises(ValueError, match='no default stringency has been defined.'):
        family.get_default_stringency()

    cutoffs = generate_cutoffs(family)
    stringency = 'default'
    family.set_cutoffs(cutoffs, stringency)

    assert family.get_default_stringency() == stringency


@pytest.mark.usefixtures('clear_db')
def test_set_default_stringency(get_pseudo_family, generate_cutoffs_dict):
    """Test the ``CutoffsPseudoPotentialFamily.set_default_stringency`` method."""
    family = get_pseudo_family(cls=CutoffsPseudoPotentialFamily)
    assert family.get_cutoff_stringencies() == ()

    stringencies = ('low', 'normal')
    for stringency, cutoffs in generate_cutoffs_dict(family, stringencies).items():
        family.set_cutoffs(cutoffs, stringency)

    assert family.get_default_stringency() == 'low'

    with pytest.raises(ValueError, match=r'the default stringency cannot be unset'):
        family.set_default_stringency(None)

    with pytest.raises(ValueError, match=r'stringency `nonexistent` is not one of the available cutoff stringencies'):
        family.set_default_stringency('nonexistent')

    family.set_default_stringency('normal')
    assert family.get_default_stringency() == 'normal'


@pytest.mark.usefixtures('clear_db')
def test_get_cutoff_stringencies(get_pseudo_family, generate_cutoffs_dict):
    """Test the ``CutoffsPseudoPotentialFamily.get_cutoff_stringencies`` method."""
    family = get_pseudo_family(cls=CutoffsPseudoPotentialFamily)
    assert family.get_cutoff_stringencies() == ()

    stringencies = ('low', 'normal', 'high')
    for stringency, cutoffs in generate_cutoffs_dict(family, stringencies).items():
        family.set_cutoffs(cutoffs, stringency)

    assert sorted(family.get_cutoff_stringencies()) == sorted(stringencies)


@pytest.mark.usefixtures('clear_db')
def test_set_cutoffs(get_pseudo_family, generate_cutoffs):
    """Test the ``CutoffsPseudoPotentialFamily.set_cutoffs`` method."""
    elements = ['Ar', 'He']
    family = get_pseudo_family(label='SSSP/1.0/PBE/efficiency', cls=CutoffsPseudoPotentialFamily, elements=elements)
    cutoffs = generate_cutoffs(family)
    stringency = 'default'

    family.set_cutoffs(cutoffs, stringency)
    assert family.get_cutoffs() == cutoffs
    assert family.get_cutoffs(stringency) == cutoffs

    with pytest.raises(ValueError, match=r'cutoffs defined for unsupported elements: .*'):
        cutoffs_invalid = copy.deepcopy(cutoffs)
        cutoffs_invalid['C'] = {'cutoff_wfc': 1.0, 'cutoff_rho': 2.0}
        family.set_cutoffs(cutoffs_invalid, stringency)

    with pytest.raises(ValueError, match=r'cutoffs not defined for all family elements: .*'):
        cutoffs_invalid = copy.deepcopy(cutoffs)
        cutoffs_invalid.pop('He')
        family.set_cutoffs(cutoffs_invalid, stringency)

    with pytest.raises(ValueError, match=r'invalid cutoff keys for element .*: .*'):
        cutoffs_invalid = copy.deepcopy(cutoffs)
        cutoffs_invalid['He'] = {'cutoff_wfc': 1.0}
        family.set_cutoffs(cutoffs_invalid, stringency)

    with pytest.raises(ValueError, match=r'invalid cutoff keys for element .*: .*'):
        cutoffs_invalid = copy.deepcopy(cutoffs)
        cutoffs_invalid['He'] = {'cutoff_wfc': 1.0, 'cutoff_rho': 2.0, 'cutoff_extra': 3.0}
        family.set_cutoffs(cutoffs_invalid, stringency)

    with pytest.raises(ValueError, match=r'invalid cutoff values for element .*: .*'):
        cutoffs_invalid = copy.deepcopy(cutoffs)
        cutoffs_invalid['He'] = {'cutoff_wfc': 1.0, 'cutoff_rho': 'string'}
        family.set_cutoffs(cutoffs_invalid, stringency)


@pytest.mark.usefixtures('clear_db')
def test_set_cutoffs_unit_default(get_pseudo_family, generate_cutoffs):
    """Test the ``CutoffsPseudoPotentialFamily.set_cutoffs`` sets a default unit if not specified."""
    elements = ['Ar']
    family = get_pseudo_family(label='SSSP/1.0/PBE/efficiency', cls=CutoffsPseudoPotentialFamily, elements=elements)
    cutoffs = generate_cutoffs(family)
    stringency = 'default'

    family.set_cutoffs(cutoffs, stringency)
    assert family.get_cutoffs_unit() == CutoffsPseudoPotentialFamily.DEFAULT_UNIT


@pytest.mark.usefixtures('clear_db')
def test_set_cutoffs_multiple_units(get_pseudo_family, generate_cutoffs):
    """Test ``CutoffsPseudoPotentialFamily.set_cutoffs`` correctly sets separate units for different stringencies."""
    elements = ['Ar']
    family = get_pseudo_family(label='SSSP/1.0/PBE/efficiency', cls=CutoffsPseudoPotentialFamily, elements=elements)
    cutoffs = generate_cutoffs(family)

    cutoffs_unit_dict = {}

    stringency = 'default'
    unit = 'hartree'
    family.set_cutoffs(cutoffs, stringency, unit)
    cutoffs_unit_dict[stringency] = unit
    assert family.get_cutoffs_unit() == unit

    stringency = 'rydberg'
    unit = 'Ry'
    family.set_cutoffs(cutoffs, stringency, unit)
    cutoffs_unit_dict[stringency] = unit
    assert family.get_cutoffs_unit(stringency) == unit

    # pylint: disable=protected-access
    assert family._get_cutoffs_unit_dict() == {'default': 'hartree', 'rydberg': 'Ry'}


@pytest.mark.usefixtures('clear_db')
def test_set_cutoffs_auto_default(get_pseudo_family, generate_cutoffs):
    """Test that the ``CutoffsPseudoPotentialFamily.set_cutoffs`` method specifies the correct default stringency.

    If family only has one stringency specified, the `set_cutoffs` method automatically sets this as the default.
    """
    elements = ['Ar']
    family = get_pseudo_family(label='SSSP/1.0/PBE/efficiency', cls=CutoffsPseudoPotentialFamily, elements=elements)
    cutoffs = generate_cutoffs(family)
    stringency = 'default'

    family.set_cutoffs(cutoffs, stringency)
    assert family.get_cutoffs() == cutoffs
    assert family.get_default_stringency() == 'default'


@pytest.mark.usefixtures('clear_db')
def test_get_cutoffs(get_pseudo_family, generate_cutoffs):
    """Test the ``CutoffsPseudoPotentialFamily.get_cutoffs`` method."""
    elements = ['Ar', 'He']
    family = get_pseudo_family(label='SSSP/1.0/PBE/efficiency', cls=CutoffsPseudoPotentialFamily, elements=elements)
    cutoffs = generate_cutoffs(family)
    stringency = 'default'

    with pytest.raises(ValueError, match='no default stringency has been defined.'):
        family.get_cutoffs()

    family.set_cutoffs(cutoffs, stringency)

    with pytest.raises(ValueError, match=r'stringency `.*` is not one of the available cutoff stringencies for this'):
        family.get_cutoffs('non-existing')

    assert family.get_cutoffs() == cutoffs

    low_cutoffs = {element: {'cutoff_wfc': 0.5, 'cutoff_rho': 1.0} for element in elements}
    family.set_cutoffs(low_cutoffs, 'low')

    assert family.get_cutoffs('low') == low_cutoffs


@pytest.mark.usefixtures('clear_db')
def test_get_recommended_cutoffs(get_pseudo_family, generate_structure, generate_cutoffs):
    """Test the ``CutoffsPseudoPotentialFamily.get_recommended_cutoffs`` method."""
    elements = ['Ar', 'He']
    family = get_pseudo_family(label='SSSP/1.0/PBE/efficiency', cls=CutoffsPseudoPotentialFamily, elements=elements)
    cutoffs = generate_cutoffs(family)
    stringency = 'default'
    family.set_cutoffs(cutoffs, stringency)

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


@pytest.mark.usefixtures('clear_db')
def test_get_recommended_cutoffs_unit(get_pseudo_family, generate_cutoffs):
    """Test the ``CutoffsPseudoPotentialFamily.get_recommended_cutoffs`` method with the ``unit`` argument."""
    elements = ['Ar', 'He']
    family = get_pseudo_family(label='SSSP/1.0/PBE/efficiency', cls=CutoffsPseudoPotentialFamily, elements=elements)
    cutoffs = generate_cutoffs(family)
    stringency = 'default'
    unit = 'Eh'
    family.set_cutoffs(cutoffs, stringency, unit)

    cutoffs_ar = cutoffs['Ar']

    expected = (cutoffs_ar['cutoff_wfc'], cutoffs_ar['cutoff_rho'])
    assert family.get_recommended_cutoffs(elements='Ar') == expected

    expected = (cutoffs_ar['cutoff_wfc'] * 2, cutoffs_ar['cutoff_rho'] * 2)
    assert family.get_recommended_cutoffs(elements='Ar', unit='Ry') == expected


@pytest.mark.usefixtures('clear_db')
def test_get_cutoffs_unit(get_pseudo_family, generate_cutoffs):
    """Test the ``CutoffsPseudoPotentialFamily.get_cutoffs_unit`` method."""
    elements = ['Ar', 'He']
    family = get_pseudo_family(label='SSSP/1.0/PBE/efficiency', cls=CutoffsPseudoPotentialFamily, elements=elements)
    cutoffs = generate_cutoffs(family)
    stringency = 'default'
    family.set_cutoffs(cutoffs, stringency)

    assert family.get_cutoffs_unit() == 'eV'
    cutoffs = family.get_cutoffs()
    stringency = family.get_default_stringency()

    family.set_cutoffs(cutoffs, stringency, unit='Ry')
    assert family.get_cutoffs_unit() == 'Ry'

    family.set_cutoffs(cutoffs, stringency, unit='Eh')
    assert family.get_cutoffs_unit() == 'Eh'


@pytest.mark.usefixtures('clear_db')
def test_delete_cutoffs(get_pseudo_family, generate_cutoffs_dict):
    """Test the ``CutoffsPseudoPotentialFamily.delete_cutoffs`` method."""
    elements = ['Ar', 'He']
    family = get_pseudo_family(label='SSSP/1.0/PBE/efficiency', cls=CutoffsPseudoPotentialFamily, elements=elements)

    stringencies = ('low', 'normal', 'high')
    for stringency, cutoffs in generate_cutoffs_dict(family, stringencies).items():
        family.set_cutoffs(cutoffs, stringency)

    with pytest.raises(ValueError, match=r'stringency `nonexistent` is not one of the available cutoff stringencies'):
        family.delete_cutoffs('nonexistent')

    with pytest.warns(UserWarning, match='`low` was the default stringency of this family. Please set'):
        family.delete_cutoffs('low')
    assert sorted(family.get_cutoff_stringencies()) == sorted(('normal', 'high'))

    with pytest.raises(ValueError, match='no default stringency has been defined.'):
        family.get_default_stringency()

    with pytest.warns(UserWarning, match='Setting `high` as the default since it is now the only defined stringency.'):
        family.delete_cutoffs('normal')

    assert family.get_default_stringency() == 'high'
