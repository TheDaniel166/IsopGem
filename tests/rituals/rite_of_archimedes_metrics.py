"""
Rite of Archimedes Metrics
Tests the granular face metrics and bidirectional solving for Archimedean solids.
"""
import sys
import unittest
import math

# Add project root to path
sys.path.append("/home/burkettdaniel927/projects/isopgem/src")

from pillars.geometry.services.archimedean_solids import (
    CuboctahedronSolidCalculator,
    TruncatedTetrahedronSolidCalculator
)

class TestRiteOfArchimedesMetrics(unittest.TestCase):
    
    def test_cuboctahedron_metrics(self):
        """Verify Cuboctahedron has Square and Triangle metrics."""
        calc = CuboctahedronSolidCalculator(edge_length=2.0)
        props = {p.key: p for p in calc.properties()}
        
        # Check keys exist
        self.assertIn("area_3_single", props) # Triangle
        self.assertIn("area_3_total", props)
        self.assertIn("area_4_single", props) # Square
        self.assertIn("area_4_total", props)
        
        # Verify values for edge=2
        # Triangle Area = sqrt(3)/4 * 2^2 = sqrt(3) ~= 1.73205
        triangle_area = math.sqrt(3)
        self.assertAlmostEqual(props["area_3_single"].value, triangle_area, places=4)
        
        # Square Area = 2^2 = 4
        self.assertAlmostEqual(props["area_4_single"].value, 4.0, places=4)
        
        # Total Areas
        # Cuboctahedron has 8 Triangles, 6 Squares
        self.assertAlmostEqual(props["area_3_total"].value, triangle_area * 8, places=4)
        self.assertAlmostEqual(props["area_4_total"].value, 4.0 * 6, places=4)
        
    def test_bidirectional_solving(self):
        """Verify setting derived metrics updates the solid."""
        calc = CuboctahedronSolidCalculator()
        
        # Set Square Area to 16 (implied edge=4)
        calc.set_property("area_4_single", 16.0)
        
        # Verify edge length updated
        props = {p.key: p for p in calc.properties()}
        self.assertAlmostEqual(props["edge_length"].value, 4.0, places=4)
        
        # Verify Triangle Area updated
        # New Triangle Area = sqrt(3)/4 * 16 = 4*sqrt(3) ~= 6.9282
        expected_tri = 4 * math.sqrt(3)
        self.assertAlmostEqual(props["area_3_single"].value, expected_tri, places=4)
        
    def test_truncated_tetrahedron(self):
        """Verify Truncated Tetrahedron (Transitions involved)."""
        calc = TruncatedTetrahedronSolidCalculator(edge_length=1.0)
        props = {p.key: p for p in calc.properties()}
        
        # Has Triangles (4) and Hexagons (4)
        self.assertIn("area_3_single", props)
        self.assertIn("area_6_single", props) 
        
        # Hexagon Area = (3*sqrt(3)/2) * s^2
        # edge=1 -> area ~= 2.59807
        expected_hex = (3 * math.sqrt(3)) / 2
        self.assertAlmostEqual(props["area_6_single"].value, expected_hex, places=4)

if __name__ == '__main__':
    unittest.main()
