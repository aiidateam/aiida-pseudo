# -*- coding: utf-8 -*-
# pylint: disable=unused-argument,pointless-statement
"""Tests for the `PseudoDojoFamily` class."""
import pytest

from aiida_pseudo.data.pseudo import UpfData, Psp8Data, PsmlData, JthXmlData
from aiida_pseudo.groups.family import PseudoDojoConfiguration, PseudoDojoFamily


def test_type_string(clear_db):
    """Verify the `_type_string` class attribute is correctly set to the corresponding entry point name."""
    assert PseudoDojoFamily._type_string == 'pseudo.family.pseudo_dojo'  # pylint: disable=protected-access


def test_pseudo_types():
    """Test the `PseudoDojoFamily.pseudo_types` method."""
    assert PseudoDojoFamily.pseudo_types == (UpfData, PsmlData, Psp8Data, JthXmlData)


def test_default_configuration():
    """Test the `PseudoDojoFamily.default_configuration` class attribute."""
    assert isinstance(PseudoDojoFamily.default_configuration, PseudoDojoConfiguration)


def test_valid_configurations():
    """Test the `PseudoDojoFamily.valid_configurations` class attribute."""
    valid_configurations = PseudoDojoFamily.valid_configurations
    assert isinstance(valid_configurations, tuple)

    for entry in valid_configurations:
        assert isinstance(entry, PseudoDojoConfiguration)


def test_get_valid_labels():
    """Test the `PseudoDojoFamily.get_valid_labels` class method."""
    valid_labels = PseudoDojoFamily.get_valid_labels()
    assert isinstance(valid_labels, tuple)

    for entry in valid_labels:
        assert isinstance(entry, str)


def test_format_configuration_label():
    """Test the `PseudoDojoFamily.format_configuration_label` class method."""
    configuration = PseudoDojoConfiguration('0.4', 'PBE', 'SR', 'standard', 'psp8')
    assert PseudoDojoFamily.format_configuration_label(configuration) == 'PseudoDojo/0.4/PBE/SR/standard/psp8'


def test_constructor():
    """Test that the `PseudoDojoFamily` constructor validates the label."""
    with pytest.raises(ValueError, match=r'the label `.*` is not a valid PseudoDojo configuration label'):
        PseudoDojoFamily()

    with pytest.raises(ValueError, match=r'the label `.*` is not a valid PseudoDojo configuration label'):
        PseudoDojoFamily(label='nc-sr-04_pbe_standard_psp8')

    label = PseudoDojoFamily.format_configuration_label(PseudoDojoFamily.default_configuration)
    family = PseudoDojoFamily(label=label)
    assert isinstance(family, PseudoDojoFamily)


@pytest.mark.usefixtures('clear_db')
def test_create_from_folder(filepath_pseudos):
    """Test the `PseudoDojoFamily.create_from_folder` class method."""
    family = PseudoDojoFamily.create_from_folder(
        filepath_pseudos('upf'), 'PseudoDojo/0.4/PBE/SR/standard/psp8', pseudo_type=UpfData
    )
    assert isinstance(family, PseudoDojoFamily)


@pytest.mark.usefixtures('clear_db')
def test_create_from_folder_duplicate(filepath_pseudos):
    """Test that `PseudoDojoFamily.create_from_folder` raises for duplicate label."""
    label = 'PseudoDojo/0.4/PBE/SR/standard/psp8'
    PseudoDojoFamily(label=label).store()

    with pytest.raises(ValueError, match=r'the PseudoDojoFamily `.*` already exists'):
        PseudoDojoFamily.create_from_folder(filepath_pseudos('upf'), label)
