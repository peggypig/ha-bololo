# -*- coding: utf-8 -*-
"""
消毒柜
"""
from __future__ import annotations

import asyncio
from typing import Any
import logging
import time

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo, DeviceEntry
from homeassistant.helpers.entity import Entity

from .const import (DOMAIN)
from .api_client import BololoApiClient
# pylint: disable=line-too-long
from .device import BololoDevice, BololoDeviceType

from .disinfection_cabinet_status import BololoDisinfectionCabinetStatus
from .disinfection_cabinet_switch import DisinfectionCabinetSwitch
from .disinfection_cabinet_switch_function import BololoDisinfectionCabinetSwitchFunction

_LOGGER = logging.getLogger(__name__)


class BololoDisinfectionCabinet(BololoDevice):
    # pylint: disable=too-many-instance-attributes
    """
        "sno": "111111",
        "productKey": "111111",
        "mac": "111111",
        "name": "消毒柜",
        "roomId": 11111,
        "hide": false,
        "manufacturer": null,
        "userId": 11111,
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
            "clusterMqttPort": 1234
        },
        "muserId": null
    """

    def __init__(
            self, device_info_from_server: dict[str, Any],
            hass: HomeAssistant,
            config_entry: ConfigEntry
    ):
        self._hass = hass
        self._config_entry = config_entry
        BololoDevice.__init__(
            self,
            BololoDeviceType.DISINFECTION_CABINET,
            BololoApiClient(
                self._config_entry.data.get("app_key"),
                self._config_entry.data.get("mobile"),
            )
        )
        self._device_entry = None
        self._sno = device_info_from_server.get("sno")
        self._product_key = device_info_from_server.get("productKey")
        self._mac = device_info_from_server.get("mac")
        self._name = device_info_from_server.get("name")
        self._room = device_info_from_server.get("roomId")
        self._hide = device_info_from_server.get("hide")
        self._manufacturer = device_info_from_server.get("manufacturer")
        self._user = device_info_from_server.get("userId")
        self._remark = device_info_from_server.get("remark")
        self._did = device_info_from_server.get("did")
        self._device_source_type = device_info_from_server.get("deviceSourceType")
        self._longitude = device_info_from_server.get("longitude")
        self._latitude = device_info_from_server.get("latitude")
        self._country = device_info_from_server.get("country")
        self._province = device_info_from_server.get("province")
        self._city = device_info_from_server.get("city")
        self._district = device_info_from_server.get("district")
        self._address = device_info_from_server.get("address")
        self._online_status = device_info_from_server.get("onlineStatus")
        if device_info_from_server.get("mqttInfo") is not None:
            self._mqtt_info = {
                "cluster_name": device_info_from_server.get("mqttInfo").get("clusterName"),
                "cluster_address": device_info_from_server.get("mqttInfo").get("clusterAddress"),
                "cluster_mqtt_port": device_info_from_server.get("mqttInfo").get("clusterMqttPort"),
            }
        self._device_status_request_timestamp_ms = None
        self._device_status_request_lock = asyncio.Lock()
        self._device_status = None
        self._entities = []
        self._device_info = DeviceInfo(
            identifiers={(DOMAIN, self._did)},
            name=self._name,
            manufacturer=self._manufacturer,
            sw_version="UnknownSW",
            hw_version="UnknownHW",
            configuration_url=None,
            serial_number=self._sno,
        )
        for function in BololoDisinfectionCabinetSwitchFunction:
            disinfection_cabinet_switch = DisinfectionCabinetSwitch(config_entry, function)
            disinfection_cabinet_switch.set_disinfection_cabinet(self)
            self._entities.append(disinfection_cabinet_switch)

    @property
    def device_entry(self):
        """
        Return the device entry
        """
        return self._device_entry

    @device_entry.setter
    def device_entry(self, device_entry: DeviceEntry):
        """
        Set the device entry
        """
        self._device_entry = device_entry

    @property
    async def device_status(self) -> BololoDisinfectionCabinetStatus:
        """
        Return the device status
        """
        _LOGGER.debug("call device_status , wait lock")
        async with self._device_status_request_lock:
            _LOGGER.debug("call device_status , got lock")
            if self._device_status is None:
                _LOGGER.debug(
                    "call device_status , request device status from server , because device status is None")
                self._device_status = BololoDisinfectionCabinetStatus(
                    await self._api_client.get_device_status(
                        auth_token=self._config_entry.data.get("token").get("userToken"),
                        product_key=self._product_key,
                        mac=self._mac
                    )
                )
                self._device_status_request_timestamp_ms = int(round(time.time() * 1000))
                return self._device_status

            current_timestamp_ms = int(round(time.time() * 1000))
            if current_timestamp_ms - self._device_status_request_timestamp_ms > 10 * 1000:
                _LOGGER.debug(
                    "call device_status , request device status from server , because device status is older than 10s"
                )
                self._device_status = BololoDisinfectionCabinetStatus(
                    await self._api_client.get_device_status(
                        auth_token=self._config_entry.data.get("token").get("userToken"),
                        product_key=self._product_key,
                        mac=self._mac
                    )
                )
                self._device_status_request_timestamp_ms = int(round(time.time() * 1000))
                return self._device_status

            _LOGGER.debug("call device_status , use cached device status")
            return self._device_status

    @property
    def device_info(self) -> DeviceInfo:
        """
        Return the device info
        """
        return self._device_info

    def get_entities(self) -> list[Entity]:
        """
        Return all entities
        """
        _LOGGER.debug("call get_entities , entities : %s", self._entities)
        return self._entities

    @property
    def mac(self) -> str:
        """
        Return the mac address
        """
        return self._mac

    async def async_control_switch(self, switch_function_on_server: str, status: bool) -> None:
        """
        控制设备开关
        """
        _LOGGER.debug("call async_control_switch , switch_function_on_server : %s , status : %s",
                      switch_function_on_server, status)
        await self._api_client.control_device(
            auth_token=self._config_entry.data.get("token").get("userToken"),
            product_key=self._product_key,
            mac=self._mac,
            command_data={
                switch_function_on_server: status
            }
        )
        if self._device_status is not None:
            setattr(self._device_status, f"_{switch_function_on_server}", status)
