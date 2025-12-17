"""Verify Fixed Stars service works correctly."""
import sys
import os

# Add src to path for proper imports
sys.path.insert(0, "/home/burkettdaniel927/projects/isopgem/src")
os.chdir("/home/burkettdaniel927/projects/isopgem")

import swisseph as swe

# Direct import to avoid circular deps through __init__
from pillars.astrology.services.fixed_stars_service import FixedStarsService

def main():
    service = FixedStarsService()
    
    # Test with current Julian Day
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    jd = swe.julday(now.year, now.month, now.day, now.hour + now.minute/60.0)
    
    print(f"Testing Fixed Stars for JD: {jd:.4f}")
    print(f"Date: {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print("-" * 60)
    
    positions = service.get_star_positions(jd)
    
    if not positions:
        print("ERROR: No star positions returned!")
        return 1
    
    print(f"Found {len(positions)} stars:\n")
    
    for star in positions:
        # Convert longitude to zodiac sign
        sign_num = int(star.longitude / 30)
        signs = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", 
                 "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
        sign = signs[sign_num % 12]
        deg = star.longitude % 30
        
        print(f"  {star.name:15} | {deg:5.2f}° {sign} | mag: {star.magnitude:5.2f} | {star.nature}")
    
    print("\n✓ Fixed Stars service working correctly!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
