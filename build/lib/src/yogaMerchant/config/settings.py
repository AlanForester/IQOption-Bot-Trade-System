# -*- coding: utf-8 -*-
"""Module for configuration settings."""

import json
import logging

import src.yogaMerchant.config.constants as config_constants


class Settings(object):
    """Class for configuration settings."""

    # pylint: disable=too-many-public-methods

    def __init__(self):
        self.__config_data = {}

    @property
    def config_data(self):
        """Property to get configuration data.

        :returns: The configuration data dictionary.
        """
        return self.__config_data

    @property
    def _broker_settings(self):
        """Property to get broker settings.

        :returns: The broker settings dictionary.
        """
        return self.__config_data.setdefault(config_constants.BROKER_SETTINGS_KEY, {})

    def set_broker_hostname(self, broker_hostname):
        """Set broker hostname.

        :param broker_hostname: The broker hostname.
        """
        self._broker_settings[config_constants.BROKER_HOSTNAME_KEY] = broker_hostname

    def get_broker_hostname(self):
        """Get broker hostname.

        :returns: The broker hostname.
        """
        return self._broker_settings[config_constants.BROKER_HOSTNAME_KEY]

    def set_broker_username(self, broker_username):
        """Set broker username.

        :param broker_username: The broker username.
        """
        self._broker_settings[config_constants.BROKER_USERNAME_KEY] = broker_username

    def get_broker_username(self):
        """Get broker username.

        :returns: The broker username.
        """
        return self._broker_settings[config_constants.BROKER_USERNAME_KEY]

    def set_broker_password(self, broker_password):
        """Set broker password.

        :param broker_password: The broker password.
        """
        self._broker_settings[config_constants.BROKER_PASSWORD_KEY] = broker_password

    def get_broker_password(self):
        """Get broker password.

        :returns: The broker password.
        """
        return self._broker_settings[config_constants.BROKER_PASSWORD_KEY]

    @property
    def _analyzer_settings(self):
        return self.__config_data.setdefault(config_constants.ANALYZER_KEY, {})

    def set_analyzer_interval(self, analyzer_interval):
        self._analyzer_settings[config_constants.ANALYZER_INTERVAL] = analyzer_interval

    def get_analyzer_interval(self):
        return self._analyzer_settings[config_constants.ANALYZER_INTERVAL]

    def set_analyzer_min_deep(self, min_deep):
        self._analyzer_settings[config_constants.ANALYZER_MIN_DEEP] = min_deep

    def get_analyzer_min_deep(self):
        return self._analyzer_settings[config_constants.ANALYZER_MIN_DEEP]

    def set_analyzer_deep(self, analyzer_deep):
        self._analyzer_settings[config_constants.ANALYZER_DEEP] = analyzer_deep

    def get_analyzer_deep(self):
        return self._analyzer_settings[config_constants.ANALYZER_DEEP]

    def set_analyzer_bid_times(self, analyzer_bid_times):
        self._analyzer_settings[config_constants.ANALYZER_BID_TIMES] = analyzer_bid_times

    def get_analyzer_bid_times(self):
        return self._analyzer_settings[config_constants.ANALYZER_BID_TIMES]

    def set_analyzer_prediction_expire(self, expire_candles):
        self._analyzer_settings[config_constants.ANALYZER_PREDICTION_EXPIRE] = expire_candles

    def get_analyzer_prediction_expire(self):
        return self._analyzer_settings[config_constants.ANALYZER_PREDICTION_EXPIRE]

    def set_analyzer_prediction_delay(self, delay):
        self._analyzer_settings[config_constants.ANALYZER_PREDICTION_DELAY] = delay

    def get_analyzer_prediction_delay(self):
        return self._analyzer_settings[config_constants.ANALYZER_PREDICTION_DELAY]

    @property
    def _trader_settings(self):
        return self.__config_data.setdefault(config_constants.TRADER_KEY, {})

    def set_trader_chance(self, trader_chance):
        self._trader_settings[config_constants.TRADER_CHANCE] = trader_chance

    def get_trader_chance(self):
        return self._trader_settings[config_constants.TRADER_CHANCE]

    def set_trader_repeats(self, repeats):
        self._trader_settings[config_constants.TRADER_REPEATS] = repeats

    def get_trader_repeats(self):
        return self._trader_settings[config_constants.TRADER_REPEATS]

    @property
    def _collector_settings(self):
        return self.__config_data.setdefault(config_constants.COLLECTOR_KEY, {})

    def set_collector_candles_durations(self, candles_durations):
        self._collector_settings[config_constants.COLLECTOR_CANDLES_DURATIONS] = candles_durations

    def get_collector_candles_durations(self):
        return self._collector_settings[config_constants.COLLECTOR_CANDLES_DURATIONS]

    @property
    def _active(self):
        return self.__config_data

    def set_active(self, active):
        self._active[config_constants.ACTIVE_KEY] = active

    def get_active(self):
        return self._active[config_constants.ACTIVE_KEY]

    def get_active_id(self):
        return self._active[config_constants.ACTIVE_KEY]

    @property
    def _db_settings(self):
        return self.__config_data.setdefault(config_constants.DB_SETTINGS_KEY, {
            config_constants.DB_POSTGRES_KEY: {},
            config_constants.DB_REDIS_KEY: {}
        })

    def get_db_postgres_username(self):
        return self._db_settings[config_constants.DB_POSTGRES_KEY][config_constants.DB_POSTGRES_USERNAME]

    def set_db_postgres_username(self, db_postgres_username):
        self._db_settings[config_constants.DB_POSTGRES_KEY][
            config_constants.DB_POSTGRES_USERNAME] = db_postgres_username

    def get_db_postgres_password(self):
        return self._db_settings[config_constants.DB_POSTGRES_KEY][config_constants.DB_POSTGRES_PASSWORD]

    def set_db_postgres_password(self, db_postgres_password):
        self._db_settings[config_constants.DB_POSTGRES_KEY][
            config_constants.DB_POSTGRES_PASSWORD] = db_postgres_password

    def get_db_postgres_hostname(self):
        return self._db_settings[config_constants.DB_POSTGRES_KEY][config_constants.DB_POSTGRES_HOSTNAME]

    def set_db_postgres_hostname(self, db_postgres_hostname):
        self._db_settings[config_constants.DB_POSTGRES_KEY][
            config_constants.DB_POSTGRES_HOSTNAME] = db_postgres_hostname

    def get_db_postgres_port(self):
        return self._db_settings[config_constants.DB_POSTGRES_KEY][config_constants.DB_POSTGRES_PORT]

    def set_db_postgres_port(self, db_postgres_port):
        self._db_settings[config_constants.DB_POSTGRES_KEY][config_constants.DB_POSTGRES_PORT] = db_postgres_port

    def get_db_postgres_database(self):
        return self._db_settings[config_constants.DB_POSTGRES_KEY][config_constants.DB_POSTGRES_DATABASE]

    def set_db_postgres_database(self, db_postgres_database):
        self._db_settings[config_constants.DB_POSTGRES_KEY][
            config_constants.DB_POSTGRES_DATABASE] = db_postgres_database

    def get_db_redis_hostname(self):
        return self._db_settings[config_constants.DB_REDIS_KEY][config_constants.DB_REDIS_HOSTNAME]

    def set_db_redis_hostname(self, db_redis_hostname):
        self._db_settings[config_constants.DB_REDIS_KEY][
            config_constants.DB_REDIS_HOSTNAME] = db_redis_hostname

    def get_db_redis_port(self):
        return self._db_settings[config_constants.DB_REDIS_KEY][config_constants.DB_REDIS_PORT]

    def set_db_redis_port(self, db_redis_port):
        self._db_settings[config_constants.DB_REDIS_KEY][
            config_constants.DB_REDIS_PORT] = db_redis_port

    def get_db_redis_db(self):
        return self._db_settings[config_constants.DB_REDIS_KEY][config_constants.DB_REDIS_DB]

    def set_db_redis_db(self, db_redis_db):
        self._db_settings[config_constants.DB_REDIS_KEY][
            config_constants.DB_REDIS_DB] = db_redis_db

    def write_config(self, config_path):
        """Write configuration to file.

        :param config_path: The path to config file.
        """
        logger = logging.getLogger(__name__)
        logger.info("Create a new configuration file '%s'.", config_path)
        with open(config_path, "wb") as config_file:
            json.dump(self.__config_data, config_file, indent=4, sort_keys=True)

    def load_config(self, config_path):
        """Create configuration object from file.

        :param config_path: The path to configuration file.
        """
        logger = logging.getLogger(__name__)
        logger.info("Load configuration from file '%s'.", config_path)
        with open(config_path, "rb") as config_file:
            self.__config_data = json.load(config_file)
