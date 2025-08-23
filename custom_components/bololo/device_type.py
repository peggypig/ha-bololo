# -*- coding: utf-8 -*-
"""
设备类型
"""
from enum import Enum

from homeassistant.const import Platform


class BololoDeviceType(Enum):
    DISINFECTION_CABINET = ("k1mvpG70tNN000000000000000000000", [Platform.SWITCH])

    def __init__(self, product_key: str, platforms):
        if platforms is None:
            platforms = []
        self._product_key = product_key
        self._platforms = platforms

    @property
    def product_key(self):
        """
        Return the product_key
        """
        return self._product_key

    @property
    def platforms(self):
        """
        Return the platforms
        """
        return self._platforms


def get_device_type_by_product_key(product_key: str):
    """
    Return the device type by product key
    """
    for device_type in BololoDeviceType:
        if device_type.product_key == product_key:
            return device_type
    return None