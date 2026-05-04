"""Custom types for ha_solar_forecast."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .coordinator import SolarForecastDataUpdateCoordinator


type SolarForecastConfigEntry = ConfigEntry[SolarForecastData]


@dataclass
class SolarForecastData:
    """Runtime data stored on the config entry."""

    coordinator: SolarForecastDataUpdateCoordinator


@dataclass
class ForecastPoint:
    """A single forecasted solar production value."""

    datetime: str
    power_w: float
    energy_wh: float


@dataclass
class CoordinatorData:
    """Data returned by the coordinator after each refresh."""

    current_power_w: float
    forecast: list[ForecastPoint]
