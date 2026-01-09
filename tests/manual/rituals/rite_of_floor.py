"""
RITE OF THE FLOOR
"The step is measured, the boundary fixed."

Verification ritual for the Adyton's Precision Floor.
"""
import sys
import os
import math

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from pillars.adyton.models.floor import FloorGeometry
from pillars.adyton.constants import (
    PERIMETER_SIDE_LENGTH,
    KATALYSIS_SIDE_LENGTH,
    VOWEL_RING_COLORS
)

def break_seal_floor():
    print("☉ BREAKING THE SEAL: FLOOR PRECISION")
    
    floor = FloorGeometry.build()
    faces = floor.faces
    
    # Requirement 1: Face Count (1 field + 7 vowel segments + 1 core)
    print(f"  [✓] Saturn: Found {len(faces)} faces.")
    assert len(faces) == 9, f"Expected 9 faces, found {len(faces)}"
    
    # Requirement 2: Perimeter Side Length (Outer Heptagon)
    outer_face = faces[0]
    v0 = outer_face.vertices[0]
    v1 = outer_face.vertices[1]
    side_len = (v1 - v0).length()
    print(f"  [✓] Sun: Perimeter side length measured at {side_len:.2f} (Target: {PERIMETER_SIDE_LENGTH})")
    assert abs(side_len - PERIMETER_SIDE_LENGTH) < 0.01, f"Side length mismatch: {side_len}"

    # Requirement 3: Katalysis Side Length (Inner Heptagon/Vowel Ring inner edge)
    # The vowel ring segments are faces[1:8]
    vowel_face = faces[1]
    # Vertices are [o0, o1, r1, r0]. r1-r0 should be Katalysis side.
    r1 = vowel_face.vertices[2]
    r0 = vowel_face.vertices[3]
    inner_side_len = (r1 - r0).length()
    print(f"  [✓] Sun: Katalysis side length measured at {inner_side_len:.2f} (Target: {KATALYSIS_SIDE_LENGTH})")
    assert abs(inner_side_len - KATALYSIS_SIDE_LENGTH) < 0.01, f"Inner side length mismatch: {inner_side_len}"

    # Requirement 4: Vowel Ring Colors
    print("  [✓] Venus: Verifying Amun Color Map (Phi-based)...")
    for i in range(7):
        assert faces[i+1].color == VOWEL_RING_COLORS[i], f"Vowel color mismatch at index {i}"
        
    print("\n[✓] ALL SEALS BROKEN: THE FLOOR IS REVEALED")

if __name__ == "__main__":
    try:
        break_seal_floor()
    except Exception as e:
        print(f"\n[X] RITE FAILED: {e}")
        sys.exit(1)
