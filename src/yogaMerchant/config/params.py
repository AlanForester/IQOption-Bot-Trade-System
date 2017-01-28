# -*- coding: utf-8 -*-
"""Module for configuration settings."""

import json
import logging

import src.yogaMerchant.config.constants as config_constants


class Params(object):
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
    def _db_settings(self):
        return self.__config_data.setdefault(config_constants.DB_SETTINGS_KEY, {
            config_constants.DB_POSTGRES_KEY: {},
            config_constants.DB_REDIS_KEY: {}
        })

    """Постгрес конфиг"""
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

    """Редис конфиг"""
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
