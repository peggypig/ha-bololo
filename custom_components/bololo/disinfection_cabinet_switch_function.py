# -*- coding: utf-8 -*-
"""
消毒柜开关功能
"""
from enum import Enum


class BololoDisinfectionCabinetSwitchFunction(Enum):
    """
    消毒柜开关功能
    """
    POWER = ("power", "switch", "mdi:power")
    ANION = ("anion", "anion", "mdi:minus-circle-outline")
    NIGHT_MODE = ("night_mode", "night_mode", "mdi:lightbulb-night")
    STORAGE = ("storage", "storage_switch", "mdi:shield-check-outline")
    DISINFECTION = ("disinfection", "disinfection_switch", "mdi:disinfection_switch_off")

    def __init__(self, switch_function: str, switch_function_on_server: str, icon: str):
        self._switch_function = switch_function
        self._switch_function_on_server = switch_function_on_server
        self._icon = icon

    @property
    def switch_function_on_server(self):
        """
        Return the switch_function_on_server
        """
        return self._switch_function_on_server

    @property
    def switch_function(self):
        """
        Return the switch_function
        """
        return self._switch_function

    @property
    def icon(self):
        """
        Return the icon
        """
        return self._icon
