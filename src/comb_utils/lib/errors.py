"""Module for custom exceptions."""


class CombUtilsError(Exception):
    """Base class for exceptions in this module."""


class DuplicateKeysDetected(CombUtilsError):
    """Raised when a user enters a query string key twice."""
