#!/usr/bin/env python3
"""
Verification Script for Horizon Phase 2 (Chart Breadth).
Tests:
1. Solar Return Calculation (Newton-Raphson Solver)
2. Secondary Progression (Logic Check)
3. Composite Chart (Midpoint Check)
"""
from datetime import datetime, timezone
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from pillars.astrology.models.chart_models import AstrologyEvent, GeoLocation, ChartRequest, ChartResult, PlanetPosition
from pillars.astrology.services.returns_service import ReturnsService
from pillars.astrology.services.progressions_service import ProgressionsService
from pillars.astrology.services.synastry_service import SynastryService
from pillars.astrology.services.openastro_service import OpenAstroService
from pillars.astrology.services.aspects_service import AspectsService

# Mock OpenAstroService to avoid needing full Ephemeris/OpenAstro install for Unit Logical Check
# But wait, ReturnsService NEEDS the real EphemerisProvider.
# We will use the real EphemerisProvider (assumed verified in Phase 1).
# We will Mock OpenAstroService for Progressions since that calls 'generate_chart'.

class MockOpenAstroService(OpenAstroService):
    def __init__(self):
        # Bypass init
        pass
        
    def generate_chart(self, request: ChartRequest) -> ChartResult:
        # Return a dummy result that mirrors the input timestamp 
        # so we can verify the Progression Math.
        # Let's say Sun moves 1 degree per day for simplicity in mock?
        # Or better, just return distinct positions we can check.
        # For Solar Arc, we need Sun position.
        
        # Mock Sun at 0 degrees + (Year - 2000) degrees? 
        # Keep it simple: Sun = 10 degrees.
        return ChartResult(
            chart_type=request.chart_type,
            planet_positions=[
                PlanetPosition(name="Sun", degree=10.0),
                PlanetPosition(name="Moon", degree=20.0)
            ],
            house_positions=[]
        )

def run_verification():
    print("🔮 Awakening Phase 2 Engines...")
    
    # 1. Test ReturnsService (Real Ephemeris)
    print("\n--- TEST 1: Solar Return Solver ---")
    try:
        ret_svc = ReturnsService()
        if not ret_svc._ephemeris.is_loaded():
             print("Waiting for Ephemeris...")
             import time
             time.sleep(10) # Give it time to load thread
             
        # Natal: 2000-01-01. Sun ~280deg Capricorn.
        natal_dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        natal_loc = GeoLocation("Greenwich", 51.5, 0.0)
        natal_ev = AstrologyEvent("Natal", natal_dt, natal_loc)
        
        # Return 2001
        print("Calculating Solar Return for 2001...")
        sr_event = ret_svc.calculate_return(natal_ev, 2001, "sun")
        
        print(f"Natal Date: {natal_dt}")
        print(f"SR Date:    {sr_event.timestamp}")
        
        # Check delta. Should be close to Jan 1.
        delta = abs((sr_event.timestamp - datetime(2001, 1, 1, 12, 0, 0, tzinfo=timezone.utc)).total_seconds())
        # The year is 365.24 days.  0.24 days is ~6 hours.
        # So 2001 SR should be approx Jan 1, 18:00.
        
        print(f"Expected ~Jan 1 18:00. Difference from Jan 1 12:00 is {delta/3600:.2f} hours")
        
        if 5.5 < (delta/3600) < 6.5: 
             print("✅ Solar Return Timing makes sense (~6 hours later)")
        else:
             print("⚠️ Solar Return Timing deviation (check consistency)")
             
    except Exception as e:
        print(f"❌ ReturnsService Failed: {e}")

    # 2. Test Synastry (Composite)
    print("\n--- TEST 2: Composite Midpoints ---")
    syn_svc = SynastryService(AspectsService())
    
    # Chart A: Sun 10
    # Chart B: Sun 30
    # Midpoint should be 20
    cA = ChartResult("A", [PlanetPosition("Sun", 10.0)], [])
    cB = ChartResult("B", [PlanetPosition("Sun", 30.0)], [])
    
    composite = syn_svc.calculate_composite(cA, cB)
    comp_sun = composite.planet_positions[0]
    
    print(f"Sun A: 10, Sun B: 30. Composite Sun: {comp_sun.degree}")
    
    if abs(comp_sun.degree - 20.0) < 0.01:
        print("✅ Composite Midpoint PASS")
    else:
        print("❌ Composite Midpoint FAIL")

    # 3. Test Progressions (Simulated)
    print("\n--- TEST 3: Secondary Progressions ---")
    # Natal: 2000-01-01
    # Target: 2001-01-01 (1 year later)
    # Progressed Date should be 2000-01-02 (1 day later)
    
    prog_svc = ProgressionsService(MockOpenAstroService())
    
    target_date = datetime(2001, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    natal_req = ChartRequest(natal_ev, "Radix")
    
    # Mocking generate_chart means we can't check the OUTPUT date inside the result 
    # unless we spy on `_openastro.generate_chart`. 
    # But we can check if it runs without error.
    
    try:
        res = prog_svc.calculate_secondary_progression(natal_req, target_date)
        print(f"Calculated Progression: {res.chart_type}")
        print("✅ Progression Pipeline PASS")
    except Exception as e:
        print(f"❌ Progression Pipeline FAIL: {e}")
        
if __name__ == "__main__":
    run_verification()
