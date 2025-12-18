
import sys
import os
import math

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'src'))

from pillars.geometry.services.vault_of_hestia_shape import VaultOfHestiaShape

shape = VaultOfHestiaShape()
# Default s=10

# Test 1: Set Triangle Leg
# leg = s * sqrt(5) / 2
# Let's set leg = 5. s should become 5 * 2 / sqrt(5) = 2 * sqrt(5) ≈ 4.4721
shape.calculate_from_property("triangle_leg", 5.0)
s = shape.properties["side_length"].value
expected_s = 5.0 * 2 / math.sqrt(5)
print(f"Set Leg=5.0 -> s={s:.4f} (Expected: {expected_s:.4f})")
if abs(s - expected_s) > 1e-4:
    print("FAILED: Leg calculation")
    sys.exit(1)

# Test 2: Set Inradius
# r = s / (2*phi)
# Set r = 1. s should be 2*phi
phi = (1 + math.sqrt(5)) / 2
shape.calculate_from_property("inradius", 1.0)
s = shape.properties["side_length"].value
expected_s = 2 * phi
print(f"Set r=1.0 -> s={s:.4f} (Expected: {expected_s:.4f})")
if abs(s - expected_s) > 1e-4:
    print("FAILED: Inradius calculation")
    sys.exit(1)
    
print("SUCCESS: Bidirectional logic working.")
