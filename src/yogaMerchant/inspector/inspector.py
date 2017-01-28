# -*- coding: utf-8 -*-

import logging
import src.api.iqoption.constants as api_constants
import time


class Inspector(object):

    def __init__(self, db, active, config):
        self.db = db
        self.active = active
        self.config = config


