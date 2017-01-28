# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta


class TimeHelper(object):
    @staticmethod
    def get_remaining_second_to_minute(from_time):
        return int(60 - int(datetime.fromtimestamp(from_time).strftime(
            '%S')))

    @staticmethod
    def get_expiration_time(from_time, bid_time):
        current_time = datetime.fromtimestamp(int(from_time))
        delta = current_time + timedelta(seconds=bid_time["time"])
        expiration = delta.replace(second=0, microsecond=0)
        expiration_ts = time.mktime(expiration.timetuple())
        return expiration_ts
