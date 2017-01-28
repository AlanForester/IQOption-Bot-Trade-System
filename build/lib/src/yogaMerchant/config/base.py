# -*- coding: utf-8 -*-
"""Module for base configuration."""

from src.yogaMerchant.config.params import Params


class BaseScenario(object):
    """Class to prepare base configuration."""
    # pylint: disable=too-few-public-methods

    def __init__(self):
        self.settings = Params()
