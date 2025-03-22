"""Docstring formatting for sphinx API docs and click CLI help."""

from dataclasses import dataclass
from typing import Final

from typeguard import typechecked


@dataclass
class ErrorDocString:
    """Error docstrings.

    Args:
            error_type: The error type. E.g., "ValueError".
            docstring: The error docstring. E.g., "When arg `a` is less than 0."
    """

    error_type: Final[str]
    docstring: Final[str]

    @typechecked
    def __init__(self, error_type: str, docstring: str) -> None:
        """Initialize the error docstring."""
        self.error_type = error_type
        self.docstring = docstring

        return


class DocString:
    """Class to format docstrings for public API `sphinx` docs and CLI `click` help.

    Args:
            opening: The opening docstring.
            args: Argument names and their docstrings.
            raises: Objects holding error types with their docstrings.
            returns: The returns docstrings.
    """

    opening: str = ""
    args: dict[str, str] = {}
    raises: list[ErrorDocString] = []
    returns: list[str] = []

    @typechecked
    def __init__(
        self,
        opening: str,
        args: dict[str, str],
        raises: list[ErrorDocString],
        returns: list[str],
    ) -> None:
        """Initialize the docstring parts."""
        self.opening = opening
        self.args = args
        self.raises = raises
        self.returns = returns

        return

    @property
    @typechecked
    def api_docstring(self) -> str:
        """Docstring formatted for Sphinx API docs."""
        parts = [self.opening.strip()]

        if self.args:
            parts.append("\nArgs:\n")
            parts.extend([f"  {key}: {value}" for key, value in self.args.items()])

        if self.raises:
            parts.append("\nRaises:\n")
            parts.extend(
                [f"  {error.error_type}: {error.docstring}" for error in self.raises]
            )

        if self.returns:
            parts.append("\nReturns:\n")
            parts.extend([f"  {item}" for item in self.returns])

        return "\n\n".join(parts) + "\n"

    @property
    @typechecked
    def cli_docstring(self) -> str:
        """Docstring formatted for Click CLI help."""
        parts = [self.opening.strip()]

        if self.raises:
            parts.append("\nRaises:\n")
            parts.extend(
                [f"  {error.error_type}: {error.docstring}" for error in self.raises]
            )

        if self.returns:
            parts.append("\nReturns:\n")
            parts.extend([f"  {item}" for item in self.returns])

        return "\n\n".join(parts) + "\n"
