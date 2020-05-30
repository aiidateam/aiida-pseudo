# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""Configuration and fixtures for unit test suite."""
import os

import pytest

from aiida_pseudo.data.pseudo import UpfData

pytest_plugins = ['aiida.manage.tests.pytest_fixtures']


@pytest.fixture
@pytest.mark.usefixtures('clear_database_before_test')
def clear_db():
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
        with open(os.path.join(filepath_pseudos, '{}.upf'.format(element)), 'rb') as handle:
            return UpfData(handle)

    return _get_upf_data
