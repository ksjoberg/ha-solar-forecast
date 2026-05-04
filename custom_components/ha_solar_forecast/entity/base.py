"""Base entity class for ha_solar_forecast."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.ha_solar_forecast.coordinator import SolarForecastDataUpdateCoordinator
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

if TYPE_CHECKING:
    from homeassistant.helpers.entity import EntityDescription


class SolarForecastEntity(CoordinatorEntity[SolarForecastDataUpdateCoordinator]):
    """Base entity: ties unique ID and device info to the config entry."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SolarForecastDataUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """Initialise the base entity."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(coordinator.config_entry.domain, coordinator.config_entry.entry_id)},
            name=coordinator.config_entry.title,
            manufacturer="Solar Forecast",
        )
