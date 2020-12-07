# -*- coding: utf-8 -*-
"""Base class for data types representing pseudo potentials."""
import typing

from aiida import orm
from aiida import plugins
from aiida.common.constants import elements
from aiida.common.exceptions import StoringNotAllowed
from aiida.common.files import md5_from_filelike

__all__ = ('PseudoPotentialData',)


class PseudoPotentialData(plugins.DataFactory('singlefile')):
    """Base class for data types representing pseudo potentials."""

    _key_element = 'element'
    _key_md5 = 'md5'

    @classmethod
    def get_or_create(cls, stream: typing.BinaryIO, filename: str = None):
        """Get pseudopotenial data node from database with matching md5 checksum or create a new one if not existent.

        :param stream: a filelike object with the binary content of the file.
        :param filename: optional explicit filename to give to the file stored in the repository.
        :return: instance of ``PseudoPotentialData``, stored if taken from database, unstored otherwise.
        """
        query = orm.QueryBuilder()
        query.append(cls, subclassing=False, filters={f'attributes.{cls._key_md5}': md5_from_filelike(stream)})

        existing = query.first()

        if existing:
            pseudo = existing[0]
        else:
            stream.seek(0)
            pseudo = cls(stream, filename)

        return pseudo

    @classmethod
    def get_entry_point_name(cls):
        """Return the entry point name associated with this data class.

        :return: the entry point name.
        """
        from aiida.plugins.entry_point import get_entry_point_from_class
        _, entry_point = get_entry_point_from_class(cls.__module__, cls.__name__)
        return entry_point.name

    @classmethod
    def validate_element(cls, element: str):
        """Validate the given element symbol.

        :param element: the symbol of the element following the IUPAC naming standard.
        :raises ValueError: if the element symbol is invalid.
        """
        if element not in [values['symbol'] for values in elements.values()]:
            raise ValueError(f'`{element}` is not a valid element.')

    def validate_md5(self, md5: str):
        """Validate that the md5 checksum matches that of the currently stored file.

        :param value: the md5 checksum.
        :raises ValueError: if the md5 does not match that of the currently stored file.
        """
        with self.open(mode='rb') as handle:
            md5_file = md5_from_filelike(handle)
            if md5 != md5_file:
                raise ValueError(f'md5 does not match that of stored file: {md5} != {md5_file}')

    def set_file(self, stream: typing.BinaryIO, filename: str = None, **kwargs):
        """Set the file content.

        :param stream: a filelike object with the binary content of the file.
        :param filename: optional explicit filename to give to the file stored in the repository.
        """
        super().set_file(stream, filename, **kwargs)
        stream.seek(0)
        self.md5 = md5_from_filelike(stream)

    def store(self, **kwargs):
        """Store the node verifying first that all required attributes are set.

        :raises :py:exc:`~aiida.common.StoringNotAllowed`: if no valid element has been defined.
        """
        try:
            self.validate_element(self.element)
        except ValueError as exception:
            raise StoringNotAllowed('no valid element has been defined.') from exception

        try:
            self.validate_md5(self.md5)
        except ValueError as exception:
            raise StoringNotAllowed(exception) from exception

        return super().store(**kwargs)

    @property
    def element(self) -> typing.Union[str, None]:
        """Return the element symbol.

        :return: the symbol of the element following the IUPAC naming standard or None if not defined.
        """
        return self.get_attribute(self._key_element, None)

    @element.setter
    def element(self, value: str):
        """Set the element.

        :param value: the symbol of the element following the IUPAC naming standard.
        :raises ValueError: if the element symbol is invalid.
        """
        self.validate_element(value)
        self.set_attribute(self._key_element, value)

    @property
    def md5(self) -> typing.Union[str, None]:
        """Return the md5.

        :return: the md5 of the stored file.
        """
        return self.get_attribute(self._key_md5, None)

    @md5.setter
    def md5(self, value: str):
        """Set the md5.

        :param value: the md5 checksum.
        :raises ValueError: if the md5 does not match that of the currently stored file.
        """
        self.validate_md5(value)
        self.set_attribute(self._key_md5, value)
