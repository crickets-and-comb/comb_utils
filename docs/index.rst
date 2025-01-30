===========================================
Reference Package: A basic package template
===========================================

Includes typical CLI and library setup. To include service app setup at some point.

See also the GitHub repository: https://github.com/crickets-and-comb/reference_package

Contents
--------

.. toctree::
   :maxdepth: 3

   CLI
   modules

Installation
------------

To install the package, run:

.. code:: bash

    pip install reference_package

See https://pypi.org/project/reference-package/.


Library
-------

Avoid calling library functions directly and stick to the public API:

.. code:: python

    from reference_package import wait_a_second

    wait_a_second()

If you're a power user, you can use the internal API:

.. code:: python

    from reference_package.api.internal import wait_a_second

    wait_a_second()


Nothing is stopping you from importing from lib directly, but you should avoid it unless you're developing:

.. code:: python

    from reference_package.lib.example import wait_a_second

    wait_a_second()

CLI
---

When this package is installed, it comes with CLI tools. See :doc:`CLI` for more information.