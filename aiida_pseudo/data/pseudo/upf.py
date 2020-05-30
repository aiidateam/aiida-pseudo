# -*- coding: utf-8 -*-
"""Module for data plugin to represent a pseudo potential in UPF format."""
import re
from typing import BinaryIO

from .pseudo import PseudoPotentialData

__all__ = ('UpfData',)

REGEX_ELEMENT_V1 = re.compile(r"""(?P<element>[a-zA-Z]{1,2})\s+Element""")
REGEX_ELEMENT_V2 = re.compile(r"""\s*element\s*=\s*['"]\s*(?P<element>[a-zA-Z]{1,2})\s*['"].*""")


def parse_element(stream: BinaryIO):
    """Parse the content of the UPF file to determine the element.

    :param stream: a filelike object with the binary content of the file.
    :return: the symbol of the element following the IUPAC naming standard.
    """
    lines = stream.read().decode('utf-8')
    match = REGEX_ELEMENT_V2.search(lines)

    if match:
        return match.group('element')

    match = REGEX_ELEMENT_V1.search(lines)

    if match:
        return match.group('element')

    raise ValueError('could not parse the element from the UPF content.')


class UpfData(PseudoPotentialData):
    """Data plugin to represent a pseudo potential in UPF format."""

    def set_file(self, stream: BinaryIO, filename: str = None, **kwargs):  # pylint: disable=arguments-differ
        """Set the file content.

        :param stream: a filelike object with the binary content of the file.
        :param filename: optional explicit filename to give to the file stored in the repository.
        :raises ValueError: if the element symbol is invalid.
        """
        stream.seek(0)
        self.element = parse_element(stream)
        stream.seek(0)
        super().set_file(stream, filename, **kwargs)
