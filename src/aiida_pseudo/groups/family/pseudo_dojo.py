# -*- coding: utf-8 -*-
"""Subclass of `PseudoPotentialFamily` designed to represent a PseudoDojo configuration."""
import json
import pathlib
import re
from typing import NamedTuple, Sequence
import warnings

from aiida.common.exceptions import ParsingError

from aiida_pseudo.data.pseudo import JthXmlData, PsmlData, Psp8Data, UpfData

from ..mixins import RecommendedCutoffMixin
from .pseudo import PseudoPotentialFamily

__all__ = ('PseudoDojoConfiguration', 'PseudoDojoFamily')


class PseudoDojoConfiguration(NamedTuple):
    """Named tuple that represents a PseudoDojo configuration."""

    version: str
    functional: str
    relativistic: str
    protocol: str
    pseudo_format: str

    def __str__(self):
        """Represent the configuration as a string."""
        return f'PseudoDojo v{self.version} {self.functional} {self.relativistic} {self.protocol} {self.pseudo_format}'


class PseudoDojoFamily(RecommendedCutoffMixin, PseudoPotentialFamily):
    """Subclass of ``PseudoPotentialFamily`` designed to represent a PseudoDojo configuration.

    The ``PseudoDojoFamily`` is essentially a ``PseudoPotentialFamily`` with some additional constraints. It can only
    be used to contain the pseudo potentials and corresponding metadata of an official PseudoDojo configuration.
    """

    _pseudo_types = (UpfData, PsmlData, Psp8Data, JthXmlData)
    _pseudo_repo_file_extensions = ('djrepo',)

    label_template = 'PseudoDojo/{version}/{functional}/{relativistic}/{protocol}/{pseudo_format}'
    default_configuration = PseudoDojoConfiguration('0.4', 'PBE', 'SR', 'standard', 'psp8')
    # yapf: disable
    valid_configurations = (
        PseudoDojoConfiguration('0.4', 'PBE', 'SR', 'standard', 'psp8'),
        PseudoDojoConfiguration('0.4', 'PBE', 'SR', 'stringent', 'psp8'),
        PseudoDojoConfiguration('0.4', 'PBEsol', 'SR', 'standard', 'psp8'),
        PseudoDojoConfiguration('0.4', 'PBEsol', 'SR', 'stringent', 'psp8'),
        PseudoDojoConfiguration('0.4', 'LDA', 'SR', 'standard', 'psp8'),
        PseudoDojoConfiguration('0.4', 'LDA', 'SR', 'stringent', 'psp8'),
        PseudoDojoConfiguration('0.4', 'PBE', 'SR3plus', 'standard', 'psp8'),
        PseudoDojoConfiguration('0.4', 'PBE', 'FR', 'standard', 'psp8'),
        PseudoDojoConfiguration('0.4', 'PBE', 'FR', 'stringent', 'psp8'),
        PseudoDojoConfiguration('0.4', 'PBEsol', 'FR', 'standard', 'psp8'),
        PseudoDojoConfiguration('0.4', 'PBEsol', 'FR', 'stringent', 'psp8'),
        PseudoDojoConfiguration('0.4', 'PBE', 'SR', 'standard', 'upf'),
        PseudoDojoConfiguration('0.4', 'PBE', 'SR', 'stringent', 'upf'),
        PseudoDojoConfiguration('0.4', 'PBEsol', 'SR', 'standard', 'upf'),
        PseudoDojoConfiguration('0.4', 'PBEsol', 'SR', 'stringent', 'upf'),
        PseudoDojoConfiguration('0.4', 'LDA', 'SR', 'standard', 'upf'),
        PseudoDojoConfiguration('0.4', 'LDA', 'SR', 'stringent', 'upf'),
        PseudoDojoConfiguration('0.4', 'PBE', 'SR3plus', 'standard', 'upf'),
        PseudoDojoConfiguration('0.4', 'PBE', 'FR', 'standard', 'upf'),
        PseudoDojoConfiguration('0.4', 'PBE', 'FR', 'stringent', 'upf'),
        PseudoDojoConfiguration('0.4', 'PBEsol', 'FR', 'standard', 'upf'),
        PseudoDojoConfiguration('0.4', 'PBEsol', 'FR', 'stringent', 'upf'),
        PseudoDojoConfiguration('0.4', 'PBE', 'SR', 'standard', 'psml'),
        PseudoDojoConfiguration('0.4', 'PBE', 'SR', 'stringent', 'psml'),
        PseudoDojoConfiguration('0.4', 'PBEsol', 'SR', 'standard', 'psml'),
        PseudoDojoConfiguration('0.4', 'PBEsol', 'SR', 'stringent', 'psml'),
        PseudoDojoConfiguration('0.4', 'LDA', 'SR', 'standard', 'psml'),
        PseudoDojoConfiguration('0.4', 'LDA', 'SR', 'stringent', 'psml'),
        PseudoDojoConfiguration('0.4', 'PBE', 'SR3plus', 'standard', 'psml'),
        PseudoDojoConfiguration('0.4', 'PBE', 'FR', 'standard', 'psml'),
        PseudoDojoConfiguration('0.4', 'PBE', 'FR', 'stringent', 'psml'),
        PseudoDojoConfiguration('0.4', 'PBEsol', 'FR', 'standard', 'psml'),
        PseudoDojoConfiguration('0.4', 'PBEsol', 'FR', 'stringent', 'psml'),
        PseudoDojoConfiguration('1.0', 'PBE', 'SR', 'standard', 'jthxml'),
        PseudoDojoConfiguration('1.0', 'PBE', 'SR', 'stringent', 'jthxml'),
        PseudoDojoConfiguration('1.0', 'LDA', 'SR', 'standard', 'jthxml'),
        PseudoDojoConfiguration('1.0', 'LDA', 'SR', 'stringent', 'jthxml')
    )
    # yapf: enable

    url_base = 'http://www.pseudo-dojo.org/pseudos/'
    urls = {
        'PseudoDojo/0.4/PBE/SR/standard/psp8': 'nc-sr-04_pbe_standard_psp8',
        'PseudoDojo/0.4/PBE/SR/stringent/psp8': 'nc-sr-04_pbe_stringent_psp8',
        'PseudoDojo/0.4/PBEsol/SR/standard/psp8': 'nc-sr-04_pbesol_standard_psp8',
        'PseudoDojo/0.4/PBEsol/SR/stringent/psp8': 'nc-sr-04_pbesol_stringent_psp8',
        'PseudoDojo/0.4/LDA/SR/standard/psp8': 'nc-sr-04_pw_standard_psp8',
        'PseudoDojo/0.4/LDA/SR/stringent/psp8': 'nc-sr-04_pw_stringent_psp8',
        'PseudoDojo/0.4/PBE/SR3plus/standard/psp8': 'nc-sr-04-3plus_pbe_standard_psp8',
        'PseudoDojo/0.4/PBE/FR/standard/psp8': 'nc-fr-04_pbe_standard_psp8',
        'PseudoDojo/0.4/PBE/FR/stringent/psp8': 'nc-fr-04_pbe_stringent_psp8',
        'PseudoDojo/0.4/PBEsol/FR/standard/psp8': 'nc-fr-04_pbesol_standard_psp8',
        'PseudoDojo/0.4/PBEsol/FR/stringent/psp8': 'nc-fr-04_pbesol_stringent_psp8',
        'PseudoDojo/0.4/PBE/SR/standard/upf': 'nc-sr-04_pbe_standard_upf',
        'PseudoDojo/0.4/PBE/SR/stringent/upf': 'nc-sr-04_pbe_stringent_upf',
        'PseudoDojo/0.4/PBEsol/SR/standard/upf': 'nc-sr-04_pbesol_standard_upf',
        'PseudoDojo/0.4/PBEsol/SR/stringent/upf': 'nc-sr-04_pbesol_stringent_upf',
        'PseudoDojo/0.4/LDA/SR/standard/upf': 'nc-sr-04_pw_standard_upf',
        'PseudoDojo/0.4/LDA/SR/stringent/upf': 'nc-sr-04_pw_stringent_upf',
        'PseudoDojo/0.4/PBE/SR3plus/standard/upf': 'nc-sr-04-3plus_pbe_standard_upf',
        'PseudoDojo/0.4/PBE/FR/standard/upf': 'nc-fr-04_pbe_standard_upf',
        'PseudoDojo/0.4/PBE/FR/stringent/upf': 'nc-fr-04_pbe_stringent_upf',
        'PseudoDojo/0.4/PBEsol/FR/standard/upf': 'nc-fr-04_pbesol_standard_upf',
        'PseudoDojo/0.4/PBEsol/FR/stringent/upf': 'nc-fr-04_pbesol_stringent_upf',
        'PseudoDojo/0.4/PBE/SR/standard/psml': 'nc-sr-04_pbe_standard_psml',
        'PseudoDojo/0.4/PBE/SR/stringent/psml': 'nc-sr-04_pbe_stringent_psml',
        'PseudoDojo/0.4/PBEsol/SR/standard/psml': 'nc-sr-04_pbesol_standard_psml',
        'PseudoDojo/0.4/PBEsol/SR/stringent/psml': 'nc-sr-04_pbesol_stringent_psml',
        'PseudoDojo/0.4/LDA/SR/standard/psml': 'nc-sr-04_pw_standard_psml',
        'PseudoDojo/0.4/LDA/SR/stringent/psml': 'nc-sr-04_pw_stringent_psml',
        'PseudoDojo/0.4/PBE/SR3plus/standard/psml': 'nc-sr-04-3plus_pbe_standard_psml',
        'PseudoDojo/0.4/PBE/FR/standard/psml': 'nc-fr-04_pbe_standard_psml',
        'PseudoDojo/0.4/PBE/FR/stringent/psml': 'nc-fr-04_pbe_stringent_psml',
        'PseudoDojo/0.4/PBEsol/FR/standard/psml': 'nc-fr-04_pbesol_standard_psml',
        'PseudoDojo/0.4/PBEsol/FR/stringent/psml': 'nc-fr-04_pbesol_stringent_psml',
        'PseudoDojo/1.0/PBE/SR/standard/jthxml': 'paw_pbe_standard_xml',
        'PseudoDojo/1.0/PBE/SR/stringent/jthxml': 'paw_pbe_stringent_xml',
        'PseudoDojo/1.0/LDA/SR/standard/jthxml': 'paw_pw_standard_xml',
        'PseudoDojo/1.0/LDA/SR/stringent/jthxml': 'paw_pw_stringent_xml',
    }

    @classmethod
    def get_valid_labels(cls) -> Sequence[str]:
        """Return the tuple of labels of all valid PseudoDojo configurations."""
        configurations = set(cls.valid_configurations)
        return tuple(cls.format_configuration_label(configuration) for configuration in configurations)

    @classmethod
    def format_configuration_label(cls, configuration: PseudoDojoConfiguration) -> str:
        """Format a label for an `PseudoDojoFamily` with the required syntax.

        :param configuration: the PseudoDojo configuration.
        :return: label.
        """
        return cls.label_template.format(
            version=configuration.version,
            functional=configuration.functional,
            relativistic=configuration.relativistic,
            protocol=configuration.protocol,
            pseudo_format=configuration.pseudo_format,
        )

    @classmethod
    def get_url_archive(cls, label):
        """Return the URL for the pseudopotential archive file for a given family label.

        :param label: the family label as formatted by ``format_configuration_label``.
        :return: the URL from which the pseudopotential archive can be downloaded.
        :raises: `ValueError` if the label is not a valid configuration label.
        """
        try:
            url_prefix = cls.urls[label]
        except KeyError as exception:
            raise ValueError(f'label {label} is not a valid PseudoDojo configuration label.') from exception

        return cls.url_base + url_prefix + '.tgz'

    @classmethod
    def get_url_metadata(cls, label):
        """Return the URL for the pseudopotential metadata file for a given family label.

        :param label: the family label as formatted by ``format_configuration_label``.
        :return: the URL from which the pseudopotential metadata can be downloaded.
        :raises: `ValueError` if the label is not a valid configuration label.
        """
        try:
            url_prefix = cls.urls[label]
        except KeyError as exception:
            raise ValueError(f'label {label} is not a valid PseudoDojo configuration label.') from exception

        # For the metadata URL, the final underscored part of the prefix (the pseudo format) is replaced with `_djrepo`.
        url_prefix = '_'.join(url_prefix.split('_')[:-1] + ['djrepo'])

        return cls.url_base + url_prefix + '.tgz'

    @classmethod
    def get_md5_from_djrepo(cls, djrepo, pseudo_type):
        """Get the appropriate md5 hash from a DJREPO file.

        :param djrepo: dictionary loaded from DJREPO JSON file.
        :reutnrs: md5 string.
        """
        md5_key_mapping = {UpfData: 'md5_upf', Psp8Data: 'md5', PsmlData: 'md5_psml', JthXmlData: 'md5'}

        try:
            md5_key = md5_key_mapping[pseudo_type]
        except KeyError as exception:
            raise ValueError(
                f'pseudo type `{pseudo_type}` is unsupported by PseudoDojo djrepos: {exception}'
            ) from exception

        try:
            md5 = djrepo[md5_key]
        except KeyError as exception:
            raise ParsingError(f'key `{cls.md5_key}` is not defined in the djrepo: {exception}') from exception

        return md5

    @classmethod
    def get_cutoffs_from_djrepo(cls, djrepo, pseudo_type):
        """Collect and organize the suggested cutoffs (hints) from a DJREPO file.

        DJREPO files only provide a kinetic energy cutoff, so for pseudo types which contain norm-conserving pseudos
        from PseudoDojo, we use a dual of 8.0 to generate the charge density (rho) cutoff.

        For PAW potentials from PseudoDojo (which are assumed to be JthXmlData), a dual of 2.0 is used.

        The cutoffs in DJREPO files are given in Hartree, which is converted to eV.

        :param djrepo: dictionary loaded from DJREPO JSON file
        :returns: cutoffs dictionary (in eV) where keys are stringency levels and values are
            {'cutoff_wfc': ..., 'cutoff_rho': ...}
        """
        dual_mapping = {UpfData: 4.0, Psp8Data: 4.0, PsmlData: 4.0, JthXmlData: 2.0}

        try:
            dual = dual_mapping[pseudo_type]
        except KeyError as exception:
            raise ValueError(
                f'cannot get cutoffs for pseudo type `{pseudo_type}` because the appropriate dual '
                'for generating density cutoffs is unknown'
            ) from exception

        cutoffs = {}

        try:
            hints = djrepo['hints']
        except KeyError as exception:
            raise ParsingError('key `hints` is not defined in the djrepo.') from exception

        for stringency in ['low', 'normal', 'high']:

            try:
                ecutwfc = hints.get(stringency, {})['ecut']
            except KeyError as exception:
                raise ParsingError(f'stringency `{stringency}` is not defined in the djrepo `hints`') from exception

            cutoffs[stringency] = {'cutoff_wfc': ecutwfc, 'cutoff_rho': ecutwfc * dual}

        return cutoffs

    @classmethod
    def parse_djrepos_from_folder(cls, dirpath: pathlib.Path, pseudo_type):
        # pylint: disable=too-many-locals,too-many-branches
        """Parse the djrepo files in the given directory into a list of data nodes.

        .. note:: The directory pointed to by `dirpath` should only contain djrepo files. Optionally, it can contain
            just a single directory, that contains all the djrepo files. If any other files are stored in the basepath
            or the subdirectory that cannot be successfully parsed as djrepo files the method will raise a `ValueError`.

        :param dirpath: absolute path to a directory containing djrepos.
        :return: list of data nodes.
        :raises ValueError: if `dirpath` is not a directory or contains anything other than files.
        :raises ValueError: if `dirpath` contains multiple djrepos for the same element.
        :raises ParsingError: if the constructor of the pseudo type fails for one of the files in the `dirpath`.
        """
        md5s = {}
        cutoffs = {'low': {}, 'normal': {}, 'high': {}}
        elements = []

        dirpath = cls._validate_dirpath(dirpath)

        for filepath in dirpath.iterdir():

            filename = filepath.name

            if not filepath.is_file():
                raise ValueError(f'dirpath `{dirpath}` contains at least one entry that is not a file: {filepath}')

            # Some of the djrepo archives contain extraneous files. Here we skip files with unsupported extensions.
            if filename.split('.')[-1] not in cls._pseudo_repo_file_extensions:
                warnings.warn(f'filename {filename} does not have a supported extension. Skipping...')
                continue

            try:
                with open(filepath, 'r', encoding='utf-8') as handle:
                    djrepo = json.load(handle)
            except ParsingError as exception:
                raise ParsingError(f'failed to parse `{filepath}`: {exception}') from exception
            else:
                match = re.search(r'^([A-Za-z]{1,2})\.\w+', filename)
                if match is None:
                    raise ParsingError(
                        f'could not parse a valid element symbol from the filename `{filename}`. '
                        'It should have the format `ELEMENT.EXTENSION`'
                    )
                element = match.group(1)
                if element in elements:
                    raise ValueError(f'directory `{dirpath}` contains djrepos with duplicate elements`')

                try:
                    md5 = cls.get_md5_from_djrepo(djrepo, pseudo_type=pseudo_type)
                except (ParsingError, ValueError) as exception:
                    raise ParsingError(f'failed to parse md5 from djrepo file `{filename}`: {exception}') from exception
                else:
                    md5s[element] = md5

                try:
                    djrepo_cutoffs = cls.get_cutoffs_from_djrepo(djrepo, pseudo_type=pseudo_type)
                except ParsingError as exception:
                    raise ParsingError(
                        f'failed to parse cutoffs from djrepo file `{filename}`: {exception}'
                    ) from exception
                else:
                    for stringency in ['low', 'normal', 'high']:
                        cutoffs[stringency][element] = djrepo_cutoffs[stringency]

                elements.append(element)

        if (not cutoffs['low']) and (not cutoffs['normal']) and (not cutoffs['high']):
            raise ValueError(f'no djrepos were parsed from `{dirpath}`')

        return md5s, cutoffs

    @classmethod
    def parse_djrepos_from_archive(cls, filepath_metadata: pathlib.Path, fmt=None, pseudo_type=None):
        """Parse metadata from a djrepo .tgz archive.

        .. warning:: the archive should not contain any subdirectories, but just the djrepo files.

        :param filepath_metadata: the path to the metadata .tgz archive.
        :param fmt: the format of the archive, if not specified will attempt to guess based on extension of `filepath`.
        :param pseudo_type: subclass of ``PseudoPotentialData`` to be used for the parsed pseudos. If not specified and
            the family only defines a single supported pseudo type in ``_pseudo_types`` then that will be used otherwise
            a ``ValueError`` is raised.
        :return: element: value dictionaries containing md5s and cutoffs.
        :raises OSError: if the archive could not be unpacked or the djrepos in it could not be parsed into md5s and
            cutoffs.
        """
        import shutil
        import tempfile

        with tempfile.TemporaryDirectory() as dirpath:
            try:
                shutil.unpack_archive(filepath_metadata, dirpath, format=fmt)
            except shutil.ReadError as exception:
                raise OSError(
                    f'failed to unpack the metadata archive `{filepath_metadata}`: {exception}'
                ) from exception

            try:
                md5s, cutoffs = cls.parse_djrepos_from_folder(pathlib.Path(dirpath), pseudo_type=pseudo_type)
            except ValueError as exception:
                raise OSError(f'failed to parse djrepos from `{dirpath}`: {exception}') from exception

        return md5s, cutoffs

    def __init__(self, label=None, **kwargs):
        """Construct a new instance, validating that the label matches the required format."""
        if label not in self.get_valid_labels():
            raise ValueError(f'the label `{label}` is not a valid PseudoDojo configuration label.')

        super().__init__(label=label, **kwargs)
