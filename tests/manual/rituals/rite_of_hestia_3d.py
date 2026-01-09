"""Rite of Hestia 3D Verification."""
import math
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from pillars.geometry.services.vault_of_hestia_solid import VaultOfHestiaSolidService, VaultOfHestiaSolidCalculator

def verify_hestia_3d():
    print("Beginning Rite of Hestia 3D...")
    
    # 1. Forward Verification
    s = 10.0
    calc = VaultOfHestiaSolidCalculator(side_length=s)
    
    # Check Properties
    phi = (1 + math.sqrt(5)) / 2
    expected_r = s / (2 * phi)
    
    actual_r = calc._properties['sphere_radius'].value
    
    if not math.isclose(actual_r, expected_r, rel_tol=1e-5):
        print(f"❌ Forward Check Failed: Expected r={expected_r}, Got {actual_r}")
        sys.exit(1)
    else:
        print(f"✅ Forward Check Passed: r={actual_r:.4f} for s={s}")

    # 2. Backward Verification (Set r, solve s)
    target_r = 5.0
    calc = VaultOfHestiaSolidCalculator(side_length=1.0) # Init dummy
    calc.set_property('sphere_radius', target_r)
    
    # expected s = r * 2 * phi
    expected_s = target_r * 2 * phi
    actual_s = calc._properties['side_length'].value
    
    if not math.isclose(actual_s, expected_s, rel_tol=1e-5):
        print(f"❌ Backward Check Failed: Expected s={expected_s}, Got {actual_s}")
        sys.exit(1)
    else:
        print(f"✅ Backward Check Passed: s={actual_s:.4f} for r={target_r}")

    # 3. Volume Check
    # s derived from Volume
    target_vol = 1000.0 # Cube volume
    calc.set_property('cube_volume', target_vol)
    actual_s = calc._properties['side_length'].value
    expected_s = 10.0
    
    if not math.isclose(actual_s, expected_s, rel_tol=1e-5):
        print(f"❌ Volume Check Failed: Expected s={expected_s}, Got {actual_s}")
        sys.exit(1)
    else:
        print(f"✅ Volume Check Passed: s={actual_s:.4f} for V={target_vol}")
        
    # 4. Expanded Metrics Verification
    # Diagonal = s * sqrt(3)
    expected_diag = 10.0 * math.sqrt(3)
    actual_diag = calc._properties['cube_diagonal'].value
    if not math.isclose(actual_diag, expected_diag, rel_tol=1e-5):
        print(f"❌ Diagonal Check Failed: Expected {expected_diag}, Got {actual_diag}")
        sys.exit(1)
        
    # Slant Height for h=s, b=s
    # slant = sqrt(h^2 + (b/2)^2) = sqrt(s^2 + s^2/4) = s * sqrt(1.25)
    expected_slant = 10.0 * math.sqrt(1.25)
    actual_slant = calc._properties['pyramid_slant'].value
    if not math.isclose(actual_slant, expected_slant, rel_tol=1e-5):
        print(f"❌ Slant H Check Failed: Expected {expected_slant}, Got {actual_slant}")
        sys.exit(1)
        
    print("✅ Expanded Metrics Verified.")

    # 5. Color Payload Verification
    result = calc._result
    if not result or not result.payload.face_colors:
        print("❌ Color Verification Failed: No face_colors in payload.")
        sys.exit(1)
    
    colors = result.payload.face_colors
    # Expect 6 Cube Faces (Blue), 5 Pyramid (Green), 256 Sphere (Red - 16*16)
    # Check first and last
    # Cube: (0, 0, 255, 60)
    if colors[0] != (0, 0, 255, 60):
        print(f"❌ Cube Color Failed: Got {colors[0]}")
        sys.exit(1)
        
    print("✅ Color Payload Verified (Structure).")
    
    # 6. Theoretical Signatures Verification
    # Pyramid TSA = 2 * phi * s^2
    expected_tsa = 2 * phi * (10.0 ** 2)
    actual_tsa = calc._properties['pyramid_tsa'].value
    if not math.isclose(actual_tsa, expected_tsa, rel_tol=1e-5):
        print(f"❌ TSA Signature Failed: Expected {expected_tsa}, Got {actual_tsa}")
        sys.exit(1)
        
    # Inradius Ratio = phi
    actual_ratio = calc._properties['inradius_ratio'].value
    if not math.isclose(actual_ratio, phi, rel_tol=1e-5):
        print(f"❌ Inradius Ratio Failed: Expected {phi}, Got {actual_ratio}")
        sys.exit(1)
        
    print("✅ Theoretical Signatures Verified (Phi Resonance found).")
    
    print("All Rituals Complete.")

if __name__ == "__main__":
    verify_hestia_3d()
