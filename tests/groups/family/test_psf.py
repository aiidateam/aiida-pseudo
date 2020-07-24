# -*- coding: utf-8 -*-
# pylint: disable=unused-argument,pointless-statement
"""Tests for the `PsfFamily` class."""
import pytest

from aiida_pseudo.groups.family.psf import PsfFamily


def test_type_string(clear_db):
    """Verify the `_type_string` class attribute is correctly set to the corresponding entry point name."""
    assert PsfFamily._type_string == 'pseudo.family.psf'  # pylint: disable=protected-access


def test_construct(clear_db):
    """Test the construction of `PsfFamily` works."""
    family = PsfFamily(label='family').store()
    assert isinstance(family, PsfFamily)

    description = 'SSSP description'
    family = PsfFamily(label='SSSP/v1.1', description=description).store()
    assert isinstance(family, PsfFamily)
    assert family.description == description


@pytest.mark.usefixtures('clear_db')
def test_create_from_folder(filepath_pseudos):
    """Test the `PsfFamily.create_from_folder` class method."""
    label = 'label'
    family = PsfFamily.create_from_folder(filepath_pseudos('psf'), label)
    assert isinstance(family, PsfFamily)


@pytest.mark.usefixtures('clear_db')
def test_create_from_folder_duplicate(filepath_pseudos):
    """Test that `PsfFamily.create_from_folder` raises for duplicate label."""
    label = 'label'
    PsfFamily(label=label).store()

    with pytest.raises(ValueError, match=r'the PsfFamily `.*` already exists'):
        PsfFamily.create_from_folder(filepath_pseudos('psf'), label)
