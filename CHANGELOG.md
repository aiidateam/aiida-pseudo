# Change log

## 0.6.0

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


## 0.5.0

### Changes
- PseudoDojo: remove support for `v0.3` and enable fixed `v0.4` families [[#39]](https://github.com/aiidateam/aiida-pseudo/pull/39)
- PseudoDojo: enable PAW based families and lower dual factors [[#42]](https://github.com/aiidateam/aiida-pseudo/pull/42)


## 0.4.0

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


## 0.3.0

### Features
- Add support for Python 3.9 [[#21]](https://github.com/aiidateam/aiida-pseudo/pull/21)
- `RecommendedCutoffMixin`: add concept of stringency levels [[#20]](https://github.com/aiidateam/aiida-pseudo/pull/20)
- `UpfData`: automatically parse the Z valence from the file [[#24]](https://github.com/aiidateam/aiida-pseudo/pull/24)

### Fixes
- `PseudoPotentialFamily.get_pseudos`: maintain structure kind names [[#20]](https://github.com/aiidateam/aiida-pseudo/pull/20)


## 0.2.0

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


## 0.1.0

First release of `aiida-pseudo`.
