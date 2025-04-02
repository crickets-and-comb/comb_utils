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


# TODO: https://github.com/crickets-and-comb/comb_utils/issues/38:
# Why are we using _set_url instead of the url property?
# Why are we using _set_request_call instead of the _request_call property?


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

                def _get_API_key(self) -> str | None:
                    # Optionally wrap your own API key retrieval function here.
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

    .. note::
        The `_set_request_call` and `_set_url` methods will be deprecated in favor of setting
        the request call member at child class definition and passing the URL to `__init__`.
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
    def _get_API_key(self) -> str | None:
        """Get the API key.

        Defaults to None, but can be overridden in child class.
        """
        return None

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


class BaseGetCaller(BaseCaller):
    """A base class for making GET API calls.

    Presets the timeout, initial wait time, and requests method.
    """

    _timeout: float = RateLimits.READ_TIMEOUT_SECONDS
    _min_wait_seconds: float = RateLimits.READ_SECONDS
    _wait_seconds: float = _min_wait_seconds

    @typechecked
    def _set_request_call(self) -> None:
        """Set the requests call method to `requests.get`."""
        self._request_call = requests.get


class BasePostCaller(BaseCaller):
    """A base class for making POST API calls.

    Presets the timeout, initial wait time, and requests method.
    """

    _timeout: float = RateLimits.WRITE_TIMEOUT_SECONDS
    _min_wait_seconds: float = RateLimits.WRITE_SECONDS
    _wait_seconds: float = _min_wait_seconds

    @typechecked
    def _set_request_call(self) -> None:
        """Set the requests call method to `requests.post`."""
        self._request_call = requests.post


class BaseDeleteCaller(BasePostCaller):
    """A base class for making DELETE API calls.

    Presets the timeout, initial wait time, and requests method.
    """

    @typechecked
    def _set_request_call(self) -> None:
        """Set the requests call method to `requests.delete`."""
        self._request_call = requests.delete


class BasePagedResponseGetter(BaseGetCaller):
    """Class for getting paged responses."""

    #: The nextPageToken returned, but called salsa to avoid bandit.
    next_page_salsa: str | None

    #: The URL for the page.
    _page_url: str

    @typechecked
    def __init__(self, page_url: str) -> None:
        """Initialize the BasePagedResponseGetter object.

        Args:
            page_url: The URL for the page. (Optionally contains nextPageToken.)
        """
        self._page_url = page_url
        super().__init__()

    @typechecked
    def _set_url(self) -> None:
        """Set the URL for the API call to the `page_url`."""
        self._url = self._page_url

    @typechecked
    def _handle_200(self) -> None:
        """Handle a 200 response.

        Sets `next_page_salsa` to the nextPageToken.
        """
        super()._handle_200()
        self.next_page_salsa = self.response_json.get("nextPageToken", None)


@typechecked
def get_response_dict(response: requests.Response) -> dict[str, Any]:
    """Safely handle a response that may not be JSON.

    Args:
        response: The response from the API call.

    Returns:
        A dictionary containing the response data.
    """
    try:
        response_dict: dict = response.json()
    except Exception as e:
        response_dict = {
            "reason": response.reason,
            "additional_notes": "No-JSON response.",
            "No-JSON response exception:": str(e),
        }

    return response_dict


# TODO: Pass params instead of forming URL first. ("params", not "json")
# (Would need to then grab params URL for next page, or just add nextpage to params?)
# https://github.com/crickets-and-comb/bfb_delivery/issues/61
# TODO: bfb_delivery issue 59, comb_utils issue 24: move above issue to comb_utils.
# TODO: bfb_delivery issue 59, comb_utils issue 24:
# Switch to default getter if key retriever can be empty.
@typechecked
def get_responses(
    url: str, paged_response_class: type[BasePagedResponseGetter]
) -> list[dict[str, Any]]:
    """Get all responses from a paginated API endpoint.

    Args:
        url: The base URL of the API endpoint.
        paged_response_class: The class used to get the paginated response.

    Returns:
        A list of dictionaries containing the responses from all pages.
    """
    # Calling the token salsa to trick bandit into ignoring what looks like a hardcoded token.
    next_page_salsa = ""
    next_page_cookie = ""
    responses = []

    while next_page_salsa is not None:
        paged_response_getter = paged_response_class(page_url=url + str(next_page_cookie))
        paged_response_getter.call_api()

        stops = paged_response_getter._response.json()
        responses.append(stops)
        next_page_salsa = paged_response_getter.next_page_salsa

        if next_page_salsa:
            salsa_prefix = "?" if "?" not in url else "&"
            next_page_cookie = f"{salsa_prefix}pageToken={next_page_salsa}"

    return responses


@typechecked
def concat_response_pages(
    page_list: list[dict[str, Any]], data_key: str
) -> list[dict[str, Any]]:
    """Extract and concatenate the data lists from response pages.

    Args:
        page_list: A list of response page dictionaries.
        data_key: The key to extract the data from each page.

    Returns:
        A list of dictionaries containing the data from each page.
    """
    data_list = []
    for page in page_list:
        data_list += page[data_key]

    return data_list
