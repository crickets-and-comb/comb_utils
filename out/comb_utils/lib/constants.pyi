from typing import Final

class RateLimits:
    """Default rate limits for :doc:`api_callers`."""
    READ_TIMEOUT_SECONDS: Final[float]
    READ_SECONDS: Final[float]
    WAIT_DECREASE_SECONDS: Final[float]
    WAIT_INCREASE_SCALAR: Final[float]
    WRITE_SECONDS: Final[float]
    WRITE_TIMEOUT_SECONDS: Final[float]
