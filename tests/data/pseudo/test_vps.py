# -*- coding: utf-8 -*-
"""Tests for the :py:`~aiida_pseudo.data.pseudo.vps` module."""
import os

import pytest

from aiida.common.exceptions import ModificationNotAllowed
from aiida_pseudo.data.pseudo import VpsData
from aiida_pseudo.data.pseudo.vps import parse_z_valence, parse_xc_type


@pytest.mark.usefixtures('clear_db')
def test_constructor(filepath_pseudos):
    """Test the constructor."""
    for filename in os.listdir(filepath_pseudos('vps')):
        with open(os.path.join(filepath_pseudos('vps'), filename), 'rb') as handle:
            pseudo = VpsData(handle, filename=filename)
            assert isinstance(pseudo, VpsData)
            assert not pseudo.is_stored
            assert pseudo.element == filename.split('.')[0]


@pytest.mark.usefixtures('clear_db')
def test_set_file(filepath_pseudos, get_pseudo_potential_data):
    """Test the `VpsData.set_file` method.

    This method allows to change the file, as long as the node has not been stored yet. We need to verify that all the
    information, such as attributes are commensurate when it is stored.
    """
    pseudo = get_pseudo_potential_data(element='Ar', entry_point='vps')
    assert pseudo.element == 'Ar'

    with open(os.path.join(filepath_pseudos('vps'), 'He.vps'), 'rb') as handle:
        pseudo.set_file(handle)
        assert pseudo.element == 'He'

        pseudo.store()
        assert pseudo.element == 'He'

        with pytest.raises(ModificationNotAllowed):
            pseudo.set_file(handle)


@pytest.mark.parametrize(
    'content', (
        'valence.electron 1.0',
        'valence.electron 1',
        'VALENCE.ELECTRON 1.0',
        'Valence.Electron 1.0'
        'valence.electron 1.0 # Z valence',
    )
)
def test_parse_z_valence(content):
    """Test the ``parse_z_valence`` method."""
    assert parse_z_valence(content)


@pytest.mark.parametrize('content', ('xc.type LDA', 'Xc.Type LDA', 'xc.type GGA', 'xc.type GGA # GGA|LDA'))
def test_parse_xc_type(content):
    """Test the ``parse_xc_type`` method."""
    assert parse_xc_type(content)
