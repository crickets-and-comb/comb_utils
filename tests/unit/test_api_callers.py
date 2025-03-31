"""A test suite for the API callers module."""

from contextlib import AbstractContextManager, nullcontext
from typing import Any, Final
from unittest.mock import Mock, patch

import pytest
import requests
from typeguard import typechecked

from comb_utils import (
    BaseCaller,
    BaseDeleteCaller,
    BaseGetCaller,
    BasePagedResponseGetter,
    BasePostCaller,
    get_responses,
)
from comb_utils.lib.constants import RateLimits

BASE_URL: Final[str] = "https://example.com/api/test"

_CALLER_DICT: Final[dict[str, type[BaseCaller]]] = {
    "get": BaseGetCaller,
    "post": BasePostCaller,
    "delete": BaseDeleteCaller,
}
_REQUEST_METHOD_DICT: Final[dict[str, str]] = {
    "get": "get",
    "post": "post",
    "delete": "delete",
}


@pytest.mark.parametrize("request_type", ["get", "post", "delete"])
@typechecked
def test_key_call(request_type: str) -> None:
    """Test `call_api` calls `_get_API_key`."""

    class MockCaller(_CALLER_DICT[request_type]):
        """Minimal concrete subclass of BaseCaller for testing."""

        def _set_url(self) -> None:
            """Set a dummy test URL."""
            self._url = BASE_URL

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


@pytest.mark.parametrize("request_type", ["get", "post", "delete"])
@pytest.mark.parametrize(
    "response_sequence, expected_result, error_context",
    [
        (
            [{"json.return_value": {"data": [1, 2, 3]}, "status_code": 200}],
            {"data": [1, 2, 3]},
            nullcontext(),
        ),
        ([{"json.return_value": {}, "status_code": 204}], {}, nullcontext()),
        (
            [
                {
                    "json.return_value": {},
                    "status_code": 429,
                    "raise_for_status.side_effect": requests.exceptions.HTTPError,
                },
                {"json.return_value": {"data": [5, 6]}, "status_code": 200},
            ],
            {"data": [5, 6]},
            nullcontext(),
        ),
        (
            [
                {
                    "json.return_value": {},
                    "status_code": 598,
                    "raise_for_status.side_effect": requests.exceptions.Timeout,
                },
                {"json.return_value": {"data": [7, 8]}, "status_code": 200},
            ],
            {"data": [7, 8]},
            nullcontext(),
        ),
        (
            [
                {
                    "status_code": 400,
                    "raise_for_status.side_effect": requests.exceptions.HTTPError,
                }
            ],
            None,
            pytest.raises(requests.exceptions.HTTPError, match="Got 400 response"),
        ),
        (
            [
                {
                    "json.return_value": {},
                    "status_code": 429,
                    "raise_for_status.side_effect": requests.exceptions.HTTPError,
                },
                {
                    "status_code": 400,
                    "raise_for_status.side_effect": requests.exceptions.HTTPError,
                },
            ],
            None,
            pytest.raises(requests.exceptions.HTTPError, match="Got 400 response"),
        ),
        (
            [
                {
                    "json.return_value": {},
                    "status_code": 598,
                    "raise_for_status.side_effect": requests.exceptions.Timeout,
                },
                {
                    "status_code": 400,
                    "raise_for_status.side_effect": requests.exceptions.HTTPError,
                },
            ],
            None,
            pytest.raises(requests.exceptions.HTTPError, match="Got 400 response"),
        ),
    ],
)
@typechecked
def test_base_caller_response_handling(
    request_type: str,
    response_sequence: list[dict[str, Any]],
    expected_result: dict[str, Any] | None,
    error_context: AbstractContextManager,
) -> None:
    """Test `call_api` handling of different HTTP responses, including retries."""

    class MockCaller(_CALLER_DICT[request_type]):
        """Minimal concrete subclass of BaseCaller for testing."""

        def _set_url(self) -> None:
            """Set a dummy test URL."""
            self._url = BASE_URL

    with patch(f"requests.{request_type}") as mock_request:
        mock_request.side_effect = [Mock(**resp) for resp in response_sequence]
        mock_caller = MockCaller()

        with patch.object(
            mock_caller, "_handle_429", wraps=mock_caller._handle_429
        ) as spy_handle_429, patch.object(
            mock_caller, "_handle_timeout", wraps=mock_caller._handle_timeout
        ) as spy_handle_timeout:

            with error_context:
                mock_caller.call_api()

                assert mock_caller.response_json == expected_result

                if any(resp["status_code"] == 429 for resp in response_sequence):
                    spy_handle_429.assert_called_once()

                if any(resp["status_code"] == 598 for resp in response_sequence):
                    spy_handle_timeout.assert_called_once()

                assert mock_request.call_count == len(response_sequence)


@pytest.mark.parametrize(
    "request_type, response_sequence, expected_wait_time",
    [
        (
            "get",
            [{"status_code": 200, "raise_for_status.side_effect": None}],
            RateLimits.READ_SECONDS,
        ),
        (
            "post",
            [{"status_code": 200, "raise_for_status.side_effect": None}],
            RateLimits.WRITE_SECONDS,
        ),
        (
            "delete",
            [{"status_code": 200, "raise_for_status.side_effect": None}],
            RateLimits.WRITE_SECONDS,
        ),
        (
            "get",
            [{"status_code": 204, "raise_for_status.side_effect": None}],
            RateLimits.READ_SECONDS,
        ),
        (
            "post",
            [{"status_code": 204, "raise_for_status.side_effect": None}],
            RateLimits.WRITE_SECONDS,
        ),
        (
            "delete",
            [{"status_code": 204, "raise_for_status.side_effect": None}],
            RateLimits.WRITE_SECONDS,
        ),
        (
            "get",
            [
                {
                    "status_code": 429,
                    "raise_for_status.side_effect": requests.exceptions.HTTPError,
                },
                {"status_code": 200, "raise_for_status.side_effect": None},
            ],
            RateLimits.READ_SECONDS
            * RateLimits.WAIT_INCREASE_SCALAR
            * RateLimits.WAIT_DECREASE_SECONDS,
        ),
        (
            "post",
            [
                {
                    "status_code": 429,
                    "raise_for_status.side_effect": requests.exceptions.HTTPError,
                },
                {"status_code": 200, "raise_for_status.side_effect": None},
            ],
            RateLimits.WRITE_SECONDS
            * RateLimits.WAIT_INCREASE_SCALAR
            * RateLimits.WAIT_DECREASE_SECONDS,
        ),
        (
            "delete",
            [
                {
                    "status_code": 429,
                    "raise_for_status.side_effect": requests.exceptions.HTTPError,
                },
                {"status_code": 200, "raise_for_status.side_effect": None},
            ],
            RateLimits.WRITE_SECONDS
            * RateLimits.WAIT_INCREASE_SCALAR
            * RateLimits.WAIT_DECREASE_SECONDS,
        ),
    ],
)
@typechecked
def test_base_caller_wait_time_adjusting(
    request_type: str, response_sequence: list[dict[str, Any]], expected_wait_time: float
) -> None:
    """Test request wait time adjustments on rate-limiting."""

    class MockCaller(_CALLER_DICT[request_type]):
        """Minimal concrete subclass of BaseCaller for testing."""

        def _set_url(self) -> None:
            """Set a dummy test URL."""
            self._url = BASE_URL

    with patch(f"requests.{_REQUEST_METHOD_DICT[request_type]}") as mock_request:
        mock_request.side_effect = [Mock(**resp) for resp in response_sequence]

        mock_caller = MockCaller()
        mock_caller.call_api()

        assert MockCaller._wait_seconds == expected_wait_time


@pytest.mark.parametrize(
    "request_type, response_sequence, expected_timeout",
    [
        (
            "get",
            [{"status_code": 200, "raise_for_status.side_effect": None}],
            RateLimits.READ_TIMEOUT_SECONDS,
        ),
        (
            "post",
            [{"status_code": 200, "raise_for_status.side_effect": None}],
            RateLimits.WRITE_TIMEOUT_SECONDS,
        ),
        (
            "delete",
            [{"status_code": 200, "raise_for_status.side_effect": None}],
            RateLimits.WRITE_TIMEOUT_SECONDS,
        ),
        (
            "get",
            [{"status_code": 204, "raise_for_status.side_effect": None}],
            RateLimits.READ_TIMEOUT_SECONDS,
        ),
        (
            "post",
            [{"status_code": 204, "raise_for_status.side_effect": None}],
            RateLimits.WRITE_TIMEOUT_SECONDS,
        ),
        (
            "delete",
            [{"status_code": 204, "raise_for_status.side_effect": None}],
            RateLimits.WRITE_TIMEOUT_SECONDS,
        ),
        (
            "get",
            [
                {
                    "status_code": 598,
                    "raise_for_status.side_effect": requests.exceptions.Timeout,
                },
                {"status_code": 200, "raise_for_status.side_effect": None},
            ],
            RateLimits.READ_TIMEOUT_SECONDS * RateLimits.WAIT_INCREASE_SCALAR,
        ),
        (
            "post",
            [
                {
                    "status_code": 598,
                    "raise_for_status.side_effect": requests.exceptions.Timeout,
                },
                {"status_code": 200, "raise_for_status.side_effect": None},
            ],
            RateLimits.WRITE_TIMEOUT_SECONDS * RateLimits.WAIT_INCREASE_SCALAR,
        ),
        (
            "delete",
            [
                {
                    "status_code": 598,
                    "raise_for_status.side_effect": requests.exceptions.Timeout,
                },
                {"status_code": 200, "raise_for_status.side_effect": None},
            ],
            RateLimits.WRITE_TIMEOUT_SECONDS * RateLimits.WAIT_INCREASE_SCALAR,
        ),
    ],
)
@typechecked
def test_base_caller_timeout_adjusting(
    request_type: str, response_sequence: list[dict[str, Any]], expected_timeout: float
) -> None:
    """Test timeout adjustment on timeout retry."""

    class MockCaller(_CALLER_DICT[request_type]):
        """Minimal concrete subclass of BaseCaller for testing."""

        def _set_url(self) -> None:
            """Set a dummy test URL."""
            self._url = BASE_URL

    with patch(f"requests.{_REQUEST_METHOD_DICT[request_type]}") as mock_request:
        mock_request.side_effect = [Mock(**resp) for resp in response_sequence]

        mock_caller = MockCaller()
        mock_caller.call_api()

        assert MockCaller._timeout == expected_timeout


@pytest.mark.parametrize(
    "response_sequence",
    [
        ([{"status_code": 200, "json.return_value": {"nextPageToken": "abc123"}}]),
        ([{"status_code": 200, "json.return_value": {"nextPageToken": None}}]),
        ([{"status_code": 200, "json.return_value": {}}]),
    ],
)
@typechecked
def test_paged_getter(response_sequence: list[dict[str, Any]]) -> None:
    """Test PagedResponseGetterBFB."""
    with patch("requests.get") as mock_request:
        mock_request.side_effect = [Mock(**resp) for resp in response_sequence]

        page_url = "https://example.com/api/test"
        caller = BasePagedResponseGetter(page_url=page_url)
        caller.call_api()
        assert mock_request.call_args_list[0][1]["url"] == page_url
        assert caller.next_page_salsa == response_sequence[-1]["json.return_value"].get(
            "nextPageToken", None
        )


@pytest.mark.parametrize(
    "responses, expected_result, error_context",
    [
        (
            [
                {
                    "json.return_value": {"data": [1, 2, 3], "nextPageToken": None},
                    "status_code": 200,
                }
            ],
            [{"data": [1, 2, 3], "nextPageToken": None}],
            nullcontext(),
        ),
        (
            [
                {
                    "json.return_value": {"data": [1], "nextPageToken": "abc"},
                    "status_code": 200,
                },
                {
                    "json.return_value": {"data": [2], "nextPageToken": None},
                    "status_code": 200,
                },
            ],
            [{"data": [1], "nextPageToken": "abc"}, {"data": [2], "nextPageToken": None}],
            nullcontext(),
        ),
        (
            [
                {"json.return_value": {}, "status_code": 429},
                {"json.return_value": {}, "status_code": 429},
                {
                    "json.return_value": {"data": [3], "nextPageToken": "asfg"},
                    "status_code": 200,
                },
                {"json.return_value": {}, "status_code": 429},
                {
                    "json.return_value": {"data": [54], "nextPageToken": None},
                    "status_code": 200,
                },
            ],
            [{"data": [3], "nextPageToken": "asfg"}, {"data": [54], "nextPageToken": None}],
            nullcontext(),
        ),
        (
            [
                {
                    "json.return_value": {},
                    "status_code": 400,
                    "raise_for_status.side_effect": requests.exceptions.HTTPError(),
                }
            ],
            None,
            pytest.raises(requests.exceptions.HTTPError),
        ),
        (
            [
                {
                    "json.return_value": {},
                    "status_code": 401,
                    "raise_for_status.side_effect": requests.exceptions.HTTPError(),
                }
            ],
            None,
            pytest.raises(requests.exceptions.HTTPError),
        ),
        (
            [
                {
                    "json.return_value": {},
                    "status_code": 403,
                    "raise_for_status.side_effect": requests.exceptions.HTTPError(),
                }
            ],
            None,
            pytest.raises(requests.exceptions.HTTPError),
        ),
        (
            [
                {
                    "json.return_value": {},
                    "status_code": 404,
                    "raise_for_status.side_effect": requests.exceptions.HTTPError(),
                }
            ],
            None,
            pytest.raises(requests.exceptions.HTTPError),
        ),
        (
            [
                {
                    "json.return_value": {},
                    "status_code": 500,
                    "raise_for_status.side_effect": requests.exceptions.HTTPError(),
                }
            ],
            None,
            pytest.raises(requests.exceptions.HTTPError),
        ),
    ],
)
@typechecked
def test_get_responses_returns(
    responses: list[dict[str, Any]],
    expected_result: list[dict[str, Any]] | None,
    error_context: AbstractContextManager,
) -> None:
    """Test get_responses function."""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = [Mock(**resp) for resp in responses]

        with error_context:
            result = get_responses(url=BASE_URL, paged_response_class=BasePagedResponseGetter)
            assert result == expected_result

        assert mock_get.call_count == len(responses)


@pytest.mark.parametrize(
    "params, responses",
    [
        (
            "",
            [
                {
                    "json.return_value": {"data": [1, 2, 3], "nextPageToken": None},
                    "status_code": 200,
                }
            ],
        ),
        (
            "",
            [
                {
                    "json.return_value": {"data": [1], "nextPageToken": "abc"},
                    "status_code": 200,
                },
                {
                    "json.return_value": {"data": [2], "nextPageToken": None},
                    "status_code": 200,
                },
            ],
        ),
        (
            "",
            [
                {"json.return_value": {}, "status_code": 429},
                {"json.return_value": {}, "status_code": 429},
                {
                    "json.return_value": {"data": [3], "nextPageToken": "asfg"},
                    "status_code": 200,
                },
                {"json.return_value": {}, "status_code": 429},
                {
                    "json.return_value": {"data": [54], "nextPageToken": None},
                    "status_code": 200,
                },
            ],
        ),
        (
            "?filter.startsGte=2015-12-12&filter.startsLTE=2021-06-25",
            [
                {
                    "json.return_value": {"data": [1], "nextPageToken": "abc"},
                    "status_code": 200,
                },
                {
                    "json.return_value": {"data": [2], "nextPageToken": None},
                    "status_code": 200,
                },
            ],
        ),
    ],
)
@typechecked
def test_get_responses_urls(responses: list[dict[str, Any]], params: str) -> None:
    """Test get_responses function."""
    base_url = f"{BASE_URL}{params}"
    with patch("requests.get") as mock_get:
        mock_get.side_effect = [Mock(**resp) for resp in responses]

        _ = get_responses(url=base_url, paged_response_class=BasePagedResponseGetter)

        expected_urls = [base_url]
        last_next_page_token = None
        for resp in responses:
            next_page_token = resp["json.return_value"].get("nextPageToken")
            if next_page_token or (not next_page_token and resp["status_code"] == 429):
                if resp["status_code"] == 429:
                    next_page_token = last_next_page_token
                last_next_page_token = next_page_token

                token_prefix = "?" if "?" not in base_url else "&"
                token = (
                    f"{token_prefix}pageToken={next_page_token}" if next_page_token else ""
                )
                expected_urls.append(f"{base_url}{token}")

        actual_urls = [call[1]["url"] for call in mock_get.call_args_list]

        assert actual_urls == expected_urls
