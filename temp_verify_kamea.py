import sys
import os

# Adjust path to find the src module
sys.path.append(os.path.abspath("/home/burkettdaniel927/projects/isopgem/src"))

from pillars.tq.services.kamea_grid_service import KameaGridService
import logging

# Configure simple logging
logging.basicConfig(level=logging.INFO)

def verify_grid():
    service = KameaGridService()
    print("Initializing Service...")
    service.initialize()
    
    print("\n--- Testing Coordinate Bounds ---")
    # Test Corners
    corners = [(-13, 13), (13, 13), (-13, -13), (13, -13)]
    for x, y in corners:
        cell = service.get_cell(x, y)
        if cell:
            print(f"Corner ({x}, {y}): {cell.ternary_value} (Dec: {cell.decimal_value}) -> Locator: {cell.kamea_locator}")
        else:
            print(f"Corner ({x}, {y}): MISSING!")

    print("\n--- Testing Center ---")
    center = service.get_cell(0, 0)
    if center:
        print(f"Center (0, 0): {center.ternary_value} (Dec: {center.decimal_value}) -> Locator: {center.kamea_locator}")
        if center.decimal_value != 0:
            print("ERROR: Center should be 0!")
    else:
        print("Center MISSING!")

    print("\n--- Testing Bigram Logic (Spot Check) ---")
    # Spot check a known value if possible, or just print properties
    # Let's check (5, 5) just as a random point
    spot = service.get_cell(5, 5)
    if spot:
        print(f"Spot (5, 5): {spot.ternary_value} -> Bigrams: {spot.bigrams} -> Family: {spot.family_id}")
        
    print("\n--- Testing Ditrunal Service ---")
    from pillars.tq.services.ditrunal_service import DitrunalService
    
    # Test a known Concurrent from Family 8 (Abyss)
    # 222222 is Prime. Let's find a Concurrent.
    # From csv: (-13, 13) is 111000. Let's mutate it.
    test_val = "111000"
    print(f"Testing Mutation for {test_val}...")
    
    # Step 1
    m1 = DitrunalService.nuclear_mutation(test_val)
    print(f"Mutation 1: {m1}")
    
    # Find Prime
    prime = DitrunalService.find_prime(test_val)
    print(f"Resolved Prime: {prime}")
    fid = DitrunalService.get_family_id(test_val)
    print(f"Family ID: {fid}")
    
    # Test Cycle 5/7
    # 121212 -> 212121 -> 121212
    val5 = "121212"
    val7 = "212121"
    print(f"Prime 5 ({val5}) resolves to: {DitrunalService.find_prime(val5)}")
    print(f"Prime 7 ({val7}) resolves to: {DitrunalService.find_prime(val7)}")

    # Test Stability of Dynamic Primes (The 'Missing Step' Fix)
    # Family 3 Prime: 101010. Should resolve to itself, not 010101 (Fam 1).
    p3 = "101010"
    res3 = DitrunalService.find_prime(p3)
    print(f"Stability Check: {p3} (Fam 3) -> {res3} [{'PASS' if res3 == p3 else 'FAIL'}]")

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    verify_grid()
