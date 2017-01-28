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
        return api_constants.ACTIVES[name]

    def save(self, active_name):
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO actives (active) VALUES (%s);", [active_name])
        self.db.commit()
        cursor.execute("SELECT id FROM actives WHERE active=%s;", [active_name])
        row = cursor.fetchone()
        return row[0]

