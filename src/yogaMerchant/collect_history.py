# -*- coding: utf-8 -*-
"""Module for IQ Option API starter."""

import argparse
import time
import logging
import os
import psycopg2
import threading
import sys
from src.api.iqoption.api import IQOption
from src.yogaMerchant.config.config import parse_config
from src.yogaMerchant.collector.dataHandler.dataHandler import DataHandler
from src.yogaMerchant.models.candle_quotation import Quotation
from src.yogaMerchant.settings.settings import Settings


class HistoryCollector(object):
    """Calss for IQ Option API starter."""

    def __init__(self, config, setting_id):
        self.config = config

        self.api = IQOption(
            self.config.get_broker_hostname(),
            self.config.get_broker_username(),
            self.config.get_broker_password()
        )

        self.db = psycopg2.connect(
            database=config.get_db_postgres_database(),
            user=config.get_db_postgres_username(),
            host=config.get_db_postgres_hostname(),
            password=config.get_db_postgres_password()
        )

        self.settings = Settings(self.db, setting_id)
        if self.settings.error:
            print "Error:", self.settings.error
            sys.exit(1)

        self.create_connection()

    def create_connection(self):
        """Method for create connection to IQ Option API."""
        logger = logging.getLogger(__name__)
        logger.info("Create connection.")
        self.api.connect()
        self.api.setactives([self.settings.active["platform_id"]])
        logger.info("Successfully connected.")


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
    return HistoryCollector(config, setting_id)


def start():
    """Main method for start."""
    _prepare_logging()
    args = _parse_args()
    history_duration = args.duration
    from_time = args.from_time
    chunk = 3000
    config = parse_config(args.config_path)

    # TODO: Сделать реконнект подобно как в анализаторе
    starter = _create_starter(config, args.setting_id)
    data_handler = DataHandler(starter.db, starter.settings.active["db_id"])

    if not from_time:
        from_time = int(time.time())
        current_time = int(time.time())
    else:
        current_time = from_time

    old_data = None
    old_quotation_value = None
    total_threads = []
    while history_duration > 0:
        minus = chunk
        if history_duration - chunk < 0:
            minus = chunk + (history_duration - chunk)
        last_ts = current_time - history_duration
        first_ts = last_ts + chunk
        if first_ts > current_time:
            first_ts = current_time
        starter.api.getcandles(starter.settings.active["platform_id"], 1, last_ts, first_ts, chunk)

        quotations = []
        start_get_candles_time = int(time.time())
        while True:

            last_get_candles_time = int(time.time())
            last_get_time = last_get_candles_time - start_get_candles_time
            if int(last_get_time) > 3 and starter.api.websocket_client.is_closed:
                starter.create_connection()

            data = starter.api.candles.candles_data
            if (data and (old_data and (old_data[0][0] != data[0][0]))) or (data and not old_data):
                old_data = data
                for quotation in data:
                    value = float((quotation[1] + quotation[2]) / 2) / 1000000.0
                    if not old_quotation_value or old_quotation_value != value:
                        old_quotation_value = value
                        quotations.append((
                            quotation[0],
                            starter.settings.active["db_id"],
                            0,
                            0,
                            value
                        ))
                break

        history_duration -= minus
        from_time -= minus
        if len(quotations) > 0:
            print "Time:", int(time.time()), "From:", int(quotations[0][0]), "Inserted:", len(
                quotations), "Remaining:", history_duration
            thread = threading.Thread(target=make_quotations_and_candles,
                                      args=(data_handler, quotations, starter.settings))
            thread.daemon = True
            thread.start()
            total_threads.append(thread)

    while len(get_alive_threads(total_threads)) > 0:
        continue


def make_quotations_and_candles(data_handler, quotations, settings):
    data_handler.save_quotations(quotations)
    for quotation in quotations:
        model = Quotation([quotation[0], quotation[4]])
        data_handler.make_candles(model, settings.collector_candles_durations)


def get_alive_threads(threads):
    result_threads = []
    if len(threads) > 0:
        for thread in threads:
            if thread.isAlive():
                result_threads.append(thread)
    return result_threads


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
        "-d", "--duration", dest="duration", type=int, required=True,
        help="Duration history"
    )
    parser.add_argument(
        "-f", "--from_time", dest="from_time", type=int, required=False,
        help="From time"
    )
    parser.add_argument(
        "-sid", "--setting_id", dest="setting_id", type=int, required=False,
        help="Setting ID."
    )
    return parser.parse_args()


if __name__ == "__main__":
    start()
