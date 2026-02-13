import abc
import requests
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from collections.abc import Callable as Callable
from comb_utils.lib import errors as errors
from comb_utils.lib.constants import RateLimits as RateLimits
from typeguard import typechecked
from typing import Any

logger: Incomplete

class BaseCaller(metaclass=abc.ABCMeta):
    '''An abstract class for making API calls.

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
    '''
    response_json: dict[str, Any]
    _response: requests.Response
    _request_call: Callable
    _url: str
    _timeout: float
    _min_wait_seconds: float
    _wait_seconds: float
    _call_kwargs: dict[str, Any]
    _wait_increase_scalar: float
    _wait_decrease_scalar: float
    @typechecked
    def __init__(self) -> None:
        """Initialize the BaseCaller object."""
    @abstractmethod
    @typechecked
    def _set_request_call(self) -> None:
        """Set the requests call method.

        requests.get, requests.post, etc.

        Raises:
            NotImplementedError: If not implemented in child class.
        """
    @abstractmethod
    @typechecked
    def _set_url(self) -> None:
        """Set the URL for the API call.

        Raises:
            NotImplementedError: If not implemented in child class.
        """
    @typechecked
    def call_api(self) -> None:
        """The main method for making the API call.

        Handle errors, parse response, and decrease class wait time on success.

        Raises:
            ValueError: If the response status code is not expected.
            requests.exceptions.HTTPError: For non-rate-limiting errors.
        """
    @typechecked
    def _call_api(self) -> None:
        """Wait and make and handle the API call.

        Wrapped separately to allow for recursive calls on rate limiting and timeout.
        """
    @typechecked
    def _make_call(self) -> None:
        """Make the API call."""
    @typechecked
    def _raise_for_status(self) -> None:
        """Handle error responses.

        For 429 (rate limiting), increases wait time and recursively calls the API.
        For timeout, increases timeout and recursively calls the API.

        Raises:
            requests.exceptions.HTTPError: For non-rate-limiting errors.
            requests.exceptions.Timeout: For timeouts.
        """
    @typechecked
    def _parse_response(self) -> None:
        """Parse the non-error reponse (200).

        Raises:
            ValueError: If the response status code is not expected.
        """
    @typechecked
    def _get_API_key(self) -> str:
        """Get the API key.

        Defaults to None, but can be overridden in child class.
        """
    @typechecked
    def _handle_429(self) -> None:
        """Handle a 429 response.

        Inreases the class wait time and recursively calls the API.
        """
    @typechecked
    def _handle_timeout(self) -> None:
        """Handle a timeout response.

        Increases the class timeout and recursively calls the API.
        """
    @typechecked
    def _handle_200(self) -> None:
        """Handle a 200 response.

        Just gets the JSON from the response and sets it to `response_json`.
        """
    @typechecked
    def _handle_204(self) -> None:
        """Handle a 204 response.

        Just sets `response_json` to an empty dictionary.
        """
    @typechecked
    def _handle_unknown_error(self, e: Exception) -> None:
        """Handle an unknown error response.

        Raises:
            Exception: The original error.
        """
    @typechecked
    def _decrease_wait_time(self) -> None:
        """Decrease the wait time between API calls for whole class."""
    @typechecked
    def _increase_wait_time(self) -> None:
        """Increase the wait time between API calls for whole class."""
    @typechecked
    def _increase_timeout(self) -> None:
        """Increase the timeout for the API call for whole class."""

class BaseGetCaller(BaseCaller, metaclass=abc.ABCMeta):
    """A base class for making GET API calls.

    Presets the timeout, initial wait time, and requests method.
    """
    _timeout: float
    _min_wait_seconds: float
    _wait_seconds: float
    _request_call: Incomplete
    @typechecked
    def _set_request_call(self) -> None:
        """Set the requests call method to `requests.get`."""

class BasePostCaller(BaseCaller, metaclass=abc.ABCMeta):
    """A base class for making POST API calls.

    Presets the timeout, initial wait time, and requests method.
    """
    _timeout: float
    _min_wait_seconds: float
    _wait_seconds: float
    _request_call: Incomplete
    @typechecked
    def _set_request_call(self) -> None:
        """Set the requests call method to `requests.post`."""

class BaseDeleteCaller(BasePostCaller, metaclass=abc.ABCMeta):
    """A base class for making DELETE API calls.

    Presets the timeout, initial wait time, and requests method.
    """
    _request_call: Incomplete
    @typechecked
    def _set_request_call(self) -> None:
        """Set the requests call method to `requests.delete`."""

class BasePagedResponseGetter(BaseGetCaller):
    """Class for getting paged responses."""
    next_page_salsa: str | None
    _page_url: str
    _params: dict[str, str] | None
    @typechecked
    def __init__(self, page_url: str, params: dict[str, str] | None = None) -> None:
        """Initialize the BasePagedResponseGetter object.

        Args:
            page_url: The URL for the page. (Optionally contains nextPageToken.)
            params: The dictionary of query string parameters.
        """
    _url: Incomplete
    @typechecked
    def _set_url(self) -> None:
        """Set the URL for the API call to the `page_url`."""
    @typechecked
    def _check_duplicates_in_URL(self) -> None:
        """Check for duplicate values in query string parameters."""
    @typechecked
    def _add_params_to_URL(self) -> None:
        """Add query string parameters to `page_url`."""
    @typechecked
    def _handle_200(self) -> None:
        """Handle a 200 response.

        Sets `next_page_salsa` to the nextPageToken.
        """

@typechecked
def get_response_dict(response: requests.Response) -> dict[str, Any]:
    """Safely handle a response that may not be JSON.

    Args:
        response: The response from the API call.

    Returns:
        A dictionary containing the response data.
    """
@typechecked
def get_responses(url: str, paged_response_class: type[BasePagedResponseGetter], params: dict[str, str] | None = None) -> list[dict[str, Any]]:
    """Get all responses from a paginated API endpoint.

    Args:
        url: The base URL of the API endpoint.
        paged_response_class: The class used to get the paginated response.
        params: The dictionary of query string parameters.

    Returns:
        A list of dictionaries containing the responses from all pages.
    """
@typechecked
def concat_response_pages(page_list: list[dict[str, Any]], data_key: str) -> list[dict[str, Any]]:
    """Extract and concatenate the data lists from response pages.

    Args:
        page_list: A list of response page dictionaries.
        data_key: The key to extract the data from each page.

    Returns:
        A list of dictionaries containing the data from each page.
    """
