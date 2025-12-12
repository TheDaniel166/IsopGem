import math
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from pillars.geometry.services import (
    EquilateralTriangleShape,
    RightTriangleShape,
    CircleShape,
    SquareShape,
    CubeSolidCalculator
)

def test_equilateral_triangle():
    print("Testing Equilateral Triangle...")
    tri = EquilateralTriangleShape()
    # Side = 10
    tri.calculate_from_property('side', 10.0)
    
    assert math.isclose(tri.properties['perimeter'].value, 30.0), f"Perimeter failed: {tri.properties['perimeter'].value}"
    expected_area = (math.sqrt(3) / 4) * 100
    assert math.isclose(tri.properties['area'].value, expected_area), f"Area failed: {tri.properties['area'].value}"
    print("✓ Equilateral Triangle Passed")

def test_right_triangle():
    print("Testing Right Triangle...")
    tri = RightTriangleShape()
    # 3-4-5 triangle
    tri.calculate_from_property('base', 3.0)
    tri.calculate_from_property('height', 4.0)
    
    assert math.isclose(tri.properties['hypotenuse'].value, 5.0), f"Hypotenuse failed: {tri.properties['hypotenuse'].value}"
    assert math.isclose(tri.properties['area'].value, 6.0), f"Area failed: {tri.properties['area'].value}"
    assert math.isclose(tri.properties['perimeter'].value, 12.0), f"Perimeter failed: {tri.properties['perimeter'].value}"
    print("✓ Right Triangle Passed")

def test_circle():
    print("Testing Circle...")
    circ = CircleShape()
    # Radius = 5
    circ.calculate_from_property('radius', 5.0)
    
    assert math.isclose(circ.properties['diameter'].value, 10.0), "Diameter failed"
    assert math.isclose(circ.properties['circumference'].value, 10 * math.pi), "Circumference failed"
    assert math.isclose(circ.properties['area'].value, 25 * math.pi), "Area failed"
    print("✓ Circle Passed")

def test_square():
    print("Testing Square...")
    sq = SquareShape()
    # Side = 4
    sq.calculate_from_property('side', 4.0)
    
    assert math.isclose(sq.properties['area'].value, 16.0), "Area failed"
    assert math.isclose(sq.properties['perimeter'].value, 16.0), "Perimeter failed"
    assert math.isclose(sq.properties['diagonal'].value, 4 * math.sqrt(2)), "Diagonal failed"
    print("✓ Square Passed")

def test_cube():
    print("Testing Cube...")
    cube = CubeSolidCalculator(edge_length=3.0)
    # Edge = 3
    # Vol = 27
    # Surface = 54
    
    props = {p.key: p.value for p in cube.properties()}
    
    assert math.isclose(props['volume'], 27.0), f"Volume failed: {props['volume']}"
    assert math.isclose(props['surface_area'], 54.0), f"Surface Area failed: {props['surface_area']}"
    print("✓ Cube Passed")

def test_shape_detection():
    print("Testing Shape Detection Service...")
    from pillars.geometry.services.shape_detection_service import ShapeDetectionService
    
    # 1. Square Points
    square_points = [(0,0), (4,0), (4,4), (0,4)]
    shape = ShapeDetectionService.detect_from_points(square_points)
    assert shape is not None, "Failed to detect square"
    assert shape.name == "Square", f"Expected Square, got {shape.name}"
    print("✓ Detection: Square Passed")
    
    # 2. Rectangle Points
    rect_points = [(0,0), (6,0), (6,3), (0,3)]
    shape = ShapeDetectionService.detect_from_points(rect_points)
    assert shape is not None, "Failed to detect rectangle"
    assert shape.name == "Rectangle", f"Expected Rectangle, got {shape.name}"
    print("✓ Detection: Rectangle Passed")
    
    # 3. Equilateral Triangle Points
    # h = s * sqrt(3)/2, s=10 -> h=5*sqrt(3)
    h = 5 * math.sqrt(3)
    eq_tri_points = [(0,0), (10,0), (5, h)]
    shape = ShapeDetectionService.detect_from_points(eq_tri_points)
    assert shape is not None, "Failed to detect triangle"
    assert shape.name == "Equilateral Triangle", f"Expected Equilateral Triangle, got {shape.name}"
    print("✓ Detection: Equilateral Triangle Passed")

if __name__ == "__main__":
    try:
        test_equilateral_triangle()
        test_right_triangle()
        test_circle()
        test_square()
        test_cube()
        test_shape_detection()
        print("\nAll Geometry Tests Passed!")
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
