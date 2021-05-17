# -*- coding: utf-8 -*-
"""Module for data plugin to represent a pseudo potential in PSML format."""
import pathlib
import re
import typing

from .pseudo import PseudoPotentialData

__all__ = ('PsmlData',)

REGEX_ELEMENT = re.compile(r"""\s*(?P<element>[a-zA-Z]{1}[a-z]?)\s+.*""")


def parse_element(stream: typing.BinaryIO) -> str:
    """Parse the content of the PSML file to determine the element.

    :param stream: a filelike object with the binary content of the file.
    :return: the symbol of the element following the IUPAC naming standard.
    """
    from xml.dom.minidom import parse

    try:
        xml = parse(stream)
        element = xml.getElementsByTagName('pseudo-atom-spec')[0].attributes['atomic-label'].value
    except (AttributeError, IndexError, KeyError) as exception:
        raise ValueError(f'could not parse the element from the PSML content: {exception}') from exception

    return element.capitalize()


def parse_z_valence(stream: typing.BinaryIO) -> int:
    """Parse the content of the PSML file to determine the Z valence.

    :param stream: a filelike object with the binary content of the file.
    :return: the Z valence.
    """
    from xml.dom.minidom import parse

    try:
        xml = parse(stream)
        z_valence = xml.getElementsByTagName('pseudo-atom-spec')[0].attributes['z-pseudo'].value
    except (AttributeError, IndexError, KeyError) as exception:
        raise ValueError(f'could not parse the Z valence from the PSML content: {exception}') from exception

    try:
        z_valence = float(z_valence)
    except ValueError as exception:
        raise ValueError(f'parsed value for the Z valence `{z_valence}` is not a valid number.') from exception

    if int(z_valence) != z_valence:
        raise ValueError(f'parsed value for the Z valence `{z_valence}` is not an integer.')

    return int(z_valence)


class PsmlData(PseudoPotentialData):
    """Data plugin to represent a pseudo potential in PSML format."""

    _key_z_valence = 'z_valence'

    def set_file(self, source: typing.Union[str, pathlib.Path, typing.BinaryIO], filename: str = None, **kwargs):  # pylint: disable=arguments-differ
        """Set the file content and parse other optional attributes from the content.

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
        :raises ValueError: if the element symbol is invalid.
        """
        source = self.prepare_source(source)
        super().set_file(source, filename, **kwargs)
        source.seek(0)
        self.element = parse_element(source)
        source.seek(0)
        self.z_valence = parse_z_valence(source)

    @property
    def z_valence(self) -> typing.Optional[int]:
        """Return the Z valence.

        :return: the Z valence.
        """
        return self.base.attributes.get(self._key_z_valence, None)

    @z_valence.setter
    def z_valence(self, value: int):
        """Set the Z valence.

        :param value: the Z valence.
        :raises ValueError: if the value is not a positive integer.
        """
        if not isinstance(value, int) or value < 0:
            raise ValueError(f'`{value}` is not a positive integer')

        self.base.attributes.set(self._key_z_valence, value)
