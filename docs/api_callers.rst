==============================================
API Callers: Base Classes for Making API Calls
==============================================

The :py:mod:`comb_utils.lib.api_callers` module provides base classes for making API calls. These classes are designed to be extended for specific APIs, allowing for easy customization and reuse of code.

The API callers are designed to be used with the :py:class:`requests` library, which is a popular library for making HTTP requests in Python. The API callers handle the details of making the requests and parsing the responses, whether successful or failed, allowing you to focus on the logic of your application.

NOTE: The current implementation requires you to extend the bases classes by at least overriding :code:`_set_url` to set the API URL you are querying. This will soon be deprecated. The plan is to allow you to pass the URL in at :code:`__init__` time, but this is not yet implemented. See https://github.com/crickets-and-comb/comb_utils/issues/38.

The main classes in this module are:

- :py:class:`comb_utils.lib.api_callers.BaseCaller`: A base class for making API calls with customizable headers and parameters. If using this, you will need to extend it and override :py:meth:`comb_utils.lib.api_callers.BaseCaller._set_request_call`, but the following classes are recommended.

- :py:class:`comb_utils.lib.api_callers.BaseGetCaller`: A base class for making GET API calls. This class is a subclass of :code:`BaseCaller` and provides a default implementation for making GET requests.

- :py:class:`comb_utils.lib.api_callers.BasePostCaller`: A base class for making POST API calls. This class is a subclass of :code:`BaseCaller` and provides a default implementation for making POST requests.

- :py:class:`comb_utils.lib.api_callers.BaseDeleteCaller`: A base class for making DELETE API calls. This class is a subclass of :code:`BaseCaller` and provides a default implementation for making DELETE requests.

The are plans to add additional classes for remaining request calls (i.e., PUT, PATCH, etc.) in the future. For now, you can use :code:`BaseCaller` and override the :code:`BaseCaller._set_request_call` method to implement these calls. See https://github.com/crickets-and-comb/comb_utils/issues/40.

Example Usage
-------------

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

Using a key for authentication
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

Additional Notes
----------------

You may want to override the request wait and timeout times or other parameters. See the :py:class:`comb_utils.lib.api_callers.BaseCaller` class for details on how to do this.
