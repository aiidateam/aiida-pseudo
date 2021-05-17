# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""Tests for the :py:`~aiida_pseudo.data.pseudo.psf` module."""
import io
import os
import pathlib

import pytest

from aiida.common.exceptions import ModificationNotAllowed
from aiida_pseudo.data.pseudo import PsfData
from aiida_pseudo.data.pseudo.psf import parse_element


@pytest.mark.parametrize(('string', 'element'), [
    (b'c other\n', 'C'),
    (b'C other\n', 'C'),
    (b' C other\n', 'C'),
    (b'ca other\n', 'Ca'),
    (b'Ca other\n', 'Ca'),
    (b' Ca other\n', 'Ca'),
])
def test_parse_element(string, element):
    """Test the `parse_element` method."""
    assert parse_element(io.BytesIO(string)) == element


@pytest.fixture
def source(request, filepath_pseudos):
    """Return a pseudopotential, eiter as ``str``, ``Path`` or ``io.BytesIO``."""
    filepath_pseudo = pathlib.Path(filepath_pseudos(entry_point='psf')) / 'Ar.psf'

    if request.param is str:
        return str(filepath_pseudo)

    if request.param is pathlib.Path:
        return filepath_pseudo

    return io.BytesIO(filepath_pseudo.read_bytes())


@pytest.mark.parametrize('source', (io.BytesIO, str, pathlib.Path), indirect=True)
def test_constructor_source_types(source):
    """Test the constructor accept the various types."""
    pseudo = PsfData(source)
    assert isinstance(pseudo, PsfData)
    assert not pseudo.is_stored


def test_constructor(filepath_pseudos):
    """Test the constructor."""
    for filename in os.listdir(filepath_pseudos('psf')):
        with open(os.path.join(filepath_pseudos('psf'), filename), 'rb') as handle:
            pseudo = PsfData(handle, filename=filename)
            assert isinstance(pseudo, PsfData)
            assert not pseudo.is_stored
            assert pseudo.element == filename.split('.')[0]


@pytest.mark.usefixtures('clear_db')
def test_set_file(filepath_pseudos, get_pseudo_potential_data):
    """Test the `PsfData.set_file` method.

    This method allows to change the file, as long as the node has not been stored yet. We need to verify that all the
    information, such as attributes are commensurate when it is stored.
    """
    pseudo = get_pseudo_potential_data(element='Ar', entry_point='psf')
    assert pseudo.element == 'Ar'

    with open(os.path.join(filepath_pseudos('psf'), 'He.psf'), 'rb') as handle:
        pseudo.set_file(handle)
        assert pseudo.element == 'He'

        pseudo.store()
        assert pseudo.element == 'He'

        with pytest.raises(ModificationNotAllowed):
            pseudo.set_file(handle)
