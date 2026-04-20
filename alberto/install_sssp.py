#!/usr/bin/env python
"""Install SSSP pseudopotential family from local archive and cutoffs JSON."""
import json
import pathlib
import sys

from aiida import load_profile
from aiida.orm import Group
from aiida_pseudo.groups.family.sssp import SsspFamily


LABEL = 'SSSP/2.0/PBEsol/precision'
DESCRIPTION = 'SSSP v2.0 PBEsol precision (installed from local archive).'

HERE = pathlib.Path(__file__).parent
PSEUDO_DIR = HERE / 'pseudos_dir'
CUTOFFS = HERE / 'cutoffs.json'


def main():
    load_profile()

    if Group.collection.find(filters={'label': LABEL}):
        sys.exit(f'family `{LABEL}` already installed.')

    cutoffs_data = json.loads(CUTOFFS.read_text())
    family = SsspFamily.create_from_folder(PSEUDO_DIR, LABEL, description=DESCRIPTION)

    family.description = DESCRIPTION
    family.set_cutoffs(
        {el: {'cutoff_wfc': v['cutoff_wfc'], 'cutoff_rho': v['cutoff_rho']}
         for el, v in cutoffs_data.items() if el in family.elements},
        'normal',
        unit='Ry',
    )

    print(f'installed `{LABEL}` with {family.count()} pseudopotentials.')

if __name__ == '__main__':
    main()
