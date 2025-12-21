from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
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

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: PonBikeCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities: list[SensorEntity] = []
    data = coordinator.data or {}
    bikes: list[dict[str, Any]] = data.get("bikes", [])
    states_by_id: dict[str, dict[str, Any]] = data.get("states_by_bike_id", {})

    for bike in bikes:
        bike_id = str(bike.get("bikeId") or "")
        if not bike_id:
            continue
        entities.append(PonBikeOdometerSensor(coordinator, entry, bike))
        entities.append(PonBikeModuleChargeSensor(coordinator, entry, bike))
        # (Optional later: add lastOnline timestamp sensor, etc.)

    async_add_entities(entities)


class _PonBikeBaseSensor(CoordinatorEntity[PonBikeCoordinator], SensorEntity):
    def __init__(self, coordinator: PonBikeCoordinator, entry: ConfigEntry, bike: dict[str, Any]) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._bike = bike
        self._bike_id = str(bike.get("bikeId") or "")
        self._bike_name = _bike_name(bike)
        self._attr_device_info = _device_info(bike)

    @property
    def _state(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return (data.get("states_by_bike_id") or {}).get(self._bike_id, {})


class PonBikeOdometerSensor(_PonBikeBaseSensor):
    _attr_icon = "mdi:counter"

    def __init__(self, coordinator: PonBikeCoordinator, entry: ConfigEntry, bike: dict[str, Any]) -> None:
        super().__init__(coordinator, entry, bike)
        self._attr_name = f"{self._bike_name} Odometer"
        self._attr_unique_id = f"{entry.entry_id}_{self._bike_id}_odometer"
        self._suggested_object_id = f"ponbike_{entry.entry_id}_{self._bike_id}_odometer"
        self._attr_native_unit_of_measurement = "km"
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> float | None:
        bt = self._state.get("bikeTelemetry") or {}
        odo = bt.get("odometer")
        try:
            return float(odo) if odo is not None else None
        except (TypeError, ValueError):
            return None


class PonBikeModuleChargeSensor(_PonBikeBaseSensor):
    _attr_icon = "mdi:battery"

    def __init__(self, coordinator: PonBikeCoordinator, entry: ConfigEntry, bike: dict[str, Any]) -> None:
        super().__init__(coordinator, entry, bike)
        self._attr_name = f"{self._bike_name} Module charge"
        self._attr_unique_id = f"{entry.entry_id}_{self._bike_id}_module_charge"
        self._suggested_object_id = f"ponbike_{entry.entry_id}_{self._bike_id}_module_charge"
        self._attr_native_unit_of_measurement = "%"
        self._attr_device_class = SensorDeviceClass.BATTERY

    @property
    def native_value(self) -> int | None:
        it = self._state.get("iotTelemetry") or {}
        mc = it.get("moduleCharge")
        try:
            return int(mc) if mc is not None else None
        except (TypeError, ValueError):
            return None

