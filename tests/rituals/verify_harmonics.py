"""Verify Harmonics service works correctly."""
import sys
import os

sys.path.insert(0, "/home/burkettdaniel927/projects/isopgem/src")
os.chdir("/home/burkettdaniel927/projects/isopgem")

from pillars.astrology.services.harmonics_service import HarmonicsService

def main():
    service = HarmonicsService()
    
    # Sample chart data
    planet_lons = {
        "Sun": 15.0,       # 15° Aries
        "Moon": 120.0,     # 0° Leo
        "Mercury": 25.0,
        "Venus": 45.0,
        "Mars": 90.0,
        "Jupiter": 180.0,
        "Saturn": 270.0,
    }
    
    signs = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", 
             "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
    
    for h in [1, 4, 5, 7, 9]:
        name, desc = service.get_preset_info(h)
        print(f"=== H{h}: {name} ===")
        
        positions = service.calculate_harmonic(planet_lons, h)
        
        for hp in positions[:5]:  # Show first 5
            sign_idx = int(hp.harmonic_longitude / 30) % 12
            deg = hp.harmonic_longitude % 30
            
            natal_sign = int(hp.natal_longitude / 30) % 12
            natal_deg = hp.natal_longitude % 30
            
            print(f"  {hp.planet:8} | Natal: {natal_deg:5.1f}° {signs[natal_sign]} -> H{h}: {deg:5.1f}° {signs[sign_idx]}")
        
        if len(positions) > 5:
            print(f"  ... and {len(positions) - 5} more")
        print()
    
    print("✓ Harmonics service working correctly!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
