# -*- coding: utf-8 -*-

from homeassistant.components.http import StaticPathConfig
from custom_components.bololo.const import DOMAIN, FIELD_NAME_MOBILE
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
import logging

from .const import DOMAIN, SERVICE_ADD_DEVICE, SERVICE_REMOVE_DEVICE, SERVICE_REDISCOVER
from .api_client import BololoApiClient
from .device_type import BololoDeviceType, get_device_type_by_product_key
from .disinfection_cabinet import BololoDisinfectionCabinet

_LOGGER = logging.getLogger(f"{__name__}.{__file__}")


async def async_setup(hass: HomeAssistant, config: dict):
    """设置集成组件"""
    _LOGGER.debug("call async_setup , config: %s", config)
    hass.data.setdefault(DOMAIN, {})

    # 注册静态图标路径
    icons_path = hass.config.path("custom_components", DOMAIN, "www", "icons")

    # 检查图标目录是否存在，如果不存在则创建
    import os
    os.makedirs(icons_path, exist_ok=True)

    # 注册静态文件服务
    await hass.http.async_register_static_paths(
        configs=[StaticPathConfig(f"/local/community/{DOMAIN}/icons", icons_path, False)]
    )

    _LOGGER.debug("call async_setup , bololo icons path register : %s", icons_path)
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """设置配置条目"""
    _LOGGER.debug("call async_setup_entry , config_entry: %s , entry.data : %s", config_entry, config_entry.data)
    # 创建API客户端和设备管理器
    bololo_api_client = BololoApiClient(hass, config_entry.data.get(FIELD_NAME_MOBILE))

    # 创建设备注册表条目
    device_registry = dr.async_get(hass)

    # 存储管理器实例
    hass.data[DOMAIN]["devices"] = {
        config_entry.entry_id: []
    }

    device_list = await bololo_api_client.list_device(
        config_entry.data.get("token").get("userToken")
    )
    platforms = []
    bololo_devices = []
    for device_item in device_list:
        bololo_device_type = get_device_type_by_product_key(device_item["productKey"])
        if bololo_device_type is None or bololo_device_type.platforms is None:
            _LOGGER.debug("call async_setup_entry , but device_type : %s for %s", bololo_device_type,
                          device_item["productKey"])
            continue
        platforms.extend(bololo_device_type.platforms)
        if bololo_device_type == BololoDeviceType.DISINFECTION_CABINET:
            # 创建设备
            bololo_device = BololoDisinfectionCabinet(
                device_info_from_server=device_item,
                hass=hass,
                config_entry=config_entry,
            )
            device_entry = device_registry.async_get_or_create(
                config_entry_id=config_entry.entry_id,
                identifiers={(DOMAIN, device_item.get('did'))},
                name=device_item.get('name'),
                manufacturer=device_item.get('manufacturer', 'Bololo'),
                model=device_item.get('model', bololo_device_type.DISINFECTION_CABINET.name),
                sw_version=device_item.get('firmware_version', 'UnknownSW'),
                hw_version=device_item.get('hardware_version', 'UnknownHW'),
            )
            bololo_device.device_entry = device_entry
            bololo_devices.append(bololo_device)

    hass.data[DOMAIN]['devices'][config_entry.entry_id] = bololo_devices
    # 设置平台
    _LOGGER.debug("call async_setup_entry , entry setup platforms: %s", platforms)
    await hass.config_entries.async_forward_entry_setups(config_entry, platforms)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # 如果需要卸载平台，取消注释下面这行
    # unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    # if unload_ok:
    #     hass.data[DOMAIN].pop(entry.entry_id)
    # return unload_ok

    return True
