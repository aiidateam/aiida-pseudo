# -*- coding: utf-8 -*-
# pylint: disable=unused-argument,pointless-statement
"""Tests for the `PseudoDojoFamily` subclasses."""
import pytest

from aiida_pseudo.groups.family import (
    PseudoDojoConfiguration, PseudoDojoFamily, PseudoDojoPsp8Family, PseudoDojoUpfFamily, PseudoDojoPsmlFamily
)


@pytest.mark.parametrize(['family', 'type_string'], (
    (PseudoDojoFamily, 'pseudo.family.pseudo_dojo'),
    (PseudoDojoPsp8Family, 'pseudo.family.pseudo_dojo.psp8'),
    (PseudoDojoUpfFamily, 'pseudo.family.pseudo_dojo.upf'),
    (PseudoDojoPsmlFamily, 'pseudo.family.pseudo_dojo.psml'),
))
def test_type_string(clear_db, family, type_string):
    """Verify the `_type_string` class attribute is correctly set to the corresponding entry point name."""
    assert family._type_string == type_string  # pylint: disable=protected-access


@pytest.mark.parametrize('family', (PseudoDojoPsp8Family, PseudoDojoUpfFamily, PseudoDojoPsmlFamily))
def test_default_configuration(family):
    """Test the `PseudoDojoFamily.default_configuration` class attribute."""
    assert isinstance(family.default_configuration, PseudoDojoConfiguration)


@pytest.mark.parametrize('family', (PseudoDojoPsp8Family, PseudoDojoUpfFamily, PseudoDojoPsmlFamily))
def test_valid_configurations(family):
    """Test the `PseudoDojoFamily.valid_configurations` class attribute."""
    valid_configurations = family.valid_configurations
    assert isinstance(valid_configurations, tuple)

    for entry in valid_configurations:
        assert isinstance(entry, PseudoDojoConfiguration)


@pytest.mark.parametrize('family', (PseudoDojoPsp8Family, PseudoDojoUpfFamily, PseudoDojoPsmlFamily))
def test_get_valid_labels(family):
    """Test the `PseudoDojoFamily.get_valid_labels` class method."""
    valid_labels = family.get_valid_labels()
    assert isinstance(valid_labels, tuple)

    for entry in valid_labels:
        assert isinstance(entry, str)


@pytest.mark.parametrize('family', (PseudoDojoPsp8Family, PseudoDojoUpfFamily, PseudoDojoPsmlFamily))
def test_format_configuration_label(family):
    """Test the `PseudoDojoFamily.format_configuration_label` class method."""
    configuration = PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard')
    pseudo_format = family.get_pseudo_format()
    assert family.format_configuration_label(configuration) == f'PseudoDojo/04/pbe/sr/standard/{pseudo_format}'


@pytest.mark.parametrize('family', (PseudoDojoPsp8Family, PseudoDojoUpfFamily, PseudoDojoPsmlFamily))
def test_constructor(family):
    """Test that the `PseudoDojoFamily` constructor validates the label."""
    with pytest.raises(ValueError, match=r'the label `.*` is not a valid PseudoDojo configuration label'):
        family()

    with pytest.raises(ValueError, match=r'the label `.*` is not a valid PseudoDojo configuration label'):
        family(label='SSSP_1.1_PBE_efficiency')

    label = family.format_configuration_label(family.default_configuration)
    family_instance = family(label=label)
    assert isinstance(family_instance, family)


@pytest.mark.parametrize(
    'family, pseudo_format', (
        (PseudoDojoPsp8Family, 'psp8'),
        (PseudoDojoUpfFamily, 'upf'),
        (PseudoDojoPsmlFamily, 'psml'),
    )
)
def test_get_pseudo_format(family, pseudo_format):
    """Test the `PseudoDojoFamily.get_pseudo_format` classmethod."""
    assert family.get_pseudo_format() == pseudo_format
