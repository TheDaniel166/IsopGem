
import sys
import os
import math

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'src'))

from pillars.geometry.services.vault_of_hestia_shape import VaultOfHestiaShape

shape = VaultOfHestiaShape()

# Test 1: Default values (s=10)
print("--- Test 1: Default (s=10) ---")
shape.calculate_from_property("side_length", 10.0)

s = 10.0
# Circumradius = 5/8 * s = 6.25
if abs(shape.get_property("circumradius") - 6.25) > 1e-5:
    print(f"FAILED: circumradius {shape.get_property('circumradius')} != 6.25")
    sys.exit(1)
print("PASS: Circumradius")

# Base Angle = atan(2) = 63.4349...
if abs(shape.get_property("base_angle") - 63.4349488) > 1e-4:
     print(f"FAILED: base_angle {shape.get_property('base_angle')} != 63.4349...")
     sys.exit(1)
print("PASS: Base Angle")

# Test 2: Bidirectional Circumradius
print("\n--- Test 2: Set Circumradius = 5.0 ---")
# If R=5, then s = 5 * (8/5) = 8.0
shape.calculate_from_property("circumradius", 5.0)
s_new = shape.get_property("side_length")
if abs(s_new - 8.0) > 1e-5:
    print(f"FAILED: side_length {s_new} != 8.0")
    sys.exit(1)
print("PASS: Bidirectional Circumradius (R=5 -> s=8)")

# Test 3: Bidirectional Diagonal
print("\n--- Test 3: Set Square Diagonal = 14.1421... (10*sqrt(2)) ---")
shape.calculate_from_property("square_diagonal", 10 * math.sqrt(2))
s_diag = shape.get_property("side_length")
if abs(s_diag - 10.0) > 1e-4:
    print(f"FAILED: side_length {s_diag} != 10.0")
    sys.exit(1)
print("PASS: Bidirectional Diagonal")

# Test 4: Bidirectional Diameter
print("\n--- Test 4: Set Diameter = 10.0 ---")
shape.calculate_from_property("circle_diameter", 10.0)
# r = 5.0. s = 2 * phi * 5 = 10 * phi = 16.1803...
s_diam = shape.get_property("side_length")
expected_s = 16.18033988
if abs(s_diam - expected_s) > 1e-4:
    print(f"FAILED: side_length {s_diam} != {expected_s}")
    sys.exit(1)
print("PASS: Bidirectional Diameter")

# Test 5: Verify Area Differences (s=10)
print("\n--- Test 5: Area Differences (s=10) ---")
shape.calculate_from_property("side_length", 10.0)
sq_area = 100.0
tri_area = 50.0
# r = 10 / (2*phi) = 3.0901699...
r = 10.0 / (2*((1 + math.sqrt(5))/2))
circ_area = math.pi * r * r # ~29.998...

diff_sq_tri = shape.get_property("area_sq_minus_tri")
expected_diff_1 = sq_area - tri_area # 50.0
if abs(diff_sq_tri - expected_diff_1) > 1e-4:
    print(f"FAILED: area_sq_minus_tri {diff_sq_tri} != {expected_diff_1}")
    sys.exit(1)
    
diff_tri_circ = shape.get_property("area_tri_minus_circ")
expected_diff_2 = tri_area - circ_area
if abs(diff_tri_circ - expected_diff_2) > 1e-4:
    print(f"FAILED: area_tri_minus_circ {diff_tri_circ} != {expected_diff_2}")
    sys.exit(1)
print("PASS: Area Differences Verified")

print("\nSUCCESS: All expanded calculations verified.")
