"""
Transit data formatting module.

This module handles the formatting and processing of transit-related data.
"""

from typing import Any, Dict, Optional

from kerykeion import AstrologicalSubject

from models import PLANET_NAMES, HOUSE_PREFIXES


class TransitDataFormatter:
    """
    Formatter for transit-related data structures.
    """

    def __init__(self, natal_chart: AstrologicalSubject):
        """
        Initialize the data formatter.

        Args:
            natal_chart: The natal chart
        """
        self.natal_chart = natal_chart

    def get_planet_positions(self, chart: AstrologicalSubject, natal_chart: Optional[AstrologicalSubject] = None) -> Dict[str, Dict[str, Any]]:
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
                # `sign_num` in kerykeion is the sign index (0-11), not the degree in-sign.
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

    def _get_natal_house_cusps(self) -> list[float]:
        """Get the absolute positions of natal house cusps."""
        houses = []
        for i in range(1, 13):
            house = getattr(self.natal_chart, f"{HOUSE_PREFIXES[i-1]}_house")
            houses.append(house.abs_pos)
        return houses

    def _determine_house(self, planet_abs_pos: float, natal_houses: list[float]) -> int:
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