# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""Tests for the `PseudoPotentialFamily` class."""
import distutils.dir_util
import os

import pytest

from aiida.common import exceptions
from aiida.orm import QueryBuilder

from aiida_pseudo.data.pseudo import PseudoPotentialData
from aiida_pseudo.groups.family.pseudo import PseudoPotentialFamily


def test_type_string():
    """Verify the `_type_string` class attribute is correctly set to the corresponding entry point name."""
    assert PseudoPotentialFamily._type_string == 'pseudo.family'  # pylint: disable=protected-access


def test_pseudo_types():
    """Test the `PseudoPotentialFamily.pseudo_types` method."""
    assert PseudoPotentialFamily.pseudo_types == (PseudoPotentialData,)


@pytest.mark.filterwarnings('ignore:no registered entry point for')
@pytest.mark.parametrize('pseudo_types', (None, (), int))
def test_pseudo_types_validation(pseudo_types):
    """Test constructor raises if ``_pseudo_types`` is not a tuple with subclasses of ``PseudoPotentialData``."""

    class CustomFamily(PseudoPotentialFamily):
        """Test subclass that intentionally defines incorrect type for ``_pseudo_types``."""

        _pseudo_types = pseudo_types

    with pytest.raises(RuntimeError, match=r'.* should be a tuple of `PseudoPotentialData` subclasses.'):
        CustomFamily(label='custom')


@pytest.mark.usefixtures('clear_db')
def test_pseudo_type(get_pseudo_potential_data):
    """Test ``PseudoPotentialFamily.pseudo_type`` property."""
    family = PseudoPotentialFamily(label='label').store()
    assert family.pseudo_type is None

    pseudo = get_pseudo_potential_data('Ar').store()
    family.add_nodes((pseudo,))
    assert family.pseudo_type == pseudo.get_entry_point_name()

    family.clear()
    assert family.pseudo_type is None

    family.add_nodes((pseudo,))
    assert family.pseudo_type == pseudo.get_entry_point_name()

    family.remove_nodes(pseudo)
    assert family.pseudo_type is None


@pytest.mark.usefixtures('clear_db')
def test_construct():
    """Test the construction of `PseudoPotentialFamily` works."""
    label = 'label'
    family = PseudoPotentialFamily(label=label)
    assert isinstance(family, PseudoPotentialFamily)
    assert not family.is_stored
    assert family.label == label

    label = 'family'
    description = 'description'
    family = PseudoPotentialFamily(label=label, description=description)
    assert isinstance(family, PseudoPotentialFamily)
    assert not family.is_stored
    assert family.label == label
    assert family.description == description


@pytest.mark.usefixtures('clear_db')
def test_create_from_folder(filepath_pseudos):
    """Test the `PseudoPotentialFamily.create_from_folder` class method."""
    label = 'label'
    family = PseudoPotentialFamily.create_from_folder(filepath_pseudos(), label)
    assert isinstance(family, PseudoPotentialFamily)
    assert family.is_stored
    assert family.label == label
    assert len(family.nodes) == len(os.listdir(filepath_pseudos()))


@pytest.mark.usefixtures('clear_db')
def test_create_from_folder_nested(filepath_pseudos, tmpdir):
    """Test the `PseudoPotentialFamily.create_from_folder` class method when the pseudos are in a subfolder."""
    filepath = str(tmpdir / 'subdirectory')
    distutils.dir_util.copy_tree(filepath_pseudos(), filepath)

    label = 'label'
    family = PseudoPotentialFamily.create_from_folder(str(tmpdir), label)
    assert isinstance(family, PseudoPotentialFamily)
    assert family.is_stored
    assert family.label == label
    assert len(family.nodes) == len(os.listdir(filepath_pseudos()))


@pytest.mark.usefixtures('clear_db')
@pytest.mark.parametrize('deduplicate', (True, False))
def test_create_from_folder_deduplicate(filepath_pseudos, deduplicate):
    """Test the `PseudoPotentialFamily.create_from_folder` class method."""
    from aiida_pseudo.data.pseudo.upf import UpfData
    from aiida_pseudo.groups.family.sssp import SsspFamily

    # We create an existing `PseudoPotentialFamily` as well as a `SsspFamily` to test that the deduplication mechanism
    # will only ever check for pseudo potentials of the exact same type and not allow subclasses
    original = PseudoPotentialFamily.create_from_folder(filepath_pseudos(), 'original_family')
    SsspFamily.create_from_folder(filepath_pseudos(), 'SSSP/1.0/PBE/efficiency', pseudo_type=UpfData)

    family = PseudoPotentialFamily.create_from_folder(filepath_pseudos(), 'duplicate_family', deduplicate=deduplicate)

    assert isinstance(family, PseudoPotentialFamily)
    assert family.is_stored

    pseudo_count = len(os.listdir(filepath_pseudos()))
    original_pseudos = {pseudo.pk for pseudo in original.pseudos.values()}
    family_pseudos = {pseudo.pk for pseudo in family.pseudos.values()}

    if deduplicate:
        assert QueryBuilder().append(PseudoPotentialFamily.pseudo_types, subclassing=False).count() == pseudo_count
        assert not original_pseudos.difference(family_pseudos)
    else:
        assert QueryBuilder().append(PseudoPotentialFamily.pseudo_types, subclassing=False).count() == pseudo_count * 2
        assert not original_pseudos.intersection(family_pseudos)


@pytest.mark.usefixtures('clear_db')
def test_create_from_folder_parse_fail(tmpdir):
    """Test the `PseudoPotentialFamily.create_from_folder` class method for file that fails to parse.

    Since the base pseudo potential class cannot really fail to parse, since there is no parsing, this would be
    difficult to test, however, the constructor parses the filename for the element, and that can fail if the filename
    has the incorrect format.
    """
    with open(os.path.join(str(tmpdir), 'Arr.upf'), 'wb'):
        pass

    with pytest.raises(exceptions.ParsingError, match=r'`.*` constructor did not define the element .*'):
        PseudoPotentialFamily.create_from_folder(str(tmpdir), 'label')


@pytest.mark.usefixtures('clear_db')
def test_create_from_folder_empty(tmpdir):
    """Test the `PseudoPotentialFamily.create_from_folder` class method for empty folder."""
    with pytest.raises(ValueError, match=r'no pseudo potentials were parsed from.*'):
        PseudoPotentialFamily.create_from_folder(str(tmpdir), 'label')


@pytest.mark.usefixtures('clear_db')
def test_create_from_folder_duplicate_element(tmpdir, filepath_pseudos):
    """Test the `PseudoPotentialFamily.create_from_folder` class method for folder containing duplicate element."""
    distutils.dir_util.copy_tree(filepath_pseudos(), str(tmpdir))

    with open(os.path.join(str(tmpdir), 'Ar.UPF'), 'wb'):
        pass

    with pytest.raises(ValueError, match=r'directory `.*` contains pseudo potentials with duplicate elements'):
        PseudoPotentialFamily.create_from_folder(str(tmpdir), 'label')


@pytest.mark.usefixtures('clear_db')
def test_create_from_folder_duplicate(filepath_pseudos):
    """Test that `PseudoPotentialFamily.create_from_folder` raises for duplicate label."""
    label = 'label'
    PseudoPotentialFamily(label=label).store()

    with pytest.raises(ValueError, match=r'the PseudoPotentialFamily `.*` already exists'):
        PseudoPotentialFamily.create_from_folder(filepath_pseudos(), label)


def test_parse_pseudos_from_directory_non_file(tmpdir):
    """Test the `PseudoPotentialFamily.parse_pseudos_from_directory` class method for folder containing a non-file.

    Note that a subdirectory containing the pseudos is fine, but if we find a directory and any other object at the
    base path, it should raise.
    """
    os.makedirs(os.path.join(str(tmpdir), 'directory'))
    with open(os.path.join(str(tmpdir), 'Ar.upf'), 'wb'):
        pass

    with pytest.raises(ValueError, match=r'dirpath `.*` contains at least one entry that is not a file'):
        PseudoPotentialFamily.parse_pseudos_from_directory(str(tmpdir))


def test_parse_pseudos_from_directory_non_file_nested(tmpdir):
    """Test the `PseudoPotentialFamily.parse_pseudos_from_directory` class method for folder containing a non-file.

    Note that a subdirectory containing the pseudos is fine, but if we find a directory and any other object at the
    base path, it should raise.
    """
    os.makedirs(os.path.join(str(tmpdir), 'pseudos', 'directory'))
    with open(os.path.join(str(tmpdir), 'pseudos', 'Ar.upf'), 'wb'):
        pass

    with pytest.raises(ValueError, match=r'dirpath `.*` contains at least one entry that is not a file'):
        PseudoPotentialFamily.parse_pseudos_from_directory(str(tmpdir))


@pytest.mark.filterwarnings('ignore:no registered entry point for `SomeFamily` so its instances will not be storable.')
def test_parse_pseudos_from_directory_incorrect_pseudo_type(tmpdir):
    """Test the `PseudoPotentialFamily.parse_pseudos_from_directory` for invalid ``pseudo_type`` arguments.

    It should be in ``cls._pseudo_types`` and if not explicitly defined, ``cls._pseudo_types`` should only contain a
    single element.
    """
    from aiida_pseudo.data.pseudo import PsfData, PsmlData, UpfData

    class SomeFamily(PseudoPotentialFamily):
        """Dummy pseudo family class that defines two supported pseudopotential types."""

        _pseudo_types = (PsfData, UpfData)

    with pytest.raises(ValueError, match=r'.* supports more than one type, so `pseudo_type` needs to be explicitly .*'):
        SomeFamily.parse_pseudos_from_directory(str(tmpdir))

    with pytest.raises(ValueError, match=r'`.*` is not supported by `.*`'):
        SomeFamily.parse_pseudos_from_directory(str(tmpdir), pseudo_type=PsmlData)


@pytest.mark.usefixtures('clear_db')
def test_add_nodes(get_pseudo_family, get_pseudo_potential_data):
    """Test that `PseudoPotentialFamily.add_nodes` method."""
    family = get_pseudo_family(elements=('Rn',))
    assert family.count() == 1

    pseudos = get_pseudo_potential_data('Ar').store()
    family.add_nodes(pseudos)
    assert family.count() == 2

    pseudos = (get_pseudo_potential_data('Ne').store(),)
    family.add_nodes(pseudos)
    assert family.count() == 3

    pseudos = (get_pseudo_potential_data('He').store(), get_pseudo_potential_data('Kr').store())
    family.add_nodes(pseudos)
    assert family.count() == 5

    # Test for an unstored family
    family = PseudoPotentialFamily(label='label')
    with pytest.raises(exceptions.ModificationNotAllowed):
        family.add_nodes(pseudos)


@pytest.fixture
def nodes_unstored(get_pseudo_potential_data, request):
    """Dynamic fixture returning instances of `PseudoPotentialData` either isolated or as a list."""
    if request.param == 'single':
        return get_pseudo_potential_data()

    if request.param == 'tuple':
        return (get_pseudo_potential_data(),)

    return [get_pseudo_potential_data(), get_pseudo_potential_data('Ne')]


@pytest.mark.usefixtures('clear_db')
@pytest.mark.parametrize('nodes_unstored', ['single', 'tuple', 'list'], indirect=True)
def test_add_nodes_unstored(get_pseudo_family, nodes_unstored):
    """Test that `PseudoPotentialFamily.add_nodes` fails if one or more nodes are unstored."""
    family = get_pseudo_family(elements=('He',))
    count = family.count()

    with pytest.raises(ValueError, match='At least one of the provided nodes is unstored, stopping...'):
        family.add_nodes(nodes_unstored)

    assert family.count() == count


@pytest.fixture
def nodes_incorrect_type(get_pseudo_potential_data, request):
    """Dynamic fixture returning instances of `UpfData` either isolated or as a list."""
    from aiida.orm import Data

    if request.param == 'single':
        return Data().store()

    if request.param == 'tuple':
        return (Data().store(),)

    return [get_pseudo_potential_data().store(), Data().store()]


@pytest.mark.usefixtures('clear_db')
@pytest.mark.parametrize('nodes_incorrect_type', ['single', 'tuple', 'list'], indirect=True)
def test_add_nodes_incorrect_type(get_pseudo_family, nodes_incorrect_type):
    """Test that `PseudoPotentialFamily.add_nodes` fails if one or more nodes has the incorrect type.

    Even though `UpfData` is a subclass of `PseudoPotentialData` it should still be refused because `add_nodes` checks
    for exact equality of the expected type and does not accept subclasses.
    """
    family = get_pseudo_family()
    count = family.count()

    with pytest.raises(TypeError, match=r'only nodes of types `.*` can be added'):
        family.add_nodes(nodes_incorrect_type)

    assert family.count() == count


@pytest.mark.usefixtures('clear_db')
def test_add_nodes_duplicate_element(get_pseudo_family, get_pseudo_potential_data):
    """Test that `PseudoPotentialFamily.add_nodes` fails if a pseudo is added whose element already exists."""
    family = get_pseudo_family(elements=('Ar',))
    pseudo = get_pseudo_potential_data('Ar').store()

    with pytest.raises(ValueError, match='element `Ar` already present in this family'):
        family.add_nodes(pseudo)


@pytest.mark.usefixtures('clear_db')
def test_remove_nodes(get_pseudo_family):
    """Test the ``PseudoPotentialFamily.remove_nodes`` method."""
    elements = ('Ar', 'He', 'Kr')
    family = get_pseudo_family(elements=elements)
    pseudos = family.get_pseudos(elements=elements)

    # Removing a single node
    pseudo = pseudos.pop('Ar')
    family.remove_nodes(pseudo)
    assert family.pseudos == pseudos

    # Removing multiple nodes
    family.remove_nodes(list(pseudos.values()))
    assert family.pseudos == {}


@pytest.mark.usefixtures('clear_db')
def test_remove_nodes_not_existing(get_pseudo_family, get_pseudo_potential_data):
    """Test the ``PseudoPotentialFamily.remove_nodes`` method works even when passing a non-existing pseudo.

    The implementation of the ``remove_nodes`` method of the ``Group`` base class does not raise when passing a node
    that is not contained within the group but will silently ignore it. Make sure that the corresponding element is not
    accidentally still removed by the ``PseudoPotentialFamily.remove_nodes`` implementation.
    """
    element = 'Ar'
    family = get_pseudo_family(elements=(element,))
    pseudo = get_pseudo_potential_data(element).store()

    # The node ``pseudo`` is not actually contained within the family and so no pseudopotentials should be removed
    family.remove_nodes(pseudo)
    assert tuple(family.pseudos.keys()) == ('Ar',)


@pytest.mark.usefixtures('clear_db')
def test_clear(get_pseudo_family):
    """Test the ``PseudoPotentialFamily.clear`` method."""
    family = get_pseudo_family(elements=('Ar', 'He', 'Kr'))
    assert family.pseudos is not None

    family.clear()
    assert family.pseudos == {}
    assert family.count() == 0


@pytest.mark.usefixtures('clear_db')
def test_pseudos(get_pseudo_potential_data):
    """Test the `PseudoPotentialFamily.pseudos` property."""
    pseudos = {
        'Ar': get_pseudo_potential_data('Ar').store(),
        'He': get_pseudo_potential_data('He').store(),
    }
    family = PseudoPotentialFamily(label='label').store()
    family.add_nodes(list(pseudos.values()))
    assert family.pseudos == pseudos


@pytest.mark.usefixtures('clear_db')
def test_pseudos_mutate(get_pseudo_family, get_pseudo_potential_data):
    """Test that `PseudoPotentialFamily.pseudos` property does not act as a setter."""
    family = get_pseudo_family()

    with pytest.raises(AttributeError):
        family.pseudos = {'He': get_pseudo_potential_data('He')}


@pytest.mark.usefixtures('clear_db')
def test_elements(get_pseudo_family):
    """Test the `PseudoPotentialFamily.elements` property."""
    elements = ['Ar', 'He']
    family = get_pseudo_family(elements=elements)
    assert sorted(family.elements) == elements

    family = PseudoPotentialFamily(label='empty').store()
    assert family.elements == []


@pytest.mark.usefixtures('clear_db')
def test_get_pseudo(get_pseudo_family):
    """Test the `PseudoPotentialFamily.get_pseudo` method."""
    element = 'Ar'
    family = get_pseudo_family(elements=(element,))

    assert family.get_pseudo(element) == family.pseudos[element]

    with pytest.raises(ValueError, match=r'family `.*` does not contain pseudo for element `.*`'):
        family.get_pseudo('He')


@pytest.mark.usefixtures('clear_db')
def test_get_pseudos_raise(get_pseudo_family, generate_structure):
    """Test the `PseudoPotentialFamily.get_pseudos` method when it is supposed to raise."""
    elements = ('Ar', 'He', 'Ne')
    structure = generate_structure(elements)
    family = get_pseudo_family(elements=elements[:2])  # Create family with only subset of the elements

    with pytest.raises(ValueError, match='have to specify one of the keyword arguments `elements` and `structure`.'):
        family.get_pseudos()

    with pytest.raises(ValueError, match='cannot specify both keyword arguments `elements` and `structure`.'):
        family.get_pseudos(elements=elements, structure=structure)

    with pytest.raises(ValueError, match='elements should be a list or tuple of symbols.'):
        family.get_pseudos(elements={'He', 'Ar'})

    with pytest.raises(ValueError, match='structure should be a `StructureData` instance.'):
        family.get_pseudos(structure={'He', 'Ar'})

    with pytest.raises(ValueError, match=r'family `.*` does not contain pseudo for element `.*`'):
        family.get_pseudos(elements=elements)

    with pytest.raises(ValueError, match=r'family `.*` does not contain pseudo for element `.*`'):
        family.get_pseudos(structure=structure)


@pytest.mark.usefixtures('clear_db')
def test_get_pseudos_list(get_pseudo_family):
    """Test the `PseudoPotentialFamily.get_pseudos` method when passing a list of elements."""
    elements = ('Ar', 'He', 'Ne')
    family = get_pseudo_family(elements=elements)

    pseudos = family.get_pseudos(elements=elements)
    assert isinstance(pseudos, dict)
    for element in elements:
        assert isinstance(pseudos[element], PseudoPotentialData)


@pytest.mark.usefixtures('clear_db')
def test_get_pseudos_structure(get_pseudo_family, generate_structure):
    """Test the `PseudoPotentialFamily.get_pseudos` method when passing a ``StructureData`` instance."""
    elements = ('Ar', 'He', 'Ne')
    structure = generate_structure(elements)
    family = get_pseudo_family(elements=elements)

    pseudos = family.get_pseudos(structure=structure)
    assert isinstance(pseudos, dict)
    for element in elements:
        assert isinstance(pseudos[element], PseudoPotentialData)


@pytest.mark.usefixtures('clear_db')
def test_get_pseudos_structure_kinds(get_pseudo_family, generate_structure):
    """Test the `PseudoPotentialFamily.get_pseudos` for ``StructureData`` with kind names including digits."""
    elements = ('Ar1', 'Ar2')
    structure = generate_structure(elements)
    family = get_pseudo_family(elements=elements)

    pseudos = family.get_pseudos(structure=structure)
    assert isinstance(pseudos, dict)
    for element in elements:
        assert isinstance(pseudos[element], PseudoPotentialData)
