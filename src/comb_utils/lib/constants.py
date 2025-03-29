"""Constants for the comb_utils library."""

from typing import Final


class RateLimits:
    """Default rate limits for :doc:`api_callers`."""

    READ_TIMEOUT_SECONDS: Final[float] = 10
    READ_SECONDS: Final[float] = 1 / 10
    WAIT_DECREASE_SECONDS: Final[float] = 0.6
    WAIT_INCREASE_SCALAR: Final[float] = 2
    WRITE_SECONDS: Final[float] = 1 / 5
    WRITE_TIMEOUT_SECONDS: Final[float] = 10