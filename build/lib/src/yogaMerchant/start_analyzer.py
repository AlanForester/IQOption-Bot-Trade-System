# -*- coding: utf-8 -*-
"""Module for IQ Option API starter."""

import argparse
import logging
import os
import psycopg2

from src.api.iqoption.api import IQOption

from src.yogaMerchant.config.config import parse_config
from src.yogaMerchant.analyzer.analyzer import create_analyzer


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

    def analyzer(self):
        analyzer = create_analyzer(self.api, self.active, self.db)
        return analyzer


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

    starter_file_handler = logging.FileHandler(os.path.join(logs_folder, "analyzer.log"))
    starter_file_handler.setLevel(logging.INFO)
    starter_file_handler.setFormatter(formatter)

    starter_logger.addHandler(console_handler)
    starter_logger.addHandler(starter_file_handler)


def _create_starter(config):
    return Starter(config)


def start():
    """Main method for start."""
    _prepare_logging()
    args = _parse_args()
    config = parse_config(args.config_path)
    starter = _create_starter(config)
    analyzer = starter.analyzer()


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
