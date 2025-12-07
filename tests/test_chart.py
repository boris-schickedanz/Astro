import pytest
from kerykeion import AstrologicalSubject, NatalAspects
from chart import display_natal_chart


@pytest.fixture
def sample_chart():
    """Fixture for a sample birth chart."""
    return AstrologicalSubject(
        name="Test Person",
        year=1990,
        month=10,
        day=9,
        hour=14,
        minute=30,
        city="New York",
        nation="US"
    )


def test_chart_creation(sample_chart):
    """Test that a chart can be created with valid data."""
    assert sample_chart.name == "Test Person"
    assert sample_chart.year == 1990
    assert sample_chart.month == 10
    assert sample_chart.day == 9
    assert sample_chart.hour == 14
    assert sample_chart.minute == 30
    assert sample_chart.city == "New York"
    assert sample_chart.nation == "US"


def test_ascendant_calculation(sample_chart):
    """Test that ascendant is calculated correctly."""
    assert sample_chart.ascendant.sign == "Cap"
    assert isinstance(sample_chart.ascendant.sign_num, (int, float))


def test_planet_positions(sample_chart):
    """Test that planet positions are calculated."""
    planets = ['sun', 'moon', 'mercury', 'venus', 'mars']
    for planet_name in planets:
        planet = getattr(sample_chart, planet_name)
        assert hasattr(planet, 'sign')
        assert hasattr(planet, 'sign_num')
        assert isinstance(planet.sign_num, (int, float))


def test_house_positions(sample_chart):
    """Test that house cusps are calculated."""
    house_names = [f"{['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'eleventh', 'twelfth'][i]}_house" for i in range(12)]
    for house_name in house_names:
        house = getattr(sample_chart, house_name)
        assert hasattr(house, 'sign')
        assert hasattr(house, 'sign_num')


def test_aspects_calculation(sample_chart):
    """Test that aspects are calculated."""
    aspects = NatalAspects(sample_chart)
    assert hasattr(aspects, 'all_aspects')
    assert isinstance(aspects.all_aspects, list)
    if aspects.all_aspects:
        aspect = aspects.all_aspects[0]
        assert hasattr(aspect, 'p1_name')
        assert hasattr(aspect, 'p2_name')
        assert hasattr(aspect, 'aspect')
        assert hasattr(aspect, 'orbit')


def test_zodiac_sign_calculation():
    """Test that zodiac signs are calculated for various dates."""
    # Test a few known dates to ensure signs are calculated
    test_cases = [
        (1, 15, "Cap"),  # Capricorn
        (2, 15, "Aqu"),  # Aquarius
        (3, 15, "Pis"),  # Pisces
        (4, 15, "Ari"),  # Aries
        (5, 15, "Tau"),  # Taurus
        (6, 15, "Gem"),  # Gemini
        (7, 15, "Can"),  # Cancer
        (8, 15, "Leo"),  # Leo
        (9, 15, "Vir"),  # Virgo
        (10, 15, "Lib"),  # Libra
        (11, 15, "Sco"),  # Scorpio
        (12, 15, "Sag"),  # Sagittarius
    ]

    for month, day, expected_sign in test_cases:
        chart = AstrologicalSubject(
            name="Test",
            year=2000,
            month=month,
            day=day,
            hour=12,
            minute=0,
            city="London",
            nation="UK"
        )
        assert chart.sun.sign == expected_sign, f"Failed for {month}/{day}: expected {expected_sign}, got {chart.sun.sign}"


def test_chart_without_time_no_houses(capsys):
    """Test that charts without birth time do not display houses."""
    chart = AstrologicalSubject(
        name="Test No Time",
        year=1990,
        month=6,
        day=15,
        hour=0,  # Default to 0
        minute=0,
        city="New York",
        nation="US"
    )
    
    # Display with has_time=False
    display_natal_chart(chart, has_time=False)
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Check that ASC and MC are not displayed
    assert "ASC:" not in output
    assert "MC:" not in output
    
    # Check that houses are not displayed
    assert "Houses:" not in output
    
    # Check that planet lines do not contain "House"
    lines = output.split('\n')
    planet_section = False
    for line in lines:
        if line.strip() == "Planets:":
            planet_section = True
        elif planet_section and line.strip() == "":
            break
        elif planet_section and line.strip():
            assert "House" not in line, f"House found in planet line: {line}"
    
    # Check that additional points do not contain "House"
    additional_section = False
    for line in lines:
        if line.strip() == "Additional Points:":
            additional_section = True
        elif additional_section and line.strip() == "":
            break
        elif additional_section and line.strip():
            assert "House" not in line, f"House found in additional points line: {line}"