# -*- coding: utf-8 -*-

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from custom_component.bololo.const import (
    DOMAIN
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """处理配置流程"""

    async def async_step_user(self, user_input=None):
        """处理用户初始步骤"""
        if user_input is not None:
            # 验证输入
            return self.async_create_entry(title="配置名称", data=user_input)

        # 显示表单
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("api_key"): str,
                vol.Optional("scan_interval", default=60): int,
                vol.Optional("options"): str
            }),
            description_placeholders={
                "help_text": "请从供应商网站获取API密钥"
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """返回选项流处理器"""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """处理选项更新"""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """管理选项"""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    "scan_interval",
                    default=self.config_entry.options.get("scan_interval", 60)
                ): int
            })
        )
