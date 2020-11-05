# -*- coding: utf-8 -*-
"""Subclass of `PseudoPotentialFamily` that serves as a base class for representing pseudo potential families \
with suggested cutoffs."""

from typing import Union

from aiida.common.lang import type_check
from aiida.plugins import DataFactory

from .pseudo import PseudoPotentialFamily

__all__ = ('PseudoPotentialCutoffFamily',)

StructureData = DataFactory('structure')


class PseudoPotentialCutoffFamily(PseudoPotentialFamily):
    """Group to represent a pseudo potential family with suggested cutoffs."""

    _key_cutoffs = '_cutoffs'
    _key_default_stringency = '_default_stringency'

    @classmethod
    def validate_cutoffs(cls, elements: set, cutoffs: dict, default_stringency: str) -> None:
        """Validate a cutoff dictionary for a given set of elements.

        :param elements: set of elements for which to validate the cutoffs dictionary.
        :param cutoffs: dictionary with recommended cutoffs. Format: keys are the element symbols and the values are
            dictionaries themselves. The keys of the value dictionaries are the names of cutoff stringencies (e.g.
            ``low``, ``normal``, ``high``). The values are again dictionaries themselves each with two keys,
            ``cutoff_wfc`` and ``cutoff_rho``, containing a float value with the recommended cutoff to be used for
            the wave functions and charge density, respectively.
        :raises ValueError: if the set of elements and those defined in the cutoffs do not match exactly, or if the
            cutoffs dictionary has an invalid format.
        """
        elements_family = set(elements)
        if default_stringency not in cutoffs.keys():
            raise ValueError(
                f'default stringency {default_stringency} is not defined in stringencies: {cutoffs.keys()}'
            )
        for stringency in cutoffs.keys():
            elements_cutoffs = set(cutoffs[stringency].keys())
            elements_diff = elements_family ^ elements_cutoffs

            if elements_family < elements_cutoffs:
                raise ValueError(
                    f'cutoffs with stringency {stringency} defined for unsupported elements: {elements_diff}'
                )

            if elements_family > elements_cutoffs:
                raise ValueError(
                    f'cutoffs with stringency {stringency} not defined for all family elements: {elements_diff}'
                )

            for element, values in cutoffs[stringency].items():
                if set(values.keys()) != {'cutoff_wfc', 'cutoff_rho'}:
                    raise ValueError(f'invalid cutoff keys for stringency {stringency} and element {element}: {values}')

                if any(not isinstance(cutoff, (int, float)) for cutoff in values.values()):
                    raise ValueError(
                        f'invalid cutoff values for stringency {stringency} and element {element}: {values}'
                    )

    def set_cutoffs(self, cutoffs: dict, default_stringency: str) -> None:
        """Set the recommended cutoffs for the pseudos in this family.

        :param cutoffs: dictionary with recommended cutoffs. Format: keys are the element symbols and the values are
            dictionaries themselves, each with two keys, ``cutoff_wfc`` and ``cutoff_rho``, containing a float value
            with the recommended cutoff to be used for the wave functions and charge density, respectively.
        :raises ValueError: if the cutoffs have an invalid format
        """
        self.validate_cutoffs(set(self.elements), cutoffs, default_stringency)
        self.set_extra(self._key_cutoffs, cutoffs)
        self.set_extra(self._key_default_stringency, default_stringency)

    def get_cutoffs(self, stringency=None) -> Union[dict, None]:
        """Return the cutoffs dictionary.

        :return: the cutoffs or ``None`` if they are not defined for this family.
        """
        cutoffs = self.get_extra(self._key_cutoffs, {})
        if stringency is None:
            stringency = self.get_extra(self._key_default_stringency, None)
        return cutoffs.get(stringency, None)

    def get_recommended_cutoffs(self, *, elements=None, structure=None, stringency=None):
        """Return tuple of recommended wavefunction and density cutoffs for the given elements or ``StructureData``.

        .. note:: at least one and only one of arguments ``elements`` or ``structure`` should be passed.

        :param elements: single or tuple of elements.
        :param structure: a ``StructureData`` node.
        :return: tuple of recommended wavefunction and density cutoff.
        """
        if (elements is None and structure is None) or (elements is not None and structure is not None):
            raise ValueError('at least one and only one of `elements` or `structure` should be defined')

        type_check(elements, (tuple, str), allow_none=True)
        type_check(structure, StructureData, allow_none=True)

        if structure is not None:
            symbols = structure.get_symbols_set()
        elif isinstance(elements, tuple):
            symbols = elements
        else:
            symbols = (elements,)

        cutoffs_wfc = []
        cutoffs_rho = []
        cutoffs = self.get_cutoffs(stringency)

        for element in symbols:
            values = cutoffs[element]
            cutoffs_wfc.append(values['cutoff_wfc'])
            cutoffs_rho.append(values['cutoff_rho'])

        return (max(cutoffs_wfc), max(cutoffs_rho))

    def get_available_cutoff_stringencies(self) -> Union[tuple, None]:
        """Return a tuple of the available cutoff stringencies.

        :return: the stringencies or ``None`` if they are not defined for this family.
        """
        return tuple(self.get_extra(self._key_cutoffs, {}).keys())
