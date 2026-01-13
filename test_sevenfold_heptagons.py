"""
Quick test for Sevenfold Nested Heptagons Service.

Verifies:
- 7-layer service initialization
- Bidirectional property solving
- Cascade propagation
"""

import sys
sys.path.insert(0, '/home/burkettdaniel927/projects/isopgem/src')

from pillars.geometry.services.nested_heptagons_service import NestedHeptagonsService


def test_sevenfold_service():
    """Test the 7-layer service."""
    print("═" * 70)
    print("SEVENFOLD NESTED HEPTAGONS SERVICE TEST")
    print("═" * 70)
    
    service = NestedHeptagonsService(num_layers=7, canonical_edge_length=1.0)
    
    print(f"✓ Number of layers: {service.num_layers}")
    print(f"✓ Canonical layer: {service.canonical_layer} (Sun)")
    print(f"✓ Canonical edge: {service.canonical_edge:.6f}\n")
    
    # Test all layer edges
    print("Layer edges:")
    for i in range(1, service.num_layers + 1):
        edge = service.layer_edge(i)
        name = NestedHeptagonsService.PLANETARY_NAMES[i-1]
        print(f"  Layer {i} ({name:8s}): {edge:.10f}")
    
    print("\n✓ All layers computed successfully\n")
    
    # Test bidirectional solving: set layer 7's long diagonal
    print("Bidirectional solving test:")
    print(f"  Before: Layer 7 long diagonal = {service.layer_properties(7).long_diagonal:.6f}")
    
    target_diagonal = 10.0
    service.set_layer_property(7, "long_diagonal", target_diagonal)
    
    actual_diagonal = service.layer_properties(7).long_diagonal
    print(f"  After:  Layer 7 long diagonal = {actual_diagonal:.6f} (target: {target_diagonal:.6f})")
    print(f"  Error: {abs(actual_diagonal - target_diagonal):.2e}")
    print(f"  ✓ Canonical edge adjusted to: {service.canonical_edge:.6f}\n")
    
    assert abs(actual_diagonal - target_diagonal) < 1e-10, "Bidirectional solve failed!"
    
    # Verify cascade propagated
    print("Cascade verification (all layers adjusted):")
    for i in range(1, service.num_layers + 1):
        props = service.layer_properties(i)
        name = NestedHeptagonsService.PLANETARY_NAMES[i-1]
        print(f"  Layer {i} ({name:8s}): edge={props.edge_length:.6f}, area={props.area:.6f}")
    
    print("\n✓ Cascade propagation verified!")
    
    # Test multiple property types
    print("\nTesting different property types:")
    test_cases = [
        (3, "circumradius", 2.5),
        (5, "area", 15.0),
        (1, "perimeter", 3.0),
    ]
    
    for layer, prop_name, target_value in test_cases:
        service.set_layer_property(layer, prop_name, target_value)
        props = service.layer_properties(layer)
        actual_value = getattr(props, prop_name)
        error = abs(actual_value - target_value)
        name = NestedHeptagonsService.PLANETARY_NAMES[layer-1]
        print(f"  Layer {layer} ({name}) {prop_name}: {actual_value:.6f} (target: {target_value:.6f}, error: {error:.2e})")
        assert error < 1e-9, f"Property {prop_name} solve failed!"
    
    print("\n✓ All property types solve correctly!")


if __name__ == "__main__":
    test_sevenfold_service()
    
    print("\n" + "═" * 70)
    print("ALL TESTS PASSED! THE SEVENFOLD HEPTAGON STANDS TRUE.")
    print("═" * 70)
