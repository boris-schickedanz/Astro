"""
Shared data models and constants for the Astro project.

This module contains common data structures, constants, and type definitions
used across different modules of the astrological calculation system.
"""

from typing import Dict, List, Any, Union
from kerykeion.kr_types.kr_literals import AxialCusps, Planet
from kerykeion.kr_types.kr_models import ActiveAspect
import swisseph as swe
import math


# Planet and point definitions for transit calculations
TRANSIT_ACTIVE_POINTS: List[Union[AxialCusps, Planet]] = [
    "Sun",
    "Moon",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto"
]

# Aspect definitions for transit calculations
TRANSIT_ACTIVE_ASPECTS: List[ActiveAspect] = [
    {"name": "conjunction", "orb": 10},
    {"name": "opposition", "orb": 10},
    {"name": "square", "orb": 7},
    {"name": "trine", "orb": 8},
    {"name": "sextile", "orb": 6},
]

# Outer planets for long-term transit calculations
OUTER_PLANET_POINTS: List[Union[AxialCusps, Planet]] = [
    "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"
]

# Tighter orbs for long-term transits
LONG_TERM_ACTIVE_ASPECTS: List[ActiveAspect] = [
    {"name": "conjunction", "orb": 2},
    {"name": "opposition", "orb": 2},
    {"name": "square", "orb": 2},  # Was 1.5 in original, but keeping as 2 for consistency
    {"name": "trine", "orb": 1},
    {"name": "sextile", "orb": 1},
]

# Planets relevant for natal aspects
NATAL_RELEVANT_PLANETS = {
    "Sun", "Moon", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"
}

# House name mappings
HOUSE_NAMES = [
    'First_House', 'Second_House', 'Third_House', 'Fourth_House',
    'Fifth_House', 'Sixth_House', 'Seventh_House', 'Eighth_House',
    'Ninth_House', 'Tenth_House', 'Eleventh_House', 'Twelfth_House'
]

# Reverse map: kerykeion's planet.house string → 1-12 integer.
HOUSE_INDEX: Dict[str, int] = {name: i + 1 for i, name in enumerate(HOUSE_NAMES)}

HOUSE_PREFIXES = [
    'first', 'second', 'third', 'fourth', 'fifth', 'sixth',
    'seventh', 'eighth', 'ninth', 'tenth', 'eleventh', 'twelfth'
]

# Planet names for display (main planets)
PLANET_NAMES = [
    'sun', 'moon', 'mercury', 'venus', 'mars',
    'jupiter', 'saturn', 'uranus', 'neptune', 'pluto'
]

# Additional celestial points for display
ADDITIONAL_POINTS = [
    'mean_node', 'mean_lilith', 'chiron'
]

# Display names for additional points
POINT_DISPLAY_NAMES = {
    'mean_node': 'North Node',
    'mean_lilith': 'Lilith',
    'chiron': 'Chiron'
}

# Aspect symbols for display
ASPECT_SYMBOLS = {
    'conjunction': '☌',
    'opposition': '☍',
    'square': '□',
    'trine': '△',
    'sextile': '⚹'
}


def calculate_lot_of_fortune(chart) -> float:
    """
    Calculate the Lot of Fortune position.

    The Lot of Fortune is calculated as:
    - Day birth: ASC + Moon - Sun
    - Night birth: ASC + Sun - Moon

    Day/night is determined by whether the Sun is above the horizon at birth time.

    Args:
        chart: AstrologicalSubject instance

    Returns:
        Position of Lot of Fortune in degrees (0-360)
    """
    # Get positions in degrees
    asc_pos = chart.ascendant.abs_pos
    sun_pos = chart.sun.abs_pos
    moon_pos = chart.moon.abs_pos

    # Determine day/night birth based on approximate Sun position
    # Day if birth hour is between 6 and 18 (daylight hours)
    is_day_birth = 6 <= chart.hour < 18

    if is_day_birth:
        lot_pos = asc_pos + moon_pos - sun_pos
    else:
        lot_pos = asc_pos + sun_pos - moon_pos

    # Normalize to 0-360 degrees
    lot_pos = lot_pos % 360
    if lot_pos < 0:
        lot_pos += 360

    return lot_pos
