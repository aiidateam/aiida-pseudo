# -*- coding: utf-8 -*-
"""Tests for the :py:mod:`~aiida_pseudo.data.pseudo.pseudo` module."""
import io

import pytest

from aiida.common.files import md5_from_filelike
from aiida.common.exceptions import ModificationNotAllowed, StoringNotAllowed
from aiida.common.links import LinkType
from aiida.orm import CalcJobNode

from aiida_pseudo.data.pseudo import PseudoPotentialData, UpfData


@pytest.mark.usefixtures('clear_db')
def test_constructor():
    """Test the constructor."""
    stream = io.BytesIO(b'pseudo')

    pseudo = PseudoPotentialData(stream)
    assert isinstance(pseudo, PseudoPotentialData)
    assert not pseudo.is_stored


@pytest.mark.usefixtures('clear_db')
def test_constructor_invalid():
    """Test the constructor for invalid arguments."""
    with pytest.raises(TypeError, match='missing 1 required positional argument'):
        PseudoPotentialData()  # pylint: disable=no-value-for-parameter


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
