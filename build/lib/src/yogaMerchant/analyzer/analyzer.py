# -*- coding: utf-8 -*-
import time
import datetime
import json
import threading
from src.yogaMerchant.helpers.fibonacci import FibonacciHelper
from src.yogaMerchant.helpers.timehelper import TimeHelper
from src.yogaMerchant.models.candle_quotation import Quotation


class Analyzer(object):
    def __init__(self, trader, redis, db, settings, is_test=False):
        self.is_test = is_test
        self.db = db
        self.settings = settings
        self.redis = redis
        self.trader = trader
        self.admissions = FibonacciHelper.get_uniq_unsigned_array(25)
        self.time_step_on_minute = 5

    def get_last_candle_till_ts(self, till_ts):
        """Достает время последней свечи
        Без этой проверки свеча может не
        существовать"""
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT till_ts FROM candles WHERE till_ts<=%s AND active_id=%s ORDER BY till_ts DESC LIMIT 1",
            [till_ts, self.settings.active["db_id"]])
        row = cursor.fetchone()
        if row:
            return row[0]
        return False

    def get_last_candles_with_parent(self, till_ts, deep):
        """Достаем похожие по длительности свечи в рекурсивной функции
        Вложенность обеспечивается свойством parent
        За уровень вложенности отвечает параметр deep(Глубина)"""
        out = []
        cursor = self.db.cursor()
        if deep > 0:
            deep -= 1
            """Получаем последний доступный ts свечи"""
            last_candle_till = self.get_last_candle_till_ts(till_ts)
            if last_candle_till:
                """Достаем свечи любой длины за время"""
                cursor.execute(
                    "SELECT change_power,duration,till_ts,from_ts FROM "
                    "candles WHERE till_ts=%s AND active_id=%s",
                    [last_candle_till, self.settings.active["db_id"]])
                rows = cursor.fetchall()
                for row in rows:
                    model = dict()
                    model["change_power"] = row[0]
                    model["duration"] = row[1]
                    # model["till_ts"] = row[2]
                    # model["from_ts"] = row[3]
                    if deep > 0:
                        """Ищем родителей по любой длинне"""
                        model["parents"] = self.get_last_candles_with_parent(row[2], deep)
                    out.append(model)
        return out

    def get_sequences_patterns(self, candles_with_parents):
        """
        Преобразует массив свечей с родителями в массив последовательностей

        :param candles_with_parents:
        :returns sequences: [{'duration': 5, 'admission': 144}]
        [{'duration': 5, 'admission': 144}, {'duration': 5, 'admission': 144}]
        [{'duration': 5, 'admission': 144}, {'duration': 10, 'admission': 144}]
        [{'duration': 5, 'admission': 144}, {'duration': 15, 'admission': 144}]
        [{'duration': 5, 'admission': 144}, {'duration': 30, 'admission': 144}]
        [{'duration': 5, 'admission': 144}, {'duration': 60, 'admission': 144}]
        [{'duration': 5, 'admission': 144}, {'duration': 120, 'admission': 144}]
        [{'duration': 5, 'admission': 144}, {'duration': 300, 'admission': 34}]
        [{'duration': 10, 'admission': 144}]....
        """
        out = list()
        for candle in candles_with_parents:
            sequence = list()
            obj = dict()
            obj["duration"] = candle["duration"]
            # obj["till_ts"] = candle["till_ts"]
            # obj["from_ts"] = candle["from_ts"]
            # obj["change_power"] = candle["change_power"]
            for admission in self.admissions:
                if candle["change_power"] <= admission:
                    obj["admission"] = admission
                    break

            if not "admission" in obj:
                obj["admission"] = int(candle["change_power"] / 100) * 100

            sequence.append(obj)
            out.append(sequence)
            if "parents" in candle:
                parents = self.get_sequences_patterns(candle["parents"])
                if len(parents) > 0:
                    for p in parents:
                        with_parents = sequence + p
                        out.append(with_parents)
        return out

    # def make_sequence_parent_item()

    def save_pattern_from_sequence(self, sequence):
        cursor = self.db.cursor()
        first = True
        last = False
        first_id = 0
        last_id = 0
        parent_id = 0
        i = 1
        duration = 0
        for pattern in sequence:
            duration += pattern["duration"]
            if len(sequence) == i:
                last = True

            cursor.execute(
                "INSERT INTO patterns (parent_id,first,last,admission,duration) "
                "VALUES (%s,%s,%s,%s,%s) ON CONFLICT (parent_id,last,admission,duration,first) "
                "DO UPDATE SET first=EXCLUDED.first RETURNING id",
                (parent_id, first, last, pattern["admission"], pattern["duration"]))
            pattern_row = cursor.fetchone()
            parent_id = pattern_row[0]
            if first_id == 0:
                first_id = parent_id
            if last:
                last_id = parent_id
            first = False
            i += 1
        self.db.commit()
        return {"id": last_id, "duration": duration}

    def upsert_prediction(self, pattern_id, time_bid, time_left, candles_durations):
        cursor = self.db.cursor()
        expires = 0
        ret = None
        is_update = False
        if len(self.settings.analyzer_prediction_expire) > 0:
            expires_array = self.settings.analyzer_prediction_expire
            expires_array.reverse()
            for expire in self.settings.analyzer_prediction_expire:

                if expire["history_duration"] <= candles_durations:
                    if expire["expire"] > 0:
                        expires = time.time() + expire["expire"]
                    break

            if expires > 0:
                cursor.execute(
                    "SELECT id,calls_count,puts_count,last_call,used_count,expires,delay FROM predictions WHERE "
                    "pattern_id=%s AND active_id=%s AND time_bid=%s AND time_left=%s AND is_test=%s "
                    "ORDER BY ts DESC LIMIT 1", (pattern_id, self.settings.active["db_id"], time_bid,
                                                 time_left, self.is_test))
                ret = cursor.fetchone()

                if ret and (ret[5] > time.time()):
                    self.update_prediction_used_counter(ret[0])
                    is_update = True

        if not is_update:
            cursor.execute("INSERT INTO predictions (pattern_id,active_id,time_bid,time_left,used_count,"
                           "calls_count,puts_count,last_call,expires,delay,ts,is_test) VALUES "
                           "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                           "ON CONFLICT (pattern_id,active_id,time_bid,time_left,expires)"
                           "DO UPDATE SET used_count = predictions.used_count + 1 "
                           "RETURNING id,calls_count,puts_count,last_call,used_count, expires, delay",
                           (pattern_id, self.settings.active["db_id"], time_bid, time_left, 1, 0, 0, 0, expires, 0, time.time(),
                            self.is_test))
            ret = cursor.fetchone()
        self.db.commit()
        return ret

    def update_prediction_used_counter(self, prediction_id):
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE predictions SET used_count=used_count+1 "
            "WHERE id=%s", (prediction_id,))

    def do_analysis(self, quotation):
        now = time.time()
        """Метод подготовки прогнозов"""
        """Получаем свечи разной длинны с их родителями"""
        candles = self.get_last_candles_with_parent(quotation.time, self.settings.analyzer_deep)
        """Получаем разные вариации последовательностей c глубиной вхождения"""
        sequences = self.get_sequences_patterns(candles)
        print sequences
        for sequence in sequences:
            if len(sequence) >= self.settings.analyzer_min_deep:
                for time_bid in self.settings.analyzer_bid_times:
                    """Заворачиваем в треды проверки с дальнейшим кешированием прогноза"""
                    cache_thread = threading.Thread(target=self.cache_prediction, args=(time_bid, quotation, sequence,))
                    cache_thread.daemon = True
                    cache_thread.start()
                    # print "Predictor worked at", time.time() - now, "s"

    def cache_prediction(self, time_bid, quotation, sequence):
        time_step = time_bid['time'] / 60 * self.time_step_on_minute
        remaining = TimeHelper.get_remaining_second_to_minute(quotation.time)
        time_left_minute = int((remaining / time_step) * time_step)
        time_left_bid = time_bid['time'] - (60 - time_left_minute)
        if time_bid["purchase"] < remaining:
            pattern = self.save_pattern_from_sequence(sequence)
            pattern_id = pattern["id"]
            duration_candles = pattern["duration"]
            expiration_ts = TimeHelper.get_expiration_time(quotation.time, time_bid)

            prediction_cache_prefix = "prediction"
            if self.is_test:
                prediction_cache_prefix = "test_prediction"

            prediction_cache_key = prediction_cache_prefix + "_" + str(self.settings.active['db_id']) + "_" + str(
                int(expiration_ts)) + "_" + str(time_bid['time']) + "_" + str(
                time_left_bid) + "_" + str(
                pattern_id)

            """Проверяем на возможность сохранения повторяющего прогноза за это время"""
            save_prediction = True
            if not self.settings.save_prediction_if_exists:
                prediction_exists = self.redis.exists(prediction_cache_key)
                if prediction_exists:
                    save_prediction = False

            """Если повторяющийся прогноз можно сохранить """
            if save_prediction:
                # TODO: Изменить на модель Prediction
                """
                Возвращает кортеж Prediction
                :returns
                    :id = prediction[0]
                    :call_count = prediction[1]
                    :puts_count = prediction[2]
                    :last_call = prediction[3]
                    :used_count = prediction[4]
                    :expires = prediction[5]
                    :delay = prediction[6]
                """
                prediction = self.upsert_prediction(pattern_id, time_bid['time'],
                                                    time_left_bid, duration_candles)
                # print prediction_cache_key, prediction

                """
                Отключаем эту функцию для режима тестирования истории
                (Используется непосредственно в тестировщике)
                """
                # Trader
                if not self.is_test:
                    trade_direction = self.trader.check_probability(prediction[1], prediction[2],
                                                                    prediction[3], prediction[4],
                                                                    prediction[6])
                    if trade_direction:
                        self.trader.trade(
                            time_bid['time'] / 60,
                            1,
                            trade_direction,
                            prediction[0],
                            int(expiration_ts),
                            quotation.value
                        )

                """
                Объект для записи прогноза в кеш для дальнейшей его проверки
                Имеет зависимые поля для тестирования истории
                    call_count
                    puts_count
                    used_count
                    created_at
                    expiration_at
                    bid_time
                """
                redis_object = {
                    "id": prediction[0],
                    "call_count": prediction[1],
                    "puts_count": prediction[2],
                    "last_call": prediction[3],
                    "used_count": prediction[4],
                    "delay": prediction[6],
                    "bid_time": time_bid['time'],
                    "value": quotation.value,
                    "pattern_id": pattern_id,
                    "created_at": quotation.time,
                    "expiration_at": int(expiration_ts)
                }

                """Запись прогноза в редис"""
                if self.is_test:
                    """Для тестирования истории без времени жизни"""
                    self.redis.set(prediction_cache_key, json.dumps(redis_object))
                else:
                    """Запись с временем жизни для реалтайм данных"""
                    self.redis.setex(prediction_cache_key, time_bid['time'] + (time_bid['time'] / 60 * 5),
                                     json.dumps(redis_object))

    def check_predictions(self, quotation=None, times=1):
        trade_result = None
        timestamp = int(time.time())
        redis_prefix = "prediction"
        if self.is_test:
            redis_prefix = "test_prediction"
            timestamp = "*"
        redis_key = redis_prefix + "_" + str(self.settings.active["db_id"]) + "_" + str(timestamp) + "_*"
        predictions_keys = self.redis.keys(redis_key)
        if predictions_keys:
            test_trading = []
            for predictions_key in predictions_keys:
                prediction_json = self.redis.get(predictions_key)
                self.redis.delete(predictions_key)
                if prediction_json:
                    prediction = json.loads(prediction_json)
                    cursor = self.db.cursor()

                    if self.is_test:
                        """В режиме теста нет котировки - поэтому достаем вручную"""
                        if not quotation:
                            cursor.execute(
                                "SELECT * FROM quotations WHERE ts>=%s AND active_id=%s ORDER BY ts LIMIT 1",
                                (prediction["expiration_at"], self.settings.active["db_id"]))
                            row = cursor.fetchone()
                            quotation = Quotation([row[0], row[4]])
                    call = 0
                    put = 0
                    last_call = 0
                    delay = 0

                    if int(prediction["delay"]) > 0:
                        delay = prediction["delay"] - 1

                    if quotation.value < float(prediction["value"]):
                        call = 0
                        put = 1
                        if prediction["last_call"] < 0:
                            last_call = prediction["last_call"] - 1
                        else:
                            last_call = -1
                    else:
                        if quotation.value > float(prediction["value"]):
                            call = 1
                            put = 0
                            if prediction["last_call"] > 0:
                                last_call = prediction["last_call"] + 1
                            else:
                                last_call = 1

                    if abs(last_call) >= self.settings.trader_min_repeats and prediction["delay"] == 0:
                        delay = self.settings.trader_delay_on_trend

                    cursor.execute("SELECT * FROM predictions WHERE id=%s", (prediction["id"],))
                    prediction_pg = cursor.fetchone()
                    if not prediction_pg:
                        times += 1
                        print time.strftime("%b %d %Y %H:%M:%S"), "- Not found in DB from redis:", prediction["id"]
                        time.sleep(5)
                        self.check_predictions(quotation, times)
                    else:
                        """Обновляем прогноз и устанавливаем счетчики"""
                        cursor.execute(
                            "UPDATE predictions SET calls_count=calls_count+%s, puts_count=puts_count+%s, "
                            "last_call=%s, delay=%s WHERE id=%s",
                            (
                                call,
                                put,
                                last_call,
                                delay,
                                prediction["id"]
                            ))

                        """Закрытие сделки - если была"""
                        cursor.execute(
                            "UPDATE orders SET expiration_cost=%s, change=created_cost-%s, closed_at=%s "
                            "WHERE active_id=%s AND prediction_id=%s AND expiration_at<=%s",
                            (
                                quotation.value,
                                quotation.value,
                                int(time.time()),
                                self.settings.active["db_id"],
                                prediction["id"],
                                quotation.time
                            ))

                    if self.is_test:
                        """
                        Торгуем по мере проверки в тестовом режиме
                        в будущем сравнивая результаты ставки с прогнозом
                        """
                        trade_direction = self.trader.check_probability(prediction["call_count"],
                                                                        prediction["puts_count"],
                                                                        prediction["last_call"],
                                                                        prediction["used_count"],
                                                                        prediction["delay"])
                        if trade_direction:
                            """Сравниваем результат с прогнозом"""
                            if trade_direction == "put":
                                if put == 1:
                                    trade_result = "Put"
                                else:
                                    trade_result = "Fail"
                            else:
                                if trade_direction == "call":
                                    if call == 1:
                                        trade_result = "Call"
                                    else:
                                        trade_result = "Fail"
                        else:
                            trade_result = "No"
                        test_trading.append(trade_result)
            self.db.commit()
            if self.is_test:
                return test_trading
