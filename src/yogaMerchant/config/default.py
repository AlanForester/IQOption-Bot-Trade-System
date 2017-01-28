# -*- coding: utf-8 -*-
"""Module for default scenario configuration."""

from src.yogaMerchant.config.base import BaseScenario


class DefaultScenario(BaseScenario):
    """Class to prepare default configuration."""

    # pylint: disable=too-few-public-methods

    def __init__(self):
        super(DefaultScenario, self).__init__()

    def _prepare_broker_settings(self):
        """Prepare connection settings configuration section."""
        self.settings.set_broker_hostname("hostname")
        self.settings.set_broker_username("username")
        self.settings.set_broker_password("password")

    def _prepare_db_settings(self):
        """Prepare db settings configuration section."""
        self.settings.set_db_postgres_database("db")
        self.settings.set_db_postgres_hostname("hostname")
        self.settings.set_db_postgres_password("pass")
        self.settings.set_db_postgres_port("5432")
        self.settings.set_db_postgres_username("user")

        self.settings.set_db_redis_hostname("localhost")
        self.settings.set_db_redis_port("6379")
        self.settings.set_db_redis_db("0")

    def create_config(self):
        """Create default configuration."""
        self._prepare_broker_settings()
        self._prepare_db_settings()
