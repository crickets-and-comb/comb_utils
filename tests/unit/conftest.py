"""Conftest for unit tests."""

from collections.abc import Iterator
from unittest.mock import patch

import pytest
from typeguard import typechecked


@pytest.fixture(autouse=True)
@typechecked
def mock_sleep() -> Iterator[None]:
    """Mock `time.sleep` to avoid waiting in tests."""
    with patch("comb_utils.lib.api_callers.sleep"):
        yield
