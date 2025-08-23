# -*- coding: utf-8 -*-
"""
消毒柜状态
"""
from typing import Any


class BololoDisinfectionCabinetStatus:
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-few-public-methods
    """
        "yogurt_mode_time": 8,
		"clean_mode_time": 5,
		"temp_mode": 1,
		"disinfection_time": 10,
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
		"switch": true,
		"filter_life": 20,
		"work_remain_time": 0,
		"custom_dis_time": 0,
		"auto_time": 60,
		"dry_time_lowtemp": 70,
		"Data_Rev1": 0,
		"status_time": 1755948969268,
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
		"status": 1
    """

    def __init__(self, status_info: dict[str, Any]):
        self._yogurt_mode_time = status_info.get("yogurt_mode_time")
        self._clean_mode_time = status_info.get("clean_mode_time")
        self._temp_mode = status_info.get("temp_mode")
        self._disinfection_time = status_info.get("disinfection_time")
        self._disinfection_switch = status_info.get("disinfection_switch")
        self._custom_atmosphere_lights = status_info.get("custom_atmosphere_lights")
        self._storage_switch = status_info.get("storage_switch")
        self._dry_time = status_info.get("dry_time")
        self._custom_total_time = status_info.get("custom_total_time")
        self._custom_total_remain_time = status_info.get("custom_total_remain_time")
        self._night_mode = status_info.get("night_mode")
        self._dry_switch = status_info.get("dry_switch")
        self._auto_switch = status_info.get("auto_switch")
        self._error = status_info.get("error")
        self._custom_dis_remain_time = status_info.get("custom_dis_remain_time")
        self._switch = status_info.get("switch")
        self._filter_life = status_info.get("filter_life")
        self._work_remain_time = status_info.get("work_remain_time")
        self._custom_dis_time = status_info.get("custom_dis_time")
        self._auto_time = status_info.get("auto_time")
        self._dry_time_lowtemp = status_info.get("dry_time_lowtemp")
        self._data_rev1 = status_info.get("Data_Rev1")
        self._status_time = status_info.get("status_time")
        self._data_rev3 = status_info.get("Data_Rev3")
        self._data_rev2 = status_info.get("Data_Rev2")
        self._data_rev5 = status_info.get("Data_Rev5")
        self._data_rev4 = status_info.get("Data_Rev4")
        self._custom_dry_time = status_info.get("custom_dry_time")
        self._custom_dry = status_info.get("custom_dry")
        self._custom_anion = status_info.get("custom_anion")
        self._baby_mode_time = status_info.get("baby_mode_time")
        self._night_mode_brightness = status_info.get("night_mode_brightness")
        self._custom_storage_switch = status_info.get("custom_storage_switch")
        self._auto_time_lowtemp = status_info.get("auto_time_lowtemp")
        self._work_mode = status_info.get("work_mode")
        self._custom_mute = status_info.get("custom_mute")
        self._fruit_mode_time = status_info.get("fruit_mode_time")
        self._storage_time = status_info.get("storage_time")
        self._anion = status_info.get("anion")
        self._custom_night = status_info.get("custom_night")
        self._custom_dry_remain_time = status_info.get("custom_dry_remain_time")
        self._scene_mode_switch = status_info.get("scene_mode_switch")
        self._warm_storage_time = status_info.get("warm_storage_time")
        self._custom_mode = status_info.get("custom_mode")
        self._custom_night_light = status_info.get("custom_night_light")
        self._custom_storage_time = status_info.get("custom_storage_time")
        self._custom_dis = status_info.get("custom_dis")
        self._status = status_info.get("status")