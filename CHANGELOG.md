# Change log

## `0.9.0` - 2023-01-05

### Features

- Add support for SSSP v1.2 [[#144]](https://github.com/aiidateam/aiida-pseudo/pull/144)

## `0.8.0` - 2022-11-08

### Features
- `PsmlData`: add parsing of Z-valence from file [[#125]](https://github.com/aiidateam/aiida-pseudo/pull/125)
- CLI: reduce the load time significantly [[#142]](https://github.com/aiidateam/aiida-pseudo/pull/142)
- CLI: filter cutoffs from JSON file for family cutoffs set [[#132]](https://github.com/aiidateam/aiida-pseudo/pull/132)
- CLI: block family cutoffs set for established families [[#134]](https://github.com/aiidateam/aiida-pseudo/pull/134)

### Dependencies
- Update to be compatible with `aiida-core~=2.1` [[#136]](https://github.com/aiidateam/aiida-pseudo/pull/136)
- Add support for Python 3.11 [[#139]](https://github.com/aiidateam/aiida-pseudo/pull/139)

### Devops
- Update all `pre-commit` dependencies [[#124]](https://github.com/aiidateam/aiida-pseudo/pull/124)
- Update dependency `pylint==2.15.5` [[#137]](https://github.com/aiidateam/aiida-pseudo/pull/137)
- Refactor: remove use of deprecated `distutils` module [[#126]](https://github.com/aiidateam/aiida-pseudo/pull/126)
- Refactor: replace `tmpdir` fixture with `tmp_path` [[#127]](https://github.com/aiidateam/aiida-pseudo/pull/127)
- Refactor: remove use of `os.path` in favor of `pathlib` [[#128]](https://github.com/aiidateam/aiida-pseudo/pull/128)
- Docs: remove manual addition of package to `sys.path` [[#129]](https://github.com/aiidateam/aiida-pseudo/pull/129)
- Docs: add acknowledgements [[#133]](https://github.com/aiidateam/aiida-pseudo/pull/133)
- Tests: address warnings [[#138]](https://github.com/aiidateam/aiida-pseudo/pull/138)


## `0.7.0` - 2022-04-28

### Fixes
- CLI: Fix bug in `install family` when downloading from URL [[#110]](https://github.com/aiidateam/aiida-pseudo/pull/110)
- CLI: Replace SSSP link to legacy MC Archive [[#110]](https://github.com/aiidateam/aiida-pseudo/pull/110)

## Changes
- Use `typing.NamedTuple` for pseudo family configurations [[#111]](https://github.com/aiidateam/aiida-pseudo/pull/111)

### Dependencies
- Add compatibility with `aiida-core==2.0` [[#120]](https://github.com/aiidateam/aiida-pseudo/pull/120)
- Update Python compatibility: drop Python 3.6 and 3.7, add support for Python 3.10 [[#117]](https://github.com/aiidateam/aiida-pseudo/pull/117)
- Update and pin `pylint==2.13.7` [[#116]](https://github.com/aiidateam/aiida-pseudo/pull/116)

### Tests
- Do not rely on actual URL to test install family [[#112]](https://github.com/aiidateam/aiida-pseudo/pull/112)

### Devops
- Adopt PEP 621 and move build spec to `pyproject.toml` [[#118]](https://github.com/aiidateam/aiida-pseudo/pull/118)
- Move the source directory into `src/` [[#121]](https://github.com/aiidateam/aiida-pseudo/pull/121)
- Add GitHub Actions workflow for continuous deployment [[#123]](https://github.com/aiidateam/aiida-pseudo/pull/123)
- Add compatibility matrix `README.md` [[#122]](https://github.com/aiidateam/aiida-pseudo/pull/122)
- Add proper file extension to license file [[#119]](https://github.com/aiidateam/aiida-pseudo/pull/119)
- Update the `pre-commit` configuration [[#113]](https://github.com/aiidateam/aiida-pseudo/pull/113)


## `0.6.3` - 2021-08-23

### Fixes
- CLI: update base URL to SSSP files on Materials Cloud [[#104]](https://github.com/aiidateam/aiida-pseudo/pull/104)

### Devops
- Dependencies: remove temporary upper limit for sqlalchemy [[#73]](https://github.com/aiidateam/aiida-pseudo/pull/73)
- Dependencies: put upper limit on psycopg2-binary [[#106]](https://github.com/aiidateam/aiida-pseudo/pull/106)


## `0.6.2` - 2021-05-17

This release comes with the addition of the first version of the [online documentation](https://aiida-pseudo.readthedocs.io/en/latest/).
It is now also possible to construct a new pseudopotential data node from a filepath on disk instead of a bytestream.

### Features
- CLI: add support for units to `family show` [[#97]](https://github.com/aiidateam/aiida-pseudo/pull/97)
- `PseudoPotentialData`: allow `str` or `Path` for `source` argument [[#98]](https://github.com/aiidateam/aiida-pseudo/pull/98)

### Improvements
- `RecommendedCutoffMixin`: improve error messages [[#86]](https://github.com/aiidateam/aiida-pseudo/pull/86)
- Docs: add first version of documentation [[#88]](https://github.com/aiidateam/aiida-pseudo/pull/88)


## `0.6.1` - 2021-05-04

This release contains two changes that would be breaking, but the `CutoffsFamily` was only intended for testing purposes and the command line option flag changes are unlikely to break code.
Therefore this is released as a patch version such that plugins do not have to update their version requirements which are often limited to a particular minor version.

### Features
- CLI: allow folder on disk for `aiida-pseudo install family` and add the `-P/--pseudo-type` option to define the pseudopotential data plugin to be used [[#80]](https://github.com/aiidateam/aiida-pseudo/pull/80)

### Changes
- Rename `CutoffsFamily` to `CutoffsPseudoPotentialFamily` [[#82]](https://github.com/aiidateam/aiida-pseudo/pull/82)
- CLI: change the `-F/--archive-format` to `-f/--archive-format` and `-T/--family-type` to `-F/--family-type` [[#80]](https://github.com/aiidateam/aiida-pseudo/pull/80)


## `0.6.0` - 2021-04-13

The biggest change in this release is the addition of explicit units for the recommended cutoffs of pseudopotential families that support it.
Before, the cutoffs always had to be specified in electronvolt, but now it is possible to define cutoffs in a variety of energy units.
To facilitate that a single family can specify multiple sets of cutoffs at different "stringencies", with optionally different units, the interface of `RecommendedCutoffMixin.set_cutoffs` had to be changed.
Instead of taking a dictionary with the cutoffs for all stringencies in one go, it now takes the dictionary of cutoffs for a single stringency.
Pseudopotential families that were installed with `aiida-pseudo>=0.4.0` should continue to function properly.

### Features
- `RecommendedCutoffMixin`: store the unit of cutoffs in extras [[#57]](https://github.com/aiidateam/aiida-pseudo/pull/57)
- Add the `VpsData` plugin [[#44]](https://github.com/aiidateam/aiida-pseudo/pull/44)
- CLI: add recommended cutoffs to `aiida-pseudo show` [[#52]](https://github.com/aiidateam/aiida-pseudo/pull/52)
- CLI: add the `aiida-pseudo family cutoffs set` command [[#55]](https://github.com/aiidateam/aiida-pseudo/pull/55)[[#67]](https://github.com/aiidateam/aiida-pseudo/pull/67)[[#71]](https://github.com/aiidateam/aiida-pseudo/pull/71)
- CLI: add `--download-only` option to automatic family install commands [[#65]](https://github.com/aiidateam/aiida-pseudo/pull/65)
- Docs: add troubleshooting section to the `README.md` [[#60]](https://github.com/aiidateam/aiida-pseudo/pull/60)

### Fixes
- `PseudoDojoFamily`: skip repo files with unsupported extension [[#48]](https://github.com/aiidateam/aiida-pseudo/pull/48)

### Changes
- CLI: move `aiida-pseudo show` to `aiida-pseudo family show` [[#58]](https://github.com/aiidateam/aiida-pseudo/pull/58)
- `RecommendedCutoffMixin`: set only one stringency with `set_cutoffs` [#72]](https://github.com/aiidateam/aiida-pseudo/pull/72)

### Refactoring
- CLI: refactor download code from automated install commands [[#69]](https://github.com/aiidateam/aiida-pseudo/pull/69)


## `0.5.0` - 2021-01-13

### Changes
- PseudoDojo: remove support for `v0.3` and enable fixed `v0.4` families [[#39]](https://github.com/aiidateam/aiida-pseudo/pull/39)
- PseudoDojo: enable PAW based families and lower dual factors [[#42]](https://github.com/aiidateam/aiida-pseudo/pull/42)


## `0.4.0` - 2020-12-09

This release significantly changes the design of the plugin with respect to how families are subclassed for different pseudopotential formats.
Before, for each pseudopotential format, one would have to create a specific subclass of a family for it to be able to store pseudopotentials of the type.
This quickly becomes untractable as more _real_ different family types are added, such as the SSSP and Pseudo Dojo.
Instead, each family class can now support any number of pseudopotential types.
However, each instance of a family will only ever host a single type of pseudopotential and not multiple.

### Features
- Add support for the Pseudo Dojo pseudopotential families [[#26]](https://github.com/aiidateam/aiida-pseudo/pull/26)
- Add support for the JTH XML format through the `JthXmlData` data plugin [[#37]](https://github.com/aiidateam/aiida-pseudo/pull/37)
- `PseudoPotentialData`: add the `get_or_create` classmethod [[#33]](https://github.com/aiidateam/aiida-pseudo/pull/33)
- `PseudoPotentialData`: add the `get_entry_point_name` classmethod [[#30]](https://github.com/aiidateam/aiida-pseudo/pull/30)
- `PseudoPotentialFamily`: allow support of multiple pseudo formats [[#31]](https://github.com/aiidateam/aiida-pseudo/pull/31)
- Update the `README.md` with simple instructions and design explanation [[#34]](https://github.com/aiidateam/aiida-pseudo/pull/34)

### Changes
- `RecommendedCutoffMixin`: require electronvolts for cutoffs [[#35]](https://github.com/aiidateam/aiida-pseudo/pull/35)
- `PseudoPotentialFamily`: add the `pseudo_type` extra [[#31]](https://github.com/aiidateam/aiida-pseudo/pull/31)
- Remove pseudo potential family plugins for specific file formats [[#31]](https://github.com/aiidateam/aiida-pseudo/pull/31)

### Fixes
- `PseudoPotentialFamily`: override `remove_nodes` and `clear` [[#29]](https://github.com/aiidateam/aiida-pseudo/pull/29)


## `0.3.0` - 2020-11-17

### Features
- Add support for Python 3.9 [[#21]](https://github.com/aiidateam/aiida-pseudo/pull/21)
- `RecommendedCutoffMixin`: add concept of stringency levels [[#20]](https://github.com/aiidateam/aiida-pseudo/pull/20)
- `UpfData`: automatically parse the Z valence from the file [[#24]](https://github.com/aiidateam/aiida-pseudo/pull/24)

### Fixes
- `PseudoPotentialFamily.get_pseudos`: maintain structure kind names [[#20]](https://github.com/aiidateam/aiida-pseudo/pull/20)


## `0.2.0` - 2020-10-26

### Changes
- `PseudoPotentialFamily.get_pseudos`: turn arguments into keyword only [[#7]](https://github.com/aiidateam/aiida-pseudo/pull/7)

### Features
- Add support for the PSF format through the `PsfData` data plugin [[`2156b45f`]](https://github.com/aiidateam/aiida-pseudo/commit/2156b45f2adc6c0c1b11fe6e6a0c123df464c0af)
- Add support for the PSML format through the `PsmlData` data plugin [[`2156b45f`]](https://github.com/aiidateam/aiida-pseudo/commit/2156b45f2adc6c0c1b11fe6e6a0c123df464c0af)
- Add support for the PSP8 format through the `Psp8Data` [[#11]](https://github.com/aiidateam/aiida-pseudo/pull/11)
- Add the `PsfFamily` group plugin for PSF pseudo potential families [[`2156b45f`]](https://github.com/aiidateam/aiida-pseudo/commit/2156b45f2adc6c0c1b11fe6e6a0c123df464c0af)
- Add the `PsmlFamily` group plugin for PSML pseudo potential families [[`2156b45f`]](https://github.com/aiidateam/aiida-pseudo/commit/2156b45f2adc6c0c1b11fe6e6a0c123df464c0af)
- Add the `Psp8Family` group plugin for PSP8 pseudo potential families [[#11]](https://github.com/aiidateam/aiida-pseudo/pull/11)
- `PseudoPotentialFamily`: deduplicate existing pseudos [[#5]](https://github.com/aiidateam/aiida-pseudo/pull/5)

### Fixes
- `PseudoPotentialData`: maintain correct signature for `store` method

### Devops
- Pre-commit: move `pylint` conf to `pyproject.toml` [[`2156b45f`]](https://github.com/aiidateam/aiida-pseudo/commit/2156b45f2adc6c0c1b11fe6e6a0c123df464c0af)
- Pre-commit: replace old format string interpolation with f-strings [[`302fb105`]](https://github.com/aiidateam/aiida-pseudo/commit/302fb1056489e2d1e1e59bf5011ea28388e8b6f2)


## `0.1.0` - 2020-10-07

First release of `aiida-pseudo`.
