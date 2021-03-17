# -*- coding: utf-8 -*-
"""Mixin that adds support of recommended cutoffs to a ``Group`` subclass, using its extras."""
from typing import Union

from aiida.common.lang import type_check
from aiida.plugins import DataFactory

from aiida_pseudo.common.units import U

StructureData = DataFactory('structure')  # pylint: disable=invalid-name

__all__ = ('RecommendedCutoffMixin',)


class RecommendedCutoffMixin:
    """Mixin that adds support of recommended cutoffs to a ``Group`` subclass, using its extras.

    This class assumes that the cutoffs apply to a plane-wave based code and as such the cutoffs pertain to the wave
    functions and the charge density. The units have to be in electronvolt.
    """

    DEFAULT_UNIT = 'eV'

    _key_cutoffs = '_cutoffs'
    _key_cutoffs_unit = '_cutoffs_unit'
    _key_default_stringency = '_default_stringency'

    @staticmethod
    def validate_cutoffs(elements: set, cutoffs: dict) -> None:
        """Validate a cutoff dictionary for a given set of elements.

        :param elements: set of elements for which to validate the cutoffs dictionary.
        :param cutoffs: dictionary with recommended cutoffs. Format: multiple sets of recommended cutoffs can be
            specified where the key represents the stringency, e.g. ``low`` or ``normal``. For each stringency, a
            dictionary should be defined that for each element symbols for which the family contains a pseudopotential,
            two values are specified, ``cutoff_wfc`` and ``cutoff_rho``, containing a float value with the recommended
            cutoff to be used for the wave functions and charge density, respectively.
        :raises ValueError: if the set of elements and those defined in the cutoffs do not match exactly, or if the
            cutoffs dictionary has an invalid format.
        """
        elements_family = set(elements)

        for stringency, cutoffs_sub in cutoffs.items():

            elements_cutoffs = set(cutoffs_sub.keys())
            elements_diff = elements_family ^ elements_cutoffs

            if elements_family < elements_cutoffs:
                raise ValueError(f'cutoffs defined for unsupported elements: {elements_diff}')

            if elements_family > elements_cutoffs:
                raise ValueError(f'cutoffs not defined for all family elements: {elements_diff}')

            for element, values in cutoffs_sub.items():
                if set(values.keys()) != {'cutoff_wfc', 'cutoff_rho'}:
                    raise ValueError(
                        f'invalid cutoff keys for stringency `{stringency}` and element {element}: {values}'
                    )

                if any(not isinstance(cutoff, (int, float)) for cutoff in values.values()):
                    raise ValueError(
                        f'invalid cutoff values for stringency `{stringency}` and element {element}: {values}'
                    )

    @staticmethod
    def validate_cutoffs_unit(unit: str) -> None:
        """Validate the cutoffs unit.

        The unit should be a name that is recognized by the ``pint`` library to be a unit of energy.

        :raises ValueError: if an invalid unit is specified.
        """
        type_check(unit, str)

        if unit not in U:
            raise ValueError(f'`{unit}` is not a valid unit.')

        if not U.Quantity(1, unit).check('[energy]'):
            raise ValueError(f'`{unit}` is not a valid energy unit.')

    def validate_stringency(self, stringency: str) -> None:
        """Validate a cutoff stringency.

        :param stringency: the cutoff stringency to validate.
        :raises ValueError: if stringency is None or the family does not define cutoffs for the specified stringency.
        """
        if stringency is None:
            raise ValueError('defining a stringency is required.')

        if stringency not in self.get_cutoff_stringencies():
            raise ValueError(f'stringency `{stringency}` is not defined for this family.')

    def _get_cutoffs(self) -> dict:
        """Return the cutoffs dictionary.

        :return: the cutoffs extra or an empty dictionary if it has not yet been set.
        """
        return self.get_extra(self._key_cutoffs, {})

    def get_default_stringency(self) -> Union[str, None]:
        """Return the default stringency if defined.

        :return: the default stringency or ``None`` if no cutoffs have been defined for this family.
        :raises ValueError: if not default stringency has been defined.
        """
        try:
            return self.get_extra(self._key_default_stringency)
        except AttributeError as exception:
            raise ValueError('no default stringency has been defined.') from exception

    def get_cutoff_stringencies(self) -> tuple:
        """Return a tuple of the available cutoff stringencies.

        :return: the tuple of stringencies that are defined for this family.
        """
        return tuple(self._get_cutoffs().keys())

    def set_cutoffs(self, cutoffs: dict, default_stringency: str = None, unit: str = None) -> None:
        """Set the recommended cutoffs for the pseudos in this family.

        .. note:: units of the cutoffs should be in electronvolt.

        :param cutoffs: dictionary with recommended cutoffs. Format: one or multiple sets of recommended cutoffs can be
            specified where each key represents a stringency set, e.g. ``low`` or ``normal``. For each stringency, a
            dictionary should be defined that for each element symbols for which the family contains a pseudopotential,
            two values are specified, ``cutoff_wfc`` and ``cutoff_rho``, containing a float value with the recommended
            cutoff to be used for the wave functions and charge density, respectively.
        :param default_stringency: the default stringency to be used when ``get_recommended_cutoffs`` is called. If is
            possible to not specify this if and only if the cutoffs only contain a single stringency set. That one will
            then automatically be set as default.
        :param unit: string definition of a unit of energy as recognized by the ``UnitRegistry`` of the ``pint`` lib.
        :raises ValueError: if the cutoffs have an invalid format or the default stringency is invalid.
        """
        unit = unit or self.DEFAULT_UNIT

        self.validate_cutoffs(set(self.elements), cutoffs)
        self.validate_cutoffs_unit(unit)

        if default_stringency is None and len(cutoffs) != 1:
            raise ValueError('have to explicitly specify a default stringency when specifying multiple cutoff sets.')

        default_stringency = default_stringency or list(cutoffs.keys())[0]

        self.set_extra(self._key_cutoffs, cutoffs)
        self.set_extra(self._key_cutoffs_unit, unit)
        self.set_extra(self._key_default_stringency, default_stringency)

    def get_cutoffs(self, stringency=None) -> Union[dict, None]:
        """Return a set of cutoffs for the given stringency.

        :param stringency: optional stringency if different from the default.
        :return: the cutoffs or ``None`` if no cutoffs whatsoever have been defined for this family.
        :raises ValueError: if the requested stringency is not defined for this family.
        """
        stringency = stringency or self.get_default_stringency()

        try:
            return self._get_cutoffs()[stringency]
        except KeyError as exception:
            raise ValueError(f'stringency `{stringency}` is not defined for this family.') from exception

    def get_recommended_cutoffs(self, *, elements=None, structure=None, stringency=None, unit=None):
        """Return tuple of recommended wavefunction and density cutoffs for the given elements or ``StructureData``.

        .. note:: at least one and only one of arguments ``elements`` or ``structure`` should be passed.

        :param elements: single or tuple of elements.
        :param structure: a ``StructureData`` node.
        :param stringency: optional stringency if different from the default.
        :return: tuple of recommended wavefunction and density cutoff.
        :raises ValueError: if the requested stringency is not defined for this family.
        :raises ValueError: if optional unit specified is invalid.
        """
        if (elements is None and structure is None) or (elements is not None and structure is not None):
            raise ValueError('at least one and only one of `elements` or `structure` should be defined')

        type_check(elements, (tuple, str), allow_none=True)
        type_check(structure, StructureData, allow_none=True)

        if unit is not None:
            self.validate_cutoffs_unit(unit)

        if structure is not None:
            symbols = structure.get_symbols_set()
        elif isinstance(elements, tuple):
            symbols = elements
        else:
            symbols = (elements,)

        cutoffs_wfc = []
        cutoffs_rho = []
        cutoffs = self.get_cutoffs(stringency=stringency)

        for element in symbols:

            if unit is not None:
                current_unit = self.get_cutoffs_unit()
                values = {k: U.Quantity(v, current_unit).to(unit).to_tuple()[0] for k, v in cutoffs[element].items()}
            else:
                values = cutoffs[element]

            cutoffs_wfc.append(values['cutoff_wfc'])
            cutoffs_rho.append(values['cutoff_rho'])

        return (max(cutoffs_wfc), max(cutoffs_rho))

    def get_cutoffs_unit(self) -> str:
        """Return the cutoffs unit.

        :return: the string representation of the unit of the cutoffs.
        """
        return self.get_extra(self._key_cutoffs_unit, self.DEFAULT_UNIT)
