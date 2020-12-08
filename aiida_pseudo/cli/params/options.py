# -*- coding: utf-8 -*-
"""Reusable options for CLI commands."""
import shutil

import click

from aiida.cmdline.params.options import OverridableOption
from .types import PseudoPotentialFamilyTypeParam

__all__ = (
    'VERSION', 'FUNCTIONAL', 'RELATIVISTIC', 'PROTOCOL', 'PSEUDO_FORMAT', 'DEFAULT_STRINGENCY', 'TRACEBACK',
    'FAMILY_TYPE', 'ARCHIVE_FORMAT'
)

VERSION = OverridableOption(
    '-v', '--version', type=click.STRING, required=False, help='Select the version of the installed configuration.'
)

FUNCTIONAL = OverridableOption(
    '-x',
    '--functional',
    type=click.STRING,
    required=False,
    help='Select the functional of the installed configuration.'
)

RELATIVISTIC = OverridableOption(
    '-r',
    '--relativistic',
    type=click.STRING,
    required=False,
    help='Select the type of relativistic effects included in the installed configuration.'
)

PROTOCOL = OverridableOption(
    '-p', '--protocol', type=click.STRING, required=False, help='Select the protocol of the installed configuration.'
)

PSEUDO_FORMAT = OverridableOption(
    '-f',
    '--pseudo-format',
    type=click.STRING,
    required=True,
    help='Select the pseudopotential file format of the installed configuration.'
)

DEFAULT_STRINGENCY = OverridableOption(
    '-s',
    '--default-stringency',
    type=click.STRING,
    required=False,
    help='Select the default stringency level for the installed configuration.'
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
