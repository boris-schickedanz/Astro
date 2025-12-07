"""
Natal chart display module for the Astro project.

This module handles the creation and display of natal (birth) charts,
including planet positions, house cusps, and aspects.
"""

from typing import Dict, Any, List
from kerykeion import AstrologicalSubject, NatalAspects
from models import PLANET_NAMES, HOUSE_PREFIXES, HOUSE_NAMES, ADDITIONAL_POINTS, POINT_DISPLAY_NAMES, calculate_lot_of_fortune, get_zodiac_sign_from_position


class ChartDisplay:
    """
    Handles the display and formatting of natal chart information.

    This class provides methods to display various components of a natal chart
    including basic info, planets, houses, and aspects.
    """

    def __init__(self, chart: AstrologicalSubject, has_time: bool = True):
        """
        Initialize the chart display with a natal chart.

        Args:
            chart: The AstrologicalSubject to display
            has_time: Whether birth time was provided
        """
        self.chart = chart
        self.has_time = has_time

    def display_basic_info(self) -> None:
        """Display basic birth information."""
        print(f"Birth Chart for {self.chart.name}")
        print(f"Born: {self.chart.year}-{self.chart.month:02d}-{self.chart.day:02d} {self.chart.hour:02d}:{self.chart.minute:02d}")
        print(f"Location: {self.chart.city}, {self.chart.nation} ({self.chart.lat:.4f}, {self.chart.lng:.4f})")
        print(f"Timezone: {self.chart.tz_str}")
        
        if self.has_time:
            # Convert ASC and MC to degrees and minutes
            asc_degrees = int(self.chart.ascendant.position)
            asc_minutes = int((self.chart.ascendant.position - asc_degrees) * 60)
            mc_degrees = int(self.chart.medium_coeli.position)
            mc_minutes = int((self.chart.medium_coeli.position - mc_degrees) * 60)
            
            print(f"ASC: {self.chart.ascendant.sign} {asc_degrees}°{asc_minutes:02d}'")
            print(f"MC: {self.chart.medium_coeli.sign} {mc_degrees}°{mc_minutes:02d}'")

    def display_planets(self) -> None:
        """Display planet positions and house placements."""
        print("\nPlanets:")

        # Initialize variables
        house_dict = {}
        houses = []

        if self.has_time:
            # Create house mapping
            house_dict = {name: i+1 for i, name in enumerate(HOUSE_NAMES)}

            # Get house cusps
            for i in range(1, 13):
                house = getattr(self.chart, f"{HOUSE_PREFIXES[i-1]}_house")
                houses.append(house.abs_pos)

        for planet_name in PLANET_NAMES:
            planet = getattr(self.chart, planet_name)
            
            if self.has_time:
                house_num = house_dict.get(planet.house, 0)

                # Check if on cusp (within 2 degrees of house boundary)
                cusp_orb = 2
                house_start = houses[(house_num - 1) % 12]  # Start of current house
                house_end = houses[house_num % 12]  # End of current house (start of next house)

                dist_to_start = min(abs(planet.abs_pos - house_start), 360 - abs(planet.abs_pos - house_start))
                dist_to_end = min(abs(planet.abs_pos - house_end), 360 - abs(planet.abs_pos - house_end))

                house_info = f"House {house_num}"
                if dist_to_start <= cusp_orb or dist_to_end <= cusp_orb:
                    # Determine which boundary it's closer to
                    if dist_to_end <= dist_to_start:
                        # Closer to end of house (next house boundary)
                        next_house_num = house_num % 12 + 1
                        cusp_info = f" (cusp {house_num}/{next_house_num})"
                    else:
                        # Closer to start of house (previous house boundary)
                        prev_house_num = house_num - 1 if house_num > 1 else 12
                        cusp_info = f" (cusp {prev_house_num}/{house_num})"
                    house_info += cusp_info
            else:
                house_info = ""

            # Convert decimal degrees to degrees and minutes
            degrees = int(planet.position)
            minutes = int((planet.position - degrees) * 60)
            retrograde = " R" if planet.retrograde else ""

            house_part = f" - {house_info}" if house_info else ""
            print(f"{planet_name.capitalize()}: {planet.sign} {degrees}°{minutes:02d}'{retrograde}{house_part}")

    def display_additional_points(self) -> None:
        """Display additional celestial points (nodes, lilith, chiron, lot of fortune)."""
        print("\nAdditional Points:")

        house_dict = {}
        houses = []
        
        if self.has_time:
            # Create house mapping
            house_dict = {name: i+1 for i, name in enumerate(HOUSE_NAMES)}

            # Get house cusps
            houses = []
            for i in range(1, 13):
                house = getattr(self.chart, f"{HOUSE_PREFIXES[i-1]}_house")
                houses.append(house.abs_pos)

        for point_name in ADDITIONAL_POINTS:
            if not hasattr(self.chart, point_name):
                continue
                
            point = getattr(self.chart, point_name)
            
            if self.has_time:
                house_num = house_dict.get(point.house, 0)

                # Check if on cusp (within 2 degrees of house boundary)
                cusp_orb = 2
                house_start = houses[(house_num - 1) % 12]  # Start of current house
                house_end = houses[house_num % 12]  # End of current house (start of next house)

                dist_to_start = min(abs(point.abs_pos - house_start), 360 - abs(point.abs_pos - house_start))
                dist_to_end = min(abs(point.abs_pos - house_end), 360 - abs(point.abs_pos - house_end))

                house_info = f"House {house_num}"
                if dist_to_start <= cusp_orb or dist_to_end <= cusp_orb:
                    # Determine which boundary it's closer to
                    if dist_to_end <= dist_to_start:
                        # Closer to end of house (next house boundary)
                        next_house_num = house_num % 12 + 1
                        cusp_info = f" (cusp {house_num}/{next_house_num})"
                    else:
                        # Closer to start of house (previous house boundary)
                        prev_house_num = house_num - 1 if house_num > 1 else 12
                        cusp_info = f" (cusp {prev_house_num}/{house_num})"
                    house_info += cusp_info
            else:
                house_info = ""

            # Convert decimal degrees to degrees and minutes
            degrees = int(point.position)
            minutes = int((point.position - degrees) * 60)
            retrograde = " R" if point.retrograde else ""

            display_name = POINT_DISPLAY_NAMES.get(point_name, point_name.capitalize())
            house_part = f" - {house_info}" if house_info else ""
            print(f"{display_name}: {point.sign} {degrees}°{minutes:02d}'{retrograde}{house_part}")

        # Display Lot of Fortune
        lot_pos = calculate_lot_of_fortune(self.chart)
        lot_sign = get_zodiac_sign_from_position(lot_pos)
        sign_start = (['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                      'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'].index(lot_sign)) * 30
        degrees_in_sign = int(lot_pos - sign_start)
        minutes = int((lot_pos - sign_start - degrees_in_sign) * 60)

        if self.has_time:
            # Determine house for Lot of Fortune
            lot_house_num = 1
            for i, house_pos in enumerate(houses):
                next_house_pos = houses[(i + 1) % 12]
                if i == 11:  # Last house, check if between last house and first house
                    if house_pos <= lot_pos or lot_pos < next_house_pos:
                        lot_house_num = i + 1
                        break
                elif house_pos <= lot_pos < next_house_pos:
                    lot_house_num = i + 1
                    break

            # Check if on cusp
            house_start = houses[(lot_house_num - 1) % 12]
            house_end = houses[lot_house_num % 12]
            dist_to_start = min(abs(lot_pos - house_start), 360 - abs(lot_pos - house_start))
            dist_to_end = min(abs(lot_pos - house_end), 360 - abs(lot_pos - house_end))

            lot_house_info = f"House {lot_house_num}"
            if dist_to_start <= 2 or dist_to_end <= 2:
                if dist_to_end <= dist_to_start:
                    next_house_num = lot_house_num % 12 + 1
                    lot_house_info += f" (cusp {lot_house_num}/{next_house_num})"
                else:
                    prev_house_num = lot_house_num - 1 if lot_house_num > 1 else 12
                    lot_house_info += f" (cusp {prev_house_num}/{lot_house_num})"
        else:
            lot_house_info = ""

        lot_house_part = f" - {lot_house_info}" if lot_house_info else ""
        print(f"Lot of Fortune: {lot_sign} {degrees_in_sign}°{minutes:02d}'{lot_house_part}")

    def display_houses(self) -> None:
        """Display house cusp positions."""
        print("\nHouses:")
        for i in range(1, 13):
            house = getattr(self.chart, f"{HOUSE_PREFIXES[i-1]}_house")
            degrees = int(house.position)
            minutes = int((house.position - degrees) * 60)
            print(f"House {i}: {house.sign} {degrees}°{minutes:02d}'")

    def display_aspects(self) -> None:
        """Display aspects between planets."""
        print("\nAspects:")
        aspects = NatalAspects(self.chart)
        for aspect in aspects.all_aspects:
            if (abs(aspect.orbit) <= 4.0):  # Display aspects with orb <= 4 degrees
                print(f"{aspect.p1_name} {aspect.aspect} {aspect.p2_name} ({aspect.orbit:.1f}°)")


def display_natal_chart(chart: AstrologicalSubject, has_time: bool = True) -> None:
    """
    Display a complete natal chart.

    Args:
        chart: The natal chart to display
        has_time: Whether birth time was provided (affects house calculations)
    """
    display = ChartDisplay(chart, has_time)
    display.display_basic_info()
    display.display_planets()
    display.display_additional_points()
    if has_time:
        display.display_houses()
    display.display_aspects()