"""Module for the command line interface."""
from .family import cmd_family  # noqa: F401
from .install import cmd_install, cmd_install_family, cmd_install_pseudo_dojo, cmd_install_sssp  # noqa: F401
from .list import cmd_list  # noqa: F401
from .root import cmd_root  # noqa: F401
