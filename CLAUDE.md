# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

```bash
source .venv/bin/activate
# or invoke directly:
.venv/bin/python <script>
```

`kerykeion` performs network lookups against geonames for city/timezone resolution. A `.env` file in the project root must define `GEONAMES_USERNAME=...` (loaded by `config.py`); without it, location-based chart creation fails or falls back unpredictably. A `cache/` directory at the project root holds kerykeion's geonames cache; the MCP server creates it on startup with `os.makedirs("cache", exist_ok=True)`.

## Commands

```bash
# Single CLI command — produces the full reading.
.venv/bin/python main.py --name "John Doe" --year 1990 --month 6 --day 15 \
    --hour 14 --minute 30 --city "New York" --nation "US"

# Solar return cast at a different "current" location:
.venv/bin/python main.py ... --current-city "Berlin" --current-nation "DE"

# Tests
.venv/bin/python -m pytest
.venv/bin/python -m pytest tests/test_chart.py
.venv/bin/python -m pytest tests/test_chart.py::test_ascendant_calculation -v

# MCP server (FastMCP). Three tools: calculate_natal_chart,
# calculate_transits, calculate_full_reading.
.venv/bin/python mcp_server.py
```

The CLI is a single command (no subparsers). Birth args are required; `--current-city` / `--current-nation` default to the birth city/nation and only affect (a) the timezone used to anchor "now" for transits/SR and (b) the solar-return chart's ASC/houses.

## What the tool produces

Each run prints, in order:

1. **Natal chart** — basic info, planets, additional points (Node, Lilith, Chiron, Lot of Fortune), house cusps.
2. **Natal aspects** — pairwise via kerykeion's `NatalAspects`, orb ≤ 4° (printed inside `display_natal_chart`).
3. **Chart analysis** — element/modality counts, hemisphere/quadrant split, chart ruler, stelliums (sign and house, ≥ 3 planets).
4. **Annual profection** — active house and year lord for current age (Hellenistic; modern rulerships).
5. **Current transits** — top-10 significant transit aspects (orb ≤ 3°) + transit planets in natal houses with entry/exit dates.
6. **Long-term transits** — outer-planet aspects (Jupiter–Pluto) to natal, bucketed Active / Recently completed (last per planet) / Upcoming (next per planet, defaults: 2 years back, 10 years forward).
7. **Solar return** — exact UTC moment Sun returns to natal longitude in the current year, chart cast at `current_city`. Reports SR ASC/MC, Sun/Moon placements (sign + degree + SR house), SR chart ruler.

Transit aspects are location-independent (zodiac math); the only place "current location" matters astrologically is the solar-return chart's ASC/houses. The same location is also used to resolve "now" in the right timezone — a single `transit_datetime` is computed once and threaded through every section so the header, house anchor, long-term focus date, profection date, and SR year stay consistent.

## Architecture

The codebase wraps `kerykeion` (which wraps Swiss Ephemeris via `pyswisseph`) and layers transit, house-residency, long-term cycle, profection, solar return, and chart-balance analysis on top. All output is text only.

### Entry points

- `main.py` — single-command CLI. Resolves `transit_datetime = now_at_location(location)` once, then walks each section.
- `mcp_server.py` — FastMCP server exposing three tools (`calculate_natal_chart`, `calculate_transits`, `calculate_full_reading`). The display layer prints rather than returning strings, so the tools wrap calls in a `_capture()` context manager that redirects `sys.stdout` to a `StringIO` and returns its contents — this is the integration seam.
- `tests/` — pytest suites that exercise the calculation core directly.

### Calculation core

`transits.TransitsCalculator` orchestrates four specialized calculators — keep this separation when extending:

- `transit_aspects.TransitAspectCalculator` — pairwise transit↔natal aspects via kerykeion's `SynastryAspects`. Uses `models.TRANSIT_ACTIVE_ASPECTS` (orbs 6–10°) for the general case and `models.LONG_TERM_ACTIVE_ASPECTS` (tight 1–2°) for outer-planet work.
- `house_transits.HouseTransitCalculator` — which natal house each transit planet currently occupies, plus entry/exit dates. Day-by-day search constructs many temporary `AstrologicalSubject` instances; step sizes vary by planet speed (1d for Sun..Mars, 7d for Jupiter/Saturn, 30d for Uranus/Neptune/Pluto).
- `long_term_transits.LongTermTransitCalculator` — outer-planet aspects across a multi-year window, monthly ephemeris sampling with retrograde re-entries merged into single periods.
- `transit_data.TransitDataFormatter` — shapes raw kerykeion planet objects into the dicts the display layer consumes.

`chart_analysis.py`, `profection.py`, and `solar_return.py` are independent of `TransitsCalculator`; each operates on a plain `AstrologicalSubject`.

### Solar return

`solar_return.py` finds the SR moment via `pyswisseph` directly: hour-step scan around the natal birthday in the target year for a sign change in `Sun_lon - natal_Sun_lon`, then bisection to ~1-second precision. `_jd_to_datetime` uses `datetime(...) + timedelta(seconds=round(hour_frac * 3600))` so any rounding carry rolls over correctly through hour/day boundaries.

When the SR location matches the natal chart's `(city, nation)`, the calculator reuses `natal_chart.lat / lng / tz_str` directly instead of building a throwaway "locator" chart — this is the common case for the CLI run with no `--current-city` override and saves one geonames-resolving `AstrologicalSubject` construction. When locations differ, a locator is built once.

### Constants and shared data

`models.py` holds: `TRANSIT_ACTIVE_POINTS`, `TRANSIT_ACTIVE_ASPECTS`, `OUTER_PLANET_POINTS`, `LONG_TERM_ACTIVE_ASPECTS`, `NATAL_RELEVANT_PLANETS`, `HOUSE_NAMES`, `HOUSE_INDEX` (reverse map: kerykeion's `'Tenth_House'` → `10`), `HOUSE_PREFIXES`, `PLANET_NAMES`, `ADDITIONAL_POINTS`, `POINT_DISPLAY_NAMES`, `ASPECT_SYMBOLS`, plus `calculate_lot_of_fortune` and `get_zodiac_sign_from_position` helpers. Modify constants here rather than redefining in calling modules.

`chart_analysis.SIGN_TO_RULER` holds the modern sign-rulership table (used for both `chart_ruler` and `profection.compute_profection`'s year-lord lookup). `STELLIUM_MIN = 3` lives in the same module.

**Element / modality counts come from kerykeion attributes**, not local tables: `compute_element_balance` reads `planet.element` and `compute_modality_balance` reads `planet.quality`. Don't reintroduce hand-rolled `SIGN_TO_ELEMENT` / `SIGN_TO_MODALITY` dicts — they drift from kerykeion.

### Display layers

`chart.py` (natal display), `display.py` (transits + long-term display), and `analysis_display.py` (balance, ruler, stelliums, profection, solar return) are pure formatting — they print to stdout. No calculation logic belongs here. The MCP layer redirects stdout to capture each tool's output.

### "Local time at a location" pattern

Computing "now in city X's timezone" requires building a throwaway `AstrologicalSubject` to discover the timezone, then converting `datetime.now(pytz.UTC)` into it. The canonical helper is `transits.now_at_location(location)`. **Always resolve `transit_datetime` once at the top of a flow and reuse it** for the header, house-residency anchor, long-term focus date, profection date, and SR year — using `datetime.now()` mid-flow desynchronizes from the location's timezone. `transits.DEFAULT_LOCATION = "Greenwich, GB"` and `_split_location()` are the shared parsing helpers.

### `has_time` semantics

Without a birth time, ASC, MC, houses, house placements, hemispheres, chart ruler, profection, and house-stelliums are all undefined. The `has_time` boolean is threaded through chart creation → display → analysis to suppress those fields. Sign stelliums *are* still reported without a birth time (signs only need date). **Note:** kerykeion populates `planet.house` even on a synthetic 00:00 chart, so the chart object alone can't tell you whether houses are meaningful — `find_stelliums` requires `has_time` from the caller for this reason.

### Birth-chart calculation reference

`.github/birth_chart_calculation.md` is the project's authoritative reference for ASC/house/planet-position math. Follow it precisely when implementing or reviewing astrological calculations.

## Style and conventions

- Type hints on public functions; PEP 8.
- Use `models.HOUSE_INDEX[planet.house]` for kerykeion-house-string → int conversion. Don't rebuild the dict locally.
- Use kerykeion's `planet.element` and `planet.quality` directly. Don't reintroduce sign→element/modality tables.
- New functionality belongs to the existing per-concern modules — `transits.py` is an orchestrator, not a dumping ground.
- Tests live in `tests/` and follow `test_*.py` / `Test*` / `test_*` naming (per `pytest.ini`).
