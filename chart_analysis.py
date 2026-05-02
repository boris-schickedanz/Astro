"""
Chart-level analysis: element/modality balance, hemispheres, stelliums, chart ruler.

Operates on a kerykeion AstrologicalSubject. All functions are pure derivations
from natal placements; no ephemeris or network access.
"""

from collections import Counter
from typing import Any, Dict, List, Optional

from kerykeion import AstrologicalSubject

from models import HOUSE_INDEX, PLANET_NAMES


# Modern rulerships (used for chart ruler and profection year-lord).
SIGN_TO_RULER: Dict[str, str] = {
    "Ari": "Mars",
    "Tau": "Venus",
    "Gem": "Mercury",
    "Can": "Moon",
    "Leo": "Sun",
    "Vir": "Mercury",
    "Lib": "Venus",
    "Sco": "Pluto",
    "Sag": "Jupiter",
    "Cap": "Saturn",
    "Aqu": "Uranus",
    "Pis": "Neptune",
}


def compute_element_balance(chart: AstrologicalSubject) -> Dict[str, int]:
    """Count main planets (Sun..Pluto) by sign element via kerykeion's planet.element."""
    counts = Counter({"Fire": 0, "Earth": 0, "Air": 0, "Water": 0})
    for planet_name in PLANET_NAMES:
        counts[getattr(chart, planet_name).element] += 1
    return dict(counts)


def compute_modality_balance(chart: AstrologicalSubject) -> Dict[str, int]:
    """Count main planets (Sun..Pluto) by sign quality via kerykeion's planet.quality."""
    counts = Counter({"Cardinal": 0, "Fixed": 0, "Mutable": 0})
    for planet_name in PLANET_NAMES:
        counts[getattr(chart, planet_name).quality] += 1
    return dict(counts)


def compute_hemispheres(chart: AstrologicalSubject) -> Optional[Dict[str, Dict[str, int]]]:
    """
    Bucket the 10 main planets by hemisphere and quadrant.

    Returns None if any planet's house can't be resolved. Conventions:
    Northern (below) = houses 1-6; Eastern (self) = houses 10-12, 1-3.
    """
    northern = southern = eastern = western = 0
    for planet_name in PLANET_NAMES:
        house = HOUSE_INDEX.get(getattr(chart, planet_name).house, 0)
        if house == 0:
            return None
        if 1 <= house <= 6:
            northern += 1
        else:
            southern += 1
        if house in (10, 11, 12, 1, 2, 3):
            eastern += 1
        else:
            western += 1
    return {
        "horizon": {"Northern (below)": northern, "Southern (above)": southern},
        "meridian": {"Eastern (self)": eastern, "Western (other)": western},
    }


STELLIUM_MIN = 3


def find_stelliums(chart: AstrologicalSubject,
                   has_time: bool = True) -> Dict[str, List[Dict[str, Any]]]:
    """
    Find sign stelliums and (when has_time) house stelliums.

    Sign stelliums are valid without a birth time; house stelliums require one.
    The has_time flag must come from the caller — kerykeion populates
    planet.house even on a synthetic 00:00 chart, so the chart object itself
    can't tell us whether houses are meaningful.
    """
    by_sign: Dict[str, List[str]] = {}
    by_house: Dict[int, List[str]] = {}

    for planet_name in PLANET_NAMES:
        planet = getattr(chart, planet_name)
        by_sign.setdefault(planet.sign, []).append(planet_name.capitalize())
        if has_time:
            house = HOUSE_INDEX.get(planet.house, 0)
            if house:
                by_house.setdefault(house, []).append(planet_name.capitalize())

    return {
        "by_sign": [{"sign": s, "planets": p} for s, p in by_sign.items() if len(p) >= STELLIUM_MIN],
        "by_house": [{"house": h, "planets": p} for h, p in by_house.items() if len(p) >= STELLIUM_MIN],
    }


def chart_ruler(chart: AstrologicalSubject) -> Optional[Dict[str, Any]]:
    """Planet ruling the ASC sign + its placement. Requires birth time."""
    if not getattr(chart, "ascendant", None):
        return None

    asc_sign = chart.ascendant.sign
    ruler_name = SIGN_TO_RULER.get(asc_sign)
    ruler_planet = getattr(chart, ruler_name.lower(), None) if ruler_name else None
    if ruler_planet is None:
        return None

    return {
        "asc_sign": asc_sign,
        "ruler": ruler_name,
        "sign": ruler_planet.sign,
        "degree": round(ruler_planet.position, 2),
        "house": HOUSE_INDEX.get(ruler_planet.house, 0),
        "retrograde": ruler_planet.retrograde,
    }
