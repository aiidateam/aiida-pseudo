# -*- coding: utf-8 -*-
"""Group to represent a pseudo potential family with pseudos in PSML format."""
from aiida.plugins import DataFactory

from .pseudo import PseudoPotentialFamily

__all__ = ('PsmlFamily',)

PsmlData = DataFactory('pseudo.psml')  # pylint: disable=invalid-name


class PsmlFamily(PseudoPotentialFamily):
    """Group to represent a pseudo potential family with pseudos in PSML format."""

    _pseudo_type = PsmlData
