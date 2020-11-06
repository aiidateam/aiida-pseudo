# -*- coding: utf-8 -*-
"""Subclass of `PseudoPotentialFamily` designed to represent a PseudoDojo configuration."""
from collections import namedtuple
from typing import Sequence

from .pseudo import PseudoPotentialFamily
from .psml import PsmlFamily
from .psp8 import Psp8Family
from .upf import UpfFamily

__all__ = (
    'PseudoDojoConfiguration', 'PseudoDojoFamily', 'PseudoDojoPsp8Family', 'PseudoDojoUpfFamily', 'PseudoDojoPsmlFamily'
)

PseudoDojoConfiguration = namedtuple('PseudoDojoConfiguration', ['version', 'functional', 'relativistic', 'protocol'])


class PseudoDojoFamily(PseudoPotentialFamily):
    """Subclass of `PseudoPotentialFamily` designed to represent an PseudoDojo configuration.

    The `PseudoDojoFamily` is essentially a `PseudoPotentialFamily` with some additional constraints. It can only be
    used to contain the pseudo potentials and corresponding metadata of an official PseudoDojo configuration.
    """

    _pseudo_format = None

    label_template = 'PseudoDojo/{version}/{functional}/{relativistic}/{protocol}/{pseudo_format}'
    default_configuration = PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard')
    invalid_configurations = ()
    valid_configurations = (
        PseudoDojoConfiguration('03', 'pbe', 'sr', 'standard'),
        PseudoDojoConfiguration('03', 'pbe', 'sr', 'stringent'),
        PseudoDojoConfiguration('03', 'pbesol', 'sr', 'standard'),
        PseudoDojoConfiguration('03', 'pbesol', 'sr', 'stringent'),
        PseudoDojoConfiguration('03', 'lda', 'sr', 'standard'),
        PseudoDojoConfiguration('03', 'lda', 'sr', 'stringent'),
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'standard'),
        PseudoDojoConfiguration('04', 'pbe', 'sr', 'stringent'),
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'standard'),
        PseudoDojoConfiguration('04', 'pbesol', 'sr', 'stringent'),
        PseudoDojoConfiguration('04', 'lda', 'sr', 'standard'),
        PseudoDojoConfiguration('04', 'lda', 'sr', 'stringent'),
        PseudoDojoConfiguration('04', 'pbe', 'sr3plus', 'standard'),
        PseudoDojoConfiguration('04', 'pbe', 'fr', 'standard'),
        PseudoDojoConfiguration('04', 'pbe', 'fr', 'stringent'),
        PseudoDojoConfiguration('04', 'pbesol', 'fr', 'standard'),
        PseudoDojoConfiguration('04', 'pbesol', 'fr', 'stringent'),
    )

    @classmethod
    def get_pseudo_format(cls) -> str:
        """Return the lower case string representation of the pseudopotential format."""
        from aiida.plugins.entry_point import get_entry_point_from_class

        if cls._pseudo_format is None:
            pseudo_type = cls._pseudo_type  # pylint: disable=protected-access
            _, entry_point = get_entry_point_from_class(pseudo_type.__module__, pseudo_type.__name__)
            cls._pseudo_format = entry_point.name.split('.')[-1]

        return cls._pseudo_format

    @classmethod
    def get_valid_labels(cls) -> Sequence[str]:
        """Return the tuple of labels of all valid PseudoDojo configurations."""
        configurations = set(cls.valid_configurations) - set(cls.invalid_configurations)
        return tuple(cls.format_configuration_label(configuration) for configuration in configurations)

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
            pseudo_format=cls.get_pseudo_format()
        )

    def __init__(self, label=None, **kwargs):
        """Construct a new instance, validating that the label matches the required format."""
        if label not in self.get_valid_labels():
            raise ValueError(f'the label `{label}` is not a valid PseudoDojo configuration label.')

        super().__init__(label=label, **kwargs)


class PseudoDojoPsp8Family(PseudoDojoFamily, Psp8Family):
    """Subclass of `PseudoDojoFamily` and `Psp8Family` to represent a PseudoDojo configuration with PSP8 pseudos.

    The `PseudoDojoPsp8Family` is essentially a `Psp8Family` with some additional constraints. It can only be used to
    contain the pseudo potentials and corresponding metadata of an official PSP8 PseudoDojo configuration.
    """


class PseudoDojoUpfFamily(PseudoDojoFamily, UpfFamily):
    """Subclass of `PseudoDojoFamily` and `UpfFamily` to represent a PseudoDojo configuration with UPF pseudos.

    The `PseudoDojoUpfFamily` is essentially a `UpfFamily` with some additional constraints. It can only be used to
    contain the pseudo potentials and corresponding metadata of an official upf
    PseudoDojo configuration.
    """


class PseudoDojoPsmlFamily(PseudoDojoFamily, PsmlFamily):
    """Subclass of `PseudoDojoFamily` and `PsmlFamily` to represent a PseudoDojo configuration with PSML pseudos.

    The `PseudoDojoPsmlFamily` is essentially a `PsmlFamily` with some additional constraints. It can only be used to
    contain the pseudo potentials and corresponding metadata of an official PSML PseudoDojo configuration.
    """

    invalid_configurations = (
        PseudoDojoConfiguration('03', 'pbe', 'sr', 'standard'),
        PseudoDojoConfiguration('03', 'pbe', 'sr', 'stringent'),
        PseudoDojoConfiguration('03', 'pbesol', 'sr', 'standard'),
        PseudoDojoConfiguration('03', 'pbesol', 'sr', 'stringent'),
        PseudoDojoConfiguration('03', 'lda', 'sr', 'standard'),
        PseudoDojoConfiguration('03', 'lda', 'sr', 'stringent'),
    )
