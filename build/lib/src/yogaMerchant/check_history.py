# -*- coding: utf-8 -*-
"""Module for IQ Option API starter."""

import argparse
import logging
import os
import time

import psycopg2
import redis
import src.api.iqoption.constants as api_constants
import threading
from multiprocessing.pool import ThreadPool
from src.yogaMerchant.config.config import parse_config
from src.yogaMerchant.analyzer.analyzer import Analyzer
from src.yogaMerchant.trader.trader import create_trader
from src.yogaMerchant.helpers.active import ActiveHelper
from src.yogaMerchant.models.candle_quotation import Quotation


class Checker(object):
    """Calss for IQ Option API starter."""

    def __init__(self, config):
        """
        :param config: The instance of :class:`Settings
            <iqpy.settings.settigns.Settings>`.
        """
        self.config = config

        self.db = psycopg2.connect(
            database=self.config.get_db_postgres_database(),
            user=self.config.get_db_postgres_username(),
            host=self.config.get_db_postgres_hostname(),
            password=self.config.get_db_postgres_password()
        )

        self.redis = redis.StrictRedis(
            host=self.config.get_db_redis_hostname(),
            port=self.config.get_db_redis_port(),
            db=self.config.get_db_redis_db())

        active_helper = ActiveHelper(self.db)

        self.active = {
            "name": self.config.get_active(),
            "db_id": active_helper.get_id_by_name(self.config.get_active()),
            "platform_id": api_constants.ACTIVES[self.config.get_active()]
        }

        self.analyzer_bid_time = self.config.get_analyzer_bid_times()
        self.analyzer_deep = self.config.get_analyzer_deep()
        self.analyzer_interval = self.config.get_analyzer_interval()
        self.collector_candles_durations = self.config.get_collector_candles_durations()
        self.min_deep = self.config.get_analyzer_min_deep()
        self.predictions_expire = self.config.get_analyzer_prediction_expire()
        self.predictions_delay = self.config.get_analyzer_prediction_delay()


def _prepare_logging():
    """Prepare logging for starter."""
    formatter = logging.Formatter(
        "%(asctime)s:%(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logs_folder = "logs"
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    starter_logger = logging.getLogger(__name__)
    starter_logger.setLevel(logging.INFO)

    starter_file_handler = logging.FileHandler(os.path.join(logs_folder, "starter.log"))
    starter_file_handler.setLevel(logging.INFO)
    starter_file_handler.setFormatter(formatter)

    starter_logger.addHandler(console_handler)
    starter_logger.addHandler(starter_file_handler)

    api_logger = logging.getLogger("iqapi")

    api_file_handler = logging.FileHandler(os.path.join(logs_folder, "iqapi.log"))
    api_file_handler.setLevel(logging.DEBUG)
    api_file_handler.setFormatter(formatter)

    api_logger.addHandler(console_handler)
    api_logger.addHandler(api_file_handler)

    collector_logger = logging.getLogger("collector")
    collector_logger.setLevel(logging.DEBUG)

    collector_file_handler = logging.FileHandler(os.path.join(logs_folder, "collector.log"))
    collector_file_handler.setLevel(logging.DEBUG)
    collector_file_handler.setFormatter(formatter)

    collector_logger.addHandler(console_handler)
    collector_logger.addHandler(collector_file_handler)

    websocket_logger = logging.getLogger("websocket")
    websocket_logger.setLevel(logging.DEBUG)

    websocket_file_handler = logging.FileHandler(os.path.join(logs_folder, "websocket.log"))
    websocket_file_handler.setLevel(logging.DEBUG)
    websocket_file_handler.setFormatter(formatter)

    websocket_logger.addHandler(console_handler)
    websocket_logger.addHandler(websocket_file_handler)


def _create_starter(config):
    return Checker(config)


def start():
    """Main method for start."""
    _prepare_logging()
    args = _parse_args()
    config = parse_config(args.config_path)
    starter = _create_starter(config)
    trader = create_trader(None, starter.active, config, starter.db, True)
    predictor = Analyzer(trader, starter.redis, starter.db, starter.active, config, True)
    begin = args.from_ts
    end = time.time()
    if args.to_ts:
        end = args.to_ts

    cursor = starter.db.cursor()
    cursor.execute(
        "SELECT * FROM quotations WHERE ts>=%s AND ts<=%s AND active_id=%s ORDER BY ts",
        (begin, end, starter.active["db_id"]))
    rows = cursor.fetchall()
    if len(rows) > 0:
        """Запускаем демона для проверки кеша и получения результата торгов"""
        check_thread = threading.Thread(target=checker_daemon, args=(predictor,))
        check_thread.setDaemon(True)
        check_thread.start()

        i = 0
        thread_limit = 10
        threads_count = 0
        total_threads = []
        for row in rows:
            if i == starter.analyzer_interval:
                # response_threads.append(pool.apply_async(run_analysis, (row, predictor)))
                """Проверка на количество работающих тредов и блокировка"""
                while threads_count >= thread_limit:
                    threads_count = len(get_alive_threads(total_threads))

                analysis_thread = threading.Thread(target=run_analysis, args=(row, predictor))
                analysis_thread.setDaemon(True)
                analysis_thread.start()

                total_threads.append(analysis_thread)
                threads_count += 1
                # print "Run analysis thread. Total:", len(total_threads)
                i = 0
            i += 1
        print "All threads running"
        check_thread.join()


def get_alive_threads(threads):
    result_threads = []
    if len(threads) > 0:
        for thread in threads:
            if thread.isAlive():
                result_threads.append(thread)
    return result_threads


def checker_daemon(predictor):
    result = {
        "put_bids": 0,
        "call_bids": 0,
        "total_success": 0,
        "total_fails": 0,
        "no_trade": 0,
        "total_check": 0
    }
    while True:
        check_result = predictor.check_predictions(None)
        if check_result and len(check_result) > 0:
            for check in check_result:
                result["total_check"] += 1
                if check == "Put":
                    result["put_bids"] += 1
                    result["total_success"] += 1
                if check == "Call":
                    result["call_bids"] += 1
                    result["total_success"] += 1
                if check == "No":
                    result["no_trade"] += 1
                if check == "Fail":
                    result["total_fails"] += 1
            print result
        time.sleep(1)


def run_analysis(row, predictor):
    quotation = Quotation([row[0], row[4]])
    """Формируем кеши прошнозов для проверки"""
    predictor.do_analysis(quotation)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config_path", dest="config_path", type=str, required=True,
        help="Path to new configuration file."
    )
    parser.add_argument(
        "-f", "--from", dest="from_ts", type=int, required=True,
        help="Check from timestamp."
    )
    parser.add_argument(
        "-t", "--to", dest="to_ts", type=int, required=False,
        help="Check to timestamp."
    )
    return parser.parse_args()


if __name__ == "__main__":
    start()
