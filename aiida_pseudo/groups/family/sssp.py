# -*- coding: utf-8 -*-
"""Subclass of ``PseudoPotentialFamily`` designed to represent an SSSP configuration."""
from typing import NamedTuple, Optional, Sequence

from aiida_pseudo.data.pseudo import UpfData

from ..mixins import RecommendedCutoffMixin
from .pseudo import PseudoPotentialFamily

__all__ = ('SsspConfiguration', 'SsspFamily')


class SsspConfiguration(NamedTuple):
    """Named tuple that represents an SSSP configuration."""

    version: str
    functional: str
    protocol: str

    def __str__(self):
        """Represent the configuration as a string."""
        return f'SSSP v{self.version} {self.functional} {self.protocol}'


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
    def format_configuration_filename(
        cls, configuration: SsspConfiguration, extension: str, patch_version: Optional[str] = None
    ) -> str:
        """Format the filename for a file of a particular SSSP configuration as it is available from MC Archive.

        :param configuration: the SSSP configuration.
        :param extension: the filename extension without the leading dot.
        :param patch_version: patch version of the files which overrides the ``version`` specified in the
            ``configuration``. This is necessary because we only let users specify the minor version, not install
            configurations with a specific patch version. The filename on the archive however will contain the patch
            version, so this needs to be substituted.
        :return: filename
        """
        version = configuration.version if patch_version is None else patch_version

        return cls.filename_template.format(
            version=version, functional=configuration.functional, protocol=configuration.protocol
        ) + f'.{extension}'

    def __init__(self, label=None, **kwargs):
        """Construct a new instance, validating that the label matches the required format."""
        if label not in self.get_valid_labels():
            raise ValueError(f'the label `{label}` is not a valid SSSP configuration label.')

        super().__init__(label=label, **kwargs)
