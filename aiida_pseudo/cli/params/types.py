# -*- coding: utf-8 -*-
# pylint: disable=no-self-use
"""Custom parameter types for command line interface commands."""
import click

from aiida.cmdline.params.types import GroupParamType

__all__ = ('PseudoPotentialFamilyTypeParam', 'PseudoPotentialFamilyParam')


class PseudoPotentialFamilyParam(GroupParamType):
    """Parameter type for `click` commands to define an instance of a `PseudoPotentialFamily`."""

    name = 'pseudo_family'


class PseudoPotentialFamilyTypeParam(click.ParamType):
    """Parameter type for `click` commands to define a subclass of `PseudoPotentialFamily`."""

    name = 'pseudo_family_type'

    def convert(self, value, _, __):
        """Convert the entry point name to the corresponding class.

        :param value: entry point name that should correspond to subclass of `PseudoPotentialFamily` group plugin
        :return: the `PseudoPotentialFamily` subclass
        :raises: `click.BadParameter` if the entry point cannot be loaded or is not subclass of `PseudoPotentialFamily`
        """
        from aiida.common import exceptions
        from aiida.plugins import GroupFactory
        from aiida_pseudo.groups.family import PseudoPotentialFamily

        try:
            family_type = GroupFactory(value)
        except exceptions.EntryPointError as exception:
            raise click.BadParameter(f'`{value}` is not an existing group plugin.') from exception

        if not issubclass(family_type, PseudoPotentialFamily):
            raise click.BadParameter(f'`{value}` entry point is not a subclass of `PseudoPotentialFamily`.')

        PseudoPotentialFamily.entry_point = value

        return family_type

    def complete(self, _, incomplete):
        """Return possible completions based on an incomplete value.

        :returns: list of tuples of valid entry points (matching incomplete) and a description
        """
        from aiida.plugins.entry_point import get_entry_point_names
        entry_points = get_entry_point_names('aiida.groups')
        return [(ep, '') for ep in entry_points if (ep.startswith('pseudo.family') and ep.startswith(incomplete))]
