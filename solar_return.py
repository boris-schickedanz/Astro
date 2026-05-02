"""
Solar return calculations.

Finds the moment in a given target year when the transiting Sun returns to
its exact natal ecliptic longitude, then casts a chart for that moment at
the location where the native is residing for the year.

Search uses pyswisseph directly (fast, no geonames lookup) to locate the
return moment to minute precision; one AstrologicalSubject is then created
at the final timestamp for full chart data.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import pytz
import swisseph as swe
from kerykeion import AstrologicalSubject

import config
from chart_analysis import chart_ruler
from models import HOUSE_INDEX


def _sun_longitude(jd: float) -> float:
    """Geocentric ecliptic longitude of the Sun at Julian Day jd (UT)."""
    pos, _ = swe.calc_ut(jd, swe.SUN)
    return pos[0] % 360.0


def _angular_diff(a: float, b: float) -> float:
    """Signed shortest angular difference (a - b) wrapped into [-180, 180]."""
    d = (a - b + 540.0) % 360.0 - 180.0
    return d


def _find_return_jd(natal_sun_lon: float, target_year: int,
                    birth_month: int, birth_day: int) -> float:
    """
    Locate the Julian Day in target_year when the Sun crosses natal longitude.

    Returns a JD accurate to ~one minute. Searches a ±5-day window around
    the natal birthday in the target year, then bisects the sign-change.
    """
    base_dt = datetime(target_year, birth_month, birth_day, 0, 0, 0)

    start_jd = swe.julday(base_dt.year, base_dt.month, base_dt.day, 0.0) - 5.0
    end_jd = start_jd + 10.0

    step = 1.0 / 24.0  # 1-hour resolution scan
    prev_jd = start_jd
    prev_diff = _angular_diff(_sun_longitude(prev_jd), natal_sun_lon)

    bracket: Optional[tuple] = None
    jd = prev_jd + step
    while jd <= end_jd:
        diff = _angular_diff(_sun_longitude(jd), natal_sun_lon)
        # Sign change without wrap = the Sun crossed natal longitude in this hour.
        if prev_diff <= 0 < diff or prev_diff < 0 <= diff:
            if abs(diff - prev_diff) < 180:
                bracket = (prev_jd, jd, prev_diff, diff)
                break
        prev_jd, prev_diff = jd, diff
        jd += step

    if bracket is None:
        # Fallback: take the closest sample.
        return prev_jd

    lo, hi, lo_diff, hi_diff = bracket
    # Bisection to ~1 second precision (more than enough; we round to minute).
    for _ in range(40):
        mid = (lo + hi) / 2.0
        mid_diff = _angular_diff(_sun_longitude(mid), natal_sun_lon)
        if (lo_diff <= 0 < mid_diff) or (lo_diff < 0 <= mid_diff):
            hi, hi_diff = mid, mid_diff
        else:
            lo, lo_diff = mid, mid_diff
        if (hi - lo) < (1.0 / 86400.0):
            break
    return (lo + hi) / 2.0


def _jd_to_datetime(jd: float) -> datetime:
    """Convert a UT Julian Day back to a Python datetime (UTC, naive, minute-precision)."""
    year, month, day, hour_frac = swe.revjul(jd)
    # Build via timedelta so any rounding carry into hour/day rolls over correctly.
    return datetime(year, month, day) + timedelta(seconds=round(hour_frac * 3600))


def calculate_solar_return(natal_chart: AstrologicalSubject, target_year: int,
                          city: str, nation: str) -> Dict[str, Any]:
    """
    Compute the solar return chart for target_year at the given location.

    When the SR location matches the natal chart's city/nation, we reuse
    natal_chart's resolved lat/lng/tz_str instead of building a throwaway
    "locator" chart — saves one geonames-resolving AstrologicalSubject.
    """
    sr_jd = _find_return_jd(natal_chart.sun.abs_pos, target_year,
                            natal_chart.month, natal_chart.day)
    sr_utc = _jd_to_datetime(sr_jd)

    if city == natal_chart.city and nation == natal_chart.nation:
        lat, lng, tz_str = natal_chart.lat, natal_chart.lng, natal_chart.tz_str
    else:
        locator = AstrologicalSubject(
            "SR_locator", 2025, 1, 1, 12, 0, city, nation,
            geonames_username=config.GEONAMES_USERNAME,
        )
        lat, lng, tz_str = locator.lat, locator.lng, locator.tz_str

    sr_local = pytz.UTC.localize(sr_utc).astimezone(pytz.timezone(tz_str))

    sr_chart = AstrologicalSubject(
        f"SR{target_year}_{natal_chart.name}",
        sr_local.year, sr_local.month, sr_local.day, sr_local.hour, sr_local.minute,
        city, nation,
        lat=lat, lng=lng, tz_str=tz_str,
        geonames_username=config.GEONAMES_USERNAME,
    )

    sr_sun_house = HOUSE_INDEX.get(sr_chart.sun.house, 0)
    sr_moon_house = HOUSE_INDEX.get(sr_chart.moon.house, 0)

    return {
        "year": target_year,
        "sr_utc": sr_utc.strftime("%Y-%m-%d %H:%M UTC"),
        "city": city,
        "nation": nation,
        "asc_sign": sr_chart.ascendant.sign,
        "asc_degree": round(sr_chart.ascendant.position, 2),
        "mc_sign": sr_chart.medium_coeli.sign,
        "mc_degree": round(sr_chart.medium_coeli.position, 2),
        "sun_sign": sr_chart.sun.sign,
        "sun_degree": round(sr_chart.sun.position, 2),
        "sun_house": sr_sun_house,
        "moon_sign": sr_chart.moon.sign,
        "moon_degree": round(sr_chart.moon.position, 2),
        "moon_house": sr_moon_house,
        "chart_ruler": chart_ruler(sr_chart),
    }
