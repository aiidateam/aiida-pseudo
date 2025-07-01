# Development

## Release

### Version

We use [semantic versioning](https://semver.org/), i.e. version labels have the form `v<major>.<minor>.<patch>`

* Patch release: `v1.7.1` to `v1.7.2`, only bug fixes
* Minor release: `v1.7.1` to `v1.8.0`, bug fixes and new features that **maintain** backwards compatibility.
* Major release: `v1.7.1` to `v2.0.0`, bug fixes and new features that **break** backwards compatibility.

In the steps below, we'll assume the version to be released is `v1.7.2`.

### Steps

To make a new release of the `aiida-pseudo` plugin package, first create a release branch based on the latest `main` branch:

```console
git fetch --all --prune
git checkout origin/main -b release/1.7.2
```

Next, update the source code `__version__` in the `src/aiida_pseudo/__init__.py` file by hand.
It should look something like this:

```
"""AiiDA plugin that simplifies working with pseudo potentials."""
__version__ = '1.7.2'
```

Then, run the `update_changelog.py` script to update the `CHANGELOG.md` with all the changes made since the last release:

```console
python .github/workflows/update_changelog.py
```

This will automatically add:

1. The header for the new release and the sub-headers in which the commits should be sorted.
2. The list of commits since the previous release, with links to them.

Sort the commit items into the correct subsection of the change log.
Ideally, describe the main changes or new features at the top of the change log message, providing code snippets where it's useful.

Once you've prepared the release branch locally, commit and push it to Github:

    git commit -am '🚀 Release `v1.7.2`'
    git push -u origin release/1.7.2

Now that the release branch is ready, push the local changes to the remote `release/1.7.2` branch, then go to Github and create a pull request to the `main` branch of the official repository.

After the pull request has been approved, merge the PR using the **"Squash and Merge"**, and make sure the commit is simply named e.g. "🚀 Release `v1.7.2`".

Once this is complete, fetch all the changes locally, checkout the `main` branch and make sure it's up to date with the remote:

    git fetch --all
    git checkout main
    git pull origin

Next, tag the final release commit:

    git tag -a v1.7.2 -m 'Release `v1.7.2`'

**IMPORTANT**: once you push the tag to GitHub, a workflow will start that automatically publishes a release on PyPI.
Double check that the tag is correct, and that the `main` branch looks in good shape.

If you accidentally tagged the wrong commit, you can delete the local tag using the following command:

    git tag -d v1.7.2

Once you're confident that the tag and `main` branch are in good shape, push both to the remote:

    git push origin main --tags

With the release tag created, the new release is automatically built and published on PyPI!
