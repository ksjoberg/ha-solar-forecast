"""Schemas for the options flow."""

from __future__ import annotations

import voluptuous as vol

from custom_components.ha_solar_forecast.const import (
    CONF_PANEL_AZIMUTH,
    CONF_PANEL_INCLINATION,
    CONF_PANEL_NAME,
    CONF_PANEL_PEAK_POWER,
    CONF_WEATHER_ENTITY,
)
from homeassistant.helpers import selector


def get_weather_entity_schema(current: str) -> vol.Schema:
    """Schema for changing the weather entity."""
    return vol.Schema(
        {
            vol.Required(CONF_WEATHER_ENTITY, default=current): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="weather")
            )
        }
    )


def get_panel_schema(defaults: dict | None = None) -> vol.Schema:
    """Schema for adding a new panel array in the options flow."""
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


def get_remove_panel_schema(panel_names: list[str]) -> vol.Schema:
    """Schema for selecting which panel array to remove."""
    return vol.Schema(
        {
            vol.Required(CONF_PANEL_NAME): selector.SelectSelector(
                selector.SelectSelectorConfig(options=panel_names, mode=selector.SelectSelectorMode.LIST)
            )
        }
    )


__all__ = [
    "get_panel_schema",
    "get_remove_panel_schema",
    "get_weather_entity_schema",
]
