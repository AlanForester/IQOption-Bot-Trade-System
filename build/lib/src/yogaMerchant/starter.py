# -*- coding: utf-8 -*-
"""Module for IQ Option API starter."""

import argparse
import logging
import os
import sys
import time
import psycopg2
import redis
import threading

from src.api.iqoption.api import IQOption
from src.yogaMerchant.collector.collector import create_collector
from src.yogaMerchant.config.config import parse_config
from src.yogaMerchant.settings.settings import Settings
from src.yogaMerchant.analyzer.analyzer import Analyzer
from src.yogaMerchant.trader.trader import create_trader


class Starter(object):
    """Calss for IQ Option API starter."""

    def __init__(self, config, setting_id):
        self.config = config

        self.redis = redis.StrictRedis(
            host=self.config.get_db_redis_hostname(),
            port=self.config.get_db_redis_port(),
            db=self.config.get_db_redis_db())

        self.db = psycopg2.connect(
            database=self.config.get_db_postgres_database(),
            user=self.config.get_db_postgres_username(),
            host=self.config.get_db_postgres_hostname(),
            password=self.config.get_db_postgres_password()
        )

        self.api = IQOption(
            self.config.get_broker_hostname(),
            self.config.get_broker_username(),
            self.config.get_broker_password()
        )

        self.settings = Settings(self.db, setting_id)
        if self.settings.error:
            print "Error:", self.settings.error
            sys.exit(1)

        self.create_connection()

    def create_connection(self):
        """Method for create connection to IQ Option API."""
        logger = logging.getLogger(__name__)
        logger.info("Create connection for active '%s'.", self.settings.active["name"])
        self.api.connect()
        logger.info("Successfully connected for active '%s'.", self.settings.active["name"])

    def start_collector(self):
        """Method for start signalers."""
        logger = logging.getLogger("collector")
        logger.info("Create collector for active '%s'.", self.settings.active["name"])
        return create_collector(self.api, self.db, self.settings)


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
    api_file_handler.setLevel(logging.DEBUG)
    api_file_handler.setFormatter(formatter)

    api_logger.addHandler(console_handler)
    api_logger.addHandler(api_file_handler)

    collector_logger = logging.getLogger("collector")
    collector_logger.setLevel(logging.DEBUG)

    collector_file_handler = logging.FileHandler(os.path.join(logs_folder, "collector.log"))
    collector_file_handler.setLevel(logging.DEBUG)
    collector_file_handler.setFormatter(formatter)

    collector_logger.addHandler(console_handler)
    collector_logger.addHandler(collector_file_handler)

    websocket_logger = logging.getLogger("websocket")
    websocket_logger.setLevel(logging.DEBUG)

    websocket_file_handler = logging.FileHandler(os.path.join(logs_folder, "websocket.log"))
    websocket_file_handler.setLevel(logging.DEBUG)
    websocket_file_handler.setFormatter(formatter)

    websocket_logger.addHandler(console_handler)
    websocket_logger.addHandler(websocket_file_handler)


def _create_starter(config, setting_id):
    """Create IQ Option API starter.

    :param config: The instance of :class:`ConfigurationSettings
        <iqpy.configuration.settigns.ConfigurationSettings>`.

    :returns: Instance of :class:`Starter <iqpy.starter.Starter>`.
    """
    return Starter(config, setting_id)


def start():
    """Main method for start."""
    _prepare_logging()
    args = _parse_args()
    config = parse_config(args.config_path)
    starter = _create_starter(config, args.setting_id)
    # Установка реального рублевого баланса
    # starter.api.changebalance(5955150)
    # Установка тестового долларового баланса

    starter.api.changebalance(12074331)
    collector = starter.start_collector()
    trader = create_trader(starter.api, starter.settings, starter.db)
    predictor = Analyzer(trader, starter.redis, starter.db, starter.settings)

    check_prediction_last_time = None
    while True:
        now = time.time()
        quotation = collector.put_quotations()
        if collector.last_quotation and (collector.last_quotation.time > check_prediction_last_time):
            """Запускаем тред на проверку прогноза"""
            check_thread = threading.Thread(target=predictor.check_predictions, args=(collector.last_quotation,))
            check_thread.daemon = True
            check_thread.start()

            check_prediction_last_time = quotation.time
        if quotation:
            """Запускаем тред на запись котировки и ее свечей"""
            analysis_thread = threading.Thread(target=run_analysis, args=(quotation, collector, predictor))
            analysis_thread.daemon = True
            analysis_thread.start()

        tsleep = float(starter.settings.collector_working_interval_sec) - (
            starter.settings.collector_working_interval_sec / 10.0)
        tend = time.time() - now
        if tend > 0:
            tsleep -= tend
        if tsleep > 0:
            time.sleep(tsleep)


def run_analysis(quotation, collector, predictor):
    collector.make_candles(quotation)
    predictor.do_analysis(quotation)


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
    parser.add_argument(
        "-sid", "--setting_id", dest="setting_id", type=int, required=False,
        help="Setting ID."
    )
    return parser.parse_args()


if __name__ == "__main__":
    start()
