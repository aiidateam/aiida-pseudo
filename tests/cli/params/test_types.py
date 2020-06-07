# -*- coding: utf-8 -*-
"""Tests for the :mod:`~aiida_pseudo.cli.params.types` module."""
import click
import pytest

from aiida_pseudo.cli.params import types
from aiida_pseudo.groups.family import PseudoPotentialFamily


def test_pseudo_family_type_param_convert(ctx):
    """Test the `PseudoPotentialFamilyTypeParam.convert` method."""
    param = types.PseudoPotentialFamilyTypeParam()

    with pytest.raises(click.BadParameter, match=r'.*is not an existing group plugin.'):
        param.convert('non.existing', None, ctx)

    with pytest.raises(click.BadParameter, match=r'.*entry point is not a subclass of `PseudoPotentialFamily`.'):
        param.convert('core', None, ctx)

    assert param.convert('pseudo.family', None, ctx) is PseudoPotentialFamily


def test_pseudo_family_type_param_complete(ctx):
    """Test the `PseudoPotentialFamilyTypeParam.complete` method."""
    param = types.PseudoPotentialFamilyTypeParam()
    assert isinstance(param.complete(ctx, ''), list)
    assert isinstance(param.complete(ctx, 'pseudo'), list)
    assert ('pseudo.family', '') in param.complete(ctx, 'pseudo')
