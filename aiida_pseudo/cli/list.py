# -*- coding: utf-8 -*-
"""Commands to list instances of `PseudoPotentialFamily`."""
import click
from aiida.cmdline.params import options as options_core
from aiida.cmdline.utils import decorators, echo

from .root import cmd_root

PROJECTIONS_VALID = ('pk', 'uuid', 'label', 'description', 'count')
PROJECTIONS_DEFAULT = ('label', 'count')


def get_families_builder():
    """Return a query builder that will query for instances of `PseudoPotentialFamily` or its subclasses.

    :return: `QueryBuilder` instance
    """
    from aiida.orm import QueryBuilder
    from aiida_pseudo.groups.family import PseudoPotentialFamily

    builder = QueryBuilder().append(PseudoPotentialFamily)

    return builder


@cmd_root.command('list')
@options_core.PROJECT(type=click.Choice(PROJECTIONS_VALID), default=PROJECTIONS_DEFAULT)
@options_core.RAW()
@decorators.with_dbenv()
def cmd_list(project, raw):
    """List installed pseudo potential families."""
    from tabulate import tabulate

    mapping_project = {
        'count': lambda family: family.count(),
    }

    rows = []

    for [group] in get_families_builder().iterall():

        row = []

        for projection in project:
            try:
                projected = mapping_project[projection](group)
            except KeyError:
                projected = getattr(group, projection)
            row.append(projected)

        rows.append(row)

    if not rows:
        echo.echo_info('no pseudo potential families have been installed it: use `aiida-pseudo install`.')
        return

    if raw:
        echo.echo(tabulate(rows, disable_numparse=True, tablefmt='plain'))
    else:
        echo.echo(tabulate(rows, headers=[projection.capitalize() for projection in project], disable_numparse=True))
