# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name,unused-argument
"""Configuration and fixtures for unit test suite."""
import os
import shutil

import pytest

from aiida_pseudo.data.pseudo import PseudoPotentialData, UpfData
from aiida_pseudo.groups.family import PseudoPotentialFamily

pytest_plugins = ['aiida.manage.tests.pytest_fixtures']  # pylint: disable=invalid-name


@pytest.fixture
def clear_db(clear_database_before_test):
    """Alias for the `clear_database_before_test` fixture from `aiida-core`."""
    yield


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
def filepath_pseudos(filepath_fixtures) -> str:
    """Return the absolute filepath to the directory containing the pseudo potential files.

    :return: absolute filepath to directory containing test pseudo potentials.
    """
    return os.path.join(filepath_fixtures, 'pseudos')


@pytest.fixture
def get_upf_data(filepath_pseudos):
    """Return a factory for `UpfData` nodes."""

    def _get_upf_data(element='Ar') -> UpfData:
        """Return a `UpfData` for the given element.

        :param element: one of the elements for which there is a UPF test file available.
        :return: the `UpfData`
        """
        filename = '{}.upf'.format(element)
        with open(os.path.join(filepath_pseudos, filename), 'rb') as handle:
            return UpfData(handle, filename)

    return _get_upf_data


@pytest.fixture
def get_pseudo_potential_data(filepath_pseudos):
    """Return a factory for `PseudoPotentialData` nodes."""

    def _get_pseudo_potential_data(element='Ar') -> PseudoPotentialData:
        """Return a `PseudoPotentialData` for the given element.

        :param element: one of the elements for which there is a UPF test file available.
        :return: the `PseudoPotentialData`
        """
        filename = '{}.upf'.format(element)
        with open(os.path.join(filepath_pseudos, filename), 'rb') as handle:
            pseudo = PseudoPotentialData(handle, filename)
            pseudo.element = element
            return pseudo

    return _get_pseudo_potential_data


@pytest.fixture
def get_pseudo_family(tmpdir, filepath_pseudos):
    """Return a factory for a `PseudoPotentialFamily` instance."""

    def _get_pseudo_family(label='family', cls=PseudoPotentialFamily, elements=None) -> PseudoPotentialFamily:
        """Return an instance of `PseudoPotentialFamily` or subclass containing the given elements.

        :param elements: optional list of elements to include instead of all the available ones
        :return: the pseudo family
        """
        for pseudo in os.listdir(filepath_pseudos):
            if elements is None or any([pseudo.startswith(element) for element in elements]):
                shutil.copyfile(os.path.join(filepath_pseudos, pseudo), os.path.join(str(tmpdir), pseudo))

        return cls.create_from_folder(str(tmpdir), label)

    return _get_pseudo_family
