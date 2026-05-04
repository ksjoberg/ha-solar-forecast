"""Solar Forecast custom integration for Home Assistant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import Platform
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN
from .coordinator import SolarForecastDataUpdateCoordinator
from .data import SolarForecastData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import SolarForecastConfigEntry

PLATFORMS: list[Platform] = [Platform.SENSOR]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(_hass: HomeAssistant, _config: dict) -> bool:
    """Set up integration-level services (none currently)."""
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SolarForecastConfigEntry,
) -> bool:
    """Set up Solar Forecast from a config entry."""
    coordinator = SolarForecastDataUpdateCoordinator(hass, entry)
    entry.runtime_data = SolarForecastData(coordinator=coordinator)

    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: SolarForecastConfigEntry,
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
