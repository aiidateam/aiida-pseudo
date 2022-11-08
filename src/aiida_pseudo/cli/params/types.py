# -*- coding: utf-8 -*-
"""Custom parameter types for command line interface commands."""
from __future__ import annotations

import pathlib

from aiida.cmdline.params.types import GroupParamType
import click
import requests

from ..utils import attempt

__all__ = ('PseudoPotentialFamilyTypeParam', 'PseudoPotentialFamilyParam', 'PseudoPotentialTypeParam')


class PseudoPotentialTypeParam(click.ParamType):
    """Parameter type for ``click`` commands to define a subclass of ``PseudoPotentialData``."""

    name = 'pseudo_type'

    def convert(self, value, _, __):
        """Convert the entry point name to the corresponding class.

        :param value: entry point name that should correspond to subclass of ``PseudoPotentialData`` data plugin
        :return: the ``PseudoPotentialData`` subclass
        :raises: ``click.BadParameter`` if the entry point cannot be loaded or is not subclass of
            ``PseudoPotentialData``
        """
        from aiida.common import exceptions
        from aiida.plugins import DataFactory

        from aiida_pseudo.data.pseudo import PseudoPotentialData

        try:
            pseudo_type = DataFactory(value)
        except exceptions.EntryPointError as exception:
            raise click.BadParameter(f'`{value}` is not an existing data plugin.') from exception

        if not issubclass(pseudo_type, PseudoPotentialData):
            raise click.BadParameter(f'`{value}` entry point is not a subclass of `PseudoPotentialData`.')

        PseudoPotentialData.entry_point = value

        return pseudo_type

    def complete(self, _, incomplete):
        """Return possible completions based on an incomplete value.

        :returns: list of tuples of valid entry points (matching incomplete) and a description
        """
        from aiida.plugins.entry_point import get_entry_point_names
        entry_points = get_entry_point_names('aiida.data')
        return [(ep, '') for ep in entry_points if (ep.startswith('pseudo') and ep.startswith(incomplete))]


class PseudoPotentialFamilyParam(GroupParamType):
    """Parameter type for ``click`` commands to define an instance of a ``PseudoPotentialFamily``."""

    name = 'pseudo_family'

    def __init__(self, blacklist: list[str] | None = None, **kwargs):
        """Construct the parameter.

        :param blacklist: an optional list of values that should be considered invalid and will raise ``BadParameter``.
        """
        super().__init__(**kwargs)
        self.blacklist = blacklist

    def convert(self, value, param, ctx):
        """Convert the entry point name to the corresponding class.

        :param value: entry point name that should correspond to subclass of ``PseudoPotentialFamily`` group plugin
        :return: the ``PseudoPotentialFamily`` subclass
        :raises: `click.BadParameter` if the entry point cannot be loaded or is not subclass of `PseudoPotentialFamily`
        """
        family = super().convert(value, param, ctx)

        if self.blacklist and family.type_string in self.blacklist:
            self.fail(f'The value `{family}` is not allowed for this parameter.', param, ctx)
        return family


class PseudoPotentialFamilyTypeParam(click.ParamType):
    """Parameter type for ``click`` commands to define a subclass of ``PseudoPotentialFamily``."""

    name = 'pseudo_family_type'

    def __init__(self, blacklist: list[str] | None = None, **kwargs):
        """Construct the parameter.

        :param blacklist: an optional list of values that should be considered invalid and will raise ``BadParameter``.
        """
        super().__init__(**kwargs)
        self.blacklist = blacklist

    def convert(self, value, _, __):
        """Convert the entry point name to the corresponding class.

        :param value: entry point name that should correspond to subclass of ``PseudoPotentialFamily`` group plugin
        :return: the ``PseudoPotentialFamily`` subclass
        :raises: `click.BadParameter` if the entry point cannot be loaded or is not subclass of `
            `PseudoPotentialFamily``
        """
        from aiida.common import exceptions
        from aiida.plugins import GroupFactory

        from aiida_pseudo.groups.family import PseudoPotentialFamily

        try:
            family_type = GroupFactory(value)
        except exceptions.EntryPointError as exception:
            raise click.BadParameter(f'`{value}` is not an existing group plugin.') from exception

        if self.blacklist and value in self.blacklist:
            raise click.BadParameter(f'`{value}` is not an accepted value for this option.')

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


class PathOrUrl(click.Path):
    """Extension of ``click``'s ``Path``-type that also supports URLs."""

    name = 'PathOrUrl'

    def convert(self, value, param, ctx) -> pathlib.Path | bytes:
        """Convert the string value to the desired value.

        If the ``value`` corresponds to a valid path on the local filesystem, return it as a ``pathlib.Path`` instance.
        Otherwise, treat it as a URL and try to fetch the content. If successful, the raw retrieved bytes will be
        returned.

        :param value: the filepath on the local filesystem or a URL.
        """
        try:
            # Call the method of the super class, which will raise if it ``value`` is not a valid path.
            return pathlib.Path(super().convert(value, param, ctx))
        except click.exceptions.BadParameter:
            with attempt(f'attempting to download data from `{value}`...'):
                response = requests.get(value, timeout=30)
                response.raise_for_status()
                return response


class UnitParamType(click.ParamType):
    """Parameter type to specify units from the ``pint`` library."""

    name = 'unit'

    def __init__(self, quantity: list[str] | None = None, **kwargs):
        """Construct the parameter.

        :param quantity: The corresponding quantity of the unit.
        """
        super().__init__(**kwargs)
        self.quantity = quantity

    def convert(self, value, _, __):
        """Check if the provided unit is a valid unit for the defined quantity.

        :raises: ``click.BadParameter`` if the provided unit is not valid for the quantity defined for this instance.
        """
        from ...common.units import U

        if value not in U:
            raise click.BadParameter(f'`{value}` is not a valid unit.')

        if not U.Quantity(1, value).check(f'[{self.quantity}]'):
            raise click.BadParameter(f'`{value}` is not a valid `{self.quantity}` unit.')

        return value
