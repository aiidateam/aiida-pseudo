# -*- coding: utf-8 -*-
# pylint: disable=unused-argument,pointless-statement
"""Tests for the `UpfFamily` class."""
import copy

import pytest

from aiida_pseudo.groups.family.upf import UpfFamily


def test_type_string(clear_db):
    """Verify the `_type_string` class attribute is correctly set to the corresponding entry point name."""
    assert UpfFamily._type_string == 'pseudo.family.upf'  # pylint: disable=protected-access


def test_construct(clear_db):
    """Test the construction of `UpfFamily` works."""
    family = UpfFamily(label='family').store()
    assert isinstance(family, UpfFamily)

    description = 'SSSP description'
    family = UpfFamily(label='SSSP/v1.1', description=description).store()
    assert isinstance(family, UpfFamily)
    assert family.description == description


@pytest.mark.usefixtures('clear_db')
def test_create_from_folder(filepath_pseudos):
    """Test the `UpfFamily.create_from_folder` class method."""
    label = 'label'
    family = UpfFamily.create_from_folder(filepath_pseudos('upf'), label)
    assert isinstance(family, UpfFamily)


@pytest.mark.usefixtures('clear_db')
def test_create_from_folder_duplicate(filepath_pseudos):
    """Test that `UpfFamily.create_from_folder` raises for duplicate label."""
    label = 'label'
    UpfFamily(label=label).store()

    with pytest.raises(ValueError, match=r'the UpfFamily `.*` already exists'):
        UpfFamily.create_from_folder(filepath_pseudos('upf'), label)


@pytest.mark.usefixtures('clear_db')
def test_set_cutoffs(get_pseudo_family):
    """Test the `UpfFamily.set_cutoffs` method."""
    elements = ['Ar', 'He']
    family = get_pseudo_family(label='SSSP/1.0/PBE/efficiency', cls=UpfFamily, elements=elements)
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
    """Test the `UpfFamily.get_cutoffs` method."""
    elements = ['Ar', 'He']
    family = get_pseudo_family(label='SSSP/1.0/PBE/efficiency', cls=UpfFamily, elements=elements)
    cutoffs = {element: {'cutoff_wfc': 1.0, 'cutoff_rho': 2.0} for element in elements}

    assert family.get_cutoffs() is None

    family.set_cutoffs(cutoffs)
    assert family.get_cutoffs() == cutoffs


@pytest.mark.usefixtures('clear_db')
def test_get_recommended_cutoffs(get_pseudo_family, generate_structure):
    """Test the `UpfFamily.get_recommended_cutoffs` method."""
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
    family = get_pseudo_family(label='SSSP/1.0/PBE/efficiency', cls=UpfFamily, elements=elements)
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
