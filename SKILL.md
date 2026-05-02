---
name: astro-reading
description: Compute astrological readings from this project's Python calculation core (no MCP needed). Use when the user asks for a birth chart, current transits, "what's happening for me now", solar return, annual profection, long-term outer-planet transits, or a full reading. Wraps kerykeion / Swiss Ephemeris and adds house-residency, long-term cycle, profection, solar return, and chart-balance analysis on top.
---

# Astro reading skill

This project produces three "blocks":

1. **Natal block** — planets, points, houses, natal aspects (orb ≤ 4°), element/modality/hemisphere balance, chart ruler, stelliums (sign and house), active annual profection.
2. **Predictions block** — current transit aspects to natal (orb ≤ 3°), transit planets in natal houses with entry/exit dates, long-term outer-planet transits (defaults: 2y back / 10y forward), solar return for the current year.
3. **Full reading** — both blocks, in the CLI's order.

The MCP server in `mcp_server.py` is one entry point. This skill covers the other two: the CLI and direct Python imports.

## Environment

```bash
source .venv/bin/activate
# or invoke directly:
.venv/bin/python <script>
```

Required: `GEONAMES_USERNAME` in a `.env` at the project root (loaded by `config.py`). Without it, city/nation resolution fails or behaves unpredictably. The project uses a `cache/` directory at the root to cache geonames lookups — create it if missing (`mkdir -p cache`).

## Quickest path — CLI (full reading)

```bash
.venv/bin/python main.py --name "John Doe" \
  --year 1990 --month 6 --day 15 --hour 14 --minute 30 \
  --city "New York" --nation "US"
```

- Omit `--hour` and `--minute` for a timeless chart (see "Timeless-chart fork" below).
- Add `--current-city "Berlin" --current-nation "DE"` to anchor "now" and the solar-return chart somewhere other than the birth city.

The CLI always prints the full reading. For just the natal half or just the predictions half, use the Python snippets below.

## Programmatic — natal block only

```python
from datetime import date
from kerykeion import AstrologicalSubject
import config
from analysis_display import (
    display_balance, display_chart_ruler, display_profection, display_stelliums,
)
from chart import display_natal_chart
from chart_analysis import (
    chart_ruler, compute_element_balance, compute_hemispheres,
    compute_modality_balance, find_stelliums,
)
from profection import compute_profection

chart = AstrologicalSubject(
    name="John Doe", year=1990, month=6, day=15, hour=14, minute=30,
    city="New York", nation="US",
    geonames_username=config.GEONAMES_USERNAME,
)
has_time = True  # set False if hour/minute were not supplied

display_natal_chart(chart, has_time)
display_balance(
    compute_element_balance(chart),
    compute_modality_balance(chart),
    compute_hemispheres(chart) if has_time else None,
)
if has_time:
    display_chart_ruler(chart_ruler(chart))
display_stelliums(find_stelliums(chart, has_time=has_time))
if has_time:
    display_profection(compute_profection(chart, date.today()))
```

## Programmatic — predictions block only

```python
from kerykeion import AstrologicalSubject
import config
from analysis_display import display_solar_return
from display import display_long_term_transits, display_transits
from solar_return import calculate_solar_return
from transits import TransitsCalculator, now_at_location

chart = AstrologicalSubject(
    name="John Doe", year=1990, month=6, day=15, hour=14, minute=30,
    city="New York", nation="US",
    geonames_username=config.GEONAMES_USERNAME,
)
has_time = True

current_city, current_nation = "Berlin", "DE"  # or birth city/nation
location = f"{current_city}, {current_nation}"
transit_datetime = now_at_location(location)  # ONE anchor for the whole flow

calc = TransitsCalculator(chart)
transits = calc.calculate_transit_for_date(transit_datetime, location)
house_dates = calc.calculate_planet_house_dates(transit_datetime, location)
display_transits(chart.name, location, transit_datetime,
                 transits, house_dates, has_time, chart)

long_term = calc.calculate_long_term_transits(
    transit_datetime, years_before=2, years_after=10,
)
display_long_term_transits(transit_datetime, long_term)

sr = calculate_solar_return(chart, transit_datetime.year,
                            current_city, current_nation)
display_solar_return(sr)
```

## Parameter semantics

| Parameter | Notes |
|-----------|-------|
| `name` | Header label only. Not used for any lookup or astrological math. |
| `year`, `month`, `day` | Gregorian birth date in **local civil time of the birth city** (not UTC). |
| `hour`, `minute` | Local civil time, 24h. If either is omitted, see "Timeless-chart fork". |
| `city`, `nation` | City name + ISO 3166-1 alpha-2 country code. Resolved via geonames (network call). |
| `lat`, `lng`, `tz_str` | Optional override triple to bypass geonames. `tz_str` MUST be an IANA name (`"Europe/Berlin"`), not a UTC offset — needed for historical DST handling. |
| `current_city`, `current_nation` | Where the user lives NOW. Affects ONLY (a) the timezone used to resolve "today" for transits/profection/SR year, and (b) the solar-return chart's ASC and house cusps. Transit-aspect math itself is location-independent. Defaults to the birth city/nation. |

## Timeless-chart fork

If `hour` or `minute` is omitted, the chart is timeless and the following are suppressed everywhere:

- ASC, MC, house cusps, planet-in-house placements
- Hemisphere balance, chart ruler
- Annual profection
- House-based stelliums

Sign placements, sign-based stelliums, transit aspects, and long-term outer transits still work. Thread `has_time` through `display_natal_chart`, `find_stelliums`, `display_transits`, etc. — kerykeion populates `planet.house` even on a synthetic 00:00 chart, so the chart object alone can't tell you whether houses are meaningful.

## Critical pattern — one `transit_datetime` per flow

Resolve `transit_datetime = now_at_location(location)` ONCE at the top of the predictions flow and reuse it for every downstream call (header, house-residency anchor, long-term focus date, profection date, SR year). Calling `datetime.now()` partway through desynchronizes from the location's timezone and gives inconsistent dates across sections.

## Output format

Every entry point prints **human-readable text to stdout**. There is no JSON / structured-data output.

To hand a result to a downstream LLM or store it as a string, capture stdout — the canonical pattern is in `mcp_server.py:_capture`:

```python
import io, sys
from contextlib import contextmanager

@contextmanager
def capture_stdout():
    buf = io.StringIO()
    old, sys.stdout = sys.stdout, buf
    try:
        yield buf
    finally:
        sys.stdout = old

with capture_stdout() as out:
    display_natal_chart(chart, has_time)
text = out.getvalue()
```

## Choosing the right block

- User asks "who am I astrologically", "what's my chart", "what's my rising sign / chart ruler / dominant element", "what's my profection year" → **natal block**.
- User asks "what's happening for me now / soon", "what transits am I under", "when does Saturn finish in my 7th", "what's my solar return this year" → **predictions block**.
- First-time reading, or user wants the whole picture in one shot → **full reading** (CLI is fine).

Prefer the narrower block when only one half is needed — predictions skip a multi-year ephemeris scan that the natal block never runs, and natal skips the SR search.

## When NOT to use this skill

- Pure ephemeris lookup (planet positions on a date with no interpretation) — `kerykeion` or `pyswisseph` directly is simpler.
- Synastry, composite charts, transit-to-transit aspects, secondary progressions, solar arc — not implemented here.
- Traditional/Hellenistic rulership systems beyond annual profection — only modern rulerships are wired in (see `SIGN_TO_RULER` in `chart_analysis.py`).

## Reference

- `.github/birth_chart_calculation.md` — authoritative project reference for ASC/house/planet-position math.
- `CLAUDE.md` — architecture overview (calculation core vs. display layers, the four specialized calculators under `TransitsCalculator`, etc.).
