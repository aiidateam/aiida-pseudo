"""Tests for the :py:`~aiida_pseudo.data.pseudo.vps` module."""
import io
import pathlib

import pytest
from aiida.common.exceptions import ModificationNotAllowed
from aiida_pseudo.data.pseudo import VpsData
from aiida_pseudo.data.pseudo.vps import parse_xc_type, parse_z_valence


@pytest.fixture
def source(request, filepath_pseudos):
    """Return a pseudopotential, eiter as ``str``, ``Path`` or ``io.BytesIO``."""
    filepath_pseudo = filepath_pseudos(entry_point='vps') / 'Ar.vps'

    if request.param is str:
        return str(filepath_pseudo)

    if request.param is pathlib.Path:
        return filepath_pseudo

    return io.BytesIO(filepath_pseudo.read_bytes())


@pytest.mark.parametrize('source', (io.BytesIO, str, pathlib.Path), indirect=True)
def test_constructor_source_types(source):
    """Test the constructor accept the various types."""
    pseudo = VpsData(source)
    assert isinstance(pseudo, VpsData)
    assert not pseudo.is_stored


def test_constructor(filepath_pseudos):
    """Test the constructor."""
    for filepath in filepath_pseudos('vps').iterdir():
        with filepath.open('rb') as handle:
            pseudo = VpsData(handle, filename=filepath.name)
            assert isinstance(pseudo, VpsData)
            assert not pseudo.is_stored
            assert pseudo.element == filepath.name.split('.')[0]


@pytest.mark.usefixtures('aiida_profile_clean')
def test_set_file(filepath_pseudos, get_pseudo_potential_data):
    """Test the `VpsData.set_file` method.

    This method allows to change the file, as long as the node has not been stored yet. We need to verify that all the
    information, such as attributes are commensurate when it is stored.
    """
    pseudo = get_pseudo_potential_data(element='Ar', entry_point='vps')
    assert pseudo.element == 'Ar'

    with (filepath_pseudos('vps') / 'He.vps').open('rb') as handle:
        pseudo.set_file(handle)
        assert pseudo.element == 'He'

        pseudo.store()
        assert pseudo.element == 'He'

        with pytest.raises(ModificationNotAllowed):
            pseudo.set_file(handle)


@pytest.mark.parametrize(
    'content',
    (
        'valence.electron 1.0',
        'valence.electron 1',
        'VALENCE.ELECTRON 1.0',
        'Valence.Electron 1.0' 'valence.electron 1.0 # Z valence',
    ),
)
def test_parse_z_valence(content):
    """Test the ``parse_z_valence`` method."""
    assert parse_z_valence(content)


@pytest.mark.parametrize('content', ('xc.type LDA', 'Xc.Type LDA', 'xc.type GGA', 'xc.type GGA # GGA|LDA'))
def test_parse_xc_type(content):
    """Test the ``parse_xc_type`` method."""
    assert parse_xc_type(content)
