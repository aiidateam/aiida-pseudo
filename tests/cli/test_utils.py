# -*- coding: utf-8 -*-
# pylint: disable=unused-argument
"""Test the command line interface utilities."""
import shutil
import tarfile
import tempfile

import pytest

from aiida_pseudo.cli.utils import attempt, create_family_from_archive
from aiida_pseudo.groups.family import PseudoPotentialFamily


@pytest.mark.usefixtures('clear_db')
@pytest.mark.parametrize(('fmt',), [(fmt[0],) for fmt in shutil.get_archive_formats()])
def test_create_family_from_archive(get_pseudo_archive, fmt):
    """Test the `create_family_from_archive` utility function."""
    label = 'PSEUDO/0.0/LDA/extreme'
    filepath_archive = next(get_pseudo_archive(fmt))
    family = create_family_from_archive(PseudoPotentialFamily, label, filepath_archive, fmt=fmt)

    assert isinstance(family, PseudoPotentialFamily)
    assert family.label == label
    assert family.count() != 0


@pytest.mark.usefixtures('clear_db')
def test_create_family_from_archive_incorrect_filetype(tmpdir):
    """Test the `create_family_from_archive` utility function for incorrect archive filetype."""
    with pytest.raises(OSError, match=r'failed to unpack the archive.*'):
        create_family_from_archive(PseudoPotentialFamily, 'label', str(tmpdir))


@pytest.mark.usefixtures('clear_db')
def test_create_family_from_archive_incorrect_format(tmpdir):
    """Test the `create_family_from_archive` utility function for invalid archive content."""
    with tempfile.NamedTemporaryFile(suffix='.tar.gz') as filepath_archive:

        with tarfile.open(filepath_archive.name, 'w:gz') as tar:
            tar.add(str(tmpdir), arcname='.')

        with pytest.raises(OSError, match=r'failed to parse pseudos from.*'):
            create_family_from_archive(PseudoPotentialFamily, 'label', filepath_archive.name)


def test_attempt_sucess(capsys):
    """Test the `attempt` utility function."""
    message = 'some message'

    with attempt(message):
        pass

    captured = capsys.readouterr()
    assert captured.out == f'Info: {message} [OK]\n'
    assert captured.err == ''


def test_attempt_exception(capsys):
    """Test the `attempt` utility function when exception is raised."""
    message = 'some message'
    exception = 'run-time-error'

    with pytest.raises(SystemExit):
        with attempt(message):
            raise RuntimeError(exception)

    captured = capsys.readouterr()
    assert captured.out == f'Info: {message} [FAILED]\n'
    assert captured.err == f'Critical: {exception}\n'


def test_attempt_exception_traceback(capsys):
    """Test the `attempt` utility function when exception is raised and `include_traceback=True`."""
    message = 'some message'
    exception = 'run-time-error'

    with pytest.raises(SystemExit):
        with attempt(message, include_traceback=True):
            raise RuntimeError(exception)

    captured = capsys.readouterr()
    assert captured.out == f'Info: {message} [FAILED]\n'
    assert captured.err.startswith(f'Critical: {exception}\n')
    assert 'Traceback' in captured.err
