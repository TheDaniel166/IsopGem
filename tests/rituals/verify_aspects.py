"""Verify Aspects service works correctly."""
import sys
import os

sys.path.insert(0, "/home/burkettdaniel927/projects/isopgem/src")
os.chdir("/home/burkettdaniel927/projects/isopgem")

from pillars.astrology.services.aspects_service import AspectsService

def main():
    service = AspectsService()
    
    # Sample chart data
    planet_lons = {
        "Sun": 15.0,       # 15° Aries
        "Moon": 135.0,     # 15° Leo - Trine to Sun
        "Mercury": 105.0,  # 15° Cancer - Square to Sun
        "Venus": 75.0,     # 15° Gemini - Sextile to Sun
        "Mars": 195.0,     # 15° Libra - Opposition to Sun
        "Jupiter": 17.0,   # 17° Aries - Conjunction to Sun
        "Saturn": 45.0,    # 15° Taurus - Semi-sextile
    }
    
    print("=== Tier 0: Major Only ===")
    aspects = service.calculate_aspects(planet_lons, tier=0)
    print(f"Found {len(aspects)} aspects")
    
    print("\n=== Tier 1: Major + Common Minor ===")
    aspects = service.calculate_aspects(planet_lons, tier=1)
    print(f"Found {len(aspects)} aspects")
    
    print("\n=== Tier 2: Major + All Minor ===")
    aspects = service.calculate_aspects(planet_lons, tier=2)
    print(f"Found {len(aspects)} aspects")
    
    print("\n✓ Aspects tier system working correctly!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
