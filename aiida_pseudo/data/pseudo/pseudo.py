# -*- coding: utf-8 -*-
"""Base class for data types representing pseudo potentials."""
import typing

from aiida.common.constants import elements
from aiida.common.exceptions import StoringNotAllowed
from aiida.common.files import md5_from_filelike
from aiida.plugins import DataFactory

SingleFileData = DataFactory('singlefile')  # pylint: disable=invalid-name

__all__ = ('PseudoPotentialData',)


class PseudoPotentialData(SingleFileData):
    """Base class for data types representing pseudo potentials."""

    _key_element = 'element'
    _key_md5 = 'md5'

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
