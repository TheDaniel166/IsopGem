"""
Test script for Cube Canon DSL integration.

Verifies that:
1. CubeSolver can solve from various properties
2. CubeRealizer can generate payloads
3. get_derivation() returns formatted text
4. Book button will work
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pillars.geometry.canon.cube_solver import CubeSolver
from pillars.geometry.canon.cube_realizer import CubeRealizer
from shared.substrate.canon_dsl import RealizeContext


def test_cube_solver():
    """Test CubeSolver bidirectional solving."""
    solver = CubeSolver()
    
    # Test solving from edge_length
    result = solver.solve_from("edge_length", 2.0)
    assert result.ok, "Edge length solve failed"
    assert abs(result.canonical_parameter - 2.0) < 1e-6
    print("✓ Edge length solve: PASS")
    
    # Test solving from volume
    result = solver.solve_from("volume", 8.0)
    assert result.ok, "Volume solve failed"
    assert abs(result.canonical_parameter - 2.0) < 1e-6
    print(f"✓ Volume solve: PASS (a={result.canonical_parameter:.6f})")
    
    # Test solving from surface_area
    result = solver.solve_from("surface_area", 24.0)
    assert result.ok, "Surface area solve failed"
    assert abs(result.canonical_parameter - 2.0) < 1e-6
    print(f"✓ Surface area solve: PASS (a={result.canonical_parameter:.6f})")
    
    # Test solving from inradius
    result = solver.solve_from("inradius", 1.0)
    assert result.ok, "Inradius solve failed"
    assert abs(result.canonical_parameter - 2.0) < 1e-6
    print(f"✓ Inradius solve: PASS (a={result.canonical_parameter:.6f})")
    
    # Test solving from circumradius
    import math
    expected_a = 2.0
    circ_r = expected_a * math.sqrt(3.0) / 2.0
    result = solver.solve_from("circumradius", circ_r)
    assert result.ok, "Circumradius solve failed"
    assert abs(result.canonical_parameter - 2.0) < 1e-3
    print(f"✓ Circumradius solve: PASS (a={result.canonical_parameter:.6f})")
    
    # Test solving from face_diagonal
    face_diag = 2.0 * math.sqrt(2.0)
    result = solver.solve_from("face_diagonal", face_diag)
    assert result.ok, "Face diagonal solve failed"
    assert abs(result.canonical_parameter - 2.0) < 1e-6
    print(f"✓ Face diagonal solve: PASS (a={result.canonical_parameter:.6f})")
    
    # Test solving from space_diagonal
    space_diag = 2.0 * math.sqrt(3.0)
    result = solver.solve_from("space_diagonal", space_diag)
    assert result.ok, "Space diagonal solve failed"
    assert abs(result.canonical_parameter - 2.0) < 1e-6
    print(f"✓ Space diagonal solve: PASS (a={result.canonical_parameter:.6f})")
    
    print("\n✅ All CubeSolver tests passed!\n")


def test_get_all_properties():
    """Test get_all_properties calculation."""
    solver = CubeSolver()
    props = solver.get_all_properties(2.0)
    
    assert abs(props["edge_length"] - 2.0) < 1e-6
    assert abs(props["volume"] - 8.0) < 1e-6
    assert abs(props["surface_area"] - 24.0) < 1e-6
    assert abs(props["faces"] - 6.0) < 1e-6
    assert abs(props["vertices"] - 8.0) < 1e-6
    assert abs(props["edges"] - 12.0) < 1e-6
    assert abs(props["dihedral_angle_deg"] - 90.0) < 1e-6
    
    print("✓ get_all_properties: PASS")
    print(f"  - Edge length: {props['edge_length']:.6f}")
    print(f"  - Volume: {props['volume']:.6f}")
    print(f"  - Surface area: {props['surface_area']:.6f}")
    print(f"  - Inradius: {props['inradius']:.6f}")
    print(f"  - Circumradius: {props['circumradius']:.6f}")
    print(f"  - Dihedral: {props['dihedral_angle_deg']:.4f}°")
    
    print("\n✅ Property calculation tests passed!\n")


def test_create_declaration():
    """Test Declaration creation."""
    solver = CubeSolver()
    decl = solver.create_declaration(2.0)
    
    assert decl.title == "Cube (a=2.0000)"
    assert len(decl.forms) == 1
    assert decl.forms[0].kind == "Cube"
    assert decl.forms[0].params["edge_length"] == 2.0
    
    print("✓ create_declaration: PASS")
    print(f"  - Title: {decl.title}")
    print(f"  - Form kind: {decl.forms[0].kind}")
    print(f"  - Edge length: {decl.forms[0].params['edge_length']}")
    
    print("\n✅ Declaration creation tests passed!\n")


def test_realizer():
    """Test CubeRealizer form realization."""
    solver = CubeSolver()
    realizer = CubeRealizer()
    
    # Create declaration
    decl = solver.create_declaration(2.0)
    
    # Realize it
    context = RealizeContext()
    realization = realizer.realize_form(decl.forms[0], context)
    
    assert realization.artifact is not None, "Artifact should not be None"
    assert "edge_length" in realization.metrics
    assert abs(realization.metrics["edge_length"] - 2.0) < 1e-6
    assert "volume" in realization.metrics
    assert abs(realization.metrics["volume"] - 8.0) < 1e-3
    
    print("✓ CubeRealizer: PASS")
    print(f"  - Artifact type: {type(realization.artifact).__name__}")
    print(f"  - Edge length: {realization.metrics['edge_length']:.6f}")
    print(f"  - Volume: {realization.metrics['volume']:.6f}")
    print(f"  - Provenance: {realization.provenance}")
    
    print("\n✅ Realizer tests passed!\n")


def test_derivation():
    """Test get_derivation() for book button."""
    solver = CubeSolver()
    derivation = solver.get_derivation()
    derivation_title = solver.get_derivation_title()
    
    assert derivation is not None
    assert len(derivation) > 0
    assert "CUBE" in derivation
    assert "PYTHAGOREAN PROGRESSION" in derivation
    assert "HERMETIC INSIGHT" in derivation
    assert derivation_title == "Cube — Earth & Stability · Mathematical Derivations"
    
    print("✓ get_derivation(): PASS")
    print(f"  - Derivation length: {len(derivation)} chars")
    print(f"  - Title: {derivation_title}")
    print(f"  - Contains core formulas: {'CORE DIMENSION' in derivation}")
    print(f"  - Contains AHA moments: {'AHA MOMENT' in derivation}")
    print(f"  - Contains hermetic: {'HERMETIC' in derivation}")
    
    print("\n✅ Derivation tests passed!\n")


if __name__ == "__main__":
    print("=" * 80)
    print("CUBE CANON DSL INTEGRATION TEST")
    print("=" * 80)
    print()
    
    test_cube_solver()
    test_get_all_properties()
    test_create_declaration()
    test_realizer()
    test_derivation()
    
    print("=" * 80)
    print("ALL TESTS PASSED ✅")
    print("=" * 80)
    print()
    print("Cube Canon DSL integration is complete and functional!")
    print("Next: Test in UnifiedGeometryViewer by selecting Cube from dropdown")
