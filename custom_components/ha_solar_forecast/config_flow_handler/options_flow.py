"""Options flow for ha_solar_forecast: manage weather entity and panel arrays."""

from __future__ import annotations

from typing import Any

from custom_components.ha_solar_forecast.config_flow_handler.schemas.options import (
    get_panel_schema,
    get_remove_panel_schema,
    get_weather_entity_schema,
)
from custom_components.ha_solar_forecast.const import (
    CONF_PANEL_AZIMUTH,
    CONF_PANEL_INCLINATION,
    CONF_PANEL_NAME,
    CONF_PANEL_PEAK_POWER,
    CONF_PANELS,
    CONF_WEATHER_ENTITY,
)
from homeassistant import config_entries


class SolarForecastOptionsFlow(config_entries.OptionsFlow):
    """Options flow: add / remove panel arrays and change the weather entity."""

    def __init__(self) -> None:
        """Keep a mutable copy of the panels list."""
        self._panels: list[dict[str, Any]] = []

    async def async_step_init(
        self,
        _user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Show the main menu."""
        self._panels = list(self.config_entry.data.get(CONF_PANELS, []))
        return self.async_show_menu(
            step_id="init",
            menu_options=["add_panel", "remove_panel", "weather_entity"],
        )

    # ------------------------------------------------------------------
    # Add panel
    # ------------------------------------------------------------------

    async def async_step_add_panel(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Add a new panel array."""
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
                return self._save()

        return self.async_show_form(
            step_id="add_panel",
            data_schema=get_panel_schema(),
            errors=errors,
        )

    # ------------------------------------------------------------------
    # Remove panel
    # ------------------------------------------------------------------

    async def async_step_remove_panel(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Remove an existing panel array."""
        if not self._panels:
            return self.async_abort(reason="no_panels")

        if user_input is not None:
            name_to_remove = user_input[CONF_PANEL_NAME]
            self._panels = [p for p in self._panels if p[CONF_PANEL_NAME] != name_to_remove]
            return self._save()

        panel_names = [p[CONF_PANEL_NAME] for p in self._panels]
        return self.async_show_form(
            step_id="remove_panel",
            data_schema=get_remove_panel_schema(panel_names),
        )

    # ------------------------------------------------------------------
    # Change weather entity
    # ------------------------------------------------------------------

    async def async_step_weather_entity(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Update the source weather entity."""
        errors: dict[str, str] = {}
        current = self.config_entry.data.get(CONF_WEATHER_ENTITY, "")

        if user_input is not None:
            entity_id = user_input[CONF_WEATHER_ENTITY]
            if not self.hass.states.get(entity_id):
                errors[CONF_WEATHER_ENTITY] = "weather_entity_not_found"
            else:
                new_data = {**self.config_entry.data, CONF_WEATHER_ENTITY: entity_id}
                self.hass.config_entries.async_update_entry(self.config_entry, data=new_data)
                return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="weather_entity",
            data_schema=get_weather_entity_schema(current),
            errors=errors,
        )

    # ------------------------------------------------------------------

    def _save(self) -> config_entries.ConfigFlowResult:
        """Persist the updated panels list into config entry data."""
        new_data = {**self.config_entry.data, CONF_PANELS: self._panels}
        self.hass.config_entries.async_update_entry(self.config_entry, data=new_data)
        return self.async_create_entry(title="", data={})


__all__ = ["SolarForecastOptionsFlow"]
