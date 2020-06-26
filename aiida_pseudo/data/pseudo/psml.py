# -*- coding: utf-8 -*-
"""Module for data plugin to represent a pseudo potential in PSML format."""
import re
from typing import BinaryIO

from .pseudo import PseudoPotentialData

__all__ = ('PsmlData',)

REGEX_ELEMENT = re.compile(r"""\s*(?P<element>[a-zA-Z]{1}[a-z]?)\s+.*""")


def parse_element(stream: BinaryIO):
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


class PsmlData(PseudoPotentialData):
    """Data plugin to represent a pseudo potential in PSML format."""

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
