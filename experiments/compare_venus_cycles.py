
from datetime import datetime, timezone, timedelta
import math
import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))
from pillars.astrology.utils.conversions import to_zodiacal_string

# --- Reference Data (Ground Truth) ---
REFERENCE_EVENTS = [
    {
        "date": datetime(2025, 3, 23, 1, 0, tzinfo=timezone.utc),
        "type": "Inferior Conjunction",
        "expected_sign": "2° Aries", # Approx
        "expected_long": 2.0 # Aries is 0-30
    },
    {
        "date": datetime(2026, 1, 6, 17, 0, tzinfo=timezone.utc),
        "type": "Superior Conjunction",
        "expected_sign": "16° Capricorn",
        "expected_long": 270 + 16 # Cap starts at 270
    },
    {
        "date": datetime(2026, 10, 24, 0, 0, tzinfo=timezone.utc),
        "type": "Inferior Conjunction",
        "expected_sign": "0° Scorpio",
        "expected_long": 210 + 0 # Scorpio starts at 210
    }
]

# --- App Logic (Copied from venus_rose_window.py to avoid UI deps) ---
# J2000.0 Epoch: 2000-01-01 12:00 UTC
J2000 = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
# Mean Longitudes at J2000 (Degrees)
L_EARTH_J2000 = 100.46
L_VENUS_J2000 = 181.98

# Orbital Periods (Days)
P_EARTH = 365.256
P_VENUS = 224.701

def calculate_app_position(target_date, use_real_physics):
    """
    Simulates the app's update_positions_by_date logic for a single target date.
    Returns: (earth_long, venus_long, venus_sign_str)
    """
    delta = target_date - J2000
    days = delta.total_seconds() / 86400.0
    
    # Earth
    deg_per_day_e = 360.0 / P_EARTH
    mean_long_e = (L_EARTH_J2000 + days * deg_per_day_e) % 360.0
    
    # Venus
    if use_real_physics:
        deg_per_day_v = 360.0 / P_VENUS
    else:
        # Locked 13:8 resonance
        deg_per_day_v = (13.0 * 360.0) / (8.0 * P_EARTH)
        
    mean_long_v = (L_VENUS_J2000 + days * deg_per_day_v) % 360.0
    
    # --- Heliocentric Coordinates (Sun as origin) ---
    # Convert polar to cartesian (radians)
    rad_e = math.radians(mean_long_e)
    rad_v = math.radians(mean_long_v)
    
    # We need orbital radii relative to each other.
    # Simplified: Earth = 1.0 AU, Venus = 0.723 AU
    # Or use the pixel constants from the app if we want to match visual exactly?
    # The app uses visual constants ORBIT_EARTH_R=300, ORBIT_VENUS_R=217
    # Let's use those to stay consistent with the "Visual Physics" of the app.
    R_EARTH = 300.0
    R_VENUS = 217.0
    
    # Earth Position (Heliocentric)
    ex = R_EARTH * math.cos(rad_e)
    ey = R_EARTH * math.sin(rad_e)
    
    # Venus Position (Heliocentric)
    vx = R_VENUS * math.cos(rad_v)
    vy = R_VENUS * math.sin(rad_v)
    
    # --- Geocentric Calculation (Earth as origin) ---
    # Vector from Earth to Venus
    # dx = vx - ex
    # dy = vy - ey
    dx = vx - ex
    dy = vy - ey
    
    # Angle of vector
    geo_rad = math.atan2(dy, dx)
    geo_deg = math.degrees(geo_rad) % 360.0
    
    return mean_long_e, geo_deg, to_zodiacal_string(geo_deg)

def run_comparison():
    print("=== Venus Cycle Calculation Comparison ===")
    print(f"J2000 Epoch: {J2000}")
    print("-" * 60)
    
    for event in REFERENCE_EVENTS:
        dt = event["date"]
        print(f"Target Event: {event['type']} on {dt.strftime('%Y-%m-%d')}")
        print(f"  Reference: {event['expected_sign']} (Long: {event['expected_long']})")
        
        # Test Ideal
        _, long_ideal, sign_ideal = calculate_app_position(dt, use_real_physics=False)
        diff_ideal = (long_ideal - event["expected_long"]) % 360
        if diff_ideal > 180: diff_ideal -= 360
        
        print(f"  App (Ideal): {sign_ideal} (Long: {long_ideal:.2f})")
        print(f"    -> Diff: {diff_ideal:.2f} degrees")
        
        # Test Real
        _, long_real, sign_real = calculate_app_position(dt, use_real_physics=True)
        diff_real = (long_real - event["expected_long"]) % 360
        if diff_real > 180: diff_real -= 360
        
        print(f"  App (Real):  {sign_real} (Long: {long_real:.2f})")
        print(f"    -> Diff: {diff_real:.2f} degrees")
        print("-" * 60)

if __name__ == "__main__":
    run_comparison()
