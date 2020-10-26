# -*- coding: utf-8 -*-
"""Group to represent a pseudo potential family with pseudos in Psp8 format."""
from aiida.plugins import DataFactory

from .pseudo import PseudoPotentialFamily

__all__ = ('Psp8Family',)

Psp8Data = DataFactory('pseudo.psp8')  # pylint: disable=invalid-name


class Psp8Family(PseudoPotentialFamily):
    """Group to represent a pseudo potential family with pseudos in Psp8 format."""

    _pseudo_type = Psp8Data
