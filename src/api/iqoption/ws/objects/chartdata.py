# -*- coding: utf-8 -*-
"""Модуль для получения котировок."""

from src.api.iqoption.ws.objects.base import Base


class Quotation(object):
    """Класс котировки IQOption."""

    def __init__(self, chart_data):

        self.__chart_data = chart_data

    @property
    def time(self):
        """Получение времени котировки.
        """
        time = 0
        if 'time' in self.__chart_data:
            time = self.__chart_data["time"]
        return time

    @property
    def value(self):
        """Получение значения котировки.
        """
        value = 0
        if 'value' in self.__chart_data:
            value = self.__chart_data["value"]
        return value

    @property
    def sell(self):
        """Значение продажи актива.
        """
        sell = 0
        if 'sell' in self.__chart_data:
            sell = self.__chart_data["sell"]
        return sell

    @property
    def buy(self):
        """Значение покупки актива.
        """
        buy = 0
        if 'buy' in self.__chart_data:
            buy = self.__chart_data["buy"]
        return buy

    @property
    def show_value(self):
        """Отображаемое значение котировки.
        """
        show_value = 0
        if 'show_value' in self.__chart_data:
            show_value = self.__chart_data["show_value"]
        return show_value


class ChartData(Base):
    """Класс для IQ Option ChartData объекта вебсокета."""

    def __init__(self):
        super(ChartData, self).__init__()
        self.__name = "newChartData"
        self.__chart_data = None

    @property
    def chart_data(self):
        """Данные графика.
        """
        return self.__chart_data

    @chart_data.setter
    def chart_data(self, chart_data):
        """Method to set candles data."""
        self.__chart_data = chart_data

    @property
    def quotation(self):
        """Экземпляо котировки.

        :returns: Котировка.
        """
        return Quotation(self.__chart_data)

