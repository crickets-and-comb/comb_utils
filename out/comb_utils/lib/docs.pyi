from dataclasses import dataclass
from typeguard import typechecked
from typing import Any, Final

@dataclass
class ErrorDocString:
    '''Error docstrings.

    Args:
            error_type: The error type. E.g., "ValueError".
            docstring: The error docstring. E.g., "When arg `a` is less than 0."
    '''
    error_type: Final[str]
    docstring: Final[str]
    @typechecked
    def __init__(self, error_type: str, docstring: str) -> None:
        """Initialize the error docstring."""

class DocString:
    """Class to format docstrings and store argument defaults for public API `sphinx` docs         and CLI `click` help.

    Args:
            opening: The opening docstring.
            args: Argument names and their docstrings.
            raises: Objects holding error types with their docstrings.
            returns: The returns docstrings.
            defaults: The parameter defaults. ``None`` casts to empty ``dict``.
    """
    opening: str
    args: dict[str, str]
    raises: list[ErrorDocString]
    returns: list[str]
    defaults: dict[str, Any]
    @typechecked
    def __init__(self, opening: str, args: dict[str, str], raises: list[ErrorDocString], returns: list[str], defaults: dict[str, Any] | None = None) -> None:
        """Initialize the docstring parts."""
    @property
    @typechecked
    def api_docstring(self) -> str:
        """Docstring formatted for Sphinx API docs."""
    @property
    @typechecked
    def cli_docstring(self) -> str:
        """Docstring formatted for Click CLI help."""
