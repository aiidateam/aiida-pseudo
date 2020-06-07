# -*- coding: utf-8 -*-
"""Command to install a pseudo potential family."""
import click

from aiida.cmdline.params import options as options_core
from aiida.cmdline.utils import decorators, echo

from .params import PseudoPotentialFamilyParam
from .root import cmd_root


@cmd_root.command('show')
@click.argument('family', type=PseudoPotentialFamilyParam(sub_classes=('aiida.groups:pseudo.family',)))
@options_core.RAW()
@decorators.with_dbenv()
def cmd_show(family, raw):
    """Show details of pseudo potential family."""
    from tabulate import tabulate

    rows = [[pseudo.element, pseudo.filename, pseudo.md5] for pseudo in family.nodes]
    headers = ['Element', 'Pseudo', 'MD5']

    if raw:
        echo.echo(tabulate(sorted(rows), tablefmt='plain'))
    else:
        echo.echo(tabulate(sorted(rows), headers=headers))
