
import math
import sys
import os

# Add src to python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from pillars.geometry.services.polygon_shape import RegularPolygonShape
from pillars.geometry.services.square_shape import RectangleShape
from pillars.geometry.services.triangle_shape import RightTriangleShape

def test_polygon_drawing_scaling():
    print("Testing RegularPolygonShape drawing scaling...")
    poly = RegularPolygonShape(num_sides=6)
    poly.set_property('side', 10.0)
    
    instructions = poly.get_drawing_instructions()
    points = instructions['points']
    
    # Check bounds of points
    max_coord = max(max(abs(x), abs(y)) for x, y in points)
    print(f"  Side=10.0, Max Coordinate ~ {max_coord:.2f}")
    
    if max_coord <= 1.5:
        print("  FAIL: Polygon points not scaled (max_coord <= 1.5)")
        return False
    
    print("  PASS: Polygon points scaled correctly.")
    return True

def test_rectangle_solving():
    print("\nTesting RectangleShape solving...")
    rect = RectangleShape()
    
    # Test 1: Length + Area -> Width
    rect.clear_all()
    rect.set_property('length', 10.0)
    rect.set_property('area', 50.0)
    width = rect.get_property('width')
    print(f"  Length=10, Area=50 -> Width={width}")
    if not math.isclose(width, 5.0):
        print("  FAIL: Width calculation from Area incorrect")
        return False

    # Test 2: Length + Perimeter -> Width
    rect.clear_all()
    rect.set_property('length', 10.0)
    rect.set_property('perimeter', 30.0) # 2*(10+5) = 30
    width = rect.get_property('width')
    print(f"  Length=10, Perimeter=30 -> Width={width}")
    if not math.isclose(width, 5.0):
        print("  FAIL: Width calculation from Perimeter incorrect")
        return False

    # Test 3: Width + Diagonal -> Length
    rect.clear_all()
    rect.set_property('width', 3.0)
    rect.set_property('diagonal', 5.0) # 3-4-5 triangle
    length = rect.get_property('length')
    print(f"  Width=3, Diagonal=5 -> Length={length}")
    if not math.isclose(length, 4.0):
        print("  FAIL: Length calculation from Diagonal incorrect")
        return False
        
    print("  PASS: RectangleShape solving logic verified.")
    return True

def test_right_triangle_solving():
    print("\nTesting RightTriangleShape solving...")
    tri = RightTriangleShape()
    
    # Test 1: Base + Hypotenuse -> Height
    tri.clear_all()
    tri.set_property('base', 3.0)
    tri.set_property('hypotenuse', 5.0)
    height = tri.get_property('height')
    print(f"  Base=3, Hypotenuse=5 -> Height={height}")
    if not math.isclose(height, 4.0):
        print("  FAIL: Height from Hypotenuse incorrect")
        return False

    # Test 2: Base + Area -> Height
    tri.clear_all()
    tri.set_property('base', 4.0)
    tri.set_property('area', 6.0) # 0.5 * 4 * 3 = 6
    height = tri.get_property('height')
    print(f"  Base=4, Area=6 -> Height={height}")
    if not math.isclose(height, 3.0):
        print("  FAIL: Height from Area incorrect")
        return False
        
    # Test 3: Perimeter + Base -> Height
    # P = 12, Base = 3. Height=? (3-4-5 triangle P=12)
    tri.clear_all()
    tri.set_property('base', 3.0)
    tri.set_property('perimeter', 12.0)
    height = tri.get_property('height')
    print(f"  Base=3, Perimeter=12 -> Height={height}")
    if not math.isclose(height, 4.0):
        print("  FAIL: Height from Perimeter incorrect")
        return False

    print("  PASS: RightTriangleShape solving logic verified.")
    return True

if __name__ == "__main__":
    passed = True
    passed &= test_polygon_drawing_scaling()
    passed &= test_rectangle_solving()
    passed &= test_right_triangle_solving()
    
    if passed:
        print("\nALL TESTS PASSED")
        sys.exit(0)
    else:
        print("\nSOME TESTS FAILED")
        sys.exit(1)
