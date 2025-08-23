import logging
from enum import Enum, StrEnum
from typing import Any, List

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import DeviceInfo, Entity

from . import BololoApiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(f"{__name__}.{__file__}")


class BololoDisinfectionCabinetSwitchFunction(Enum):
    POWER = ("power", "switch", "mdi:power")
    ANION = ("anion", "anion", "mdi:minus-circle-outline")
    NIGHT_MODE = ("night_mode", "night_mode", "mdi:lightbulb-night")
    STORAGE = ("storage", "storage_switch", "mdi:shield-check-outline")

    def __init__(self, switch_function: str, switch_function_on_server: str, icon: str):
        self._switch_function = switch_function
        self._switch_function_on_server = switch_function_on_server
        self._icon = icon

    def get_switch_function(self):
        return self._switch_function

    def get_switch_function_on_server(self):
        return self._switch_function_on_server

    def get_icon(self):
        return self._icon


class BololoDeviceType(Enum):
    DISINFECTION_CABINET = ("k1mvpG70tNN000000000000000000000", [Platform.SWITCH])

    def __init__(self, product_key: str, platforms: []):
        if platforms is None:
            platforms = []
        self.product_key = product_key
        self.platforms = platforms

    def get_support_platforms(self):
        return self.platforms


def get_device_type_by_product_key(product_key: str):
    for device_type in BololoDeviceType:
        if device_type.product_key == product_key:
            return device_type
    return None
