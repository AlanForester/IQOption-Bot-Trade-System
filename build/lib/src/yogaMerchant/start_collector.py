# -*- coding: utf-8 -*-
"""Module for IQ Option API starter."""

import argparse
import logging
import os
import psycopg2
import time
import redis
import json
import threading

from src.api.iqoption.api import IQOption

from src.yogaMerchant.config.config import parse_config
from src.yogaMerchant.collector.collector import create_collector
from src.yogaMerchant.collector.predictor.predictor import Predictor
from src.yogaMerchant.trader.trader import create_trader
from src.yogaMerchant.models.signal import Signal


class Starter(object):
    """Calss for IQ Option API starter."""

    def __init__(self, config):
        """
        :param config: The instance of :class:`Settings
            <iqpy.settings.settigns.Settings>`.
        """
        self.config = config
        self.active = self.config.get_active()
        self.broker = self.config.get_broker()
        self.api = IQOption(
            self.config.get_broker_hostname(),
            self.config.get_broker_username(),
            self.config.get_broker_password()
        )
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.create_connection()
        self.db = psycopg2.connect(
            database=self.config.get_db_postgres_database(),
            user=self.config.get_db_postgres_username(),
            host=self.config.get_db_postgres_hostname(),
            password=self.config.get_db_postgres_password()
        )

    def create_connection(self):
        """Method for create connection to IQ Option API."""
        logger = logging.getLogger(__name__)
        logger.info("Create connection for active '%s'.", self.active)
        self.api.connect()
        logger.info("Successfully connected for active '%s'.", self.active)

    def start_collector(self):
        """Method for start signalers."""
        logger = logging.getLogger(__name__)
        logger.info("Create collectors.")
        collector = create_collector(self.api, self.active, self.db)
        collector.start()
        return collector


def _prepare_logging():
    """Prepare logging for starter."""
    formatter = logging.Formatter(
        "%(asctime)s:%(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logs_folder = "logs"
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    starter_logger = logging.getLogger(__name__)
    starter_logger.setLevel(logging.INFO)

    starter_file_handler = logging.FileHandler(os.path.join(logs_folder, "starter.log"))
    starter_file_handler.setLevel(logging.INFO)
    starter_file_handler.setFormatter(formatter)

    starter_logger.addHandler(console_handler)
    starter_logger.addHandler(starter_file_handler)

    api_logger = logging.getLogger("iqapi")

    api_file_handler = logging.FileHandler(os.path.join(logs_folder, "iqapi.log"))
    api_file_handler.setLevel(logging.INFO)
    api_file_handler.setFormatter(formatter)

    api_logger.addHandler(console_handler)
    api_logger.addHandler(api_file_handler)

    collector_logger = logging.getLogger("collector")
    collector_logger.setLevel(logging.INFO)

    collector_file_handler = logging.FileHandler(os.path.join(logs_folder, "collector.log"))
    collector_file_handler.setLevel(logging.DEBUG)
    collector_file_handler.setFormatter(formatter)

    collector_logger.addHandler(console_handler)
    collector_logger.addHandler(collector_file_handler)

    websocket_logger = logging.getLogger("websocket")

    websocket_file_handler = logging.FileHandler(os.path.join(logs_folder, "websocket.log"))
    websocket_file_handler.setLevel(logging.INFO)
    websocket_file_handler.setFormatter(formatter)

    websocket_logger.addHandler(console_handler)
    websocket_logger.addHandler(websocket_file_handler)


def _create_starter(config):
    """Create IQ Option API starter.

    :param config: The instance of :class:`ConfigurationSettings
        <iqpy.configuration.settigns.ConfigurationSettings>`.

    :returns: Instance of :class:`Starter <iqpy.starter.Starter>`.
    """
    return Starter(config)


def start():
    """Main method for start."""
    _prepare_logging()
    args = _parse_args()
    config = parse_config(args.config_path)
    starter = _create_starter(config)
    # Установка реального рублевого баланса
    # starter.api.changebalance(5955150)
    # Установка тестового долларового баланса
    starter.api.changebalance(12074331)
    collector = starter.start_collector()
    trader = create_trader(starter.api, starter.active)
    trader.start()
    print vars(starter.api.timesync)
    predictor = Predictor(trader, starter.redis, starter.db, starter.active)
    last_quotation = None
    # trader.trade(Signal("put", 10, 10, "turbo"))
    while True:
        starter.api.timesync.expiration_time = 1
        starter.api.buy(
            10,
            10,
            "turbo",
            "call")
        quotation = collector.put_quotations()
        if quotation:
            last_quotation = quotation
            predictor_thread = threading.Thread(target=predictor.get_candles(quotation, ), args=(), kwargs={})
            predictor_thread.start()

        if last_quotation:
            predictor.check_predictions(last_quotation)
        time.sleep(1)


def _parse_args():
    """
    Parse commandline arguments.

    :returns: Instance of :class:`argparse.Namespace`.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config_path", dest="config_path", type=str, required=True,
        help="Path to new configuration file."
    )
    return parser.parse_args()


if __name__ == "__main__":
    start()
