# -*- coding: utf-8 -*-
"""Reusable options for CLI commands."""
import shutil

import click

from aiida.cmdline.params.options import OverridableOption
from .types import PseudoPotentialFamilyTypeParam, PseudoPotentialTypeParam, UnitParamType

__all__ = (
    'VERSION', 'FUNCTIONAL', 'RELATIVISTIC', 'PROTOCOL', 'PSEUDO_FORMAT', 'STRINGENCY', 'DEFAULT_STRINGENCY',
    'TRACEBACK', 'FAMILY_TYPE', 'ARCHIVE_FORMAT', 'UNIT', 'DOWNLOAD_ONLY'
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

STRINGENCY = OverridableOption(
    '-s', '--stringency', type=click.STRING, required=False, help='Stringency level for the recommended cutoffs.'
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
    '-F',
    '--family-type',
    type=PseudoPotentialFamilyTypeParam(),
    default='pseudo.family',
    show_default=True,
    help='Choose the type of pseudo potential family to create.'
)

PSEUDO_TYPE = OverridableOption(
    '-P',
    '--pseudo-type',
    type=PseudoPotentialTypeParam(),
    default='pseudo',
    show_default=True,
    help=(
        'Select the pseudopotential type to be used for the family. Should be the entry point name of a '
        'subclass of `PseudoPotentialData`.'
    )
)

ARCHIVE_FORMAT = OverridableOption(
    '-f', '--archive-format', type=click.Choice([fmt[0] for fmt in shutil.get_archive_formats()])
)

UNIT = OverridableOption(
    '-u',
    '--unit',
    type=UnitParamType(quantity='energy'),
    required=False,
    default='eV',
    show_default=True,
    help='Specify the energy unit of the cutoffs. Must be recognized by the ``UnitRegistry`` of the ``pint`` library.'
)

DOWNLOAD_ONLY = OverridableOption(
    '--download-only',
    is_flag=True,
    help=(
        'Only download the pseudopotential files to the current working directory, without installing the '
        'pseudopotential family.'
    )
)
