"""Schemas for the main config flow steps."""

from __future__ import annotations

import voluptuous as vol

from custom_components.ha_solar_forecast.const import (
    CONF_ELEVATION,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_PANEL_AZIMUTH,
    CONF_PANEL_INCLINATION,
    CONF_PANEL_NAME,
    CONF_PANEL_PEAK_POWER,
    CONF_WEATHER_ENTITY,
)
from homeassistant.helpers import selector


def get_location_schema(
    latitude: float,
    longitude: float,
    elevation: float,
) -> vol.Schema:
    """Schema for the first step: location + weather entity."""
    return vol.Schema(
        {
            vol.Required(CONF_LATITUDE, default=latitude): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=-90,
                    max=90,
                    step=0.000001,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="°",
                )
            ),
            vol.Required(CONF_LONGITUDE, default=longitude): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=-180,
                    max=180,
                    step=0.000001,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="°",
                )
            ),
            vol.Optional(CONF_ELEVATION, default=elevation): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=-500,
                    max=9000,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="m",
                )
            ),
            vol.Required(CONF_WEATHER_ENTITY): selector.EntitySelector(selector.EntitySelectorConfig(domain="weather")),
        }
    )


def get_panel_schema(defaults: dict | None = None) -> vol.Schema:
    """Schema for a solar panel array configuration step."""
    d = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_PANEL_NAME, default=d.get(CONF_PANEL_NAME, "")): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
            ),
            vol.Required(CONF_PANEL_PEAK_POWER, default=d.get(CONF_PANEL_PEAK_POWER, 3000)): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=100000,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="Wp",
                )
            ),
            vol.Required(CONF_PANEL_INCLINATION, default=d.get(CONF_PANEL_INCLINATION, 35)): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=90,
                    step=1,
                    mode=selector.NumberSelectorMode.SLIDER,
                    unit_of_measurement="°",
                )
            ),
            vol.Required(CONF_PANEL_AZIMUTH, default=d.get(CONF_PANEL_AZIMUTH, 180)): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=360,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="°",
                )
            ),
        }
    )


__all__ = [
    "get_location_schema",
    "get_panel_schema",
]
