# -*- coding: utf-8 -*-
"""Subclass of ``Group`` that serves as a base class for representing pseudo potential families."""
import re
from typing import List, Mapping, Tuple, Union

from aiida.common import exceptions
from aiida.common.lang import classproperty, type_check
from aiida.orm import Group, QueryBuilder
from aiida.plugins import DataFactory

from aiida_pseudo.data.pseudo import PseudoPotentialData

__all__ = ('PseudoPotentialFamily',)

StructureData = DataFactory('core.structure')


class PseudoPotentialFamily(Group):
    """Group to represent a pseudo potential family.

    This is a base class that provides most of the functionality but does not actually define what type of pseudo
    potentials can be contained. If ``_pseudo_types`` is not defined, any pseudo potential type is accepted in this
    family, as long as it is a subclass of ``PseudoPotentialData``. Subclasses can limit which pseudo types can be
    hosted by setting ``_pseudo_types`` to a tuple of ``PseudoPotentialData`` subclasses.
    """

    _key_pseudo_type = '_pseudo_type'
    _pseudo_types = (PseudoPotentialData,)
    _pseudos = None

    def __repr__(self):
        """Represent the instance for debugging purposes."""
        return f'{self.__class__.__name__}<{self.pk or self.uuid}>'

    def __str__(self):
        """Represent the instance for human-readable purposes."""
        return f'{self.__class__.__name__}<{self.label}>'

    def __init__(self, *args, **kwargs):
        """Validate that the ``_pseudo_types`` class attribute is a tuple of ``PseudoPotentialData`` subclasses."""
        if not self._pseudo_types or not isinstance(self._pseudo_types, tuple) or any(
            not issubclass(pseudo_type, PseudoPotentialData) for pseudo_type in self._pseudo_types
        ):
            raise RuntimeError('`_pseudo_types` should be a tuple of `PseudoPotentialData` subclasses.')

        super().__init__(*args, **kwargs)

    @classproperty
    def pseudo_types(cls):  # pylint: disable=no-self-argument
        """Return the pseudo potential types that this family accepts.

        :return: the tuple of subclasses of ``PseudoPotentialData`` that this family can host nodes of. If it returns
            ``None``, that means all subclasses are supported.
        """
        return cls._pseudo_types

    @classmethod
    def _validate_pseudo_type(cls, pseudo_type):
        """Validate the ``pseudo_type`` passed to ``parse_pseudos_from_directory``.

        :return: the pseudo type to be used.
        """
        if pseudo_type is None and len(cls._pseudo_types) > 1:
            raise ValueError(f'`{cls}` supports more than one type, so `pseudo_type` needs to be explicitly passed.')

        pseudo_type = pseudo_type or cls._pseudo_types[0]

        if all(not issubclass(pseudo_type, supported_type) for supported_type in cls._pseudo_types):
            raise ValueError(f'`{pseudo_type}` is not supported by `{cls}`.')

        return pseudo_type

    @classmethod
    def _validate_dirpath(cls, dirpath):
        """Validate the ``dirpath`` passed to ``parse_pseudos_from_directory``.

        :return: the directory path to be used.
        """
        if not dirpath.is_dir():
            raise ValueError(f'`{dirpath}` is not a directory')

        dirpath_contents = list(dirpath.iterdir())

        if len(dirpath_contents) == 1 and (dirpath / dirpath_contents[0]).is_dir():
            dirpath = dirpath_contents[0]

        return dirpath

    @classmethod
    def parse_pseudos_from_directory(cls, dirpath, pseudo_type=None, deduplicate=True):
        """Parse the pseudo potential files in the given directory into a list of data nodes.

        .. note:: The directory pointed to by `dirpath` should only contain pseudo potential files. Optionally, it can
            contain just a single directory, that contains all the pseudo potential files. If any other files are stored
            in the basepath or the subdirectory, that cannot be successfully parsed as pseudo potential files the method
            will raise a ``ValueError``.

        :param dirpath: absolute path to a directory containing pseudo potentials.
        :param pseudo_type: subclass of ``PseudoPotentialData`` to be used for the parsed pseudos. If not specified and
            the family only defines a single supported pseudo type in ``_pseudo_types`` then that will be used otherwise
            a ``ValueError`` is raised.
        :param deduplicate: if True, will scan database for existing pseudo potentials of same type and with the same
            md5 checksum, and use that instead of the parsed one.
        :return: list of data nodes
        :raises ValueError: if ``dirpath`` is not a directory or contains anything other than files.
        :raises ValueError: if ``dirpath`` contains multiple pseudo potentials for the same element.
        :raises ValueError: if ``pseudo_type`` is explicitly specified and is not supported by this family class.
        :raises ValueError: if ``pseudo_type`` is not specified and the class supports more than one pseudo type.
        :raises ParsingError: if the constructor of the pseudo type fails for one of the files in the ``dirpath``.
        """
        from aiida.common.exceptions import ParsingError

        pseudos = []
        dirpath = cls._validate_dirpath(dirpath)
        pseudo_type = cls._validate_pseudo_type(pseudo_type)

        for filepath in dirpath.iterdir():

            filename = filepath.name

            if not filepath.is_file():
                raise ValueError(f'dirpath `{dirpath}` contains at least one entry that is not a file: {filepath}')

            with open(filepath, 'rb') as handle:
                try:
                    if deduplicate:
                        pseudo = pseudo_type.get_or_create(handle, filename=filename)
                    else:
                        pseudo = pseudo_type(handle, filename=filename)
                except ParsingError as exception:
                    raise ParsingError(f'failed to parse `{filepath}`: {exception}') from exception

            if pseudo.element is None:
                match = re.search(r'^([A-Za-z]{1,2})\.\w+', filename)
                if match is None:
                    raise ParsingError(
                        f'`{pseudo.__class__}` constructor did not define the element and could not parse a valid '
                        'element symbol from the filename `{filename}` either. It should have the format '
                        '`ELEMENT.EXTENSION`'
                    )
                pseudo.element = match.group(1)
            pseudos.append(pseudo)

        if not pseudos:
            raise ValueError(f'no pseudo potentials were parsed from `{dirpath}`')

        elements = set(pseudo.element for pseudo in pseudos)

        if len(pseudos) != len(elements):
            raise ValueError(f'directory `{dirpath}` contains pseudo potentials with duplicate elements')

        return pseudos

    @classmethod
    def create_from_folder(cls, dirpath, label, *, description='', pseudo_type=None, deduplicate=True):
        """Create a new ``PseudoPotentialFamily`` from the pseudo potentials contained in a directory.

        :param dirpath: absolute path to the folder containing the UPF files.
        :param label: label to give to the ``PseudoPotentialFamily``, should not already exist.
        :param description: description to give to the family.
        :param pseudo_type: subclass of ``PseudoPotentialData`` to be used for the parsed pseudos. If not specified and
            the family only defines a single supported pseudo type in ``_pseudo_types`` then that will be used otherwise
            a ``ValueError`` is raised.
        :param deduplicate: if True, will scan database for existing pseudo potentials of same type and with the same
            md5 checksum, and use that instead of the parsed one.
        :raises ValueError: if a ``PseudoPotentialFamily`` already exists with the given name.
        :raises ValueError: if ``dirpath`` is not a directory or contains anything other than files.
        :raises ValueError: if ``dirpath`` contains multiple pseudo potentials for the same element.
        :raises ValueError: if ``pseudo_type`` is explicitly specified and is not supported by this family class.
        :raises ValueError: if ``pseudo_type`` is not specified and the class supports more than one pseudo type.
        :raises ParsingError: if the constructor of the pseudo type fails for one of the files in the ``dirpath``.
        """
        type_check(description, str, allow_none=True)

        if cls.collection.count(filters={'label': label}):
            raise ValueError(f'the {cls.__name__} `{label}` already exists')

        family = cls(label=label, description=description)
        pseudos = cls.parse_pseudos_from_directory(dirpath, pseudo_type, deduplicate=deduplicate)

        # Only store the ``Group`` and the pseudo nodes now, such that we don't have to worry about the clean up in the
        # case that an exception is raised during creating them.
        family.store()
        family.add_nodes([pseudo.store() for pseudo in pseudos])

        return family

    @property
    def pseudo_type(self):
        """Return the type of the pseudopotentials that are hosted by this family.

        :return: the pseudopotential type or ``None`` if none has been set yet.
        """
        return self.base.extras.get(self._key_pseudo_type, None)

    def update_pseudo_type(self):
        """Update the pseudo type, stored as an extra, based on the current nodes in the family."""
        pseudo_types = {pseudo.__class__ for pseudo in self.pseudos.values()}

        if pseudo_types:
            assert len(pseudo_types) == 1, 'Family contains pseudopotential data nodes of various types.'
            entry_point_name = tuple(pseudo_types)[0].get_entry_point_name()
        else:
            entry_point_name = None

        self.base.extras.set(self._key_pseudo_type, entry_point_name)

    def add_nodes(self, nodes):
        """Add a node or a set of nodes to the family.

        .. note: Each family instance can only contain a single pseudo potential for each element.

        :param nodes: a single or list of ``Node`` instances of type that is in ``PseudoPotentialFamily._pseudo_types``.
        :raises ModificationNotAllowed: if the family is not stored.
        :raises TypeError: if nodes are not an instance or list of instance of any of the classes listed by
            ``PseudoPotentialFamily._pseudo_types``.
        :raises ValueError: if any of the nodes are not stored or their elements already exist in this family.
        """
        if not self.is_stored:
            raise exceptions.ModificationNotAllowed('cannot add nodes to an unstored group')

        if not isinstance(nodes, (list, tuple)):
            nodes = [nodes]

        if any(not isinstance(node, self._pseudo_types) for node in nodes):
            raise TypeError(f'only nodes of types `{self._pseudo_types}` can be added: {nodes}')

        pseudos = {}

        # Check for duplicates before adding any pseudo to the internal cache
        for pseudo in nodes:
            if pseudo.element in self.elements:
                raise ValueError(f'element `{pseudo.element}` already present in this family')
            pseudos[pseudo.element] = pseudo

        self.pseudos.update(pseudos)
        self.update_pseudo_type()

        super().add_nodes(nodes)

    def remove_nodes(self, nodes):
        """Remove a pseudopotential or a set of pseudopotentials from the family.

        :param nodes: a single or list of ``PseudoPotentialData`` instances or subclasses thereof.
        """
        super().remove_nodes(nodes)

        if not isinstance(nodes, (list, tuple)):
            nodes = (nodes,)

        removed = [node.pk for node in nodes]
        self._pseudos = {pseudo.element: pseudo for pseudo in self.pseudos.values() if pseudo.pk not in removed}
        self.update_pseudo_type()

    def clear(self):
        """Remove all the pseudopotentials from this family."""
        super().clear()
        self._pseudos = None
        self.update_pseudo_type()

    @property
    def pseudos(self):
        """Return the dictionary of pseudo potentials of this family indexed on the element symbol.

        :return: dictionary of element symbol mapping pseudo potentials
        """
        if self._pseudos is None:
            self._pseudos = {pseudo.element: pseudo for pseudo in self.nodes}

        return self._pseudos

    @property
    def elements(self):
        """Return the list of elements for which this family defines a pseudo potential.

        :return: list of element symbols
        """
        return list(self.pseudos.keys())

    def get_pseudo(self, element):
        """Return the pseudo potential for the given element.

        :param element: the element for which to return the corresponding pseudo potential.
        :return: pseudo potential instance if it exists
        :raises ValueError: if the family does not contain a pseudo potential for the given element
        """
        try:
            pseudo = self.pseudos[element]
        except KeyError:
            builder = QueryBuilder()
            builder.append(self.__class__, filters={'id': self.pk}, tag='group')
            builder.append(self._pseudo_types, filters={'attributes.element': element}, with_group='group')

            try:
                pseudo = builder.one()[0]
            except exceptions.MultipleObjectsError as exception:
                raise RuntimeError(f'family `{self.label}` contains multiple pseudos for `{element}`') from exception
            except exceptions.NotExistent as exception:
                raise ValueError(
                    f'family `{self.label}` does not contain pseudo for element `{element}`'
                ) from exception
            else:
                self.pseudos[element] = pseudo

        return pseudo

    def get_pseudos(
        self,
        *,
        elements: Union[List[str], Tuple[str]] = None,
        structure: StructureData = None,
    ) -> Mapping[str, StructureData]:
        """Return the mapping of kind names on pseudo potential data nodes for the given list of elements or structure.

        :param elements: list of element symbols.
        :param structure: the ``StructureData`` node.
        :return: dictionary mapping the kind names of a structure on the corresponding pseudo potential data nodes.
        :raises ValueError: if the family does not contain a pseudo for any of the elements of the given structure.
        """
        if elements is not None and structure is not None:
            raise ValueError('cannot specify both keyword arguments `elements` and `structure`.')

        if elements is None and structure is None:
            raise ValueError('have to specify one of the keyword arguments `elements` and `structure`.')

        if elements is not None and not isinstance(elements, (list, tuple)) and not isinstance(elements, StructureData):
            raise ValueError('elements should be a list or tuple of symbols.')

        if structure is not None and not isinstance(structure, StructureData):
            raise ValueError('structure should be a `StructureData` instance.')

        if structure is not None:
            return {kind.name: self.get_pseudo(kind.symbol) for kind in structure.kinds}

        return {element: self.get_pseudo(element) for element in elements}
