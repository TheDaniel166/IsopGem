"""
Service for analyzing mathematical patterns in Quadsets.
"""
import math
from typing import List
from ..models import QuadsetMember
from ..services.number_properties import NumberPropertiesService

class PatternAnalyzer:
    """Analyzes a collection of Quadset members for mathematical patterns."""

    def analyze(self, members: List[QuadsetMember]) -> str:
        """
        Generate a textual summary of patterns found in the quadset members.
        
        Args:
            members: List of the 4 main QuadsetMember objects.
            
        Returns:
            A formatted string report.
        """
        lines: list[str] = []
        decimals = [m.decimal for m in members]
        ternaries = [m.ternary for m in members]
        names = [m.name for m in members]

        # 1. LCM
        non_zero = [n for n in decimals if n != 0]
        lcm_value = math.lcm(*non_zero) if non_zero else 0
        lines.append(f"LCM of quadset decimals: {lcm_value:,}")

        # 2. GCD
        gcd_value = 0
        for value in decimals:
            gcd_value = math.gcd(gcd_value, abs(value))
        lines.append(
            f"GCD of quadset decimals: {gcd_value:,}" if gcd_value > 0 else "GCD of quadset decimals: 0"
        )

        # 3. Parity
        even_count = sum(1 for value in decimals if value % 2 == 0)
        odd_count = len(decimals) - even_count
        lines.append(f"Parity: {even_count} even, {odd_count} odd")

        # 4. Shared Divisor
        if gcd_value > 1:
            lines.append(f"Shared divisor (>1): {gcd_value}")
        else:
            lines.append("Shared divisor (>1): None")

        # 5. Primes
        primes = [
            f"{name} ({value:,})"
            for name, value in zip(names, decimals)
            if NumberPropertiesService.is_prime(value)
        ]
        if primes:
            lines.append(f"Primes: {', '.join(primes)}")
            lines.append(f"Prime density: {len(primes)}/{len(decimals)}")
        else:
            lines.append("Primes: None in the quadset")
            lines.append("Prime density: 0/4")

        # 6. Factor Counts
        factor_counts = []
        for name, value in zip(names, decimals):
            if value != 0:
                count = len(NumberPropertiesService.get_factors(abs(value)))
                factor_counts.append(f"{name}({count} factors)")
            else:
                factor_counts.append(f"{name}(undefined factors)")
        lines.append(f"Factor counts: {', '.join(factor_counts)}")

        # 7. Abundance
        abundance_parts = []
        for name, value in zip(names, decimals):
            props = NumberPropertiesService.get_properties(value)
            abundance_parts.append(f"{name} is {props['abundance_status']}")
        lines.append(f"Abundance: {', '.join(abundance_parts)}")

        # 8. Digit Sums & Roots
        digit_sums = [
            f"{name}({NumberPropertiesService.digit_sum(value)})"
            for name, value in zip(names, decimals)
        ]
        lines.append(f"Digit sums: {', '.join(digit_sums)}")
        
        digit_roots = [
            f"{name}({(abs(value) - 1) % 9 + 1 if value != 0 else 0})"
            for name, value in zip(names, decimals)
        ]
        lines.append(f"Digital roots: {', '.join(digit_roots)}")

        # 9. Decimal Palindromes
        reversed_palindromes = [
            f"{name} ({value:,})"
            for name, value in zip(names, decimals)
            if str(abs(value)) == str(abs(value))[::-1]
        ]
        if reversed_palindromes:
            lines.append(f"Decimal palindromes: {', '.join(reversed_palindromes)}")
        else:
            lines.append("Decimal palindromes: None")

        # 10. Arithmetic Progression
        sorted_decimals = sorted(decimals)
        diffs = [sorted_decimals[i + 1] - sorted_decimals[i] for i in range(3)]
        if len(set(diffs)) == 1:
            lines.append(f"Arithmetic progression: common difference {diffs[0]:,}")
        else:
            lines.append("Arithmetic progression: No")

        # 11. Geometric Progression
        geo_progression = "No"
        ratios = []
        for i in range(3):
            if sorted_decimals[i] == 0:
                ratios = []
                break
            ratios.append(sorted_decimals[i + 1] / sorted_decimals[i])
        if ratios and len(set(ratios)) == 1:
            geo_progression = f"Yes (ratio {ratios[0]:.2f})"
        lines.append(f"Geometric progression: {geo_progression}")

        # 12. Modular Congruence
        congruent_mod3 = {value % 3 for value in decimals}
        congruent_mod5 = {value % 5 for value in decimals}
        if len(congruent_mod3) == 1:
            lines.append(f"Congruent mod 3: {congruent_mod3.pop()} for all")
        if len(congruent_mod5) == 1:
            lines.append(f"Congruent mod 5: {congruent_mod5.pop()} for all")

        # 13. Ternary Palindromes
        palindromes = [
            f"{name} ({ternary})"
            for name, ternary in zip(names, ternaries)
            if ternary == ternary[::-1]
        ]
        if palindromes:
            lines.append(f"Ternary palindromes: {', '.join(palindromes)}")
        else:
            lines.append("Ternary palindromes: None")

        # 14. Binary-like (0/1 only)
        only_01 = [
            name
            for name, ternary in zip(names, ternaries)
            if set(ternary).issubset({"0", "1"})
        ]
        if only_01:
            lines.append(f"Digits limited to 0/1: {', '.join(only_01)}")
        else:
            lines.append("Digits limited to 0/1: None")

        # 15. Digit Frequencies
        digit_frequency = [
            f"{name}(0:{ternary.count('0')} 1:{ternary.count('1')} 2:{ternary.count('2')})"
            for name, ternary in zip(names, ternaries)
        ]
        lines.append(f"Digit frequencies: {', '.join(digit_frequency)}")

        return "\n".join(lines)
