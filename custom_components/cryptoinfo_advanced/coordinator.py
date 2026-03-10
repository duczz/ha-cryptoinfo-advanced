#!/usr/bin/env python3
"""DataUpdateCoordinator for Cryptoinfo Advanced."""

import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)


class CryptoinfoAdvCoordinator(DataUpdateCoordinator):
    """Coordinator managing periodic data fetching for a single Cryptoinfo sensor."""

    def __init__(self, hass, sensor):
        super().__init__(
            hass,
            _LOGGER,
            name=sensor.name,
            update_interval=sensor._update_frequency,
        )
        self._sensor = sensor

    async def _async_update_data(self):
        """Fetch data from the sensor's API endpoint."""
        try:
            await self._sensor._async_fetch_data()
        except Exception as err:
            raise UpdateFailed(
                f"Error fetching data for {self._sensor.name}: {err}"
            ) from err
        return self._sensor.data
