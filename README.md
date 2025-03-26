# Comb Utils

Some handy utils for Python projects. Repo is made from the `reference_package` template repo: https://github.com/crickets-and-comb/reference_package. See the docs: https://crickets-and-comb.github.io/shared_utils/.

This is a [Crickets and Comb](https://cricketsandcomb.org) resource.

## Structure

```bash
    .github/workflows               GitHub Actions CI/CD workflows.
    docs                            RST docs and doc build staging.
    Makefile                        Dev tools and params. (includes shared/Makefile)
    setup.cfg                       Metadata and dependencies.
    shared                          Shared dev tools Git submodule.
    src/comb_utils/lib              Implementation.
    tests/unit                      Unit tests.
```

## Installation

To install the package, run:

  $ pip install comb_utils

See https://pypi.org/project/comb-utils/.

## Dev workflow

There are a number of dev tools in the `Makefile`. You can list all the make tools you might want to use:

    $ make list-targets

Go check them out in `Makefile`.

*Note: The dev tools are built around developing on a Mac, so they may not all work on Windows without some modifications.*

### Shared tools setup

When you first clone this repo, you'll need to set up the shared tools Git submodule. Follow the setup directions on that repo's README: https://github.com/crickets-and-comb/shared

#### Updating shared tools

Once you've set up the shared dev tools submodule, you'll want to periodically update it to get updates to the shared tools:

  $ make update-shared

Note that, while you'll be able to run with this updated shared submodule, you'll still want to commit that update to your consuming repo to track that update.

#### Setting Personal Access Token

The shared workflows rely on a Personal Access Token (PAT) (to checkout the submodule so they can use the make targets). You need to create a PAT with repo access and add it to the consuming repo's (`comb_utils` in this case) action secrets as `CHECKOUT_SHARED`. See GitHub for how to set up PATs (hint: check the developer settings on your personal account) and how to add secrets to a repo's actions (hint: check the repo's settings).

Note: Using a PAT tied to a single user like this is less than ideal. Figuring out how to get around this is a welcome security upgrade.

### Dev installation

You'll want this package's site-package files to be the source files in this repo so you can test your changes without having to reinstall. We've got some tools for that.

First build and activate the env before installing this package:

    $ make build-env
    $ conda activate comb_utils_py3.12

Note, if you don't have Python installed, you need to pass the package name directly when you build the env: `make build-env PACKAGE_NAME=comb_utils`. If you have Python installed (e.g., this conda env already activated), then you don't need to because it uses Python to grab the package name from the `setup.cfg` file.

Then, install this package and its dev dependencies:

    $ make install

This installs all the dependencies in your conda env site-packages, but the files for this package's installation are now your source files in this repo.

### QC and testing

Before pushing commits, you'll usually want to rebuild the env and run all the QC and testing:

    $ make clean format full

When making smaller commits, you might just want to run some of the smaller commands:

    $ make clean format full-qc full-test

#### Using act

As a final step, it's good practice to test run the workflow before opening a PR or pushing to an open PR. We don't want to waste GitHub runtime on a glitch that we could have caught before. You can use a make target for that:

  $ make run-act

That will run `.github/workflows/CI_CD.yml`. But, you can also run any workflow you'd like by using `act` directly. See https://nektosact.com.

To use this tool, you'll need to have Docker installed and running on your machine: https://www.docker.com/. You'll also need to install `act` in your terminal:

  $ brew install act

NOTE: To be more accurate, we've overridden `set-CI-CD-file` to create a local `CI_CD_act.yml` (which we ignore with Git) as a copy of `CI_CD.yml` and replace one of the workflow call URLs with a relative path. We use a relative path because otherwise `act` will not honor the overridden `full-test` make target and will run the shared version. That will fail because the shared `full-test` target includes running integration and e2e tests, which this repo does not include.