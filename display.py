"""
Transit display module for the Astro project.

This module handles the display and formatting of transit calculations,
including current transits, long-term transits, and planetary positions.
"""

from typing import Dict, Any, List
from datetime import datetime
from models import ASPECT_SYMBOLS


class TransitDisplay:
    """
    Handles the display and formatting of transit information.

    This class provides methods to display various transit-related information
    including current transits, planetary positions, and long-term transit cycles.
    """

    def __init__(self, natal_chart_name: str, transit_location: str, transit_datetime: datetime, has_time: bool = True, natal_chart=None):
        """
        Initialize the transit display.

        Args:
            natal_chart_name: Name from the natal chart
            transit_location: Location string for transit calculations
            transit_datetime: DateTime for transit calculations
            has_time: Whether natal time was provided (affects house displays)
            natal_chart: The natal chart object (optional)
        """
        self.natal_name = natal_chart_name
        self.transit_location = transit_location
        self.transit_datetime = transit_datetime
        self.has_time = has_time
        self.natal_chart = natal_chart

    def display_transit_header(self, transits: Dict[str, Any]) -> None:
        """Display the transit calculation header."""
        time_description = f"on {self.transit_datetime.strftime('%Y-%m-%d %H:%M')}"
        print(f"\nTransits for {self.natal_name} {time_description} at {self.transit_location}")
        print(f"Number of active transit aspects: {len(transits['aspects'])}")
        print(f"Number of significant transits (orb ≤ 3°): {len(transits['significant_transits'])}")

    def display_significant_transits(self, significant_transits: List[Dict[str, Any]]) -> None:
        """Display the most significant current transits."""
        print("\nSignificant Transits:")
        for i, transit in enumerate(significant_transits[:10], 1):
            print(f"{i}. {transit['transit_planet']} {transit['aspect']} natal {transit['natal_planet']} (orb: {transit['orb']}°)")

    def display_current_planetary_positions(self, transit_planets: Dict[str, Dict[str, Any]],
                                          house_dates: Dict[str, Dict[str, Any]]) -> None:
        """Display current planetary positions in natal houses."""
        if self.has_time:
            print("\nCurrent Planetary Positions (in natal houses):")
        else:
            print("\nCurrent Planetary Positions:")

        for planet_name in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']:
            if planet_name in transit_planets:
                planet_data = transit_planets[planet_name]
                retrograde = " (R)" if planet_data['retrograde'] else ""

                if self.has_time:
                    house_num = planet_data.get('natal_house', 0)
                    # Get house date info
                    house_info = house_dates.get(planet_name, {})
                    entry_date = house_info.get('entry_date', 'Unknown')
                    exit_date = house_info.get('exit_date', 'Unknown')
                    days_in_house = house_info.get('days_in_house', 0)

                    date_range = f" ({entry_date} to {exit_date}"
                    if days_in_house > 0:
                        weeks = days_in_house // 7
                        remaining_days = days_in_house % 7
                        if weeks > 0:
                            date_range += f", {weeks}w {remaining_days}d"
                        else:
                            date_range += f", {days_in_house}d"
                    date_range += ")"

                    print(f"{planet_name}: {planet_data['sign']} {planet_data['sign_num']}° - House {house_num}{retrograde}{date_range}")
                else:
                    print(f"{planet_name}: {planet_data['sign']} {planet_data['sign_num']}°{retrograde}")

    def display_natal_houses(self) -> None:
        """Display natal house cusps if available."""
        if self.has_time and self.natal_chart and hasattr(self.natal_chart, 'houses_list'):
            print("\nNatal Houses:")
            for i in range(1, 13):
                house = self.natal_chart.houses_list[i-1]
                print(f"House {i}: {house.sign} {house.signlon}°")

    def display_long_term_transits_header(self, base_date: datetime) -> None:
        """Display the long-term transits header."""
        print("\n" + "="*50)
        print("SIGNIFICANT LONG-TERM TRANSITS")
        print("="*50)
        print(f"Focus date: {base_date.strftime('%B %d, %Y')}")
        print("Showing: Jupiter, Saturn, Uranus, Neptune, Pluto transits")
        print("Timeframe: Past 2 years | Active Now | Next 10 years")

    def display_active_long_term_transits(self, active_transits: List[Dict[str, Any]]) -> None:
        """Display currently active long-term transits."""
        if not active_transits:
            print("\nNo currently active long-term transits")
            return

        print(f"\n{'━' * 60}")
        print(f"CURRENTLY ACTIVE ({len(active_transits)} transit{'s' if len(active_transits) != 1 else ''}):")
        print(f"{'━' * 60}")

        for i, transit in enumerate(active_transits, 1):
            # Get aspect symbol
            symbol = ASPECT_SYMBOLS.get(transit['aspect'], '')

            print(f"\n{i}. {transit['transit_planet']} {transit['aspect']} natal {transit['natal_planet']} {symbol}")
            print(f"   Status: Active ({transit['progress_percent']}% complete)")
            print(f"   Period: {transit['start_date']} to {transit['end_date']} ({transit['duration_months']} months)")
            print(f"   {transit['transit_planet']} at {transit['transit_position']}, Natal {transit['natal_planet']} at {transit['natal_position']}")
            print(f"   Tightest orb: {transit['min_orb']}°")

            # Show number of passes if multiple (indicates retrograde pattern)
            passes = transit.get('passes', [])
            if isinstance(passes, list) and len(passes) > 1:
                print(f"   Note: Transit has {len(passes)} passes (retrograde pattern)")

    def display_recent_long_term_transits(self, recent_past: List[Dict[str, Any]]) -> None:
        """Display recently completed long-term transits."""
        if not recent_past:
            return

        print(f"\n{'━' * 60}")
        print(f"RECENTLY COMPLETED (Past 2 years):")
        print(f"{'━' * 60}")

        for transit in recent_past:
            # Get aspect symbol
            symbol = ASPECT_SYMBOLS.get(transit['aspect'], '')
            
            days_ago = transit.get('days_ago', 0)
            months_ago = round(days_ago / 30.44, 1)
            time_desc = f"{months_ago} months ago" if months_ago >= 1 else f"{days_ago} days ago"
            
            print(f"\n{transit['transit_planet']}:")
            print(f"  {transit['aspect']} natal {transit['natal_planet']} {symbol}")
            print(f"  {transit['start_date']} to {transit['end_date']} ({transit['duration_months']} months)")
            print(f"  {transit['transit_planet']} at {transit['transit_position']}, Natal {transit['natal_planet']} at {transit['natal_position']}")
            print(f"  Tightest orb: {transit['min_orb']}°")
            print(f"  Ended {time_desc}")
            
            # Show number of passes if multiple (indicates retrograde pattern)
            passes = transit.get('passes', [])
            if isinstance(passes, list) and len(passes) > 1:
                print(f"  Note: Transit had {len(passes)} passes (retrograde pattern)")

    def display_upcoming_long_term_transits(self, upcoming: List[Dict[str, Any]]) -> None:
        """Display upcoming long-term transits."""
        if not upcoming:
            return

        print(f"\n{'━' * 60}")
        print(f"UPCOMING (Next 10 years):")
        print(f"{'━' * 60}")

        for transit in upcoming:
            # Get aspect symbol
            symbol = ASPECT_SYMBOLS.get(transit['aspect'], '')
            
            days_until = transit.get('days_until', 0)
            months_until = round(days_until / 30.44, 1)
            time_desc = f"{months_until} months" if months_until >= 1 else f"{days_until} days"
            
            print(f"\n{transit['transit_planet']}:")
            print(f"  {transit['aspect']} natal {transit['natal_planet']} {symbol}")
            print(f"  {transit['start_date']} to {transit['end_date']} ({transit['duration_months']} months)")
            print(f"  {transit['transit_planet']} at {transit['transit_position']}, Natal {transit['natal_planet']} at {transit['natal_position']}")
            print(f"  Tightest orb: {transit['min_orb']}°")
            print(f"  Starts in {time_desc}")
            
            # Show number of passes if multiple (indicates retrograde pattern)
            passes = transit.get('passes', [])
            if isinstance(passes, list) and len(passes) > 1:
                print(f"  Note: Transit will have {len(passes)} passes (retrograde pattern)")

    def display_no_long_term_transits_message(self) -> None:
        """Display message when no long-term transits are found."""
        print("\nNo significant long-term transits found in the specified timeframe.")
        print("This could mean you're in a quieter astrological period regarding outer planet transits.")

    def display_transit_footer(self) -> None:
        """Display the transit explanation footer."""
        print("\nNote: Transits show how current planetary movements interact with your natal chart.")
        print("They indicate timing for opportunities, challenges, and life changes.")


def display_transits(natal_chart_name: str, transit_location: str, transit_datetime: datetime,
                   transits: Dict[str, Any], house_dates: Dict[str, Dict[str, Any]], has_time: bool = True,
                   natal_chart=None) -> None:
    """
    Display complete transit information.

    Args:
        natal_chart_name: Name from the natal chart
        transit_location: Location for transit calculations
        transit_datetime: DateTime for transit calculations
        transits: Transit calculation results
        house_dates: House transit date information
        has_time: Whether natal time was provided
        natal_chart: The natal chart object
    """
    display = TransitDisplay(natal_chart_name, transit_location, transit_datetime, has_time, natal_chart)
    display.display_transit_header(transits)
    display.display_significant_transits(transits['significant_transits'])
    display.display_current_planetary_positions(transits['transit_planets'], house_dates)
    display.display_natal_houses()
    display.display_transit_footer()


def display_long_term_transits(base_date: datetime, long_term_transits: Dict[str, Any]) -> None:
    """
    Display long-term transit information.

    Args:
        base_date: Base date for the transit calculations
        long_term_transits: Long-term transit calculation results
    """
    display = TransitDisplay("", "", base_date, True)
    display.display_long_term_transits_header(base_date)
    display.display_active_long_term_transits(long_term_transits.get('active', []))
    display.display_recent_long_term_transits(long_term_transits.get('recent_past', []))
    display.display_upcoming_long_term_transits(long_term_transits.get('upcoming', []))

    if not (long_term_transits.get('active') or long_term_transits.get('recent_past') or long_term_transits.get('upcoming')):
        display.display_no_long_term_transits_message()