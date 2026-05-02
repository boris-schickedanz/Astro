"""
Display helpers for the natal-analysis sections (balance, chart ruler,
stelliums) and the annual layer (profection, solar return).
"""

from typing import Any, Dict, List, Optional


def display_balance(elements: Dict[str, int], modalities: Dict[str, int],
                    hemispheres: Optional[Dict[str, Dict[str, int]]]) -> None:
    """Print element/modality counts and (if available) hemisphere split."""
    print("\nChart Balance:")
    fire, earth, air, water = elements["Fire"], elements["Earth"], elements["Air"], elements["Water"]
    print(f"  Elements:   Fire {fire}  Earth {earth}  Air {air}  Water {water}")

    card, fix, mut = modalities["Cardinal"], modalities["Fixed"], modalities["Mutable"]
    print(f"  Modalities: Cardinal {card}  Fixed {fix}  Mutable {mut}")

    if hemispheres:
        h = hemispheres["horizon"]
        m = hemispheres["meridian"]
        print(f"  Horizon:    Below {h['Northern (below)']}  Above {h['Southern (above)']}")
        print(f"  Meridian:   East (self) {m['Eastern (self)']}  West (other) {m['Western (other)']}")


def display_chart_ruler(ruler: Optional[Dict[str, Any]]) -> None:
    """Print the chart ruler and its placement."""
    if ruler is None:
        return
    rx = " R" if ruler.get("retrograde") else ""
    house_part = f", House {ruler['house']}" if ruler.get("house") else ""
    print("\nChart Ruler:")
    print(f"  ASC in {ruler['asc_sign']} → ruled by {ruler['ruler']}")
    print(f"  {ruler['ruler']}: {ruler['sign']} {ruler['degree']}°{rx}{house_part}")


def display_stelliums(stelliums: Dict[str, List[Dict[str, Any]]]) -> None:
    """Print sign and house stelliums (3+ planets)."""
    by_sign = stelliums.get("by_sign", [])
    by_house = stelliums.get("by_house", [])
    if not by_sign and not by_house:
        return
    print("\nStelliums (3+ planets):")
    for s in by_sign:
        print(f"  Sign  {s['sign']:>3}: {', '.join(s['planets'])}")
    for s in by_house:
        print(f"  House {s['house']:>3}: {', '.join(s['planets'])}")


def display_profection(profection: Optional[Dict[str, Any]]) -> None:
    """Print the active annual profection and the year lord placement."""
    if profection is None:
        return
    rx = " R" if profection.get("year_lord_retrograde") else ""
    print("\n" + "=" * 50)
    print("ANNUAL PROFECTION")
    print("=" * 50)
    print(f"Age {profection['age']} → House {profection['profected_house']} ({profection['profected_sign']})")
    if profection["year_lord"]:
        deg = profection["year_lord_degree"]
        sign = profection["year_lord_sign"]
        house = profection["year_lord_house"]
        house_part = f", House {house}" if house else ""
        print(f"Year lord: {profection['year_lord']} at {sign} {deg}°{rx}{house_part}")


def display_solar_return(sr: Dict[str, Any]) -> None:
    """Print the solar return summary (axes, luminaries, chart ruler)."""
    print("\n" + "=" * 50)
    print(f"SOLAR RETURN {sr['year']}")
    print("=" * 50)
    print(f"Exact return: {sr['sr_utc']}  (cast at {sr['city']}, {sr['nation']})")
    print(f"SR ASC: {sr['asc_sign']} {sr['asc_degree']}°")
    print(f"SR MC:  {sr['mc_sign']} {sr['mc_degree']}°")
    print(f"SR Sun:  {sr['sun_sign']} {sr['sun_degree']}° - House {sr['sun_house']}")
    print(f"SR Moon: {sr['moon_sign']} {sr['moon_degree']}° - House {sr['moon_house']}")

    ruler = sr.get("chart_ruler")
    if ruler:
        rx = " R" if ruler.get("retrograde") else ""
        house_part = f", House {ruler['house']}" if ruler.get("house") else ""
        print(f"SR Ruler: {ruler['ruler']} ({ruler['sign']} {ruler['degree']}°{rx}{house_part})")
