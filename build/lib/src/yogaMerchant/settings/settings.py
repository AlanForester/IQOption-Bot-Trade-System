import json
from src.yogaMerchant.settings.default import SettingsDefault


class Settings(SettingsDefault):
    def __init__(self, db, setting_id=None):
        super(Settings, self).__init__(db)
        self.error = None
        cursor = db.cursor()
        if setting_id:
            cursor.execute("SELECT * FROM settings WHERE id=%s", (setting_id,))
            setting_row = cursor.fetchone()
            if setting_row:
                self._load_setting(setting_row)
            else:
                self.error = "Setting not found in db"
        else:
            cursor.execute("SELECT * FROM settings WHERE is_default=%s", (True,))
            setting_row = cursor.fetchone()
            if setting_row:
                self._load_setting(setting_row)
            else:
                cursor.execute(
                    "INSERT INTO settings (name, is_default, created_at, updated_at, active_id, "
                    "analyzer_bid_times, analyzer_deep, analyzer_min_deep, analyzer_prediction_expire, "
                    "analyzer_save_prediction_if_exists, collector_candles_durations, "
                    "collector_working_interval_sec, trader_min_chance, trader_min_repeats, "
                    "trader_max_count_orders_for_expiration_time, trader_delay_on_trend) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *", (
                        self.name, self.is_default, self.created_at, self.updated_at, int(self.active["db_id"]),
                        self.analyzer_bid_times, self.analyzer_deep, self.analyzer_min_deep,
                        self.analyzer_prediction_expire, self.save_prediction_if_exists,
                        self.collector_candles_durations, self.collector_working_interval_sec,
                        self.trader_min_chance, self.trader_min_repeats,
                        self.trader_max_count_orders_for_expiration_time, self.trader_delay_on_trend
                    ))
                setting_row = cursor.fetchone()

                print setting_row
                self.db.commit()
                if setting_row:
                    self._load_setting(setting_row)
                else:
                    self.error = "Setting insert error"
