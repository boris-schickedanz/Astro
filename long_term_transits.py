"""
Long-term transit calculation module.

This module handles calculations for significant long-term transits from outer planets.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List
from collections import defaultdict

from kerykeion import AstrologicalSubject, TransitsTimeRangeFactory
import pytz
import config

from models import OUTER_PLANET_POINTS, LONG_TERM_ACTIVE_ASPECTS, NATAL_RELEVANT_PLANETS


class LongTermTransitCalculator:
    """
    Calculator for significant long-term transits from outer planets.
    """

    def __init__(self, natal_chart: AstrologicalSubject):
        """
        Initialize the long-term transit calculator.

        Args:
            natal_chart: The natal chart
        """
        self.natal_chart = natal_chart

    def calculate_long_term_transits(self, base_date: datetime,
                                   years_before: int = 2, years_after: int = 2,
                                   location: str = "Greenwich, GB") -> Dict[str, Any]:
        """
        Calculate significant long-term transits from outer planets.

        This method identifies when slow-moving outer planets (Saturn, Uranus, Neptune, Pluto)
        form major aspects with natal planets. It tracks complete transit cycles including
        retrograde patterns.

        Args:
            base_date: The base date for the transit calculation (typically today)
            years_before: Number of years before base_date to check (default: 2)
            years_after: Number of years after base_date to check (default: 2)
            location: Location for transit calculations

        Returns:
            List of significant long-term transits with date ranges, organized by status
        """
                # Generate monthly ephemeris points across the requested range
        start_date = base_date - timedelta(days=years_before * 365)
        end_date = base_date + timedelta(days=years_after * 365)

        ephemeris_points = self._generate_ephemeris_points(start_date, end_date, location)

        if not ephemeris_points:
            return {
                'active': [],
                'recent_past': [],
                'upcoming': [],
                'base_date': base_date.date().strftime('%Y-%m-%d')
            }

        # Calculate transit periods
        transit_periods = self._calculate_transit_periods(ephemeris_points)

        # Merge transit passes that are part of the same cycle (due to retrograde)
        merged_transits = self._merge_transit_passes(transit_periods)

        # Convert to output format and categorize
        categorized_transits = self._categorize_long_term_transits(merged_transits, base_date, years_after)

        return categorized_transits

    def _generate_ephemeris_points(self, start_date: datetime, end_date: datetime, location: str) -> List[AstrologicalSubject]:
        """Generate monthly ephemeris points for the date range."""
        ephemeris_points: List[AstrologicalSubject] = []

        current_date = start_date
        while current_date <= end_date:
            try:
                chart = AstrologicalSubject(
                    f"Transit_{current_date.strftime('%Y%m%d')}",
                    current_date.year,
                    current_date.month,
                    current_date.day,
                    12,
                    0,
                    location.split(",")[0].strip(),
                    location.split(",")[1].strip() if "," in location else "GB",
                    geonames_username=config.GEONAMES_USERNAME
                )
                ephemeris_points.append(chart)
            except Exception:
                pass  # Skip dates that can't be calculated

            current_date += timedelta(days=30)  # Monthly instead of weekly

        return ephemeris_points

    def _calculate_transit_periods(self, ephemeris_points: List[AstrologicalSubject]) -> List[Dict[str, Any]]:
        """Calculate transit periods from ephemeris data."""
        def parse_iso_datetime(value: str) -> datetime:
            cleaned = value.replace("Z", "+00:00") if value.endswith("Z") else value
            dt = datetime.fromisoformat(cleaned)
            if dt.tzinfo is not None:
                dt = dt.astimezone(pytz.UTC).replace(tzinfo=None)
            return dt

        # Create lookup dict for fast access
        ephemeris_dict = {chart.iso_formatted_utc_datetime: chart for chart in ephemeris_points}

        transit_factory = TransitsTimeRangeFactory(
            self.natal_chart,
            ephemeris_points,
            active_points=OUTER_PLANET_POINTS,
            active_aspects=LONG_TERM_ACTIVE_ASPECTS,
        )
        transit_model = transit_factory.get_transit_moments()

        transit_periods: List[Dict[str, Any]] = []
        current_transits: Dict[tuple, Dict[str, Any]] = {}

        outer_planet_set = {name for name in OUTER_PLANET_POINTS}

        dates = transit_model.dates or []
        moments = transit_model.transits or []

        for date_str, moment in zip(dates, moments):
            date_obj = parse_iso_datetime(date_str)
            chart = ephemeris_dict.get(date_str)

            active_this_week = set()

            for aspect in (moment.aspects or []):
                transit_planet = aspect.p1_name
                natal_planet = aspect.p2_name

                if transit_planet not in outer_planet_set or natal_planet not in NATAL_RELEVANT_PLANETS:
                    continue

                aspect_name = aspect.aspect
                orb_diff = abs(aspect.orbit)
                transit_key = (transit_planet, natal_planet, aspect_name)
                active_this_week.add(transit_key)

                if transit_key not in current_transits:
                    transit_body = getattr(chart, transit_planet.lower(), None) if chart else None
                    natal_body = getattr(self.natal_chart, natal_planet.lower())

                    current_transits[transit_key] = {
                        'transit_planet': transit_planet,
                        'natal_planet': natal_planet,
                        'aspect': aspect_name,
                        'start_date': date_obj,
                        'end_date': date_obj,
                        'min_orb': orb_diff,
                        'transit_sign': transit_body.sign if transit_body else '',
                        # Use `position` to get degrees within the sign (0-30),
                        # `sign_num` is the sign index (0-11) and not a degree.
                        'transit_degree': transit_body.position if transit_body else 0,
                        'natal_sign': natal_body.sign,
                        'natal_degree': natal_body.position,
                        'is_retrograde': transit_body.retrograde if transit_body else False,
                        'passes': [{'start': date_obj, 'end': date_obj}],
                    }
                else:
                    existing = current_transits[transit_key]
                    existing['end_date'] = date_obj
                    if orb_diff < existing['min_orb']:
                        existing['min_orb'] = orb_diff

            completed_keys = []
            for transit_key, transit_data in current_transits.items():
                if transit_key not in active_this_week:
                    transit_data['passes'][-1]['end'] = transit_data['end_date']
                    transit_periods.append(transit_data.copy())
                    completed_keys.append(transit_key)

            for key in completed_keys:
                del current_transits[key]

        # Add remaining active transits
        for transit_data in current_transits.values():
            transit_data['passes'][-1]['end'] = transit_data['end_date']
            transit_periods.append(transit_data.copy())

        return transit_periods

    def _merge_transit_passes(self, transit_periods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge multiple passes of the same transit that occur due to retrograde motion.

        If the same transit (same planets, same aspect) occurs multiple times with gaps
        less than ~6 months, they're likely part of the same transit cycle and should
        be merged into one period showing the full transit duration.

        Args:
            transit_periods: List of individual transit periods

        Returns:
            List of merged transit periods
        """
        # Group transits by their key (planet pair + aspect)
        transit_groups = defaultdict(list)
        for transit in transit_periods:
            key = (transit['transit_planet'], transit['natal_planet'], transit['aspect'])
            transit_groups[key].append(transit)

        merged = []

        for key, transits in transit_groups.items():
            if not transits:
                continue

            # Sort by start date
            transits.sort(key=lambda x: x['start_date'])

            # Merge passes that are close together (within 6 months = retrograde cycle)
            current_merged = None

            for transit in transits:
                if current_merged is None:
                    # Start a new merged transit
                    current_merged = transit.copy()
                    current_merged['passes'] = [{'start': transit['start_date'], 'end': transit['end_date']}]
                else:
                    # Check if this pass is part of the same cycle
                    gap_days = (transit['start_date'] - current_merged['end_date']).days

                    # Saturn/Uranus: ~6 month retrograde cycle
                    # Neptune/Pluto: ~5-6 month retrograde cycle
                    max_gap = 180  # 6 months

                    if gap_days <= max_gap:
                        # Part of same cycle - merge
                        current_merged['end_date'] = transit['end_date']
                        if transit['min_orb'] < current_merged['min_orb']:
                            current_merged['min_orb'] = transit['min_orb']
                        current_merged['passes'].append({'start': transit['start_date'], 'end': transit['end_date']})
                    else:
                        # Different cycle - save current and start new
                        merged.append(current_merged)
                        current_merged = transit.copy()
                        current_merged['passes'] = [{'start': transit['start_date'], 'end': transit['end_date']}]

            # Add the last merged transit
            if current_merged is not None:
                merged.append(current_merged)

        return merged

    def _categorize_long_term_transits(self, transits: List[Dict[str, Any]], base_date: datetime, years_after: int = 2) -> Dict[str, Any]:
        """
        Categorize long-term transits into active, recently completed, and upcoming.

        Args:
            transits: List of all detected transit periods
            base_date: The reference date (typically today)
            years_after: Number of years after base_date to include upcoming transits

        Returns:
            Dictionary with categorized transits
        """
        base_date_only = base_date.date()

        # Categorize transits
        active_transits = []
        past_transits = defaultdict(list)  # Group by planet
        future_transits = defaultdict(list)  # Group by planet

        for transit in transits:
            start_date = transit['start_date'].date() if isinstance(transit['start_date'], datetime) else transit['start_date']
            end_date = transit['end_date'].date() if isinstance(transit['end_date'], datetime) else transit['end_date']
            planet = transit['transit_planet']

            # Calculate duration in months (more appropriate than years for most transits)
            duration_days = (end_date - start_date).days
            duration_months = round(duration_days / 30.44, 1)

            transit_info = {
                'transit_planet': planet,
                'natal_planet': transit['natal_planet'],
                'aspect': transit['aspect'],
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'duration_months': duration_months,
                'min_orb': round(transit['min_orb'], 2),
                'transit_position': f"{transit['transit_sign']} {round(transit['transit_degree'], 1)}°",
                'natal_position': f"{transit['natal_sign']} {round(transit['natal_degree'], 1)}°",
                'is_retrograde': transit.get('is_retrograde', False)
            }

            if start_date <= base_date_only <= end_date:
                # Currently active
                # Calculate how far through the transit we are
                total_days = (end_date - start_date).days
                elapsed_days = (base_date_only - start_date).days
                progress_pct = round((elapsed_days / total_days * 100) if total_days > 0 else 0, 1)
                transit_info['progress_percent'] = progress_pct
                transit_info['status'] = 'Active'
                active_transits.append(transit_info)
            elif end_date < base_date_only:
                # Past transit
                days_ago = (base_date_only - end_date).days
                if days_ago <= 730:  # Within past 2 years
                    transit_info['days_ago'] = days_ago
                    past_transits[planet].append(transit_info)
            elif start_date > base_date_only:
                # Future transit
                days_until = (start_date - base_date_only).days
                max_days = years_after * 365
                if days_until <= max_days:  # Within specified years
                    transit_info['days_until'] = days_until
                    future_transits[planet].append(transit_info)

        # For past and future, keep only the most relevant per planet
        # Past: most recent one
        recent_past = []
        for planet, transits_list in past_transits.items():
            if transits_list:
                most_recent = min(transits_list, key=lambda x: x['days_ago'])
                recent_past.append(most_recent)

        # Future: next upcoming one
        upcoming = []
        for planet, transits_list in future_transits.items():
            if transits_list:
                next_one = min(transits_list, key=lambda x: x['days_until'])
                upcoming.append(next_one)

        # Sort active transits by planet priority (personal planets first)
        planet_priority = {'Saturn': 1, 'Uranus': 2, 'Neptune': 3, 'Pluto': 4}
        active_transits.sort(key=lambda x: (planet_priority.get(x['transit_planet'], 5), x['natal_planet']))
        recent_past.sort(key=lambda x: (planet_priority.get(x['transit_planet'], 5), -x['days_ago']))
        upcoming.sort(key=lambda x: (planet_priority.get(x['transit_planet'], 5), x['days_until']))

        return {
            'active': active_transits,
            'recent_past': recent_past,
            'upcoming': upcoming,
            'base_date': base_date_only.strftime('%Y-%m-%d')
        }