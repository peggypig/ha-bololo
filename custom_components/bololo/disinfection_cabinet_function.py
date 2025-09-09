# -*- coding: utf-8 -*-
"""
消毒柜功能
"""
from enum import Enum

from homeassistant.const import Platform


class BololoDisinfectionCabinetFunction(Enum):
    """
    消毒柜功能
    """
    POWER = ("power", "switch", "mdi:power", Platform.SWITCH)
    ANION = ("anion", "anion", "mdi:minus-circle-outline", Platform.SWITCH)
    NIGHT_MODE = ("night_mode", "night_mode", "mdi:lightbulb-night", Platform.SWITCH)
    STORAGE = ("storage", "storage_switch", "mdi:shield-check-outline", Platform.SWITCH)
    DISINFECTION = ("disinfection", "disinfection_switch", "mdi:sun-wireless", Platform.SWITCH)
    DRY = ("dry", "dry_switch", "mdi:heat-wave", Platform.SWITCH)
    AUTO = ("auto", "auto_switch", "mdi:refresh-auto", Platform.SWITCH)
    DISINFECTION_TIME = ("disinfection_time", "disinfection_time", "mdi:sun-wireless", Platform.SELECT)
    AUTO_TIME = ("auto_time", "auto_time", "mdi:refresh-auto", Platform.SELECT)

    def __init__(self, function: str, function_on_server: str, icon: str, platform: Platform):
        self._function = function
        self._function_on_server = function_on_server
        self._platform = platform
        self._icon = icon

    @property
    def platform(self):
        """return the platform"""
        return self._platform

    @property
    def function_on_server(self):
        """
        Return the function_on_server
        """
        return self._function_on_server

    @property
    def function(self):
        """
        Return the button_function
        """
        return self._function

    @property
    def icon(self):
        """
        Return the icon
        """
        return self._icon
