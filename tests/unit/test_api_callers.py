"""A test suite for the API callers module."""

from typing import Any, Final
from unittest.mock import Mock, patch

import pytest
from typeguard import typechecked

from comb_utils import BaseCaller, BaseDeleteCaller, BaseGetCaller, BasePostCaller

_CALLER_DICT: Final[dict[str, type[BaseCaller]]] = {
    "get": BaseGetCaller,
    "post": BasePostCaller,
    "delete": BaseDeleteCaller,
}


@pytest.mark.parametrize("request_type", ["get", "post", "delete"])
@typechecked
def test_key_call(request_type: str) -> None:
    """Test `call_api` handling of different HTTP responses, including retries."""

    class MockCaller(_CALLER_DICT[request_type]):
        """Minimal concrete subclass of BaseCaller for testing."""

        def _set_url(self) -> None:
            """Set a dummy test URL."""
            self._url = "https://example.com/api/test"

    response_sequence: list[dict[str, Any]] = [
        {"json.return_value": {"data": [1, 2, 3]}, "status_code": 200}
    ]

    with patch(f"requests.{request_type}") as mock_request:
        mock_request.side_effect = [Mock(**resp) for resp in response_sequence]
        mock_caller = MockCaller()

        with patch.object(
            mock_caller, "_get_API_key", wraps=mock_caller._get_API_key
        ) as spy_handle_get_API_key:
            mock_caller.call_api()
            spy_handle_get_API_key.assert_called_once()
