"""Top-level init."""

from importlib.metadata import version

try:
    __version__: str = version(__name__)
except Exception:
    __version__ = "unknown"

del version
