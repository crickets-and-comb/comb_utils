"""Classes for making API calls."""

import logging
from abc import abstractmethod
from collections.abc import Callable
from time import sleep
from typing import Any

import requests
from requests.auth import HTTPBasicAuth
from typeguard import typechecked

from comb_utils.lib.constants import RateLimits

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class BaseCaller:
    """An abstract class for making API calls.

    See :doc:`api_callers`.

    Example:
        .. code:: python

            class MyGetCaller(BaseCaller):
                target_response_value

                _min_wait_seconds: float = 0.1
                # Initialize _wait_seconds and timeout as a class variable.
                # Instances will adjust for class.
                _wait_seconds: float = _min_wait_seconds
                _timeout: float = 10

                def _set_request_call(self):
                    self._request_call = requests.get

                def _set_url(self):
                    self._url = "https://example.com/public/v0.2b/"

                @typechecked
                def _get_API_key(self) -> str:
                    # Wrap your own API key retrieval function here.
                    return my_custom_key_retrieval_function()

                def _handle_200(self):
                    super()._handle_200()
                    self.target_response_value = self.response_json["target_key"]

            my_caller = MyCaller()
            my_caller.call_api()
            target_response_value = my_caller.target_response_value

    .. important::
        You must initialize _wait_seconds, _timeout, and _min_wait_seconds in child classes.
        This allows child class instances to adjust the wait/timeout time for the child class.

    .. warning::
        There is a potential for this to run indefinitely for rate limiting and timeouts.
        It handles them somewhat intelligently, but the assumption is that someone is watching
        this run in the background and will stop it if it runs too long. It will eventually
        at least crash the memory, depending on available memory, mean time to failure, and
        time left in the universe.
    """

    # Set by object:
    #: The JSON from the response.
    response_json: dict[str, Any]
    #: The response from the API call.
    _response: requests.Response

    # Must set in child class with _set*:
    #: The requests call method. (get, post, etc.)
    _request_call: Callable
    #: The URL for the API call.
    _url: str

    # Must set in child class:
    #: The timeout for the API call.
    _timeout: float
    #: The minimum wait time between API calls.
    _min_wait_seconds: float
    #: The wait time between API calls. (Adjusted by instances, at class level.)
    _wait_seconds: float

    # Optionally set in child class, to pass to _request_call if needed:
    #: The kwargs to pass to the requests call.
    _call_kwargs: dict[str, Any] = {}
    #: The scalar to increase wait time on rate limiting.
    _wait_increase_scalar: float = RateLimits.WAIT_INCREASE_SCALAR
    #: The scalar to decrease wait time on success.
    _wait_decrease_scalar: float = RateLimits.WAIT_DECREASE_SECONDS

    @typechecked
    def __init__(self) -> None:  # noqa: ANN401
        """Initialize the BaseCaller object."""
        self._set_request_call()
        self._set_url()

    @abstractmethod
    @typechecked
    def _set_request_call(self) -> None:
        """Set the requests call method.

        requests.get, requests.post, etc.

        Raises:
            NotImplementedError: If not implemented in child class.
        """
        raise NotImplementedError

    @abstractmethod
    @typechecked
    def _set_url(self) -> None:
        """Set the URL for the API call.

        Raises:
            NotImplementedError: If not implemented in child class.
        """
        raise NotImplementedError

    # TODO: bfb_delivery issue 59, comb_utils issue 24: Return "" for no-key API calls?
    @abstractmethod
    @typechecked
    def _get_API_key(self) -> str:
        """Get the API key.

        Raises:
            NotImplementedError: If not implemented in child class.
        """
        raise NotImplementedError

    @typechecked
    def call_api(self) -> None:
        """The main method for making the API call.

        Handle errors, parse response, and decrease class wait time on success.

        Raises:
            ValueError: If the response status code is not expected.
            requests.exceptions.HTTPError: For non-rate-limiting errors.
        """
        # Separated to allow for recursive calls on rate limiting.
        self._call_api()
        self._decrease_wait_time()

    @typechecked
    def _call_api(self) -> None:
        """Wait and make and handle the API call.

        Wrapped separately to allow for recursive calls on rate limiting and timeout.
        """
        sleep(type(self)._wait_seconds)
        self._make_call()
        self._raise_for_status()
        self._parse_response()

    @typechecked
    def _make_call(self) -> None:
        """Make the API call."""
        self._response = self._request_call(
            url=self._url,
            auth=HTTPBasicAuth(self._get_API_key(), ""),
            timeout=self._timeout,
            **self._call_kwargs,
        )

    @typechecked
    def _raise_for_status(self) -> None:
        """Handle error responses.

        For 429 (rate limiting), increases wait time and recursively calls the API.
        For timeout, increases timeout and recursively calls the API.

        Raises:
            requests.exceptions.HTTPError: For non-rate-limiting errors.
            requests.exceptions.Timeout: For timeouts.
        """
        try:
            self._response.raise_for_status()
        except requests.exceptions.HTTPError as http_e:
            if self._response.status_code == 429:
                self._handle_429()
            else:
                self._handle_unknown_error(e=http_e)
        except requests.exceptions.Timeout:
            self._handle_timeout()

    @typechecked
    def _parse_response(self) -> None:
        """Parse the non-error reponse (200).

        Raises:
            ValueError: If the response status code is not expected.
        """
        if self._response.status_code == 200:
            self._handle_200()
        elif self._response.status_code == 204:
            self._handle_204()
        elif self._response.status_code == 429:
            # This is here as well as in the _raise_for_status method because there was a case
            # when the status code was 429 but the response didn't raise.
            self._handle_429()
        else:
            response_dict = get_response_dict(response=self._response)
            raise ValueError(
                f"Unexpected response {self._response.status_code}:\n{response_dict}"
            )

    @typechecked
    def _handle_429(self) -> None:
        """Handle a 429 response.

        Inreases the class wait time and recursively calls the API.
        """
        self._increase_wait_time()
        logger.warning(f"Rate limited. Waiting {type(self)._wait_seconds} seconds to retry.")
        self._call_api()

    @typechecked
    def _handle_timeout(self) -> None:
        """Handle a timeout response.

        Increases the class timeout and recursively calls the API.
        """
        self._increase_timeout()
        response_dict = get_response_dict(response=self._response)
        logger.warning(
            f"Request timed out.\n{response_dict}"
            f"\nTrying again with longer timeout: {type(self)._timeout} seconds."
        )
        self._call_api()

    @typechecked
    def _handle_200(self) -> None:
        """Handle a 200 response.

        Just gets the JSON from the response and sets it to `response_json`.
        """
        self.response_json = self._response.json()

    @typechecked
    def _handle_204(self) -> None:
        """Handle a 204 response.

        Just sets `response_json` to an empty dictionary.
        """
        self.response_json = {}

    @typechecked
    def _handle_unknown_error(self, e: Exception) -> None:
        """Handle an unknown error response.

        Raises:
            Exception: The original error.
        """
        response_dict = get_response_dict(response=self._response)
        err_msg = f"Got {self._response.status_code} response:\n{response_dict}"
        raise requests.exceptions.HTTPError(err_msg) from e

    @typechecked
    def _decrease_wait_time(self) -> None:
        """Decrease the wait time between API calls for whole class."""
        cls = type(self)
        cls._wait_seconds = max(
            cls._wait_seconds * self._wait_decrease_scalar, cls._min_wait_seconds
        )

    @typechecked
    def _increase_wait_time(self) -> None:
        """Increase the wait time between API calls for whole class."""
        cls = type(self)
        cls._wait_seconds = cls._wait_seconds * self._wait_increase_scalar

    @typechecked
    def _increase_timeout(self) -> None:
        """Increase the timeout for the API call for whole class."""
        cls = type(self)
        cls._timeout = cls._timeout * self._wait_increase_scalar


@typechecked
def get_response_dict(response: requests.Response) -> dict[str, Any]:
    """Safely handle a response that may not be JSON."""
    try:
        response_dict: dict = response.json()
    except Exception as e:
        response_dict = {
            "reason": response.reason,
            "additional_notes": "No-JSON response.",
            "No-JSON response exception:": str(e),
        }
    return response_dict
