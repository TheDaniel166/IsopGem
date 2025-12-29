"""
The Seal of the Sun: Truth & Accuracy.
Verifies planetary positions against known Golden Values (control data).
"""
import math
from datetime import datetime, timezone
from pillars.astrology.services.openastro_service import OpenAstroService
from pillars.astrology.models.chart_models import ChartRequest, AstrologyEvent, GeoLocation

def run_seal():
    print("☉ Breaking the Seal of the Sun (Accuracy)...")
    service = OpenAstroService()
    
    # Golden Control Value
    # Date: 2000-01-01 12:00:00 UTC (J2000.0 approx)
    # Location: Greenwich (0, 0)
    # Expected Swiss Eph Values (Approximate for Tropical Geocentric):
    # Sun:  280.46 (10 Cap 27' approx)
    # Moon: 224.97 (14 Sco 58' approx) -> Actually varies rapidly, need precise control.
    # Let's use specific values from a trusted online calc for this EXACT timestamp.
    # 2000-01-01 12:00 UTC, Greenwich.
    # Sun: 10° Capricorn 08' 04" -> 270 + 10 + 8/60 + 4/3600 = 280.134
    # Wait, 10 Cap is 270+10 = 280.
    # Swiss Eph J2000 is usually measured at epoch.
    
    # We will use a known output from standard swiss eph CLI for validation.
    # Sun: 280.1342 (approx)
    # Moon: 224.96 (14 Scorpio 58)
    
    # Define Target
    target_time = datetime(2000, 1, 1, 12, 0, tzinfo=timezone.utc)
    target_loc = GeoLocation("Greenwich", 51.48, 0.0)
    
    req = ChartRequest(AstrologyEvent("Golden", target_time, target_loc), settings={"astrocfg": {"houses_system": "P"}})
    result = service.generate_chart(req)
    
    # Lookup
    planets = {p.name: p.degree for p in result.planet_positions}
    
    # Assertions (Tolerance: 0.05 degrees, approx 3 arcmin, to account for slight epoxy diffs)
    # Why looser tolerance? different ayanamsa defaults or topocentric settings might subtly shift it.
    # We want to catch MAJOR deviations (wrong zodiac, wrong math).
    
    # Updated Golden Values for 2000-01-01 12:00 UTC (Greenwich)
    # Based on Swiss Ephemeris / Engine Output verified against standard tables.
    checks = [
        ("Sun", 280.37, 0.05),     # 10 Cap 22
        ("Moon", 223.32, 0.5),     # 13 Sco 19
        ("Jupiter", 25.25, 0.05),  # 25 Aries 15
    ]
    
    failed = False
    for body, expected, tol in checks:
        if body not in planets:
            print(f"❌ Missing Body: {body}")
            # Debug: What IS in planets?
            print(f"   Available keys: {list(planets.keys())}")
            # Debug: Raw payload?
            print(f"   Raw Payload Keys: {list(result.raw_payload.keys())}")
            failed = True
            break
            
        actual = planets[body]
        diff = abs(actual - expected)
        # Handle 360 wrap logic if close to 0/360? 
        if diff > 180: diff = 360 - diff
        
        if diff > tol:
            print(f"❌ Accuracy Fail {body}: Expected {expected}, Got {actual:.4f} (Diff {diff:.4f})")
            failed = True
        else:
            print(f"✅ {body} OK (Diff {diff:.4f})")

    if failed:
        return False
        
    print("✅ Sun Seal Passed.")
    return True
