# -*- coding: utf-8 -*-

import logging
import src.api.iqoption.constants as api_constants


class ActiveHelper(object):
    def __init__(self, db):
        self.db = db

    def get_db_id_by_name(self, active_name):
        """Достает ID актива из базы"""
        cursor = self.db.cursor()
        cursor.execute("SELECT id FROM actives WHERE active=%s;", [active_name])
        row = cursor.fetchone()
        if row:
            active_id = row[0]
        else:
            active_id = self.save(active_name)
        return active_id

    def get_name_by_db_id(self, active_id):
        """Достает ID актива из базы"""
        cursor = self.db.cursor()
        cursor.execute("SELECT active FROM actives WHERE id=%s;", [active_id])
        row = cursor.fetchone()
        if row:
            active_id = row[0]
        else:
            active_id = self.save(active_id)
        return active_id

    def get_platform_id_by_name(self, name):
        """Достает ID платформы из базы по имени актива"""
        cursor = self.db.cursor()
        cursor.execute("SELECT platform_id FROM actives WHERE active=%s;", [name])
        row = cursor.fetchone()
        if row:
            platform_id = row[0]
        else:
            platform_id = self.save(name)
        return platform_id

    def save(self, active_name):
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO actives (active, platform_id) VALUES (%s, %s);",
                       [active_name, api_constants.ACTIVES[active_name]])
        self.db.commit()
        cursor.execute("SELECT id FROM actives WHERE active=%s;", [active_name])
        row = cursor.fetchone()
        return row[0]

    def check_actives_in_db(self):
        result_check = False
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM actives")
        row = cursor.fetchone()
        if row and row[0] > 0:
            result_check = True
        return result_check

    def load_defaults(self):
        cursor = self.db.cursor()
        for active_key in api_constants.ACTIVES:
            cursor.execute("INSERT INTO actives (active, platform_id) VALUES (%s, %s);",
                           [active_key, self.get_platform_id_by_name(active_key)])
        self.db.commit()

