"""
Transit data formatting module.

This module handles the formatting and processing of transit-related data.
"""

from typing import Any, Dict, Optional

from kerykeion import AstrologicalSubject
from kerykeion.utilities import get_houses_list, get_planet_house

from models import PLANET_NAMES, HOUSE_INDEX


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
        natal_house_degrees = (
            [h.abs_pos for h in get_houses_list(natal_chart)] if natal_chart else None
        )

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

            if natal_house_degrees is not None:
                house_name = get_planet_house(planet.abs_pos, natal_house_degrees)
                planet_data['natal_house'] = HOUSE_INDEX[house_name]

            positions[planet_name.capitalize()] = planet_data

        return positions
