"""
Annual profection (Hellenistic technique).

Each year of life advances the activated house by one. Year 0 = 1st house,
year 1 = 2nd, ..., year 12 = 1st again. The sign on that natal house cusp
identifies the "lord of the year" via modern rulership.
"""

from datetime import date
from typing import Any, Dict, Optional

from kerykeion import AstrologicalSubject

from chart_analysis import SIGN_TO_RULER
from models import HOUSE_INDEX, HOUSE_PREFIXES


def _age_at(reference: date, birth_year: int, birth_month: int, birth_day: int) -> int:
    """Completed years between birth and reference date (i.e. age in years)."""
    age = reference.year - birth_year
    if (reference.month, reference.day) < (birth_month, birth_day):
        age -= 1
    return age


def compute_profection(chart: AstrologicalSubject, reference: date) -> Optional[Dict[str, Any]]:
    """
    Compute the active annual profection for the given reference date.

    Returns None if the chart has no birth time (houses required).
    """
    if not hasattr(chart, "first_house") or chart.first_house is None:
        return None

    age = _age_at(reference, chart.year, chart.month, chart.day)
    profected_house = (age % 12) + 1

    house_attr = f"{HOUSE_PREFIXES[profected_house - 1]}_house"
    house_obj = getattr(chart, house_attr)
    profected_sign = house_obj.sign

    year_lord_name = SIGN_TO_RULER.get(profected_sign)
    year_lord_planet = getattr(chart, year_lord_name.lower(), None) if year_lord_name else None
    year_lord_house = HOUSE_INDEX.get(year_lord_planet.house, 0) if year_lord_planet else 0

    return {
        "age": age,
        "profected_house": profected_house,
        "profected_sign": profected_sign,
        "year_lord": year_lord_name,
        "year_lord_sign": year_lord_planet.sign if year_lord_planet else None,
        "year_lord_degree": round(year_lord_planet.position, 2) if year_lord_planet else None,
        "year_lord_house": year_lord_house,
        "year_lord_retrograde": year_lord_planet.retrograde if year_lord_planet else False,
    }
