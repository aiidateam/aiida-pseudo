# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""Tests for the :py:`~aiida_pseudo.data.pseudo.upf` module."""
import io
import os
import pathlib

import pytest

from aiida.common.exceptions import ModificationNotAllowed
from aiida_pseudo.data.pseudo import UpfData
from aiida_pseudo.data.pseudo.upf import parse_z_valence


@pytest.fixture
def source(request, filepath_pseudos):
    """Return a pseudopotential, eiter as ``str``, ``Path`` or ``io.BytesIO``."""
    filepath_pseudo = pathlib.Path(filepath_pseudos(entry_point='upf')) / 'Ar.upf'

    if request.param is str:
        return str(filepath_pseudo)

    if request.param is pathlib.Path:
        return filepath_pseudo

    return io.BytesIO(filepath_pseudo.read_bytes())


@pytest.mark.parametrize('source', (io.BytesIO, str, pathlib.Path), indirect=True)
def test_constructor_source_types(source):
    """Test the constructor accept the various types."""
    pseudo = UpfData(source)
    assert isinstance(pseudo, UpfData)
    assert not pseudo.is_stored


def test_constructor(filepath_pseudos):
    """Test the constructor."""
    for filename in os.listdir(filepath_pseudos('upf')):
        with open(os.path.join(filepath_pseudos('upf'), filename), 'rb') as handle:
            pseudo = UpfData(handle, filename=filename)
            assert isinstance(pseudo, UpfData)
            assert not pseudo.is_stored
            assert pseudo.element == filename.split('.')[0]


@pytest.mark.usefixtures('clear_db')
def test_set_file(filepath_pseudos, get_pseudo_potential_data):
    """Test the `UpfData.set_file` method.

    This method allows to change the file, as long as the node has not been stored yet. We need to verify that all the
    information, such as attributes are commensurate when it is stored.
    """
    pseudo = get_pseudo_potential_data(element='Ar', entry_point='upf')
    assert pseudo.element == 'Ar'

    with open(os.path.join(filepath_pseudos('upf'), 'He.upf'), 'rb') as handle:
        pseudo.set_file(handle)
        assert pseudo.element == 'He'

        pseudo.store()
        assert pseudo.element == 'He'

        with pytest.raises(ModificationNotAllowed):
            pseudo.set_file(handle)


@pytest.mark.parametrize(
    'content', (
        'z_valence="1"',
        'z_valence="1.0"',
        'z_valence="1.000"',
        'z_valence="1.00E+01"',
        'z_valence="1500."',
        "z_valence='1.0'",
        'z_valence="    1"',
        'z_valence="1    "',
        '1.0     Z valence',
    )
)
def test_parse_z_valence(content):
    """Test the ``parse_z_valence`` method."""
    assert parse_z_valence(content)
