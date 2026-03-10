#!/usr/bin/env python3
"""
Sensor component for Cryptoinfo Advanced
Author: TheHoliestRoger
"""

from datetime import timedelta

import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import CONF_ID, CONF_UNIT_OF_MEASUREMENT
import homeassistant.helpers.config_validation as cv

from .const.const import (
    _LOGGER,
    DEFAULT_MAX_FETCH_FAILURES,
    CONF_CRYPTOCURRENCY_NAME,
    CONF_CURRENCY_NAME,
    CONF_MULTIPLIER,
    CONF_UPDATE_FREQUENCY,
    CONF_API_MODE,
    CONF_POOL_PREFIX,
    CONF_FETCH_ARGS,
    CONF_EXTRA_SENSORS,
    CONF_EXTRA_SENSOR_PROPERTY,
    CONF_API_DOMAIN_NAME,
    CONF_POOL_NAME,
    CONF_DIFF_MULTIPLIER,
    CONF_BLOCK_TIME_MINUTES,
    CONF_DIFFICULTY_WINDOW,
    CONF_HALVING_WINDOW,
    CONF_MAX_FETCH_FAILURES,
    CONF_API_KEY,
    DOMAIN,
)

from .manager import CryptoInfoAdvEntityManager
from .crypto_sensor import CryptoinfoAdvSensor

_CONF_ID = "id"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_ID, default=""): cv.string,
        vol.Optional(CONF_CRYPTOCURRENCY_NAME, default="bitcoin"): cv.string,
        vol.Optional(CONF_CURRENCY_NAME, default="usd"): cv.string,
        vol.Optional(CONF_UNIT_OF_MEASUREMENT, default="$"): cv.string,
        vol.Optional(CONF_MULTIPLIER, default="1"): cv.string,
        vol.Optional(CONF_UPDATE_FREQUENCY, default="60"): cv.string,
        vol.Optional(CONF_API_MODE, default="price_main"): cv.string,
        vol.Optional(CONF_POOL_PREFIX, default=[""]): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(CONF_FETCH_ARGS, default=""): cv.string,
        vol.Optional(CONF_EXTRA_SENSORS, default=[]): vol.All(
            cv.ensure_list,
            [
                vol.Schema(
                    {
                        vol.Required(CONF_EXTRA_SENSOR_PROPERTY): cv.string,
                        vol.Optional(CONF_UNIT_OF_MEASUREMENT, default="$"): cv.string,
                        vol.Optional(CONF_ID, default=""): cv.string,
                    }
                )
            ],
        ),
        vol.Optional(CONF_API_DOMAIN_NAME, default=""): cv.string,
        vol.Optional(CONF_POOL_NAME, default=""): cv.string,
        vol.Optional(CONF_DIFF_MULTIPLIER, default=""): cv.string,
        vol.Optional(CONF_BLOCK_TIME_MINUTES, default=""): cv.string,
        vol.Optional(CONF_DIFFICULTY_WINDOW, default=""): cv.string,
        vol.Optional(CONF_HALVING_WINDOW, default=""): cv.string,
        vol.Optional(CONF_MAX_FETCH_FAILURES, default=DEFAULT_MAX_FETCH_FAILURES): cv.positive_int,
        vol.Optional(CONF_API_KEY, default=""): cv.string,
    }
)


async def async_setup_platform(hass, config, _async_add_entities, _discovery_info=None):
    """Trigger import of a YAML sensor config as a config entry (one-time migration)."""
    _LOGGER.warning(
        "Cryptoinfo Advanced: YAML sensor '%s' is being migrated to a config entry. "
        "Please remove the 'platform: cryptoinfo_advanced' entry from configuration.yaml.",
        config.get(CONF_ID) or config.get(CONF_CRYPTOCURRENCY_NAME, ""),
    )
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_IMPORT},
            data=dict(config),
        )
    )


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Cryptoinfo Advanced sensors from a config entry."""
    data = {**config_entry.data, **config_entry.options}

    # pool_prefix is stored as a comma-separated string in the config entry
    raw_pool_prefix = data.get(CONF_POOL_PREFIX, "")
    pool_prefix = [p.strip() for p in raw_pool_prefix.split(",")] if raw_pool_prefix else [""]

    # extra_sensors are stored as a list of property-key strings → convert to sensor dicts
    unit = data.get(CONF_UNIT_OF_MEASUREMENT, "$")
    extra_sensor_keys = data.get(CONF_EXTRA_SENSORS, [])
    extra_sensors_config = [
        {
            CONF_EXTRA_SENSOR_PROPERTY: key,
            CONF_UNIT_OF_MEASUREMENT: unit,
            _CONF_ID: "",
        }
        for key in extra_sensor_keys
    ]

    try:
        new_sensor = CryptoinfoAdvSensor(
            hass,
            data.get(CONF_CRYPTOCURRENCY_NAME, "bitcoin").lower().strip(),
            data.get(CONF_CURRENCY_NAME, "usd").lower().strip(),
            unit,
            str(data.get(CONF_MULTIPLIER, "1")).strip(),
            timedelta(minutes=float(data.get(CONF_UPDATE_FREQUENCY, 60))),
            id_name="",
            unique_id=config_entry.entry_id,
            state_class=None,
            api_mode=data.get(CONF_API_MODE, "price_main").lower().strip(),
            pool_prefix=pool_prefix,
            fetch_args=data.get(CONF_FETCH_ARGS, ""),
            extra_sensors=extra_sensors_config,
            api_domain_name=data.get(CONF_API_DOMAIN_NAME, "").lower().strip(),
            pool_name=data.get(CONF_POOL_NAME, "").strip(),
            diff_multiplier=data.get(CONF_DIFF_MULTIPLIER, ""),
            block_time_minutes=data.get(CONF_BLOCK_TIME_MINUTES, ""),
            difficulty_window=data.get(CONF_DIFFICULTY_WINDOW, ""),
            halving_window=data.get(CONF_HALVING_WINDOW, ""),
            max_fetch_failures=int(data.get(CONF_MAX_FETCH_FAILURES, DEFAULT_MAX_FETCH_FAILURES)),
            api_key=data.get(CONF_API_KEY, ""),
        )
        if new_sensor.check_valid_config(False):
            entities = [new_sensor] + new_sensor.init_child_sensors()
            async_add_entities(entities)
            CryptoInfoAdvEntityManager.instance().add_entities(entities)
    except Exception as error:
        _LOGGER.error(f"{type(error).__name__}: {error}")
        return False

    return True
