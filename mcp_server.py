"""
MCP server for the Astro project.

Exposes three tools:
  - calculate_natal_chart: natal placements, aspects, balance, ruler, stelliums, profection
  - calculate_transits:    current transits + long-term outer transits + solar return
  - calculate_full_reading: both blocks, mirrors the CLI output
"""

import io
import os
import sys
from contextlib import contextmanager
from datetime import date, datetime
from typing import Optional

from fastmcp import FastMCP
from kerykeion import AstrologicalSubject

# Set working directory so relative paths (cache/, .env) resolve correctly when
# the server is launched from elsewhere.
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("cache", exist_ok=True)

import config
from analysis_display import (
    display_balance,
    display_chart_ruler,
    display_profection,
    display_solar_return,
    display_stelliums,
)
from chart import display_natal_chart
from chart_analysis import (
    chart_ruler,
    compute_element_balance,
    compute_hemispheres,
    compute_modality_balance,
    find_stelliums,
)
from display import display_long_term_transits, display_transits
from profection import compute_profection
from solar_return import calculate_solar_return
from transits import TransitsCalculator, now_at_location

mcp = FastMCP("Astro")


def _create_subject(name: str, year: int, month: int, day: int,
                    hour: Optional[int], minute: Optional[int],
                    city: str, nation: str,
                    lat: Optional[float], lng: Optional[float],
                    tz: Optional[str]) -> AstrologicalSubject:
    return AstrologicalSubject(
        name=name, year=year, month=month, day=day,
        hour=hour or 0, minute=minute or 0,
        city=city, nation=nation, lat=lat, lng=lng, tz_str=tz,
        geonames_username=config.GEONAMES_USERNAME,
    )


@contextmanager
def _capture():
    """Redirect stdout into a StringIO; yield the buffer, restore on exit."""
    buf = io.StringIO()
    old, sys.stdout = sys.stdout, buf
    try:
        yield buf
    finally:
        sys.stdout = old


def _print_natal_block(chart: AstrologicalSubject, has_time: bool,
                       reference_date: Optional[date] = None) -> None:
    display_natal_chart(chart, has_time)
    display_balance(
        compute_element_balance(chart),
        compute_modality_balance(chart),
        compute_hemispheres(chart) if has_time else None,
    )
    if has_time:
        display_chart_ruler(chart_ruler(chart))
    display_stelliums(find_stelliums(chart, has_time=has_time))
    if has_time:
        display_profection(compute_profection(chart, reference_date or date.today()))


def _print_predictions_block(chart: AstrologicalSubject, has_time: bool,
                             current_city: str, current_nation: str,
                             transit_datetime: datetime) -> None:
    location = f"{current_city}, {current_nation}"
    transit_calculator = TransitsCalculator(chart)
    transits = transit_calculator.calculate_transit_for_date(transit_datetime, location)
    house_dates = transit_calculator.calculate_planet_house_dates(transit_datetime, location)

    print("\n" + "=" * 50)
    print("TRANSITS CALCULATION")
    print("=" * 50)
    display_transits(chart.name, location, transit_datetime, transits, house_dates, has_time, chart)

    long_term = transit_calculator.calculate_long_term_transits(
        transit_datetime, years_before=2, years_after=10, location=location,
    )
    display_long_term_transits(transit_datetime, long_term)

    sr = calculate_solar_return(chart, transit_datetime.year, current_city, current_nation)
    display_solar_return(sr)


@mcp.tool()
def calculate_natal_chart(
    name: str, year: int, month: int, day: int,
    hour: Optional[int] = None, minute: Optional[int] = None,
    city: str = "London", nation: str = "GB",
    lat: Optional[float] = None, lng: Optional[float] = None,
    tz: Optional[str] = None,
) -> str:
    """
    Full natal block: planets, additional points, houses, natal aspects,
    element/modality/hemisphere balance, chart ruler, stelliums, and the
    active annual profection.
    """
    has_time = hour is not None and minute is not None
    chart = _create_subject(name, year, month, day, hour, minute,
                            city, nation, lat, lng, tz)
    with _capture() as out:
        _print_natal_block(chart, has_time)
    return out.getvalue()


@mcp.tool()
def calculate_transits(
    name: str, year: int, month: int, day: int,
    hour: Optional[int] = None, minute: Optional[int] = None,
    city: str = "London", nation: str = "GB",
    lat: Optional[float] = None, lng: Optional[float] = None,
    tz: Optional[str] = None,
    current_city: Optional[str] = None,
    current_nation: Optional[str] = None,
) -> str:
    """
    Predictions block: current transit aspects to natal, transit planets in
    natal houses, long-term outer-planet transits (active / past 2y / next 10y),
    and the solar return for the current year cast at current_city.

    current_city / current_nation default to the birth city/nation.
    """
    has_time = hour is not None and minute is not None
    chart = _create_subject(name, year, month, day, hour, minute,
                            city, nation, lat, lng, tz)
    cc, cn = current_city or city, current_nation or nation
    transit_datetime = now_at_location(f"{cc}, {cn}")
    with _capture() as out:
        _print_predictions_block(chart, has_time, cc, cn, transit_datetime)
    return out.getvalue()


@mcp.tool()
def calculate_full_reading(
    name: str, year: int, month: int, day: int,
    hour: Optional[int] = None, minute: Optional[int] = None,
    city: str = "London", nation: str = "GB",
    lat: Optional[float] = None, lng: Optional[float] = None,
    tz: Optional[str] = None,
    current_city: Optional[str] = None,
    current_nation: Optional[str] = None,
) -> str:
    """Natal block + predictions block in one call. Mirrors the CLI output."""
    has_time = hour is not None and minute is not None
    chart = _create_subject(name, year, month, day, hour, minute,
                            city, nation, lat, lng, tz)
    cc, cn = current_city or city, current_nation or nation
    transit_datetime = now_at_location(f"{cc}, {cn}")
    with _capture() as out:
        _print_natal_block(chart, has_time, transit_datetime.date())
        _print_predictions_block(chart, has_time, cc, cn, transit_datetime)
    return out.getvalue()


if __name__ == "__main__":
    mcp.run()
