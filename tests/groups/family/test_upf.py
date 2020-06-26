# -*- coding: utf-8 -*-
# pylint: disable=unused-argument,pointless-statement
"""Tests for the `UpfFamily` class."""
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
