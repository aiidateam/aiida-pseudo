# -*- coding: utf-8 -*-
"""Reusable options for CLI commands."""
import shutil

import click

from aiida.cmdline.params.options import OverridableOption
from .types import PseudoPotentialFamilyTypeParam

__all__ = (
    'VERSION', 'FUNCTIONAL', 'REL', 'PROTOCOL', 'HINT', 'PSEUDO_FORMAT', 'TRACEBACK', 'FAMILY_TYPE', 'ARCHIVE_FORMAT'
)

VERSION = OverridableOption(
    '-v',
    '--version',
    type=click.STRING,
    required=False,
    help='Select the version of the SSSP or PseudoDojo configuration.'
)

FUNCTIONAL = OverridableOption(
    '-x',
    '--functional',
    type=click.STRING,
    required=False,
    help='Select the functional of the SSSP or PseudoDojo configuration.'
)

REL = OverridableOption(
    '-r',
    '--rel',
    type=click.STRING,
    required=False,
    help='Select the type of relativistic effects included in the PseudoDojo configuration.'
)

PROTOCOL = OverridableOption(
    '-p',
    '--protocol',
    type=click.STRING,
    required=False,
    help='Select the protocol of the SSSP or PseudoDojo configuration.'
)

HINT = OverridableOption(
    '-c',
    '--hint',
    type=click.STRING,
    required=False,
    help='Select the stringency of energy cutoff hints of the PseudoDojo configuration.'
)

PSEUDO_FORMAT = OverridableOption(
    '-f',
    '--pseudo-format',
    type=click.STRING,
    required=True,
    help='Select the pseudopotential file format of the PseudoDojo configuration.'
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
