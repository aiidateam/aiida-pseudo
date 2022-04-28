# -*- coding: utf-8 -*-
"""Reusable arguments for CLI commands."""
from aiida.cmdline.params.arguments.overridable import OverridableArgument

from .types import PseudoPotentialFamilyParam

__all__ = ('PSEUDO_POTENTIAL_FAMILY',)

PSEUDO_POTENTIAL_FAMILY = OverridableArgument(
    'family', type=PseudoPotentialFamilyParam(sub_classes=('aiida.groups:pseudo.family',))
)
