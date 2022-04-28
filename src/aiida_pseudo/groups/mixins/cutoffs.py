# -*- coding: utf-8 -*-
"""Mixin that adds support of recommended cutoffs to a ``Group`` subclass, using its extras."""
from typing import Optional
import warnings

from aiida.common.lang import type_check
from aiida.plugins import DataFactory

from aiida_pseudo.common.units import U

StructureData = DataFactory('core.structure')  # pylint: disable=invalid-name

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
        :param cutoffs: dictionary with recommended cutoffs. Format: set of recommended cutoffs written as a
            dictionary that maps each element for which the family contains a pseudopotential to a dictionary that
            specifies the ``cutoff_wfc`` and ``cutoff_rho`` keys, corresponding a float value with the recommended
            cutoff to be used for the wave functions and charge density, respectively. For example:

            .. code-block::

                {
                    "Ag": {
                        "cutoff_wfc": 50.0,
                        "cutoff_rho": 200.0
                    },
                    ...
                }
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

    def validate_stringency(self, stringency: Optional[str]) -> None:
        """Validate a cutoff stringency.

        Check if the stringency is defined for the family. If no stringency input is passed, the method checks if a
        default stringency has been set.

        :param stringency: the cutoff stringency to validate.
        :raises ValueError: if `stringency` is equal to `None` and the family defines no default stringency.
        :raises ValueError: if the family does not define cutoffs for the specified stringency.
        """
        if stringency is None:
            self.get_default_stringency()
        elif stringency not in self.get_cutoff_stringencies():
            raise ValueError(
                f'stringency `{stringency}` is not one of the available cutoff stringencies for this family: '
                f'{self.get_cutoff_stringencies()}.'
            )

    def _get_cutoffs_dict(self) -> dict:
        """Return the cutoffs dictionary that maps the stringencies to the recommended cutoffs.

        :return: the cutoffs extra or an empty dictionary if it has not yet been set.
        """
        return self.base.extras.get(self._key_cutoffs, {})

    def _get_cutoffs_unit_dict(self) -> dict:
        """Return the cutoffs units for each of the stringencies.

        :return: the cutoffs units extra or an empty dictionary if it has not yet been set.
        """
        return self.base.extras.get(self._key_cutoffs_unit, {})

    def get_default_stringency(self) -> str:
        """Return the default stringency if defined.

        :return: the default stringency.
        :raises ValueError: if default stringency has not been defined.
        """
        try:
            return self.base.extras.get(self._key_default_stringency)
        except AttributeError as exception:
            raise ValueError('no default stringency has been defined.') from exception

    def set_default_stringency(self, default_stringency: str) -> None:
        """Set the default stringency for the recommended cutoffs.

        :param default_stringency: the default stringency to be used for the recommended cutoffs.
        :raises ValueError: if the provided default stringency is not in the tuple of available cutoff stringencies for
            the pseudo family.
        :raises ValueError: if the user tries to unset the stringency by providing ``None`` as an input.
        """
        if default_stringency is None:
            raise ValueError('the default stringency cannot be unset.')

        self.validate_stringency(default_stringency)
        self.base.extras.set(self._key_default_stringency, default_stringency)

    def get_cutoff_stringencies(self) -> tuple:
        """Return a tuple of the available cutoff stringencies.

        :return: the tuple of stringencies that are defined for this family.
        """
        return tuple(self._get_cutoffs_dict().keys())

    def set_cutoffs(self, cutoffs: dict, stringency: str, unit: str = None) -> None:
        """Set the recommended cutoffs for the pseudos in this family and a specified stringency.

        .. note: If, after the cutoffs have been set, there is only one stringency defined for the pseudo family, this
            method will automatically set this as the default. Use the ``set_default_stringency`` method to change the
            default when setting multiple stringencies.

        :param cutoffs: dictionary with recommended cutoffs. Format: set of recommended cutoffs written as a
            dictionary that maps each element for which the family contains a pseudopotential to a dictionary that
            specifies the ``cutoff_wfc`` and ``cutoff_rho`` keys, corresponding a float value with the recommended
            cutoff to be used for the wave functions and charge density, respectively. For example:

            .. code-block::

                {
                    "Ag": {
                        "cutoff_wfc": 50.0,
                        "cutoff_rho": 200.0
                    },
                    ...
                }
        :param stringency: the stringency corresponding to the provided cutoffs.
        :param unit: string definition of a unit of energy as recognized by the ``UnitRegistry`` of the ``pint`` lib.
            Defaults to electronvolt.
        :raises ValueError: if the cutoffs have an invalid format or the unit is not a valid energy unit.
        """
        unit = unit or self.DEFAULT_UNIT

        self.validate_cutoffs(set(self.elements), cutoffs)
        self.validate_cutoffs_unit(unit)

        cutoffs_dict = self._get_cutoffs_dict()
        cutoffs_dict[stringency] = cutoffs

        cutoffs_unit_dict = self._get_cutoffs_unit_dict()
        cutoffs_unit_dict[stringency] = unit

        self.base.extras.set(self._key_cutoffs, cutoffs_dict)
        self.base.extras.set(self._key_cutoffs_unit, cutoffs_unit_dict)
        if len(cutoffs_dict) == 1:
            self.set_default_stringency(stringency)

    def get_cutoffs(self, stringency: str = None) -> dict:
        """Return a set of cutoffs for the given stringency.

        :param stringency: optional stringency for which to retrieve the cutoffs. If not specified, the default
            stringency of the family is used.
        :raises ValueError: if no stringency is specified and no default stringency is defined for the family.
        :raises ValueError: if the requested stringency is not defined for this family.
        """
        self.validate_stringency(stringency)
        stringency = stringency or self.get_default_stringency()
        return self._get_cutoffs_dict()[stringency]

    def delete_cutoffs(self, stringency: str) -> None:
        """Delete the recommended cutoffs for a specified stringency.

        .. note: If, after the cutoffs have been deleted, there is only one stringency defined for the pseudo family,
            this method will automatically set this as the default. Use the ``set_default_stringency`` method to change
            the default in case multiple stringencies are still defined.

        :param stringency: stringency for which to delete the cutoffs.
        :raises ValueError: if the requested stringency is not defined for this family.
        """
        self.validate_stringency(stringency)

        cutoffs_dict = self._get_cutoffs_dict()
        cutoffs_dict.pop(stringency)

        cutoffs_unit_dict = self._get_cutoffs_unit_dict()
        cutoffs_unit_dict.pop(stringency, None)  # `None` is added to support pseudo families installed with v0.5.0

        self.base.extras.set(self._key_cutoffs, cutoffs_dict)
        self.base.extras.set(self._key_cutoffs_unit, cutoffs_unit_dict)

        warning = ''
        try:
            if stringency == self.get_default_stringency():
                self.delete_extra('_default_stringency')
                warning += f'`{stringency}` was the default stringency of this family.'
                assign_new_default = True
            else:
                assign_new_default = False
        except ValueError:
            assign_new_default = True

        if assign_new_default:
            if len(cutoffs_dict) == 0:
                warning += (
                    ' Since no other stringencies are defined for this family, no new default can be specified.'
                )
            elif len(cutoffs_dict) == 1:
                final_stringency = list(cutoffs_dict.keys())[0]
                self.set_default_stringency(final_stringency)
                warning += f' Setting `{final_stringency}` as the default since it is now the only defined stringency.'
            else:
                warning += (
                    f' Please set one of {self.get_cutoff_stringencies()} as the new default stringency with the '
                    '`set_default_stringency` method.'
                )

        if len(warning) > 0:
            warnings.warn(warning)

    def get_cutoffs_unit(self, stringency: str = None) -> str:
        """Return the cutoffs unit for the specified or family default stringency.

        :param stringency: optional stringency for which to retrieve the unit. If not specified, the default stringency
            of the family is used.
        :return: the string representation of the unit of the cutoffs.
        :raises ValueError: if no stringency is specified and no default stringency is defined for the family.
        :raises ValueError: if the requested stringency is not defined for this family.
        """
        self.validate_stringency(stringency)
        stringency = stringency or self.get_default_stringency()

        try:
            return self._get_cutoffs_unit_dict()[stringency]
        except KeyError:
            # Workaround to deal with pseudo families installed in v0.5.0 - Set default unit in case it is not in extras
            cutoffs_unit_dict = self._get_cutoffs_unit_dict()
            cutoffs_unit_dict[stringency] = 'eV'
            self.base.extras.set(self._key_cutoffs_unit, cutoffs_unit_dict)
            return 'eV'
            # End of workaround

    def get_recommended_cutoffs(self, *, elements=None, structure=None, stringency=None, unit=None):
        """Return tuple of recommended wavefunction and density cutoffs for the given elements or ``StructureData``.

        .. note:: at least one and only one of arguments ``elements`` or ``structure`` should be passed.

        :param elements: single or tuple of elements.
        :param structure: a ``StructureData`` node.
        :param stringency: optional stringency if different from the default.
        :param unit: string definition of a unit of energy as recognized by the ``UnitRegistry`` of the ``pint`` lib.
        :return: tuple of recommended wavefunction and density cutoff.
        :raises ValueError: if the requested stringency is not defined for this family.
        :raises ValueError: if optional unit specified is invalid.
        :raises ValueError: if the family does not have a pseudo for one of the elements (of the structure).
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
        cutoffs = self.get_cutoffs(stringency)

        for element in symbols:

            if element not in cutoffs:
                raise ValueError(f'family does not contain a pseudo for element `{element}`.')

            if unit is not None:
                current_unit = self.get_cutoffs_unit(stringency)
                values = {k: U.Quantity(v, current_unit).to(unit).to_tuple()[0] for k, v in cutoffs[element].items()}
            else:
                values = cutoffs[element]

            cutoffs_wfc.append(values['cutoff_wfc'])
            cutoffs_rho.append(values['cutoff_rho'])

        return (max(cutoffs_wfc), max(cutoffs_rho))
