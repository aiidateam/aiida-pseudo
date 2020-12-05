# -*- coding: utf-8 -*-
# pylint: disable=undefined-variable
"""Module with group plugins to represent pseudo potential families."""
from .pseudo import *
from .sssp import *

__all__ = (pseudo.__all__ + sssp.__all__)
