"""Tests for long-term transit calculations powered by Kerykeion."""

from datetime import datetime

import pytest
import config
from kerykeion import AstrologicalSubject

from transits import TransitsCalculator


@pytest.fixture
def sample_chart() -> AstrologicalSubject:
    return AstrologicalSubject(
        "Sample",
        1990,
        6,
        15,
        14,
        30,
        "London",
        "GB",
        geonames_username=config.GEONAMES_USERNAME,
    )


def test_long_term_transits_structure(sample_chart: AstrologicalSubject) -> None:
    calculator = TransitsCalculator(sample_chart)
    base_date = datetime(2024, 6, 1, 12, 0)

    result = calculator.calculate_long_term_transits(
        base_date,
        years_before=1,
        years_after=1,
    )

    assert set(result.keys()) == {"active", "recent_past", "upcoming", "base_date"}
    assert result["base_date"] == base_date.date().strftime("%Y-%m-%d")


def test_long_term_transits_outer_planet_filter(sample_chart: AstrologicalSubject) -> None:
    calculator = TransitsCalculator(sample_chart)
    base_date = datetime(2024, 6, 1, 12, 0)

    result = calculator.calculate_long_term_transits(
        base_date,
        years_before=2,
        years_after=2,
    )

    all_transits = (
        result.get("active", [])
        + result.get("recent_past", [])
        + result.get("upcoming", [])
    )

    if not all_transits:
        pytest.skip("No long-term transits found in the examined timeframe")

    allowed_transit_planets = {"Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"}
    allowed_natal_planets = {
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
        "Pluto",
    }

    for transit in all_transits:
        assert transit["transit_planet"] in allowed_transit_planets
        assert transit["natal_planet"] in allowed_natal_planets


def test_long_term_transits_years_after_parameter(sample_chart: AstrologicalSubject) -> None:
    """Test that years_after parameter correctly limits upcoming transits."""
    calculator = TransitsCalculator(sample_chart)
    base_date = datetime(2024, 6, 1, 12, 0)

    # Test with 2 years - should have some upcoming transits
    result_2_years = calculator.calculate_long_term_transits(
        base_date,
        years_before=2,
        years_after=2,
    )

    # Test with 10 years - should have more or same upcoming transits
    result_10_years = calculator.calculate_long_term_transits(
        base_date,
        years_before=2,
        years_after=10,
    )

    upcoming_2 = result_2_years.get("upcoming", [])
    upcoming_10 = result_10_years.get("upcoming", [])

    # With more years, we should have at least as many upcoming transits
    assert len(upcoming_10) >= len(upcoming_2)

    # Check that transits in the 10-year version can be up to ~10 years out
    if upcoming_10:
        max_days = max(t["days_until"] for t in upcoming_10)
        # Allow some tolerance for the 365-day approximation
        assert max_days <= 10 * 365 + 30, f"Found transit {max_days} days out, exceeding 10 years"

    # Verify that there are transits beyond 2 years in the 10-year version
    transits_beyond_2_years = [t for t in upcoming_10 if t["days_until"] > 2 * 365]
    assert len(transits_beyond_2_years) > 0, "Expected at least one transit beyond 2 years in 10-year scan"

    # If there are transits beyond 2 years, they should only appear in the 10-year version
    for transit in transits_beyond_2_years:
        # This transit should not appear in the 2-year version
        transit_ids_2 = {(t["transit_planet"], t["natal_planet"], t["aspect"]) for t in upcoming_2}
        transit_id = (transit["transit_planet"], transit["natal_planet"], transit["aspect"])
        assert transit_id not in transit_ids_2, f"Transit {transit_id} appears in 2-year version but is {transit['days_until']} days out"
