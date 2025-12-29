#!/usr/bin/env python3
"""
Verification Script for Horizon Phase 1 (Astrometric Integrity).
Tests:
1. Sidereal Calculation (Lahiri Ayanamsa)
2. Topocentric vs Geocentric (Parallax check)
3. Mean Node vs True Node
"""
from datetime import datetime, timezone
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from pillars.astrology.repositories.ephemeris_provider import EphemerisProvider
from pillars.astrology.models.chart_models import GeoLocation
import time

def run_verification():
    print("🔮 Awakening Ephemeris Provider...")
    provider = EphemerisProvider.get_instance()
    
    # Wait for fill
    timeout = 30
    start = time.time()
    while not provider.is_loaded():
        if time.time() - start > timeout:
            print("❌ Timeout waiting for Ephemeris load.")
            return
        time.sleep(0.5)
        
    print("✅ Ephemeris Loaded.")
    
    # Test Date: J2000 (2000-01-01 12:00 UTC)
    dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    
    print(f"\n📅 Test Date: {dt}")
    
    # ---------------------------------------------------------
    # Test 1: Sidereal vs Tropical (Sun)
    # ---------------------------------------------------------
    print("\n--- TEST 1: Sidereal Check (Sun) ---")
    sun_trop = provider.get_geocentric_ecliptic_position("sun", dt, zodiac_type="TROPICAL")
    sun_sid = provider.get_geocentric_ecliptic_position("sun", dt, zodiac_type="SIDEREAL", ayanamsa="LAHIRI")
    
    diff = (sun_trop - sun_sid) % 360
    # Expected Ayanamsa ~23.85 degrees at J2000
    expected_ayanamsa = 23.85
    error = abs(diff - expected_ayanamsa)
    
    print(f"Sun Tropical: {sun_trop:.4f}°")
    print(f"Sun Sidereal: {sun_sid:.4f}°")
    print(f"Difference (Ayanamsa): {diff:.4f}° (Expected ~{expected_ayanamsa}°)")
    
    if error < 0.1:
        print("✅ Sidereal Calculation PASS")
    else:
        print("❌ Sidereal Calculation FAIL (Deviation too high)")

    # ---------------------------------------------------------
    # Test 2: Topocentric Parallax (Moon)
    # ---------------------------------------------------------
    print("\n--- TEST 2: Topocentric Parallax (Moon) ---")
    # Location: North Pole (Max latitude) to maximize Z-axis parallax? 
    # Or Equator for max horizontal parallax. Let's try Equator.
    loc_equator = GeoLocation(name="Equator", latitude=0.0, longitude=0.0)
    
    moon_geo = provider.get_geocentric_ecliptic_position("moon", dt, location=None)
    moon_topo = provider.get_geocentric_ecliptic_position("moon", dt, location=loc_equator)
    
    parallax = abs(moon_geo - moon_topo)
    print(f"Moon Geocentric: {moon_geo:.4f}°")
    print(f"Moon Topocentric (Equator): {moon_topo:.4f}°")
    print(f"Parallax Difference: {parallax:.4f}°")
    
    if parallax > 0.01:
        print("✅ Topocentric Parallax Detected PASS")
    else:
        print("❌ Topocentric Parallax FAIL (No significant difference)")

    # ---------------------------------------------------------
    # Test 3: Mean vs True Node
    # ---------------------------------------------------------
    print("\n--- TEST 3: Lunar Nodes ---")
    true_node = provider.get_osculating_north_node(dt) # Existing method
    mean_node = provider.get_mean_north_node(dt)      # New method
    
    node_diff = abs(true_node - mean_node)
    print(f"True Node: {true_node:.4f}°")
    print(f"Mean Node: {mean_node:.4f}°")
    print(f"Difference: {node_diff:.4f}°")
    
    if node_diff > 0.0001:
        print("✅ Distinct Node Calculations PASS")
    else:
        print("⚠️ Warning: True and Mean node are identical (suspicious but possible if crossing)")

if __name__ == "__main__":
    run_verification()
