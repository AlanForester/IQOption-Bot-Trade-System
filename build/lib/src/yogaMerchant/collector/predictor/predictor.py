# -*- coding: utf-8 -*-
import datetime
import time
import json

class Predictor(object):
    def __init__(self, trader, redis, db, active):
        self.db = db
        self.active = active
        self.redis = redis
        self.trader = trader
        self.candles_durations = [
            5,  # 5 секунд
            10,  # 10 секунд
            15,  # 15 секунд
            30,  # 30 секунд
            60,  # 1 минута
            120,  # 2 минуты
            300  # 5 минут
        ]
        self.admissions = [
            -2048,
            -1024,
            -512,
            -256,
            -128,
            -64,
            -32,
            -16,
            -8,
            -4,
            -2,
            -1,
            1,
            2,
            4,
            8,
            16,
            32,
            64,
            128,
            256,
            512,
            1024,
            2048
        ]
        self.time_bids = [
            60,
            120,
            180,
            240,
            300
        ]

    def get_candles(self, quotation):
        cursor = self.db.cursor()
        cursor.execute("SELECT change_power,duration,till_ts FROM candles WHERE till_ts=%s", [quotation.time])
        candles = cursor.fetchall()
        step = 5
        time_left = int((60 - int(datetime.datetime.fromtimestamp(quotation.time).strftime('%S'))) / step) * step
        if len(candles) < len(self.candles_durations):
            time.sleep(1)
            self.get_candles(quotation)

        for candle in candles:
            for admission in self.admissions:
                if int(candle[0]) <= admission:
                    for tb in self.time_bids:
                        cursor.execute(
                            "SELECT * FROM quotation_predictions "
                            "WHERE admission=%s AND duration=%s AND time_left=%s AND time_bid=%s",
                            [admission, candle[1], time_left, tb])
                        prediction = cursor.fetchone()
                        if not prediction:
                            cursor.execute(
                                "INSERT INTO quotation_predictions "
                                "(admission, infinity, time_bid, time_left, used_count, calls_count, puts_count, "
                                "last_call, ts, duration) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [
                                    admission, True, tb, time_left, 1, 0, 0, False, candle[2], candle[1]])
                            self.db.commit()
                        else:
                            # Trader
                            chance = 50

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

                            # call_amount = 0
                            # put_amount = 0
                            # if prediction[6]:
                            #     call_amount = prediction[6]
                            # if prediction[7]:
                            #     put_amount = prediction[7]
                            #
                            # ch = 0
                            # if call_amount < put_amount:
                            #     if call_amount > 0:
                            #         ch = put_amount / call_amount
                            #     if ch > chance/100:
                            #         print "Put"
                            #         self.trader.trade(1, 'put')
                            # else:
                            #     if call_amount > put_amount:
                            #         if put_amount > 0:
                            #             ch = call_amount / put_amount
                            #         if ch > chance/100:
                            #             print "Call"
                            #             self.trader.trade(1, 'call')

                            cursor.execute(
                                "UPDATE quotation_predictions SET used_count = %s"
                                "WHERE admission=%s AND duration=%s AND time_left=%s AND time_bid=%s",
                                [prediction[5] + 1, admission, candle[1], time_left, tb])
                            self.db.commit()
                        redis_object = {
                            "admission": admission,
                            "duration": candle[1],
                            "time_left": time_left,
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

                cursor.execute(
                    "SELECT * FROM quotation_predictions "
                    "WHERE admission=%s AND duration=%s AND time_left=%s AND time_bid=%s",
                    [prediction["admission"], prediction["duration"], prediction["time_left"], prediction["time_bid"]])
                prediction_pg = cursor.fetchone()
                if not prediction:
                    print "Not found from redis in DB"
                else:
                    cursor.execute(
                        "UPDATE quotation_predictions SET calls_count=%s, puts_count=%s, last_call=%s "
                        "WHERE admission=%s AND duration=%s AND time_left=%s AND time_bid=%s",
                        [prediction_pg[6] + call, prediction_pg[7] + put, last_call, prediction["admission"],
                         prediction["duration"], prediction["time_left"], prediction["time_bid"]])
                    self.db.commit()
                self.redis.delete(redis_key)
