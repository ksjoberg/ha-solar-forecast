"""Solar production forecast sensor entity."""

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from custom_components.ha_solar_forecast.const import PARALLEL_UPDATES as PARALLEL_UPDATES  # noqa: PLC0414
from custom_components.ha_solar_forecast.entity.base import SolarForecastEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import UnitOfPower

if TYPE_CHECKING:
    from custom_components.ha_solar_forecast.coordinator import SolarForecastDataUpdateCoordinator

ENTITY_DESCRIPTION = SensorEntityDescription(
    key="solar_production",
    translation_key="solar_production",
    device_class=SensorDeviceClass.POWER,
    native_unit_of_measurement=UnitOfPower.WATT,
    state_class=SensorStateClass.MEASUREMENT,
    suggested_display_precision=0,
)


class SolarForecastProductionSensor(SolarForecastEntity, SensorEntity):
    """Current solar power production with full hourly forecast as an attribute."""

    entity_description: SensorEntityDescription

    def __init__(self, coordinator: SolarForecastDataUpdateCoordinator) -> None:
        """Initialise the sensor."""
        super().__init__(coordinator, ENTITY_DESCRIPTION)

    @property
    def native_value(self) -> float | None:
        """Return the current estimated solar power (W)."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.current_power_w

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the full forecast as an attribute."""
        if self.coordinator.data is None:
            return {}
        return {
            "forecast": [asdict(pt) for pt in self.coordinator.data.forecast],
        }
