import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from pillars.adyton.services.kamea_loader_service import KameaLoaderService

def verify_map():
    loader = KameaLoaderService(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    wall_map = loader.load_wall_map()
    
    print(f"Loaded {len(wall_map)} entries in Wall Map.")
    
    # Test Cases from zodiacal_heptagon.csv
    # Set 1: A1=1, B1=2 -> Wall 0 (Sun)
    # Set 1: A2=137, B2=190 -> Wall 1 (Mercury)
    # Set 1: A7=349, B7=662 -> Wall 6 (Saturn)
    
    test_cases = [
        (1, 0, "Sun"),
        (2, 0, "Sun"),
        (137, 1, "Mercury"),
        (190, 1, "Mercury"),
        (349, 6, "Saturn"),
        (662, 6, "Saturn"),
        (200, 0, "Sun (Wall 0 Row 1 Col 1 in sun_wall.csv?) - Wait, sun_wall.csv is display, zodiacal matches Set logic.")
    ]
    
    passed = 0
    for val, expected_wall, name in test_cases:
        actual = wall_map.get(val, -1)
        status = "PASS" if actual == expected_wall else "FAIL"
        print(f"Value {val}: Expected {expected_wall} ({name}), Got {actual} -> {status}")
        if status == "PASS": passed += 1
        
    print(f"\nVerification Results: {passed}/{len(test_cases)} Passed")
    
    # Check total coverage
    # Expect 7 maps * 52 sets * 2 values = 728 values?
    # Some values might repeat or be missing if CSV is partial?
    # zodiacal_heptagon.csv has 53 lines (Header + 52 sets).
    # So 52 * 7 * 2 = 728.
    # Plus Axis Mundi (364) maybe not in there?
    
    print(f"Total mapped values: {len(wall_map)}")
    missing = [i for i in range(729) if i not in wall_map and i != 364]
    if missing:
        print(f"Missing Values (excluding 364): {len(missing)}")
        print(f"first 10 missing: {missing[:10]}")
    else:
        print("All values 0-728 (except 364) are mapped.")

if __name__ == "__main__":
    verify_map()
