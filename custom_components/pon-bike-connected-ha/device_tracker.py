from __future__ import annotations

from typing import Any

from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PonBikeCoordinator


def _bike_name(bike: dict[str, Any]) -> str:
    nickname = bike.get("nickName") or bike.get("nickname")
    frame = bike.get("frameNumber")
    bike_id = bike.get("bikeId")

    if nickname and frame:
        return f"{nickname} ({frame})"
    if nickname:
        return nickname
    if frame:
        return frame
    if bike_id:
        return bike_id
    return "Bike"

def _device_info(bike: dict[str, Any]) -> dict[str, Any]:
    bike_id = str(bike.get("bikeId") or "")
    manufacturer_id = bike.get("manufacturerId")

    manufacturer = "PON"
    if manufacturer_id == "UA":
        manufacturer = "Urban Arrow"

    # Show human-friendly model in the device card
    model = bike.get("displayName") or bike.get("sku") or "Connected Bike"
    serial = bike.get("frameNumber") or None

    # Concatenate hardware attributes into hw_version
    hw_parts = [
        bike.get("category"),
        bike.get("type"),
        bike.get("color"),
        bike.get("driveUnitType"),
    ]
    hw_parts = [str(p) for p in hw_parts if p]
    hw_version = "-".join(hw_parts) if hw_parts else None

    info: dict[str, Any] = {
        "identifiers": {(DOMAIN, bike_id)},
        "name": _bike_name(bike),
        "manufacturer": manufacturer,
        "model": model,
        "serial_number": serial,
    }

    if hw_version:
        info["hw_version"] = hw_version

    return info

def _extract_lat_lon(state: dict[str, Any]) -> tuple[float | None, float | None]:
    loc = state.get("location") or {}
    coord = (loc.get("coordinate") or {}) if isinstance(loc, dict) else {}
    lat = coord.get("latitude")
    lon = coord.get("longitude")
    try:
        return (float(lat), float(lon))
    except (TypeError, ValueError):
        return (None, None)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: PonBikeCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities: list[TrackerEntity] = []
    data = coordinator.data or {}
    bikes: list[dict[str, Any]] = data.get("bikes", [])

    for bike in bikes:
        bike_id = str(bike.get("bikeId") or "")
        if not bike_id:
            continue
        entities.append(PonBikeTracker(coordinator, entry, bike))

    async_add_entities(entities)


class PonBikeTracker(CoordinatorEntity[PonBikeCoordinator], TrackerEntity):
    _attr_should_poll = False

    def __init__(self, coordinator: PonBikeCoordinator, entry: ConfigEntry, bike: dict[str, Any]) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._bike = bike
        self._bike_id = str(bike.get("bikeId") or "")
        self._bike_name = _bike_name(bike)
        self._attr_device_info = _device_info(bike)

        self._attr_name = f"{self._bike_name} Location"
        self._attr_unique_id = f"{entry.entry_id}_{self._bike_id}_tracker"
        self._attr_suggested_object_id = f"ponbike_{entry.entry_id}_{self._bike_id}_tracker"

    @property
    def _state(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return (data.get("states_by_bike_id") or {}).get(self._bike_id, {})

    @property
    def latitude(self) -> float | None:
        lat, _ = _extract_lat_lon(self._state)
        return lat

    @property
    def longitude(self) -> float | None:
        _, lon = _extract_lat_lon(self._state)
        return lon

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        s = self._state
        bt = s.get("bikeTelemetry") or {}
        it = s.get("iotTelemetry") or {}
        return {
            "bikeId": self._bike_id,
            "lastOnline": s.get("lastOnline"),
            "odometer_km": bt.get("odometer"),
            "module_charge_pct": it.get("moduleCharge"),
        }

