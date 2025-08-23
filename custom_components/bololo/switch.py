# -*- coding: utf-8 -*-
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .device import  BololoDevice

_LOGGER = logging.getLogger(f"{__name__}.{__file__}")


async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """设置 config entry."""
    _LOGGER.debug("call async_setup_entry , config_entry: %s", config_entry)
    bololo_devices: list[BololoDevice] = hass.data[DOMAIN]['devices'][config_entry.entry_id]
    _LOGGER.debug("call async_setup_entry , bololo_devices: %s", bololo_devices)

    new_entities = []
    for bololo_device in bololo_devices:
        new_entities.extend(bololo_device.get_entities())
    _LOGGER.debug("call async_setup_entry , new_entities: %s", new_entities)

    if new_entities:
        async_add_entities(new_entities)



