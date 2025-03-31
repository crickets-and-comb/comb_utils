"""Constants for the comb_utils library."""

from typing import Final


class RateLimits:
    """Default rate limits for :doc:`api_callers`."""

    READ_TIMEOUT_SECONDS: Final[float] = 10
    READ_SECONDS: Final[float] = 0.1
    WAIT_DECREASE_SECONDS: Final[float] = 0.6
    WAIT_INCREASE_SCALAR: Final[float] = 2
    WRITE_SECONDS: Final[float] = 0.2
    WRITE_TIMEOUT_SECONDS: Final[float] = 10
