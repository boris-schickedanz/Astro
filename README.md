# Astro Project

A Python project for calculating astrological data with text output only.

## Features
- Calculate birth charts (natal charts) including:
  - Ascendant (ASC)
  - Midheaven (MC)
  - Planet positions with house placements
  - House cusps
  - Aspects between celestial bodies
  - Cusp detection for planets within 2° of house boundaries
- Calculate astrological transits
  - Current planetary positions and their aspects to natal charts
  - Transit calculations for specific dates
  - Transit calculations for date ranges
  - Long-term transits from outer planets (-10 to +20 years)
  - Generate transit chart visualizations (SVG)

For detailed information on astrological calculations, including ASC, houses, planet positions, aspects, and transits, see `.github/birth_chart_calculation.md`.

## Usage

### Command-Line Interface
The main script now accepts command-line parameters for flexible chart and transit calculations:

```bash
python main.py --name "John Doe" --year 1990 --month 6 --day 15 --hour 14 --minute 30 --city "New York" --nation "US"
```

#### Required Parameters for Birth Chart:
- `--name`: Name of the person
- `--year`: Birth year (4 digits)
- `--month`: Birth month (1-12)
- `--day`: Birth day (1-31)
- `--city`: Birth city name
- `--nation`: Birth nation/country code

#### Optional Parameters:
- `--hour`: Birth hour (0-23)
- `--minute`: Birth minute (0-59)
- `--lng`: Birth longitude (will be looked up if not provided)
- `--lat`: Birth latitude (will be looked up if not provided)
- `--tz`: Timezone string (will be looked up if not provided)
- `--transit-city`: City for transit calculations (defaults to birth city)
- `--transit-nation`: Nation for transit calculations (defaults to birth nation)
- `--transit-date`: Date for transit calculations (YYYY-MM-DD format, defaults to current date)
- `--transit-hour`: Hour for transit calculations (0-23, defaults to 12)

#### Examples:

**Basic natal chart:**
```bash
python main.py --name "Jane Smith" --year 1985 --month 3 --day 20 --hour 9 --minute 15 --city "London" --nation "UK"
```

**Natal chart with transits for different location:**
```bash
python main.py --name "John Doe" --year 1990 --month 6 --day 15 --hour 14 --minute 30 --city "New York" --nation "US" --transit-city "Paris" --transit-nation "FR"
```

**Natal chart with transits for specific date:**
```bash
python main.py --name "Alice Johnson" --year 1975 --month 12 --day 25 --hour 18 --minute 45 --city "Sydney" --nation "AU" --transit-date "2025-12-25"
```

## Output Format

The natal chart output includes:

- **Basic Information**: Birth date, time, location, timezone, ASC, and MC (ASC and MC only shown if birth time is provided)
- **Planets**: Each planet shows:
  - Zodiac sign and degree
  - House number (only if birth time is provided)
  - Cusp notation when within 2° of house boundaries (only if birth time is provided)
- **Houses**: Cusp positions for all 12 houses (only shown if birth time is provided)
- **Aspects**: Angular relationships between planets
- **Transits**: Current planetary influences and significant transit aspects

### Example Output:
```
Birth Chart for Boris
Born: 1975-08-06 09:48
Location: Hanau, DE (50.1342, 8.9142)
Timezone: Europe/Berlin
ASC: Lib 6°
MC: Can 3°

Planets:
Sun: Leo 4° - House 11
Moon: Can 3° - House 10
Mercury: Leo 4° - House 11
Venus: Vir 5° - House 12 (cusp 11/12)
Mars: Tau 1° - House 8
Jupiter: Ari 0° - House 7
Saturn: Can 3° - House 10
Uranus: Lib 6° - House 2 (cusp 1/2)
Neptune: Sag 8° - House 3
Pluto: Lib 6° - House 1

Houses:
House 1: Lib 6°
...

Aspects:
Sun conjunction Mercury (5.4°)
...

==================================================
TRANSITS CALCULATION
==================================================

Transits for Boris on 2025-10-09 12:00 at Stans, CH
Number of active transit aspects: 49
Number of significant transits (orb ≤ 3°): 10

Significant Transits:
1. Mars conjunction natal Venus (orb: 0.18°)
...

==================================================
LONG-TERM TRANSITS (-10 to +20 YEARS)
==================================================

Most important long-term transits from outer planets (20 found):
1. 2025-02-09 to 2045-09-09 (-0.7 years, 20.6 years): Pluto conjunction natal Pluto
   Transit: Aqu 10° | Natal: Lib 6° | Min orb: 0.02°
2. 2022-04-09 to 2039-03-09 (-3.5 years, 16.9 years): Neptune conjunction natal Uranus
   Transit: Pis 11° | Natal: Lib 6° | Min orb: 0.02°
...
```

### Basic Natal Chart Calculation
Run the main script with command-line parameters for birth data:

```bash
python main.py --name "John Doe" --year 1990 --month 6 --day 15 --hour 14 --minute 30 --city "New York" --nation "US"
```

This calculates the natal chart and current transits. See the Usage section above for all parameters.

### Transit Calculations

#### Using the TransitsCalculator Class
```python
from kerykeion import AstrologicalSubject
from transits import TransitsCalculator
from datetime import datetime

# Create natal chart
natal = AstrologicalSubject("John Doe", 1990, 6, 15, 14, 30, lng=-74.0060, lat=40.7128, tz_str="America/New_York", city="New York")

# Initialize calculator
calculator = TransitsCalculator(natal)

# Calculate current transits
current_transits = calculator.calculate_transit_for_date(datetime.now())
print(f"Significant transits: {len(current_transits['significant_transits'])}")

# Calculate transits for a specific date
future_date = datetime(2025, 12, 25, 12, 0, 0)
holiday_transits = calculator.calculate_transit_for_date(future_date)

# Generate transit chart SVG
chart_file = calculator.generate_transit_chart_svg(datetime.now())
```

#### Using the Helper Function
```python
from transits import calculate_current_transits
from kerykeion import AstrologicalSubject

natal = AstrologicalSubject("Jane Smith", 1985, 3, 20, 9, 15, lng=-0.1276, lat=51.5074, tz_str="Europe/London", city="London")
current = calculate_current_transits(natal)
```

## What are Transits?

Transits show how current planetary movements interact with your natal (birth) chart:

- **Purpose**: Indicate timing for opportunities, challenges, and life changes
- **Calculation**: Compare current planetary positions with natal positions
- **Aspects**: Conjunction, opposition, trine, square, sextile
- **Duration**: Inner planets (Sun, Moon, Mercury, Venus, Mars) = days/weeks
- **Duration**: Outer planets (Jupiter, Saturn, Uranus, Neptune, Pluto) = months/years
- **Orbs**: Angular separation allowance (tight orbs = stronger effects)

## Requirements
Install dependencies in a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage Notes
- Always activate the virtual environment before running Python commands: `source .venv/bin/activate`
- Use the virtual environment's Python executable: `.venv/bin/python main.py`
- The project uses the kerykeion library with geonames for location lookups
- Set a custom geonames username in your code for better reliability (see kerykeion documentation)

## Testing
This project uses pytest for unit testing. To run the tests:

```bash
source .venv/bin/activate
python -m pytest
```

The tests cover:
- Chart creation and data validation
- Ascendant and planet position calculations
- House cusp calculations
- Planet house assignments and cusp detection
- Aspect calculations
- Zodiac sign calculations
- Famous persons' charts validation (Einstein, Oprah Winfrey, Steve Jobs, Queen Elizabeth II, Barack Obama)
- **NEW**: Transit calculations and significant transit identification

Aim for >80% test coverage. Run tests before committing code changes.

## Project Structure
```
├── main.py                 # Main script with CLI for natal charts and transits
├── chart.py               # Chart calculation and display logic
├── cli.py                 # Command-line interface handling
├── display.py             # Output formatting functions
├── models.py              # Data models for astrological entities
├── transits.py            # Transit calculation classes and functions
├── transit_aspects.py     # Transit aspect calculations
├── transit_data.py        # Transit data handling
├── house_transits.py      # House transit calculations
├── long_term_transits.py  # Long-term transit calculations
├── test_*.py             # Unit tests
├── requirements.txt       # Python dependencies
├── pytest.ini            # Pytest configuration
├── README.md             # This file
├── .gitignore            # Git ignore file
├── .github/
│   ├── copilot-instructions.md  # Custom Copilot instructions
│   └── birth_chart_calculation.md  # Technical details on calculations
├── cache/                # Geonames cache directory
├── tests/                # Test directory
│   ├── test_chart.py
│   ├── test_famous_charts.py
│   ├── test_transits.py
│   └── test_transits_time_range.py
└── __pycache__/         # Python bytecode cache
```

## Libraries Used
- **kerykeion**: Main astrology calculation library (free, MIT license)
  - Supports natal charts, synastry, composite charts, and **transits**
  - Uses Swiss Ephemeris for astronomical precision
- **pyswisseph**: Swiss Ephemeris Python wrapper (AGPL license)
- Other dependencies as listed in requirements.txt

## Documentation
- `.github/copilot-instructions.md`: Custom instructions for GitHub Copilot
- `.github/birth_chart_calculation.md`: Technical details on astrological calculations
- Includes transit calculation methodology and interpretation guidelines