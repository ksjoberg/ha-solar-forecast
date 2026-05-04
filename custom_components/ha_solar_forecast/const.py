"""Constants for ha_solar_forecast."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "ha_solar_forecast"

PARALLEL_UPDATES = 1

# Config entry data keys
CONF_WEATHER_ENTITY = "weather_entity"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_ELEVATION = "elevation"
CONF_PANELS = "panels"

# Panel config keys
CONF_PANEL_NAME = "name"
CONF_PANEL_PEAK_POWER = "peak_power"
CONF_PANEL_INCLINATION = "inclination"
CONF_PANEL_AZIMUTH = "azimuth"

# Weather condition → clear-sky attenuation factor (0–1)
WEATHER_ATTENUATION: dict[str, float] = {
    "sunny": 1.0,
    "clear-night": 0.0,
    "partlycloudy": 0.55,
    "cloudy": 0.20,
    "overcast": 0.15,
    "fog": 0.10,
    "rainy": 0.15,
    "pouring": 0.05,
    "snowy": 0.10,
    "snowy-rainy": 0.08,
    "lightning": 0.20,
    "lightning-rainy": 0.12,
    "hail": 0.10,
    "windy": 0.95,
    "windy-variant": 0.80,
    "exceptional": 0.50,
}

DEFAULT_ATTENUATION = 0.50

# Performance de-rating factor (cable/inverter/temperature losses)
SYSTEM_EFFICIENCY = 0.85

UPDATE_INTERVAL_MINUTES = 30
