# -*- coding: utf-8 -*-
"""
bololo api 客户端
"""
import json
from typing import Any

import aiohttp
import async_timeout
import logging


_LOGGER = logging.getLogger(f"{__name__}.{__file__}")


class BololoApiClientError(Exception):
    """自定义API异常."""
    pass


class BololoApiClient:
    """封装Bololo IoT API的客户端."""

    def __init__(self, app_key, mobile):
        self._app_key = app_key
        self._mobile = mobile
        self._host = "https://app.bololoapp3.com"

    async def send_verify_code(self):
        _LOGGER.debug("request bololo verify code with app_key : %s , mobile : %s", self._app_key, self._mobile)
        """发送短信验证码"""
        url = f"{self._host}/app/user/mobileCode"
        body_json = {
            "appKey": self._app_key,
            "data": {
                "mobile": self._mobile,
                "lang": "zh"
            },
            "version": "1.0"
        }
        _session = aiohttp.ClientSession()
        try:
            async with async_timeout.timeout(10):  # 设置超时
                async with _session.post(url, json=body_json, ssl=False) as response:
                    if response.status == 200:
                        data = await response.json()
                        _LOGGER.debug("call send_verify_code request response : %s", data)
                        data_code = data.get("code")
                        if data_code == "200":
                            _LOGGER.debug("call send_verify_code request success: %s", data_code)
                        else:
                            raise BololoApiClientError(
                                f"call send_verify_code request HTTP response not expected: {data}"
                            )
                    else:
                        error_text = await response.text()
                        _LOGGER.error("call send_verify_code request failed: %s - %s", response.status, error_text)
                        raise BololoApiClientError(
                            f"call send_verify_code request HTTP {response.status}: {error_text}"
                        )
        finally:
            await _session.close()

    async def control_device(self, auth_token: str, product_key: str, mac: str, command_data: dict[str, Any]):
        """设备控制"""
        _LOGGER.debug("request bololo control device with auth_token : %s , mac : %s , product_key : %s",
                      auth_token, mac, product_key)
        url = f"{self._host}/bololo/app/device/control/{product_key}/{mac}"
        headers = {
            "Authorization": auth_token,
        }
        body_json = {
            "appKey": self._app_key,
            "data": json.dumps(command_data),
            "version": "1.0"
        }
        _session = aiohttp.ClientSession()
        try:
            async with async_timeout.timeout(10):  # 设置超时
                async with _session.post(url, json=body_json, headers=headers, ssl=False) as response:
                    if response.status == 200:
                        data = await response.json()
                        _LOGGER.debug("call control_device request response : %s", data)
                        data_code = data.get("code")
                        if data_code == "200":
                            _LOGGER.debug("call control_device request success: %s", data_code)
                            """
                            {
                              "code": "200",
                              "message": "本次请求成功",
                              "data": true,
                              "display": null,
                              "error": false
                            }
                            """
                        else:
                            raise BololoApiClientError(
                                f"call control_device request HTTP response not excepted : {data}"
                            )
                    else:
                        error_text = await response.text()
                        _LOGGER.error("call control_device request failed: %s - %s", response.status, error_text)
                        raise BololoApiClientError(
                            f"call control_device request HTTP {response.status}: {error_text}"
                        )
        finally:
            await _session.close()

    async def login_by_mobile(self, verify_code: str) -> dict[str, object]:
        """短信验证码登录"""
        _LOGGER.debug(
            "request bololo login by mobile with verify code : %s , mobile : %s",
            verify_code,
            self._mobile
        )
        url = f"{self._host}/app/user/loginByMobile"
        body_json = {
            "appKey": self._app_key,
            "data": {
                "mobile": self._mobile,
                "code": verify_code,
                "mobileCountryCode": "CN",
                "lang": "zh"
            },
            "version": "1.0"
        }
        _session = aiohttp.ClientSession()
        try:
            async with async_timeout.timeout(10):  # 设置超时
                async with _session.post(url, json=body_json, ssl=False) as response:
                    if response.status == 200:
                        data = await response.json()
                        _LOGGER.debug("call login_by_mobile request response : %s", data)
                        data_code = data.get("code")
                        if data_code == "200":
                            _LOGGER.debug("call login_by_mobile request success: %s", data_code)
                            """
                                {
                                    "code": "200",
                                    "message": "本次请求成功",
                                    "data": {
                                        "jwtAuthenticationDto": {
                                            "token": ""
                                        },
                                        "userToken": "",
                                        "uid": "",
                                        "userId": 123,
                                        "refreshToken": "",
                                        "createdAt": 1755672309,
                                        "expiredAt": 1771224309
                                    },
                                    "display": null,
                                    "error": false
                                }
                            """
                            return data.get("data")
                        else:
                            raise BololoApiClientError(
                                f"call login_by_mobile request HTTP response not excepted : {data}"
                            )
                    else:
                        error_text = await response.text()
                        _LOGGER.error("call login_by_mobile request failed: %s - %s", response.status, error_text)
                        raise BololoApiClientError(
                            f"call login_by_mobile request HTTP {response.status}: {error_text}"
                        )
        finally:
            await _session.close()

    async def get_device_status(self, auth_token: str, product_key: str, mac: str):
        """获取设备状态"""
        _LOGGER.debug("request bololo device status with auth_token : %s , product_key : %s , mac : %s ",
                      auth_token, product_key, mac)
        url = f"{self._host}/bololo/app/device/status/{product_key}/{mac}"
        headers = {
            "Authorization": auth_token,
        }
        body_json = {}
        _session = aiohttp.ClientSession()
        try:
            async with async_timeout.timeout(10):  # 设置超时
                async with _session.post(url, headers=headers, ssl=False, json=body_json) as response:
                    if response.status == 200:
                        data = await response.json()
                        _LOGGER.debug("call get_device_status request response : %s", data)
                        data_code = data.get("code")
                        if data_code == "200":
                            _LOGGER.debug("call get_device_status request success: %s", data_code)
                            """
                           {
                                "code": "200",
                                "message": "本次请求成功",
                                "data": {
                                    "yogurt_mode_time": 8,
                                    "clean_mode_time": 5,
                                    "temp_mode": 1,
                                    "disinfection_time": 15,
                                    "disinfection_switch": false,
                                    "custom_atmosphere_lights": 0,
                                    "storage_switch": true,
                                    "dry_time": 40,
                                    "custom_total_time": 0,
                                    "custom_total_remain_time": 0,
                                    "night_mode": false,
                                    "dry_switch": false,
                                    "auto_switch": false,
                                    "error": 0,
                                    "custom_dis_remain_time": 0,
                                    "switch": false,
                                    "filter_life": 20,
                                    "work_remain_time": 0,
                                    "custom_dis_time": 0,
                                    "auto_time": 60,
                                    "dry_time_lowtemp": 70,
                                    "Data_Rev1": 0,
                                    "status_time": 1755765294647,
                                    "Data_Rev3": 0,
                                    "Data_Rev2": 0,
                                    "Data_Rev5": 0,
                                    "Data_Rev4": 0,
                                    "custom_dry_time": 0,
                                    "custom_dry": false,
                                    "custom_anion": false,
                                    "baby_mode_time": 3,
                                    "night_mode_brightness": 5,
                                    "custom_storage_switch": false,
                                    "auto_time_lowtemp": 90,
                                    "work_mode": 0,
                                    "custom_mute": false,
                                    "fruit_mode_time": 90,
                                    "storage_time": 4320,
                                    "anion": false,
                                    "custom_night": false,
                                    "custom_dry_remain_time": 0,
                                    "scene_mode_switch": 0,
                                    "warm_storage_time": 5,
                                    "custom_mode": 1,
                                    "custom_night_light": 0,
                                    "custom_storage_time": 0,
                                    "custom_dis": false,
                                    "status": 0
                                },
                                "display": null,
                                "error": false
                            }
                            """
                            return data.get("data")
                        else:
                            raise BololoApiClientError(
                                f"call get_device_status request HTTP response not excepted : {data}"
                            )
                    else:
                        error_text = await response.text()
                        _LOGGER.error("call get_device_status request failed: %s - %s", response.status, error_text)
                        raise BololoApiClientError(
                            f"call get_device_status request HTTP {response.status}: {error_text}"
                        )
        finally:
            await _session.close()

    async def list_home(self, auth_token: str):
        """拉取家庭列表"""
        _LOGGER.debug("request bololo list home with auth_token : %s", auth_token)
        url = f"{self._host}/app/smartHome/v2/homes"
        headers = {
            "Authorization": auth_token
        }
        _session = aiohttp.ClientSession()
        try:
            async with async_timeout.timeout(10):  # 设置超时
                async with _session.get(url, headers=headers, ssl=False) as response:
                    if response.status == 200:
                        data = await response.json()
                        _LOGGER.debug("call list_home request response : %s", data)
                        data_code = data.get("code")
                        if data_code == "200":
                            _LOGGER.debug("call list_home request success: %s", data_code)
                            """
                            {
                                "code": "200",
                                "message": "本次请求成功",
                                "data": [
                                    {
                                        "userId": 1111,
                                        "id": 1111,
                                        "name": "测试",
                                        "wallpaper": "./static/bg_a_x@3x.e7cfdbc7.jpg",
                                        "address": null,
                                        "longitude": null,
                                        "latitude": null,
                                        "bgColor": "rgb(89,135,139)",
                                        "rooms": [
                                            {
                                                "id": 1111,
                                                "homeId": 1111,
                                                "name": null,
                                                "icon": null,
                                                "devices": [],
                                                "groups": [],
                                                "default": true
                                            }
                                        ],
                                        "favorites": [],
                                        "owner": true,
                                        "wallsHistory": null,
                                        "homeNickName": "",
                                        "homeUserEmail": null,
                                        "homeUserMobile": "",
                                        "appType": null,
                                        "ctime": "2025-08-21 11:59:57",
                                        "mobileCountryCode": "CN"
                                    }
                                ],
                                "display": null,
                                "error": false
                            }
                            """
                            return data.get("data")
                        else:
                            raise BololoApiClientError(
                                f"call list_room request HTTP response not excepted : {data}"
                            )
                    else:
                        error_text = await response.text()
                        _LOGGER.error("call list_room request failed: %s - %s", response.status, error_text)
                        raise BololoApiClientError(
                            f"call list_room request HTTP {response.status}: {error_text}"
                        )
        finally:
            await _session.close()

    async def list_device(self, auth_token: str):
        """拉取设备列表"""
        _LOGGER.debug(
            "request bololo list device with auth_token : %s ",
            auth_token
        )
        url = f"{self._host}/app/smartHome/v2/users/devices"
        headers = {
            "Authorization": auth_token,
        }
        _session = aiohttp.ClientSession()
        try:
            async with async_timeout.timeout(10):  # 设置超时
                async with _session.get(url, headers=headers, ssl=False) as response:
                    if response.status == 200:
                        data = await response.json()
                        _LOGGER.debug("call list_device request response : %s", data)
                        data_code = data.get("code")
                        if data_code == "200":
                            _LOGGER.debug("call list_device request success: %s", data_code)
                            """
                             {
                                "code": "200",
                                "message": "本次请求成功",
                                "data": [
                                    {
                                        "sno": "",
                                        "productKey": "",
                                        "mac": "",
                                        "name": "消毒柜",
                                        "roomId": 123,
                                        "hide": false,
                                        "manufacturer": null,
                                        "userId": 123,
                                        "remark": null,
                                        "did": "",
                                        "deviceSourceType": 1,
                                        "longitude": null,
                                        "latitude": null,
                                        "country": null,
                                        "province": null,
                                        "city": null,
                                        "district": null,
                                        "address": null,
                                        "onlineStatus": 1,
                                        "mqttInfo": {
                                            "clusterName": "",
                                            "clusterAddress": "",
                                            "clusterMqttPort": 1883
                                        },
                                        "muserId": null
                                    }
                                ],
                                "display": null,
                                "error": false
                            }
                            """
                            return data.get("data")
                        else:
                            raise BololoApiClientError(
                                f"call list_device request HTTP response not excepted : {data}"
                            )
                    else:
                        error_text = await response.text()
                        _LOGGER.error("call list_device request failed: %s - %s", response.status, error_text)
                        raise BololoApiClientError(
                            f"call list_device request HTTP {response.status}: {error_text}"
                        )
        finally:
            await _session.close()
