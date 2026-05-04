"""Pure-Python solar geometry and irradiance calculations."""

from __future__ import annotations

from datetime import UTC, datetime
import math

# Solar constant at top of atmosphere (W/m²)
_SOLAR_CONSTANT = 1361.0


def _fractional_year(dt: datetime) -> float:
    """Fractional year in radians (NOAA formula)."""
    dt_utc = dt.astimezone(UTC)
    doy = dt_utc.timetuple().tm_yday
    return 2 * math.pi / 365 * (doy - 1 + (dt_utc.hour - 12) / 24)


def _equation_of_time(gamma: float) -> float:
    """Equation of time in minutes (NOAA)."""
    return 229.18 * (
        0.000075
        + 0.001868 * math.cos(gamma)
        - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2 * gamma)
        - 0.04089 * math.sin(2 * gamma)
    )


def _solar_declination(gamma: float) -> float:
    """Solar declination in radians (Spencer 1971)."""
    return (
        0.006918
        - 0.399912 * math.cos(gamma)
        + 0.070257 * math.sin(gamma)
        - 0.006758 * math.cos(2 * gamma)
        + 0.000907 * math.sin(2 * gamma)
        - 0.002697 * math.cos(3 * gamma)
        + 0.00148 * math.sin(3 * gamma)
    )


def solar_elevation_azimuth(lat_deg: float, lon_deg: float, dt: datetime) -> tuple[float, float]:
    """
    Return (elevation_deg, azimuth_deg) for the given location and moment.

    azimuth is 0° = North, 90° = East, 180° = South, 270° = West.
    elevation is negative when the sun is below the horizon.
    """
    dt_utc = dt.astimezone(UTC)
    gamma = _fractional_year(dt_utc)

    eqtime = _equation_of_time(gamma)
    decl = _solar_declination(gamma)

    # True solar time (minutes past midnight UTC adjusted for longitude and EoT)
    tst = dt_utc.hour * 60 + dt_utc.minute + dt_utc.second / 60 + eqtime + 4 * lon_deg

    # Solar hour angle in degrees (noon = 0°)
    ha_deg = tst / 4 - 180
    ha_rad = math.radians(ha_deg)

    lat_rad = math.radians(lat_deg)

    cos_zenith = math.sin(lat_rad) * math.sin(decl) + math.cos(lat_rad) * math.cos(decl) * math.cos(ha_rad)
    cos_zenith = max(-1.0, min(1.0, cos_zenith))
    zenith_rad = math.acos(cos_zenith)
    elevation_deg = 90.0 - math.degrees(zenith_rad)

    # Azimuth (0=N, 90=E, 180=S, 270=W)
    sin_zenith = math.sin(zenith_rad)
    if sin_zenith < 1e-6 or elevation_deg <= 0:
        return elevation_deg, 0.0

    cos_az = (math.sin(decl) - math.sin(lat_rad) * cos_zenith) / (math.cos(lat_rad) * sin_zenith)
    cos_az = max(-1.0, min(1.0, cos_az))
    az_deg = math.degrees(math.acos(cos_az))
    if ha_deg > 0:  # afternoon: sun west of south
        az_deg = 360.0 - az_deg

    return elevation_deg, az_deg


def clear_sky_ghi(elevation_deg: float) -> float:
    """
    Simplified clear-sky Global Horizontal Irradiance (W/m²).

    Uses the Kasten-Young air-mass formula with a typical rural atmosphere.
    Returns 0 when the sun is at or below the horizon.
    """
    if elevation_deg <= 0.0:
        return 0.0

    elev_rad = math.radians(elevation_deg)
    # Kasten-Young air mass
    am = 1.0 / (math.sin(elev_rad) + 0.50572 * (elevation_deg + 6.07995) ** -1.6364)
    ghi = _SOLAR_CONSTANT * math.sin(elev_rad) * (0.7 ** (am**0.678))
    return max(0.0, ghi)


def panel_irradiance(
    elevation_deg: float,
    azimuth_deg: float,
    panel_tilt_deg: float,
    panel_azimuth_deg: float,
    ghi: float,
) -> float:
    """
    Plane-of-array irradiance on a tilted panel (W/m²).

    Uses a simple isotropic sky diffuse model.

    panel_tilt_deg  : 0 = horizontal, 90 = vertical
    panel_azimuth_deg: 0 = North, 90 = East, 180 = South, 270 = West
    """
    if elevation_deg <= 0.0 or ghi <= 0.0:
        return 0.0

    elev_rad = math.radians(elevation_deg)
    panel_tilt_rad = math.radians(panel_tilt_deg)

    # Angle of incidence between sun rays and panel normal
    cos_aoi = math.sin(elev_rad) * math.cos(panel_tilt_rad) + math.cos(elev_rad) * math.sin(panel_tilt_rad) * math.cos(
        math.radians(azimuth_deg - panel_azimuth_deg)
    )
    cos_aoi = max(0.0, cos_aoi)

    # Simple GHI decomposition: ~85% beam on horizontal, ~15% diffuse
    sin_elev = math.sin(elev_rad)
    dni = (ghi * 0.85 / sin_elev) if elevation_deg > 2 else 0.0
    dhi = ghi * 0.15

    # Isotropic sky model for tilted surface
    poa = dni * cos_aoi + dhi * (1 + math.cos(panel_tilt_rad)) / 2
    return max(0.0, poa)


def total_system_power_w(
    panels: list[dict],
    elevation_deg: float,
    azimuth_deg: float,
    weather_ghi: float,
    efficiency: float,
) -> float:
    """
    Aggregate DC power from all panel arrays (W), derated by system efficiency.

    panels entries must have keys: peak_power (Wp), inclination (°), azimuth (°).
    weather_ghi is already attenuated for cloud/weather conditions.
    """
    total = 0.0
    for panel in panels:
        poa = panel_irradiance(
            elevation_deg,
            azimuth_deg,
            panel["inclination"],
            panel["azimuth"],
            weather_ghi,
        )
        # STC irradiance = 1000 W/m², so power = peak_power * (poa/1000)
        total += panel["peak_power"] * (poa / 1000.0)

    return total * efficiency
