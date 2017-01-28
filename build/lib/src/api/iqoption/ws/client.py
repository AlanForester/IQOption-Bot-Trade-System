# -*- coding: utf-8 -*-
"""Module for IQ option websocket."""

import json
import logging
import websocket


class WebsocketClient(object):
    """Class for work with IQ option websocket."""

    def __init__(self, api):
        """
        :param api: The instance of :class:`IQOptionAPI <iqapi.api.IQOptionAPI>`.
        """
        self.api = api
        self.wss = websocket.WebSocketApp(
            self.api.wss_url, on_message=self.on_message,
            on_error=self.on_error, on_close=self.on_close,
            on_open=self.on_open)
        self.is_closed = False

    def on_message(self, wss, message):
        """Method to process websocket messages."""
        # pylint: disable=unused-argument
        logger = logging.getLogger(__name__)
        logger.debug(message)

        message = json.loads(str(message))

        if message["name"] == "timeSync":
            self.api.timesync.server_timestamp = message["msg"]

        if message["name"] == "profile":
            self.api.profile.balance = message["msg"]["balance"]

        if message["name"] == "candles":
            self.api.candles.candles_data = message["msg"]["data"]

        if message["name"] == "newChartData":
            self.api.chartData.chart_data = message["msg"]

    @staticmethod
    def on_error(wss, error):
        """Method to process websocket errors."""
        # pylint: disable=unused-argument
        logger = logging.getLogger("websocket")
        logger.error(error)

    def on_open(self, wss):
        """Method to process websocket open."""
        # pylint: disable=unused-argument
        logger = logging.getLogger("websocket")
        logger.info("Websocket client connected.")
        self.is_closed = False

    def on_close(self, wss):
        """Method to process websocket close."""
        # pylint: disable=unused-argument
        logger = logging.getLogger("websocket")
        logger.info("Websocket connection closed.")
        self.is_closed = True
