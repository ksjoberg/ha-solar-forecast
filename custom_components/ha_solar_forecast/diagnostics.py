"""Diagnostics support for ha_solar_forecast."""

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.redact import async_redact_data

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import SolarForecastConfigEntry

TO_REDACT: set[str] = set()


async def async_get_config_entry_diagnostics(
    _hass: HomeAssistant,
    entry: SolarForecastConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data.coordinator

    forecast_sample = []
    if coordinator.data:
        forecast_sample = [asdict(pt) for pt in coordinator.data.forecast[:5]]

    return {
        "config": async_redact_data(dict(entry.data), TO_REDACT),
        "current_power_w": coordinator.data.current_power_w if coordinator.data else None,
        "forecast_sample": forecast_sample,
        "last_update_success": coordinator.last_update_success,
        "update_interval": str(coordinator.update_interval),
    }
