"""
Transits calculation module for the Astro Python project.

This module provides the main TransitsCalculator class that orchestrates
transit calculations using specialized sub-modules.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from kerykeion import AstrologicalSubject, KerykeionChartSVG, SynastryAspects, TransitsTimeRangeFactory
import pytz
import config

from models import (
    TRANSIT_ACTIVE_POINTS,
    TRANSIT_ACTIVE_ASPECTS,
    OUTER_PLANET_POINTS,
    LONG_TERM_ACTIVE_ASPECTS,
    NATAL_RELEVANT_PLANETS,
)
from transit_aspects import TransitAspectCalculator
from house_transits import HouseTransitCalculator
from long_term_transits import LongTermTransitCalculator
from transit_data import TransitDataFormatter


class TransitsCalculator:
    """
    Calculator for astrological transits.

    Transits represent the current planetary positions and their relationships
    to a natal (birth) chart. This class provides methods to calculate transits
    for specific dates and time ranges.
    """

    def __init__(self, natal_chart: AstrologicalSubject):
        """
        Initialize the transits calculator with a natal chart.

        Args:
            natal_chart: The natal AstrologicalSubject to calculate transits for
        """
        self.natal_chart = natal_chart
        self.aspect_calculator = TransitAspectCalculator(natal_chart)
        self.house_calculator = HouseTransitCalculator(natal_chart)
        self.long_term_calculator = LongTermTransitCalculator(natal_chart)
        self.data_formatter = TransitDataFormatter(natal_chart)

    def calculate_transit_for_date(self, transit_date: datetime, location: str = "Greenwich, GB") -> Dict[str, Any]:
        """
        Calculate transits for a specific date and time.

        Args:
            transit_date: The date and time for which to calculate transits
            location: Location string for the transit chart (default: Greenwich)

        Returns:
            Dictionary containing transit information including planetary positions
            and aspects to the natal chart
        """
        # Create transit chart for the specified date
        transit_chart = AstrologicalSubject(
            "Transit",
            transit_date.year,
            transit_date.month,
            transit_date.day,
            transit_date.hour,
            transit_date.minute,
            location.split(",")[0].strip(),
            location.split(",")[1].strip() if "," in location else "DE",
            geonames_username=config.GEONAMES_USERNAME
        )

        # Calculate aspects between transit and natal planets
        transit_aspects = self._calculate_transit_aspects(transit_chart)

        return {
            "transit_date": transit_date.isoformat(),
            "natal_name": self.natal_chart.name,
            "transit_planets": self._get_planet_positions(transit_chart, self.natal_chart),
            "natal_planets": self._get_planet_positions(self.natal_chart),
            "aspects": transit_aspects,
            "significant_transits": self._identify_significant_transits(transit_aspects)
        }

    def calculate_transits_for_range(self, start_date: datetime, end_date: datetime,
                                   location: str = "Greenwich, GB",
                                   interval_days: int = 1) -> List[Dict[str, Any]]:
        """
        Calculate transits for a date range.

        Args:
            start_date: Start of the date range
            end_date: End of the date range
            location: Location string for transit calculations
            interval_days: Days between calculations (default: 1)

        Returns:
            List of transit calculations for each date in the range
        """
        transits = []
        current_date = start_date

        while current_date <= end_date:
            transit_data = self.calculate_transit_for_date(current_date, location)
            transits.append(transit_data)
            current_date += timedelta(days=interval_days)

        return transits

    def generate_transit_chart_svg(self, transit_date: datetime,
                                 location: str = "Greenwich, GB",
                                 output_path: Optional[str] = None) -> str:
        """
        Generate an SVG transit chart showing natal planets with transit overlays.

        Args:
            transit_date: Date and time for the transit chart
            location: Location for transit calculations
            output_path: Custom output path for the SVG file

        Returns:
            Path to the generated SVG file
        """
        transit_chart = AstrologicalSubject(
            f"Transit_{transit_date.strftime('%Y%m%d_%H%M')}",
            transit_date.year,
            transit_date.month,
            transit_date.day,
            transit_date.hour,
            transit_date.minute,
            location.split(",")[0].strip(),
            location.split(",")[1].strip() if "," in location else "DE",
            geonames_username=config.GEONAMES_USERNAME
        )

        chart_svg = KerykeionChartSVG(
            self.natal_chart,
            "Transit",
            transit_chart,
            new_output_directory=output_path
        )
        chart_svg.makeSVG()

        return f"{self.natal_chart.name} - Transit Chart.svg"

    def _get_planet_positions(self, chart: AstrologicalSubject, natal_chart: Optional[AstrologicalSubject] = None) -> Dict[str, Dict[str, Any]]:
        """Get positions of all planets in a chart."""
        return self.data_formatter.get_planet_positions(chart, natal_chart)

    def calculate_planet_house_dates(self, base_date: datetime, location: str = "Greenwich, GB") -> Dict[str, Dict[str, Any]]:
        """
        Calculate the date ranges for when planets are in their current natal houses.
        
        For each planet, determines when it entered its current natal house and when
        it will exit to the next house.
        
        Args:
            base_date: The reference date for calculations
            location: Location for transit calculations
            
        Returns:
            Dictionary with house transit information for each planet
        """
        return self.house_calculator.calculate_planet_house_dates(base_date, location)

    def _find_house_entry_date(self, planet_name: str, target_house: int, base_date: datetime, 
                              location: str, natal_houses: List[float], direction: str = 'backward', 
                              max_days: int = 365) -> Optional[datetime]:
        """
        Find when a planet entered or will enter a specific natal house.
        
        Args:
            planet_name: Name of the planet
            target_house: The natal house number
            base_date: Starting date for search
            location: Location for calculations
            natal_houses: List of natal house cusp positions
            direction: 'backward' or 'forward' from base_date
            max_days: Maximum days to search
            
        Returns:
            Date when planet entered/exited the house, or None if not found
        """
        step = -1 if direction == 'backward' else 1
        current_date = base_date
        
        # Get current house
        try:
            transit_chart = AstrologicalSubject(
                "Temp",
                current_date.year,
                current_date.month,
                current_date.day,
                12, 0,  # Noon for consistency
                location.split(",")[0].strip(),
                location.split(",")[1].strip() if "," in location else "GB",
                geonames_username=config.GEONAMES_USERNAME
            )
            planet = getattr(transit_chart, planet_name)
            current_pos = planet.abs_pos
            
            # Determine current house
            current_house = 1
            for i in range(12):
                current_house_start = natal_houses[i]
                next_house_start = natal_houses[(i + 1) % 12]
                
                if current_house_start < next_house_start:
                    if current_house_start <= current_pos < next_house_start:
                        current_house = i + 1
                        break
                else:
                    if current_house_start <= current_pos or current_pos < next_house_start:
                        current_house = i + 1
                        break
                        
        except Exception:
            return None
            
        # If we're looking for entry to target house and we're already in it,
        # search backward until we're not in it
        if direction == 'backward' and current_house == target_house:
            # Search backward until we're in a different house
            for days in range(1, max_days + 1):
                check_date = base_date + timedelta(days=-days)
                try:
                    transit_chart = AstrologicalSubject(
                        "Temp",
                        check_date.year,
                        check_date.month,
                        check_date.day,
                        12, 0,
                        location.split(",")[0].strip(),
                        location.split(",")[1].strip() if "," in location else "GB",
                        geonames_username=config.GEONAMES_USERNAME
                    )
                    planet = getattr(transit_chart, planet_name)
                    check_pos = planet.abs_pos
                    
                    # Determine house at check date
                    check_house = 1
                    for i in range(12):
                        current_house_start = natal_houses[i]
                        next_house_start = natal_houses[(i + 1) % 12]
                        
                        if current_house_start < next_house_start:
                            if current_house_start <= check_pos < next_house_start:
                                check_house = i + 1
                                break
                        else:
                            if current_house_start <= check_pos or check_pos < next_house_start:
                                check_house = i + 1
                                break
                    
                    if check_house != target_house:
                        # Found the entry date - the day before this check
                        return check_date + timedelta(days=1)
                        
                except Exception:
                    continue
                    
        # If we're looking for exit from target house and we're in it,
        # search forward until we're not in it
        elif direction == 'forward' and current_house == target_house:
            # Search forward until we're in a different house
            for days in range(1, max_days + 1):
                check_date = base_date + timedelta(days=days)
                try:
                    transit_chart = AstrologicalSubject(
                        "Temp",
                        check_date.year,
                        check_date.month,
                        check_date.day,
                        12, 0,
                        location.split(",")[0].strip(),
                        location.split(",")[1].strip() if "," in location else "GB",
                        geonames_username=config.GEONAMES_USERNAME
                    )
                    planet = getattr(transit_chart, planet_name)
                    check_pos = planet.abs_pos
                    
                    # Determine house at check date
                    check_house = 1
                    for i in range(12):
                        current_house_start = natal_houses[i]
                        next_house_start = natal_houses[(i + 1) % 12]
                        
                        if current_house_start < next_house_start:
                            if current_house_start <= check_pos < next_house_start:
                                check_house = i + 1
                                break
                        else:
                            if current_house_start <= check_pos or check_pos < next_house_start:
                                check_house = i + 1
                                break
                    
                    if check_house != target_house:
                        # Found the exit date - the day before this check
                        return check_date + timedelta(days=-1)
                        
                except Exception:
                    continue
        
    def _calculate_transit_aspects(self, transit_chart: AstrologicalSubject) -> List[Dict[str, Any]]:
        """
        Calculate aspects between transit and natal planets manually.
        
        This implements traditional transit calculation by comparing each transit planet
        with each natal planet to find aspects within acceptable orbs.
        """
        return self.aspect_calculator.calculate_transit_aspects(transit_chart)

    def _identify_significant_transits(self, aspects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify the most significant transits from the aspect list."""
        return self.aspect_calculator.identify_significant_transits(aspects)

    def calculate_long_term_transits(self, base_date: datetime, 
                                   years_before: int = 2, years_after: int = 2,
                                   location: str = "Greenwich, GB") -> Dict[str, Any]:
        """
        Calculate significant long-term transits from outer planets.
        
        This method identifies when slow-moving outer planets (Saturn, Uranus, Neptune, Pluto)
        form major aspects with natal planets. It tracks complete transit cycles including
        retrograde patterns.

        Args:
            base_date: The base date for the transit calculation (typically today)
            years_before: Number of years before base_date to check (default: 2)
            years_after: Number of years after base_date to check (default: 2)
            location: Location for transit calculations

        Returns:
            List of significant long-term transits with date ranges, organized by status
        """
        return self.long_term_calculator.calculate_long_term_transits(base_date, years_before, years_after, location)


def calculate_current_transits(natal_chart: AstrologicalSubject,
                              location: str = "Greenwich, GB") -> Dict[str, Any]:
    """
    Calculate transits for the current moment at the specified location.

    Args:
        natal_chart: The natal chart to calculate transits for
        location: Current location for transit calculations (affects local time)

    Returns:
        Current transit information
    """
    # Get current time in the specified location's timezone
    try:
        # Create a temporary chart to get timezone info for the location
        temp_chart = AstrologicalSubject(
            "Temp",
            2025, 1, 1, 12, 0,  # dummy date/time
            location.split(",")[0].strip(),
            location.split(",")[1].strip() if "," in location else "GB",
            geonames_username=config.GEONAMES_USERNAME
        )
        location_tz = pytz.timezone(temp_chart.tz_str)
        current_time = datetime.now(pytz.UTC).astimezone(location_tz)
    except Exception:
        # Fallback to system local time if timezone lookup fails
        current_time = datetime.now()

    calculator = TransitsCalculator(natal_chart)
    return calculator.calculate_transit_for_date(current_time, location)


# Example usage
if __name__ == "__main__":
    # Example natal chart
    natal = AstrologicalSubject("John Lennon", 1940, 10, 9, 18, 30, "Liverpool", "GB")

    # Calculate current transits
    calculator = TransitsCalculator(natal)
    current_transits = calculator.calculate_transit_for_date(datetime.now())

    print(f"Transits for {natal.name}:")
    print(f"Date: {current_transits['transit_date']}")
    print(f"Significant transits: {len(current_transits['significant_transits'])}")

    for transit in current_transits['significant_transits'][:5]:
        print(f"- {transit['transit_planet']} {transit['aspect']} natal {transit['natal_planet']} (orb: {transit['orb']}°)")