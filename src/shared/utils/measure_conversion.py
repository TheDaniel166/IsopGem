from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


@dataclass(frozen=True)
class ConversionResult:
    """
    Conversion Result class definition.
    
    """
    input_value: float
    from_name: str
    to_name: str
    base_value: float
    base_unit: str
    converted_value: float


def parse_measure_value(raw: str) -> float:
    """Parse a human-friendly numeric value.

    Supported:
    - ints/floats ("12", "3.5")
    - comma thousands separators ("1,234.56")
    - simple fractions ("3/4", "-5/2")
    """

    text = raw.strip().replace(",", "")
    if not text:
        raise ValueError("Invalid number")

    if "/" in text:
        parts = text.split("/")
        if len(parts) != 2:
            raise ValueError("Invalid number")
        num_s, den_s = parts[0].strip(), parts[1].strip()
        if not num_s or not den_s:
            raise ValueError("Invalid number")
        num = float(num_s)
        den = float(den_s)
        if den == 0:
            raise ValueError("Invalid number")
        return num / den

    return float(text)


def _coerce_factor(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        return float(value)
    return 1.0


def convert_between_units(
    value: float,
    from_unit: Dict[str, Any],
    to_unit: Dict[str, Any],
) -> ConversionResult:
    """Convert between units using `to_si` factors and a shared `si_unit` base."""

    if not isinstance(from_unit, dict) or not isinstance(to_unit, dict):
        raise ValueError("Invalid unit")

    from_factor = _coerce_factor(from_unit.get("to_si", 1.0))
    to_factor = _coerce_factor(to_unit.get("to_si", 1.0))
    if to_factor == 0:
        raise ValueError("Invalid unit")

    base_unit = str(from_unit.get("si_unit", ""))
    base_value = value * from_factor
    converted_value = base_value / to_factor

    return ConversionResult(
        input_value=value,
        from_name=str(from_unit.get("name") or ""),
        to_name=str(to_unit.get("name") or ""),
        base_value=base_value,
        base_unit=base_unit,
        converted_value=converted_value,
    )