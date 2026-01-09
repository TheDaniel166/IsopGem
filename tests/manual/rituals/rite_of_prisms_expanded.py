"""Verification Ritual for Expanded Prisms and Antiprisms."""
import sys
import os
import math

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from pillars.geometry.services import (
    GeneralPrismSolidCalculator,
    GeneralAntiprismSolidCalculator,
    SnubAntiprismSolidService,
    GyroelongatedSquarePrismSolidService
)

def test_general_prism():
    print("Testing General Prism (n=5)...")
    calc = GeneralPrismSolidCalculator(sides=5, base_edge=2.0, height=4.0)
    payload = calc.payload()
    # n=5 prism: 2 pentagons, 5 rectangles => 7 faces
    if len(payload.faces) != 7:
        print(f"❌ General Prism Faces Failed: Got {len(payload.faces)}, Expected 7")
        sys.exit(1)
        
    print("Updating to n=7...")
    calc.set_property('sides', 7)
    payload = calc.payload()
    # n=7 prism: 2 heptagons, 7 rectangles => 9 faces
    if len(payload.faces) != 9:
        print(f"❌ General Prism (n=7) Faces Failed: Got {len(payload.faces)}, Expected 9")
        sys.exit(1)
    print("✅ General Prism Verified.")

def test_general_antiprism():
    print("Testing General Antiprism (n=3)...")
    calc = GeneralAntiprismSolidCalculator(sides=3, base_edge=2.0, height=4.0)
    payload = calc.payload()
    # n=3 antiprism (octahedron-like): 2 triangles, 6 lateral triangles => 8 faces
    if len(payload.faces) != 8:
        print(f"❌ General Antiprism Faces Failed: Got {len(payload.faces)}, Expected 8")
        sys.exit(1)
    print("✅ General Antiprism Verified.")

def test_snub_antiprism():
    print("Testing Snub Square Antiprism (J85)...")
    result = SnubAntiprismSolidService.build(edge=2.0)
    payload = result.payload
    # J85: 2 squares + 24 triangles = 26 faces
    if len(payload.faces) != 26:
        print(f"❌ J85 Faces Failed: Got {len(payload.faces)}, Expected 26")
        sys.exit(1)
    if len(payload.vertices) != 16:
        print(f"❌ J85 Vertices Failed: Got {len(payload.vertices)}, Expected 16")
        sys.exit(1)
    print("✅ Snub Antiprism Verified.")

def test_gyro_prism():
    print("Testing Gyroelongated Square Prism...")
    result = GyroelongatedSquarePrismSolidService.build(edge=2.0, prism_h=2.0, anti_h=1.414)
    payload = result.payload
    # 2 squares, 4 prism rectangles, 8 antiprism triangles = 14 faces
    if len(payload.faces) != 14:
        print(f"❌ Gyro-Prism Faces Failed: Got {len(payload.faces)}, Expected 14")
        sys.exit(1)
    print("✅ Gyroelongated Square Prism Verified.")

if __name__ == "__main__":
    print("Beginning Rite of Prisms Expanded...")
    test_general_prism()
    test_general_antiprism()
    test_snub_antiprism()
    test_gyro_prism()
    print("All Prismatic Rituals Complete. The Expanded Pillar is manifest.")
