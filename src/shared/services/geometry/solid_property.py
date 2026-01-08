"""Shared dataclasses for 3D solid calculators."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class SolidProperty:
    """Describes a metric exposed by a solid calculator."""

    name: str
    key: str
    unit: str = ''
    value: Optional[float] = None
    precision: int = 4
    editable: bool = True
    formula: Optional[str] = None


__all__ = ["SolidProperty"]
