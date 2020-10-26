# -*- coding: utf-8 -*-
# pylint: disable=unused-argument,pointless-statement
"""Tests for the `Psp8Family` class."""
import pytest

from aiida_pseudo.groups.family.psp8 import Psp8Family


def test_type_string(clear_db):
    """Verify the `_type_string` class attribute is correctly set to the corresponding entry point name."""
    assert Psp8Family._type_string == 'pseudo.family.psp8'  # pylint: disable=protected-access


def test_construct(clear_db):
    """Test the construction of `Psp8Family` works."""
    family = Psp8Family(label='family').store()
    assert isinstance(family, Psp8Family)

    description = 'PseudoDojo description'
    family = Psp8Family(label='PseudoDojo/v0.4', description=description).store()
    assert isinstance(family, Psp8Family)
    assert family.description == description


@pytest.mark.usefixtures('clear_db')
def test_create_from_folder(filepath_pseudos):
    """Test the `Psp8Family.create_from_folder` class method."""
    label = 'label'
    family = Psp8Family.create_from_folder(filepath_pseudos('psp8'), label)
    assert isinstance(family, Psp8Family)


@pytest.mark.usefixtures('clear_db')
def test_create_from_folder_duplicate(filepath_pseudos):
    """Test that `Psp8Family.create_from_folder` raises for duplicate label."""
    label = 'label'
    Psp8Family(label=label).store()

    with pytest.raises(ValueError, match=r'the Psp8Family `.*` already exists'):
        Psp8Family.create_from_folder(filepath_pseudos('psp8'), label)
