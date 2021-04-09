# -*- coding: utf-8 -*-
"""Command to install a pseudo potential family."""
import click

from aiida.cmdline.params import options as options_core
from aiida.cmdline.utils import decorators, echo

from ..groups.mixins import RecommendedCutoffMixin
from .params import PseudoPotentialFamilyParam, options
from .root import cmd_root


@cmd_root.command('show')
@click.argument('family', type=PseudoPotentialFamilyParam(sub_classes=('aiida.groups:pseudo.family',)))
@options.STRINGENCY()
@options_core.RAW()
@decorators.with_dbenv()
def cmd_show(family, stringency, raw):
    """Show details of pseudo potential family."""
    from tabulate import tabulate

    if isinstance(family, RecommendedCutoffMixin):

        if stringency is not None and stringency not in family.get_cutoff_stringencies():
            raise click.BadParameter(f'`{stringency}` is not defined for family `{family}`.', param_hint='stringency')

        headers = ['Element', 'Pseudo', 'MD5', 'Wavefunction (eV)', 'Charge density (eV)']
        rows = [[
            pseudo.element, pseudo.filename, pseudo.md5,
            *family.get_recommended_cutoffs(elements=pseudo.element, stringency=stringency)
        ] for pseudo in family.nodes]
    else:
        headers = ['Element', 'Pseudo', 'MD5']
        rows = [[pseudo.element, pseudo.filename, pseudo.md5] for pseudo in family.nodes]

    if raw:
        echo.echo(tabulate(sorted(rows), tablefmt='plain', floatfmt='.1f'))
    else:
        echo.echo(tabulate(sorted(rows), headers=headers, floatfmt='.1f'))
