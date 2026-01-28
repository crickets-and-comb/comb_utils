============================================================
DocString: A Class to Format Docstrings for Sphinx and Click
============================================================

The :py:class:`comb_utils.lib.docs.DocString` class is used to format docstrings for `Sphinx <https://www.sphinx-doc.org/en/master/>`_ API docs and `Click <https://click.palletsprojects.com/en/stable/>`_ CLI help docs. It's useful when you have multiple functions that should have the same docstring, such as when you have a public API function and a CLI function that call the same underlying code.

:code:`DocString` takes an opening docstring, an arg dict, a default dict, a list of returns text, and a list of :py:class:`comb_utils.lib.docs.ErrorDocString` objects. It has three important members that you can use:

:api_docstring: Docstring formatted for Sphinx API docs.
:cli_docstring: Docstring formatted for Click.
:args: Simply the arg dict you pass when you initialize the :code:`DocString` object.

The main difference between :code:`api_docstring` and :code:`cli_docstring` is that :code:`cli_docstring` excludes the args block. CLI args help is picked up by Click in the :code:`click.option` decorators' :code:`help` arguments, to which you can pass the values in :code:`args`.

Example usage:

.. code:: python

    from comb_utils import DocString, ErrorDocString

    ADD_EM_DOCSTRING = DocString(
        opening_docstring="A function to add two numbers.",
        args={
            "a": "The first number. Must be greater than 0.",
            "b": "The second number. Must be less than 100."
        },
        defaults={
            "a": 1,
            "b": 99
        },
        returns=["The sum of the two numbers."],
        error_docstrings=[
            ErrorDocString(
                error_type="ValueError",
                docstring="If `a` is less than 0."
            ),
            ErrorDocString(
                error_type="ValueError",
                docstring="If `b` is greater than 100."
            )
        ]
    )

Now you can use :code:`docstring.api_docstring` in your functions, and :code:`docstring.cli_docstring` and :code:`args` in your Click commands.

Using :code:`docstring.api_docstring` in a function:

.. code:: python

    def add_em(a: int = ADD_EM_DOCSTRING.defaults["a"], b: int = ADD_EM_DOCSTRING.defaults["b"]) -> int:
        if a < 0:
            raise ValueError("a must be greater than 0.")
        if b > 100:
            raise ValueError("b must be less than 100.")
        return a + b

    add_em.__doc__ = ADD_EM_DOCSTRING.api_docstring

Now your Sphinx API docs will have the correct docstring for :code:`add_em`.

Using :code:`docstring.cli_docstring` and :code:`args` in a Click command:

.. code:: python

    import click

    from my_package import ADD_EM_DOCSTRING, add_em
    

    @click.command(help=ADD_EM_DOCSTRING.cli_docstring)
    @click.option("--a", type=int, help=ADD_EM_DOCSTRING.args["a"])
    @click.option("--b", type=int, help=ADD_DOADD_EM_DOCSTRINGCSTRING.args["b"])
    def main(a: int, b: int):
        the_sum = add_em(a=a, b=b)
        click.echo(the_sum)

Now your CLI command help will have a docstring and args that match the function's docstring. Say you created an entry point named :code:`add_em` in your :code:`setup.cfg` file:

.. code:: ini

    [options.entry_points]
    console_scripts =
        add_em = my_package.cli.add_em:main

Then, when you run :code:`add_em --help`, you'll see the correct help doc:

.. code:: bash

    $ add_em --help
    Usage: add_em [OPTIONS]

    A function to add two numbers.

    Raises:

        ValueError: If `a` is less than 0.

        ValueError: If `b` is greater than 100.

    Returns:

        The sum of the two numbers.

    Options:
      --a INTEGER  The first number. Must be greater than 0.
      --b INTEGER  The second number. Must be less than 100.
      --help       Show this message and exit.

You can even use the sphinx-click extension's click directive to include the Click help doc within the CLI module itself, and it's not a problem that it's a circular reference. This is useful for keeping the Sphinx' CLI docs in sync with the CLI's help doc. It's not really a feauture of :code:`DocString`, but it's worth mentioning here:

.. code:: python

    __doc__ = """
    .. click:: my_package.cli.add_em:main
        :prog: add_em
        :nested: full
    """

    import click

    from my_package import ADD_EM_DOCSTRING, add_em


    @click.command(help=ADD_EM_DOCSTRING.cli_docstring)
    @click.option("--a", type=int, help=ADD_EM_DOCSTRING.args["a"])
    @click.option("--b", type=int, help=ADD_DOADD_EM_DOCSTRINGCSTRING.args["b"])
    def main(a: int, b: int):
        the_sum = add_em(a=a, b=b)
        click.echo(the_sum)
