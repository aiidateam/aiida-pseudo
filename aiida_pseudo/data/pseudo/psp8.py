# -*- coding: utf-8 -*-
"""Module for data plugin to represent a pseudo potential in Psp8 format."""
from typing import BinaryIO
from aiida.common.constants import elements

from .pseudo import PseudoPotentialData

__all__ = ('Psp8Data',)


def parse_element(stream: BinaryIO):
    """Parse the content of the Psp8 file to determine the element.

    :param stream: a filelike object with the binary content of the file.
    :return: the symbol of the element following the IUPAC naming standard.
    """
    lines = stream.read().decode('utf-8')

    # Split the line at each new line character \n
    lines_splt = lines.splitlines()

    # Split the second line on white space
    lines_splt_space = lines_splt[1].split()

    try:
        atomic_number = int(float(lines_splt_space[0]))
    except (IndexError, ValueError) as val_err:
        raise ValueError('failed to parse the atomic number.') from val_err

    try:
        symbol = elements[atomic_number]['symbol']
    except KeyError as key_err:
        raise ValueError('the atomic number {atomic_number} is not supported.') from key_err

    return symbol


class Psp8Data(PseudoPotentialData):
    """Data plugin to represent a pseudo potential in Psp8 (Abinit) format."""

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
