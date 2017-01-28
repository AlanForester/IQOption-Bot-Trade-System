import time
import json

from src.yogaMerchant.helpers.active import ActiveHelper


class SettingsDefault(object):
    def __init__(self, db):
        self.db = db
        self.active_helper = ActiveHelper(db)

        self.id = None
        self.name = "Default"
        self.is_default = True
        self.created_at = time.time()
        self.updated_at = time.time()
        self.analyzer_bid_times = json.dumps([{"time": 180, "purchase": 0}])
        self.analyzer_deep = 6
        self.analyzer_min_deep = 6
        self.analyzer_prediction_expire = json.dumps([{"history_duration": 0, "expire": 0}])
        self.save_prediction_if_exists = False
        self.collector_candles_durations = json.dumps([30])
        self.collector_working_interval_sec = 1
        self.trader_min_chance = 60
        self.trader_min_repeats = 2
        self.trader_max_count_orders_for_expiration_time = 1
        self.trader_delay_on_trend = 0

        active_name = "EURUSD"
        self.active = {
            "name": active_name,
            "db_id": self.active_helper.get_db_id_by_name(active_name),
            "platform_id": self.active_helper.get_platform_id_by_name(active_name)
        }

    def _load_setting(self, raw):
        self.id = raw[0]
        self.name = raw[1]
        self.is_default = raw[2]
        self.created_at = raw[3]
        self.updated_at = raw[4]
        active_name = self.active_helper.get_name_by_db_id(raw[5])
        self.active = {
            "name": active_name,
            "db_id": raw[5],
            "platform_id": self.active_helper.get_platform_id_by_name(active_name)
        }
        self.analyzer_bid_times = raw[6]
        self.analyzer_deep = raw[7]
        self.analyzer_min_deep = raw[8]
        self.analyzer_prediction_expire = raw[9]
        self.save_prediction_if_exists = raw[10]
        self.collector_candles_durations = raw[11]
        self.collector_working_interval_sec = raw[12]
        self.trader_min_chance = raw[13]
        self.trader_min_repeats = raw[14]
        self.trader_max_count_orders_for_expiration_time = raw[15]
        self.trader_delay_on_trend = raw[16]
