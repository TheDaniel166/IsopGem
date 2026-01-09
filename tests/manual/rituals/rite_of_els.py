"""Rite of ELS - Verification ritual for ELS Bible Code search.

The Seven Seals:
- ♄ SATURN: Structure - grid factors and import tests
- ☉ SUN: Core Logic - ELS search algorithm
- ♂ MARS: Edge Cases - empty text, overflow
- ☿ MERCURY: Logging - verify log output
"""
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def test_saturn_structure():
    """♄ SATURN: Test grid factor calculation."""
    print("\n♄ SATURN: Testing Structure...")
    
    from pillars.gematria.services.els_service import ELSSearchService
    
    service = ELSSearchService()
    
    # Test factor calculation for 12
    factors = service.get_grid_factors(12)
    expected = [(3, 4), (4, 3), (2, 6), (6, 2)]  # Sorted by squareness
    
    print(f"  Factors of 12: {factors}")
    assert len(factors) == 4, f"Expected 4 factors, got {len(factors)}"
    
    # Test factor calculation for 100
    factors_100 = service.get_grid_factors(100)
    print(f"  Factors of 100: {factors_100}")
    assert (10, 10) in factors_100, "10×10 should be a factor of 100"
    
    print("  ✓ Saturn Seal BROKEN - Structure is sound")
    return True


def test_sun_core_logic():
    """☉ SUN: Test core ELS search algorithm."""
    print("\n☉ SUN: Testing Core Logic...")
    
    from pillars.gematria.services.els_service import ELSSearchService
    
    service = ELSSearchService()
    
    # Test case: "AXBXCX" with skip=2 should find "ABC" at position 0
    text = "AXBXCX"
    term = "ABC"
    
    summary = service.search_els(text, term, skip=2, direction='forward')
    
    print(f"  Searching '{term}' in '{text}' with skip=2")
    print(f"  Found: {len(summary.results)} matches")
    
    assert summary.total_hits >= 1, "Should find at least 1 match"
    
    result = summary.results[0]
    assert result.start_pos == 0, f"Expected start_pos=0, got {result.start_pos}"
    assert result.letter_positions == [0, 2, 4], f"Expected [0,2,4], got {result.letter_positions}"
    
    print(f"  Result: {result}")
    print("  ✓ Sun Seal BROKEN - Core logic confirmed")
    return True


def test_mars_edge_cases():
    """♂ MARS: Test edge cases and error handling."""
    print("\n♂ MARS: Testing Edge Cases...")
    
    from pillars.gematria.services.els_service import ELSSearchService
    
    service = ELSSearchService()
    
    # Empty text
    summary = service.search_els("", "ABC", skip=1)
    assert summary.total_hits == 0, "Empty text should return 0 results"
    print("  ✓ Empty text handled")
    
    # Skip larger than text
    summary = service.search_els("ABC", "ABC", skip=100)
    assert summary.total_hits == 0, "Skip > text length should return 0"
    print("  ✓ Skip overflow handled")
    
    # Single character search
    summary = service.search_els("ABCABC", "A", skip=3)
    print(f"  Single char search found: {summary.total_hits} matches")
    assert summary.total_hits >= 1, "Should find single char"
    print("  ✓ Single character handled")
    
    # Reverse search
    summary = service.search_els("CXBXA", "ABC", skip=2, direction='reverse')
    print(f"  Reverse search found: {summary.total_hits} matches")
    
    print("  ✓ Mars Seal BROKEN - Edge cases defended")
    return True


def test_mercury_text_preparation():
    """☿ MERCURY: Test text stripping and position mapping."""
    print("\n☿ MERCURY: Testing Text Preparation...")
    
    from pillars.gematria.services.els_service import ELSSearchService
    
    service = ELSSearchService()
    
    # Test stripping
    raw_text = "Hello, World! 123"
    stripped, positions = service.prepare_text(raw_text)
    
    print(f"  Raw: '{raw_text}'")
    print(f"  Stripped: '{stripped}'")
    print(f"  Position map: {positions}")
    
    assert stripped == "HelloWorld", f"Expected 'HelloWorld', got '{stripped}'"
    assert len(positions) == len(stripped), "Position map length mismatch"
    
    print("  ✓ Mercury Seal BROKEN - Communication channels clear")
    return True


def test_venus_matrix_building():
    """♀ VENUS: Test matrix arrangement."""
    print("\n♀ VENUS: Testing Matrix Building...")
    
    from pillars.gematria.services.els_service import ELSSearchService
    
    service = ELSSearchService()
    
    text = "ABCDEFGHIJ"
    matrix = service.build_matrix(text, 3)
    
    print(f"  Text: {text}")
    print(f"  Matrix (3 cols):")
    for row in matrix:
        print(f"    {row}")
    
    assert len(matrix) == 4, f"Expected 4 rows, got {len(matrix)}"
    assert matrix[0] == ['A', 'B', 'C'], f"First row mismatch: {matrix[0]}"
    
    print("  ✓ Venus Seal BROKEN - Data contracts harmonious")
    return True


def main():
    """Execute the Rite of ELS."""
    print("=" * 60)
    print("       THE RITE OF ELS - VERIFICATION RITUAL")
    print("=" * 60)
    
    seals = [
        ("SATURN", test_saturn_structure),
        ("SUN", test_sun_core_logic),
        ("MARS", test_mars_edge_cases),
        ("MERCURY", test_mercury_text_preparation),
        ("VENUS", test_venus_matrix_building),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in seals:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"\n  ✗ {name} Seal INTACT - Test failed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RITE COMPLETE: {passed} Seals Broken, {failed} Intact")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
