# -*- coding: utf-8 -*-
"""Subclass of `PseudoPotentialFamily` designed to represent an PseudoDojo configuration."""
from collections import namedtuple
from typing import Sequence

from aiida_pseudo.data.pseudo import PseudoPotentialData

from .pseudo import PseudoPotentialFamily
from .psml import PsmlFamily
from .psp8 import Psp8Family
from .upf import UpfFamily

__all__ = (
    'PseudoDojoConfiguration', 'PseudoDojoFamily', 'PseudoDojoPsp8Family', 'PseudoDojoUpfFamily', 'PseudoDojoPsmlFamily'
)

PseudoDojoConfiguration = namedtuple(
    'PseudoDojoConfiguration', ['version', 'functional', 'rel', 'protocol', 'hint', 'format']
)


class PseudoDojoFamily(PseudoPotentialFamily):
    """Subclass of `PseudoPotentialFamily` designed to represent an PseudoDojo configuration.

    The `PseudoDojoFamily` is essentially a `PseudoPotentialFamily` with some additional constraints. It can only be used to contain the
    pseudo potentials and corresponding metadata of an official PseudoDojo configuration.
    """

    label_template = 'PseudoDojo/{version}/{functional}/{rel}/{protocol}/{hint}/{format}'

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
            rel=configuration.rel,
            protocol=configuration.protocol,
            hint=configuration.hint,
            format=configuration.format
        )

    def __init__(self, label=None, **kwargs):
        """Construct a new instance, validating that the label matches the required format."""
        if label not in self.get_valid_labels():
            raise ValueError(f'the label `{label}` is not a valid PseudoDojo configuration label.')

        super().__init__(label=label, **kwargs)


class PseudoDojoPsp8Family(PseudoDojoFamily, Psp8Family):
    """Subclass of `PseudoDojoFamily` and `Psp8Family` designed to represent a psp8 PseudoDojo configuration.

    The `PseudoDojoPsp8Family` is essentially a `PseudoDojoFamily` with some additional constraints. It can only be used to contain the
    pseudo potentials and corresponding metadata of an official psp8 PseudoDojo configuration.
    """

    default_configuration = PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard', 'normal', 'psp8')
    valid_configurations = (
        # nc-sr-03_pbe
        PseudoDojoConfiguration('03', 'pbe', 'sr', 'standard', 'none', 'psp8'),
        PseudoDojoConfiguration('03', 'pbe', 'sr', 'stringent', 'none', 'psp8'),
        # nc-sr-03_pbesol
        PseudoDojoConfiguration('03', 'pbesol', 'sr', 'standard', 'none', 'psp8'),
        PseudoDojoConfiguration('03', 'pbesol', 'sr', 'stringent', 'none', 'psp8'),
        # nc-sr-03_lda
        PseudoDojoConfiguration('03', 'lda', 'sr', 'standard', 'none', 'psp8'),
        PseudoDojoConfiguration('03', 'lda', 'sr', 'stringent', 'none', 'psp8'),
        # nc-sr-04_pbe_standard
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard', 'low', 'psp8'),
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard', 'normal', 'psp8'),
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard', 'high', 'psp8'),
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard', 'none', 'psp8'),
        # nc-sr-04_pbe_stringent
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'stringent', 'low', 'psp8'),
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'stringent', 'normal', 'psp8'),
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'stringent', 'high', 'psp8'),
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'stringent', 'none', 'psp8'),
        # nc-sr-04_pbesol_standard
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'standard', 'low', 'psp8'),
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'standard', 'normal', 'psp8'),
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'standard', 'high', 'psp8'),
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'standard', 'none', 'psp8'),
        # nc-sr-04_pbesol_stringent
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'stringent', 'low', 'psp8'),
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'stringent', 'normal', 'psp8'),
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'stringent', 'high', 'psp8'),
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'stringent', 'none', 'psp8'),
        # nc-sr-04_lda
        PseudoDojoConfiguration('04', 'lda', 'sr', 'standard', 'none', 'psp8'),
        PseudoDojoConfiguration('04', 'lda', 'sr', 'stringent', 'none', 'psp8'),
        # nc-sr-04-3plus_pbe
        PseudoDojoConfiguration('04', 'pbe', 'sr3plus', 'standard', 'none', 'psp8'),
        # nc-fr-04_pbe_standard
        # PseudoDojoConfiguration('04', 'pbe', 'fr','standard', 'low', 'psp8'),
        # PseudoDojoConfiguration('04', 'pbe', 'fr','standard', 'normal', 'psp8'),
        # PseudoDojoConfiguration('04', 'pbe', 'fr','standard', 'high', 'psp8'),
        PseudoDojoConfiguration('04', 'pbe', 'fr', 'standard', 'none', 'psp8'),
        # nc-fr-04_pbe_stringent
        # PseudoDojoConfiguration('04', 'pbe', 'fr', 'stringent', 'low', 'psp8'),
        # PseudoDojoConfiguration('04', 'pbe', 'fr', 'stringent', 'normal', 'psp8'),
        # PseudoDojoConfiguration('04', 'pbe', 'fr', 'stringent', 'high', 'psp8'),
        PseudoDojoConfiguration('04', 'pbe', 'fr', 'stringent', 'none', 'psp8'),
        # nc-fr-04_pbesol
        PseudoDojoConfiguration('04', 'pbesol', 'fr', 'standard', 'none', 'psp8'),
        PseudoDojoConfiguration('04', 'pbesol', 'fr', 'stringent', 'none', 'psp8'),
    )


class PseudoDojoUpfFamily(PseudoDojoFamily, UpfFamily):
    """Subclass of `PseudoDojoFamily` and `UpfFamily` designed to represent a upf PseudoDojo configuration.

    The `PseudoDojoUpfFamily` is essentially a `PseudoDojoFamily` with some additional constraints. It can only be used to contain the
    pseudo potentials and corresponding metadata of an official upf PseudoDojo configuration.
    """
    default_configuration = PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard', 'normal', 'upf')
    valid_configurations = (
        # nc-sr-03_pbe
        PseudoDojoConfiguration('03', 'pbe', 'sr', 'standard', 'none', 'upf'),
        PseudoDojoConfiguration('03', 'pbe', 'sr', 'stringent', 'none', 'upf'),
        # nc-sr-03_pbesol
        PseudoDojoConfiguration('03', 'pbesol', 'sr', 'standard', 'none', 'upf'),
        PseudoDojoConfiguration('03', 'pbesol', 'sr', 'stringent', 'none', 'upf'),
        # nc-sr-03_lda
        PseudoDojoConfiguration('03', 'lda', 'sr', 'standard', 'none', 'upf'),
        PseudoDojoConfiguration('03', 'lda', 'sr', 'stringent', 'none', 'upf'),
        # nc-sr-04_pbe_standard
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard', 'low', 'upf'),
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard', 'normal', 'upf'),
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard', 'high', 'upf'),
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard', 'none', 'upf'),
        # nc-sr-04_pbe_stringent
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'stringent', 'low', 'upf'),
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'stringent', 'normal', 'upf'),
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'stringent', 'high', 'upf'),
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'stringent', 'none', 'upf'),
        # nc-sr-04_pbesol_standard
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'standard', 'low', 'upf'),
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'standard', 'normal', 'upf'),
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'standard', 'high', 'upf'),
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'standard', 'none', 'upf'),
        # nc-sr-04_pbesol_stringent
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'stringent', 'low', 'upf'),
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'stringent', 'normal', 'upf'),
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'stringent', 'high', 'upf'),
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'stringent', 'none', 'upf'),
        # nc-sr-04_lda
        PseudoDojoConfiguration('04', 'lda', 'sr', 'standard', 'none', 'upf'),
        PseudoDojoConfiguration('04', 'lda', 'sr', 'stringent', 'none', 'upf'),
        # nc-sr-04-3plus_pbe_standard
        PseudoDojoConfiguration('04', 'pbe', 'sr3plus', 'standard', 'none', 'upf'),
        # nc-fr-04_pbe_standard
        # PseudoDojoConfiguration('04', 'pbe', 'fr','standard', 'low', 'upf'),
        # PseudoDojoConfiguration('04', 'pbe', 'fr','standard', 'normal', 'upf'),
        # PseudoDojoConfiguration('04', 'pbe', 'fr','standard', 'high', 'upf'),
        PseudoDojoConfiguration('04', 'pbe', 'fr', 'standard', 'none', 'upf'),
        # nc-fr-04_pbe_stringent
        # PseudoDojoConfiguration('04', 'pbe', 'fr', 'stringent', 'low', 'upf'),
        # PseudoDojoConfiguration('04', 'pbe', 'fr', 'stringent', 'normal', 'upf'),
        # PseudoDojoConfiguration('04', 'pbe', 'fr', 'stringent', 'high', 'upf'),
        PseudoDojoConfiguration('04', 'pbe', 'fr', 'stringent', 'none', 'upf'),
        # nc-fr-04_pbesol
        PseudoDojoConfiguration('04', 'pbesol', 'fr', 'standard', 'none', 'upf'),
        PseudoDojoConfiguration('04', 'pbesol', 'fr', 'stringent', 'none', 'upf'),
    )


class PseudoDojoPsmlFamily(PseudoDojoFamily, PsmlFamily):
    """Subclass of `PseudoDojoFamily` and `PsmlFamily` designed to represent a psml PseudoDojo configuration.

    The `PseudoDojoPsmlFamily` is essentially a `PseudoDojoFamily` with some additional constraints. It can only be used to contain the
    pseudo potentials and corresponding metadata of an official psml PseudoDojo configuration.
    """
    default_configuration = PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard', 'normal', 'psml')
    valid_configurations = (
        # nc-sr-04_pbe_standard
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard', 'low', 'psml'),
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard', 'normal', 'psml'),
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard', 'high', 'psml'),
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard', 'none', 'psml'),
        # nc-sr-04_pbe_stringent
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'stringent', 'low', 'psml'),
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'stringent', 'normal', 'psml'),
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'stringent', 'high', 'psml'),
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'stringent', 'none', 'psml'),
        # nc-sr-04_pbesol_standard
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'standard', 'low', 'psml'),
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'standard', 'normal', 'psml'),
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'standard', 'high', 'psml'),
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'standard', 'none', 'psml'),
        # nc-sr-04_pbesol_standard
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'stringent', 'low', 'psml'),
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'stringent', 'normal', 'psml'),
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'stringent', 'high', 'psml'),
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'stringent', 'none', 'psml'),
        # nc-sr-04_lda
        PseudoDojoConfiguration('04', 'lda', 'sr', 'standard', 'none', 'psml'),
        PseudoDojoConfiguration('04', 'lda', 'sr', 'stringent', 'none', 'psml'),
        # nc-sr-04-3plus_pbe_standard
        PseudoDojoConfiguration('04', 'pbe', 'sr3plus', 'standard', 'none', 'psml'),
        # nc-fr-04_pbe_standard
        # PseudoDojoConfiguration('04', 'pbe', 'fr','standard', 'low', 'psml'),
        # PseudoDojoConfiguration('04', 'pbe', 'fr','standard', 'normal', 'psml'),
        # PseudoDojoConfiguration('04', 'pbe', 'fr','standard', 'high', 'psml'),
        PseudoDojoConfiguration('04', 'pbe', 'fr', 'standard', 'none', 'psml'),
        # nc-fr-04_pbe_stringent
        # PseudoDojoConfiguration('04', 'pbe', 'fr', 'stringent', 'low', 'psml'),
        # PseudoDojoConfiguration('04', 'pbe', 'fr', 'stringent', 'normal', 'psml'),
        # PseudoDojoConfiguration('04', 'pbe', 'fr', 'stringent', 'high', 'psml'),
        PseudoDojoConfiguration('04', 'pbe', 'fr', 'stringent', 'none', 'psml'),
        # nc-fr-04_pbesol
        PseudoDojoConfiguration('04', 'pbesol', 'fr', 'standard', 'none', 'psml'),
        PseudoDojoConfiguration('04', 'pbesol', 'fr', 'stringent', 'none', 'psml'),
    )
