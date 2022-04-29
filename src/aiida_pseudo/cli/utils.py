# -*- coding: utf-8 -*-
"""Command line interface utilities."""
from contextlib import contextmanager
from pathlib import Path

from aiida.cmdline.utils import echo

__all__ = ('attempt', 'create_family_from_archive')


@contextmanager
def attempt(message, exception_types=Exception, include_traceback=False):
    """Context manager to be used to wrap statements in CLI that can throw exceptions.

    :param message: the message to print before yielding
    :param include_traceback: boolean, if True, will also print traceback if an exception is caught
    """
    import sys
    import traceback

    echo.echo_report(message, nl=False)

    try:
        yield
    except exception_types as exception:  # pylint: disable=broad-except
        echo.echo(' [FAILED]', fg='red', bold=True)
        message = str(exception)
        if include_traceback:
            message += f"\n{''.join(traceback.format_exception(*sys.exc_info()))}"
        echo.echo_critical(message)
    else:
        echo.echo(' [OK]', fg='green', bold=True)


def create_family_from_archive(cls, label, filepath_archive: Path, fmt=None, pseudo_type=None):
    """Construct a new pseudo family instance from a tar.gz archive.

    .. warning:: the archive should not contain any subdirectories, but just the pseudo potential files.

    :param cls: the pseudopotential family class to use, e.g. ``SsspFamily``
    :param label: the label for the new family
    :param filepath_archive: absolute filepath to the .tar.gz archive containing the pseudo potentials
    :param fmt: the format of the archive, if not specified will attempt to guess based on extension of ``filepath``
    :param pseudo_type: subclass of ``PseudoPotentialData`` to be used for the parsed pseudos. If not specified and
        the family only defines a single supported pseudo type in ``_pseudo_types`` then that will be used otherwise
        a ``ValueError`` is raised.
    :return: newly created family
    :raises OSError: if the archive could not be unpacked or pseudos in it could not be parsed into a family
    """
    import shutil
    import tempfile

    with tempfile.TemporaryDirectory() as dirpath:

        try:
            shutil.unpack_archive(filepath_archive, dirpath, format=fmt)
        except shutil.ReadError as exception:
            raise OSError(f'failed to unpack the archive `{filepath_archive}`: {exception}') from exception

        try:
            family = cls.create_from_folder(Path(dirpath), label, pseudo_type=pseudo_type)
        except ValueError as exception:
            raise OSError(f'failed to parse pseudos from `{dirpath}`: {exception}') from exception

    return family
