# -*- coding: utf-8 -*-
"""Tests for the :py:`~aiida_pseudo.data.pseudo.upf` module."""
import os

import pytest

from aiida.common.exceptions import ModificationNotAllowed
from aiida_pseudo.data.pseudo import UpfData


@pytest.mark.usefixtures('clear_db')
def test_constructor(filepath_pseudos):
    """Test the constructor."""
    for filename in os.listdir(filepath_pseudos):
        with open(os.path.join(filepath_pseudos, filename), 'rb') as handle:
            upf = UpfData(handle, filename=filename)
            assert isinstance(upf, UpfData)
            assert not upf.is_stored
            assert upf.element == filename.split('.')[0]


@pytest.mark.usefixtures('clear_db')
def test_set_file(filepath_pseudos, get_upf_data):
    """Test the `UpfData.set_file` method.

    This method allows to change the file, as long as the node has not been stored yet. We need to verify that all the
    information, such as attributes are commensurate when it is stored.
    """
    upf = get_upf_data(element='Ar')
    assert upf.element == 'Ar'

    with open(os.path.join(filepath_pseudos, 'He.upf'), 'rb') as handle:
        upf.set_file(handle)
        assert upf.element == 'He'

        upf.store()
        assert upf.element == 'He'

        with pytest.raises(ModificationNotAllowed):
            upf.set_file(handle)
