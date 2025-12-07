"""
Main entry point for the Astro project.

This module orchestrates the astrological calculation workflow by coordinating
between the CLI parser, chart creation, transit calculations, and display modules.
"""

from cli import CLIParser, create_chart_from_args
from chart import display_natal_chart
from transits import TransitsCalculator, calculate_current_transits
from kerykeion import AstrologicalSubject
import argparse
from display import display_transits, display_long_term_transits


def main():
    """Main application entry point."""
    # Parse command line arguments
    cli_parser = CLIParser()
    args = cli_parser.parse_args()

    if args.command == 'natal':
        # Handle natal chart
        handle_natal_chart(args, cli_parser)
    elif args.command == 'collective':
        # Handle collective chart
        handle_collective_chart(args, cli_parser)
    else:
        print("Error: Unknown command. Use 'natal' or 'collective'.")
        return


def handle_natal_chart(args: argparse.Namespace, cli_parser: CLIParser):
    """Handle natal chart calculation and display."""
    # Get transit parameters
    transit_datetime = cli_parser.get_transit_datetime(args)
    transit_location = cli_parser.get_transit_location(args)

    # Determine if time was provided
    has_time = args.hour is not None and args.minute is not None

    # Create the natal chart
    chart = create_chart_from_args(args)

    # Display the natal chart
    display_natal_chart(chart, has_time)

    print("\n" + "="*50)
    print("TRANSITS CALCULATION")
    print("="*50)

    # Calculate and display transits
    transit_calculator = TransitsCalculator(chart)

    # Determine if we should show current transits or transits for a specific time
    if hasattr(args, 'transit_date') and args.transit_date:
        # Use the specified date/time
        transits = transit_calculator.calculate_transit_for_date(transit_datetime, transit_location)
    else:
        # Use current local time at transit location
        transits = calculate_current_transits(chart, transit_location)

    # Calculate house dates for planets
    house_dates = transit_calculator.calculate_planet_house_dates(transit_datetime, transit_location)

    # Display transits
    display_transits(chart.name, transit_location, transit_datetime, transits, house_dates, has_time, chart)

    # Calculate and display long-term transits
    long_term_transits = transit_calculator.calculate_long_term_transits(
        transit_datetime,
        years_before=2,
        years_after=10,
        location=transit_location
    )

    display_long_term_transits(transit_datetime, long_term_transits)


def handle_collective_chart(args: argparse.Namespace, cli_parser: CLIParser):
    """Handle collective chart calculation and display."""
    # Create the collective chart
    chart = create_chart_from_args(args)

    # Determine if time was provided
    has_time = args.hour is not None and args.minute is not None

    # Display the collective chart
    display_natal_chart(chart, has_time)


if __name__ == "__main__":
    main()