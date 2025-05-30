#!/bin/bash
"""Script for automatically updating the `CHANGELOG.md` based on the commits since the latest release tag."""
import re
import subprocess
from pathlib import Path

DEFAULT_CHANGELOG_SECTIONS = """
### ‼️ Breaking changes


### ✨ New features


### 🗑️ Deprecations


### 👌 Improvements


### 🐛 Bug fixes


### 📚 Documentation


### 🔧 Maintenance


### ⬆️ Update dependencies


### 🧪 Tests


### ♻️ Refactor

"""


def update_changelog():
    """Update the `CHANGELOG.md` for a first draft of the release."""

    print('🔍 Checking the current version number')
    current_changelog = Path('CHANGELOG.md').read_text(encoding='utf-8')

    from aiida_pseudo import __version__

    if str(__version__) in current_changelog:
        print('🛑 Current version already in `CHANGELOG.md`. Skipping...')
        return

    print('⬆️ Found updated version number, adapting `CHANGELOG.md`.')
    tags = subprocess.run(['git', 'tag', '--sort=v:refname'], capture_output=True, check=True, encoding='utf-8').stdout
    latest_tag = re.findall(r'(v\d\.\d\.\d)\n', tags)[-1]

    print(f'🔄 Comparing with latest tag `{latest_tag}`.')
    commits = subprocess.run(
        ['git', 'log', "--pretty=format:'%h|%H|%s'", f'{latest_tag}..origin/main'],
        capture_output=True,
        check=True,
        encoding='utf-8',
    ).stdout

    pr_pattern = re.compile(r'\(\S(?P<pr_number>\d+)\)')

    changelog_message = f'## v{__version__}\n' + DEFAULT_CHANGELOG_SECTIONS

    for commit in commits.splitlines():
        hash_short, hash_long, message = commit.strip("'").split('|', maxsplit=2)

        # Remove the PR number from the commit message
        pr_match = pr_pattern.search(message)

        if pr_match is not None:
            pr_number = pr_match.groupdict()['pr_number']
            message = message.replace(rf'(#{pr_number})', '')

        # Add the commit hash (short) to link to the changelog
        message += f' [[{hash_short}](https://github.com/aiidateam/aiida-pseudo/commit/{hash_long})]'
        changelog_message += f'\n* {message}'

    with Path('CHANGELOG.md').open('w', encoding='utf8') as handle:
        new_changelog = current_changelog.replace('# Change log', f'# Change log\n\n{changelog_message}')
        handle.write(new_changelog)

    print("🚀 Success! Finalise the `CHANGELOG.md` and let's get this baby released.")


if __name__ == '__main__':
    update_changelog()
