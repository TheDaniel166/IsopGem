
import sys
import os
import math

# Add source directory to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from pillars.geometry.services.torus_knot_solid import TorusKnotSolidService, TorusKnotSolidCalculator, TorusKnotMeshConfig

def run_tests():
    print("Verifying Torus Knot Solid...")
    
    # Test 1: Trefoil (2, 3)
    print("\n--- Test 1: Trefoil (2, 3) Generation ---")
    p = 2
    q = 3
    R = 3.0
    r = 1.0
    tube_r = 0.4
    
    # Default config: 200 segments x 12 radial
    config = TorusKnotMeshConfig(tubular_segments=200, radial_segments=12)
    result = TorusKnotSolidService.build(p, q, R, r, tube_r, config)
    payload = result.payload
    
    n_verts = len(payload.vertices)
    n_faces = len(payload.faces)
    n_edges = len(payload.edges)
    
    print(f"Vertices: {n_verts} (Expected ~2400)")
    print(f"Faces: {n_faces} (Expected ~2400)")
    print(f"Edges: {n_edges}")
    
    # Expected Vertices = 200 * 12 = 2400
    if n_verts != 2400:
        print("FAILED: Vertex count mismatch")
        sys.exit(1)
        
    if n_faces != 2400:
        print("FAILED: Face count mismatch")
        sys.exit(1)
        
    if n_edges < 1000: # Rough check, edges should be many
        print("FAILED: Edge generation seems broken (too few edges)")
        sys.exit(1)
        
    print("PASS: Mesh counts correct")
    
    # Test 2: Calculator Metrics
    print("\n--- Test 2: Calculator Metrics ---")
    calc = TorusKnotSolidCalculator(p=2, q=3)
    props = {p.key: p.value for p in calc.properties()}
    
    v = props['volume']
    a = props['surface_area']
    l = props['arc_length']
    
    print(f"Arc Length: {l:.4f}")
    print(f"Volume: {v:.4f}")
    print(f"Surface Area: {a:.4f}")
    
    if l <= 0 or v <= 0 or a <= 0:
        print("FAILED: Metrics are zero or negative")
        sys.exit(1)
        
    # Test 3: Parameter Update
    print("\n--- Test 3: Parameter Update (P=3, Q=2) ---")
    # Change into a different knot (3, 2 should is topologically same as 2,3 but geometry differs?)
    # Or try (5, 2) Cinquefoil
    calc.set_property('p', 5)
    calc.set_property('q', 2)
    
    new_props = {p.key: p.value for p in calc.properties()}
    print(f"New P: {new_props['p']}")
    print(f"New Q: {new_props['q']}")
    print(f"New Arc Length: {new_props['arc_length']:.4f}")
    
    if new_props['p'] != 5 or new_props['q'] != 2:
        print("FAILED: Property update failed")
        sys.exit(1)

    print("PASS: Update logic works")
    print("\nSUCCESS: All Torus Knot tests passed.")

if __name__ == "__main__":
    run_tests()
