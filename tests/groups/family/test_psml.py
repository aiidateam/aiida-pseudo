# -*- coding: utf-8 -*-
# pylint: disable=unused-argument,pointless-statement
"""Tests for the `PsmlFamily` class."""
import pytest

from aiida_pseudo.groups.family.psml import PsmlFamily


def test_type_string(clear_db):
    """Verify the `_type_string` class attribute is correctly set to the corresponding entry point name."""
    assert PsmlFamily._type_string == 'pseudo.family.psml'  # pylint: disable=protected-access


def test_construct(clear_db):
    """Test the construction of `PsmlFamily` works."""
    family = PsmlFamily(label='family').store()
    assert isinstance(family, PsmlFamily)

    description = 'SSSP description'
    family = PsmlFamily(label='SSSP/v1.1', description=description).store()
    assert isinstance(family, PsmlFamily)
    assert family.description == description


@pytest.mark.usefixtures('clear_db')
def test_create_from_folder(filepath_pseudos):
    """Test the `PsmlFamily.create_from_folder` class method."""
    label = 'label'
    family = PsmlFamily.create_from_folder(filepath_pseudos('psml'), label)
    assert isinstance(family, PsmlFamily)


@pytest.mark.usefixtures('clear_db')
def test_create_from_folder_duplicate(filepath_pseudos):
    """Test that `PsmlFamily.create_from_folder` raises for duplicate label."""
    label = 'label'
    PsmlFamily(label=label).store()

    with pytest.raises(ValueError, match=r'the PsmlFamily `.*` already exists'):
        PsmlFamily.create_from_folder(filepath_pseudos('psml'), label)
