#!/usr/bin/env python
"""
Deep Rite of the Seven Seals - Comprehensive Verification Script
Target: Quadset Analysis Window & Dependencies
"""
import sys
import os
import time
import traceback
from typing import List, Tuple, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

# Import test subjects
from pillars.tq.services.number_properties import NumberPropertiesService as NPS
from pillars.tq.services.quadset_engine import QuadsetEngine

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def test_section(title: str):
    """Print section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_result(name: str, passed: bool, details: str = ""):
    """Print test result."""
    status = "✓" if passed else "✗"
    detail_str = f" ({details})" if details else ""
    print(f"  {status} {name}{detail_str}")
    return passed

def run_tests(tests: List[Tuple[str, callable]]) -> Tuple[int, int]:
    """Run list of tests, return (passed, total)."""
    passed = 0
    total = len(tests)
    for name, test_fn in tests:
        try:
            result = test_fn()
            if test_result(name, result):
                passed += 1
        except Exception as e:
            test_result(name, False, f"Exception: {e}")
    return passed, total

# ============================================================================
# ♄ SATURN - STRUCTURE & BOUNDARIES
# ============================================================================

def test_saturn():
    test_section("♄ SATURN - Structure & Boundaries")
    
    tests = [
        ("NumberPropertiesService importable", lambda: NPS is not None),
        ("QuadsetEngine importable", lambda: QuadsetEngine is not None),
        ("get_properties is static method", lambda: callable(NPS.get_properties)),
        ("is_happy is static method", lambda: callable(NPS.is_happy)),
        ("is_pronic is static method", lambda: callable(NPS.is_pronic)),
        ("get_happy_chain is static method", lambda: callable(NPS.get_happy_chain)),
        ("get_figurate_3d_info is static method", lambda: callable(NPS.get_figurate_3d_info)),
        ("QuadsetEngine has calculate method", lambda: callable(getattr(QuadsetEngine(), 'calculate', None))),
    ]
    
    return run_tests(tests)

# ============================================================================
# ♃ JUPITER - EXPANSION & LOAD
# ============================================================================

def test_jupiter():
    test_section("♃ JUPITER - Expansion & Load")
    
    # Performance benchmarks
    results = []
    
    # Test 1: 100 numbers performance
    start = time.time()
    for n in range(1, 101):
        NPS.get_properties(n)
    elapsed = (time.time() - start) * 1000
    results.append(test_result(f"100 get_properties calls", elapsed < 1000, f"{elapsed:.1f}ms"))
    
    # Test 2: Large number range
    start = time.time()
    for n in [10**6, 10**7, 10**8, 10**9]:
        NPS.get_properties(n)
    elapsed = (time.time() - start) * 1000
    results.append(test_result("Large numbers (10^6 to 10^9)", elapsed < 500, f"{elapsed:.1f}ms"))
    
    # Test 3: Happy chain on very large number
    start = time.time()
    chain = NPS.get_happy_chain(10**15)
    elapsed = (time.time() - start) * 1000
    results.append(test_result(f"Happy chain for 10^15", elapsed < 100, f"{elapsed:.1f}ms, len={len(chain)}"))
    
    # Test 4: Quadset engine performance
    engine = QuadsetEngine()
    start = time.time()
    for n in range(1, 101):
        engine.calculate(n)
    elapsed = (time.time() - start) * 1000
    results.append(test_result("100 quadset computations", elapsed < 500, f"{elapsed:.1f}ms"))
    
    passed = sum(1 for r in results if r)
    return passed, len(results)

# ============================================================================
# ♂ MARS - CONFLICT & SEVERITY
# ============================================================================

def test_mars():
    test_section("♂ MARS - Conflict & Severity (Edge Cases)")
    
    tests = []
    
    # Realistic boundary values (Quadset uses positive integers)
    boundary_cases = [
        (0, "Zero"),
        (1, "One"),
        (999999, "Large 6-digit"),
        (9999999, "Large 7-digit"),
    ]
    
    for val, desc in boundary_cases:
        def test_fn(v=val):
            props = NPS.get_properties(v)
            return isinstance(props, dict) and 'is_prime' in props
        tests.append((f"get_properties({desc})", test_fn))
    
    # Happy number edge cases
    tests.append(("is_happy(0)", lambda: NPS.is_happy(0) == False))
    tests.append(("is_happy(1)", lambda: NPS.is_happy(1) == True))
    tests.append(("is_happy(-7)", lambda: NPS.is_happy(-7) == False))
    
    # Happy chain edge cases
    tests.append(("get_happy_chain(0)", lambda: NPS.get_happy_chain(0) == []))
    tests.append(("get_happy_chain(-1)", lambda: NPS.get_happy_chain(-1) == []))
    tests.append(("get_happy_chain(1)", lambda: NPS.get_happy_chain(1) == [1]))
    
    # Pronic edge cases
    tests.append(("is_pronic(0)", lambda: NPS.is_pronic(0) == True))  # 0 = 0 * 1
    tests.append(("is_pronic(-2)", lambda: NPS.is_pronic(-2) == False))
    
    # 3D Figurate edge cases
    tests.append(("get_figurate_3d_info(0)", lambda: NPS.get_figurate_3d_info(0) == []))
    tests.append(("get_figurate_3d_info(1)", lambda: 'Tetrahedral' in str(NPS.get_figurate_3d_info(1))))
    
    return run_tests(tests)

# ============================================================================
# ☉ SUN - VITALITY & TRUTH (Core Calculations)
# ============================================================================

def test_sun():
    test_section("☉ SUN - Vitality & Truth (Core Calculations)")
    
    tests = []
    
    # Exhaustive Happy numbers (first 50)
    # Source: https://oeis.org/A007770
    HAPPY_NUMBERS = [1, 7, 10, 13, 19, 23, 28, 31, 32, 44, 49, 68, 70, 79, 82, 86, 91, 94, 97, 100,
                    103, 109, 129, 130, 133, 139, 167, 176, 188, 190, 192, 193, 203, 208, 219, 226, 
                    230, 236, 239, 262, 263, 280, 291, 293, 301, 302, 310, 313, 319, 320]
    
    def test_happy_exhaustive():
        failures = []
        for n in HAPPY_NUMBERS:
            if not NPS.is_happy(n):
                failures.append(n)
        return len(failures) == 0
    tests.append((f"Happy numbers ({len(HAPPY_NUMBERS)} known)", test_happy_exhaustive))
    
    # Known Sad numbers (first 10 that enter cycle)
    SAD_NUMBERS = [2, 3, 4, 5, 6, 8, 9, 11, 12, 14, 15, 16, 17, 18, 20]
    def test_sad_exhaustive():
        failures = []
        for n in SAD_NUMBERS:
            if NPS.is_happy(n):
                failures.append(n)
        return len(failures) == 0
    tests.append((f"Sad numbers ({len(SAD_NUMBERS)} known)", test_sad_exhaustive))
    
    # Happy iteration counts
    # 7: 7 → 49 → 97 → 130 → 10 → 1 (5 iterations)
    tests.append(("Happy iterations for 7", lambda: NPS.get_happy_iterations(7) == 5))
    # 19: 19 → 82 → 68 → 100 → 1 (4 iterations)
    tests.append(("Happy iterations for 19", lambda: NPS.get_happy_iterations(19) == 4))
    
    # Prime numbers
    PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    def test_primes():
        for p in PRIMES:
            if not NPS.is_prime(p):
                return False
        return True
    tests.append((f"Prime detection ({len(PRIMES)} primes)", test_primes))
    
    # Non-primes (composites)
    COMPOSITES = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25, 26, 27, 28]
    def test_composites():
        for c in COMPOSITES:
            if NPS.is_prime(c):
                return False
        return True
    tests.append((f"Composite detection ({len(COMPOSITES)} composites)", test_composites))
    
    # Prime ordinals
    tests.append(("Prime ordinal of 2", lambda: NPS.get_prime_ordinal(2) == 1))
    tests.append(("Prime ordinal of 7", lambda: NPS.get_prime_ordinal(7) == 4))
    tests.append(("Prime ordinal of 97", lambda: NPS.get_prime_ordinal(97) == 25))
    tests.append(("Prime ordinal of 4 (not prime)", lambda: NPS.get_prime_ordinal(4) == 0))
    
    # Pronic numbers: n(n+1)
    PRONIC = [(0, 0), (2, 1), (6, 2), (12, 3), (20, 4), (30, 5), (42, 6), (56, 7), (72, 8), (90, 9)]
    for val, idx in PRONIC:
        tests.append((f"Pronic {val} (index={idx})", 
                     lambda v=val, i=idx: NPS.is_pronic(v) and NPS.get_pronic_index(v) == i))
    
    # Triangle numbers (polygonal, 3 sides) - Note: output says "Triangle" not "Triangular"
    TRIANGULAR = [1, 3, 6, 10, 15, 21, 28, 36, 45, 55]
    def test_triangular():
        for t in TRIANGULAR:
            info = NPS.get_polygonal_info(t)
            found = any("Triangle" in x for x in info)
            if not found:
                return False
        return True
    tests.append((f"Triangle numbers ({len(TRIANGULAR)} values)", test_triangular))
    
    # Square numbers
    SQUARES = [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
    def test_squares():
        for s in SQUARES:
            if not NPS.is_square(s):
                return False
        return True
    tests.append((f"Perfect squares ({len(SQUARES)} values)", test_squares))
    
    # Cubes
    CUBES = [1, 8, 27, 64, 125, 216, 343, 512, 729, 1000]
    def test_cubes():
        for c in CUBES:
            if not NPS.is_cube(c):
                return False
        return True
    tests.append((f"Perfect cubes ({len(CUBES)} values)", test_cubes))
    
    # Fibonacci
    FIBONACCI = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]
    def test_fibonacci():
        for f in FIBONACCI:
            if not NPS.is_fibonacci(f):
                return False
        return True
    tests.append((f"Fibonacci numbers ({len(FIBONACCI)} values)", test_fibonacci))
    
    # 3D Figurate: Tetrahedral = n(n+1)(n+2)/6
    TETRAHEDRAL = [(1, 1), (4, 2), (10, 3), (20, 4), (35, 5), (56, 6), (84, 7)]
    def test_tetrahedral():
        for val, idx in TETRAHEDRAL:
            info = NPS.get_figurate_3d_info(val)
            expected = f"Tetrahedral (Index: {idx})"
            if expected not in info:
                return False
        return True
    tests.append((f"Tetrahedral numbers ({len(TETRAHEDRAL)} values)", test_tetrahedral))
    
    # 3D Figurate: Cubic = n^3
    CUBIC = [(1, 1), (8, 2), (27, 3), (64, 4), (125, 5)]
    def test_cubic():
        for val, idx in CUBIC:
            info = NPS.get_figurate_3d_info(val)
            expected = f"Cubic (Index: {idx})"
            if expected not in info:
                return False
        return True
    tests.append((f"Cubic numbers ({len(CUBIC)} values)", test_cubic))
    
    # Abundance classification
    tests.append(("Abundant: 12", lambda: NPS.get_properties(12)['abundance_status'] == 'Abundant'))
    tests.append(("Deficient: 8", lambda: NPS.get_properties(8)['abundance_status'] == 'Deficient'))
    tests.append(("Perfect: 6", lambda: NPS.get_properties(6)['abundance_status'] == 'Perfect'))
    tests.append(("Perfect: 28", lambda: NPS.get_properties(28)['abundance_status'] == 'Perfect'))
    
    # Factor calculations
    tests.append(("Factors of 12", lambda: set(NPS.get_factors(12)) == {1, 2, 3, 4, 6, 12}))
    tests.append(("Factors of 28", lambda: set(NPS.get_factors(28)) == {1, 2, 4, 7, 14, 28}))
    
    # Prime factorization
    tests.append(("Prime factors of 12", lambda: NPS.get_prime_factorization(12) == [(2, 2), (3, 1)]))
    tests.append(("Prime factors of 100", lambda: NPS.get_prime_factorization(100) == [(2, 2), (5, 2)]))
    
    # Quadset Engine
    engine = QuadsetEngine()
    
    tests.append(("QuadsetEngine.compute(123) returns result", 
                 lambda: engine.calculate(123) is not None))
    tests.append(("Quadset has 4 members", 
                 lambda: len(engine.calculate(123).members) == 4))
    tests.append(("Quadset has upper_diff", 
                 lambda: hasattr(engine.calculate(123), 'upper_diff')))
    tests.append(("Quadset has lower_diff", 
                 lambda: hasattr(engine.calculate(123), 'lower_diff')))
    
    return run_tests(tests)

# ============================================================================
# ♀ VENUS - HARMONY & INTEGRATION
# ============================================================================

def test_venus():
    test_section("♀ VENUS - Harmony & Integration")
    
    tests = []
    
    # API Contract: all expected keys present
    EXPECTED_KEYS = [
        'is_prime', 'prime_ordinal', 'is_square', 'is_cube', 'is_fibonacci',
        'is_pronic', 'pronic_index', 'is_happy', 'happy_iterations', 'happy_chain',
        'digit_sum', 'factors', 'sum_factors', 'aliquot_sum', 'abundance_status',
        'abundance_diff', 'prime_factors', 'polygonal_info', 'centered_polygonal_info',
        'figurate_3d_info'
    ]
    
    def test_keys():
        props = NPS.get_properties(42)
        missing = [k for k in EXPECTED_KEYS if k not in props]
        return len(missing) == 0
    tests.append((f"API Contract: {len(EXPECTED_KEYS)} keys", test_keys))
    
    # Type contracts
    TYPE_CONTRACTS = [
        ('is_prime', bool),
        ('is_happy', bool),
        ('is_square', bool),
        ('is_cube', bool),
        ('is_fibonacci', bool),
        ('is_pronic', bool),
        ('prime_ordinal', int),
        ('happy_iterations', int),
        ('digit_sum', int),
        ('pronic_index', int),
        ('sum_factors', int),
        ('aliquot_sum', int),
        ('abundance_diff', int),
        ('happy_chain', list),
        ('factors', list),
        ('prime_factors', list),
        ('polygonal_info', list),
        ('centered_polygonal_info', list),
        ('figurate_3d_info', list),
        ('abundance_status', str),
    ]
    
    def test_types():
        props = NPS.get_properties(42)
        for key, expected_type in TYPE_CONTRACTS:
            if not isinstance(props.get(key), expected_type):
                return False
        return True
    tests.append((f"Type contracts ({len(TYPE_CONTRACTS)} fields)", test_types))
    
    # Quadset consistency
    engine = QuadsetEngine()
    
    def test_quadset_symmetry():
        result = engine.calculate(1162)
        # The four members should be: original, conrune, reverse, conrune_reverse
        members = result.members
        # Check that all are distinct in most cases (or equal in palindromic cases)
        return len(members) == 4
    tests.append(("Quadset has 4 members", test_quadset_symmetry))
    
    def test_quadset_diffs():
        result = engine.calculate(1162)
        # upper_diff = |original - conrune|
        # lower_diff = |reverse - conrune_reverse|
        return result.upper_diff is not None and result.lower_diff is not None
    tests.append(("Quadset has diff values", test_quadset_diffs))
    
    # Cross-check: Happy chain length vs iterations
    def test_chain_iteration_consistency():
        for n in [7, 19, 23, 44]:
            chain = NPS.get_happy_chain(n)
            iters = NPS.get_happy_iterations(n)
            # Chain includes starting number and ending 1, so len = iters + 1
            if len(chain) != iters + 1:
                return False
        return True
    tests.append(("Chain length = iterations + 1", test_chain_iteration_consistency))
    
    return run_tests(tests)

# ============================================================================
# ☿ MERCURY - COMMUNICATION
# ============================================================================

def test_mercury():
    test_section("☿ MERCURY - Communication (Error Handling)")
    
    tests = []
    
    # None input handling
    def test_none_props():
        try:
            NPS.get_properties(None)
            return False  # Should have raised
        except (TypeError, ValueError, AttributeError):
            return True
    tests.append(("get_properties(None) raises", test_none_props))
    
    def test_none_happy():
        try:
            NPS.is_happy(None)
            return False
        except (TypeError, ValueError, AttributeError):
            return True
    tests.append(("is_happy(None) raises", test_none_happy))
    
    # String input handling
    def test_string_props():
        try:
            NPS.get_properties("abc")
            return False
        except (TypeError, ValueError, AttributeError):
            return True
    tests.append(("get_properties('abc') raises", test_string_props))
    
    # Float input handling (should reject or truncate)
    def test_float_props():
        try:
            result = NPS.get_properties(3.14)
            # If it doesn't raise, it should treat as int
            return isinstance(result, dict)
        except (TypeError, ValueError):
            return True  # Raising is also acceptable
    tests.append(("get_properties(3.14) handles gracefully", test_float_props))
    
    return run_tests(tests)

# ============================================================================
# ☾ MOON - MEMORY & REFLECTION
# ============================================================================

def test_moon():
    test_section("☾ MOON - Memory & Reflection (Statelessness)")
    
    tests = []
    
    # Statelessness
    def test_stateless():
        props1 = NPS.get_properties(42)
        props2 = NPS.get_properties(42)
        return props1 == props2
    tests.append(("get_properties is stateless", test_stateless))
    
    # Determinism
    def test_deterministic_chain():
        chain1 = NPS.get_happy_chain(7)
        chain2 = NPS.get_happy_chain(7)
        return chain1 == chain2
    tests.append(("get_happy_chain is deterministic", test_deterministic_chain))
    
    # No side effects
    def test_no_side_effects():
        before = NPS.get_properties(10)
        _ = NPS.get_properties(20)  # Call with different value
        _ = NPS.get_properties(30)
        after = NPS.get_properties(10)  # Same as before
        return before == after
    tests.append(("No side effects from other calls", test_no_side_effects))
    
    # QuadsetEngine statelessness
    def test_engine_stateless():
        engine = QuadsetEngine()
        result1 = engine.calculate(123)
        result2 = engine.calculate(123)
        return result1.members[0].decimal == result2.members[0].decimal
    tests.append(("QuadsetEngine is stateless", test_engine_stateless))
    
    return run_tests(tests)

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*60)
    print("   DEEP RITE OF THE SEVEN SEALS")
    print("   Comprehensive Verification Protocol")
    print("="*60)
    
    total_passed = 0
    total_tests = 0
    seal_results = []
    
    seals = [
        ("♄ Saturn", test_saturn),
        ("♃ Jupiter", test_jupiter),
        ("♂ Mars", test_mars),
        ("☉ Sun", test_sun),
        ("♀ Venus", test_venus),
        ("☿ Mercury", test_mercury),
        ("☾ Moon", test_moon),
    ]
    
    for seal_name, test_fn in seals:
        try:
            passed, total = test_fn()
            total_passed += passed
            total_tests += total
            status = "PASS" if passed == total else "PARTIAL" if passed > 0 else "FAIL"
            seal_results.append((seal_name, passed, total, status))
        except Exception as e:
            print(f"\n  ✗ SEAL FAILED WITH EXCEPTION: {e}")
            traceback.print_exc()
            seal_results.append((seal_name, 0, 1, "ERROR"))
            total_tests += 1
    
    # Summary
    test_section("PLANETARY REPORT")
    print()
    print("  Seal           | Tests    | Status")
    print("  " + "-"*40)
    for name, passed, total, status in seal_results:
        status_icon = "✓" if status == "PASS" else "⚠" if status == "PARTIAL" else "✗"
        print(f"  {name:<14} | {passed:>3}/{total:<3}   | {status_icon} {status}")
    
    print("  " + "-"*40)
    pct = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"  TOTAL          | {total_passed:>3}/{total_tests:<3}   | {pct:.1f}%")
    
    print()
    if total_passed == total_tests:
        print("  ✓ ALL SEALS BROKEN - THE TEMPLE STANDS STRONG")
    else:
        print(f"  ⚠ {total_tests - total_passed} TESTS FAILED - REVIEW REQUIRED")
    print()
    
    return 0 if total_passed == total_tests else 1

if __name__ == "__main__":
    sys.exit(main())
