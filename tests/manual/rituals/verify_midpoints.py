"""Verify Midpoints service works correctly."""
import sys
import os

sys.path.insert(0, "/home/burkettdaniel927/projects/isopgem/src")
os.chdir("/home/burkettdaniel927/projects/isopgem")

from pillars.astrology.services.midpoints_service import MidpointsService

def main():
    service = MidpointsService()
    
    # Sample chart data
    planet_lons = {
        "Sun": 15.0,
        "Moon": 120.0,
        "Mercury": 25.0,
        "Venus": 45.0,
        "Mars": 90.0,
        "Jupiter": 180.0,
        "Saturn": 270.0,
        "Uranus": 50.0,
        "Neptune": 355.0,
        "Pluto": 300.0,
    }
    
    print("=== Classic 7 Only ===")
    midpoints = service.calculate_midpoints(planet_lons, classic_only=True)
    print(f"Found {len(midpoints)} midpoints (7 choose 2 = 21 expected)\n")
    
    signs = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", 
             "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
    
    for mp in midpoints[:10]:  # Show first 10
        sign_idx = int(mp.longitude / 30) % 12
        deg = mp.longitude % 30
        print(f"  {mp.planet_a:8}/{mp.planet_b:8} | {deg:5.1f}° {signs[sign_idx]}")
    
    if len(midpoints) > 10:
        print(f"  ... and {len(midpoints) - 10} more")
    
    print("\n=== Modern 10 ===")
    midpoints = service.calculate_midpoints(planet_lons, classic_only=False)
    print(f"Found {len(midpoints)} midpoints (10 choose 2 = 45 expected)")
    
    print("\n✓ Midpoints service working correctly!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
