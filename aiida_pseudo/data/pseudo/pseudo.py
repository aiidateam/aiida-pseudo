# -*- coding: utf-8 -*-
"""Base class for data types representing pseudo potentials."""
import io
import pathlib
import typing

from aiida import orm, plugins
from aiida.common.constants import elements
from aiida.common.exceptions import StoringNotAllowed
from aiida.common.files import md5_from_filelike

__all__ = ('PseudoPotentialData',)


class PseudoPotentialData(plugins.DataFactory('core.singlefile')):
    """Base class for data types representing pseudo potentials."""

    _key_element = 'element'
    _key_md5 = 'md5'

    @classmethod
    def get_or_create(cls, source: typing.Union[str, pathlib.Path, typing.BinaryIO], filename: str = None):
        """Get pseudopotenial data node from database with matching md5 checksum or create a new one if not existent.

        :param source: the source pseudopotential content, either a binary stream, or a ``str`` or ``Path`` to the path
            of the file on disk, which can be relative or absolute.
        :param filename: optional explicit filename to give to the file stored in the repository.
        :return: instance of ``PseudoPotentialData``, stored if taken from database, unstored otherwise.
        :raises TypeError: if the source is not a ``str``, ``pathlib.Path`` instance or binary stream.
        :raises FileNotFoundError: if the source is a filepath but does not exist.
        """
        source = cls.prepare_source(source)

        query = orm.QueryBuilder()
        query.append(cls, subclassing=False, filters={f'attributes.{cls._key_md5}': md5_from_filelike(source)})

        pseudo = query.first(flat=True)

        if not pseudo:
            source.seek(0)
            pseudo = cls(source, filename)

        return pseudo

    @classmethod
    def get_entry_point_name(cls):
        """Return the entry point name associated with this data class.

        :return: the entry point name.
        """
        from aiida.plugins.entry_point import get_entry_point_from_class
        _, entry_point = get_entry_point_from_class(cls.__module__, cls.__name__)
        return entry_point.name

    @staticmethod
    def is_readable_byte_stream(stream) -> bool:
        """Return whether an object appears to be a readable filelike object in binary mode or stream of bytes.

        :param stream: the object to analyse.
        :returns: True if ``stream`` appears to be a readable filelike object in binary mode, False otherwise.
        """
        return (
            isinstance(stream, io.BytesIO) or
            (hasattr(stream, 'read') and hasattr(stream, 'mode') and 'b' in stream.mode)
        )

    @classmethod
    def prepare_source(cls, source: typing.Union[str, pathlib.Path, typing.BinaryIO]) -> typing.BinaryIO:
        """Validate the ``source`` representing a file on disk or a byte stream.

        .. note:: if the ``source`` is a valid file on disk, its content is read and returned as a stream of bytes.

        :raises TypeError: if the source is not a ``str``, ``pathlib.Path`` instance or binary stream.
        :raises FileNotFoundError: if the source is a filepath but does not exist.
        """
        if not isinstance(source, (str, pathlib.Path)) and not cls.is_readable_byte_stream(source):
            raise TypeError(
                f'`source` should be a `str` or `pathlib.Path` filepath on disk or a stream of bytes, got: {source}'
            )

        if isinstance(source, (str, pathlib.Path)):
            filename = pathlib.Path(source).name
            with open(source, 'rb') as handle:
                source = io.BytesIO(handle.read())
                source.name = filename

        return source

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

    def set_file(self, source: typing.Union[str, pathlib.Path, typing.BinaryIO], filename: str = None, **kwargs):
        """Set the file content.

        .. note:: this method will first analyse the type of the ``source`` and if it is a filepath will convert it
            to a binary stream of the content located at that filepath, which is then passed on to the superclass. This
            needs to be done first, because it will properly set the file and filename attributes that are expected by
            other methods. Straight after the superclass call, the source seeker needs to be reset to zero if it needs
            to be read again, because the superclass most likely will have read the stream to the end. Finally it is
            important that the ``prepare_source`` is called here before the superclass invocation, because this way the
            conversion from filepath to byte stream will be performed only once. Otherwise, each subclass would perform
            the conversion over and over again.

        :param source: the source pseudopotential content, either a binary stream, or a ``str`` or ``Path`` to the path
            of the file on disk, which can be relative or absolute.
        :param filename: optional explicit filename to give to the file stored in the repository.
        :raises TypeError: if the source is not a ``str``, ``pathlib.Path`` instance or binary stream.
        :raises FileNotFoundError: if the source is a filepath but does not exist.
        """
        source = self.prepare_source(source)
        super().set_file(source, filename, **kwargs)
        source.seek(0)
        self.md5 = md5_from_filelike(source)

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
    def element(self) -> typing.Optional[int]:
        """Return the element symbol.

        :return: the symbol of the element following the IUPAC naming standard or None if not defined.
        """
        return self.base.attributes.get(self._key_element, None)

    @element.setter
    def element(self, value: str):
        """Set the element.

        :param value: the symbol of the element following the IUPAC naming standard.
        :raises ValueError: if the element symbol is invalid.
        """
        self.validate_element(value)
        self.base.attributes.set(self._key_element, value)

    @property
    def md5(self) -> typing.Optional[int]:
        """Return the md5.

        :return: the md5 of the stored file.
        """
        return self.base.attributes.get(self._key_md5, None)

    @md5.setter
    def md5(self, value: str):
        """Set the md5.

        :param value: the md5 checksum.
        :raises ValueError: if the md5 does not match that of the currently stored file.
        """
        self.validate_md5(value)
        self.base.attributes.set(self._key_md5, value)
