# -*- coding: utf-8 -*-
"""
开关设备设置
"""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback, EntityPlatform

from .const import DOMAIN
from .device import  BololoDevice
from .disinfection_cabinet_button import DisinfectionCabinetButton
from .disinfection_cabinet_select import DisinfectionCabinetSelect

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """设置 config entry."""
    _LOGGER.debug("call select async_setup_entry , config_entry: %s", config_entry)
    bololo_devices: list[BololoDevice] = hass.data[DOMAIN]['devices'][config_entry.entry_id]
    _LOGGER.debug("call select async_setup_entry , bololo_devices: %s", bololo_devices)

    new_entities = []
    for bololo_device in bololo_devices:
        for entity in bololo_device.get_entities():
            if isinstance(entity,DisinfectionCabinetSelect):
                new_entities.append(entity)
    _LOGGER.debug("call select async_setup_entry , new_entities: %s", new_entities)

    if new_entities:
        async_add_entities(new_entities)
