"""
MCP server for the Astro project.
Exposes astrological calculations as tools for AI agents.
"""

import io
import sys
import os

# Set working directory to the script's directory to ensure relative paths (like 'cache/') work correctly
# and that .env files are loaded from the project root.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from typing import Optional
import pytz
from fastmcp import FastMCP
from kerykeion import AstrologicalSubject
import config
from chart import display_natal_chart
from transits import TransitsCalculator, calculate_current_transits
from display import display_transits, display_long_term_transits

# Ensure cache directory exists
if not os.path.exists("cache"):
    try:
        os.makedirs("cache")
    except Exception:
        pass

# Initialize FastMCP server
mcp = FastMCP("Astro")

def create_subject(
    name: str,
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    city: str = "London",
    nation: str = "GB",
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    tz: Optional[str] = None
) -> AstrologicalSubject:
    """Helper to create an AstrologicalSubject."""
    return AstrologicalSubject(
        name=name,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        city=city,
        nation=nation,
        lat=lat,
        lng=lng,
        tz_str=tz,
        geonames_username=config.GEONAMES_USERNAME
    )

def get_current_time_at_location(city: str, nation: str) -> datetime:
    """Helper to get current local time at a specific location."""
    try:
        temp_chart = AstrologicalSubject(
            "Temp",
            2025, 1, 1, 12, 0,
            city,
            nation,
            geonames_username=config.GEONAMES_USERNAME
        )
        location_tz = pytz.timezone(temp_chart.tz_str)
        return datetime.now(pytz.UTC).astimezone(location_tz)
    except Exception:
        return datetime.now()

@mcp.tool()
def calculate_natal_chart(
    name: str,
    year: int,
    month: int,
    day: int,
    hour: Optional[int] = None,
    minute: Optional[int] = None,
    city: str = "London",
    nation: str = "GB",
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    tz: Optional[str] = None
) -> str:
    """
    Calculate and display a natal (birth) chart for a person.
    Use this tool when you need to know the planetary positions, house placements, 
    and aspects at the moment of someone's birth.
    
    Args:
        name: Name of the person
        year: Birth year (e.g., 1990)
        month: Birth month (1-12)
        day: Birth day (1-31)
        hour: Birth hour (0-23), optional. Defaults to 0 if not provided.
        minute: Birth minute (0-59), optional. Defaults to 0 if not provided.
        city: Birth city (e.g., 'New York')
        nation: Birth nation/country code (e.g., 'US', 'GB')
        lat: Latitude (optional, overrides city lookup)
        lng: Longitude (optional, overrides city lookup)
        tz: Timezone string (e.g., 'America/New_York', optional, overrides city lookup)
    """
    has_time = hour is not None and minute is not None
    h = hour if hour is not None else 0
    m = minute if minute is not None else 0
    
    chart = create_subject(name, year, month, day, h, m, city, nation, lat, lng, tz)
    
    # Capture output
    output = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = output
    try:
        display_natal_chart(chart, has_time)
    finally:
        sys.stdout = old_stdout
        
    return output.getvalue()

@mcp.tool()
def calculate_transits(
    name: str,
    year: int,
    month: int,
    day: int,
    hour: Optional[int] = None,
    minute: Optional[int] = None,
    city: str = "London",
    nation: str = "GB",
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    tz: Optional[str] = None,
    transit_date: Optional[str] = None,
    transit_hour: int = 12,
    transit_city: Optional[str] = None,
    transit_nation: Optional[str] = None
) -> str:
    """
    Calculate transits for a natal chart at a specific time and location.
    Use this tool to see how current or future planetary positions interact with a person's birth chart.
    This is useful for daily, monthly, or specific date astrological readings.
    
    Args:
        name: Name of the person
        year: Birth year
        month: Birth month (1-12)
        day: Birth day
        hour: Birth hour (0-23), optional
        minute: Birth minute (0-59), optional
        city: Birth city
        nation: Birth nation/country code
        lat: Birth latitude (optional)
        lng: Birth longitude (optional)
        tz: Birth timezone string (optional)
        transit_date: Date for transit calculations (YYYY-MM-DD), defaults to current date
        transit_hour: Hour for transit calculations (0-23), defaults to 12
        transit_city: City for transit calculations, defaults to birth city
        transit_nation: Nation for transit calculations, defaults to birth nation
    """
    has_time = hour is not None and minute is not None
    h = hour if hour is not None else 0
    m = minute if minute is not None else 0
    
    chart = create_subject(name, year, month, day, h, m, city, nation, lat, lng, tz)
    
    t_city = transit_city or city
    t_nation = transit_nation or nation
    transit_location = f"{t_city}, {t_nation}"
    
    if transit_date:
        try:
            t_date = datetime.strptime(transit_date, "%Y-%m-%d")
            transit_datetime = t_date.replace(hour=transit_hour, minute=0)
        except ValueError:
            return f"Error: Invalid transit_date format. Use YYYY-MM-DD."
    else:
        transit_datetime = get_current_time_at_location(t_city, t_nation)
        if transit_hour != 12: # If user specified an hour but no date
            transit_datetime = transit_datetime.replace(hour=transit_hour, minute=0)

    # Capture output
    output = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = output
    try:
        transit_calculator = TransitsCalculator(chart)
        
        if transit_date:
            transits = transit_calculator.calculate_transit_for_date(transit_datetime, transit_location)
        else:
            transits = calculate_current_transits(chart, transit_location)
            
        house_dates = transit_calculator.calculate_planet_house_dates(transit_datetime, transit_location)
        display_transits(chart.name, transit_location, transit_datetime, transits, house_dates, has_time, chart)
    finally:
        sys.stdout = old_stdout
        
    return output.getvalue()

@mcp.tool()
def calculate_collective_chart(
    city: str,
    nation: str,
    date: Optional[str] = None,
    hour: Optional[int] = None,
    minute: Optional[int] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    tz: Optional[str] = None
) -> str:
    """
    Calculate a collective chart for a specific location and time.
    Use this tool to get the current planetary positions (the 'sky right now') or for a specific 
    historical/future moment without reference to a birth chart.
    
    Args:
        city: City for the chart
        nation: Nation/country code (e.g., 'US', 'GB')
        date: Date for the chart (YYYY-MM-DD), defaults to current date
        hour: Hour (0-23), optional
        minute: Minute (0-59), optional
        lat: Latitude (optional)
        lng: Longitude (optional)
        tz: Timezone string (optional)
    """
    if date:
        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
            if hour is not None:
                dt = dt.replace(hour=hour, minute=minute or 0)
            else:
                now = get_current_time_at_location(city, nation)
                dt = dt.replace(hour=now.hour, minute=now.minute)
        except ValueError:
            return "Error: Invalid date format. Use YYYY-MM-DD."
    else:
        dt = get_current_time_at_location(city, nation)
        if hour is not None:
            dt = dt.replace(hour=hour, minute=minute or 0)

    chart = create_subject(f"Collective Chart {city}", dt.year, dt.month, dt.day, dt.hour, dt.minute, city, nation, lat, lng, tz)
    
    has_time = hour is not None
    
    # Capture output
    output = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = output
    try:
        display_natal_chart(chart, has_time)
    finally:
        sys.stdout = old_stdout
        
    return output.getvalue()

@mcp.tool()
def calculate_long_term_transits(
    name: str,
    year: int,
    month: int,
    day: int,
    hour: Optional[int] = None,
    minute: Optional[int] = None,
    city: str = "London",
    nation: str = "GB",
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    tz: Optional[str] = None,
    years_before: int = 2,
    years_after: int = 10
) -> str:
    """
    Calculate long-term transits (outer planets) for a natal chart.
    Use this tool to identify major life themes and long-term astrological cycles 
    (like Saturn returns, Uranus oppositions, etc.) over a period of several years.
    
    Args:
        name: Name of the person
        year: Birth year
        month: Birth month (1-12)
        day: Birth day
        hour: Birth hour (0-23), optional
        minute: Birth minute (0-59), optional
        city: Birth city
        nation: Birth nation/country code
        lat: Birth latitude (optional)
        lng: Birth longitude (optional)
        tz: Birth timezone string (optional)
        years_before: Number of years before current date to start (default 2)
        years_after: Number of years after current date to end (default 10)
    """
    h = hour if hour is not None else 0
    m = minute if minute is not None else 0
    chart = create_subject(name, year, month, day, h, m, city, nation, lat, lng, tz)
    
    transit_datetime = datetime.now()
    transit_location = f"{city}, {nation}"
    
    # Capture output
    output = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = output
    try:
        transit_calculator = TransitsCalculator(chart)
        long_term_transits = transit_calculator.calculate_long_term_transits(
            transit_datetime,
            years_before=years_before,
            years_after=years_after,
            location=transit_location
        )
        display_long_term_transits(transit_datetime, long_term_transits)
    finally:
        sys.stdout = old_stdout
        
    return output.getvalue()

if __name__ == "__main__":
    mcp.run()
