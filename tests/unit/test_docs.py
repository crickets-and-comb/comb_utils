"""Tests for the docs module."""

import pytest

from comb_utils import DocString, ErrorDocString


@pytest.mark.parametrize(
    "docstring, expected_docstring",
    [
        (
            DocString(
                opening="Test opening",
                args={"arg1": "arg1 docstring", "arg2": "arg2 docstring"},
                raises=[
                    ErrorDocString(error_type="Error1", docstring="Error1 docstring"),
                    ErrorDocString(error_type="Error2", docstring="Error2 docstring"),
                ],
                returns=["return1", "return2"],
            ),
            (
                "Test opening\n\n\n"
                "Args:\n\n\n  arg1: arg1 docstring\n\n  arg2: arg2 docstring\n\n\n"
                "Raises:\n\n\n  Error1: Error1 docstring\n\n  Error2: Error2 docstring\n\n\n"
                "Returns:\n\n\n  return1\n\n  return2\n"
            ),
        ),
        (
            DocString(
                opening="Test opening",
                args={},
                raises=[ErrorDocString(error_type="Error1", docstring="Error1 docstring")],
                returns=["return1", "return2"],
            ),
            (
                "Test opening\n\n\n"
                "Raises:\n\n\n  Error1: Error1 docstring\n\n\n"
                "Returns:\n\n\n  return1\n\n  return2\n"
            ),
        ),
        (
            DocString(
                opening="Test opening",
                args={"arg1": "arg1 docstring", "arg2": "arg2 docstring"},
                raises=[],
                returns=["return1", "return2"],
            ),
            (
                "Test opening\n\n\n"
                "Args:\n\n\n  arg1: arg1 docstring\n\n  arg2: arg2 docstring\n\n\n"
                "Returns:\n\n\n  return1\n\n  return2\n"
            ),
        ),
        (
            DocString(
                opening="Test opening",
                args={"arg1": "arg1 docstring", "arg2": "arg2 docstring"},
                raises=[ErrorDocString(error_type="Error1", docstring="Error1 docstring")],
                returns=[],
            ),
            (
                "Test opening\n\n\n"
                "Args:\n\n\n  arg1: arg1 docstring\n\n  arg2: arg2 docstring\n\n\n"
                "Raises:\n\n\n  Error1: Error1 docstring\n"
            ),
        ),
    ],
)
def test_api_docstring(docstring: DocString, expected_docstring: str) -> None:
    """Test the DocString class."""
    assert docstring.api_docstring == expected_docstring


@pytest.mark.parametrize(
    "docstring, expected_docstring",
    [
        (
            DocString(
                opening="Test opening",
                args={"arg1": "arg1 docstring", "arg2": "arg2 docstring"},
                raises=[
                    ErrorDocString(error_type="Error1", docstring="Error1 docstring"),
                    ErrorDocString(error_type="Error2", docstring="Error2 docstring"),
                ],
                returns=["return1", "return2"],
            ),
            (
                "Test opening\n\n\n"
                "Raises:\n\n\n  Error1: Error1 docstring\n\n  Error2: Error2 docstring\n\n\n"
                "Returns:\n\n\n  return1\n\n  return2\n"
            ),
        ),
        (
            DocString(
                opening="Test opening",
                args={},
                raises=[ErrorDocString(error_type="Error1", docstring="Error1 docstring")],
                returns=["return1", "return2"],
            ),
            "Test opening\n\n\n"
            "Raises:\n\n\n  Error1: Error1 docstring\n\n\n"
            "Returns:\n\n\n  return1\n\n  return2\n",
        ),
        (
            DocString(
                opening="Test opening",
                args={"arg1": "arg1 docstring", "arg2": "arg2 docstring"},
                raises=[],
                returns=["return1", "return2"],
            ),
            "Test opening\n\n\nReturns:\n\n\n  return1\n\n  return2\n",
        ),
        (
            DocString(
                opening="Test opening",
                args={"arg1": "arg1 docstring", "arg2": "arg2 docstring"},
                raises=[ErrorDocString(error_type="Error1", docstring="Error1 docstring")],
                returns=[],
            ),
            "Test opening\n\n\nRaises:\n\n\n  Error1: Error1 docstring\n",
        ),
    ],
)
def test_cli_docstring(docstring: DocString, expected_docstring: str) -> None:
    """Test the DocString class."""
    assert docstring.cli_docstring == expected_docstring
