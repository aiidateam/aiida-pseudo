# -*- coding: utf-8 -*-
"""Commands to list instances of `PseudoPotentialFamily`."""
from aiida.cmdline.params import options as options_core
from aiida.cmdline.utils import decorators, echo
import click

from .params import options
from .root import cmd_root

PROJECTIONS_VALID = ('pk', 'uuid', 'type_string', 'label', 'description', 'count')
PROJECTIONS_DEFAULT = ('label', 'type_string', 'count')


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
@options.FAMILY_TYPE(default=None, help='Filter for families of with this type string.')
@decorators.with_dbenv()
def cmd_list(project, raw, family_type):
    """List installed pseudo potential families."""
    from tabulate import tabulate

    mapping_project = {
        'count': lambda family: family.count(),
    }

    if get_families_builder().count() == 0:
        echo.echo_report('no pseudo potential families have been installed yet: use `aiida-pseudo install`.')
        return

    rows = []

    for group, in get_families_builder().iterall():

        if family_type and family_type.entry_point != group.type_string:
            continue

        row = []

        for projection in project:
            try:
                projected = mapping_project[projection](group)
            except KeyError:
                projected = getattr(group, projection)
            row.append(projected)

        rows.append(row)

    if not rows:
        echo.echo_report('no pseudo potential families found that match the filtering criteria.')
        return

    if raw:
        echo.echo(tabulate(rows, disable_numparse=True, tablefmt='plain'))
    else:
        headers = [projection.replace('_', ' ').capitalize() for projection in project]
        echo.echo(tabulate(rows, headers=headers, disable_numparse=True))
