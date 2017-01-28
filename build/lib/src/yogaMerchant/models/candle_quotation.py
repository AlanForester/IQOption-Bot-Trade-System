# -*- coding: utf-8 -*-
"""Module for IQ Option API signal."""


class Quotation(object):
    """Class for IQ Option API signal."""
    # pylint: disable=too-few-public-methods

    def __init__(self, candle_data):
        self._data = candle_data

    @property
    def time(self):
        """Получение времени котировки.
        """
        time = self._data[0]
        return time

    @property
    def value(self):
        """Получение значения котировки.
        """
        value = self._data[1]
        return value

    @property
    def sell(self):
        """Значение продажи актива.
        """
        sell = self._data[2]
        return sell

    @property
    def buy(self):
        """Значение покупки актива.
        """
        buy = self._data[3]
        return buy

    @property
    def show_value(self):
        """Отображаемое значение котировки.
        """
        show_value = self._data[4]
        return show_value
