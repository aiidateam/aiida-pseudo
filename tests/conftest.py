"""Configuration and fixtures for unit test suite."""
import io
import os
import pathlib
import re
import shutil

import click
import pytest
from aiida.plugins import DataFactory
from aiida_pseudo.data.pseudo import PseudoPotentialData
from aiida_pseudo.groups.family import CutoffsPseudoPotentialFamily, PseudoPotentialFamily

pytest_plugins = 'aiida.tools.pytest_fixtures'


@pytest.fixture
def ctx():
    """Return an empty `click.Context` instance."""
    return click.Context(click.Command(name='dummy'))


@pytest.fixture
def chdir_tmp_path(tmp_path):
    """Change the current working directory to a temporary directory."""
    cwd = pathlib.Path.cwd()
    os.chdir(tmp_path)
    try:
        yield
    finally:
        os.chdir(cwd)


@pytest.fixture
def run_cli_command():
    """Run a `click` command with the given options.

    The call will raise if the command triggered an exception or the exit code returned is non-zero.
    """

    def _run_cli_command(command, options=None, raises=None):
        """Run the command and check the result.

        :param command: the command to invoke
        :param options: the list of command line options to pass to the command invocation
        :param raises: optionally an exception class that is expected to be raised
        """
        import traceback

        from click.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(command, options or [])

        if raises is not None:
            assert result.exception is not None, result.output
            assert result.exit_code != 0
        else:
            assert result.exception is None, ''.join(traceback.format_exception(*result.exc_info))
            assert result.exit_code == 0, result.output

        result.output_lines = [line.strip() for line in result.output.split('\n') if line.strip()]

        return result

    return _run_cli_command


@pytest.fixture
def filepath_fixtures() -> pathlib.Path:
    """Return the absolute filepath to the directory containing the file `fixtures`.

    :return: absolute filepath to directory containing test fixture data.
    """
    return pathlib.Path(__file__).parent.resolve() / 'fixtures'


@pytest.fixture
def filepath_pseudos(filepath_fixtures):
    """Return the absolute filepath to the directory containing the pseudo potential files.

    :return: absolute filepath to directory containing test pseudo potentials.
    """

    def _filepath_pseudos(entry_point='upf') -> pathlib.Path:
        """Return the absolute filepath containing the pseudo potential files for a given entry point.

        :param entry_point: pseudo potential data entry point
        :return: filepath to folder containing pseudo files.
        """
        return filepath_fixtures / 'pseudos' / entry_point

    return _filepath_pseudos


@pytest.fixture
def get_pseudo_potential_data(filepath_pseudos):
    """Return a factory for `PseudoPotentialData` nodes."""

    def _get_pseudo_potential_data(element='Ar', entry_point=None) -> PseudoPotentialData:
        """Return a `PseudoPotentialData` for the given element.

        :param element: one of the elements for which there is a UPF test file available.
        :return: the `PseudoPotentialData`
        """
        if entry_point is None:
            cls = DataFactory('pseudo')
            content = f'<UPF version="2.0.1"><PP_HEADER\nelement="{element}"\nz_valence="4.0"\n/></UPF>\n'
            pseudo = cls(io.BytesIO(content.encode('utf-8')), f'{element}.pseudo')
            pseudo.element = element
        else:
            cls = DataFactory(f'pseudo.{entry_point}')
            filename = f'{element}.{entry_point}'
            with (filepath_pseudos(entry_point) / filename).open('rb') as handle:
                pseudo = cls(handle, filename)

        return pseudo

    return _get_pseudo_potential_data


@pytest.fixture
def generate_cutoffs():
    """Return a dictionary of cutoffs for all elements in a given family."""

    def _generate_cutoffs(family):
        """Return a dictionary of cutoffs for a given family."""
        return {element: {'cutoff_wfc': 1.0, 'cutoff_rho': 2.0} for element in family.elements}

    return _generate_cutoffs


@pytest.fixture
def generate_cutoffs_dict(generate_cutoffs):
    """Return a dictionary of cutoffs for a given family with specified stringencies."""

    def _generate_cutoffs_dict(family, stringencies=('normal',)):
        """Return a dictionary of cutoffs for a given family."""
        cutoffs_dict = {}

        for stringency in stringencies:
            cutoffs_dict[stringency] = generate_cutoffs(family)

        return cutoffs_dict

    return _generate_cutoffs_dict


@pytest.fixture
def get_pseudo_family(tmp_path, filepath_pseudos):
    """Return a factory for a ``PseudoPotentialFamily`` instance."""

    def _get_pseudo_family(
        label='family',
        cls=PseudoPotentialFamily,
        pseudo_type=PseudoPotentialData,
        elements=None,
        cutoffs_dict=None,
        unit=None,
        default_stringency=None,
    ) -> PseudoPotentialFamily:
        """Return an instance of `PseudoPotentialFamily` or subclass containing the given elements.

        :param elements: optional list of elements to include instead of all the available ones
        :params cutoffs_dict: optional dictionary of cutoffs to specify. Format: multiple sets of cutoffs can be
            specified where the key represents the stringency, e.g. ``low`` or ``normal``. For each stringency, a
            dictionary should be defined that for each element symbols for which the family contains a pseudopotential,
            two values are specified, ``cutoff_wfc`` and ``cutoff_rho``, containing a float value with the recommended
            cutoff to be used for the wave functions and charge density, respectively..
        :param unit: string definition of a unit of energy as recognized by the ``UnitRegistry`` of the ``pint`` lib.
        :param default_stringency: string with the default stringency name, if not specified, the first one specified in
            the ``cutoffs`` argument will be used if specified.
        :return: the pseudo family
        """
        if elements is not None:
            elements = {re.sub('[0-9]+', '', element) for element in elements}

        if pseudo_type is PseudoPotentialData:
            # There is no actual pseudopotential file fixtures for the base class, so default back to `.upf` files
            extension = 'upf'
        else:
            extension = pseudo_type.get_entry_point_name()[len('pseudo.') :]

        dirpath = filepath_pseudos(extension)

        for pseudo in dirpath.iterdir():
            if elements is None or any(pseudo.name.startswith(element) for element in elements):
                shutil.copyfile(pseudo, tmp_path / pseudo.name)

        family = cls.create_from_folder(tmp_path, label, pseudo_type=pseudo_type)

        if cutoffs_dict is not None and isinstance(family, CutoffsPseudoPotentialFamily):
            default_stringency = default_stringency or next(iter(cutoffs_dict.keys()))
            for stringency, cutoff_values in cutoffs_dict.items():
                family.set_cutoffs(cutoff_values, stringency, unit)
            family.set_default_stringency(default_stringency)

        return family

    return _get_pseudo_family


@pytest.fixture
def get_pseudo_archive(tmp_path, filepath_pseudos):
    """Create an archive with pseudos."""

    def _get_pseudo_archive(fmt='gztar'):
        shutil.make_archive(tmp_path / 'archive', fmt, filepath_pseudos('upf'))
        # The created archive should be the only file in ``tmp_path`` so just get first entry from the iterator.
        return next(iter(tmp_path.iterdir()))

    return _get_pseudo_archive


@pytest.fixture
def generate_structure():
    """Return a ``StructureData``."""

    def _generate_structure(elements=('Ar',)):
        """Return a ``StructureData``."""
        from aiida.orm import StructureData

        structure = StructureData(cell=[[1, 0, 0], [0, 1, 0], [0, 0, 1]])

        for index, element in enumerate(elements):
            symbol = re.sub(r'[0-9]+', '', element)
            structure.append_atom(position=(index * 0.5, index * 0.5, index * 0.5), symbols=symbol, name=element)

        return structure

    return _generate_structure
