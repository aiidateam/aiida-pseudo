# -*- coding: utf-8 -*-
"""Group to represent a pseudo potential family with pseudos in UPF format."""
from aiida.plugins import DataFactory

from ..mixins import RecommendedCutoffMixin
from .pseudo import PseudoPotentialFamily

__all__ = ('UpfFamily',)

UpfData = DataFactory('pseudo.upf')  # pylint: disable=invalid-name


class UpfFamily(RecommendedCutoffMixin, PseudoPotentialFamily):
    """Group to represent a pseudo potential family with pseudos in UPF format."""

    _pseudo_type = UpfData
