# -*- coding: utf-8 -*-
"""Group to represent a pseudo potential family with pseudos in PSF format."""
from aiida.plugins import DataFactory

from .pseudo import PseudoPotentialFamily

__all__ = ('PsfFamily',)

PsfData = DataFactory('pseudo.psf')  # pylint: disable=invalid-name


class PsfFamily(PseudoPotentialFamily):
    """Group to represent a pseudo potential family with pseudos in PSF format."""

    _pseudo_type = PsfData
