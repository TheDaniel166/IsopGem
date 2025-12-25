"""Unit tests for 2D Triangle shapes."""
import math
import pytest
from src.pillars.geometry.services.triangle_shape import (
    RightTriangleShape,
    IsoscelesTriangleShape,
    EquilateralTriangleShape,
    TriangleSolution
)

class TestRightTriangle:
    def test_base_height_calc(self):
        """Test calculating from base and height."""
        triangle = RightTriangleShape()
        assert triangle.calculate_from_property('base', 3.0)
        assert triangle.calculate_from_property('height', 4.0)
        
        assert triangle.get_property('hypotenuse') == pytest.approx(5.0)
        assert triangle.get_property('area') == pytest.approx(6.0)
        assert triangle.get_property('perimeter') == pytest.approx(12.0)

    def test_hypotenuse_base_calc(self):
        """Test calculating from hypotenuse and base."""
        triangle = RightTriangleShape()
        assert triangle.calculate_from_property('hypotenuse', 5.0)
        assert triangle.calculate_from_property('base', 3.0)
        
        assert triangle.get_property('height') == pytest.approx(4.0)
        assert triangle.get_property('area') == pytest.approx(6.0)

    def test_area_height_calc(self):
        """Test calculating from area and height."""
        triangle = RightTriangleShape()
        # Area = 6, Height = 4 -> Base should be (2*6)/4 = 3
        assert triangle.calculate_from_property('area', 6.0)
        assert triangle.calculate_from_property('height', 4.0)
        
        assert triangle.get_property('base') == pytest.approx(3.0)
        assert triangle.get_property('hypotenuse') == pytest.approx(5.0)

    def test_hypotenuse_area_calc(self):
        """Test calculating from hypotenuse and area (Ambiguous case handling)."""
        triangle = RightTriangleShape()
        # Hyp = 5, Area = 6 -> Base=3, Height=4 (or vice versa)
        # This requires the complex solver logic (Formula 6 in original code)
        assert triangle.calculate_from_property('hypotenuse', 5.0)
        assert triangle.calculate_from_property('area', 6.0)
        
        base = triangle.get_property('base')
        height = triangle.get_property('height')
        
        # We don't know which is which, but set {3, 4} should match
        # Check manually to avoid unhashable type error
        assert (base == pytest.approx(3.0) and height == pytest.approx(4.0)) or \
               (base == pytest.approx(4.0) and height == pytest.approx(3.0))

    def test_perimeter_base_calc(self):
        """Test calculating from perimeter and base."""
        triangle = RightTriangleShape()
        # P = 12, Base = 3 -> Height should be 4
        assert triangle.calculate_from_property('perimeter', 12.0)
        assert triangle.calculate_from_property('base', 3.0)
        
        assert triangle.get_property('height') == pytest.approx(4.0)
        assert triangle.get_property('hypotenuse') == pytest.approx(5.0)

    def test_invalid_input(self):
        """Test that impossible triangles are rejected."""
        triangle = RightTriangleShape()
        # Hypotenuse must be > base
        assert triangle.calculate_from_property('base', 10.0)
        assert not triangle.calculate_from_property('hypotenuse', 5.0)
        
        # Verify it reverted or didn't set invalid state
        # (The current implementation might differ in how it handles 'False' return)
        # But logically, it should fail.


class TestEquilateralTriangle:
    def test_side_calc(self):
        triangle = EquilateralTriangleShape()
        side = 2.0
        assert triangle.calculate_from_property('side', side)
        
        height = side * math.sqrt(3) / 2
        area = (math.sqrt(3) / 4) * side * side
        
        assert triangle.get_property('height') == pytest.approx(height)
        assert triangle.get_property('area') == pytest.approx(area)
        assert triangle.get_property('perimeter') == pytest.approx(side * 3)

    def test_height_calc(self):
        triangle = EquilateralTriangleShape()
        height = math.sqrt(3) # implies side = 2
        assert triangle.calculate_from_property('height', height)
        
        assert triangle.get_property('side') == pytest.approx(2.0)


class TestIsoscelesTriangle:
    def test_base_height_calc(self):
        triangle = IsoscelesTriangleShape()
        # Base=6, Height=4 -> Leg=5
        assert triangle.calculate_from_property('base', 6.0)
        assert triangle.calculate_from_property('height', 4.0)
        
        assert triangle.get_property('leg') == pytest.approx(5.0)
        assert triangle.get_property('area') == pytest.approx(12.0) # 0.5 * 6 * 4

    def test_base_leg_calc(self):
        triangle = IsoscelesTriangleShape()
        # Base=6, Leg=5 -> Height=4
        assert triangle.calculate_from_property('base', 6.0)
        assert triangle.calculate_from_property('leg', 5.0)
        
        assert triangle.get_property('height') == pytest.approx(4.0)

    def test_perimeter_base_calc(self):
        triangle = IsoscelesTriangleShape()
        # P = 16, Base = 6 -> Leg = (16-6)/2 = 5 -> Height=4
        assert triangle.calculate_from_property('perimeter', 16.0)
        assert triangle.calculate_from_property('base', 6.0)
        
        assert triangle.get_property('leg') == pytest.approx(5.0)
        assert triangle.get_property('height') == pytest.approx(4.0)
        assert triangle.get_property('area') == pytest.approx(12.0)

    def test_perimeter_leg_calc(self):
        triangle = IsoscelesTriangleShape()
        # P = 16, Leg = 5 -> Base = 16 - 10 = 6 -> Height=4
        assert triangle.calculate_from_property('perimeter', 16.0)
        assert triangle.calculate_from_property('leg', 5.0)

        assert triangle.get_property('base') == pytest.approx(6.0)
        assert triangle.get_property('height') == pytest.approx(4.0)

    def test_area_base_calc(self):
        triangle = IsoscelesTriangleShape()
        # Area = 12, Base = 6 -> Height = 24/6 = 4 -> Leg=5
        assert triangle.calculate_from_property('area', 12.0)
        assert triangle.calculate_from_property('base', 6.0)

        assert triangle.get_property('height') == pytest.approx(4.0)
        assert triangle.get_property('leg') == pytest.approx(5.0)

    def test_area_height_calc(self):
        triangle = IsoscelesTriangleShape()
        # Area = 12, Height = 4 -> Base = 24/4 = 6 -> Leg=5
        assert triangle.calculate_from_property('area', 12.0)
        assert triangle.calculate_from_property('height', 4.0)

        assert triangle.get_property('base') == pytest.approx(6.0)
        assert triangle.get_property('leg') == pytest.approx(5.0)

    def test_area_leg_calc(self):
        # Bi-quadratic case
        triangle = IsoscelesTriangleShape()
        # Leg=5, Area=12 -> Two solutions technically, but we picked the sharper one (h=4, b=6) or (h=3, b=8)?
        # Our logic picked h2_a (larger height).
        # h^4 - L^2*h^2 + A^2 = 0
        # h^4 - 25h^2 + 144 = 0
        # (h^2 - 16)(h^2 - 9) = 0
        # h^2 = 16 OR h^2 = 9
        # h=4 (so b=6) OR h=3 (so b=8)
        # We picked larger height -> h=4.
        
        assert triangle.calculate_from_property('area', 12.0)
        assert triangle.calculate_from_property('leg', 5.0)

        assert triangle.get_property('height') == pytest.approx(4.0)
        assert triangle.get_property('base') == pytest.approx(6.0)
