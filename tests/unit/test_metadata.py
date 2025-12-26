"""Tests for the metadata module."""

from typing import Any

import pytest

from comb_utils import ErrorDocString, FunctionMetaDataFormatter


@pytest.mark.parametrize(
    "metadata, expected_docstring",
    [
        (
            FunctionMetaDataFormatter(
                opening="Test opening",
                args={"arg1": "arg1 docstring", "arg2": "arg2 docstring"},
                defaults={},
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
            FunctionMetaDataFormatter(
                opening="Test opening",
                args={},
                defaults={},
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
            FunctionMetaDataFormatter(
                opening="Test opening",
                args={"arg1": "arg1 docstring", "arg2": "arg2 docstring"},
                defaults={},
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
            FunctionMetaDataFormatter(
                opening="Test opening",
                args={"arg1": "arg1 docstring", "arg2": "arg2 docstring"},
                defaults={},
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
def test_api_docstring(metadata: FunctionMetaDataFormatter, expected_docstring: str) -> None:
    """Test the api_docstring method of the FunctionMetaDataFormatter class."""
    assert metadata.api_docstring == expected_docstring


@pytest.mark.parametrize(
    "metadata, expected_docstring",
    [
        (
            FunctionMetaDataFormatter(
                opening="Test opening",
                args={"arg1": "arg1 docstring", "arg2": "arg2 docstring"},
                defaults={},
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
            FunctionMetaDataFormatter(
                opening="Test opening",
                args={},
                defaults={},
                raises=[ErrorDocString(error_type="Error1", docstring="Error1 docstring")],
                returns=["return1", "return2"],
            ),
            "Test opening\n\n\n"
            "Raises:\n\n\n  Error1: Error1 docstring\n\n\n"
            "Returns:\n\n\n  return1\n\n  return2\n",
        ),
        (
            FunctionMetaDataFormatter(
                opening="Test opening",
                args={"arg1": "arg1 docstring", "arg2": "arg2 docstring"},
                defaults={},
                raises=[],
                returns=["return1", "return2"],
            ),
            "Test opening\n\n\nReturns:\n\n\n  return1\n\n  return2\n",
        ),
        (
            FunctionMetaDataFormatter(
                opening="Test opening",
                args={"arg1": "arg1 docstring", "arg2": "arg2 docstring"},
                defaults={},
                raises=[ErrorDocString(error_type="Error1", docstring="Error1 docstring")],
                returns=[],
            ),
            "Test opening\n\n\nRaises:\n\n\n  Error1: Error1 docstring\n",
        ),
    ],
)
def test_cli_docstring(metadata: FunctionMetaDataFormatter, expected_docstring: str) -> None:
    """Test the cli_docstring method of the FunctionMetaDataFormatter class."""
    assert metadata.cli_docstring == expected_docstring


@pytest.mark.parametrize(
    "metadata, expected_defaults",
    [
        (
            FunctionMetaDataFormatter(
                opening="Test opening",
                args={"arg1": "arg1 docstring", "arg2": "arg2 docstring"},
                defaults={"arg1": "arg1 default", "arg2": None},
                raises=[
                    ErrorDocString(error_type="Error1", docstring="Error1 docstring"),
                    ErrorDocString(error_type="Error2", docstring="Error2 docstring"),
                ],
                returns=["return1", "return2"],
            ),
            ({"arg1": "arg1 default", "arg2": None}),
        ),
        (
            FunctionMetaDataFormatter(
                opening="",
                args={"arg1": "arg1 docstring"},
                defaults={"arg1": 0},
                raises=[],
                returns=[],
            ),
            ({"arg1": 0}),
        ),
    ],
)
def test_defaults(
    metadata: FunctionMetaDataFormatter, expected_defaults: dict[str, Any]
) -> None:
    """Test the defaults attribute of the FunctionMetaDataFormatter class."""
    assert metadata.defaults == expected_defaults
