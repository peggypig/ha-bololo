# -*- coding: utf-8 -*-
"""
消毒柜按钮
"""
from __future__ import annotations

from typing import (TYPE_CHECKING, Any)
import logging

from homeassistant.components.button import ButtonEntity, ButtonDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo

from .bololo_entity import BololoEntity
from .const import (DOMAIN)
from .disinfection_cabinet_function import BololoDisinfectionCabinetFunction
from .tools import sync_call

# pylint: disable=line-too-long

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from . import BololoDisinfectionCabinet


class DisinfectionCabinetButton(ButtonEntity, BololoEntity):
    # pylint: disable=too-many-instance-attributes
    """
    消毒柜开关（自动模式时长切换...）
    """

    def __init__(
            self,
            config_entry: ConfigEntry,
            bololo_disinfection_cabinet_function: BololoDisinfectionCabinetFunction,
    ) -> None:
        ButtonEntity.__init__(self)
        BololoEntity.__init__(self, config_entry, bololo_disinfection_cabinet_function)
        self._disinfection_cabinet = None
        self._bololo_disinfection_cabinet_function = bololo_disinfection_cabinet_function
        self._config_entry: ConfigEntry = config_entry
        self._attr_unique_id = None
        self._attr_name = self._bololo_disinfection_cabinet_function.function
        self.entity_id = f"{DOMAIN}.disinfection_cabinet_{self._bololo_disinfection_cabinet_function.function_on_server}"
        _LOGGER.debug("call init disinfection cabinet button, %s", self.entity_id)
        self._attr_icon = self._bololo_disinfection_cabinet_function.icon

    def set_disinfection_cabinet(self, disinfection_cabinet: BololoDisinfectionCabinet):
        """
        设置 消毒柜对象引用
        """
        self._disinfection_cabinet = disinfection_cabinet
        self._attr_unique_id = f"{self._disinfection_cabinet.mac.lower()}_{self._bololo_disinfection_cabinet_function.function_on_server}"

    @property
    def device_info(self) -> DeviceInfo:
        """返回设备信息"""
        _LOGGER.debug("call device_info , device_info : %s", self._disinfection_cabinet.device_info)
        return self._disinfection_cabinet.device_info

    @property
    def icon(self) -> str | None:
        _LOGGER.debug("call icon")
        if hasattr(self, "_attr_icon"):
            return self._attr_icon
        if hasattr(self, "entity_description"):
            return self.entity_description.icon
        return None

    @property
    def available(self) -> bool:
        """Return True if the button is available."""
        if self._bololo_disinfection_cabinet_function == BololoDisinfectionCabinetFunction.AUTO_TIME:
            if self._disinfection_cabinet is None:
                _LOGGER.debug("call auto_time button available, but _disinfection_cabinet is None , False")
                return False
            device_status = sync_call(self._disinfection_cabinet.device_status)
            if device_status is None:
                _LOGGER.debug(
                    "call auto_time button available, self._disinfection_cabinet.device_status is None , False")
                return False
            auto_switch_on = getattr(device_status, f"_{self._bololo_disinfection_cabinet_function.function_on_server}")
            _LOGGER.debug("call auto_time button available , %s", auto_switch_on)
            return auto_switch_on
        return True

    def press(self) -> None:
        """Handle the button press."""
        _LOGGER.debug("call press, button function %s", self._bololo_disinfection_cabinet_function.name)

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.debug("call async_press, button function %s", self._bololo_disinfection_cabinet_function.name)
