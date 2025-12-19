"""Verification Ritual for the Foundational Trinity (Sphere, Cylinder, Cone)."""
import math
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from pillars.geometry.services.sphere_solid import SphereSolidCalculator
from pillars.geometry.services.cylinder_solid import CylinderSolidCalculator
from pillars.geometry.services.cone_solid import ConeSolidCalculator

def test_sphere():
    print("Testing Sphere...")
    calc = SphereSolidCalculator(radius=10.0)
    
    # Check forward math
    expected_vol = (4/3) * math.pi * (10.0**3)
    if not math.isclose(calc._properties['volume'].value, expected_vol, rel_tol=1e-5):
        print(f"❌ Sphere Volume Failed: Got {calc._properties['volume'].value}, Expected {expected_vol}")
        sys.exit(1)
        
    # Check bidirectional (Volume -> Radius)
    target_vol = 500.0
    calc.set_property('volume', target_vol)
    expected_r = (3 * target_vol / (4 * math.pi)) ** (1/3)
    if not math.isclose(calc._properties['radius'].value, expected_r, rel_tol=1e-5):
        print(f"❌ Sphere Bidirectional Failed: Got r={calc._properties['radius'].value}, Expected {expected_r}")
        sys.exit(1)
    print("✅ Sphere Verified.")

def test_cylinder():
    print("Testing Cylinder...")
    calc = CylinderSolidCalculator(radius=5.0, height=10.0)
    
    # Check forward math
    expected_vol = math.pi * (5.0**2) * 10.0
    if not math.isclose(calc._properties['volume'].value, expected_vol, rel_tol=1e-5):
        print(f"❌ Cylinder Volume Failed: Got {calc._properties['volume'].value}, Expected {expected_vol}")
        sys.exit(1)
        
    # Check bidirectional (Volume -> Radius keeping height=10)
    target_vol = 1000.0
    calc.set_property('volume', target_vol)
    expected_r = math.sqrt(target_vol / (math.pi * 10.0))
    if not math.isclose(calc._properties['radius'].value, expected_r, rel_tol=1e-5):
        print(f"❌ Cylinder Bidirectional Failed: Got r={calc._properties['radius'].value}, Expected {expected_r}")
        sys.exit(1)
    print("✅ Cylinder Verified.")

def test_cone():
    print("Testing Cone...")
    calc = ConeSolidCalculator(radius=5.0, height=12.0)
    
    # Check slant height: sqrt(5^2 + 12^2) = 13
    if not math.isclose(calc._properties['slant_height'].value, 13.0, rel_tol=1e-5):
        print(f"❌ Cone Slant Height Failed: Got {calc._properties['slant_height'].value}, Expected 13.0")
        sys.exit(1)
        
    # Check bidirectional (Slant -> Height)
    # Set slant to 15, radius remains 5. Height should be sqrt(15^2 - 5^2) = sqrt(200) = 14.142
    calc.set_property('slant_height', 15.0)
    expected_h = math.sqrt(15.0**2 - 5.0**2)
    if not math.isclose(calc._properties['height'].value, expected_h, rel_tol=1e-5):
        print(f"❌ Cone Bidirectional Failed: Got h={calc._properties['height'].value}, Expected {expected_h}")
        sys.exit(1)
    print("✅ Cone Verified.")

if __name__ == "__main__":
    print("Beginning Rite of Trinity 3D...")
    test_sphere()
    test_cylinder()
    test_cone()
    print("All Foundational Rituals Complete. The Trinity is manifest.")
