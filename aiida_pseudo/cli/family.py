# -*- coding: utf-8 -*-
"""Commands to inspect or modify the contents of pseudo potential families."""
import json

import click

from aiida.cmdline.utils import decorators, echo

from ..groups.mixins import RecommendedCutoffMixin
from .params import arguments, options
from .root import cmd_root


@cmd_root.group('family')
def cmd_family():
    """Command group to inspect or modify the contents of pseudo potential families."""


@cmd_family.group('cutoffs')
def cmd_family_cutoffs():
    """Command group to inspect or modify the recommended cutoffs of pseudo potential families."""


@cmd_family_cutoffs.command('set')
@arguments.PSEUDO_POTENTIAL_FAMILY()
@click.argument('cutoffs', type=click.File(mode='rb'))
@options.STRINGENCY(required=True)
@decorators.with_dbenv()
def cmd_family_cutoffs_set(family, cutoffs, stringency):  # noqa: D301
    """Set the recommended cutoffs for a pseudo potential family.

    The cutoffs should be provided as a JSON file through the argument `CUTOFFS` which should have the structure:

    \b
        {
            "Ag": {
                "cutoff_wfc": 50.0,
                "cutoff_rho": 200.0
            },
            ...
        }

    where the cutoffs are expected to be in electronvolt.
    """
    if not isinstance(family, RecommendedCutoffMixin):
        raise click.BadParameter(f'family `{family}` does not support recommended cutoffs to be set.')

    try:
        data = json.load(cutoffs)
    except ValueError as exception:
        raise click.BadParameter(f'`{cutoffs.name}` contains invalid JSON: {exception}', param_hint='CUTOFFS')

    try:
        family.set_cutoffs({stringency: data})
    except ValueError as exception:
        raise click.BadParameter(f'`{cutoffs.name}` contains invalid cutoffs: {exception}', param_hint='CUTOFFS')

    echo.echo_success(f'set cutoffs for `{family}` with the stringency `{stringency}`.')
