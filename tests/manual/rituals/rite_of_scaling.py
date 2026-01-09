"""
RITE OF SCALING
"The wall is bound to the corner, the corner to the circle."

Verification ritual for Adyton wall-to-floor alignment.
"""
import sys
import os
import math

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from pillars.adyton.models.prism import SevenSidedPrism
from pillars.adyton.constants import (
    PERIMETER_SIDE_LENGTH,
    KATALYSIS_SIDE_LENGTH,
    Z_BIT_INCHES
)

def break_seal_scaling():
    print("☉ BREAKING THE SEAL: ARCHITECTURAL SCALING")
    
    # 1. Test Chord Solver
    print("  [✓] Saturn: Testing Chord Solver (14-gon regular/irregular)...")
    c = Z_BIT_INCHES # 19
    w = KATALYSIS_SIDE_LENGTH # 166
    
    alpha_rad, beta_rad, V = SevenSidedPrism._solve_corner_wall_angles(c, w)
    
    # Check if sum of angles covers 1/7th of 360
    total_sector_rad = (alpha_rad + beta_rad) * 7
    print(f"      Total 14-gon rotation: {math.degrees(total_sector_rad):.2f}° (Target: 360°)")
    assert abs(math.degrees(total_sector_rad) - 360.0) < 0.001

    # Check the Side Length (Corner chord + Wall chord projection? No, the side of the Perimeter heptagon)
    # The Perimeter Heptagon is defined as having side 185.
    # In an irregular 14-gon, the 'effective' side is the distance between main sector vertices?
    # Actually, the documents implies Perimeter = 7 * (C + W) for a flattened boundary.
    # But in 3D geometry, it's a 14-gon.
    
    # Let's verify our C (19) and W (166) indeed sum to 185.
    print(f"  [✓] Sun: Verifying Linear Sum (19 + 166): {c + w}")
    assert (c + w) == PERIMETER_SIDE_LENGTH
    
    # 2. Verify Prism Construction
    print("  [✓] Mars: Checking total Sanctuary objects...")
    objects = SevenSidedPrism.build()
    # 1 Floor, 7 Corners, 7 Walls
    assert len(objects) == 1 + 7 + 7, f"Expected 15 objects, found {len(objects)}"

    print("\n[✓] ALL SEALS BROKEN: THE SCALING IS PERFECTED")

if __name__ == "__main__":
    try:
        break_seal_scaling()
    except Exception as e:
        print(f"\n[X] RITE FAILED: {e}")
        sys.exit(1)
