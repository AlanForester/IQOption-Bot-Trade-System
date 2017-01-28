# -*- coding: utf-8 -*-
import datetime
import time
import json
from src.yogaMerchant.helpers.fibonacci import FibonacciHelper


class Predictor(object):
    def __init__(self, trader, redis, db, active):
        self.db = db
        self.active = active
        self.redis = redis
        self.trader = trader
        self.admissions = FibonacciHelper.get_uniq_unsigned_array(20)
        self.time_bids = [
                             60,
                             120,
                             180,
                             240,
                             300
                         ],
        self.deep = 2

    def make_predictions(self, quotation):
        cursor = self.db.cursor()
        cursor.execute("SELECT change_power,duration,till_ts FROM candles WHERE till_ts=%s AND active_id=%s",
                       [quotation.time, self.active])
        candles = cursor.fetchall()
        step = 5
        time_left = int((60 - int(datetime.datetime.fromtimestamp(quotation.time).strftime('%S'))) / step) * step

        for candle in candles:
            for admission in self.admissions:
                if int(candle[0]) <= admission:
                    for tb in self.time_bids:
                        tl = tb - (60 - time_left)
                        cursor.execute(
                            "SELECT * FROM quotation_predictions "
                            "WHERE admission=%s AND duration=%s AND time_left=%s AND time_bid=%s;",
                            [admission, candle[1], tl, tb])
                        prediction = cursor.fetchone()
                        if not prediction:
                            if tl > tb / 2:  # Время / 2 = Время доступной торговли
                                cursor.execute(
                                    "INSERT INTO quotation_predictions "
                                    "(admission, infinity, time_bid, time_left, used_count, calls_count, puts_count, "
                                    "last_call, ts, duration) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [
                                        admission, True, tb, tl, 1, 0, 0, False, candle[2], candle[1]])
                                self.db.commit()
                        else:
                            # Trader
                            chance_percent = 75

                            # amount_percent = float(prediction[5])/100
                            # if amount_percent:
                            #     call_chance = int(prediction[6]/amount_percent)
                            #     put_chance = int(prediction[7]/amount_percent)
                            #     print amount_percent, call_chance, put_chance
                            #     if call_chance > chance:
                            #         print "Call"
                            #         self.trader.trade(1, 'call')
                            #     else:
                            #         if put_chance > chance:
                            #             print "Put"
                            #             self.trader.trade(1, 'put')

                            call_amount = 0.0
                            put_amount = 0.0
                            if prediction[6]:
                                call_amount = prediction[6]
                            if prediction[7]:
                                put_amount = prediction[7]

                            if call_amount > 0 and put_amount > 0:
                                all_amounts = call_amount + put_amount
                                all_condition = float(all_amounts) / 100
                                if call_amount < put_amount:
                                    # print "Amounts put: ", float(put_amount)/all_condition, all_condition
                                    if not prediction[8]:
                                        if float(put_amount) / all_condition > float(chance_percent):
                                            print "Select: ", admission, candle[1], tl, tb, prediction[8]
                                            print "Amounts: ", call_amount, put_amount
                                            print "Put: ", float(put_amount) / all_condition, float(chance_percent)
                                            self.trader.trade(tb / 60, 1, 'put')
                                else:
                                    if call_amount > put_amount:
                                        # print "Amounts call: ", float(call_amount)/all_condition, all_condition
                                        if prediction[8]:
                                            if float(call_amount) / all_condition > float(chance_percent):
                                                print "Select: ", admission, candle[1], tl, tb, prediction[8]
                                                print "Amounts: ", call_amount, put_amount
                                                print "Call: ", float(call_amount) / all_condition, float(
                                                    chance_percent)
                                                self.trader.trade(tb / 60, 1, 'call')

                            cursor.execute(
                                "UPDATE quotation_predictions SET used_count = %s"
                                "WHERE admission=%s AND duration=%s AND time_left=%s AND time_bid=%s",
                                [prediction[5] + 1, admission, candle[1], tl, tb])
                            self.db.commit()
                        redis_object = {
                            "admission": admission,
                            "duration": candle[1],
                            "time_left": tl,
                            "time_bid": tb,
                            "value": quotation.value
                        }

                        self.redis.set(str(int(candle[2]) + tb) + str(tb) + self.active, json.dumps(redis_object))

                    break

    def check_predictions(self, quotation):
        timestamp = int(time.time())
        for tb in self.time_bids:
            redis_key = str(int(timestamp)) + str(tb) + self.active
            prediction_json = self.redis.get(redis_key)
            if prediction_json:
                prediction = json.loads(prediction_json)
                cursor = self.db.cursor()
                call = 1
                put = 0
                last_call = True
                if quotation.value < float(prediction["value"]):
                    call = 0
                    put = 1
                    last_call = False

                if not prediction["time_left"]:
                    prediction["time_left"] = 0

                cursor.execute(
                    "SELECT * FROM quotation_predictions "
                    "WHERE admission=%s AND duration=%s AND time_left=%s AND time_bid=%s",
                    [prediction["admission"], prediction["duration"], prediction["time_left"], prediction["time_bid"]])
                prediction_pg = cursor.fetchone()
                if not prediction_pg:
                    print "Not found from redis in DB"  # TODO: Check
                    self.redis.delete(redis_key)
                else:
                    cursor.execute(
                        "UPDATE quotation_predictions SET calls_count=%s, puts_count=%s, last_call=%s "
                        "WHERE admission=%s AND duration=%s AND time_left=%s AND time_bid=%s",
                        [prediction_pg[6] + call, prediction_pg[7] + put, last_call, prediction["admission"],
                         prediction["duration"], prediction["time_left"], prediction["time_bid"]])
                    self.db.commit()
                self.redis.delete(redis_key)
