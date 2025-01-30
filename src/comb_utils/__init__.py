"""Top-level init."""

from importlib.metadata import version

from comb_utils.lib import DocString, ErrorDocString

try:
    __version__: str = version(__name__)
except Exception:
    __version__ = "unknown"

del version
