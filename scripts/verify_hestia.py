import sys
import os
sys.path.append(os.getcwd())
# Add src to path if needed, but usually running from root works if structured correctly
sys.path.append(os.path.join(os.getcwd(), 'src'))

try:
    from pillars.geometry.services import VaultOfHestiaShape
    print("Import successful.")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

shape = VaultOfHestiaShape()
success = shape.calculate_from_property('side_length', 10.0)

if not success:
    print("Calculation failed.")
    sys.exit(1)

r = shape.properties['inradius'].value
phi_check = shape.properties['phi_check'].value

print(f"Side: 10.0")
print(f"Inradius: {r}")
print(f"Phi Check (s/2r): {phi_check}")

# Golden Ratio is approx 1.61803398875
if abs(phi_check - 1.61803398875) < 0.0001:
    print("VERIFICATION PASSED: Golden Ratio confirmed.")
else:
    print("VERIFICATION FAILED: Phi check mismatch.")
