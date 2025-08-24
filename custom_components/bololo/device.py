# -*- coding: utf-8 -*-
"""
设备
"""
import logging
from abc import abstractmethod, ABC

from homeassistant.helpers.entity import  Entity

from .api_client import BololoApiClient
from .device_type import BololoDeviceType

_LOGGER = logging.getLogger(__name__)



class BololoDevice(ABC):
    """
    bololo 抽象设备类
    """
    def __init__(self, device_type: BololoDeviceType, bololo_api_client: BololoApiClient):
        self._device_type = device_type
        self._api_client = bololo_api_client

    @property
    def api_client(self) -> BololoApiClient:
        """
        返回api 客户端
        """
        return self._api_client

    @property
    def device_type(self):
        """
        获取设备类型
        """
        return self._device_type

    @abstractmethod
    def get_entities(self) -> list[Entity]:
        """
        获取设备支持的entity
        """
