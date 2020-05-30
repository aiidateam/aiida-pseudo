# -*- coding: utf-8 -*-
"""Test the root command of the CLI."""
from aiida_pseudo.cli import cmd_root


def test_root(run_cli_command):
    """Test the root command for the CLI is callable."""
    run_cli_command(cmd_root)

    for option in ['-h', '--help']:
        result = run_cli_command(cmd_root, [option])
        assert cmd_root.__doc__ in result.output
