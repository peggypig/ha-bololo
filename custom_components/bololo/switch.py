import logging
import threading
import time
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.translation import async_get_translations
from homeassistant.helpers.typing import UndefinedType

from custom_components.bololo import DOMAIN, get_device_type_by_product_key, BololoApiClient
from custom_components.bololo.device import BololoDeviceType, BololoDisinfectionCabinetSwitchFunction

_LOGGER = logging.getLogger(f"{__name__}.{__file__}")


async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """设置 config entry."""
    _LOGGER.debug("async_setup_entry config_entry: %s", config_entry)
    device_list: list[dict] = hass.data[DOMAIN]['devices'][config_entry.entry_id]
    _LOGGER.debug("async_setup_entry device_list: %s", device_list)

    new_entities = []
    for device in device_list:
        device_type = get_device_type_by_product_key(device.get('productKey'))
        if device_type is None:
            _LOGGER.info("async_setup_entry unknown device_type: %s for product_key",
                         device_type,
                         device.get('productKey')
                         )
            continue
        if device_type == BololoDeviceType.DISINFECTION_CABINET:
            for function in BololoDisinfectionCabinetSwitchFunction:
                device["device_type"] = BololoDeviceType.DISINFECTION_CABINET
                device["switch_function"] = function.get_switch_function()
                device["switch_function_on_server"] = function.get_switch_function_on_server()
                device["icon"] = function.get_icon()
                new_entities.append(DisinfectionCabinetSwitch(config_entry, device))
    _LOGGER.debug("async_setup_entry new_entities: %s", new_entities)

    if new_entities:
        async_add_entities(new_entities)


device_status_cache: dict[str, dict[str, Any]] = {}

_disinfection_cabinet_switch_init_lock = threading.Lock()


class DisinfectionCabinetSwitch(SwitchEntity):

    def __init__(self, config_entry: ConfigEntry, device_data: dict[str, Any]):
        Entity.__init__(self)
        _LOGGER.debug("init switch , device_data : %s", device_data)
        self._device_data = device_data
        self._switch_function = device_data.get("switch_function")
        self._switch_function_on_server = device_data.get("switch_function_on_server")
        self._config_entry: ConfigEntry = config_entry

        self._attr_unique_id = f"{device_data.get("mac").lower()}_{self._switch_function}"
        self._attr_name = self._switch_function
        self._attr_is_on = False
        self.entity_id = f"{DOMAIN}.disinfection_cabinet_{self._switch_function}"
        self._attr_icon = device_data.get("icon")

        self._api = BololoApiClient(
            self._config_entry.data.get("app_key"),
            self._config_entry.data.get("mobile"),
        )
        if device_status_cache.get(self._device_data.get('mac')) is None:
            with _disinfection_cabinet_switch_init_lock:
                if device_status_cache.get(self._device_data.get('mac')) is None:
                    device_status_cache[device_data.get('mac')] = {
                        "device_status_request_lock": threading.Lock(),
                        "device_status_from_server": None,
                        "device_status_from_server_timestamp_ms": None
                    }

        # 设备信息配置
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_data.get("did"))},
            name=device_data.get("name"),
            manufacturer=device_data.get("manufacturer"),
            sw_version=device_data.get("fw_version"),
            hw_version=device_data.get("hw_version"),
            configuration_url=device_data.get("configuration_url"),
            serial_number=device_data.get('sno'),
        )

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
            f"component.{self.platform.config_entry.domain}.entity.switch.{self._switch_function}.name",
            self._attr_name  # 默认名称
        )

    @property
    def device_info(self) -> DeviceInfo:
        """返回设备信息"""
        _LOGGER.debug("device_info _attr_device_info : %s", self._attr_device_info)
        return self._attr_device_info

    @property
    def icon(self) -> str | None:
        _LOGGER.debug("call icon method")
        if hasattr(self, "_attr_icon"):
            return self._attr_icon
        if hasattr(self, "entity_description"):
            return self.entity_description.icon
        return None

    @property
    def is_on(self) -> bool | None:
        _LOGGER.debug("call is_on method")
        return self._attr_is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.async_control_switch(
            self._switch_function_on_server, True
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.async_control_switch(
            self._switch_function_on_server, False
        )

    async def async_update(self):
        """更新状态"""
        _LOGGER.debug("sync bololo disinfection cabinet %s status for config_entity : %s",
                      self._switch_function, self._config_entry)
        if (device_status_cache.get(self._device_data.get("mac")).get("device_status_from_server") is not None
                and device_status_cache.get(self._device_data.get("mac")).get(
                    "device_status_from_server_timestamp_ms") is not None
                and int(round(time.time() * 1000)) - device_status_cache.get(self._device_data.get("mac")).get(
                    "device_status_from_server_timestamp_ms") < 120000):
            _LOGGER.debug("using cache , bololo disinfection cabinet status : %s",
                          device_status_cache.get(self._device_data.get("mac")).get("device_status_from_server"))
            return
        else:
            with device_status_cache.get(self._device_data.get("mac")).get("device_status_request_lock"):
                if (device_status_cache.get(self._device_data.get("mac")).get("device_status_from_server") is not None
                        and device_status_cache.get(self._device_data.get("mac")).get(
                            "device_status_from_server_timestamp_ms") is not None
                        and int(round(time.time() * 1000)) - device_status_cache.get(self._device_data.get("mac")).get(
                            "device_status_from_server_timestamp_ms") < 120000):
                    _LOGGER.debug("using cache , bololo disinfection cabinet status : %s",
                                  device_status_cache.get(self._device_data.get("mac")).get(
                                      "device_status_from_server"))
                else:
                    await self.async_update_status_from_server()
        is_on = device_status_cache.get(self._device_data.get("mac")).get("device_status_from_server").get(
            self._switch_function_on_server)
        _LOGGER.debug("bololo disinfection cabinet %s status : %s",
                      self._switch_function, is_on)
        if is_on != self._attr_is_on:
            # 必须调用 async_write_ha_state 来更新UI
            _LOGGER.debug("update bololo disinfection cabinet %s status for config_entity : %s",
                          self._switch_function, self._config_entry)
            self.async_write_ha_state()
        self._attr_is_on = is_on

    async def async_control_switch(self, switch_name_on_server: str, status: bool):
        _LOGGER.debug("turn bololo disinfection cabinet %s %s", switch_name_on_server, status)
        await self._api.control_device(
            auth_token=self._config_entry.data.get("token").get("userToken"),
            product_key=self._device_data.get("productKey"),
            mac=self._device_data.get("mac"),
            command_data={
                switch_name_on_server: status,
            }
        )
        self._attr_is_on = status

    async def async_update_status_from_server(self):
        """更新状态"""
        _LOGGER.debug("sync bololo disinfection cabinet status for config_entity : %s", self._config_entry)
        device_status = await self._api.get_device_status(
            auth_token=self._config_entry.data.get("token").get("userToken"),
            product_key=self._device_data.get("productKey"),
            mac=self._device_data.get("mac")
        )
        device_status_cache.get(self._device_data.get("mac"))["device_status_from_server"] = device_status
        device_status_cache.get(self._device_data.get("mac"))["device_status_from_server_timestamp_ms"] = int(
            round(time.time() * 1000))
        _LOGGER.debug("bololo disinfection cabinet status : %s",
                      device_status_cache.get(self._device_data.get("mac")).get("device_status_from_server"))

# class DisinfectionCabinetAnionSwitch(DisinfectionCabinetSwitch):
#     """消毒柜 负离子"""
#
#     def __init__(self, config_entry: ConfigEntry, device_data: dict[str, Any]):
#         device_data["switch_type"] = "anion"
#         device_data["icon"] = "mdi:minus-circle-outline"
#         DisinfectionCabinetSwitch.__init__(self, config_entry, device_data)
#         _LOGGER.debug("init anion switch , device_data : %s", device_data)
#
#     async def async_turn_on(self, **kwargs: Any) -> None:
#         await self.async_control_switch(
#             "anion", True
#         )
#
#     async def async_turn_off(self, **kwargs: Any) -> None:
#         await self.async_control_switch(
#             "anion", False
#         )
#
#     async def async_update(self):
#         """更新状态"""
#         _LOGGER.debug("sync bololo disinfection cabinet anion status for config_entity : %s", self._config_entry)
#         await self.async_update_status_from_server()
#         is_on = self._device_status_from_server.get("anion")
#         _LOGGER.debug("bololo disinfection cabinet anion status : %s", is_on)
#         if is_on != self._attr_is_on:
#             # 必须调用 async_write_ha_state 来更新UI
#             _LOGGER.debug("update bololo disinfection cabinet anion status for config_entity : %s", self._config_entry)
#             self.async_write_ha_state()
#         self._attr_is_on = is_on


# class DisinfectionCabinetPowerSwitch(DisinfectionCabinetSwitch):
#     """消毒柜 电源"""
#
#     def __init__(self, config_entry: ConfigEntry, device_data: dict[str, Any]):
#         device_data["switch_type"] = "power"
#         device_data["icon"] = "mdi:power"
#         DisinfectionCabinetSwitch.__init__(self, config_entry, device_data)
#         _LOGGER.debug("init power switch , device_data : %s", device_data)
#
#     async def async_turn_on(self, **kwargs: Any) -> None:
#         await self.async_control_switch(
#             "switch", True
#         )
#
#     async def async_turn_off(self, **kwargs: Any) -> None:
#         await self.async_control_switch(
#             "switch", False
#         )
#
#     async def async_update(self):
#         """更新状态"""
#         _LOGGER.debug("sync bololo disinfection cabinet power status for config_entity : %s", self._config_entry)
#         await self.async_update_status_from_server()
#         is_on = self._device_status_from_server.get("switch")
#         _LOGGER.debug("bololo disinfection cabinet power status : %s", is_on)
#         if is_on != self._attr_is_on:
#             # 必须调用 async_write_ha_state 来更新UI
#             _LOGGER.debug("update bololo disinfection cabinet power status for config_entity : %s", self._config_entry)
#             self.async_write_ha_state()
#         self._attr_is_on = is_on


# class DisinfectionCabinetNightModeSwitch(DisinfectionCabinetSwitch):
#     """消毒柜 夜间模式"""
#
#     def __init__(self, config_entry: ConfigEntry, device_data: dict[str, Any]):
#         device_data["switch_type"] = "night_mode"
#         device_data["icon"] = "mdi:lightbulb-night"
#         DisinfectionCabinetSwitch.__init__(self, config_entry, device_data)
#         _LOGGER.debug("init night_mode switch , device_data : %s", device_data)
#
#     async def async_turn_on(self, **kwargs: Any) -> None:
#         await self.async_control_switch(
#             "night_mode", True
#         )
#
#     async def async_turn_off(self, **kwargs: Any) -> None:
#         await self.async_control_switch(
#             "night_mode", False
#         )
#
#     async def async_update(self):
#         """更新状态"""
#         _LOGGER.debug("sync bololo disinfection cabinet night_mode status for config_entity : %s", self._config_entry)
#         await self.async_update_status_from_server()
#         is_on = self._device_status_from_server.get("night_mode")
#         _LOGGER.debug("bololo disinfection cabinet night_mode status : %s", is_on)
#         if is_on != self._attr_is_on:
#             # 必须调用 async_write_ha_state 来更新UI
#             _LOGGER.debug("update bololo disinfection cabinet night_mode status for config_entity : %s",
#                           self._config_entry)
#             self.async_write_ha_state()
#         self._attr_is_on = is_on

# class DisinfectionCabinetStorageSwitch(DisinfectionCabinetSwitch):
#     """消毒柜 保管"""
#
#     def __init__(self, config_entry: ConfigEntry, device_data: dict[str, Any]):
#         device_data["switch_type"] = "storage_switch"
#         device_data["icon"] = "mdi:shield-check-outline"
#         DisinfectionCabinetSwitch.__init__(self, config_entry, device_data)
#         _LOGGER.debug("init storage_switch switch , device_data : %s", device_data)
#
#     async def async_turn_on(self, **kwargs: Any) -> None:
#         await self.async_control_switch(
#             "storage_switch", True
#         )
#
#     async def async_turn_off(self, **kwargs: Any) -> None:
#         await self.async_control_switch(
#             "storage_switch", False
#         )
#
#     async def async_update(self):
#         """更新状态"""
#         _LOGGER.debug("sync bololo disinfection cabinet storage_switch status for config_entity : %s", self._config_entry)
#         await self.async_update_status_from_server()
#         is_on = self._device_status_from_server.get("storage_switch")
#         _LOGGER.debug("bololo disinfection cabinet storage_switch status : %s", is_on)
#         if is_on != self._attr_is_on:
#             # 必须调用 async_write_ha_state 来更新UI
#             _LOGGER.debug("update bololo disinfection cabinet storage_switch status for config_entity : %s",
#                           self._config_entry)
#             self.async_write_ha_state()
#         self._attr_is_on = is_on

#########################################################################################################


# class DisinfectionCabinetAnionSwitch(SwitchEntity):
#     def __init__(self, config_entry: ConfigEntry, device_data: dict[str, Any]):
#         Entity.__init__(self)
#         _LOGGER.debug("init anion switch device_data : %s", device_data)
#         self._device_data = device_data
#         # 实体标识符（包含设备信息）
#         self._attr_unique_id = f"{device_data.get("mac").lower()}_anion"
#         self._attr_name = "anion"
#         self._attr_is_on = False
#         self.entity_id = f"{DOMAIN}.disinfection_cabinet_anion"
#         self._config_entry: ConfigEntry = config_entry
#         self._entity_type = "anion"
#         self._api = BololoApiClient(
#             self._config_entry.data.get("app_key"),
#             self._config_entry.data.get("mobile"),
#         )
#         self._attr_icon = "mdi:minus-circle-outline"
#
#         # 设备信息配置
#         self._attr_device_info = DeviceInfo(
#             identifiers={(DOMAIN, device_data.get("did"))},
#             name=device_data.get("name"),
#             manufacturer=device_data.get("manufacturer"),
#             sw_version=device_data.get("fw_version"),
#             hw_version=device_data.get("hw_version"),
#             configuration_url=device_data.get("configuration_url"),
#             serial_number=device_data.get('sno'),
#         )
#
#     @property
#     def device_info(self) -> DeviceInfo:
#         """返回设备信息"""
#         _LOGGER.debug("device_info _attr_device_info : %s", self._attr_device_info)
#         return self._attr_device_info
#
#     @property
#     def icon(self) -> str | None:
#         _LOGGER.debug("call icon method")
#         if hasattr(self, "_attr_icon"):
#             return self._attr_icon
#         if hasattr(self, "entity_description"):
#             return self.entity_description.icon
#         return None
#
#     @property
#     def is_on(self) -> bool | None:
#         _LOGGER.debug("call is_on method")
#         return self._attr_is_on
#
#     # @property
#     # async def async_is_on(self, **kwargs) -> bool:
#     #     _LOGGER.debug("Call async_is_on method")
#     #     return self._attr_is_on
#
#     async def async_turn_on(self, **kwargs):
#         """打开负离子开关"""
#         _LOGGER.debug("turn bololo disinfection cabinet anion on")
#         await self._api.control_device(
#             auth_token=self._config_entry.data.get("token").get("userToken"),
#             product_key=self._device_data.get("productKey"),
#             mac=self._device_data.get("mac"),
#             command_data={
#                 "anion": True,
#             }
#         )
#         self._attr_is_on = True
#
#     async def async_turn_off(self, **kwargs):
#         """关闭负离子"""
#         _LOGGER.debug("turn bololo disinfection cabinet anion off")
#         await self._api.control_device(
#             auth_token=self._config_entry.data.get("token").get("userToken"),
#             product_key=self._device_data.get("productKey"),
#             mac=self._device_data.get("mac"),
#             command_data={
#                 "anion": False,
#             }
#         )
#         self._attr_is_on = False
#
#     async def async_update(self):
#         """更新状态"""
#         _LOGGER.debug("sync bololo disinfection cabinet anion status for config_entity : %s", self._config_entry)
#         device_status = await self._api.get_device_status(
#             auth_token=self._config_entry.data.get("token").get("userToken"),
#             product_key=self._device_data.get("productKey"),
#             mac=self._device_data.get("mac")
#         )
#         is_on = device_status.get("anion")
#         _LOGGER.debug("bololo disinfection cabinet anion status : %s", is_on)
#         if device_status.get("anion") != self._attr_is_on:
#             # 必须调用 async_write_ha_state 来更新UI
#             _LOGGER.debug("update bololo disinfection cabinet anion status for config_entity : %s", self._config_entry)
#             self.async_write_ha_state()
#         self._attr_is_on = is_on


# class DisinfectionCabinetPowerSwitch(SwitchEntity):
#     """消毒柜"""
#
#     def __init__(self, config_entry: ConfigEntry, device_data: dict[str, Any]):
#         Entity.__init__(self)
#         _LOGGER.debug("init power switch device_data : %s", device_data)
#         self._device_data = device_data
#         # 实体标识符（包含设备信息）
#         self._attr_unique_id = f"{device_data.get("mac").lower()}_power"
#         self._attr_name = "power"
#         self._attr_is_on = False
#         self.entity_id = f"{DOMAIN}.disinfection_cabinet_power"
#         self._config_entry: ConfigEntry = config_entry
#         self._entity_type = "power"
#         self._api = BololoApiClient(
#             self._config_entry.data.get("app_key"),
#             self._config_entry.data.get("mobile"),
#         )
#         self._attr_icon = "mdi:power"
#
#         # 设备信息配置
#         self._attr_device_info = DeviceInfo(
#             identifiers={(DOMAIN, device_data.get("did"))},
#             name=device_data.get("name"),
#             manufacturer=device_data.get("manufacturer"),
#             sw_version=device_data.get("fw_version"),
#             hw_version=device_data.get("hw_version"),
#             configuration_url=device_data.get("configuration_url"),
#             serial_number=device_data.get('sno'),
#         )
#
#     async def async_added_to_hass(self):
#         """当实体添加到HA时调用"""
#         translations = await async_get_translations(
#             hass=self.hass,
#             language=self.hass.config.language,
#             category="entity",
#             integrations=[DOMAIN]
#         )
#         _LOGGER.debug("call async_added_to_hass , translations : %s", translations)
#         # 使用翻译后的名称
#         self._attr_name = translations.get(
#             f"component.{self.platform.config_entry.domain}.entity.switch.{self._entity_type}.name",
#             self._attr_name  # 默认名称
#         )
#
#     @property
#     def icon(self) -> str | None:
#         _LOGGER.debug("call icon method")
#         if hasattr(self, "_attr_icon"):
#             return self._attr_icon
#         if hasattr(self, "entity_description"):
#             return self.entity_description.icon
#         return None
#
#     @property
#     def is_on(self) -> bool | None:
#         _LOGGER.debug("call is_on method")
#         return self._attr_is_on
#
#     # @property
#     # async def async_is_on(self, **kwargs) -> bool:
#     #     _LOGGER.debug("Call async_is_on method")
#     #     return self._attr_is_on
#
#     async def async_turn_on(self, **kwargs):
#         """打开电源"""
#         _LOGGER.debug("turn bololo disinfection cabinet power on")
#         await self._api.control_device(
#             auth_token=self._config_entry.data.get("token").get("userToken"),
#             product_key=self._device_data.get("productKey"),
#             mac=self._device_data.get("mac"),
#             command_data={
#                 "switch": True,
#             }
#         )
#         self._attr_is_on = True
#
#     async def async_turn_off(self, **kwargs):
#         """关闭电源"""
#         _LOGGER.debug("turn bololo disinfection cabinet power off")
#         await self._api.control_device(
#             auth_token=self._config_entry.data.get("token").get("userToken"),
#             product_key=self._device_data.get("productKey"),
#             mac=self._device_data.get("mac"),
#             command_data={
#                 "switch": False,
#             }
#         )
#         self._attr_is_on = False
#
#     async def async_update(self):
#         """更新状态"""
#         _LOGGER.debug("sync bololo disinfection cabinet power status for config_entity : %s", self._config_entry)
#         device_status = await self._api.get_device_status(
#             auth_token=self._config_entry.data.get("token").get("userToken"),
#             product_key=self._device_data.get("productKey"),
#             mac=self._device_data.get("mac")
#         )
#         is_on = device_status.get("switch")
#         _LOGGER.debug("bololo disinfection cabinet power status : %s", is_on)
#         if device_status.get("switch") != self._attr_is_on:
#             # 必须调用 async_write_ha_state 来更新UI
#             _LOGGER.debug("update bololo disinfection cabinet power status for config_entity : %s", self._config_entry)
#             self.async_write_ha_state()
#         self._attr_is_on = is_on
#
#     @property
#     def device_info(self) -> DeviceInfo:
#         """返回设备信息"""
#         _LOGGER.debug("device_info _attr_device_info : %s", self._attr_device_info)
#         return self._attr_device_info
