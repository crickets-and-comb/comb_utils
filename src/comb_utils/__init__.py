"""Top-level init."""

from importlib.metadata import version

from comb_utils.api.public import wait_a_second

try:
    __version__: str = version(__name__)
except Exception:
    __version__ = "unknown"

del version
