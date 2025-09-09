# -*- coding: utf-8 -*-
"""
消毒柜按钮
"""
from __future__ import annotations

from typing import (TYPE_CHECKING, Any)
import logging

from homeassistant.components.select import SelectEntity
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


class DisinfectionCabinetSelect(SelectEntity, BololoEntity):
    # pylint: disable=too-many-instance-attributes
    """
    消毒柜开关（自动模式时长切换...）
    """

    def __init__(
            self,
            config_entry: ConfigEntry,
            bololo_disinfection_cabinet_function: BololoDisinfectionCabinetFunction,
    ) -> None:
        SelectEntity.__init__(self)
        BololoEntity.__init__(self, config_entry, bololo_disinfection_cabinet_function)
        self._disinfection_cabinet = None
        self._bololo_disinfection_cabinet_function = bololo_disinfection_cabinet_function
        self._config_entry: ConfigEntry = config_entry
        self._attr_unique_id = None
        self._attr_name = self._bololo_disinfection_cabinet_function.function
        self.entity_id = f"{DOMAIN}.disinfection_cabinet_{self._bololo_disinfection_cabinet_function.function_on_server}"
        _LOGGER.debug("call init disinfection cabinet select, %s", self.entity_id)
        self._attr_icon = self._bololo_disinfection_cabinet_function.icon
        if self._bololo_disinfection_cabinet_function == BololoDisinfectionCabinetFunction.DISINFECTION_TIME:
            self._attr_current_option = "20"
            self._attr_options = ["off", "10", "15", "20"]
        elif self._bololo_disinfection_cabinet_function == BololoDisinfectionCabinetFunction.AUTO_TIME:
            self._attr_current_option = "60"
            self._attr_options = ["off", "40", "50", "60"]

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

    async def async_update(self):
        """
        更新设备信息（基础信息/状态信息），由hass调用
        """
        device_status = await self._disinfection_cabinet.device_status
        _LOGGER.debug("call async_update ,select function %s , device_status : %s",
                      self._bololo_disinfection_cabinet_function,
                      device_status.__dict__)
        disinfection_time = getattr(device_status,
                                    f"_{BololoDisinfectionCabinetFunction.DISINFECTION_TIME.function_on_server}")
        auto_time = getattr(device_status, f"_{BololoDisinfectionCabinetFunction.AUTO_TIME.function_on_server}")
        if self._bololo_disinfection_cabinet_function == BololoDisinfectionCabinetFunction.AUTO_TIME:
            if auto_time != self._attr_current_option:
                _LOGGER.debug("call async_update , update %s status for config_entity : %s , auto_time %s -> %s",
                              self._bololo_disinfection_cabinet_function,
                              self._config_entry,
                              self._attr_current_option,
                              auto_time
                              )
                self._attr_current_option = str(auto_time)
                self.async_write_ha_state()
        elif self._bololo_disinfection_cabinet_function == BololoDisinfectionCabinetFunction.DISINFECTION_TIME:
            if disinfection_time != self._attr_current_option:
                _LOGGER.debug(
                    "call async_update , update %s status for config_entity : %s , disinfection_time %s -> %s",
                    self._bololo_disinfection_cabinet_function,
                    self._config_entry,
                    self._attr_current_option,
                    disinfection_time
                )
                self._attr_current_option = str(disinfection_time)
                self.async_write_ha_state()

    # @property
    # def available(self) -> bool:
    #     """Return True if the button is available."""
    #     # if self._bololo_disinfection_cabinet_function == BololoDisinfectionCabinetFunction.DISINFECTION_TIME:
    #     #     if self._disinfection_cabinet is None:
    #     #         _LOGGER.debug("call disinfection_time select available, but _disinfection_cabinet is None , False")
    #     #         return False
    #     #     device_status = sync_call(self._disinfection_cabinet.device_status)
    #     #     if device_status is None:
    #     #         _LOGGER.debug(
    #     #             "call disinfection_time select available, self._disinfection_cabinet.device_status is None , False")
    #     #         return False
    #     #     disinfection_switch_on = getattr(device_status,
    #     #                                      f"_{BololoDisinfectionCabinetFunction.DISINFECTION.function_on_server}")
    #     #     _LOGGER.debug("call disinfection_time select available , %s", disinfection_switch_on)
    #     #     return disinfection_switch_on
    #     return True

    # def disinfection_time_available(self):
    #     """
    #     消毒时长是否可用
    #     """
    #     if self._bololo_disinfection_cabinet_function != BololoDisinfectionCabinetFunction.DISINFECTION_TIME:
    #         return False
    #     if self._disinfection_cabinet is None:
    #         _LOGGER.debug("call disinfection_time select available, but _disinfection_cabinet is None , False")
    #         return False
    #     device_status = sync_call(self._disinfection_cabinet.device_status)
    #     if device_status is None:
    #         _LOGGER.debug(
    #             "call disinfection_time select available, self._disinfection_cabinet.device_status is None , False")
    #         return False
    #     disinfection_switch_on = getattr(device_status,
    #                                      f"_{BololoDisinfectionCabinetFunction.DISINFECTION.function_on_server}")
    #     _LOGGER.debug("call disinfection_time select available , %s", disinfection_switch_on)
    #     return disinfection_switch_on

    def select_option(self, option: str) -> None:
        """Change the selected option."""
        _LOGGER.debug("call select_option %s, %s", option, self._disinfection_cabinet)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        _LOGGER.debug("call async_select_option %s, %s", option, self._disinfection_cabinet)
