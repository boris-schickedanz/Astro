"""
Nation birth data for mundane astrology calculations.

This module contains birth data (founding/independence dates) for major nations,
used to calculate national birth charts and transits.

Sources: Historical records of independence declarations, constitution ratifications,
and modern state formations.
"""

from typing import Dict, Any, List

# Nation birth data: Each entry contains the founding/independence date and location
# Format: name, year, month, day, hour, minute, capital city, nation code, notes
NATION_DATA: List[Dict[str, Any]] = [
    # Americas
    {
        "name": "United States of America",
        "year": 1789,
        "month": 3,
        "day": 4,  # Constitution took effect, First Congress
        "hour": 12,
        "minute": 0,
        "city": "New York",
        "nation": "US",
        "capital": "Washington",
        "notes": "Constitution effective date, March 4, 1789"
    },
    {
        "name": "Canada",
        "year": 1867,
        "month": 7,
        "day": 1,
        "hour": 0,
        "minute": 0,
        "city": "Ottawa",
        "nation": "CA",
        "capital": "Ottawa",
        "notes": "Canadian Confederation, July 1, 1867"
    },
    {
        "name": "Mexico",
        "year": 1810,
        "month": 9,
        "day": 16,
        "hour": 6,
        "minute": 0,
        "city": "Mexico City",
        "nation": "MX",
        "capital": "Mexico City",
        "notes": "Independence from Spain, September 16, 1810"
    },
    {
        "name": "Brazil",
        "year": 1822,
        "month": 9,
        "day": 7,
        "hour": 16,
        "minute": 30,
        "city": "São Paulo",
        "nation": "BR",
        "capital": "Brasília",
        "notes": "Independence from Portugal, September 7, 1822"
    },
    {
        "name": "Argentina",
        "year": 1816,
        "month": 7,
        "day": 9,
        "hour": 12,
        "minute": 0,
        "city": "Buenos Aires",
        "nation": "AR",
        "capital": "Buenos Aires",
        "notes": "Independence from Spain, July 9, 1816"
    },

    # Europe
    {
        "name": "United Kingdom",
        "year": 1801,
        "month": 1,
        "day": 1,
        "hour": 0,
        "minute": 0,
        "city": "London",
        "nation": "GB",
        "capital": "London",
        "notes": "Union of Great Britain and Ireland, January 1, 1801"
    },
    {
        "name": "France",
        "year": 1958,
        "month": 10,
        "day": 4,
        "hour": 0,
        "minute": 0,
        "city": "Paris",
        "nation": "FR",
        "capital": "Paris",
        "notes": "Fifth Republic, October 4, 1958"
    },
    {
        "name": "Germany",
        "year": 1949,
        "month": 5,
        "day": 23,
        "hour": 0,
        "minute": 0,
        "city": "Bonn",
        "nation": "DE",
        "capital": "Berlin",
        "notes": "Federal Republic of Germany (Basic Law), May 23, 1949"
    },
    {
        "name": "Italy",
        "year": 1946,
        "month": 6,
        "day": 2,
        "hour": 18,
        "minute": 0,
        "city": "Rome",
        "nation": "IT",
        "capital": "Rome",
        "notes": "Italian Republic, June 2, 1946"
    },
    {
        "name": "Spain",
        "year": 1978,
        "month": 12,
        "day": 27,
        "hour": 0,
        "minute": 0,
        "city": "Madrid",
        "nation": "ES",
        "capital": "Madrid",
        "notes": "Spanish Constitution, December 27, 1978"
    },
    {
        "name": "Russia",
        "year": 1991,
        "month": 12,
        "day": 25,
        "hour": 19,
        "minute": 32,
        "city": "Moscow",
        "nation": "RU",
        "capital": "Moscow",
        "notes": "Russian Federation independence, December 25, 1991"
    },
    {
        "name": "Ukraine",
        "year": 1991,
        "month": 8,
        "day": 24,
        "hour": 18,
        "minute": 0,
        "city": "Kyiv",
        "nation": "UA",
        "capital": "Kyiv",
        "notes": "Independence from Soviet Union, August 24, 1991"
    },
    {
        "name": "Poland",
        "year": 1918,
        "month": 11,
        "day": 11,
        "hour": 0,
        "minute": 0,
        "city": "Warsaw",
        "nation": "PL",
        "capital": "Warsaw",
        "notes": "Independence restoration, November 11, 1918"
    },

    # Asia
    {
        "name": "China",
        "year": 1949,
        "month": 10,
        "day": 1,
        "hour": 15,
        "minute": 0,
        "city": "Beijing",
        "nation": "CN",
        "capital": "Beijing",
        "notes": "People's Republic of China, October 1, 1949"
    },
    {
        "name": "India",
        "year": 1947,
        "month": 8,
        "day": 15,
        "hour": 0,
        "minute": 0,
        "city": "New Delhi",
        "nation": "IN",
        "capital": "New Delhi",
        "notes": "Independence from Britain, August 15, 1947"
    },
    {
        "name": "Japan",
        "year": 1947,
        "month": 5,
        "day": 3,
        "hour": 0,
        "minute": 0,
        "city": "Tokyo",
        "nation": "JP",
        "capital": "Tokyo",
        "notes": "Post-war Constitution, May 3, 1947"
    },
    {
        "name": "South Korea",
        "year": 1948,
        "month": 8,
        "day": 15,
        "hour": 10,
        "minute": 0,
        "city": "Seoul",
        "nation": "KR",
        "capital": "Seoul",
        "notes": "Republic of Korea, August 15, 1948"
    },
    {
        "name": "North Korea",
        "year": 1948,
        "month": 9,
        "day": 9,
        "hour": 0,
        "minute": 0,
        "city": "Pyongyang",
        "nation": "KP",
        "capital": "Pyongyang",
        "notes": "Democratic People's Republic of Korea, September 9, 1948"
    },
    {
        "name": "Israel",
        "year": 1948,
        "month": 5,
        "day": 14,
        "hour": 16,
        "minute": 0,
        "city": "Tel Aviv",
        "nation": "IL",
        "capital": "Jerusalem",
        "notes": "Declaration of Independence, May 14, 1948"
    },
    {
        "name": "Saudi Arabia",
        "year": 1932,
        "month": 9,
        "day": 23,
        "hour": 0,
        "minute": 0,
        "city": "Riyadh",
        "nation": "SA",
        "capital": "Riyadh",
        "notes": "Unification of Saudi Arabia, September 23, 1932"
    },
    {
        "name": "Iran",
        "year": 1979,
        "month": 4,
        "day": 1,
        "hour": 15,
        "minute": 0,
        "city": "Tehran",
        "nation": "IR",
        "capital": "Tehran",
        "notes": "Islamic Republic, April 1, 1979"
    },
    {
        "name": "Turkey",
        "year": 1923,
        "month": 10,
        "day": 29,
        "hour": 20,
        "minute": 30,
        "city": "Ankara",
        "nation": "TR",
        "capital": "Ankara",
        "notes": "Turkish Republic, October 29, 1923"
    },
    {
        "name": "Pakistan",
        "year": 1947,
        "month": 8,
        "day": 14,
        "hour": 0,
        "minute": 0,
        "city": "Karachi",
        "nation": "PK",
        "capital": "Islamabad",
        "notes": "Independence from Britain, August 14, 1947"
    },
    {
        "name": "Indonesia",
        "year": 1945,
        "month": 8,
        "day": 17,
        "hour": 10,
        "minute": 0,
        "city": "Jakarta",
        "nation": "ID",
        "capital": "Jakarta",
        "notes": "Independence from Netherlands, August 17, 1945"
    },
    {
        "name": "Vietnam",
        "year": 1945,
        "month": 9,
        "day": 2,
        "hour": 14,
        "minute": 0,
        "city": "Hanoi",
        "nation": "VN",
        "capital": "Hanoi",
        "notes": "Independence declaration, September 2, 1945"
    },
    {
        "name": "Thailand",
        "year": 1932,
        "month": 6,
        "day": 24,
        "hour": 17,
        "minute": 0,
        "city": "Bangkok",
        "nation": "TH",
        "capital": "Bangkok",
        "notes": "Constitutional Monarchy, June 24, 1932"
    },

    # Middle East
    {
        "name": "Egypt",
        "year": 1953,
        "month": 6,
        "day": 18,
        "hour": 0,
        "minute": 0,
        "city": "Cairo",
        "nation": "EG",
        "capital": "Cairo",
        "notes": "Republic of Egypt, June 18, 1953"
    },

    # Africa
    {
        "name": "South Africa",
        "year": 1994,
        "month": 4,
        "day": 27,
        "hour": 0,
        "minute": 0,
        "city": "Pretoria",
        "nation": "ZA",
        "capital": "Pretoria",
        "notes": "First democratic elections, April 27, 1994"
    },
    {
        "name": "Nigeria",
        "year": 1960,
        "month": 10,
        "day": 1,
        "hour": 0,
        "minute": 0,
        "city": "Lagos",
        "nation": "NG",
        "capital": "Abuja",
        "notes": "Independence from Britain, October 1, 1960"
    },
    {
        "name": "Ethiopia",
        "year": 1995,
        "month": 8,
        "day": 21,
        "hour": 0,
        "minute": 0,
        "city": "Addis Ababa",
        "nation": "ET",
        "capital": "Addis Ababa",
        "notes": "Federal Democratic Republic, August 21, 1995"
    },

    # Oceania
    {
        "name": "Australia",
        "year": 1901,
        "month": 1,
        "day": 1,
        "hour": 13,
        "minute": 0,
        "city": "Sydney",
        "nation": "AU",
        "capital": "Canberra",
        "notes": "Commonwealth of Australia, January 1, 1901"
    },
    {
        "name": "New Zealand",
        "year": 1907,
        "month": 9,
        "day": 26,
        "hour": 0,
        "minute": 0,
        "city": "Wellington",
        "nation": "NZ",
        "capital": "Wellington",
        "notes": "Dominion status, September 26, 1907"
    },

    # International Organizations
    {
        "name": "European Union",
        "year": 1993,
        "month": 11,
        "day": 1,
        "hour": 0,
        "minute": 0,
        "city": "Brussels",
        "nation": "BE",
        "capital": "Brussels",
        "notes": "Maastricht Treaty, November 1, 1993"
    },
    {
        "name": "United Nations",
        "year": 1945,
        "month": 10,
        "day": 24,
        "hour": 16,
        "minute": 50,
        "city": "New York",
        "nation": "US",
        "capital": "New York",
        "notes": "UN Charter entered into force, October 24, 1945"
    },
]


def get_nation_by_name(name: str) -> Dict[str, Any]:
    """
    Get nation data by name.

    Args:
        name: The name of the nation

    Returns:
        Dictionary containing nation birth data
    """
    for nation in NATION_DATA:
        if nation["name"].lower() == name.lower():
            return nation
    raise ValueError(f"Nation '{name}' not found in database")


def get_all_nations() -> List[Dict[str, Any]]:
    """
    Get all nations in the database.

    Returns:
        List of all nation birth data dictionaries
    """
    return NATION_DATA.copy()


def get_nations_by_region(region: str) -> List[Dict[str, Any]]:
    """
    Get nations filtered by region.

    Args:
        region: Region identifier (Americas, Europe, Asia, Middle East, Africa, Oceania)

    Returns:
        List of nation birth data dictionaries for the specified region
    """
    # This is a simple implementation - could be enhanced with actual region tagging
    region_keywords = {
        "americas": ["United States", "Canada", "Mexico", "Brazil", "Argentina"],
        "europe": ["United Kingdom", "France", "Germany", "Italy", "Spain", "Russia", "Ukraine", "Poland"],
        "asia": ["China", "India", "Japan", "South Korea", "North Korea", "Pakistan", "Indonesia", "Vietnam", "Thailand"],
        "middle_east": ["Israel", "Saudi Arabia", "Iran", "Turkey", "Egypt"],
        "africa": ["South Africa", "Nigeria", "Ethiopia"],
        "oceania": ["Australia", "New Zealand"]
    }

    region_lower = region.lower()
    if region_lower not in region_keywords:
        return []

    keywords = region_keywords[region_lower]
    return [n for n in NATION_DATA if any(keyword in n["name"] for keyword in keywords)]
