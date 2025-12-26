"""
Rite of Calculator Refinement
Tests the granular metrics and bidirectional solving for Cylinders and Cones.
"""
import sys
import unittest
import math

# Add project root to path
sys.path.append("/home/burkettdaniel927/projects/isopgem/src")

from pillars.geometry.services.cylinder_solid import CylinderSolidCalculator
from pillars.geometry.services.cone_solid import ConeSolidCalculator

class TestRiteOfCalculatorRefinement(unittest.TestCase):
    
    def test_cylinder_solving(self):
        """Verify Cylinder bidirectional metrics."""
        # r=1, h=2. Base Area = pi. Lateral = 4pi. Total = 6pi.
        calc = CylinderSolidCalculator(radius=1.0, height=2.0)
        props = {p.key: p for p in calc.properties()}
        
        self.assertIn("circumference", props)
        self.assertAlmostEqual(props["circumference"].value, 2 * math.pi, places=4)
        
        # Test 1: Set Base Area -> solves for Radius
        # Set Area = 4pi => r should be 2
        calc.set_property("base_area", 4 * math.pi)
        self.assertAlmostEqual(props["radius"].value, 2.0, places=4)
        
        # Test 2: Set Lateral Area -> solves for Height (since r=2 is set)
        # L = 2*pi*r*h. Set L = 8pi. With r=2 -> 8pi = 4pi*h -> h=2
        calc.set_property("lateral_area", 8 * math.pi)
        self.assertAlmostEqual(props["height"].value, 2.0, places=4)
        
        # Test 3: Set Surface Area -> solves for Height (if r valid)
        # A = 2pi*r(r+h). Let's aim for h=3, r=2.
        # A = 2pi*2*(2+3) = 4pi*5 = 20pi.
        calc.set_property("surface_area", 20 * math.pi)
        self.assertAlmostEqual(props["height"].value, 3.0, places=4)
        self.assertAlmostEqual(props["radius"].value, 2.0, places=4) # r shouldn't change
        
    def test_cone_solving(self):
        """Verify Cone bidirectional metrics."""
        # r=3, h=4 -> s=5. 
        # Base=9pi. Lateral=15pi. Total=24pi.
        calc = ConeSolidCalculator(radius=3.0, height=4.0)
        props = {p.key: p for p in calc.properties()}
        
        self.assertIn("base_circumference", props)
        
        # Test 1: Set Base Area -> solves for Radius
        # Set B = 16pi => r=4
        calc.set_property("base_area", 16 * math.pi)
        self.assertAlmostEqual(props["radius"].value, 4.0, places=4)
        
        # Test 2: Set Lateral Area -> solves for Slant -> Height
        # r=4. Set L = 20pi. L = pi*r*s => 20pi = 4pi*s => s=5.
        # h = sqrt(s^2 - r^2) = sqrt(25-16) = 3.
        calc.set_property("lateral_area", 20 * math.pi)
        self.assertAlmostEqual(props["slant_height"].value, 5.0, places=4)
        self.assertAlmostEqual(props["height"].value, 3.0, places=4)
        
        # Test 3: Set Surface Area -> solves for Height
        # r=4. Let's aim for h=3 (total area = 36pi, Wait. L=20pi, B=16pi. Total=36pi).
        # Let's set Total Area to 36pi. Should keep h=3, r=4.
        self.assertAlmostEqual(props["height"].value, 3.0, places=4)

    def test_pyramid_solving(self):
        """Verify Pyramid bidirectional metrics (Square Pyramid)."""
        from pillars.geometry.services.regular_pyramid_solids import RegularPyramidSolidCalculatorBase, RegularPyramidSolidServiceBase
        
        # Mock class for Square Pyramid (sides=4)
        class SquarePyramidCalc(RegularPyramidSolidCalculatorBase):
            SIDES = 4
            SERVICE = RegularPyramidSolidServiceBase # Base service defaults to 3 but we can override build? 
            # Actually RegularPyramidSolidServiceBase uses cls.SIDES. 
            # Let's use the actual Hexagonal or create a dummy class structure properly.
            
        # Let's use HexagonalPyramidSolidCalculator from imports if we can, or just mock properly.
        # Ideally we import the actual calculator to be safe.
        from pillars.geometry.services.regular_pyramid_solids import HexagonalPyramidSolidCalculator
        
        # Hex Pyramid: s=2, h=3.
        # Base Edge = 2. Sides = 6.
        calc = HexagonalPyramidSolidCalculator(base_edge=2.0, height=3.0)
        props = {p.key: p for p in calc.properties()}
        
        # Test 1: Set Lateral Area -> solve Height
        # Current L value?
        original_L = props['lateral_area'].value
        # Double the L?
        target_L = original_L * 1.5
        calc.set_property('lateral_area', target_L)
        self.assertAlmostEqual(props['lateral_area'].value, target_L, places=4)
        self.assertNotAlmostEqual(props['height'].value, 3.0) # Height should change

    def test_prism_solving(self):
        """Verify Prism bidirectional metrics."""
        from pillars.geometry.services.regular_prism_solids import HexagonalPrismSolidCalculator
        
        # Hex Prism: s=1, h=5.
        calc = HexagonalPrismSolidCalculator(base_edge=1.0, height=5.0)
        props = {p.key: p for p in calc.properties()}
        
        # Test 1: Set Lateral Area -> solve Height
        # L = P*h = (6*1)*5 = 30.
        self.assertAlmostEqual(props['lateral_area'].value, 30.0, places=4)
        
        # Set L=60 -> h should be 10 (keeping s=1)
        calc.set_property('lateral_area', 60.0)
        self.assertAlmostEqual(props['height'].value, 10.0, places=4)
        self.assertAlmostEqual(props['base_edge'].value, 1.0, places=4)

    def test_antiprism_solving(self):
        """Verify Antiprism bidirectional metrics."""
        from pillars.geometry.services.regular_antiprism_solids import SquareAntiprismSolidCalculator
        
        # Square Antiprism: s=2, h=4
        calc = SquareAntiprismSolidCalculator(base_edge=2.0, height=4.0)
        props = {p.key: p for p in calc.properties()}
        
        # Test 1: Set Lateral Area -> solve Height
        original_L = props['lateral_area'].value
        # If we double L, height should increase (since base edge fixed)
        calc.set_property('lateral_area', original_L * 2.0)
        self.assertGreater(props['height'].value, 4.0)
        self.assertAlmostEqual(props['base_edge'].value, 2.0, places=4)
        
    def test_frustum_solving(self):
        """Verify Frustum bidirectional metrics."""
        from pillars.geometry.services.regular_pyramid_frustum_solids import HexagonalPyramidFrustumSolidCalculator
        
        # Hex Frustum: s=2, top=1, h=1
        calc = HexagonalPyramidFrustumSolidCalculator(base_edge=2.0, top_edge=1.0, height=1.0)
        props = {p.key: p for p in calc.properties()}
        
        # Test 1: Set Lateral Area -> solve Height
        original_L = props['lateral_area'].value
        # Increase L, Height should increase
        calc.set_property('lateral_area', original_L * 1.5)
        self.assertGreater(props['height'].value, 1.0)
        self.assertAlmostEqual(props['base_edge'].value, 2.0, places=4)
        self.assertAlmostEqual(props['top_edge'].value, 1.0, places=4)

if __name__ == '__main__':
    unittest.main()
