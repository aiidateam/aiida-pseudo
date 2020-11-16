# -*- coding: utf-8 -*-
"""Module for data plugin to represent a pseudo potential in UPF format."""
import re
from typing import BinaryIO, Union

from .pseudo import PseudoPotentialData

__all__ = ('UpfData',)

REGEX_ELEMENT_V1 = re.compile(r"""(?P<element>[a-zA-Z]{1,2})\s+Element""")
REGEX_ELEMENT_V2 = re.compile(r"""\s*element\s*=\s*['"]\s*(?P<element>[a-zA-Z]{1,2})\s*['"].*""")

PATTERN_FLOAT = r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?'
REGEX_Z_VALENCE_V1 = re.compile(r"""(?P<z_valence>""" + PATTERN_FLOAT + r""")\s+Z valence""")
REGEX_Z_VALENCE_V2 = re.compile(r"""\s*z_valence\s*=\s*['"]\s*(?P<z_valence>""" + PATTERN_FLOAT + r""")\s*['"].*""")


def parse_element(content: str):
    """Parse the content of the UPF file to determine the element.

    :param stream: a filelike object with the binary content of the file.
    :return: the symbol of the element following the IUPAC naming standard.
    """
    for regex in [REGEX_ELEMENT_V2, REGEX_ELEMENT_V1]:

        match = regex.search(content)

        if match:
            return match.group('element')

    raise ValueError(f'could not parse the element from the UPF content: {content}')


def parse_z_valence(content: str) -> int:
    """Parse the content of the UPF file to determine the Z valence.

    :param stream: a filelike object with the binary content of the file.
    :return: the Z valence.
    """
    for regex in [REGEX_Z_VALENCE_V2, REGEX_Z_VALENCE_V1]:

        match = regex.search(content)

        if match:
            z_valence = match.group('z_valence')

            try:
                z_valence = float(z_valence)
            except ValueError as exception:
                raise ValueError(f'parsed value for the Z valence `{z_valence}` is not a valid number.') from exception

            if int(z_valence) != z_valence:
                raise ValueError(f'parsed value for the Z valence `{z_valence}` is not an integer.')

            return int(z_valence)

    raise ValueError(f'could not parse the Z valence from the UPF content: {content}')


class UpfData(PseudoPotentialData):
    """Data plugin to represent a pseudo potential in UPF format."""

    _key_z_valence = 'z_valence'

    def set_file(self, stream: BinaryIO, filename: str = None, **kwargs):  # pylint: disable=arguments-differ
        """Set the file content.

        :param stream: a filelike object with the binary content of the file.
        :param filename: optional explicit filename to give to the file stored in the repository.
        :raises ValueError: if the element symbol is invalid.
        """
        stream.seek(0)

        content = stream.read().decode('utf-8')
        self.element = parse_element(content)
        self.z_valence = parse_z_valence(content)

        stream.seek(0)
        super().set_file(stream, filename, **kwargs)

    @property
    def z_valence(self) -> Union[int, None]:
        """Return the Z valence.

        :return: the Z valence.
        """
        return self.get_attribute(self._key_z_valence, None)

    @z_valence.setter
    def z_valence(self, value: int):
        """Set the Z valence.

        :param value: the Z valence.
        :raises ValueError: if the value is not a positive integer.
        """
        if not isinstance(value, int) or value < 0:
            raise ValueError(f'`{value}` is not a positive integer')

        self.set_attribute(self._key_z_valence, value)
