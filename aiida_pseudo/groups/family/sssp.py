# -*- coding: utf-8 -*-
"""Subclass of ``PseudoPotentialFamily`` designed to represent an SSSP configuration."""
from collections import namedtuple
from typing import Sequence

from aiida_pseudo.data.pseudo import UpfData
from ..mixins import RecommendedCutoffMixin
from .pseudo import PseudoPotentialFamily

__all__ = ('SsspConfiguration', 'SsspFamily')

SsspConfiguration = namedtuple('SsspConfiguration', ['version', 'functional', 'protocol'])


class SsspFamily(RecommendedCutoffMixin, PseudoPotentialFamily):
    """Subclass of ``PseudoPotentialFamily`` designed to represent an SSSP configuration.

    The ``SsspFamily`` is essentially a ``PseudoPotentialFamily`` with some additional constraints. It can only be used
    to contain the pseudo potentials and corresponding metadata of an official SSSP configuration.
    """

    _pseudo_types = (UpfData,)

    label_template = 'SSSP/{version}/{functional}/{protocol}'
    filename_template = 'SSSP_{version}_{functional}_{protocol}'
    default_configuration = SsspConfiguration('1.1', 'PBE', 'efficiency')
    valid_configurations = (
        SsspConfiguration('1.0', 'PBE', 'efficiency'),
        SsspConfiguration('1.0', 'PBE', 'precision'),
        SsspConfiguration('1.1', 'PBE', 'efficiency'),
        SsspConfiguration('1.1', 'PBE', 'precision'),
        SsspConfiguration('1.1', 'PBEsol', 'efficiency'),
        SsspConfiguration('1.1', 'PBEsol', 'precision'),
    )

    @classmethod
    def get_valid_labels(cls) -> Sequence[str]:
        """Return the tuple of labels of all valid SSSP configurations."""
        return tuple(cls.format_configuration_label(configuration) for configuration in cls.valid_configurations)

    @classmethod
    def format_configuration_label(cls, configuration: SsspConfiguration) -> str:
        """Format a label for an `SsspFamily` with the required syntax.

        :param configuration: the SSSP configuration
        :return: label
        """
        return cls.label_template.format(
            version=configuration.version, functional=configuration.functional, protocol=configuration.protocol
        )

    @classmethod
    def format_configuration_filename(cls, configuration: SsspConfiguration, extension: str) -> str:
        """Format the filename for a file of a particular SSSP configuration as it is available from MC Archive.

        :param configuration: the SSSP configuration.
        :param extension: the filename extension without the leading dot.
        :return: filename
        """
        return cls.filename_template.format(
            version=configuration.version, functional=configuration.functional, protocol=configuration.protocol
        ) + f'.{extension}'

    def __init__(self, label=None, **kwargs):
        """Construct a new instance, validating that the label matches the required format."""
        if label not in self.get_valid_labels():
            raise ValueError(f'the label `{label}` is not a valid SSSP configuration label.')

        super().__init__(label=label, **kwargs)
