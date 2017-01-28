# -*- coding: utf-8 -*-
"""Module for IQ Option API starter."""

import argparse
import time
import logging
import os
import psycopg2
import threading
import src.api.iqoption.constants as api_constants

from src.api.iqoption.api import IQOption
from src.yogaMerchant.config.config import parse_config
from src.yogaMerchant.helpers.active import ActiveHelper
from src.yogaMerchant.collector.dataHandler.dataHandler import DataHandler
from src.yogaMerchant.models.candle_quotation import Quotation


class HistoryCollector(object):
    """Calss for IQ Option API starter."""

    def __init__(self, config):
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

        active_name = config.get_active()
        active_helper = ActiveHelper(self.db)
        self.active = {
            "name": active_name,
            "db_id": active_helper.get_id_by_name(active_name),
            "platform_id": api_constants.ACTIVES[active_name]
        }

        self.create_connection()

    def create_connection(self):
        """Method for create connection to IQ Option API."""
        logger = logging.getLogger(__name__)
        logger.info("Create connection.")
        self.api.connect()
        self.api.setactives([self.active["platform_id"]])
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


def _create_starter(config):
    """Create IQ Option API starter.

    :param config: The instance of :class:`ConfigurationSettings
        <iqpy.configuration.settigns.ConfigurationSettings>`.

    :returns: Instance of :class:`Starter <iqpy.starter.Starter>`.
    """
    return HistoryCollector(config)


def start():
    """Main method for start."""
    _prepare_logging()
    args = _parse_args()
    history_duration = args.duration
    from_time = args.from_time
    chunk = 3000
    config = parse_config(args.config_path)
    starter = _create_starter(config)
    data_handler = DataHandler(starter.db, starter.active["db_id"])

    if not from_time:
        from_time = int(time.time())
        current_time = int(time.time())
    else:
        current_time = from_time

    old_data = None
    old_quotation_value = None
    while history_duration > 0:
        minus = chunk
        if history_duration - chunk < 0:
            minus = chunk + (history_duration - chunk)
        last_ts = current_time - history_duration
        first_ts = last_ts + chunk
        if first_ts > current_time:
            first_ts = current_time
        starter.api.getcandles(starter.active["platform_id"], 1, last_ts, first_ts, chunk)

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
                            starter.active["db_id"],
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
            thread = threading.Thread(target=make_quotations_and_candles, args=(data_handler, quotations, config))
            thread.daemon = True
            thread.start()


def make_quotations_and_candles(data_handler, quotations, config):
    data_handler.save_quotations(quotations)
    for quotation in quotations:
        model = Quotation([quotation[0], quotation[4]])
        data_handler.make_candles(model, config.get_collector_candles_durations())


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
    return parser.parse_args()


if __name__ == "__main__":
    start()
