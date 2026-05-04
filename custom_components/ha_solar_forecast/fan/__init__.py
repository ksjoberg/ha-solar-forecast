"""Fan platform for ha_solar_forecast."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.ha_solar_forecast.const import PARALLEL_UPDATES as PARALLEL_UPDATES
from homeassistant.components.fan import FanEntityDescription

from .air_purifier_fan import ENTITY_DESCRIPTIONS as FAN_DESCRIPTIONS, SolarForecastFan

if TYPE_CHECKING:
    from custom_components.ha_solar_forecast.data import SolarForecastConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

# Combine all entity descriptions from different modules
ENTITY_DESCRIPTIONS: tuple[FanEntityDescription, ...] = (*FAN_DESCRIPTIONS,)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SolarForecastConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the fan platform."""
    async_add_entities(
        SolarForecastFan(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )
