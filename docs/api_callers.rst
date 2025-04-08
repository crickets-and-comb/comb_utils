==============================================
API Callers: Base Classes for Making API Calls
==============================================

The :py:mod:`comb_utils.lib.api_callers` module provides base classes for making API calls, along with a few helper functions. These classes are designed to be extended for specific APIs, allowing for easy customization and reuse of code.

The API callers wrap the :py:class:`requests` library, which is a popular library for making HTTP requests in Python. The API callers handle the details of making the requests and parsing the responses, whether successful or failed, allowing you to focus on the logic of your application.

.. attention::
    
    The current implementation requires you to extend the bases classes by at least overriding :code:`_set_url` to set the API URL you are querying. This will soon be deprecated. The plan is to allow you to pass the URL in at :code:`__init__` time, but this is not yet implemented. See https://github.com/crickets-and-comb/comb_utils/issues/38.

Base classes
############

The main classes in this module are:

- :py:class:`comb_utils.lib.api_callers.BaseCaller`: A base class for making API calls with customizable headers and parameters. If using this, you will need to extend it and override :py:meth:`comb_utils.lib.api_callers.BaseCaller._set_request_call`, but the following classes are recommended.

- :py:class:`comb_utils.lib.api_callers.BaseGetCaller`: A base class for making GET API calls. This class is a subclass of :code:`BaseCaller` and provides a default implementation for making GET requests.

- :py:class:`comb_utils.lib.api_callers.BasePostCaller`: A base class for making POST API calls. This class is a subclass of :code:`BaseCaller` and provides a default implementation for making POST requests.

- :py:class:`comb_utils.lib.api_callers.BaseDeleteCaller`: A base class for making DELETE API calls. This class is a subclass of :code:`BaseCaller` and provides a default implementation for making DELETE requests.

- :py:class:`comb_utils.lib.api_callers.BasePagedResponseGetter`: A base class for making paginated GET calls. This class is a subclass of :code:`BaseGetCaller` and provides a default implementation for making paginated GET requests. It returns the next page token and the response data. This is useful for APIs that return large amounts of data in multiple pages. To get the most out of this class, use in conjunction with :py:func:`comb_utils.lib.api_callers.get_responses` and :py:func:`comb_utils.lib.api_callers.concat_response_pages`, which will handle the pagination for you (see :ref:`helper-functions` below).

The are plans to add additional classes for remaining request calls (i.e., PUT, PATCH, etc.) in the future. For now, you can use :code:`BaseCaller` and override the :code:`BaseCaller._set_request_call` method to implement these calls. See https://github.com/crickets-and-comb/comb_utils/issues/40.

Example usage
*************

To use the API callers, you need to create a subclass of one of the base classes and implement the required methods. Here is an example of how to create a custom API caller for a hypothetical API:

.. code:: python

    from comb_utils import BaseGetCaller

    class MyAPICaller(BaseGetCaller):

        # Optionally create a custom member to store the response value.
        # The, override the `_handle_200` method to set this value.
        target_response_value

        def _set_url(self):
            self.url = "https://api.example.com/data"

        # Optionally override `_handle_200` to process the response.
        def _handle_200(self):
            super()._handle_200()
            self.target_response_value = self.response_json["target_key"]
                    
    my_caller = MyCaller()
    my_caller.call_api()
    target_response_value = my_caller.target_response_value

Here we call the example.com API. We optionally extract a specific value from the JSON response. The :code:`call_api` method is inherited from the base class and handles the details of making the request and processing the response.

See :ref:`helper-functions` examples below for more details on how to handle paginated responses.

Using a key for authentication
******************************

Using a key for authentication is common in APIs. You can override the :code:`_get_API_key` method to return the key. The base class will then construct the authentication for you. Here is an example of how to do this:

.. code:: python

    from comb_utils import BaseGetCaller

    class MyAPICaller(BaseGetCaller):

        def _set_url(self):
            self.url = "https://api.example.com/data"

        def _get_API_key(self):
            return my_custom_key_retrieval_function()

    my_caller = MyCaller()
    my_caller.call_api()

.. _helper-functions:

Helper functions
################

The :py:mod:`comb_utils.lib.api_callers` module provides a few helper functions for working with the base callers. These functions are designed to make it easier to work with the API callers and provide additional functionality.

- :py:func:`comb_utils.lib.api_callers.get_response_dict`: This function takes a response object and returns a dictionary containing the status code, headers, and JSON data. This is useful for debugging and logging purposes. You may wish to use it within your own custom API caller class or within a script to generically handle response data. The base callers use this function to handle errors and timeouts.

- :py:func:`comb_utils.lib.api_callers.get_responses`: This function gets all the responses from a paginated API endpoint using the :py:class:`comb_utils.lib.api_callers.BaseDeleteCaller` class. Returns a list of all the response pages. use this in conjunction with :py:func:`comb_utils.lib.api_callers.concat_response_pages` to get all the data from a paginated API endpoint.

- :py:func:`comb_utils.lib.api_callers.concat_response_pages`: This function concatenates the response pages from a paginated API endpoint into a single list. This is useful for working with APIs that return large amounts of data in multiple pages. Use this in conjunction with :py:func:`comb_utils.lib.api_callers.get_responses` to get all the data from a paginated API endpoint.

Example usage
*************

Here are examples of how to use the helper functions.

Getting generic responses: ``get_response_dict``
================================================

.. code:: python

    from comb_utils import get_response_dict

    response = requests.get("https://api.example.com/data")
    response_dict = get_response_dict(response)

    print(response_dict["status_code"])  # 200
    print(response_dict["headers"])  # {'Content-Type': 'application/json', ...}
    print(response_dict["json"])  # {'key': 'value', ...}

Handling paginated responses: ``get_responses`` and ``concat_response_pages``
=============================================================================

.. code:: python

    from comb_utils import (
        BasePagedResponseGetter,
        concat_response_pages,
        get_responses,
    )

    # Create a custom API caller for the paginated endpoint
    class MyBaseKeyRetriever:

        def _get_API_key(self):
            return my_custom_key_retrieval_function()

    class MyAPICaller(BaseKeyRetriever, BasePagedResponseGetter):

    # Get all the responses from a paginated API endpoint.
    all_responses = get_responses(url="https://api.example.com/data", paged_response_class=MyAPICaller)

    # Put the responses records from all the pages into a single document.
    concatenated_data = concat_response_pages(page_list=all_responses, data_key="data")

    print(concatenated_data)  # [{'key': 'value', ...}, {'key': 'value', ...}, ...]

Additional Notes
################

You may want to override the request wait and timeout times or other parameters. See the :py:class:`comb_utils.lib.api_callers.BaseCaller` class for details on how to do this.
