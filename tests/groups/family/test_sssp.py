# -*- coding: utf-8 -*-
# pylint: disable=unused-argument,pointless-statement
"""Tests for the `SsspFamily` class."""
import pytest

from aiida_pseudo.data.pseudo.upf import UpfData
from aiida_pseudo.groups.family import SsspConfiguration, SsspFamily


def test_type_string(clear_db):
    """Verify the `_type_string` class attribute is correctly set to the corresponding entry point name."""
    assert SsspFamily._type_string == 'pseudo.family.sssp'  # pylint: disable=protected-access


def test_pseudo_types():
    """Test the `SsspFamily.pseudo_types` method."""
    assert SsspFamily.pseudo_types == (UpfData,)


def test_default_configuration():
    """Test the `SsspFamily.default_configuration` class attribute."""
    assert isinstance(SsspFamily.default_configuration, SsspConfiguration)


def test_valid_configurations():
    """Test the `SsspFamily.valid_configurations` class attribute."""
    valid_configurations = SsspFamily.valid_configurations
    assert isinstance(valid_configurations, tuple)

    for entry in valid_configurations:
        assert isinstance(entry, SsspConfiguration)


def test_get_valid_labels():
    """Test the `SsspFamily.get_valid_labels` class method."""
    valid_labels = SsspFamily.get_valid_labels()
    assert isinstance(valid_labels, tuple)

    for entry in valid_labels:
        assert isinstance(entry, str)


def test_format_configuration_label():
    """Test the `SsspFamily.format_configuration_label` class method."""
    configuration = SsspConfiguration(1.1, 'PBE', 'efficiency')
    assert SsspFamily.format_configuration_label(configuration) == 'SSSP/1.1/PBE/efficiency'


def test_constructor():
    """Test that the `SsspFamily` constructor validates the label."""
    with pytest.raises(ValueError, match=r'the label `.*` is not a valid SSSP configuration label'):
        SsspFamily()

    with pytest.raises(ValueError, match=r'the label `.*` is not a valid SSSP configuration label'):
        SsspFamily(label='SSSP_1.1_PBE_efficiency')

    label = SsspFamily.format_configuration_label(SsspFamily.default_configuration)
    family = SsspFamily(label=label)
    assert isinstance(family, SsspFamily)


@pytest.mark.usefixtures('clear_db')
def test_create_from_folder(filepath_pseudos):
    """Test the `SsspFamily.create_from_folder` class method."""
    family = SsspFamily.create_from_folder(filepath_pseudos('upf'), 'SSSP/1.1/PBE/efficiency', pseudo_type=UpfData)
    assert isinstance(family, SsspFamily)


@pytest.mark.usefixtures('clear_db')
def test_create_from_folder_duplicate(filepath_pseudos):
    """Test that `SsspFamily.create_from_folder` raises for duplicate label."""
    label = 'SSSP/1.1/PBE/efficiency'
    SsspFamily(label=label).store()

    with pytest.raises(ValueError, match=r'the SsspFamily `.*` already exists'):
        SsspFamily.create_from_folder(filepath_pseudos('upf'), label)
