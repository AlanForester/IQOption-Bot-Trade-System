# -*- coding: utf-8 -*-
"""Module for default scenario configuration."""

from src.yogaMerchant.config.base import BaseScenario


class DefaultScenario(BaseScenario):
    """Class to prepare default configuration."""

    # pylint: disable=too-few-public-methods

    def __init__(self):
        super(DefaultScenario, self).__init__()

    def _prepare_analyzer(self):
        self.settings.set_analyzer_interval(5)
        self.settings.set_analyzer_deep(2)
        self.settings.set_analyzer_min_deep(2)
        self.settings.set_analyzer_bid_times([
            {"time": 60, "purchase": 30},
            {"time": 120, "purchase": 0},
            {"time": 180, "purchase": 0},
            {"time": 240, "purchase": 0},
            {"time": 300, "purchase": 0},
        ])
        self.settings.set_analyzer_prediction_expire([
            {"history_duration": 0, "expire": 0},
            {"history_duration": 5, "expire": 30},
        ])
        self.settings.set_analyzer_prediction_delay(1)
        self.settings.set_analyzer_prediction_save_if_exists(False)

    def _prepare_trader(self):
        self.settings.set_trader_chance(80)
        self.settings.set_trader_repeats(2)
        self.settings.set_trader_max_bids_for_expiration_time(1)

    def _prepare_collector(self):
        self.settings.set_collector_candles_durations([
            5,  # 5 секунд
            10,  # 10 секунд
            15,  # 15 секунд
            30,  # 30 секунд
            60,  # 1 минута
            120,  # 2 минуты
            300,  # 5 минут
            600,  # 10 минут
            900,  # 15 минут
            1800,  # 30 минут
            3600,  # 1 час
            7200,  # 2 часа
            14400,  # 4 часа
            28800,  # 8 часов
            43200,  # 12 часов
            86400,  # 1 день
        ])

    def _prepare_broker_settings(self):
        """Prepare connection settings configuration section."""
        self.settings.set_broker_hostname("hostname")
        self.settings.set_broker_username("username")
        self.settings.set_broker_password("password")

    def _prepare_active(self):
        """Prepare trade settings configuration section."""
        self.settings.set_active("USDRUB")

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
        self._prepare_active()
        self._prepare_db_settings()
        self._prepare_analyzer()
        self._prepare_trader()
        self._prepare_collector()
