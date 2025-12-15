
from skyfield.api import load
from skyfield.framelib import ecliptic_frame
from datetime import datetime, timezone

def test_skyfield():
    # Load Ephemeris (this might trigger a download if not present)
    # DE421 is small and usually sufficient
    ts = load.timescale()
    planets = load('de421.bsp')
    
    earth = planets['earth']
    venus = planets['venus']
    sun = planets['sun']
    
    # Reference Date: Inferior Conjunction 2025-03-23 01:00 UTC
    # Expected: ~2 Aries (Geocentric)
    
    t = ts.utc(2025, 3, 23, 1, 0, 0)
    
    # Geocentric position of Venus (Earth -> Venus)
    astrometric = earth.at(t).observe(venus)
    
    # We want Ecliptic Longitude (Zodiac)
    lat, lon, distance = astrometric.ecliptic_latlon()
    
    # lon.degrees is 0-360
    degrees = lon.degrees
    print(f"Date: 2025-03-23 01:00 UTC")
    print(f"Skyfield Calculated Longitude: {degrees:.4f}")
    
    # Check Aries (0-30)
    # 2 deg Aries = 2.0
    print(f"Reference: ~2.0 (Aries)")
    
    # Second Reference: Superior Conjunction 2026-01-06 17:00 UTC
    # Expected: 16 deg Capricorn = 270 + 16 = 286.0
    t2 = ts.utc(2026, 1, 6, 17, 0, 0)
    lat2, lon2, dist2 = earth.at(t2).observe(venus).ecliptic_latlon()
    print(f"\nDate: 2026-01-06 17:00 UTC")
    print(f"Skyfield Calculated Longitude: {lon2.degrees:.4f}")
    print(f"Reference: ~286.0 (Capricorn)")

if __name__ == "__main__":
    test_skyfield()
