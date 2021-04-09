# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-position,wildcard-import
"""Module for the command line interface."""
import click_completion

# Activate the completion of parameter types provided by the click_completion package
click_completion.init()

from .root import cmd_root
from .family import cmd_family
from .install import cmd_install, cmd_install_family, cmd_install_sssp, cmd_install_pseudo_dojo
from .list import cmd_list
