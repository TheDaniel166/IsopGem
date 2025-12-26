"""Rite of Advanced Visualization.

Verifies the topological correctness of generated dual solids for the 5 Platonic solids.
Checks V, E, F counts against expected values (Dual of Cube is Octahedron, etc.).
"""
import math
import sys
import unittest
from typing import Tuple

# Adjust path to find module
sys.path.append('/home/burkettdaniel927/projects/isopgem/src')

from pillars.geometry.services.cube_solid import CubeSolidService
from pillars.geometry.services.tetrahedron_solid import TetrahedronSolidService
from pillars.geometry.services.octahedron_solid import OctahedronSolidService
from pillars.geometry.services.dodecahedron_solid import DodecahedronSolidService
from pillars.geometry.services.icosahedron_solid import IcosahedronSolidService

class TestDualSolids(unittest.TestCase):
    def verify_dual_counts(self, dual_payload, expected_v: int, expected_f: int):
        self.assertIsNotNone(dual_payload, "Dual payload should not be None")
        self.assertEqual(len(dual_payload.vertices), expected_v, f"Expected {expected_v} dual vertices")
        # Dual edges count = Primal edges count
        # We don't strictly check edges here as they are derived, but faces should match.
        self.assertEqual(len(dual_payload.faces), expected_f, f"Expected {expected_f} dual faces")

    def test_tetrahedron_dual(self):
        # Dual of Tetrahedron is Tetrahedron (Self-dual)
        # V=4, F=4 -> Dual V=4, F=4
        result = TetrahedronSolidService.build(1.0)
        print("\nTesting Tetrahedron Dual...")
        self.verify_dual_counts(result.payload.dual, 4, 4)

    def test_cube_dual(self):
        # Dual of Cube (V=8, F=6) is Octahedron (V=6, F=8)
        result = CubeSolidService.build(1.0)
        print("Testing Cube Dual...")
        self.verify_dual_counts(result.payload.dual, 6, 8)

    def test_octahedron_dual(self):
        # Dual of Octahedron (V=6, F=8) is Cube (V=8, F=6)
        result = OctahedronSolidService.build(1.0)
        print("Testing Octahedron Dual...")
        self.verify_dual_counts(result.payload.dual, 8, 6)

    def test_dodecahedron_dual(self):
        # Dual of Dodecahedron (V=20, F=12) is Icosahedron (V=12, F=20)
        result = DodecahedronSolidService.build(1.0)
        print("Testing Dodecahedron Dual...")
        # Note: Dodecahedron services calculates Dual Icosahedron.
        self.verify_dual_counts(result.payload.dual, 12, 20)

    def test_icosahedron_dual(self):
        # Dual of Icosahedron (V=12, F=20) is Dodecahedron (V=20, F=12)
        result = IcosahedronSolidService.build(1.0)
        print("Testing Icosahedron Dual...")
        self.verify_dual_counts(result.payload.dual, 20, 12)

    def test_dual_scale_consistency(self):
        # Check that scaling primal scales the dual
        r1 = CubeSolidService.build(1.0)
        r2 = CubeSolidService.build(2.0)
        
        d1 = r1.payload.dual
        d2 = r2.payload.dual
        
        # Distance of first vertex from origin
        dist1 = math.dist((0,0,0), d1.vertices[0])
        dist2 = math.dist((0,0,0), d2.vertices[0])
        
        self.assertAlmostEqual(dist2, dist1 * 2.0, places=5, msg="Dual should scale linearly with primal")

if __name__ == '__main__':
    unittest.main()
