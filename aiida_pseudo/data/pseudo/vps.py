# -*- coding: utf-8 -*-
"""Module for data plugin to represent a pseudo potential in VPS format."""
import re
from typing import BinaryIO, Union

from aiida.common.constants import elements

from .pseudo import PseudoPotentialData

__all__ = ('VpsData',)

PATTERN_FLOAT = r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?'
REGEX_ATOMIC_NUMBER = re.compile(r"""\s*AtomSpecies\s*(?P<atomic_number>[\d]{1,3})\s*""", re.I)
REGEX_Z_VALENCE = re.compile(r"""\s*valence\.electron\s*(?P<z_valence>""" + PATTERN_FLOAT + r""")\s*""", re.I)
REGEX_XC_TYPE = re.compile(r"""\s*xc\.type\s*(?P<xc_type>[A-Z]{3})\s*""", re.I)

VALID_XC_TYPES = ('LDA', 'LSDA-CA', 'LSDA-PW', 'GGA-PBE', 'EXX-TEST')


def parse_element(content: str):
    """Parse the content of the VPS file to determine the element.

    :param content: the decoded content of the file.
    :return: the symbol of the element following the IUPAC naming standard.
    """
    match = REGEX_ATOMIC_NUMBER.search(content)

    if match:
        atomic_number = match.group('atomic_number')

        try:
            atomic_number = int(atomic_number)
        except ValueError as exception:
            raise ValueError(
                f'parsed value for the atomic number `{atomic_number}` is not a valid number.'
            ) from exception

        try:
            element = elements[atomic_number]['symbol']
        except KeyError as exception:
            raise ValueError(
                f'parsed value for the atomic number `{atomic_number}` is not in aiida.common.constants.elements.'
            ) from exception

        return element

    raise ValueError(f'could not parse the element from the VPS content: {content}')


def parse_z_valence(content: str):
    """Parse the content of the VPS file to determine the Z valence.

    :param content: the decoded content of the file.
    :return: the number of valence electrons for which the pseudopotential was generated.
    """
    match = REGEX_Z_VALENCE.search(content)

    if match:
        z_valence = match.group('z_valence')

        try:
            z_valence = float(z_valence)
        except ValueError as exception:
            raise ValueError(f'parsed value for the Z valence `{z_valence}` is not a valid number.') from exception

        if int(z_valence) != z_valence:
            raise ValueError(f'parsed value for the Z valence `{z_valence}` is not an integer')

        return int(z_valence)

    raise ValueError(f'could not parse the Z valence from the VPS content: {content}')


def parse_xc_type(content: str):
    """Parse the content of the VPS file to determine the exchange-correlation functional type.

    :param content: the decoded content of the file.
    :return: the OpenMX-compatible name of the exchange-correlation type.
    """
    match = REGEX_XC_TYPE.search(content)

    if match:
        xc_type = match.group('xc_type')

        if xc_type == 'GGA':
            xc_type = 'GGA-PBE'

        if xc_type not in VALID_XC_TYPES:
            raise ValueError(
                f'parsed value for the exchange-correlation type `{xc_type}` is not a valid OpenMX XcType string.'
            )

        return xc_type

    raise ValueError(f'could not parse the exchange-correlation type from the VPS content: {content}')


class VpsData(PseudoPotentialData):
    """Data plugin to represent a pseudo potential in VPS format."""

    _key_z_valence = 'z_valence'
    _key_xc_type = 'xc_type'

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
        self.xc_type = parse_xc_type(content)

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
        :raises ValueError: if the value is not a positive integer
        """
        if not isinstance(value, int) or value < 0:
            raise ValueError(f'`{value}` is not a positive integer.')

        self.set_attribute(self._key_z_valence, value)

    @property
    def xc_type(self) -> Union[str, None]:
        """Return the exchange-correlation type.

        :return: the exchange-correlation type.
        """
        return self.get_attribute(self._key_xc_type, None)

    @xc_type.setter
    def xc_type(self, value: str):
        """Set the exchange-correlation type.

        :param value: the exchange-correlation type.
        :raises ValueError: if the value is not a valid OpenMX XcType
        """
        if not isinstance(value, str) or value not in VALID_XC_TYPES:
            raise ValueError(f'`{value}` is not a valid OpenMX XcType string.')

        self.set_attribute(self._key_xc_type, value)