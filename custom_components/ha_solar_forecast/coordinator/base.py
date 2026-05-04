"""DataUpdateCoordinator for Solar Forecast."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any, cast

from custom_components.ha_solar_forecast.const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_PANELS,
    CONF_WEATHER_ENTITY,
    DEFAULT_ATTENUATION,
    LOGGER,
    SYSTEM_EFFICIENCY,
    UPDATE_INTERVAL_MINUTES,
    WEATHER_ATTENUATION,
)
from custom_components.ha_solar_forecast.data import CoordinatorData, ForecastPoint
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .solar_math import clear_sky_ghi, solar_elevation_azimuth, total_system_power_w

if TYPE_CHECKING:
    from custom_components.ha_solar_forecast.data import SolarForecastConfigEntry
    from homeassistant.core import HomeAssistant


class SolarForecastDataUpdateCoordinator(DataUpdateCoordinator[CoordinatorData]):
    """Coordinator that fetches weather forecasts and computes solar production."""

    config_entry: SolarForecastConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: SolarForecastConfigEntry) -> None:
        """Initialise the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=f"Solar Forecast ({config_entry.title})",
            update_interval=timedelta(minutes=UPDATE_INTERVAL_MINUTES),
            always_update=False,
            config_entry=config_entry,
        )

    async def _async_update_data(self) -> CoordinatorData:
        """Fetch hourly weather forecasts and compute solar production for each slot."""
        entry_data = self.config_entry.data
        lat: float = entry_data[CONF_LATITUDE]
        lon: float = entry_data[CONF_LONGITUDE]
        panels: list[dict[str, Any]] = entry_data.get(CONF_PANELS, [])
        weather_entity: str = entry_data[CONF_WEATHER_ENTITY]

        if not panels:
            return CoordinatorData(current_power_w=0.0, forecast=[])

        forecasts = await self._fetch_forecasts(weather_entity)
        if not forecasts:
            return CoordinatorData(current_power_w=0.0, forecast=[])

        forecast_points = self._compute_forecast(lat, lon, panels, forecasts)

        current_power = self._interpolate_current(forecast_points)
        return CoordinatorData(current_power_w=current_power, forecast=forecast_points)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _fetch_forecasts(self, weather_entity: str) -> list[dict[str, Any]]:
        """Call weather.get_forecasts and return the hourly list."""
        try:
            raw = await self.hass.services.async_call(
                "weather",
                "get_forecasts",
                {"entity_id": weather_entity, "type": "hourly"},
                blocking=True,
                return_response=True,
            )
        except Exception as exc:
            raise UpdateFailed(f"Failed to fetch weather forecast from {weather_entity}: {exc}") from exc

        if not isinstance(raw, dict):
            return []
        entity_data = raw.get(weather_entity)
        if not isinstance(entity_data, dict):
            return []
        forecasts = entity_data.get("forecast")
        if not isinstance(forecasts, list):
            return []
        return cast(list[dict[str, Any]], forecasts)

    def _compute_forecast(
        self,
        lat: float,
        lon: float,
        panels: list[dict[str, Any]],
        raw_forecasts: list[dict[str, Any]],
    ) -> list[ForecastPoint]:
        """Convert raw weather forecast slots into solar power estimates."""
        points: list[ForecastPoint] = []

        for slot in raw_forecasts:
            dt_str: str = slot.get("datetime", "")
            if not dt_str:
                continue

            try:
                dt = datetime.fromisoformat(dt_str)
            except ValueError:
                continue

            # Solar position at the midpoint of the hour
            dt_mid = dt + timedelta(minutes=30)
            elevation, azimuth = solar_elevation_azimuth(lat, lon, dt_mid)

            ghi_clear = clear_sky_ghi(elevation)

            # Determine weather attenuation from cloud coverage or condition
            cloud_coverage: float | None = slot.get("cloud_coverage")
            if cloud_coverage is not None:
                # Cloud coverage 0–100 → attenuation 1.0…0.10
                factor = 1.0 - (cloud_coverage / 100.0) * 0.90
            else:
                condition: str = slot.get("condition", "")
                factor = WEATHER_ATTENUATION.get(condition, DEFAULT_ATTENUATION)

            ghi_attenuated = ghi_clear * factor

            power_w = total_system_power_w(
                panels=panels,
                elevation_deg=elevation,
                azimuth_deg=azimuth,
                weather_ghi=ghi_attenuated,
                efficiency=SYSTEM_EFFICIENCY,
            )

            # energy_wh = power_w * 1 h (hourly slots)
            points.append(
                ForecastPoint(
                    datetime=dt_str,
                    power_w=round(power_w, 1),
                    energy_wh=round(power_w * 1.0, 1),
                )
            )

        return points

    @staticmethod
    def _interpolate_current(points: list[ForecastPoint]) -> float:
        """Return power for the most recent slot that has started."""
        now = datetime.now(tz=UTC)
        best: ForecastPoint | None = None
        for pt in points:
            try:
                dt = datetime.fromisoformat(pt.datetime)
            except ValueError:
                continue
            if dt <= now:
                best = pt
        if best is not None:
            return best.power_w
        # If all slots are in the future, use the first one
        return points[0].power_w if points else 0.0
