# Basic package template

## Summary

Just a basic package template. See the docs: https://crickets-and-comb.github.io/reference_package/.

## Structure

```bash
    .github/workflows               GitHub Actions CI/CD workflows.
    docs                            RST docs and doc build staging.
    Makefile                        Dev tools and params. (includes shared/Makefile)
    src/reference_package/api       Public and internal API.
    src/reference_package/cli       Command-line-interface.
    setup.cfg                       Metadata and dependencies.
    shared                          Shared dev tools Git submodule.
    src/reference_package/lib       Implementation.
    tests/e2e                       End-to-end tests.
    test/integration                Integration tests.
    tests/unit                      Unit tests.
```

## Installation

To install the package, run:

  $ pip install reference_package

See https://pypi.org/project/reference-package/.

## Library functions

`reference_package` is a library from which you can import functions. Import the public example function like this: `from reference_package import wait_a_second`. Or, import the internal version like a power user like this: `from reference_package.api.internal import wait_a_second`.

Unless you're developing, avoid importing directly from library, like `from reference_package.lib.example import wait_a_second`.

## CLI

Try the example CLI:

    $ python -m example
    $ python -m example --secs 2

## Dev workflow

There are a number of dev tools in the `Makefile`. You can list all the make tools you might want to use:

    $ make list-targets

Go check them out in `Makefile`.

*Note: The dev tools are built around developing on a Mac, so they may not all work on Windows without some modifications.*

### Shared tools setup

When you first clone this repo, you'll need to set up the shared tools Git submodule. Follow the setup directions on that repo's README: https://github.com/crickets-and-comb/shared

*Note: There is a lot of overlap in the documentation for this package and the shared tools. This will likely be consolidated at some point, but for now I've stopped updating this package with documentation about using `shared`, so this part may have fallen out of date. Please see documentation for `shared`.*

See also https://git-scm.com/book/en/v2/Git-Tools-Submodules. And, take a look at the `.gitmodules` file in this repo.

The shared repo contains dev tools that this repo depends on, namely reusable workflows (for running QC/tests and CI/CD on GitHub) and make recipes/targets for running QC/tests locally while developing.

While the Makefile points to the shared Makefile via the Git submodule as a subdirectory, the workflows point to the shared reusable workflows via GitHub. You can point workflows at the shared workflows in the submodule directory (say for trying out uncommitted changes to a shared workflow) and run the workflows from `act` (see the `run-act` in the shared Makefile), but they will not run on the GitHub runners unless they point via GitHub.

You can override shared make targets or add new targets that aren't in the shared Makefile by adding them to this repo's top-level Makefile.

#### Updating shared tools

Once you've set up the shared dev tools submodule, you'll want to periodically update it to get updates to the shared tools:

  $ make update-shared

This is just a wrapper to `git submodule update --remote --merge` and will pull the latest commit on the submodule's remote. Note that, while you'll be able to run with this updated shared submodule, you'll still want to commit that update to your consuming repo to track that update. After updating, you'll see an unstaged change in the submodule's commit hash that the consuming repo tracks:

```bash
$ make clean update-shared
git submodule update --remote --merge
remote: Enumerating objects: 3, done.
remote: Counting objects: 100% (3/3), done.
remote: Total 3 (delta 2), reused 3 (delta 2), pack-reused 0 (from 0)
Unpacking objects: 100% (3/3), 1.49 KiB | 761.00 KiB/s, done.
From github.com:crickets-and-comb/shared
   c5be642..b8cc5aa  my/shared/branch -> origin/my/shared/branch
Updating c5be642..b8cc5aa
Fast-forward
 Makefile | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
Submodule path 'shared': merged in 'b8cc5aa3881af14404a491624c9251f4f774cefb'
$ 
$ 
$ git diff
diff --git a/shared b/shared
index c5be642..b8cc5aa 160000
--- a/shared
+++ b/shared
@@ -1 +1 @@
-Subproject commit c5be6421082ec103687282c1a12cf16d7968384a
+Subproject commit b8cc5aa3881af14404a491624c9251f4f774cefb
$ 
```

#### Setting Personal Access Token

The shared workflows rely on a Personal Access Token (PAT) (to checkout the submodule so they can use the make targets). You need to create a PAT with repo access and add it to the consuming repo's (`reference_package` in this case) action secrets as `CHECKOUT_SHARED`. See GitHub for how to set up PATs (hint: check the developer settings on your personal account) and how to add secrets to a repo's actions (hint: check the repo's settings).

Note: Using a PAT tied to a single user like this is less than ideal. Figuring out how to get around this is a welcome security upgrade.

### Dev installation

You'll want this package's site-package files to be the source files in this repo so you can test your changes without having to reinstall. We've got some tools for that.

First build and activate the env before installing this package:

    $ make build-env
    $ conda activate reference_package_py3.12

Note, if you don't have Python installed, you need to pass the package name directly when you build the env: `make build-env PACKAGE_NAME=reference_package`. If you have Python installed (e.g., this conda env already activated), then you don't need to because it uses Python to grab the package name from the `setup.cfg` file.

Then, install this package and its dev dependencies:

    $ make install

This installs all the dependencies in your conda env site-packages, but the files for this package's installation are now your source files in this repo.

Note: Running `make install` is equivalent to running `make install INSTALL_EXTRAS=[dev]`. If you want to install 

### QC and testing

Before pushing commits, you'll usually want to rebuild the env and run all the QC and testing:

    $ make clean format full

When making smaller commits, you might just want to run some of the smaller commands:

    $ make clean format full-qc full-test

### Workflows: usage and limitations

Using the workflows found in `.github/workflows`, QC, tests, builds, and deployment run on GitHub on certain events (e.g., pull requests, pushes to main, manual dispatches).

The shared workflows (in the shared submodule at `shared/.github/workflows`) are reusable workflows, meaning they can can be called from within other workflows. See https://docs.github.com/en/actions/sharing-automations/reusing-workflows.

See also `.github/workflows/test_install_dispatch.yml` workflow for an example. Here we've wrapped a single reusable workflow in another so we can dispatch it manually from the consuming repo.

While wrapping a single workflow for manual dispatch is handy, we've wrapped these shared workflows into a single workflow calling them in the desired order (QC/test, build, publish, test installation, deploy docs). See `.github/workflows/CI_CD.yml`.

#### Publishing to PyPi

Shared workflows are split into different aspects of CI/CD, but they don't cover all of them. Specifically, they don't cover publishing packages to PyPi. This is because PyPi doesn't allow trusted publishing from reusable workflows. In `.github/workflows/CI_CD.yml`, we've defined publishing jobs within the same workflow that calls shared workflows to create a full CI/CD pipeline.

#### TEST_OR_PROD

Some of the workflows have a `TEST_OR_PROD` parameter. This is to control which aspects run. Some jobs and steps only run on `TEST_OR_PROD=test`, some only on `TEST_OR_PROD=prod`, some only on both, some no matter what. While the parameter defaults to "dev", this value does not enable anything in particular; it's just an unambiguous way to say neither "test" nor "prod". This is useful for avoiding deployment during development. For example, passing "dev" (or not "test" or "prod") skips uploading build artifacts to GitHub for later use, since attempting this locally with the `run-act` make target will fail (see `shared/.github/workflows/build_dist.yml` and `shared/Makefile`).

Int `.github/workflows/CI_CD.yml`, we've set up the CI/CD pipeline to run on all pull requests (PRs), on pushes to main, and on manual dispatch. For pull requests, we only run QC, pre-publishing testing, and building (`TEST_OR_PROD=dev`). We don't want to publish any packages or documentation until the pull request has been approved and merged to main. On pushes to main (approved PRs), we run the same bits as PRs, and if those pass again, we run a test release to TestPyPi followed by a test installation (`TEST_OR_PROD=test`). The manual workflow_dispatch allows you to run from GitHub Actions with any parameters on any branch at any time. For instance, once you see that the test deployment succeeded and you're ready to release to PyPi and publish documentation to GitHub Pages, you then manually dispatch the workflow again with `TEST_OR_PROD=prod`.

#### Developing workflows

When developing the workflows themselves, you'll want to try them out locally before trying them on GitHub (which costs $ for every second of runtime). We use `act` and Docker to run workflows locally. Since `act` doesn't work with Mac and Windows architecture, it skips/fails them, but it is a good test of the Linux build.

You can use a make target for that:

  $ make run-act

That will run `.github/workflows/CI_CD.yml`. But, you can also run any workflow you'd like by using `act` directly. See https://nektosact.com.

To use this tool, you'll need to have Docker installed and running on your machine: https://www.docker.com/. You'll also need to install `act` in your terminal:

  $ brew install act

Additionally, you'll need to change the URLs in the calling workflows that refer to the shared workflows. `act` looks at your local files and does not follow the GitHub URL. It will fail when it tries to find the shared workflow. So, you need to point it to the local submodule. For instance, if you're calling this:

```YML
jobs:
  CI:
    name: QC and Tests
    uses: crickets-and-comb/shared/.github/workflows/CI.yml@main
    secrets: inherit
```

Change it to:

```YML
jobs:
  CI:
    name: QC and Tests
    uses: ./shared/.github/workflows/CI.yml
    secrets: inherit
```

Incidentally, you don't need to worry about the branch name with `act` as it will just run what's in your directory. GitHub, on the other hand, does need a branch reference, so you'll need to change that to test changes to workflows on GitHub. So, change the branch like this:

```YML
jobs:
  CI:
    name: QC and Tests
    uses: crickets-and-comb/shared/.github/workflows/CI.yml@dev/me/my-shared-dev-branch
    secrets: inherit
```

Further, in order to checkout the right commit of the submodule when testing a workflow on GitHub, you'll need to check a couple of things. First, make sure you have the branch set in the `.gitmodules` file. Second, make sure you've committed, in this repo, the commit hash you're testing of the shared repo submodule.

It's tricky developing shared workflows, but if you're just developing this package itself, you shouldn't need to do any of this. The `full*` make targets in `Makefile` should suffice. They will run on your local machine without Docker and will look in your shared submodule without any special direction.

## Matrix build and support window

The shared workflows run a matrix of Python versions and OS versions. See https://github.com/crickets-and-comb/shared.

While we run installation tests on Ubuntu, macOS, and Windows to ensure published packages work on all three, we run pre-publishing QC only on Ubuntu and macOS. The reason for this is that QC uses our dev tools and we don't yet support dev on Windows. Supporting Windows dev tools may only require a simple set of changes (e.g., conditionally setting filepath syntax), and is a welcome upgrade on the list of TODOs.

We run QC and installation tests on a Python matrix as well (3.11 - 3.13 at time of writing). We set this matrix based on the Scientific Python SPEC 0 support window https://scientific-python.org/specs/spec-0000/#support-window. This support window includes common packages for scientific computing (e.g., `numpy` and `pandas`), and we recommend keeping relevant dependencies pinned within this support window when consuming shared tools.

See https://github.com/crickets-and-comb/shared `.github/workflows/CI.yml` and `.github/workflows/test_install.yml`. See also the workflows within this repo that call them.

## Acknowledgement

To start this reference package, I borrowed, modified, and added to some of the idiomatic structure and tools of IHME's Central Computation GBD team from when I worked with them in 2022-2024.