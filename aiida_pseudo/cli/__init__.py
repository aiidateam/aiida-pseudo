# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-position,wildcard-import
"""Module for the command line interface."""
import click_completion

# Activate the completion of parameter types provided by the click_completion package
click_completion.init()

from .family import cmd_family
from .install import cmd_install, cmd_install_family, cmd_install_pseudo_dojo, cmd_install_sssp
from .list import cmd_list
from .root import cmd_root
