# -*- coding: utf-8 -*-

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
import logging
from custom_component.bololo.const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the component."""
    _LOGGER.debug("async_setup config : %s", config)
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry):
    """Set up from a config entry."""
    # 这里实现配置项初始化
    _LOGGER.debug("async_setup_entry entry : %s", entry)
    # hass.async_create_task(
    #     hass.config_entries.async_forward_entry_setup(entry, "sensor")
    # )
    return True
