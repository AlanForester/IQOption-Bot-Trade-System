# -*- coding: utf-8 -*-
"""Module for IQ Option API trader."""

import logging
import src.api.iqoption.constants as api_constants


class Emitter(object):
    """Class for data emitter."""

    def __init__(self, active, db):
        self.db = db
        self.active = active

    def start(self):
        logger = logging.getLogger(__name__)

        logger.info("Analyzer for active '%s' started.", self.active)

