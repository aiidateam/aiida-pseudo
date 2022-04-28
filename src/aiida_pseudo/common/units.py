# -*- coding: utf-8 -*-
"""Module with constants for unit conversions."""
from pint import UnitRegistry

# This unit registry singleton should be used to construct new quantities with a unit and to convert them to other units
U = UnitRegistry()
