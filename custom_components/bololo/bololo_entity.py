# -*- coding: utf-8 -*-
"""
bololo api 客户端
"""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.translation import async_get_translations

from custom_components.bololo import DOMAIN
from custom_components.bololo.disinfection_cabinet_function import BololoDisinfectionCabinetFunction

_LOGGER = logging.getLogger(__name__)


class BololoEntity(Entity):

    def __init__(
            self,
            config_entry: ConfigEntry,
            bololo_disinfection_cabinet_function: BololoDisinfectionCabinetFunction,
    ) -> None:
        Entity.__init__(self)
        self._config_entry = config_entry
        self._bololo_disinfection_cabinet_function = bololo_disinfection_cabinet_function

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
            f"component.{self.platform.config_entry.domain}.entity.{self._bololo_disinfection_cabinet_function.platform.lower()}.{self._bololo_disinfection_cabinet_function.function}.name",
            self._attr_name  # 默认名称
        )
