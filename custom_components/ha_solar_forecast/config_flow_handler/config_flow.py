"""Config flow for ha_solar_forecast."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from custom_components.ha_solar_forecast.config_flow_handler.schemas.config import get_location_schema, get_panel_schema
from custom_components.ha_solar_forecast.const import (
    CONF_ELEVATION,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_PANEL_AZIMUTH,
    CONF_PANEL_INCLINATION,
    CONF_PANEL_NAME,
    CONF_PANEL_PEAK_POWER,
    CONF_PANELS,
    CONF_WEATHER_ENTITY,
    DOMAIN,
)
from homeassistant import config_entries
from homeassistant.core import callback

if TYPE_CHECKING:
    from .options_flow import SolarForecastOptionsFlow


class SolarForecastConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Solar Forecast."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialise the flow state."""
        self._location_data: dict[str, Any] = {}
        self._panels: list[dict[str, Any]] = []

    @staticmethod
    @callback
    def async_get_options_flow(
        _config_entry: config_entries.ConfigEntry,
    ) -> SolarForecastOptionsFlow:
        """Return the options flow handler."""
        from .options_flow import SolarForecastOptionsFlow  # noqa: PLC0415

        return SolarForecastOptionsFlow()

    # ------------------------------------------------------------------
    # Step 1: location + weather entity
    # ------------------------------------------------------------------

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step: location and weather entity."""
        errors: dict[str, str] = {}

        if user_input is not None:
            weather_entity = user_input[CONF_WEATHER_ENTITY]

            if not self.hass.states.get(weather_entity):
                errors[CONF_WEATHER_ENTITY] = "weather_entity_not_found"
            else:
                self._location_data = {
                    CONF_LATITUDE: user_input[CONF_LATITUDE],
                    CONF_LONGITUDE: user_input[CONF_LONGITUDE],
                    CONF_ELEVATION: user_input.get(CONF_ELEVATION, 0),
                    CONF_WEATHER_ENTITY: weather_entity,
                }
                return await self.async_step_panel()

        default_lat: float = self.hass.config.latitude
        default_lon: float = self.hass.config.longitude
        default_elev: float = self.hass.config.elevation or 0

        return self.async_show_form(
            step_id="user",
            data_schema=get_location_schema(default_lat, default_lon, default_elev),
            errors=errors,
        )

    # ------------------------------------------------------------------
    # Step 2: first / additional panel array
    # ------------------------------------------------------------------

    async def async_step_panel(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Collect one panel array configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            name = str(user_input[CONF_PANEL_NAME]).strip()
            if not name:
                errors[CONF_PANEL_NAME] = "panel_name_empty"
            elif any(p[CONF_PANEL_NAME] == name for p in self._panels):
                errors[CONF_PANEL_NAME] = "panel_name_duplicate"
            else:
                self._panels.append(
                    {
                        CONF_PANEL_NAME: name,
                        CONF_PANEL_PEAK_POWER: int(user_input[CONF_PANEL_PEAK_POWER]),
                        CONF_PANEL_INCLINATION: int(user_input[CONF_PANEL_INCLINATION]),
                        CONF_PANEL_AZIMUTH: int(user_input[CONF_PANEL_AZIMUTH]),
                    }
                )
                return await self.async_step_add_another()

        return self.async_show_form(
            step_id="panel",
            data_schema=get_panel_schema(),
            errors=errors,
            description_placeholders={"panel_index": str(len(self._panels) + 1)},
        )

    # ------------------------------------------------------------------
    # Step 3: menu — add another panel or finish
    # ------------------------------------------------------------------

    async def async_step_add_another(
        self,
        _user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Ask the user whether to add another panel array."""
        return self.async_show_menu(
            step_id="add_another",
            menu_options=["panel", "finish"],
        )

    async def async_step_finish(
        self,
        _user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Create the config entry."""
        title = self.hass.config.location_name or "Solar Forecast"
        return self.async_create_entry(
            title=title,
            data={
                **self._location_data,
                CONF_PANELS: self._panels,
            },
        )


__all__ = ["SolarForecastConfigFlowHandler"]
