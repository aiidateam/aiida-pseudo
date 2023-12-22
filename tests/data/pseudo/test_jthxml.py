# -*- coding: utf-8 -*-
"""Tests for the :py:`~aiida_pseudo.data.pseudo.jthxml` module."""
import io
import pathlib

import pytest
from aiida.common.exceptions import ModificationNotAllowed
from aiida_pseudo.data.pseudo import JthXmlData


@pytest.fixture
def source(request, filepath_pseudos):
    """Return a pseudopotential, eiter as ``str``, ``Path`` or ``io.BytesIO``."""
    filepath_pseudo = filepath_pseudos(entry_point='jthxml') / 'Ar.jthxml'

    if request.param is str:
        return str(filepath_pseudo)

    if request.param is pathlib.Path:
        return filepath_pseudo

    return io.BytesIO(filepath_pseudo.read_bytes())


@pytest.mark.parametrize('source', (io.BytesIO, str, pathlib.Path), indirect=True)
def test_constructor_source_types(source):
    """Test the constructor accept the various types."""
    pseudo = JthXmlData(source)
    assert isinstance(pseudo, JthXmlData)
    assert not pseudo.is_stored


def test_constructor(filepath_pseudos):
    """Test the constructor."""
    for filepath in filepath_pseudos('jthxml').iterdir():
        with filepath.open('rb') as handle:
            pseudo = JthXmlData(handle, filename=filepath.name)
            assert isinstance(pseudo, JthXmlData)
            assert not pseudo.is_stored
            assert pseudo.element == filepath.name.split('.')[0]


@pytest.mark.usefixtures('clear_db')
def test_set_file(filepath_pseudos, get_pseudo_potential_data):
    """Test the `JthXmlData.set_file` method.

    This method allows to change the file, as long as the node has not been stored yet. We need to verify that all the
    information, such as attributes are commensurate when it is stored.
    """
    pseudo = get_pseudo_potential_data(element='Ar', entry_point='jthxml')
    assert pseudo.element == 'Ar'

    with (filepath_pseudos('jthxml') / 'He.jthxml').open('rb') as handle:
        pseudo.set_file(handle)
        assert pseudo.element == 'He'

        pseudo.store()
        assert pseudo.element == 'He'

        with pytest.raises(ModificationNotAllowed):
            pseudo.set_file(handle)
