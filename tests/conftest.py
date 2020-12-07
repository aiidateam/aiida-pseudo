# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name,unused-argument
"""Configuration and fixtures for unit test suite."""
import io
import os
import re
import shutil

import click
import pytest

from aiida.plugins import DataFactory

from aiida_pseudo.data.pseudo import PseudoPotentialData
from aiida_pseudo.groups.family import PseudoPotentialFamily

pytest_plugins = ['aiida.manage.tests.pytest_fixtures']  # pylint: disable=invalid-name


@pytest.fixture
def clear_db(clear_database_before_test):
    """Alias for the `clear_database_before_test` fixture from `aiida-core`."""
    yield


@pytest.fixture
def ctx():
    """Return an empty `click.Context` instance."""
    return click.Context(click.Command(name='dummy'))


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
def filepath_fixtures() -> str:
    """Return the absolute filepath to the directory containing the file `fixtures`.

    :return: absolute filepath to directory containing test fixture data.
    """
    return os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.fixture
def filepath_pseudos(filepath_fixtures):
    """Return the absolute filepath to the directory containing the pseudo potential files.

    :return: absolute filepath to directory containing test pseudo potentials.
    """

    def _filepath_pseudos(entry_point='upf') -> str:
        """Return the absolute filepath containing the pseudo potential files for a given entry point.

        :param entry_point: pseudo potential data entry point
        :return: filepath to folder containing pseudo files.
        """
        return os.path.join(filepath_fixtures, 'pseudos', entry_point)

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
            pseudo = cls(io.BytesIO(b'content'), f'{element}.pseudo')
            pseudo.element = element
        else:
            cls = DataFactory(f'pseudo.{entry_point}')
            filename = f'{element}.{entry_point}'
            with open(os.path.join(filepath_pseudos(entry_point), filename), 'rb') as handle:
                pseudo = cls(handle, filename)

        return pseudo

    return _get_pseudo_potential_data


@pytest.fixture
def get_pseudo_family(tmpdir, filepath_pseudos):
    """Return a factory for a `PseudoPotentialFamily` instance."""

    def _get_pseudo_family(
        label='family',
        cls=PseudoPotentialFamily,
        pseudo_type=PseudoPotentialData,
        elements=None
    ) -> PseudoPotentialFamily:
        """Return an instance of `PseudoPotentialFamily` or subclass containing the given elements.

        :param elements: optional list of elements to include instead of all the available ones
        :return: the pseudo family
        """
        if elements is not None:
            elements = {re.sub('[0-9]+', '', element) for element in elements}

        if pseudo_type is PseudoPotentialData:
            # There is no actual pseudopotential file fixtures for the base class, so default back to `.upf` files
            extension = 'upf'
        else:
            extension = pseudo_type.get_entry_point_name()[len('pseudo.'):]

        dirpath = filepath_pseudos(extension)

        for pseudo in os.listdir(dirpath):
            if elements is None or any([pseudo.startswith(element) for element in elements]):
                shutil.copyfile(os.path.join(dirpath, pseudo), os.path.join(str(tmpdir), pseudo))

        return cls.create_from_folder(str(tmpdir), label, pseudo_type=pseudo_type)

    return _get_pseudo_family


@pytest.fixture
def get_pseudo_archive(tmpdir, filepath_pseudos):
    """Create an archive with pseudos."""

    def _get_pseudo_archive(fmt='gztar'):
        shutil.make_archive(str(tmpdir / 'archive'), fmt, filepath_pseudos('upf'))
        filepath = os.path.join(str(tmpdir), os.listdir(str(tmpdir))[0])
        yield filepath

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
