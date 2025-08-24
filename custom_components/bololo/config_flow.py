# -*- coding: utf-8 -*-
"""
初始化配置流程
"""
import logging
from typing import Dict, Any, Self

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback

from .api_client import BololoApiClient
from .const import (
    DOMAIN,
    FIELD_NAME_MOBILE,
    FIELD_NAME_APP_KEY,
    FIELD_NAME_VERIFY_CODE, FIELD_NAME_TOKEN
)

_LOGGER = logging.getLogger(__name__)


class BololoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """
    配置流程
    """
    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self):
        self.mobile = None
        self.app_key = None

    def is_matching(self, other_flow: Self) -> bool:
        """Return True if other_flow is matching this flow."""
        raise NotImplementedError

    async def async_step_user(self, user_input=None):
        """处理用户初始步骤"""

        _LOGGER.debug("step user user_input: %s", user_input)
        errors: Dict[str, str] = {}
        description_placeholders = {}
        try:
            if user_input is not None:
                # 发送验证码
                api = BololoApiClient(
                    user_input.get(FIELD_NAME_APP_KEY),
                    user_input.get(FIELD_NAME_MOBILE),
                )
                await api.send_verify_code()
                self.mobile = user_input.get(FIELD_NAME_MOBILE)
                self.app_key = user_input.get(FIELD_NAME_APP_KEY)
                return await self.async_step_verify_code()
        # pylint: disable=broad-exception-caught
        except  Exception as err:
            _LOGGER.error("forward step verify_code failed: %s", err)
            errors["base"] = 'request_verify_code_failed'

        # 显示表单
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(schema=FIELD_NAME_APP_KEY): str,
                    vol.Required(schema=FIELD_NAME_MOBILE): str
                }
            ),
            errors=errors,
            description_placeholders=description_placeholders,
        )

    async def async_step_verify_code(self, user_input=None):
        """
        发送短信验证码
        """
        _LOGGER.debug("step verify_code user_input: %s", user_input)
        errors = {}
        description_placeholders = {
            FIELD_NAME_MOBILE: self.mobile,
            FIELD_NAME_APP_KEY: self.app_key,
        }
        try:
            if (user_input is not None
                    and user_input.get(FIELD_NAME_VERIFY_CODE) is not None
                    and isinstance(user_input.get(FIELD_NAME_VERIFY_CODE), str)
                    and (not user_input.get(FIELD_NAME_VERIFY_CODE).isspace())
                    and user_input.get(FIELD_NAME_VERIFY_CODE) != ""):
                # 登录
                verify_code = user_input.get(FIELD_NAME_VERIFY_CODE)
                api = BololoApiClient(
                    self.app_key,
                    self.mobile,
                )
                token = await api.login_by_mobile(verify_code)
                _LOGGER.debug("verify code %s, token: %s", verify_code, token)
                entry_data = {
                    FIELD_NAME_TOKEN: token,
                    FIELD_NAME_MOBILE: self.mobile,
                    FIELD_NAME_APP_KEY: self.app_key,
                }
                _LOGGER.debug("verify code , entry data: %s", entry_data)
                return self.async_create_entry(
                    title=self.mobile,
                    data=entry_data
                )
        # pylint: disable=broad-exception-caught
        except Exception as err:
            _LOGGER.error("forward step login_by_mobile failed: %s", err)
            errors["base"] = 'request_login_failed'
        return self.async_show_form(
            step_id="verify_code",
            data_schema=vol.Schema({
                vol.Required(FIELD_NAME_VERIFY_CODE): str
            }),
            errors=errors,
            description_placeholders=description_placeholders
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        """返回选项流处理器"""
        return BololoOptionsFlowHandler()


class BololoOptionsFlowHandler(config_entries.OptionsFlow):
    """处理选项更新"""

    def __init__(self):
        """初始化选项流"""

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """管理选项"""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        # config_entry = self.hass.config_entries.async_get_entry(self._config_entry_id)
        config_entity = self.config_entry
        # 获取当前选项值
        current_options = config_entity.options.copy() if config_entity.options else {}

        # api = BololoApiClient(
        #     self.config_entry.data.get(FIELD_NAME_APP_KEY),
        #     self.config_entry.data.get(FIELD_NAME_MOBILE),
        # )
        # devices = await api.list_device(self.config_entry.data.get(FIELD_NAME_TOKEN).get("userToken"))
        # device_dict: dict = {}
        # for device in devices:
        #     device_dict[str(device["did"])] = device.get("name")
        #
        # homes = await api.list_home(self.config_entry.data.get(FIELD_NAME_TOKEN).get("userToken"))
        # home_dict: dict = {}
        # for home in homes:
        #     home_dict[str(home["id"])] = home.get("name")

        return self.async_show_form(
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "scan_interval",
                        default=current_options.get("scan_interval", 60)
                    ): int,
                    # vol.Optional("update_device_list", default=False): bool,  # 伪装成按钮
                    # vol.Optional('home_list'): cv.multi_select(home_dict),
                    # vol.Optional('device_list'): cv.multi_select(device_dict),
                },
            )
        )
