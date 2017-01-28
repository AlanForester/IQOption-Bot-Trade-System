# -*- coding: utf-8 -*-
"""Модуль для обработки и записи приходящих с коллектора данных."""


class DataHandler(object):
    """Класс для обработчика данных."""

    def __init__(self, db, active):
        self.db = db
        self.active = active

    def check_quotation(self, quotation):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM quotations WHERE ts=%s AND active_id=%s LIMIT 1", [quotation.time, self.active])
        row = cursor.fetchone()
        if row:
            return True
        else:
            return False

    def save_quotations(self, quotations):
        cursor = self.db.cursor()
        query = "INSERT INTO quotations (ts,active_id,sell,buy,value) VALUES " + \
                ",".join(cursor.mogrify("(%s,%s,%s,%s,%s)", x) for x in quotations) + \
                " ON CONFLICT (ts,active_id) DO NOTHING"

        cursor.execute(query)
        self.db.commit()

    def save_quotation(self, quotation):
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO quotations (ts, active_id, sell, buy, value) "
                       "VALUES (%s, %s, %s, %s, %s) ON CONFLICT (ts, active_id) DO NOTHING",
                       (quotation.time, self.active, quotation.sell, quotation.buy, quotation.value))

        self.db.commit()
        return quotation

    def make_candles(self, quotation, candles_durations):
        cursor = self.db.cursor()
        candles = []
        for duration in candles_durations:
            cursor.execute("SELECT "
                           "MAX(value) OVER w AS high, "
                           "MIN(value) OVER w AS low, "
                           "first_value(value) OVER w AS open, "
                           "last_value(value) OVER w AS close, "
                           "AVG(value) OVER w AS average "
                           "FROM quotations WHERE ts>=%s AND active_id=%s AND ts<%s "
                           "WINDOW w AS () "
                           "ORDER BY ts DESC LIMIT 1",
                           [quotation.time - duration, self.active, quotation.time])
            rows = cursor.fetchone()
            high = 0
            low = 0
            open = 0
            close = 0
            avg = 0
            if rows:
                if rows[0]:
                    high = rows[0]
                if rows[1]:
                    low = rows[1]
                if rows[2]:
                    open = rows[2]
                if rows[3]:
                    close = rows[3]
                if rows[4]:
                    avg = rows[4]

            range = high - low
            change = open - close

            last_avg_cursor = self.db.cursor()
            last_avg_cursor.execute("SELECT "
                                    "first_value(value) OVER w AS open, "
                                    "last_value(value) OVER w AS close "
                                    "FROM quotations WHERE ts>=%s AND active_id=%s AND ts<%s "
                                    "WINDOW w AS () "
                                    "ORDER BY ts DESC LIMIT 1",
                                    (quotation.time - duration * 2, self.active, quotation.time - duration))
            last_rel_row = last_avg_cursor.fetchone()

            rel_open = 0
            rel_close = 0

            if last_rel_row:
                if last_rel_row[0]:
                    rel_open = last_rel_row[0]
                if last_rel_row[1]:
                    rel_close = last_rel_row[1]

            rel_change = rel_open - rel_close

            change_power = 0
            if rel_change != 0:
                change_power = change / (rel_change / 100)

            candles.append((
                self.active,
                quotation.time - duration,
                quotation.time,
                duration,
                high,
                low,
                open,
                close,
                range,
                change,
                avg,
                0,  # average_power
                0,  # range_power
                change_power,  # change_power
                0,  # high_power
                0  # low_power
            ))
        self.save_candles(candles)

    def save_candles(self, candles):
        cursor = self.db.cursor()
        query = "INSERT INTO candles (active_id,from_ts,till_ts,duration,high,low,open,close,range,change,average," \
                "average_power,range_power,change_power,high_power,low_power) VALUES " + \
                ",".join(cursor.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", x) for x in candles) + \
                " ON CONFLICT (active_id,from_ts,till_ts) DO NOTHING"

        cursor.execute(query)
        self.db.commit()
