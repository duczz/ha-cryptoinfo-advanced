#!/usr/bin/env python3
"""Config flow for Cryptoinfo Advanced."""

import os
import re

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_UNIT_OF_MEASUREMENT
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const.const import (
    _LOGGER,
    CONF_EXTRA_SENSOR_PROPERTY,
    CONF_API_KEY,
    CONF_API_DOMAIN_NAME,
    CONF_API_MODE,
    CONF_BLOCK_TIME_MINUTES,
    CONF_CRYPTOCURRENCY_NAME,
    CONF_CURRENCY_NAME,
    CONF_DIFF_MULTIPLIER,
    CONF_DIFFICULTY_WINDOW,
    CONF_EXTRA_SENSORS,
    CONF_FETCH_ARGS,
    CONF_HALVING_WINDOW,
    CONF_MAX_FETCH_FAILURES,
    CONF_MULTIPLIER,
    CONF_POOL_NAME,
    CONF_POOL_PREFIX,
    CONF_UPDATE_FREQUENCY,
    DEFAULT_MAX_FETCH_FAILURES,
    DOMAIN,
)
from .crypto_sensor import CryptoinfoAdvSensor

_ALL_API_MODES = [
    "price_main",
    "price_simple",
    "dominance",
    "chain_summary",
    "chain_control",
    "chain_orphans",
    "chain_block_time",
    "nomp_pool_stats",
    "mempool_stats",
    "mempool_fees",
    "mempool_next_block",
]

_NOMP_MODES = {"nomp_pool_stats"}
_CHAIN_MODES = {"chain_summary", "chain_block_time"}
_POOL_PREFIX_MODES = {"chain_control", "chain_summary", "nomp_pool_stats"}

# Popular CoinGecko coin IDs — user can still type any custom value
_POPULAR_COINS = [
    "bitcoin", "ethereum", "solana", "binancecoin", "ripple",
    "cardano", "dogecoin", "shiba-inu", "polkadot", "avalanche-2",
    "chainlink", "uniswap", "litecoin", "stellar", "cosmos",
    "monero", "tron", "algorand", "tezos", "near",
    "fantom", "sui", "fetch-ai", "aptos", "arbitrum",
    "optimism", "polygon", "aave", "maker", "dai",
    "vechain", "internet-computer", "hedera", "theta-token",
    "filecoin", "decentraland", "sandbox", "axie-infinity",
    "ethereum-classic", "bitcoin-cash", "litecoin", "eos",
]

# Popular currency codes
_POPULAR_CURRENCIES = [
    "eur", "usd", "gbp", "chf", "jpy", "aud", "cad", "cny", "krw",
    "btc", "eth", "sat",
]


def _core_schema(defaults: dict) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_API_MODE,
                default=defaults.get(CONF_API_MODE, "price_main"),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=_ALL_API_MODES,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_CRYPTOCURRENCY_NAME,
                default=defaults.get(CONF_CRYPTOCURRENCY_NAME, "bitcoin"),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=_POPULAR_COINS,
                    custom_value=True,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_CURRENCY_NAME,
                default=defaults.get(CONF_CURRENCY_NAME, "usd"),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=_POPULAR_CURRENCIES,
                    custom_value=True,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(
                CONF_UNIT_OF_MEASUREMENT,
                default=defaults.get(CONF_UNIT_OF_MEASUREMENT, "$"),
            ): selector.TextSelector(),
            vol.Optional(
                CONF_UPDATE_FREQUENCY,
                default=defaults.get(CONF_UPDATE_FREQUENCY, 60),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1, max=10080, mode=selector.NumberSelectorMode.BOX, unit_of_measurement="min"
                )
            ),
            vol.Optional(
                CONF_API_KEY,
                default=defaults.get(CONF_API_KEY, ""),
            ): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
            ),
        }
    )


def _advanced_schema(api_mode: str, defaults: dict) -> vol.Schema:
    fields = {
        vol.Optional(
            CONF_MULTIPLIER,
            default=defaults.get(CONF_MULTIPLIER, "1"),
        ): selector.TextSelector(),
        vol.Optional(
            CONF_MAX_FETCH_FAILURES,
            default=defaults.get(CONF_MAX_FETCH_FAILURES, DEFAULT_MAX_FETCH_FAILURES),
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=1, max=100, mode=selector.NumberSelectorMode.BOX
            )
        ),
        vol.Optional(
            CONF_EXTRA_SENSORS,
            default=defaults.get(CONF_EXTRA_SENSORS, []),
        ): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=CryptoinfoAdvSensor.get_valid_extra_sensor_keys(),
                multiple=True,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
    }

    if api_mode in _NOMP_MODES:
        fields[vol.Optional(CONF_API_DOMAIN_NAME, default=defaults.get(CONF_API_DOMAIN_NAME, ""))] = selector.TextSelector()
        fields[vol.Optional(CONF_POOL_NAME, default=defaults.get(CONF_POOL_NAME, ""))] = selector.TextSelector()

    if api_mode in _CHAIN_MODES:
        fields[vol.Optional(CONF_DIFF_MULTIPLIER, default=defaults.get(CONF_DIFF_MULTIPLIER, ""))] = selector.TextSelector()
        fields[vol.Optional(CONF_BLOCK_TIME_MINUTES, default=defaults.get(CONF_BLOCK_TIME_MINUTES, ""))] = selector.TextSelector()
        fields[vol.Optional(CONF_DIFFICULTY_WINDOW, default=defaults.get(CONF_DIFFICULTY_WINDOW, ""))] = selector.TextSelector()
        fields[vol.Optional(CONF_HALVING_WINDOW, default=defaults.get(CONF_HALVING_WINDOW, ""))] = selector.TextSelector()

    if api_mode in _POOL_PREFIX_MODES:
        fields[vol.Optional(CONF_POOL_PREFIX, default=defaults.get(CONF_POOL_PREFIX, ""))] = selector.TextSelector()
        fields[vol.Optional(CONF_FETCH_ARGS, default=defaults.get(CONF_FETCH_ARGS, ""))] = selector.TextSelector()

    return vol.Schema(fields)


# Matches !include_dir_merge_list / !include_dir_list anywhere in a YAML file
_INCLUDE_DIR_RE = re.compile(r"!include_dir(?:_merge)?_list\s+(\S+)")


def _remove_cryptoinfo_blocks(content: str) -> str:
    """Remove all '- platform: cryptoinfo_advanced' blocks from YAML content."""
    lines = content.splitlines(keepends=True)
    result = []
    skip_indent = None
    for line in lines:
        line_clean = line.rstrip("\n\r")
        stripped = line_clean.lstrip()
        indent = len(line_clean) - len(stripped)
        if skip_indent is not None:
            if not stripped or indent > skip_indent:
                continue
            else:
                skip_indent = None
        if stripped.startswith("- platform: cryptoinfo_advanced"):
            skip_indent = indent
            continue
        result.append(line)
    return "".join(result)


def _cleanup_include_dir(directory: str) -> None:
    """Remove cryptoinfo_advanced blocks from all YAML files in a directory."""
    if not os.path.isdir(directory):
        return
    for filename in os.listdir(directory):
        if not filename.endswith((".yaml", ".yml")):
            continue
        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
            new_content = _remove_cryptoinfo_blocks(content)
            if new_content == content:
                continue
            if not new_content.strip():
                os.remove(filepath)
                _LOGGER.info("Cryptoinfo Advanced: deleted empty sensor file %s", filepath)
            else:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_content)
                _LOGGER.info("Cryptoinfo Advanced: removed migrated YAML entries from %s", filepath)
        except Exception as err:
            _LOGGER.warning("Cryptoinfo Advanced: could not clean %s: %s", filepath, err)


async def _cleanup_yaml(hass) -> None:
    """Auto-remove cryptoinfo_advanced YAML sensor entries after migration."""
    config_dir = hass.config.config_dir
    config_file = os.path.join(config_dir, "configuration.yaml")
    try:
        with open(config_file, encoding="utf-8") as f:
            content = f.read()
        new_content = _remove_cryptoinfo_blocks(content)
        if new_content != content:
            with open(config_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            _LOGGER.info("Cryptoinfo Advanced: removed migrated YAML entries from configuration.yaml")
        # Also clean any !include_dir_merge_list / !include_dir_list directories
        for match in _INCLUDE_DIR_RE.finditer(content):
            include_dir = os.path.join(config_dir, match.group(1))
            _cleanup_include_dir(include_dir)
    except Exception as err:
        _LOGGER.warning("Cryptoinfo Advanced: could not auto-clean configuration.yaml: %s", err)


def _make_title(data: dict) -> str:
    crypto = data.get(CONF_CRYPTOCURRENCY_NAME, "?").upper()
    currency = data.get(CONF_CURRENCY_NAME, "?").upper()
    mode = data.get(CONF_API_MODE, "")
    return f"{crypto}/{currency} ({mode})"


class CryptoinfoAdvConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Cryptoinfo Advanced."""

    VERSION = 1

    def __init__(self):
        self._core_data: dict = {}

    async def async_step_user(self, user_input=None):
        """Step 1: Core sensor parameters."""
        if user_input is not None:
            self._core_data = user_input
            return await self.async_step_advanced()

        return self.async_show_form(
            step_id="user",
            data_schema=_core_schema({}),
        )

    async def async_step_advanced(self, user_input=None):
        """Step 2: Advanced / mode-specific parameters."""
        api_mode = self._core_data.get(CONF_API_MODE, "price_main")

        if user_input is not None:
            data = {**self._core_data, **user_input}
            return self.async_create_entry(title=_make_title(data), data=data)

        return self.async_show_form(
            step_id="advanced",
            data_schema=_advanced_schema(api_mode, {}),
        )

    async def async_step_import(self, import_data: dict):
        """Create a config entry from a YAML sensor config (one-time migration)."""
        # pool_prefix: list → comma-separated string
        raw_prefix = import_data.get(CONF_POOL_PREFIX, [""])
        pool_prefix_str = ",".join(raw_prefix) if isinstance(raw_prefix, list) else (raw_prefix or "")

        # extra_sensors: list of dicts → list of property key strings
        raw_extra = import_data.get(CONF_EXTRA_SENSORS, [])
        if raw_extra and isinstance(raw_extra[0], dict):
            extra_keys = [s[CONF_EXTRA_SENSOR_PROPERTY] for s in raw_extra if s.get(CONF_EXTRA_SENSOR_PROPERTY)]
        else:
            extra_keys = list(raw_extra)

        data = {
            CONF_API_MODE: import_data.get(CONF_API_MODE, "price_main"),
            CONF_CRYPTOCURRENCY_NAME: import_data.get(CONF_CRYPTOCURRENCY_NAME, "bitcoin"),
            CONF_CURRENCY_NAME: import_data.get(CONF_CURRENCY_NAME, "usd"),
            CONF_UNIT_OF_MEASUREMENT: import_data.get(CONF_UNIT_OF_MEASUREMENT, "$"),
            CONF_UPDATE_FREQUENCY: float(import_data.get(CONF_UPDATE_FREQUENCY, 60)),
            CONF_API_KEY: import_data.get(CONF_API_KEY, ""),
            CONF_MULTIPLIER: str(import_data.get(CONF_MULTIPLIER, "1")),
            CONF_MAX_FETCH_FAILURES: int(import_data.get(CONF_MAX_FETCH_FAILURES, DEFAULT_MAX_FETCH_FAILURES)),
            CONF_EXTRA_SENSORS: extra_keys,
            CONF_POOL_PREFIX: pool_prefix_str,
            CONF_FETCH_ARGS: import_data.get(CONF_FETCH_ARGS, ""),
            CONF_API_DOMAIN_NAME: import_data.get(CONF_API_DOMAIN_NAME, ""),
            CONF_POOL_NAME: import_data.get(CONF_POOL_NAME, ""),
            CONF_DIFF_MULTIPLIER: import_data.get(CONF_DIFF_MULTIPLIER, ""),
            CONF_BLOCK_TIME_MINUTES: import_data.get(CONF_BLOCK_TIME_MINUTES, ""),
            CONF_DIFFICULTY_WINDOW: import_data.get(CONF_DIFFICULTY_WINDOW, ""),
            CONF_HALVING_WINDOW: import_data.get(CONF_HALVING_WINDOW, ""),
        }

        await _cleanup_yaml(self.hass)
        return self.async_create_entry(title=_make_title(data), data=data)

    @staticmethod
    @callback
    def async_get_options_flow(_config_entry):
        return CryptoinfoAdvOptionsFlow()


class CryptoinfoAdvOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow — edit all sensor parameters."""

    async def async_step_init(self, user_input=None):
        """Show all parameters for editing."""
        current = {**self.config_entry.data, **self.config_entry.options}
        api_mode = current.get(CONF_API_MODE, "price_main")

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Merge core + advanced fields into one options schema
        core_fields = _core_schema(current).schema
        advanced_fields = _advanced_schema(api_mode, current).schema
        combined = vol.Schema({**core_fields, **advanced_fields})

        return self.async_show_form(
            step_id="init",
            data_schema=combined,
        )
