"""
Transit aspects calculation module.

This module handles the calculation and identification of astrological aspects
between transit and natal planets.
"""

from typing import Any, Dict, List

from kerykeion import AstrologicalSubject, SynastryAspects

from models import (
    TRANSIT_ACTIVE_POINTS,
    TRANSIT_ACTIVE_ASPECTS,
    ASPECT_SYMBOLS
)


class TransitAspectCalculator:
    """
    Calculator for transit aspects between transit and natal charts.
    """

    def __init__(self, natal_chart: AstrologicalSubject):
        """
        Initialize the aspect calculator.

        Args:
            natal_chart: The natal chart to calculate aspects against
        """
        self.natal_chart = natal_chart

    def calculate_transit_aspects(self, transit_chart: AstrologicalSubject) -> List[Dict[str, Any]]:
        """
        Calculate aspects between transit and natal planets.

        Args:
            transit_chart: The transit chart

        Returns:
            List of aspect dictionaries
        """
        synastry_aspects = SynastryAspects(
            transit_chart,
            self.natal_chart,
            active_points=TRANSIT_ACTIVE_POINTS,
            active_aspects=TRANSIT_ACTIVE_ASPECTS
        )

        allowed_planets = {name for name in TRANSIT_ACTIVE_POINTS}
        aspects: List[Dict[str, Any]] = []

        for aspect in synastry_aspects.all_aspects:
            if aspect.p1_name not in allowed_planets or aspect.p2_name not in allowed_planets:
                continue

            aspects.append({
                'transit_planet': aspect.p1_name,
                'natal_planet': aspect.p2_name,
                'aspect': aspect.aspect,
                'orb': round(abs(aspect.orbit), 2),
                'exact_angle': aspect.aspect_degrees,
                'transit_position': round(aspect.p1_abs_pos % 30, 2),
                'natal_position': round(aspect.p2_abs_pos % 30, 2)
            })

        return aspects

    def identify_significant_transits(self, aspects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify the most significant transits from the aspect list.

        Args:
            aspects: List of transit aspects

        Returns:
            List of significant transits (orb ≤ 3 degrees)
        """
        # Prioritize aspects by importance and tight orbs
        aspect_priority = {
            'conjunction': 10,
            'opposition': 9,
            'square': 8,
            'trine': 7,
            'sextile': 6
        }

        # Sort by priority and orb tightness
        sorted_aspects = sorted(
            aspects,
            key=lambda x: (aspect_priority.get(x['aspect'], 0), -x['orb']),
            reverse=True
        )

        # Return top significant aspects (those with orb <= 3 degrees)
        return [aspect for aspect in sorted_aspects if aspect['orb'] <= 3][:10]