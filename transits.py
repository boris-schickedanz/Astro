"""
Transits orchestrator.

Composes the four specialized calculators (aspects, house residency,
long-term cycles, data formatting) and resolves "now" in the location's
local timezone for the convenience helper.
"""

from datetime import datetime
from typing import Any, Dict

import pytz
from kerykeion import AstrologicalSubject

import config
from house_transits import HouseTransitCalculator
from long_term_transits import LongTermTransitCalculator
from transit_aspects import TransitAspectCalculator
from transit_data import TransitDataFormatter


DEFAULT_LOCATION = "Greenwich, GB"


def _split_location(location: str) -> tuple[str, str]:
    """Split a "City, NN" string into (city, nation), defaulting nation to GB."""
    parts = [p.strip() for p in location.split(",", 1)]
    if len(parts) == 2 and parts[1]:
        return parts[0], parts[1]
    return parts[0], "GB"


class TransitsCalculator:
    """Top-level transit calculator. Stateless aside from the bound natal chart."""

    def __init__(self, natal_chart: AstrologicalSubject):
        self.natal_chart = natal_chart
        self.aspect_calculator = TransitAspectCalculator(natal_chart)
        self.house_calculator = HouseTransitCalculator(natal_chart)
        self.long_term_calculator = LongTermTransitCalculator(natal_chart)
        self.data_formatter = TransitDataFormatter(natal_chart)

    def calculate_transit_for_date(self, transit_date: datetime,
                                   location: str = DEFAULT_LOCATION) -> Dict[str, Any]:
        """Compute transit aspects + planet positions for a specific moment."""
        city, nation = _split_location(location)
        transit_chart = AstrologicalSubject(
            "Transit",
            transit_date.year, transit_date.month, transit_date.day,
            transit_date.hour, transit_date.minute,
            city, nation,
            geonames_username=config.GEONAMES_USERNAME,
        )

        transit_aspects = self.aspect_calculator.calculate_transit_aspects(transit_chart)
        return {
            "transit_date": transit_date.isoformat(),
            "natal_name": self.natal_chart.name,
            "transit_planets": self.data_formatter.get_planet_positions(transit_chart, self.natal_chart),
            "natal_planets": self.data_formatter.get_planet_positions(self.natal_chart),
            "aspects": transit_aspects,
            "significant_transits": self.aspect_calculator.identify_significant_transits(transit_aspects),
        }

    def calculate_planet_house_dates(self, base_date: datetime,
                                     location: str = DEFAULT_LOCATION) -> Dict[str, Dict[str, Any]]:
        """Entry/exit dates for each transit planet through its current natal house."""
        return self.house_calculator.calculate_planet_house_dates(base_date, location)

    def calculate_long_term_transits(self, base_date: datetime,
                                     years_before: int = 2,
                                     years_after: int = 2) -> Dict[str, Any]:
        """Outer-planet aspects to natal across a multi-year window."""
        return self.long_term_calculator.calculate_long_term_transits(
            base_date, years_before, years_after
        )


def now_at_location(location: str = DEFAULT_LOCATION) -> datetime:
    """`datetime.now()` in the given location's local timezone (tz-aware)."""
    try:
        city, nation = _split_location(location)
        temp_chart = AstrologicalSubject(
            "Temp", 2025, 1, 1, 12, 0, city, nation,
            geonames_username=config.GEONAMES_USERNAME,
        )
        return datetime.now(pytz.UTC).astimezone(pytz.timezone(temp_chart.tz_str))
    except Exception:
        return datetime.now()


def calculate_current_transits(natal_chart: AstrologicalSubject,
                               location: str = DEFAULT_LOCATION) -> Dict[str, Any]:
    """Convenience: transits for "now" in the given location's local timezone."""
    return TransitsCalculator(natal_chart).calculate_transit_for_date(
        now_at_location(location), location
    )
