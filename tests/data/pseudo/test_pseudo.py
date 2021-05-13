# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""Tests for the :py:mod:`~aiida_pseudo.data.pseudo.pseudo` module."""
import io
import pathlib

import pytest

from aiida.common.files import md5_from_filelike
from aiida.common.exceptions import ModificationNotAllowed, StoringNotAllowed
from aiida.common.links import LinkType
from aiida.orm import CalcJobNode

from aiida_pseudo.data.pseudo import PseudoPotentialData, UpfData


@pytest.fixture
def source(request, filepath_pseudos):
    """Return a pseudopotential, eiter as ``str``, ``Path`` or ``io.BytesIO``."""
    filepath_pseudo = pathlib.Path(filepath_pseudos()) / 'Ar.upf'

    if request.param is str:
        return str(filepath_pseudo)

    if request.param is pathlib.Path:
        return filepath_pseudo

    return io.BytesIO(filepath_pseudo.read_bytes())


@pytest.mark.parametrize('source', (io.BytesIO, str, pathlib.Path), indirect=True)
def test_constructor_source_types(source):
    """Test the constructor."""
    pseudo = PseudoPotentialData(source)
    assert isinstance(pseudo, PseudoPotentialData)
    assert not pseudo.is_stored


def test_constructor_invalid():
    """Test the constructor for invalid arguments."""
    with pytest.raises(TypeError, match='missing 1 required positional argument'):
        PseudoPotentialData()  # pylint: disable=no-value-for-parameter


@pytest.mark.usefixtures('chtmpdir')
@pytest.mark.parametrize('source_type', ('stream', 'str_absolute', 'str_relative', 'pathlib.Path'))
@pytest.mark.parametrize('implicit', (True, False))
def test_constructor_filename(get_pseudo_potential_data, implicit, source_type):
    """Test the ``filename`` argument of the constructor."""
    pseudo = get_pseudo_potential_data()
    explicit_filename = 'custom.dat'

    # Copy the content of the test pseudo to file in the current working directory
    filepath = pathlib.Path('tempfile.pseudo')

    with open(filepath, mode='wb') as handle:
        handle.write(pseudo.get_object_content(pseudo.filename, mode='rb'))
        handle.flush()

    if source_type == 'stream':
        with open(filepath, 'rb') as handle:
            source = io.BytesIO(handle.read())
    elif source_type == 'str_absolute':
        source = str(filepath.absolute())
    elif source_type == 'str_relative':
        source = str(filepath.name)
    elif source_type == 'pathlib.Path':
        source = filepath

    if implicit:
        node = PseudoPotentialData(source, filename=None)
        # If the source type was a stream, we pass a bytestream which doesn't have a name and so the name will be
        # determined by the baseclass which has some default, but in this case we don't have to check anything.
        if source_type != 'stream':
            assert node.filename == filepath.name
    else:
        node = PseudoPotentialData(source, filename=explicit_filename)
        assert node.filename == explicit_filename


@pytest.mark.parametrize(('value, exception, pattern'), (
    (io.StringIO('content'), TypeError, r'`source` should be a `str` or `pathlib.Path` filepath .*'),
    ('non-existing/path', FileNotFoundError, r'No such file or directory: .*'),
    (pathlib.Path('non-existing/path'), FileNotFoundError, r'No such file or directory: .*'),
))
def test_prepare_source_excepts(value, exception, pattern):
    """Test the ``PseudoPotentialData.prepare_source`` method when it is supposed to except."""
    with pytest.raises(exception, match=pattern):
        PseudoPotentialData.prepare_source(value)


@pytest.mark.parametrize('source', (io.BytesIO, str, pathlib.Path), indirect=True)
def test_prepare_source(source):
    """Test the ``PseudoPotentialData.prepare_source`` method for valid input."""
    assert isinstance(PseudoPotentialData.prepare_source(source), io.BytesIO)

    if isinstance(source, io.BytesIO):
        # If we pass a bytestream, we should get the exact same back
        assert PseudoPotentialData.prepare_source(source) is source


@pytest.mark.usefixtures('clear_db')
def test_store():
    """Test the `PseudoPotentialData.store` method."""
    stream = io.BytesIO(b'pseudo')
    md5_correct = md5_from_filelike(stream)
    md5_incorrect = 'abcdef0123456789'
    stream.seek(0)

    pseudo = PseudoPotentialData(io.BytesIO(b'pseudo'))

    with pytest.raises(StoringNotAllowed, match='no valid element has been defined.'):
        pseudo.store()

    pseudo.element = 'Ar'
    pseudo.set_attribute(PseudoPotentialData._key_md5, md5_incorrect)  # pylint: disable=protected-access

    with pytest.raises(StoringNotAllowed, match=r'md5 does not match that of stored file:'):
        pseudo.store()

    pseudo.md5 = md5_correct
    result = pseudo.store()
    assert result is pseudo
    assert pseudo.is_stored


@pytest.mark.usefixtures('clear_db')
def test_element():
    """Test the `PseudoPotentialData.element` property."""
    element = 'Ar'
    pseudo = PseudoPotentialData(io.BytesIO(b'pseudo'))
    assert pseudo.element is None

    element = 'He'
    pseudo.element = element
    assert pseudo.element == element

    with pytest.raises(ValueError, match=r'.* is not a valid element'):
        pseudo.element = 'Aa'

    pseudo.store()

    with pytest.raises(ModificationNotAllowed, match='the attributes of a stored entity are immutable'):
        pseudo.element = element


@pytest.mark.usefixtures('clear_db')
def test_md5():
    """Test the `PseudoPotentialData.md5` property."""
    stream = io.BytesIO(b'pseudo')
    md5 = md5_from_filelike(stream)
    stream.seek(0)

    pseudo = PseudoPotentialData(stream)
    pseudo.element = 'Ar'
    assert pseudo.md5 == md5

    with pytest.raises(ValueError, match=r'md5 does not match that of stored file.*'):
        pseudo.md5 = 'abcdef0123456789'

    pseudo.store()

    with pytest.raises(ModificationNotAllowed, match='the attributes of a stored entity are immutable'):
        pseudo.md5 = md5


@pytest.mark.usefixtures('clear_db')
def test_store_indirect():
    """Test the `PseudoPotentialData.store` method when called indirectly because its is an input."""
    pseudo = PseudoPotentialData(io.BytesIO(b'pseudo'))
    pseudo.element = 'Ar'

    node = CalcJobNode()
    node.add_incoming(pseudo, link_type=LinkType.INPUT_CALC, link_label='pseudo')
    node.store_all()


@pytest.mark.usefixtures('clear_db')
def test_get_or_create(get_pseudo_potential_data):
    """Test the ``PseudoPotentialData.get_or_create`` classmethod."""
    upf = get_pseudo_potential_data(entry_point='upf')
    stream = io.BytesIO(upf.get_content().encode('utf-8'))

    original = PseudoPotentialData.get_or_create(stream)
    original.element = upf.element
    assert isinstance(original, PseudoPotentialData)
    assert not original.is_stored

    # Need to store it so it can actually be loaded from it by the ``get_or_create`` method
    original.store()

    # Return the stream to initial state and call again, which should return the same node.
    stream.seek(0)
    duplicate = PseudoPotentialData.get_or_create(stream)
    assert isinstance(duplicate, PseudoPotentialData)
    assert duplicate.is_stored
    assert duplicate.uuid == original.uuid

    # If the content is different, we should get a different node.
    stream.seek(0)
    different_content = PseudoPotentialData.get_or_create(io.BytesIO(b'different'))
    different_content.element = upf.element
    assert isinstance(different_content, PseudoPotentialData)
    assert not different_content.is_stored
    assert different_content.uuid != original.uuid

    # If the class is different, even if it is a subclass, we should get a different node even if content is identical
    stream.seek(0)
    different_class = UpfData.get_or_create(stream)
    assert isinstance(different_class, PseudoPotentialData)
    assert not different_class.is_stored
    assert different_class.uuid != original.uuid
