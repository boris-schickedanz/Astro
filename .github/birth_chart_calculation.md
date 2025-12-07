# Calculating Astrological Birth Charts

This document provides instructions on how to calculate key components of an astrological birth chart: the Ascendant (ASC), houses, and planet positions. Calculations require precise astronomical data and account for location, date, time, and factors like daylight saving time (DST).

## Prerequisites
- Accurate birth data: Date, time (preferably in 24-hour format), and location (latitude and longitude).
- Ephemeris data: Use high-precision ephemerides like the Swiss Ephemeris (based on JPL DE431) for planet positions.
- Time zone and DST adjustments: Ensure time is converted to UTC.
- Software or library: Libraries like pyswisseph (Python wrapper for Swiss Ephemeris) or similar for calculations.

## Step 1: Adjust Birth Time for Time Zone and DST
- Convert local birth time to Coordinated Universal Time (UTC).
- Account for DST: If DST was in effect at birth, subtract 1 hour from the local time before converting to UTC.
- Example: Birth at 14:00 local time in New York (EST, UTC-5) during DST (EDT, UTC-4). Adjust to 13:00 EDT = 17:00 UTC.

## Step 2: Calculate the Ascendant (ASC)
The Ascendant is the zodiac sign rising on the eastern horizon at birth.

### Formula
Use the following formula to calculate the ecliptical longitude of the ASC (λAsc):

λAsc = arctan( y / x )

Where:
- θL = Local Sidereal Time (LST) in degrees
- ε = Obliquity of the ecliptic (approximately 23.4392911° for J2000.0)
- φ = Latitude of birth location (positive for northern, negative for southern)

x = -cos(θL) * sin(θL) * cos(ε) + tan(φ) * sin(ε)
y = -cos(θL) * sin(θL) * cos(ε) + tan(φ) * sin(ε)

### Quadrant Adjustment
- If x < 0, then λAsc = λAsc + 180°
- Else, λAsc = λAsc + 360°
- Then, ensure λAsc is between 0° and 360°.

### Local Sidereal Time (LST)
LST = GST + longitude (in degrees, positive east)

Where GST is Greenwich Sidereal Time, calculated from UTC.

### Notes
- At polar latitudes (>66°N or <66°S), calculations may have discontinuities.
- Long ascension signs (e.g., Cancer, Leo) take longer to rise than short ascension signs (e.g., Capricorn, Aquarius).

## Step 3: Calculate Houses
Houses divide the ecliptic into 12 sections representing life areas. Choose a house system (e.g., Placidus, Equal, Whole Sign).

### Common House Systems
- **Equal House**: Divide the ecliptic into 12 equal 30° segments starting from the ASC.
- **Placidus**: Most common; trisects time arcs from angles (ASC, MC, DSC, IC).
- **Whole Sign**: Each house is a full zodiac sign, starting from the sign containing the ASC.
- **Koch**: Similar to Placidus but uses equal RA increments.

### Calculation Steps
1. Determine the Midheaven (MC) using latitude and LST.
2. For Placidus: Calculate cusps by trisecting the arcs between ASC/MC, MC/DSC, etc.
3. Adjust for latitude; some systems fail near poles.

### Notes
- House systems vary; Placidus is popular but distorts at high latitudes.
- Each house cusp is 180° from the 7th following house.

## Step 4: Calculate Planet Positions
Planet positions are the longitudes in the zodiac at birth time.

### Using Ephemeris
- Use Swiss Ephemeris or similar for precise positions.
- Input: Julian Day Number (JDN) of birth, calculated from date/time.
- Output: Ecliptical longitude (λ) for each planet.

### Key Planets
- Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto.
- Include Chiron, asteroids if desired.

### Adjustments
- True positions: Account for aberration, nutation.
- Sidereal vs. Tropical zodiac: Most Western astrology uses tropical.

## Step 5: Assign Planets to Houses
After calculating planet positions and house cusps, assign each planet to its corresponding house based on its ecliptical longitude.

### House Assignment Logic
1. **Determine House Range**: Each house spans from its cusp to the next house's cusp.
2. **Planet Position**: Compare the planet's longitude (λ) to house cusp longitudes.
3. **Assignment**: A planet belongs to house N if: cusp_N ≤ λ < cusp_(N+1)
4. **Circular Logic**: Handle the transition from House 12 to House 1 (360°/0° boundary).

### Cusp Detection
Planets within 2° of a house boundary are considered "on a cusp" and may exhibit characteristics of both adjacent houses.

#### Cusp Detection Algorithm
For each planet in house N:
- Calculate distance to house N start boundary
- Calculate distance to house N end boundary  
- Use minimum angular distance accounting for zodiac circularity: `min(|λ - boundary|, 360° - |λ - boundary|)`
- If either distance ≤ 2°, mark as cusp with notation "(cusp X/Y)" where X is the closer boundary

#### Example
- Planet at 29° Aries in House 1 (0° Aries cusp)
- Distance to House 1 start: |29° - 0°| = 29°
- Distance to House 1 end: |29° - 30°| = 1°
- Since distance to end ≤ 2°, mark as "(cusp 1/2)"

## Step 6: Assemble the Chart
- Plot ASC, MC, house cusps on the ecliptic.
- Place planets at their calculated longitudes.
- Calculate aspects (angular relationships) between planets.

## Step 9: Calculate Arabic Parts (Lots)
Arabic Parts, also known as Lots, are calculated points in the horoscope that represent various life areas and fortunes. The most important is the Lot of Fortune.

### Lot of Fortune
The Lot of Fortune (Pars Fortuna) represents prosperity, well-being, material success, and fortune.

#### Calculation Formula
The Lot of Fortune is calculated differently for day and night births:

- **Day Birth** (Sun above horizon, in houses 1-6): Lot of Fortune = ASC + Moon - Sun
- **Night Birth** (Sun below horizon, in houses 7-12): Lot of Fortune = ASC + Sun - Moon

All positions are in degrees (0-360° ecliptical longitude). The result must be normalized to 0-360°.

#### Determining Day/Night Birth
- Day birth: Birth hour between 6 and 18 (approximate daylight hours)
- Night birth: Birth hour outside 6-18

#### Example Calculation
For a day birth:
- ASC: 180° (Libra 0°)
- Moon: 120° (Leo 0°)  
- Sun: 90° (Cancer 0°)
- Lot of Fortune = 180 + 120 - 90 = 210° (Libra 30°)

For a night birth:
- ASC: 180° (Libra 0°)
- Moon: 120° (Leo 0°)
- Sun: 270° (Capricorn 0°)
- Lot of Fortune = 180 + 270 - 120 = 330° (Aquarius 0°)

#### Interpretation
- The Lot of Fortune shows where fortune, prosperity, and well-being are found
- Its house placement indicates the life area where success comes naturally
- Aspects to the Lot of Fortune show how fortune is activated
- The sign shows the style or manner of fortune manifestation
Transits show how current planetary positions interact with the natal chart, indicating timing for life events and changes.

### What are Transits?
- **Definition**: Current planetary positions and their aspects to natal planets/house cusps.
- **Purpose**: Show when natal potentials are activated by current celestial movements.
- **Duration**: Effects vary by planet speed (fast: Sun/Moon; slow: outer planets).
- **Interpretation**: Transits trigger events when they aspect natal planets within specified orbs.

### Transit Calculation Steps
1. **Get Current Planetary Positions**: Calculate positions for current date/time using ephemeris.
2. **Compare with Natal Chart**: Find angular relationships between current and natal positions.
3. **Identify Aspects**: Look for conjunctions, oppositions, trines, squares, sextiles within orbs.
4. **Determine Significance**: Prioritize aspects by orb tightness and planet importance.

### Major Transit Aspects
- **Conjunction (0°)**: Merging of energies, new beginnings.
- **Opposition (180°)**: Awareness, relationships, challenges.
- **Trine (120°)**: Harmony, opportunities, ease.
- **Square (90°)**: Tension, action, growth through conflict.
- **Sextile (60°)**: Opportunities, cooperation, positive changes.

### Transit Orbs (Allowable Angular Separation)
- **Sun**: ±10°
- **Moon**: ±8°
- **Inner Planets** (Mercury, Venus, Mars): ±7°
- **Outer Planets** (Jupiter, Saturn): ±5°
- **Slow Outer Planets** (Uranus, Neptune, Pluto): ±3°

### Transit Duration Guidelines
- **Sun**: 1-2 days
- **Moon**: Hours
- **Mercury/Venus**: 1-2 days
- **Mars**: 1-2 weeks
- **Jupiter**: 1-2 months
- **Saturn**: 1-2 years
- **Uranus/Neptune/Pluto**: Multiple years

### Special Transit Considerations
- **Retrograde Transits**: Extended influence, internal processing.
- **Stationary Planets**: Intensified effects when changing direction.
- **Multiple Transits**: Combined effects create complex periods.
- **House Transits**: Planets transiting natal house cusps activate house themes.

## Step 8: Calculate Long-Term Transits
Long-term transits track the slower-moving outer planets over extended periods to identify major life themes and transformational periods.

### What are Long-Term Transits?
- **Purpose**: Track significant life-changing planetary influences over months to years.
- **Focus**: Outer planets (Jupiter, Saturn, Uranus, Neptune, Pluto) that move slowly and have profound effects.
- **Time Window**: Scan 2 years before and 10 years after current date (12-year total window) to capture both recent past and upcoming major transits.
- **Retrograde Awareness**: Track multiple passes when planets go retrograde and return to the same aspect.

### Planets Included in Long-Term Transit Analysis
- **Jupiter** (12-year orbit): Expansion, growth, opportunities, philosophy, luck (0.5-3 months per transit).
- **Saturn** (29-year orbit): Structure, discipline, lessons, responsibilities (3-12 months per transit).
- **Uranus** (84-year orbit): Revolution, awakening, breakthroughs, sudden changes (6-18 months per transit).
- **Neptune** (165-year orbit): Spirituality, dissolution, dreams, confusion (12-24 months per transit).
- **Pluto** (248-year orbit): Transformation, power, death/rebirth, deep change (12-36 months per transit).

### Long-Term Transit Orbs (Tight for Precision)
These orbs are tighter than regular transits to identify peak influence periods:
- **Conjunction (0°)**: ±2°
- **Opposition (180°)**: ±2°
- **Square (90°)**: ±1.5°
- **Trine (120°)**: ±1°
- **Sextile (60°)**: ±1°

**Rationale**: Tight orbs focus on the most intense period when the transit is exact or near-exact, avoiding the extended "shadow period" captured by wider orbs in regular transit calculations.

### Long-Term Transit Calculation Algorithm
1. **Define Scan Window**: Start 2 years before current date, end 10 years after (12-year total).
2. **Weekly Sampling**: Calculate planetary positions every 7 days (not monthly) to capture retrograde patterns.
3. **Aspect Detection**: For each sample date, check if transiting planet forms major aspect within tight orbs.
4. **Track Individual Passes**: Each time a planet enters orb, create a new transit pass record.
5. **Merge Retrograde Cycles**: If multiple passes occur within 6 months, merge them into one complete transit cycle.
6. **Calculate Duration**: Compute months from first entry to final exit of orb.
7. **Categorize by Status**:
   - **Currently Active**: Transit is happening now (current date within start/end range).
   - **Recently Completed**: Transit ended within past 6 months.
   - **Upcoming**: Transit will begin within next 6 months to 10 years.

### Retrograde Pass Merging Logic
When an outer planet goes retrograde, it may aspect the same natal planet 2-3 times:
1. **Direct Pass**: Planet moves forward into aspect.
2. **Retrograde Pass**: Planet turns retrograde, moves backward through aspect again.
3. **Final Direct Pass**: Planet turns direct, moves forward through aspect one last time.

**Merging Rule**: If the gap between passes is ≤6 months, merge them into one continuous transit showing the complete cycle from first entry to final exit.

**Example**: 
- Saturn enters orb of trine to natal Moon: April 15, 2025
- Saturn goes retrograde, re-enters orb: August 3, 2025
- Saturn turns direct, exits orb: January 27, 2026
- **Result**: One transit "Saturn trine Moon: Apr 2025 - Jan 2026 (9.2 months, 2 passes)"

### Long-Term Transit Output Format
Transits are displayed in three temporal categories with detailed information:

#### Currently Active Transits
```
♃ Jupiter opposition Venus
  Duration: 2025-08-19 to 2025-11-02 (2.5 months)
  Status: Active (55.3% complete)
  Current orb: 0.85° (applying)
```

#### Recently Completed Transits (Past 6 Months)
```
♆ Neptune trine Moon
  Duration: 2024-02-13 to 2025-02-04 (11.7 months, 3 passes)
  Status: Completed 8 months ago
  Peak precision: 0.12° (exact on 2024-09-15)
```

#### Upcoming Transits (Next 6 Months to 10 Years)
```
♄ Saturn square Sun
  Duration: 2026-03-10 to 2026-09-22 (6.4 months)
  Status: Begins in 5 months
  Retrograde cycle: 2 passes expected
```

### Long-Term Transit Interpretation
- **Jupiter Transits**: Opportunities for growth, expansion in the area of life represented by the natal planet/house. Generally positive but can indicate excess.
- **Saturn Transits**: Tests, responsibilities, maturation in life area. Hard aspects challenge; soft aspects support building solid foundations.
- **Uranus Transits**: Sudden changes, liberation, breakthroughs. Disrupts status quo, brings innovation and awakening.
- **Neptune Transits**: Spiritual openings, dissolution of boundaries, confusion. Can inspire creativity or create illusions.
- **Pluto Transits**: Deep transformation, power dynamics, elimination of what no longer serves. Intense but ultimately regenerative.

### Why Jupiter is Included Despite Faster Motion
Although Jupiter completes its orbit in 12 years (faster than Saturn's 29 years), it is included in long-term transit analysis because:
1. **Traditional Importance**: Jupiter is a "social planet" representing expansion, growth, and opportunities—major life themes.
2. **Meaningful Duration**: Jupiter transits last 0.5-3 months (with retrograde), long enough to create significant life changes.
3. **Timing of Opportunities**: Jupiter marks windows when opportunities open in specific life areas—critical for planning and decision-making.
4. **Balance with Saturn**: Jupiter (benefic) and Saturn (malefic) together show the balance of expansion/contraction in life.

### Performance Considerations
- **Sampling Rate**: Weekly (7-day) intervals balance accuracy with performance (~208 calculations for 4-year window).
- **Calculation Time**: Typically 1-2 seconds for complete long-term transit analysis.
- **Caching**: Consider caching results since outer planet positions change slowly.

### Using Kerykeion for Transits
The Kerykeion library provides comprehensive transit calculation support and automatic house assignment:

```python
from kerykeion import AstrologicalSubject, KerykeionChartSVG
from transits import TransitsCalculator
from datetime import datetime

# Create natal chart with automatic house assignment
natal = AstrologicalSubject("Person", 1990, 10, 9, 14, 30, "New York", "US")

# Access planet house information
for planet_name in ['sun', 'moon', 'mercury', 'venus', 'mars']:
    planet = getattr(natal, planet_name)
    house_num = ['First_House', 'Second_House', 'Third_House', 'Fourth_House', 
                 'Fifth_House', 'Sixth_House', 'Seventh_House', 'Eighth_House',
                 'Ninth_House', 'Tenth_House', 'Eleventh_House', 'Twelfth_House'].index(planet.house) + 1
    print(f"{planet_name.capitalize()}: {planet.sign} {planet.sign_num}° - House {house_num}")

# Calculate current transits
calculator = TransitsCalculator(natal)
current_transits = calculator.calculate_transit_for_date(datetime.now())

# Generate transit chart SVG
chart_path = calculator.generate_transit_chart_svg(datetime.now())
```

### Transit Interpretation Guidelines
- **Personal Planets**: Daily life, immediate concerns.
- **Social Planets** (Jupiter/Saturn): Life direction, major changes.
- **Transpersonal Planets** (Uranus/Neptune/Pluto): Soul-level transformation.
- **Hard Aspects**: Challenges, growth opportunities.
- **Soft Aspects**: Support, natural flow.
- **Free Will**: Transits show potentials, not destiny.

## Tools and Libraries
- **Swiss Ephemeris**: High-precision, covers 13,000 BC to 17,000 AD.
- **pyswisseph**: Python interface for Swiss Ephemeris.
- **Kerykeion**: Complete astrology library with transit support.
- **Astropy**: For astronomical calculations in Python.
- Online calculators: Astro.com, Astro-Seek (for verification).

## Considerations
- Precision: Errors in time/location can shift ASC by degrees.
- DST and Time Changes: Historical DST rules may affect old charts.
- House Assignment: Planets are assigned to houses based on ecliptical longitude ranges between cusps.
- Cusp Detection: Planets within 2° of house boundaries exhibit cusp characteristics and are specially marked.
- Software: Always verify against multiple sources.

## References
- Wikipedia: Astrological Houses, Ascendant, Astrological Transit.
- Swiss Ephemeris Documentation.
- Astronomical Algorithms by Jean Meeus.
- Kerykeion Documentation: https://github.com/g-battaglia/kerykeion