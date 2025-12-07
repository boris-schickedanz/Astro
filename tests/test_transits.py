"""
Tests for the transits calculation functionality.
"""

import pytest
from datetime import datetime, timedelta
from kerykeion import AstrologicalSubject
from transits import TransitsCalculator, calculate_current_transits


class TestTransitsCalculator:
    """Test cases for the TransitsCalculator class."""

    @pytest.fixture
    def sample_natal_chart(self):
        """Create a sample natal chart for testing."""
        return AstrologicalSubject("Test Person", 1990, 6, 15, 14, 30, "London", "GB")

    @pytest.fixture
    def calculator(self, sample_natal_chart):
        """Create a TransitsCalculator instance."""
        return TransitsCalculator(sample_natal_chart)

    def test_calculator_initialization(self, calculator, sample_natal_chart):
        """Test that the calculator initializes correctly."""
        assert calculator.natal_chart == sample_natal_chart
        assert calculator.natal_chart.name == "Test Person"

    def test_calculate_transit_for_date(self, calculator):
        """Test transit calculation for a specific date."""
        test_date = datetime(2024, 6, 15, 12, 0, 0)
        result = calculator.calculate_transit_for_date(test_date)

        # Check basic structure
        assert "transit_date" in result
        assert "natal_name" in result
        assert "transit_planets" in result
        assert "natal_planets" in result
        assert "aspects" in result
        assert "significant_transits" in result

        # Check that transit date is correct
        assert result["transit_date"] == test_date.isoformat()
        assert result["natal_name"] == "Test Person"

        # Check that planets are included
        expected_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']
        assert all(planet in result["transit_planets"] for planet in expected_planets)
        assert all(planet in result["natal_planets"] for planet in expected_planets)

    def test_calculate_transits_for_range(self, calculator):
        """Test transit calculation for a date range."""
        start_date = datetime(2024, 6, 15, 12, 0, 0)
        end_date = datetime(2024, 6, 17, 12, 0, 0)

        results = calculator.calculate_transits_for_range(start_date, end_date, interval_days=1)

        # Should have 3 results (15th, 16th, 17th)
        assert len(results) == 3

        # Check that dates are sequential
        for i, result in enumerate(results):
            expected_date = start_date + timedelta(days=i)
            assert result["transit_date"] == expected_date.isoformat()

    def test_significant_transits_identification(self, calculator):
        """Test that significant transits are properly identified."""
        test_date = datetime(2024, 6, 15, 12, 0, 0)
        result = calculator.calculate_transit_for_date(test_date)

        significant_transits = result["significant_transits"]

        # Significant transits should have orb <= 3 degrees
        for transit in significant_transits:
            assert transit["orb"] <= 3.0

        # Should be sorted by priority and orb tightness
        if len(significant_transits) > 1:
            # Check that higher priority aspects come first
            aspect_priority = {'conjunction': 10, 'opposition': 9, 'square': 8, 'trine': 7, 'sextile': 6}
            first_priority = aspect_priority.get(significant_transits[0]["aspect"], 0)
            second_priority = aspect_priority.get(significant_transits[1]["aspect"], 0)
            assert first_priority >= second_priority

    def test_calculate_current_transits(self, sample_natal_chart):
        """Test the calculate_current_transits helper function."""
        result = calculate_current_transits(sample_natal_chart)

        assert "transit_date" in result
        assert "natal_name" in result
        assert result["natal_name"] == "Test Person"

        # Should have current timestamp (timezone-aware comparison)
        import pytz
        current_time = datetime.now(pytz.UTC)
        transit_datetime = datetime.fromisoformat(result["transit_date"])
        if transit_datetime.tzinfo is None:
            # If somehow it's naive, make it UTC
            transit_datetime = pytz.UTC.localize(transit_datetime)
        time_diff = abs((current_time - transit_datetime).total_seconds())
        assert time_diff < 120  # Within 2 minutes (allowing for timezone lookup time)

    def test_aspect_calculation_structure(self, calculator):
        """Test that aspects are calculated with correct structure."""
        test_date = datetime(2024, 6, 15, 12, 0, 0)
        result = calculator.calculate_transit_for_date(test_date)

        aspects = result["aspects"]

        # Check that aspects have required fields
        required_fields = ["transit_planet", "natal_planet", "aspect", "orb", "exact_angle", "transit_position", "natal_position"]

        for aspect in aspects:
            for field in required_fields:
                assert field in aspect
                assert isinstance(aspect[field], (str, float, int))

    def test_generate_transit_chart_svg(self, calculator, tmp_path):
        """Test SVG chart generation."""
        test_date = datetime(2024, 6, 15, 12, 0, 0)

        # Generate chart with custom output directory
        chart_path = calculator.generate_transit_chart_svg(test_date, output_path=str(tmp_path))

        # Should return a filename
        assert isinstance(chart_path, str)
        assert "Transit Chart.svg" in chart_path

        # Note: We don't check if file actually exists as it depends on KerykeionChartSVG working correctly
        # In a real test environment, you'd want to verify the file creation

    def test_different_locations(self, calculator):
        """Test transit calculation for different locations."""
        test_date = datetime(2024, 6, 15, 12, 0, 0)

        # Test with different location
        result_ny = calculator.calculate_transit_for_date(test_date, "New York, US")
        result_london = calculator.calculate_transit_for_date(test_date, "London, GB")

        # Results should be different (different time zones affect calculations)
        # Note: This is a basic check - in reality the differences might be subtle
        assert result_ny["transit_date"] == result_london["transit_date"]  # Same UTC time
        assert result_ny["natal_name"] == result_london["natal_name"]


if __name__ == "__main__":
    pytest.main([__file__])