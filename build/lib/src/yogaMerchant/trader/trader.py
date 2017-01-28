# -*- coding: utf-8 -*-
"""Module for IQ Option API trader."""

import logging
import time


class Trader(object):
    """Calss for  IQ Option API trader."""

    def __init__(self, api, settings, db, is_test):
        self.is_test = is_test
        self.api = api
        self.db = db
        self.settings = settings

    def check_probability(self, call_count, put_count, last_call, used_count, delay):
        result = None
        if (call_count > 0 or put_count > 0) and delay == 0:
            call_amount = 0.0
            put_amount = 0.0
            if call_count:
                call_amount = call_count
            if put_count:
                put_amount = put_count

            all_amounts = call_amount + put_amount
            all_condition = float(all_amounts) / 100
            if call_amount < put_amount:
                # print "Amounts put: ", float(put_amount)/all_condition, all_condition
                if last_call <= -self.settings.trader_min_repeats:
                    if float(put_amount) / all_condition > float(self.settings.trader_min_chance):
                        if not self.is_test:
                            print "Amounts:", used_count, call_amount, put_amount, last_call
                            print "Put:", float(put_amount) / all_condition, float(self.settings.trader_min_chance)
                        result = 'put'
            else:
                if call_amount > put_amount:
                    # print "Amounts call: ", float(call_amount)/all_condition, all_condition
                    if last_call >= self.settings.trader_min_repeats:
                        if float(call_amount) / all_condition > float(self.settings.trader_min_chance):
                            if not self.is_test:
                                print "Amounts:", used_count, call_amount, put_amount, last_call
                                print "Call: ", float(call_amount) / all_condition, float(
                                    self.settings.trader_min_chance)
                            result = 'call'
        return result

    def trade(self, minute, price, direction, prediction_id, expiration_at, cost):
        cursor = self.db.cursor()
        """Проверка сделанных ставок до времени экспирации по активу"""
        cursor.execute("SELECT COUNT(*) FROM orders WHERE active_id=%s AND expiration_at=%s", (
            self.settings.active["db_id"],
            expiration_at
        ))
        bids_count = cursor.fetchone()
        if bids_count[0] < self.settings.trader_max_count_orders_for_expiration_time:
            self.api.timesync.expiration_time = minute
            """Method for trade."""
            print "Trade " + direction + ": " + time.strftime("%b %d %Y %H:%M:%S")
            self.api.buy(
                price,
                self.settings.active["platform_id"],
                "turbo",
                direction)

            d = 0
            if direction == 'call':
                d = 1
            if direction == 'put':
                d = -1

            cursor.execute(
                "INSERT INTO orders (active_id,prediction_id,created_at,expiration_at,direction,"
                "created_cost,expiration_cost,change,closed_at,bid_cost) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (
                    self.settings.active["db_id"],
                    prediction_id,
                    int(time.time()),
                    expiration_at,
                    d,
                    cost,
                    0.0,
                    0.0,
                    0,
                    float(price)
                ))
        else:
            print "Pass " + direction + ": " + time.strftime("%b %d %Y %H:%M:%S")


def create_trader(api, settings, db, is_test=False):
    return Trader(api, settings, db, is_test)
