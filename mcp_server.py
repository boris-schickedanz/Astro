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
from typing import Annotated, Optional

from fastmcp import FastMCP
from kerykeion import AstrologicalSubject
from pydantic import Field

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


# ---- Shared parameter annotations -------------------------------------------
# Defined once so the three tools present an identical, self-documenting schema.

NameParam = Annotated[str, Field(
    description="Label for the chart (used in printed headers only — not used "
                "for any lookup or astrological calculation).",
)]
YearParam = Annotated[int, Field(
    description="Gregorian birth year, e.g. 1990. Birth date is interpreted in "
                "the LOCAL CIVIL TIME of the birth city, not UTC.",
)]
MonthParam = Annotated[int, Field(ge=1, le=12, description="Gregorian birth month, 1–12.")]
DayParam = Annotated[int, Field(ge=1, le=31, description="Gregorian birth day of month, 1–31.")]

HourParam = Annotated[Optional[int], Field(
    ge=0, le=23,
    description="Birth hour in local civil time, 24h (0–23). "
                "If hour OR minute is omitted the chart is treated as TIMELESS: "
                "ASC, MC, house cusps, planet-in-house placements, hemispheres, "
                "chart ruler, annual profection, and house-based stelliums are "
                "all suppressed from output. Sign placements, sign-based "
                "stelliums, transit aspects, and long-term outer transits "
                "still work without a time. Pass both hour and minute to get "
                "the full reading.",
)]
MinuteParam = Annotated[Optional[int], Field(
    ge=0, le=59,
    description="Birth minute in local civil time, 0–59. See `hour` for the "
                "consequences of omitting it.",
)]

CityParam = Annotated[str, Field(
    description="Birth city name. Resolved against the geonames database "
                "(network call; requires GEONAMES_USERNAME in the server's "
                ".env) to obtain latitude, longitude, and IANA timezone. "
                "If the city is ambiguous, misspelled, or geonames is "
                "unavailable, pass `lat`, `lng`, and `tz` directly instead.",
)]
NationParam = Annotated[str, Field(
    description="ISO 3166-1 alpha-2 country code of the birth city, e.g. "
                "'US', 'GB', 'DE', 'CH'. Disambiguates same-named cities.",
)]
LatParam = Annotated[Optional[float], Field(
    ge=-90, le=90,
    description="Optional birth latitude in decimal degrees (positive = north). "
                "Pass together with `lng` and `tz` to bypass the geonames "
                "lookup — useful for offline use, ambiguous city names, or "
                "when you already have precise coordinates.",
)]
LngParam = Annotated[Optional[float], Field(
    ge=-180, le=180,
    description="Optional birth longitude in decimal degrees (positive = east). "
                "Must be passed together with `lat` and `tz` to take effect.",
)]
TzParam = Annotated[Optional[str], Field(
    description="Optional IANA timezone name for the birth location, e.g. "
                "'Europe/Berlin', 'America/New_York'. Required when supplying "
                "`lat`/`lng` overrides. NOT a UTC offset — must be an IANA "
                "zone so historical DST is handled correctly.",
)]

CurrentCityParam = Annotated[Optional[str], Field(
    description="City the user is living in NOW (where 'today' should be "
                "anchored). Defaults to the birth city. Affects only two "
                "things: (a) which timezone is used to resolve 'now' for "
                "transits/profection/solar-return year, and (b) the ASC/MC "
                "and house cusps of the solar-return chart. Transit-aspect "
                "math itself is location-independent.",
)]
CurrentNationParam = Annotated[Optional[str], Field(
    description="ISO 3166-1 alpha-2 country code matching `current_city`. "
                "Defaults to the birth nation.",
)]


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
        transit_datetime, years_before=2, years_after=10,
    )
    display_long_term_transits(transit_datetime, long_term)

    sr = calculate_solar_return(chart, transit_datetime.year, current_city, current_nation)
    display_solar_return(sr)


@mcp.tool()
def calculate_natal_chart(
    name: NameParam,
    year: YearParam, month: MonthParam, day: DayParam,
    hour: HourParam = None, minute: MinuteParam = None,
    city: CityParam = "London", nation: NationParam = "GB",
    lat: LatParam = None, lng: LngParam = None,
    tz: TzParam = None,
) -> str:
    """
    Compute the BIRTH CHART only — no current transits, no future timing.

    Use this when the user asks about who they are astrologically: birth
    placements, natal aspects, sign/element/modality balance, chart ruler,
    stelliums, or their current annual profection. Prefer this over
    `calculate_full_reading` when the user does NOT need predictions for
    the current period — it's faster (no transit ephemeris scan) and produces
    a shorter, more focused report.

    Returns (as a single human-readable text block, NOT JSON):
      - Planets in signs and houses, additional points (Node, Lilith, Chiron,
        Lot of Fortune), house cusps
      - Natal aspects (orb ≤ 4°)
      - Element / modality / hemisphere balance, chart ruler
      - Stelliums (≥ 3 planets in a sign or house)
      - Active annual profection (Hellenistic, modern rulerships)

    Behavioral note: if `hour` or `minute` is omitted, all house-, ASC-, and
    profection-dependent sections are suppressed (see the `hour` parameter).
    """
    has_time = hour is not None and minute is not None
    chart = _create_subject(name, year, month, day, hour, minute,
                            city, nation, lat, lng, tz)
    with _capture() as out:
        _print_natal_block(chart, has_time)
    return out.getvalue()


@mcp.tool()
def calculate_transits(
    name: NameParam,
    year: YearParam, month: MonthParam, day: DayParam,
    hour: HourParam = None, minute: MinuteParam = None,
    city: CityParam = "London", nation: NationParam = "GB",
    lat: LatParam = None, lng: LngParam = None,
    tz: TzParam = None,
    current_city: CurrentCityParam = None,
    current_nation: CurrentNationParam = None,
) -> str:
    """
    Compute CURRENT AND UPCOMING TIMING only — assumes the natal chart is
    either already known to the caller or not needed for this question.

    Use this when the user asks "what's happening for me now / soon",
    "what transits am I under", "when does Saturn finish in my 7th house",
    or "what's my solar return this year". Prefer this over
    `calculate_full_reading` when the user does NOT need the natal recap —
    the report is shorter and easier to reason about.

    Returns (as a single human-readable text block, NOT JSON):
      - Current transit aspects to natal points (top significant ones, orb ≤ 3°)
      - Each transit planet's current natal house with entry/exit dates
      - Long-term outer-planet transits (Jupiter–Pluto): active now, recently
        completed (last 2 years), and upcoming (next 10 years)
      - Solar return for the current year, cast at `current_city`

    Location semantics: transit-aspect math is location-independent. Pass
    `current_city` / `current_nation` only if the user has moved since birth
    (affects the solar-return ASC/houses and the timezone used to resolve
    'now'). Defaults to the birth city/nation.
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
    name: NameParam,
    year: YearParam, month: MonthParam, day: DayParam,
    hour: HourParam = None, minute: MinuteParam = None,
    city: CityParam = "London", nation: NationParam = "GB",
    lat: LatParam = None, lng: LngParam = None,
    tz: TzParam = None,
    current_city: CurrentCityParam = None,
    current_nation: CurrentNationParam = None,
) -> str:
    """
    Compute the COMPLETE READING — natal chart plus current/upcoming timing.

    Use this for first-time readings or when the user explicitly wants the
    whole picture in one go. If the user only needs one of the two halves,
    prefer the narrower tool: `calculate_natal_chart` (birth chart only)
    or `calculate_transits` (timing only). Those produce shorter output and
    skip the work the user didn't ask for.

    Returns the union of `calculate_natal_chart` and `calculate_transits`,
    as a single human-readable text block (NOT JSON). Mirrors the CLI output.
    Location and timeless-chart semantics are the same as the narrower tools.
    """
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
