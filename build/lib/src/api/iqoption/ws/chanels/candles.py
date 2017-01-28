# -*- coding: utf-8 -*-
"""Module for IQ option candles websocket chanel."""

from src.api.iqoption.ws.chanels.base import Base


class GetCandles(Base):
    """Класс для IQ option свечей."""
    # pylint: disable=too-few-public-methods

    name = "candles"

    def __call__(self, active_id, duration, fromts, tillts, chunk=25):
        """Method to send message to candles websocket chanel.

        :param active_id: The active identifier.
        :param duration: The candle duration.
        """
        data = {"active_id": active_id,
                "duration": duration,
                "chunk_size": chunk,
                "from": fromts,
                "till": tillts}

        self.send_websocket_request(self.name, data)
