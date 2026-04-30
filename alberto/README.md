# Instructions

> [!WARNING]
> Carefully check the pseudo files and cutoffs are correct! Use with care, here be dragons. 🐉
> The pseudos/cutoffs for Pt and Ir are still being tested, so YMMV.

Pull in this branch, go into the `alberto` dir and execute:

```
python install_sssp.py
```

Assumptions:

* You know how `git` works
* you are in your AiiDA env
* You have installed `aiida-pseudo` in said local env with a local (editable) install: `pip install -e aiida-pseudo/`

(possible other things, works on my machine 🤷‍♂️)

As a sanity check, you can run:

```
aiida-pseudo family show SSSP/2.0/PBEsol/precision
```

And verify the pseudo filenames and cutoffs are correct.
