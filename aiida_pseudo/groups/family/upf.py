# -*- coding: utf-8 -*-
"""Group to represent a pseudo potential family with pseudos in UPF format."""
from typing import Union

from aiida.plugins import DataFactory

from .pseudo import PseudoPotentialFamily

__all__ = ('UpfFamily',)

UpfData = DataFactory('pseudo.upf')  # pylint: disable=invalid-name


class UpfFamily(PseudoPotentialFamily):
    """Group to represent a pseudo potential family with pseudos in UPF format."""

    _pseudo_type = UpfData
    _key_cutoffs = '_cutoffs'

    @classmethod
    def validate_cutoffs(cls, elements: set, cutoffs: dict) -> None:
        """Validate a cutoff dictionary for a given set of elements.

        :param elements: set of elements for which to validate the cutoffs dictionary.
        :param cutoffs: dictionary with recommended cutoffs. Format: keys are the element symbols and the values are
            dictionaries themselves, each with two keys, ``cutoff_wfc`` and ``cutoff_rho``, containing a float value
            with the recommended cutoff to be used for the wave functions and charge density, respectively.
        :raises ValueError: if the set of elements and those defined in the cutoffs do not match exactly, or if the
            cutoffs dictionary has an invalid format.
        """
        elements_family = set(elements)
        elements_cutoffs = set(cutoffs.keys())
        elements_diff = elements_family ^ elements_cutoffs

        if elements_family < elements_cutoffs:
            raise ValueError(f'cutoffs defined for unsupported elements: {elements_diff}')

        if elements_family > elements_cutoffs:
            raise ValueError(f'cutoffs not defined for all family elements: {elements_diff}')

        for element, values in cutoffs.items():
            if set(values.keys()) != {'cutoff_wfc', 'cutoff_rho'}:
                raise ValueError(f'invalid cutoff keys for element {element}: {values}')

            if any(not isinstance(cutoff, (int, float)) for cutoff in values.values()):
                raise ValueError(f'invalid cutoff values for element {element}: {values}')

    def set_cutoffs(self, cutoffs: dict) -> None:
        """Set the recommended cutoffs for the pseudos in this family.

        :param cutoffs: dictionary with recommended cutoffs. Format: keys are the element symbols and the values are
            dictionaries themselves, each with two keys, ``cutoff_wfc`` and ``cutoff_rho``, containing a float value
            with the recommended cutoff to be used for the wave functions and charge density, respectively.
        :raises ValueError: if the cutoffs have an invalid format
        """
        self.validate_cutoffs(set(self.elements), cutoffs)
        self.set_extra(self._key_cutoffs, cutoffs)

    def get_cutoffs(self) -> Union[dict, None]:
        """Return the cutoffs dictionary.

        :return: the cutoffs or ``None`` if they are not defined for this family.
        """
        return self.get_extra(self._key_cutoffs, None)
