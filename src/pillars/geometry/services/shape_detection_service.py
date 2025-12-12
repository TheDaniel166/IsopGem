"""Service for detecting geometric shapes from point data."""
import math
from typing import List, Optional, Tuple, Type

from .base_shape import GeometricShape
from .triangle_shape import (
    EquilateralTriangleShape,
    IsoscelesRightTriangleShape,
    IsoscelesTriangleShape,
    RightTriangleShape,
    ScaleneTriangleShape,
)
from .square_shape import SquareShape, RectangleShape
from .quadrilateral_shape import RhombusShape, ParallelogramShape
from .irregular_polygon_shape import IrregularPolygonShape


class ShapeDetectionService:
    """Detects and initializes geometric shapes from a set of 2D points."""

    @staticmethod
    def detect_from_points(points: List[Tuple[float, float]]) -> Optional[GeometricShape]:
        """
        Analyze points and return the most specific GeometricShape instance.
        
        Args:
            points: List of (x, y) tuples.
            
        Returns:
            Initialized GeometricShape or None if fewer than 3 points.
        """
        count = len(points)
        if count < 3:
            return None

        if count == 3:
            return ShapeDetectionService._detect_triangle(points)
        elif count == 4:
            return ShapeDetectionService._detect_quadrilateral(points)
        else:
            return IrregularPolygonShape(points)

    @staticmethod
    def _detect_triangle(points: List[Tuple[float, float]]) -> GeometricShape:
        p0, p1, p2 = points
        
        # Calculate side lengths
        s1 = math.dist(p0, p1)
        s2 = math.dist(p1, p2)
        s3 = math.dist(p2, p0)
        
        sides = sorted([s1, s2, s3])
        a, b, c = sides[0], sides[1], sides[2] # Smallest to largest
        
        # Check for Equilateral (all sides equal)
        if math.isclose(a, c, rel_tol=1e-4):
            shape = EquilateralTriangleShape()
            shape.set_property("side", a)
            return shape
            
        # Check for Isosceles (2 sides equal)
        elif math.isclose(a, b, rel_tol=1e-4) or math.isclose(b, c, rel_tol=1e-4):
            # In isosceles, leg is defined.
            leg = a if math.isclose(a, b, rel_tol=1e-4) else c
            base = c if math.isclose(a, b, rel_tol=1e-4) else a
            
            # IsoscelesRight check: base (hypotenuse) approx leg * sqrt(2)?
            is_right = math.isclose(base, leg * math.sqrt(2), rel_tol=1e-4)
            
            if is_right:
                shape = IsoscelesRightTriangleShape()
                shape.set_property("leg", leg)
                return shape
            else:
                shape = IsoscelesTriangleShape()
                shape.set_property("leg", leg)
                shape.set_property("base", base)
                return shape
                
        # Check for Right Triangle (a^2 + b^2 = c^2)
        elif math.isclose(a*a + b*b, c*c, rel_tol=1e-4):
            shape = RightTriangleShape()
            shape.set_property("base", a)
            shape.set_property("height", b)
            return shape
            
        else:
            # Scalene (Generic)
            shape = ScaleneTriangleShape()
            # Use raw lengths we calculated. ordering doesn't strictly matter for setting properties
            # but mapping s1, s2, s3 to correct sides would imply mapping back to vertices.
            # For pure SSS, just providing the lengths is sufficient.
            shape.set_property("side_a", s1)
            shape.set_property("side_b", s2)
            shape.set_property("side_c", s3)
            return shape

    @staticmethod
    def _detect_quadrilateral(points: List[Tuple[float, float]]) -> GeometricShape:
        p0, p1, p2, p3 = points

        # Calculate sides (0-1, 1-2, 2-3, 3-0)
        s1 = math.dist(p0, p1)
        s2 = math.dist(p1, p2)
        s3 = math.dist(p2, p3)
        s4 = math.dist(p3, p0)
        
        # Calculate diagonals (0-2, 1-3)
        d1 = math.dist(p0, p2)
        d2 = math.dist(p1, p3)
        
        sides = [s1, s2, s3, s4]
        avg_side = sum(sides) / 4.0
        
        is_equilateral = all(math.isclose(s, sides[0], rel_tol=1e-3) for s in sides)
        is_opp_equal = math.isclose(s1, s3, rel_tol=1e-3) and math.isclose(s2, s4, rel_tol=1e-3)
        is_diag_equal = math.isclose(d1, d2, rel_tol=1e-3)
        
        if is_equilateral and is_diag_equal:
            # Square
            shape = SquareShape()
            shape.set_property("side", avg_side)
            return shape
            
        elif is_opp_equal and is_diag_equal:
            # Rectangle
            shape = RectangleShape()
            # Typically length > width, but we just need dimensions
            shape.set_property("length", max(s1, s2))
            shape.set_property("width", min(s1, s2))
            return shape
            
        elif is_equilateral:
            # Rhombus
            shape = RhombusShape()
            shape.set_property("side", avg_side)
            # Use one diagonal to define the shape
            shape.set_property("diagonal_long", max(d1, d2))
            shape.set_property("diagonal_short", min(d1, d2))
            return shape
            
        elif is_opp_equal:
            # Parallelogram
            shape = ParallelogramShape()
            shape.set_property("base", s1)
            shape.set_property("side", s2)
            # Parallelogram needs more than just sides to be fully defined (angle or height).
            # But the shape calculator might be able to ingest diagonals?
            # As per reading ParallelogramShape, it doesn't easily calculate from diagonals + sides directly 
            # without complex logic not exposed in basic 'calculate_from_property'.
            # However, we can try to facilitate what we can.
            # But for now, we return it with sides populated.
            return shape
            
        else:
            # Irregular Quadrilateral
            return IrregularPolygonShape(points)
