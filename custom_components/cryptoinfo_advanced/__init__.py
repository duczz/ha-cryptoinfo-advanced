#!/usr/bin/env python3
"""Cryptoinfo Advanced integration."""

__version__ = "0.4.0"

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const.const import DOMAIN, PLATFORMS
from .manager import CryptoInfoAdvEntityManager


async def async_setup(hass: HomeAssistant, _config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Cryptoinfo Advanced from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Only create the manager once — shared across all sensor entries
    if "manager" not in hass.data[DOMAIN]:
        manager = CryptoInfoAdvEntityManager()
        hass.data[DOMAIN]["manager"] = manager
        CryptoInfoAdvEntityManager._instance = manager

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unloaded:
        # Only clear the manager when the last entry is removed
        remaining = [
            e for e in hass.config_entries.async_entries(DOMAIN)
            if e.entry_id != entry.entry_id
        ]
        if not remaining:
            hass.data[DOMAIN].pop("manager", None)
            CryptoInfoAdvEntityManager._instance = None

    return unloaded


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
