"""
Command Line Interface for the Astro project.

A single command: produce the natal chart, current transit aspects to natal,
transit-planets-in-natal-houses, long-term outer-planet transits, annual
profection, and solar return for the current year.

Transit aspects are location-independent (zodiac math); the only place where
"current location" matters is casting the solar return chart, hence the
optional --current-city / --current-nation flags. They default to the birth
location.
"""

import argparse
from kerykeion import AstrologicalSubject

import config


class CLIParser:
    """Argparse wrapper. Single-command tool — no subparsers."""

    def __init__(self):
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="Calculate a full natal reading: chart, aspects, transits, "
                        "long-term outer transits, annual profection, solar return.",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Example:
  python main.py --name "John Doe" --year 1990 --month 6 --day 15 \\
      --hour 14 --minute 30 --city "New York" --nation "US"

  python main.py --name "Jane" --year 1985 --month 3 --day 22 \\
      --hour 9 --minute 45 --city "London" --nation "GB" \\
      --current-city "Berlin" --current-nation "DE"
            """,
        )
        parser.add_argument("--name", required=True, help="Name of the person")
        parser.add_argument("--year", type=int, required=True, help="Birth year")
        parser.add_argument("--month", type=int, required=True, help="Birth month (1-12)")
        parser.add_argument("--day", type=int, required=True, help="Birth day")
        parser.add_argument("--hour", type=int, help="Birth hour (0-23)")
        parser.add_argument("--minute", type=int, help="Birth minute (0-59)")
        parser.add_argument("--city", required=True, help="Birth city")
        parser.add_argument("--nation", required=True, help="Birth nation/country code")

        parser.add_argument("--lng", type=float, help="Birth longitude (optional override)")
        parser.add_argument("--lat", type=float, help="Birth latitude (optional override)")
        parser.add_argument("--tz", help="Timezone string (optional override)")

        parser.add_argument("--current-city", dest="current_city",
                            help="Current city (used only for solar-return chart; defaults to birth city)")
        parser.add_argument("--current-nation", dest="current_nation",
                            help="Current nation (used only for solar-return chart; defaults to birth nation)")
        return parser

    def parse_args(self) -> argparse.Namespace:
        return self.parser.parse_args()


def create_chart_from_args(args: argparse.Namespace) -> AstrologicalSubject:
    """Create the natal AstrologicalSubject from parsed args."""
    hour = args.hour if args.hour is not None else 0
    minute = args.minute if args.minute is not None else 0
    return AstrologicalSubject(
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
        geonames_username=config.GEONAMES_USERNAME,
    )
