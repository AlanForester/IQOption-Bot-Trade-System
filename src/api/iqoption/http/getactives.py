# -*- coding: utf-8 -*-
"""Module for IQ Option http option/init/all resource."""

from src.api.iqoption.http.resource import Resource


class GetActives(Resource):
    """Class for IQ option option/init/all resource."""
    # pylint: disable=too-few-public-methods

    url = "/option/init/all"

    def _get(self):
        """Send get request for IQ Option API getregdata http resource.

        :returns: The instace of :class:`requests.Response`.
        """
        return self.send_http_request("GET")

    def __call__(self):
        """Method to get IQ Option API getregdata http request.

        :returns: The instance of :class:`requests.Response`.
        """
        return self._get()
