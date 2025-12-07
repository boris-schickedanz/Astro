"""
Command Line Interface module for the Astro project.

This module handles command-line argument parsing and provides a clean interface
for user input to the astrological calculation system.
"""

import argparse
from typing import Any, Dict
from datetime import datetime
from kerykeion import AstrologicalSubject
import pytz
import config


class CLIParser:
    """
    Command line interface parser for astrological calculations.

    Handles argument parsing and validation for birth chart and transit calculations.
    """

    def __init__(self):
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create and configure the argument parser."""
        parser = argparse.ArgumentParser(
            description='Calculate astrological charts and transits',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  Natal chart:
    python main.py natal --name "John Doe" --year 1990 --month 6 --day 15 --hour 14 --minute 30 --city "New York" --nation "US"
    python main.py natal --name "Jane Smith" --year 1985 --month 3 --day 22 --hour 9 --minute 45 --city "London" --nation "GB" --transit-date "2024-01-15"

  Collective chart:
    python main.py collective --city "New York" --nation "US" --date "2024-01-15" --hour 12
    python main.py collective --city "London" --nation "GB"  # Uses current time
            """
        )

        subparsers = parser.add_subparsers(dest='command', help='Available commands')

        # Natal chart command
        natal_parser = subparsers.add_parser('natal', help='Calculate natal chart and transits')
        natal_parser.add_argument('--name', required=True, help='Name of the person')
        natal_parser.add_argument('--year', type=int, required=True, help='Birth year')
        natal_parser.add_argument('--month', type=int, required=True, help='Birth month (1-12)')
        natal_parser.add_argument('--day', type=int, required=True, help='Birth day')
        natal_parser.add_argument('--hour', type=int, help='Birth hour (0-23)')
        natal_parser.add_argument('--minute', type=int, help='Birth minute (0-59)')
        natal_parser.add_argument('--city', required=True, help='Birth city')
        natal_parser.add_argument('--nation', required=True, help='Birth nation/country code')

        # Optional arguments for natal
        natal_parser.add_argument('--lng', type=float, help='Birth longitude (optional, will be looked up if not provided)')
        natal_parser.add_argument('--lat', type=float, help='Birth latitude (optional, will be looked up if not provided)')
        natal_parser.add_argument('--tz', help='Timezone string (optional, will be looked up if not provided)')

        # Transit-specific arguments for natal
        natal_parser.add_argument('--transit-city', help='City for transit calculations (defaults to birth city)')
        natal_parser.add_argument('--transit-nation', help='Nation for transit calculations (defaults to birth nation)')
        natal_parser.add_argument('--transit-date', help='Date for transit calculations (YYYY-MM-DD format, defaults to current date)')
        natal_parser.add_argument('--transit-hour', type=int, default=12, help='Hour for transit calculations (defaults to 12)')

        # Collective chart command
        collective_parser = subparsers.add_parser('collective', help='Calculate collective chart for a location and time')
        collective_parser.add_argument('--city', required=True, help='City for the collective chart')
        collective_parser.add_argument('--nation', required=True, help='Nation/country code for the collective chart')
        collective_parser.add_argument('--date', help='Date for the collective chart (YYYY-MM-DD format, defaults to current date)')
        collective_parser.add_argument('--hour', type=int, help='Hour for the collective chart (optional)')
        collective_parser.add_argument('--minute', type=int, help='Minute for the collective chart (optional)')

        # Optional arguments for collective
        collective_parser.add_argument('--lng', type=float, help='Longitude (optional, will be looked up if not provided)')
        collective_parser.add_argument('--lat', type=float, help='Latitude (optional, will be looked up if not provided)')
        collective_parser.add_argument('--tz', help='Timezone string (optional, will be looked up if not provided)')

        return parser

    def parse_args(self) -> argparse.Namespace:
        """Parse command line arguments."""
        return self.parser.parse_args()

    def get_transit_datetime(self, args: argparse.Namespace) -> datetime:
        """
        Get the transit datetime from arguments.

        Args:
            args: Parsed command line arguments

        Returns:
            DateTime for transit calculations

        Raises:
            ValueError: If transit date format is invalid
        """
        if args.command == 'natal':
            if args.transit_date:
                try:
                    transit_datetime = datetime.strptime(args.transit_date, '%Y-%m-%d')
                    transit_datetime = transit_datetime.replace(hour=args.transit_hour)
                except ValueError:
                    raise ValueError("Invalid transit date format. Use YYYY-MM-DD")
            else:
                # Use current local time at transit location
                transit_city = args.transit_city or args.city
                transit_nation = args.transit_nation or args.nation
                transit_location = f"{transit_city}, {transit_nation}"

                try:
                    # Create a temporary chart to get timezone info for the transit location
                    temp_chart = AstrologicalSubject(
                        "Temp",
                        2025, 1, 1, 12, 0,  # dummy date/time
                        transit_city,
                        transit_nation,
                        geonames_username=config.GEONAMES_USERNAME
                    )
                    location_tz = pytz.timezone(temp_chart.tz_str)
                    transit_datetime = datetime.now(pytz.UTC).astimezone(location_tz)
                except Exception:
                    # Fallback to system local time if timezone lookup fails
                    transit_datetime = datetime.now()
        elif args.command == 'collective':
            if args.date:
                try:
                    transit_datetime = datetime.strptime(args.date, '%Y-%m-%d')
                    if args.hour is not None:
                        transit_datetime = transit_datetime.replace(hour=args.hour, minute=args.minute or 0)
                    else:
                        # Use current time on the given date
                        current = datetime.now()
                        transit_datetime = transit_datetime.replace(hour=current.hour, minute=current.minute)
                except ValueError:
                    raise ValueError("Invalid date format. Use YYYY-MM-DD")
            else:
                # Use current local time at the collective location
                try:
                    temp_chart = AstrologicalSubject(
                        "Temp",
                        2025, 1, 1, 12, 0,  # dummy date/time
                        args.city,
                        args.nation,
                        geonames_username=config.GEONAMES_USERNAME
                    )
                    location_tz = pytz.timezone(temp_chart.tz_str)
                    transit_datetime = datetime.now(pytz.UTC).astimezone(location_tz)
                except Exception:
                    transit_datetime = datetime.now()

        else:
            # Default fallback
            transit_datetime = datetime.now()

        return transit_datetime

    def get_transit_location(self, args: argparse.Namespace) -> str:
        """
        Get the transit location string from arguments.

        Args:
            args: Parsed command line arguments

        Returns:
            Location string for transit calculations
        """
        if args.command == 'natal':
            transit_city = args.transit_city or args.city
            transit_nation = args.transit_nation or args.nation
        elif args.command == 'collective':
            transit_city = args.city
            transit_nation = args.nation
        else:
            transit_city = "Greenwich"
            transit_nation = "GB"
        return f"{transit_city}, {transit_nation}"


def create_chart_from_args(args: argparse.Namespace) -> AstrologicalSubject:
    """
    Create an AstrologicalSubject from parsed command line arguments.

    Args:
        args: Parsed command line arguments

    Returns:
        AstrologicalSubject instance

    Raises:
        Exception: If chart creation fails
    """
    try:
        if args.command == 'natal':
            hour = args.hour if args.hour is not None else 0
            minute = args.minute if args.minute is not None else 0
            chart = AstrologicalSubject(
                name=args.name,
                year=args.year,
                month=args.month,
                day=args.day,
                hour=hour,
                minute=minute,
                lng=args.lng,
                lat=args.lat,
                tz_str=args.tz,
                city=args.city,
                nation=args.nation,
                geonames_username=config.GEONAMES_USERNAME
            )
        elif args.command == 'collective':
            # For collective, we need to get the datetime first
            cli_parser = CLIParser()
            chart_datetime = cli_parser.get_transit_datetime(args)
            chart = AstrologicalSubject(
                name=f"Collective Chart {args.city}",
                year=chart_datetime.year,
                month=chart_datetime.month,
                day=chart_datetime.day,
                hour=chart_datetime.hour,
                minute=chart_datetime.minute,
                lng=args.lng,
                lat=args.lat,
                tz_str=args.tz,
                city=args.city,
                nation=args.nation,
                geonames_username=config.GEONAMES_USERNAME
            )
        else:
            raise ValueError(f"Unknown command: {args.command}")
        return chart
    except Exception as e:
        raise Exception(f"Error creating chart: {e}")