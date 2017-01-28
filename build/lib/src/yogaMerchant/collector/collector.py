# -*- coding: utf-8 -*-
"""Module for IQ Option API signaler."""
import logging
from src.yogaMerchant.collector.dataHandler.dataHandler import DataHandler


class Collector(object):
    """Class for  IQ Option API signaler."""

    def __init__(self, api, db, settings):
        self.api = api
        self.db = db
        self.settings = settings
        logger = logging.getLogger("collector")
        self.api.setactives([settings.active["platform_id"]])
        logger.info("Collector for active '%s' started.", settings.active["name"])
        self.last_quotation = None
        self.data_handler = DataHandler(db, settings.active["db_id"])

    def put_quotations(self):
        data = self.api.chartData
        if data.chart_data:
            check_row = self.data_handler.check_quotation(data.quotation)
            if not check_row:
                self.last_quotation = self.data_handler.save_quotation(data.quotation)
                return self.last_quotation

    def make_candles(self, quotation):
        self.data_handler.make_candles(quotation, self.settings.collector_candles_durations)


def create_collector(api, db, settings):
    logger = logging.getLogger("collector")
    logger.info("Create collector for active '%s'.", settings.active["name"])
    return Collector(api, db, settings)
