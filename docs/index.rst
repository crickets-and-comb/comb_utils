===========================================
Reference Package: A basic package template
===========================================

Includes typical CLI and library setup. To include service app setup at some point.

See also the GitHub repository: https://github.com/crickets-and-comb/comb_utils

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

    pip install comb_utils

See https://pypi.org/project/comb-utils/.


Library
-------

Avoid calling library functions directly and stick to the public API:

.. code:: python

    from comb_utils import wait_a_second

    wait_a_second()

If you're a power user, you can use the internal API:

.. code:: python

    from comb_utils.api.internal import wait_a_second

    wait_a_second()


Nothing is stopping you from importing from lib directly, but you should avoid it unless you're developing:

.. code:: python

    from comb_utils.lib.example import wait_a_second

    wait_a_second()

CLI
---

When this package is installed, it comes with CLI tools. See :doc:`CLI` for more information.