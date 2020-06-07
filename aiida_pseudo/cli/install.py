# -*- coding: utf-8 -*-
"""Command to install a pseudo potential family."""
import click

from aiida.cmdline.utils import decorators, echo
from aiida.cmdline.params import options

from .params import PseudoPotentialFamilyTypeParam
from .root import cmd_root


@cmd_root.group('install')
def cmd_install():
    """Install pseudo potential families."""


@cmd_install.command('family')
@options.DESCRIPTION(help='Description for the family.')
@click.option(
    '-T',
    '--family-type',
    type=PseudoPotentialFamilyTypeParam(),
    default='pseudo.family',
    show_default=True,
    help='Choose the type of pseudo potential family to create.'
)
@click.option('-t', '--traceback', is_flag=True, help='Include the stacktrace if an exception is encountered.')
@click.argument('filepath_archive', type=click.Path(exists=True))
@click.argument('label', type=click.STRING)
@decorators.with_dbenv()
def cmd_install_family(description, family_type, traceback, filepath_archive, label):
    """Install a standard pseudo potential family."""
    from .utils import attempt, create_family_from_archive

    with attempt('unpacking archive and parsing pseudos... ', include_traceback=traceback):
        family = create_family_from_archive(family_type, label, filepath_archive)

    family.description = description
    echo.echo_success('installed `{}` containing {} pseudo potentials'.format(label, family.count()))
