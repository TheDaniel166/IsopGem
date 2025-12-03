"""Service to compute Conrune pair information."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .ternary_service import TernaryService


@dataclass(frozen=True)
class ConrunePair:
    """Represents a ternary decimal pairing."""

    label: str
    ternary: str
    decimal: int


class ConrunePairFinderService:
    """Find Conrune pairs based on a target difference D."""

    NEGATIVE_SYMBOL = "-"  # Represents -1 in balanced ternary

    def __init__(self) -> None:
        self.ternary_service = TernaryService()

    def analyze(self, difference: int) -> Dict[str, object]:
        """Return Conrune pair information for the requested difference D."""
        balanced = self._decimal_to_balanced_ternary(difference)
        ternary_a = self._balanced_to_original_ternary(balanced)
        ternary_b = self.ternary_service.conrune_transform(ternary_a)

        decimal_a = self.ternary_service.ternary_to_decimal(ternary_a) if ternary_a else 0
        decimal_b = self.ternary_service.ternary_to_decimal(ternary_b) if ternary_b else 0
        calculated_diff = abs(decimal_a - decimal_b)
        expected_diff = abs(difference)

        pairs = [
            ConrunePair("Original (A)", ternary_a or "0", decimal_a),
            ConrunePair("Conrune (B)", ternary_b or "0", decimal_b),
        ]

        return {
            "balanced": balanced,
            "pairs": pairs,
            "calculated_difference": calculated_diff,
            "expected_difference": expected_diff,
            "verified": calculated_diff == expected_diff,
        }

    # ------------------------------------------------------------------
    def _decimal_to_balanced_ternary(self, number: int) -> str:
        if number == 0:
            return "0"

        digits: List[int] = []
        value = number
        while value != 0:
            value, remainder = divmod(value, 3)
            if remainder == 2:
                remainder = -1
                value += 1
            digits.append(remainder)

        symbol_map = { -1: self.NEGATIVE_SYMBOL, 0: "0", 1: "1" }
        return "".join(symbol_map[d] for d in reversed(digits))

    def _balanced_to_original_ternary(self, balanced: str) -> str:
        if not balanced:
            return "0"

        mapping = {
            self.NEGATIVE_SYMBOL: "1",  # -1 maps to digit 1
            "0": "0",
            "1": "2",
        }

        converted = []
        for char in balanced:
            converted.append(mapping.get(char, "0"))
        return "".join(converted)
