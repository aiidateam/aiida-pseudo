# -*- coding: utf-8 -*-
"""Subclass of ``PseudoPotentialFamily`` designed to represent a family with recommended cutoffs."""
from ..mixins import RecommendedCutoffMixin
from .pseudo import PseudoPotentialFamily

__all__ = ('CutoffsPseudoPotentialFamily',)


class CutoffsPseudoPotentialFamily(RecommendedCutoffMixin, PseudoPotentialFamily):
    """Subclass of ``PseudoPotentialFamily`` designed to represent a family with recommended cutoffs.

    This is mostly used for testing the functionality around the ``RecommendedCutoffMixin``.
    """
