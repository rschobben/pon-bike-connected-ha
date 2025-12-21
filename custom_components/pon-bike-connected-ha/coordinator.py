from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PonBikeApi
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class PonBikeCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll bikes/info + last-known-states and merge into one data structure."""

    def __init__(self, hass: HomeAssistant, api: PonBikeApi) -> None:
        self.api = api
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            bikes = await self.api.async_get_bikes_info()
            states = await self.api.async_get_last_known_states()

            # bikes is usually a list; if provider changes, keep it robust
            bikes_list: list[dict[str, Any]] = bikes if isinstance(bikes, list) else []

            states_by_bike_id: dict[str, dict[str, Any]] = {}
            if isinstance(states, list):
                for s in states:
                    bid = s.get("bikeId")
                    if bid:
                        states_by_bike_id[str(bid)] = s

            return {
                "bikes": bikes_list,
                "states_by_bike_id": states_by_bike_id,
            }
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(str(err)) from err

