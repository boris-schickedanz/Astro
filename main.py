"""
Main entry point. Single command, full reading.

Output sections (in order):
  1. Natal chart      — basic info, planets, additional points, houses
  2. Chart analysis   — element/modality/hemisphere balance, chart ruler, stelliums
  3. Natal aspects    — pairwise natal aspects (orb ≤ 4°)
  4. Annual profection — active house + year lord
  5. Current transits — significant transit aspects, transit planets in natal houses
  6. Long-term transits — outer-planet active / past / upcoming
  7. Solar return     — for current year, cast at current location
"""

from cli import CLIParser, create_chart_from_args
from chart import display_natal_chart
from chart_analysis import (
    chart_ruler,
    compute_element_balance,
    compute_hemispheres,
    compute_modality_balance,
    find_stelliums,
)
from analysis_display import (
    display_balance,
    display_chart_ruler,
    display_profection,
    display_solar_return,
    display_stelliums,
)
from display import display_long_term_transits, display_transits
from profection import compute_profection
from solar_return import calculate_solar_return
from transits import TransitsCalculator, now_at_location


def main() -> None:
    args = CLIParser().parse_args()

    has_time = args.hour is not None and args.minute is not None
    chart = create_chart_from_args(args)

    current_city = args.current_city or args.city
    current_nation = args.current_nation or args.nation
    location = f"{current_city}, {current_nation}"

    display_natal_chart(chart, has_time)

    display_balance(
        compute_element_balance(chart),
        compute_modality_balance(chart),
        compute_hemispheres(chart) if has_time else None,
    )
    if has_time:
        display_chart_ruler(chart_ruler(chart))
    display_stelliums(find_stelliums(chart, has_time=has_time))

    # Single anchor for header, house dates, long-term focus, profection, SR year.
    transit_datetime = now_at_location(location)

    if has_time:
        display_profection(compute_profection(chart, transit_datetime.date()))

    print("\n" + "=" * 50)
    print("TRANSITS CALCULATION")
    print("=" * 50)
    transit_calculator = TransitsCalculator(chart)
    transits = transit_calculator.calculate_transit_for_date(transit_datetime, location)
    house_dates = transit_calculator.calculate_planet_house_dates(transit_datetime, location)
    display_transits(chart.name, location, transit_datetime, transits, house_dates, has_time, chart)

    long_term = transit_calculator.calculate_long_term_transits(
        transit_datetime, years_before=2, years_after=10, location=location
    )
    display_long_term_transits(transit_datetime, long_term)

    sr = calculate_solar_return(chart, transit_datetime.year, current_city, current_nation)
    display_solar_return(sr)


if __name__ == "__main__":
    main()
