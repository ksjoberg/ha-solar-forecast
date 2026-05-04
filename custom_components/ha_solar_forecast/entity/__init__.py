"""
Entity package for ha_solar_forecast.

Architecture:
    All platform entities inherit from (PlatformEntity, SolarForecastEntity).
    MRO order matters — platform-specific class first, then the integration base.
    Entities read data from coordinator.data and NEVER call the API client directly.
    Unique IDs follow the pattern: {entry_id}_{description.key}

See entity/base.py for the SolarForecastEntity base class.
"""

from .base import SolarForecastEntity

__all__ = ["SolarForecastEntity"]
