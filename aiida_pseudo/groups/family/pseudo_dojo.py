# -*- coding: utf-8 -*-
"""Subclass of `PseudoPotentialCutoffFamily` designed to represent an PseudoDojo configuration."""
from collections import namedtuple
from typing import Sequence

from .pseudo_cutoff import PseudoPotentialCutoffFamily
from .psml import PsmlFamily
from .psp8 import Psp8Family
from .upf import UpfFamily

__all__ = (
    'PseudoDojoConfiguration', 'PseudoDojoFamily', 'PseudoDojoPsp8Family', 'PseudoDojoUpfFamily', 'PseudoDojoPsmlFamily'
)

PseudoDojoConfiguration = namedtuple(
    'PseudoDojoConfiguration', ['version', 'functional', 'relativistic', 'protocol', 'format']
)


class PseudoDojoFamily(PseudoPotentialCutoffFamily):
    """Subclass of `PseudoPotentialCutoffFamily` designed to represent an PseudoDojo configuration.

    The `PseudoDojoFamily` is essentially a `PseudoPotentialCutoffFamily` with some additional constraints.
    It can only be used to contain the pseudo potentials and corresponding metadata of an official
    PseudoDojo configuration.
    """

    label_template = 'PseudoDojo/{version}/{functional}/{relativistic}/{protocol}/{format}'

    @classmethod
    def get_valid_labels(cls) -> Sequence[str]:
        """Return the tuple of labels of all valid PseudoDojo configurations."""
        return tuple(cls.format_configuration_label(configuration) for configuration in cls.valid_configurations)

    @classmethod
    def format_configuration_label(cls, configuration: PseudoDojoConfiguration) -> str:
        """Format a label for an `PseudoDojoFamily` with the required syntax.

        :param configuration: the PseudoDojo configuration
        :return: label
        """
        return cls.label_template.format(
            version=configuration.version,
            functional=configuration.functional,
            relativistic=configuration.relativistic,
            protocol=configuration.protocol,
            format=configuration.format
        )

    def __init__(self, label=None, **kwargs):
        """Construct a new instance, validating that the label matches the required format."""
        if label not in self.get_valid_labels():
            raise ValueError(f'the label `{label}` is not a valid PseudoDojo configuration label.')

        super().__init__(label=label, **kwargs)


class PseudoDojoPsp8Family(PseudoDojoFamily, Psp8Family):
    """Subclass of `PseudoDojoFamily` and `Psp8Family` designed to represent a psp8 PseudoDojo configuration.

    The `PseudoDojoPsp8Family` is essentially a `PseudoDojoFamily` with some additional constraints.
    It can only be used to contain the pseudo potentials and corresponding metadata of an official psp8
    PseudoDojo configuration.
    """

    default_configuration = PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard', 'psp8')
    valid_configurations = (
        # nc-sr-03_pbe
        PseudoDojoConfiguration('03', 'pbe', 'sr', 'standard', 'psp8'),
        PseudoDojoConfiguration('03', 'pbe', 'sr', 'stringent', 'psp8'),
        # nc-sr-03_pbesol
        PseudoDojoConfiguration('03', 'pbesol', 'sr', 'standard', 'psp8'),
        PseudoDojoConfiguration('03', 'pbesol', 'sr', 'stringent', 'psp8'),
        # nc-sr-03_lda
        PseudoDojoConfiguration('03', 'lda', 'sr', 'standard', 'psp8'),
        PseudoDojoConfiguration('03', 'lda', 'sr', 'stringent', 'psp8'),
        # nc-sr-04_pbe
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard', 'psp8'),
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'stringent', 'psp8'),
        # nc-sr-04_pbesol
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'standard', 'psp8'),
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'stringent', 'psp8'),
        # nc-sr-04_lda
        PseudoDojoConfiguration('04', 'lda', 'sr', 'standard', 'psp8'),
        PseudoDojoConfiguration('04', 'lda', 'sr', 'stringent', 'psp8'),
        # nc-sr-04-3plus_pbe
        PseudoDojoConfiguration('04', 'pbe', 'sr3plus', 'standard', 'psp8'),
        # nc-fr-04_pbe
        PseudoDojoConfiguration('04', 'pbe', 'fr', 'standard', 'psp8'),
        PseudoDojoConfiguration('04', 'pbe', 'fr', 'stringent', 'psp8'),
        # nc-fr-04_pbesol
        PseudoDojoConfiguration('04', 'pbesol', 'fr', 'standard', 'psp8'),
        PseudoDojoConfiguration('04', 'pbesol', 'fr', 'stringent', 'psp8'),
    )


class PseudoDojoUpfFamily(PseudoDojoFamily, UpfFamily):
    """Subclass of `PseudoDojoFamily` and `UpfFamily` designed to represent a upf PseudoDojo configuration.

    The `PseudoDojoUpfFamily` is essentially a `PseudoDojoFamily` with some additional constraints.
    It can only be used to contain the pseudo potentials and corresponding metadata of an official upf
    PseudoDojo configuration.
    """

    default_configuration = PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard', 'upf')
    valid_configurations = (
        # nc-sr-03_pbe
        PseudoDojoConfiguration('03', 'pbe', 'sr', 'standard', 'upf'),
        PseudoDojoConfiguration('03', 'pbe', 'sr', 'stringent', 'upf'),
        # nc-sr-03_pbesol
        PseudoDojoConfiguration('03', 'pbesol', 'sr', 'standard', 'upf'),
        PseudoDojoConfiguration('03', 'pbesol', 'sr', 'stringent', 'upf'),
        # nc-sr-03_lda
        PseudoDojoConfiguration('03', 'lda', 'sr', 'standard', 'upf'),
        PseudoDojoConfiguration('03', 'lda', 'sr', 'stringent', 'upf'),
        # nc-sr-04_pbe
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard', 'upf'),
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'stringent', 'upf'),
        # nc-sr-04_pbesol
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'standard', 'upf'),
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'stringent', 'upf'),
        # nc-sr-04_lda
        PseudoDojoConfiguration('04', 'lda', 'sr', 'standard', 'upf'),
        PseudoDojoConfiguration('04', 'lda', 'sr', 'stringent', 'upf'),
        # nc-sr-04-3plus_pbe
        PseudoDojoConfiguration('04', 'pbe', 'sr3plus', 'standard', 'upf'),
        # nc-fr-04_pbe
        PseudoDojoConfiguration('04', 'pbe', 'fr', 'standard', 'upf'),
        PseudoDojoConfiguration('04', 'pbe', 'fr', 'stringent', 'upf'),
        # nc-fr-04_pbesol
        PseudoDojoConfiguration('04', 'pbesol', 'fr', 'standard', 'upf'),
        PseudoDojoConfiguration('04', 'pbesol', 'fr', 'stringent', 'upf'),
    )


class PseudoDojoPsmlFamily(PseudoDojoFamily, PsmlFamily):
    """Subclass of `PseudoDojoFamily` and `PsmlFamily` designed to represent a psml PseudoDojo configuration.

    The `PseudoDojoPsmlFamily` is essentially a `PseudoDojoFamily` with some additional constraints.
    It can only be used to contain the pseudo potentials and corresponding metadata of an official psml
    PseudoDojo configuration.
    """

    default_configuration = PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard', 'psml')
    valid_configurations = (
        # nc-sr-04_pbe
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard', 'psml'),
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'stringent', 'psml'),
        # nc-sr-04_pbesol
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'standard', 'psml'),
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'stringent', 'psml'),
        # nc-sr-04_lda
        PseudoDojoConfiguration('04', 'lda', 'sr', 'standard', 'psml'),
        PseudoDojoConfiguration('04', 'lda', 'sr', 'stringent', 'psml'),
        # nc-sr-04-3plus_pbe
        PseudoDojoConfiguration('04', 'pbe', 'sr3plus', 'standard', 'psml'),
        # nc-fr-04_pbe
        PseudoDojoConfiguration('04', 'pbe', 'fr', 'standard', 'psml'),
        PseudoDojoConfiguration('04', 'pbe', 'fr', 'stringent', 'psml'),
        # nc-fr-04_pbesol
        PseudoDojoConfiguration('04', 'pbesol', 'fr', 'standard', 'psml'),
        PseudoDojoConfiguration('04', 'pbesol', 'fr', 'stringent', 'psml'),
    )
