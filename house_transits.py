"""
House transit calculation module.

This module handles calculations related to planetary transits through natal houses.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from kerykeion import AstrologicalSubject

from models import PLANET_NAMES, HOUSE_PREFIXES


class HouseTransitCalculator:
    """
    Calculator for planetary transits through natal houses.
    """

    def __init__(self, natal_chart: AstrologicalSubject):
        """
        Initialize the house transit calculator.

        Args:
            natal_chart: The natal chart
        """
        self.natal_chart = natal_chart

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
        house_dates = {}

        # Get current positions
        current_positions = self._get_current_planet_positions(base_date, location)

        # Get natal house cusps
        natal_houses = self._get_natal_house_cusps()

        for planet_name in PLANET_NAMES:
            planet_key = planet_name.capitalize()
            if planet_key not in current_positions:
                continue

            current_house = current_positions[planet_key]['natal_house']
            if current_house == 0:
                continue

            # Use different search ranges and steps for different planets
            # Fast-moving planets: 90 days, daily steps
            # Jupiter/Saturn: 2 years, weekly steps
            # Uranus/Neptune/Pluto: 5 years, monthly steps
            if planet_name in ['sun', 'moon', 'mercury', 'venus', 'mars']:
                search_days = 90
                step_days = 1
            elif planet_name in ['jupiter', 'saturn']:
                search_days = 730  # 2 years
                step_days = 7
            else:  # Uranus, Neptune, Pluto
                search_days = 1825  # 5 years
                step_days = 30

            # Find entry date (when planet entered current house)
            entry_date = self._find_house_entry_date(planet_name, current_house, base_date, location, natal_houses, direction='backward', max_days=search_days, step_days=step_days)

            # Find exit date (when planet will leave current house)
            exit_date = self._find_house_entry_date(planet_name, current_house, base_date, location, natal_houses, direction='forward', max_days=search_days, step_days=step_days)

            house_dates[planet_key] = {
                'current_house': current_house,
                'entry_date': entry_date.strftime('%Y-%m-%d') if entry_date else 'Unknown',
                'exit_date': exit_date.strftime('%Y-%m-%d') if exit_date else 'Unknown',
                'days_in_house': (exit_date - entry_date).days if entry_date and exit_date else 0
            }

        return house_dates

    def _get_current_planet_positions(self, base_date: datetime, location: str) -> Dict[str, Dict[str, Any]]:
        """Get current planet positions with natal house information."""
        # Create transit chart
        transit_chart = AstrologicalSubject(
            "Temp",
            base_date.year,
            base_date.month,
            base_date.day,
            12, 0,  # Noon for consistency
            location.split(",")[0].strip(),
            location.split(",")[1].strip() if "," in location else "GB",
            geonames_username="borisalpine"
        )

        return self._get_planet_positions(transit_chart, self.natal_chart)

    def _get_natal_house_cusps(self) -> List[float]:
        """Get the absolute positions of natal house cusps."""
        houses = []
        for i in range(1, 13):
            house = getattr(self.natal_chart, f"{HOUSE_PREFIXES[i-1]}_house")
            houses.append(house.abs_pos)
        return houses

    def _find_house_entry_date(self, planet_name: str, target_house: int, base_date: datetime,
                              location: str, natal_houses: List[float], direction: str = 'backward',
                              max_days: int = 365, step_days: int = 1) -> Optional[datetime]:
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
                geonames_username="borisalpine"
            )
            planet = getattr(transit_chart, planet_name)
            current_pos = planet.abs_pos

            # Determine current house
            current_house = self._determine_house(current_pos, natal_houses)

        except Exception:
            return None

        # If we're looking for entry to target house and we're already in it,
        # search backward until we're not in it
        if direction == 'backward' and current_house == target_house:
            # Search backward until we're in a different house
            for days in range(step_days, max_days + 1, step_days):
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
                        geonames_username="borisalpine",
                    )
                    planet = getattr(transit_chart, planet_name)
                    check_pos = planet.abs_pos

                    # Determine house at check date
                    check_house = self._determine_house(check_pos, natal_houses)

                    if check_house != target_house:
                        # Found the entry date - approximately the day after this check
                        return check_date + timedelta(days=step_days)

                except Exception:
                    continue

        # If we're looking for exit from target house and we're in it,
        # search forward until we're not in it
        elif direction == 'forward' and current_house == target_house:
            # Search forward until we're in a different house
            for days in range(step_days, max_days + 1, step_days):
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
                        geonames_username="borisalpine"
                    )
                    planet = getattr(transit_chart, planet_name)
                    check_pos = planet.abs_pos

                    # Determine house at check date
                    check_house = self._determine_house(check_pos, natal_houses)

                    if check_house != target_house:
                        # Found the exit date - approximately the day before this check
                        return check_date + timedelta(days=-step_days)

                except Exception:
                    continue

        return None

    def _determine_house(self, planet_abs_pos: float, natal_houses: List[float]) -> int:
        """
        Determine which natal house a planet is in based on its absolute position.

        Args:
            planet_abs_pos: Planet's absolute position in degrees
            natal_houses: List of natal house cusp positions

        Returns:
            House number (1-12)
        """
        for i in range(12):
            current_house_start = natal_houses[i]
            next_house_start = natal_houses[(i + 1) % 12]

            # Handle the wrap-around at 360/0 degrees
            if current_house_start < next_house_start:
                # Normal case
                if current_house_start <= planet_abs_pos < next_house_start:
                    return i + 1
            else:
                # Wrap-around case (e.g., House 12 to House 1)
                if current_house_start <= planet_abs_pos or planet_abs_pos < next_house_start:
                    return i + 1

        return 1  # Default fallback

    def _get_planet_positions(self, chart: AstrologicalSubject, natal_chart: Optional[AstrologicalSubject] = None) -> Dict[str, Dict[str, Any]]:
        """
        Get positions of all planets in a chart.

        Args:
            chart: The chart to get positions from
            natal_chart: Optional natal chart to calculate house placements

        Returns:
            Dictionary of planet positions
        """
        positions = {}
        for planet_name in PLANET_NAMES:
            planet = getattr(chart, planet_name)

            planet_data = {
                'sign': planet.sign,
                # Use `position` (degrees within the sign) for displayable degree value.
                'sign_num': planet.position,
                'position': planet.position,
                'retrograde': planet.retrograde
            }

            # If natal chart is provided, calculate which natal house the planet is in
            if natal_chart:
                # Get natal house cusps
                natal_houses = self._get_natal_house_cusps()

                # Find which natal house the planet is in
                planet_abs_pos = planet.abs_pos
                house_num = self._determine_house(planet_abs_pos, natal_houses)

                planet_data['natal_house'] = house_num

            positions[planet_name.capitalize()] = planet_data

        return positions