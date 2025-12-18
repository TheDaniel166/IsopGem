
import sys
import os
import math

# Add source directory to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from pillars.geometry.services.seed_of_life_shape import SeedOfLifeShape

def run_tests():
    print("Verifying Seed of Life Shape...")
    shape = SeedOfLifeShape()
    shape._init_properties()
    
    # Test 1: Default State (Radius=10)
    print("\n--- Test 1: Default State ---")
    shape.calculate_from_property("radius", 10.0)
    
    r = shape.get_property("radius")
    d = shape.get_property("diameter")
    w = shape.get_property("total_width")
    a = shape.get_property("circle_area") # Single circle area
    
    print(f"Radius: {r}")
    
    if r != 10.0:
        print(f"FAILED: Radius {r} != 10.0")
        sys.exit(1)
        
    if d != 20.0:
        print(f"FAILED: Diameter {d} != 20.0")
        sys.exit(1)
        
    # Total width should be 4*r (from left edge of left circle to right edge of right circle)
    # Center circle at 0. Left circle center at -r. Left edge at -2r.
    # Right circle center at +r. Right edge at +2r.
    # Total width = 4r.
    if w != 40.0:
        print(f"FAILED: Total Width {w} != 40.0")
        sys.exit(1)
        
    print("PASS: Default metrics correct")

    # Test 2: Bidirectional Area
    print("\n--- Test 2: Set Single Circle Area ---")
    # Set area to 100*pi. Radius should become 10.
    target_area = 100.0 * math.pi
    shape.calculate_from_property("circle_area", target_area)
    
    new_r = shape.get_property("radius")
    if abs(new_r - 10.0) > 1e-4:
        print(f"FAILED: Radius {new_r} != 10.0 derived from area {target_area}")
        sys.exit(1)
    print("PASS: Area -> Radius calculation")

    # Test 3: Bidirectional Width
    print("\n--- Test 3: Set Total Width ---")
    # Set width to 100. Radius should be 25.
    shape.calculate_from_property("total_width", 100.0)
    
    new_r = shape.get_property("radius")
    if abs(new_r - 25.0) > 1e-4:
        print(f"FAILED: Radius {new_r} != 25.0 derived from width 100")
        sys.exit(1)
    print("PASS: Width -> Radius calculation")

    # Test 4: Vesica Area & Flower Area
    print("\n--- Test 4: Area Metrics ---")
    shape.calculate_from_property("radius", 10.0)
    # Vesica area formula check
    # r=10. Area = 100 * (2pi/3 - sqrt(3)/2)
    expected_vesica = 100.0 * (2 * math.pi / 3 - math.sqrt(3) / 2) # ~122.837
    actual_vesica = shape.get_property("vesica_area")
    
    if abs(actual_vesica - expected_vesica) > 1e-4:
        print(f"FAILED: Vesica Area {actual_vesica} != {expected_vesica}")
        sys.exit(1)
        
    actual_flower = shape.get_property("flower_area")
    if abs(actual_flower - 6 * expected_vesica) > 1e-4:
        print(f"FAILED: Flower Area {actual_flower} != {6 * expected_vesica}")
        sys.exit(1)
        
    # Test bidirectional Flower Area
    target_flower_area = 600.0
    shape.calculate_from_property("flower_area", target_flower_area)
    # r = sqrt( (600/6) / factor ) = sqrt(100 / factor)
    # factor ~ 1.22837...
    # r^2 = 81.4... -> r ~ 9.02...
    new_flower = shape.get_property("flower_area")
    if abs(new_flower - target_flower_area) > 1e-4:
        print(f"FAILED: Loopback Flower Area {new_flower} != {target_flower_area}")
        sys.exit(1)
    
    print("PASS: Area Metrics Verified")

    # Test 5: Perimeters
    print("\n--- Test 5: Perimeters ---")
    shape.calculate_from_property("radius", 10.0)
    # Perimeter should be 4 * pi * r = 40pi
    expected_perim = 40.0 * math.pi
    actual_perim = shape.get_property("flower_perimeter")
    
    if abs(actual_perim - expected_perim) > 1e-4:
        print(f"FAILED: Flower Perimeter {actual_perim} != {expected_perim}")
        sys.exit(1)
        
    print("PASS: Perimeters Verified")

if __name__ == "__main__":
    run_tests()
