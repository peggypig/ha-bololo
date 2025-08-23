# -*- coding: utf-8 -*-
"""
设备
"""
import logging
from abc import abstractmethod, ABC

from homeassistant.helpers.entity import  Entity

from .api_client import BololoApiClient
from .device_type import BololoDeviceType

_LOGGER = logging.getLogger(f"{__name__}.{__file__}")



class BololoDevice(ABC):

    def __init__(self, device_type: BololoDeviceType, bololo_api_client: BololoApiClient):
        self._device_type = device_type
        self._api_client = bololo_api_client

    @property
    def api_client(self) -> BololoApiClient:
        return self._api_client

    @property
    def device_type(self):
        return self._device_type

    @abstractmethod
    def get_entities(self) -> list[Entity]:
        pass
