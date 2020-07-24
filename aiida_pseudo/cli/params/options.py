# -*- coding: utf-8 -*-
"""Reusable options for CLI commands."""
import shutil

import click

from aiida.cmdline.params.options import OverridableOption
from .types import PseudoPotentialFamilyTypeParam

__all__ = ('VERSION', 'FUNCTIONAL', 'PROTOCOL', 'TRACEBACK', 'FAMILY_TYPE', 'ARCHIVE_FORMAT')

VERSION = OverridableOption(
    '-v', '--version', type=click.STRING, required=False, help='Select the version of the SSSP configuration.'
)

FUNCTIONAL = OverridableOption(
    '-f', '--functional', type=click.STRING, required=False, help='Select the functional of the SSSP configuration.'
)

PROTOCOL = OverridableOption(
    '-p', '--protocol', type=click.STRING, required=False, help='Select the protocol of the SSSP configuration.'
)

TRACEBACK = OverridableOption(
    '-t', '--traceback', is_flag=True, help='Include the stacktrace if an exception is encountered.'
)

FAMILY_TYPE = OverridableOption(
    '-T',
    '--family-type',
    type=PseudoPotentialFamilyTypeParam(),
    default='pseudo.family',
    show_default=True,
    help='Choose the type of pseudo potential family to create.'
)

ARCHIVE_FORMAT = OverridableOption(
    '-F', '--archive-format', type=click.Choice([fmt[0] for fmt in shutil.get_archive_formats()])
)
