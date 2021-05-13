# -*- coding: utf-8 -*-
"""Module for data plugin to represent a pseudo potential in Psp8 format."""
import pathlib
import typing

from aiida.common.constants import elements

from .pseudo import PseudoPotentialData

__all__ = ('Psp8Data',)


def parse_element(stream: typing.BinaryIO):
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
