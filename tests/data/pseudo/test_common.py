# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""Tests that are common to all data plugins in the :py:mod:`~aiida_pseudo.data.pseudo` module."""
import pytest

from aiida import plugins


def get_entry_point_names():
    """Return the registered entry point names for the given common workflow.

    :param workflow: the name of the common workflow.
    :param leaf: if True, only return the leaf of the entry point name, i.e., the name of plugin that implements it.
    :return: list of entry points names.
    """
    prefix = 'pseudo.'
    entry_points_names = plugins.entry_point.get_entry_point_names('aiida.data')
    return [name for name in entry_points_names if name.startswith(prefix)]


@pytest.fixture(scope='function', params=get_entry_point_names())
def entry_point_name(request):
    """Fixture that parametrizes over all the registered subclass implementations of ``PseudoPotentialData``."""
    return request.param


def test_get_entry_point_name(entry_point_name):
    """Test the ``PseudoPotentialData.get_entry_point_name`` method."""
    cls = plugins.DataFactory(entry_point_name)
    assert cls.get_entry_point_name() == entry_point_name
