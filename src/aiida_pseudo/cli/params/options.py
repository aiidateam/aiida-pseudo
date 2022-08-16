# -*- coding: utf-8 -*-
"""Reusable options for CLI commands."""
import functools
import shutil

from aiida.cmdline.params import options as core_options
from aiida.cmdline.params import types as core_types
import click

from .types import PseudoPotentialFamilyTypeParam, PseudoPotentialTypeParam, UnitParamType

__all__ = (
    'PROFILE', 'VERBOSITY', 'VERSION', 'FUNCTIONAL', 'RELATIVISTIC', 'PROTOCOL', 'PSEUDO_FORMAT', 'STRINGENCY',
    'DEFAULT_STRINGENCY', 'TRACEBACK', 'FAMILY_TYPE', 'ARCHIVE_FORMAT', 'UNIT', 'DOWNLOAD_ONLY'
)

PROFILE = functools.partial(
    core_options.PROFILE, type=core_types.ProfileParamType(load_profile=True), expose_value=False
)

# Clone the ``VERBOSITY`` option from ``aiida-core`` so the ``-v`` short flag can be removed, since that overlaps with
# the flag of the ``VERSION`` option of this CLI.
VERBOSITY = core_options.VERBOSITY.clone()
VERBOSITY.args = ('--verbosity',)

VERSION = core_options.OverridableOption(
    '-v', '--version', type=click.STRING, required=False, help='Select the version of the installed configuration.'
)

FUNCTIONAL = core_options.OverridableOption(
    '-x',
    '--functional',
    type=click.STRING,
    required=False,
    help='Select the functional of the installed configuration.'
)

RELATIVISTIC = core_options.OverridableOption(
    '-r',
    '--relativistic',
    type=click.STRING,
    required=False,
    help='Select the type of relativistic effects included in the installed configuration.'
)

PROTOCOL = core_options.OverridableOption(
    '-p', '--protocol', type=click.STRING, required=False, help='Select the protocol of the installed configuration.'
)

PSEUDO_FORMAT = core_options.OverridableOption(
    '-f',
    '--pseudo-format',
    type=click.STRING,
    required=True,
    help='Select the pseudopotential file format of the installed configuration.'
)

STRINGENCY = core_options.OverridableOption(
    '-s', '--stringency', type=click.STRING, required=False, help='Stringency level for the recommended cutoffs.'
)

DEFAULT_STRINGENCY = core_options.OverridableOption(
    '-s',
    '--default-stringency',
    type=click.STRING,
    required=False,
    help='Select the default stringency level for the installed configuration.'
)

TRACEBACK = core_options.OverridableOption(
    '-t', '--traceback', is_flag=True, help='Include the stacktrace if an exception is encountered.'
)

FAMILY_TYPE = core_options.OverridableOption(
    '-F',
    '--family-type',
    type=PseudoPotentialFamilyTypeParam(),
    default='pseudo.family',
    show_default=True,
    help='Choose the type of pseudo potential family to create.'
)

PSEUDO_TYPE = core_options.OverridableOption(
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

ARCHIVE_FORMAT = core_options.OverridableOption(
    '-f', '--archive-format', type=click.Choice([fmt[0] for fmt in shutil.get_archive_formats()])
)

UNIT = core_options.OverridableOption(
    '-u',
    '--unit',
    type=UnitParamType(quantity='energy'),
    required=False,
    default='eV',
    show_default=True,
    help='Specify the energy unit of the cutoffs. Must be recognized by the ``UnitRegistry`` of the ``pint`` library.'
)

DOWNLOAD_ONLY = core_options.OverridableOption(
    '--download-only',
    is_flag=True,
    help=(
        'Only download the pseudopotential files to the current working directory, without installing the '
        'pseudopotential family.'
    )
)
