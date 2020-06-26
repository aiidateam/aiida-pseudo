# -*- coding: utf-8 -*-
"""Module for data plugin to represent a pseudo potential in PSF format."""
import re
from typing import BinaryIO

from .pseudo import PseudoPotentialData

__all__ = ('PsfData',)

REGEX_ELEMENT = re.compile(r"""\s*(?P<element>[a-zA-Z]{1}[a-z]?)\s+.*""")


def parse_element(stream: BinaryIO):
    """Parse the content of the PSF file to determine the element.

    :param stream: a filelike object with the binary content of the file.
    :return: the symbol of the element following the IUPAC naming standard.
    """
    lines = stream.read().decode('utf-8')
    line = lines.split('\n')[0]
    match = REGEX_ELEMENT.search(line)

    if match:
        return match.group('element').capitalize()

    raise ValueError('could not parse the element from the PSF content.')


class PsfData(PseudoPotentialData):
    """Data plugin to represent a pseudo potential in PSF format."""

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
