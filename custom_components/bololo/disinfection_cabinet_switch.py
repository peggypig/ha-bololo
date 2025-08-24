# -*- coding: utf-8 -*-
"""
消毒柜开关
"""
from __future__ import annotations

from typing import (TYPE_CHECKING, Any)
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.translation import async_get_translations

from .const import (DOMAIN)
# pylint: disable=line-too-long
from .disinfection_cabinet_switch_function import BololoDisinfectionCabinetSwitchFunction

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from . import BololoDisinfectionCabinet


class DisinfectionCabinetSwitch(SwitchEntity):
    # pylint: disable=too-many-instance-attributes
    """
    消毒柜开关（电源、负离子、夜间模式...）
    """

    def __init__(
            self,
            config_entry: ConfigEntry,
            switch_function: BololoDisinfectionCabinetSwitchFunction,
    ) -> None:
        SwitchEntity.__init__(self)
        _LOGGER.debug("call init disinfection cabinet switch")
        self._disinfection_cabinet = None
        self._switch_function = switch_function
        self._config_entry: ConfigEntry = config_entry
        self._attr_unique_id = None
        self._attr_name = self._switch_function.switch_function
        self._attr_is_on = False
        self.entity_id = f"{DOMAIN}.disinfection_cabinet_{self._switch_function}"
        self._attr_icon = self._switch_function.icon

    def set_disinfection_cabinet(self, disinfection_cabinet: BololoDisinfectionCabinet):
        """
        设置 消毒柜对象引用
        """
        self._disinfection_cabinet = disinfection_cabinet
        self._attr_unique_id = f"{self._disinfection_cabinet.mac.lower()}_{self._switch_function}"

    async def async_added_to_hass(self):
        """当实体添加到HA时调用"""
        translations = await async_get_translations(
            hass=self.hass,
            language=self.hass.config.language,
            category="entity",
            integrations=[DOMAIN]
        )
        _LOGGER.debug("call async_added_to_hass , translations : %s", translations)
        # 使用翻译后的名称
        self._attr_name = translations.get(
            f"component.{self.platform.config_entry.domain}.entity.switch.{self._switch_function.switch_function}.name",
            self._attr_name  # 默认名称
        )

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
    def is_on(self) -> bool | None:
        _LOGGER.debug("call is_on")
        return self._attr_is_on

    async def async_update(self):
        """
        更新设备信息（基础信息/状态信息），由hass调用
        """
        device_status = await self._disinfection_cabinet.device_status
        _LOGGER.debug("call async_update ,switch function %s , device_status : %s", self._switch_function,
                      device_status.__dict__)
        is_on = getattr(device_status, f"_{self._switch_function.switch_function_on_server}")
        if is_on != self._attr_is_on:
            # 必须调用 async_write_ha_state 来更新UI
            _LOGGER.debug("call async_update , update %s status for config_entity : %s", self._switch_function,
                          self._config_entry)
            self.async_write_ha_state()
        self._attr_is_on = is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        await self._disinfection_cabinet.async_control_switch(
            self._switch_function.switch_function_on_server, True
        )
        self._attr_is_on = True

    def turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        self._disinfection_cabinet.async_control_switch(
            self._switch_function.switch_function_on_server, True
        )

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        self._disinfection_cabinet.async_control_switch(
            self._switch_function.switch_function_on_server, False
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await self._disinfection_cabinet.async_control_switch(
            self._switch_function.switch_function_on_server, False
        )
        self._attr_is_on = False
