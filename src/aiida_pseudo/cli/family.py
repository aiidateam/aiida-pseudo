# -*- coding: utf-8 -*-
"""Commands to inspect or modify the contents of pseudo potential families."""
import json

from aiida.cmdline.params import options as options_core
from aiida.cmdline.utils import decorators, echo
import click

from .params import arguments, options, types
from .root import cmd_root


@cmd_root.group('family')
def cmd_family():
    """Command group to inspect or modify the contents of pseudo potential families."""


@cmd_family.command('show')
@arguments.PSEUDO_POTENTIAL_FAMILY()
@options.STRINGENCY()
@options.UNIT(default=None)
@options_core.RAW()
@decorators.with_dbenv()
def cmd_family_show(family, stringency, unit, raw):
    """Show details of pseudo potential family."""
    from tabulate import tabulate

    from ..groups.mixins import RecommendedCutoffMixin

    if isinstance(family, RecommendedCutoffMixin):

        try:
            family.validate_stringency(stringency)
        except ValueError as exception:
            raise click.BadParameter(f'{exception}', param_hint="'-s' / '--stringency'")

        unit = unit or family.get_cutoffs_unit(stringency)

        headers = ['Element', 'Pseudo', 'MD5', f'Wavefunction ({unit})', f'Charge density ({unit})']
        rows = [[
            pseudo.element, pseudo.filename, pseudo.md5,
            *family.get_recommended_cutoffs(elements=pseudo.element, stringency=stringency, unit=unit)
        ] for pseudo in family.nodes]
    else:
        headers = ['Element', 'Pseudo', 'MD5']
        rows = [[pseudo.element, pseudo.filename, pseudo.md5] for pseudo in family.nodes]

    if raw:
        echo.echo(tabulate(sorted(rows), tablefmt='plain', floatfmt='.1f'))
    else:
        echo.echo(tabulate(sorted(rows), headers=headers, floatfmt='.1f'))


@cmd_family.group('cutoffs')
def cmd_family_cutoffs():
    """Command group to inspect or modify the recommended cutoffs of pseudo potential families."""


@cmd_family_cutoffs.command('set')
@arguments.PSEUDO_POTENTIAL_FAMILY(
    type=types.PseudoPotentialFamilyParam(blacklist=('pseudo.family.sssp', 'pseudo.family.pseudo_dojo'))
)
@click.argument('cutoffs', type=click.File(mode='rb'))
@options.STRINGENCY(required=True)
@options.UNIT()
@decorators.with_dbenv()
def cmd_family_cutoffs_set(family, cutoffs, stringency, unit):  # noqa: D301
    """Set the recommended cutoffs for a pseudo potential family and a specified stringency.

    The cutoffs should be provided as a JSON file through the argument `CUTOFFS` which should have the structure:

    \b
        {
            "Ag": {
                "cutoff_wfc": 50.0,
                "cutoff_rho": 200.0
            },
            ...
        }

    where the cutoffs are expected to be in electronvolt by default.
    """
    from ..groups.mixins import RecommendedCutoffMixin

    if not isinstance(family, RecommendedCutoffMixin):
        raise click.BadParameter(f'family `{family}` does not support recommended cutoffs to be set.')

    try:
        data = json.load(cutoffs)
    except ValueError as exception:
        raise click.BadParameter(f'`{cutoffs.name}` contains invalid JSON: {exception}', param_hint='CUTOFFS')

    cutoffs_dict = {}
    for element, values in data.items():
        try:
            cutoffs_dict[element] = {'cutoff_wfc': values['cutoff_wfc'], 'cutoff_rho': values['cutoff_rho']}
        except KeyError as exception:
            raise click.BadParameter(
                f'`{cutoffs.name}` is missing cutoffs for element `{element}`: {exception}', param_hint='CUTOFFS'
            ) from exception

    try:
        family.set_cutoffs(cutoffs_dict, stringency, unit=unit)
    except ValueError as exception:
        raise click.BadParameter(f'`{cutoffs.name}` contains invalid cutoffs: {exception}', param_hint='CUTOFFS')

    echo.echo_success(f'set cutoffs for `{family}` with the stringency `{stringency}`.')
