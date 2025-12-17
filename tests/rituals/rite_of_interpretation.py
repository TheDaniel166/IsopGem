"""Rite of Interpretation: Verification of the Chart Interpretation Service."""
import sys
import os
from pathlib import Path

# Fix path to include src/
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root / "src"))

from datetime import datetime
from unittest.mock import MagicMock

# Mock requests before importing services that rely on it
sys.modules["requests"] = MagicMock()
sys.modules["sqlalchemy"] = MagicMock()
sys.modules["sqlalchemy.orm"] = MagicMock()
# sys.modules["shared"] = MagicMock() # Don't mock the root if we need submodules unless we structure it carefully
sys.modules["shared.database"] = MagicMock()
# Mock shared.utils.text_utils as it is used
sys.modules["shared.utils"] = MagicMock()
sys.modules["shared.utils.text_utils"] = MagicMock()
sys.modules["swisseph"] = MagicMock()

from pillars.astrology.models.chart_models import ChartResult, PlanetPosition, HousePosition, AstrologyEvent, GeoLocation
from pillars.astrology.services.interpretation_service import InterpretationService
from pillars.astrology.repositories.interpretation_repository import InterpretationRepository

def test_combinatorial_interpretation():
    print("Testing Combinatorial Interpretation (Sun in Aries in House 1)...")
    
    # 1. Setup Mock Data
    # Sun at 15 degrees Aries (sign index 0)
    sun = PlanetPosition(name="Sun", degree=15.0, sign_index=0)
    
    # House 1: 0 to 30 degrees (Aries)
    houses = [
        HousePosition(number=1, degree=0.0),
        HousePosition(number=2, degree=30.0),
        HousePosition(number=3, degree=60.0),
        HousePosition(number=4, degree=90.0),
        HousePosition(number=5, degree=120.0),
        HousePosition(number=6, degree=150.0),
        HousePosition(number=7, degree=180.0), # Descendant
        HousePosition(number=8, degree=210.0),
        HousePosition(number=9, degree=240.0),
        HousePosition(number=10, degree=270.0), # MC
        HousePosition(number=11, degree=300.0),
        HousePosition(number=12, degree=330.0),
    ]
    
    chart_result = ChartResult(
        chart_type="Radix",
        planet_positions=[sun],
        house_positions=houses
    )
    
    # 2. Init Service
    # We rely on the real repository loading the dummy files we created
    repo = InterpretationRepository()
    service = InterpretationService(repository=repo)
    
    # 3. Interpret
    report = service.interpret_chart(chart_result)
    
    # 4. Verify
    print("\n--- Report Generated ---")
    print(report.to_markdown())
    print("------------------------\n")
    
    found_triad = False
    for segment in report.segments:
        if "Triad" in segment.tags:
            found_triad = True
            print("[SAFE] Found Triad interpretation.")
            if "Double Aries influence" in segment.content.text:
                print("[SAFE] Body text matches expected content.")
            else:
                print("[WARN] Body text mismatch:", segment.content.text)
                sys.exit(1)
        
        if segment.title == "Sun in Aries":
            print("[WARN] Fallback 'Sun in Aries' segment found. This should NOT happen if Triad is found, unless we output both?")
            # Ideally we only output the specific one if found, or maybe both?
            # Current logic: If Triad found, it adds it. 
            # BUT the else block prevents the fallback.
            # So we should NOT see "Sun in Aries" separately if Triad worked.
            sys.exit(1)

    if not found_triad:
        print("[FAIL] Did not find Triad interpretation.")
        sys.exit(1)

    print("[PASS] Combinatorial Interpretation Verified.")

def test_fallback_logic():
    print("\nTesting Fallback Logic (Moon in Aries - No House Data)...")
    
    # Moon at 15 Aries (Sign 0). 
    # But let's say it's in House 2. We don't have combinatorial data for Moon in House 2 in our dummy file.
    # We only have data for Sun.
    
    moon = PlanetPosition(name="Moon", degree=15.0, sign_index=0)
    
    # House 2: 0 to 30 (wait, houses above cover 0-30 for H1)
    # Let's put Moon at 45 degrees (Taurus, Sign 1) in House 2.
    # Wait, simple test: Moon in Aries (15 deg), House 1.
    # We DO NOT have combinatorial text for Moon-Aries-H1 in dummy file.
    # So it should fallback to Moon in Aries + Moon in House 1.
    
    houses = [HousePosition(number=i, degree=(i-1)*30) for i in range(1, 13)]
    
    chart_result = ChartResult(
        chart_type="Radix",
        planet_positions=[moon],
        house_positions=houses
    )
    
    repo = InterpretationRepository()
    service = InterpretationService(repository=repo)
    report = service.interpret_chart(chart_result)
    
    found_sign = False
    found_house = False
    found_triad = False
    
    for segment in report.segments:
        if "Triad" in segment.tags:
            found_triad = True
        if segment.title == "Moon in Aries":
            found_sign = True
        if segment.title == "Moon in House 1":
            found_house = True
            
    if found_triad:
        print("[FAIL] Found Triad for Moon, but none exists in dummy data.")
        sys.exit(1)
        
    if found_sign and found_house:
        print("[PASS] Fallback successful: Found both Sign and House interpretations.")
        
        # Verify content richness
        sign_segment = next(s for s in report.segments if s.title == "Moon in Aries")
        if sign_segment.content.archetype == "The Emotional Warrior":
            print("[SAFE] Sign interpretation has correct archetype.")
        else:
            print(f"[WARN] Sign interpretation missing archetype. Got: {sign_segment.content.archetype}")
            sys.exit(1)
            
        house_segment = next(s for s in report.segments if s.title == "Moon in House 1")
        # Note: In our dummy data above (write_to_file), we set Moon/1 archetype to "The Feeler".
        # Ensure we are testing against the actual file content we just wrote.
        if house_segment.content.archetype == "The Feeler":
             print("[SAFE] House interpretation has correct archetype.")
        else:
             print(f"[WARN] House interpretation missing expected archetype. Got: {house_segment.content.archetype}")
             sys.exit(1)

    else:
        print(f"[FAIL] Missing fallback segments. Sign: {found_sign}, House: {found_house}")
        sys.exit(1)

if __name__ == "__main__":
    test_combinatorial_interpretation()
    test_fallback_logic() 
