"""Constants for the comb_utils library."""

from typing import Final

from comb_utils.lib.metadata import FunctionMetaDataFormatter


class RateLimits:
    """Default rate limits for :doc:`api_callers`."""

    READ_TIMEOUT_SECONDS: Final[float] = 10
    READ_SECONDS: Final[float] = 0.1
    WAIT_DECREASE_SECONDS: Final[float] = 0.6
    WAIT_INCREASE_SCALAR: Final[float] = 2
    WRITE_SECONDS: Final[float] = 0.2
    WRITE_TIMEOUT_SECONDS: Final[float] = 10


# A constant class to store all function metadata (docstrings and argument defaults)
class FunctionMetaData:
    """Docstrings and Defaults for the public API."""

    GET_RESPONSE_DICT: Final = FunctionMetaDataFormatter(
        opening="""
Safely handle a response that may not be JSON.
""",
        args={
            "response": "The response from the API call.",
        },
        defaults={},
        returns=["A dictionary containing the response data."],
        raises=[],
    )

    GET_RESPONSES: Final = FunctionMetaDataFormatter(
        opening="""
Get all responses from a paginated API endpoint.
""",
        args={
            "url": "The base URL of the API endpoint.",
            "paged_response_class": "The class used to get the paginated response.",
            "params": "The dictionary of query string parameters.",
        },
        defaults={
            "params": None,
        },
        returns=["A list of dictionaries containing the responses from all pages."],
        raises=[],
    )

    CONCAT_RESPONSE_PAGES: Final = FunctionMetaDataFormatter(
        opening="""
Extract and concatenate the data lists from response pages.
""",
        args={
            "page_list": "A list of response page dictionaries.",
            "data_key": "The key to extract the data from each page.",
        },
        defaults={},
        returns=["A list of dictionaries containing the data from each page."],
        raises=[],
    )
