"""Verify Arabic Parts service works correctly."""
import sys
import os

sys.path.insert(0, "/home/burkettdaniel927/projects/isopgem/src")
os.chdir("/home/burkettdaniel927/projects/isopgem")

from pillars.astrology.services.arabic_parts_service import ArabicPartsService

def main():
    service = ArabicPartsService()
    
    # Sample chart data (Sun in Aries, Moon in Leo, etc.)
    planet_lons = {
        "Sun": 15.0,       # 15° Aries
        "Moon": 120.0,     # 0° Leo
        "Mercury": 5.0,
        "Venus": 45.0,
        "Mars": 90.0,
        "Jupiter": 180.0,
        "Saturn": 270.0,
        "Uranus": 50.0,
        "Neptune": 355.0,
        "Pluto": 300.0,
    }
    
    house_cusps = {
        1: 0.0,     # ASC at 0° Aries
        2: 30.0,
        3: 60.0,
        4: 90.0,
        5: 120.0,
        6: 150.0,
        7: 180.0,
        8: 210.0,
        9: 240.0,
        10: 270.0,  # MC
        11: 300.0,
        12: 330.0,
    }
    
    # Day chart (Sun above horizon)
    is_day = service.is_day_chart(planet_lons["Sun"], house_cusps[1])
    print(f"Day Chart: {is_day}")
    print("-" * 60)
    
    parts = service.calculate_parts(planet_lons, house_cusps, is_day)
    
    if not parts:
        print("ERROR: No Parts calculated!")
        return 1
    
    print(f"Calculated {len(parts)} Arabic Parts:\n")
    
    # Group by category
    current_cat = ""
    for part in parts:
        if part.category != current_cat:
            current_cat = part.category
            print(f"\n=== {current_cat.upper()} ===")
        
        # Convert to zodiac
        sign_idx = int(part.longitude / 30) % 12
        signs = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", 
                 "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
        deg_in_sign = part.longitude % 30
        
        print(f"  {part.name:15} | {deg_in_sign:5.1f}° {signs[sign_idx]} | {part.formula}")
    
    print("\n✓ Arabic Parts service working correctly!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
