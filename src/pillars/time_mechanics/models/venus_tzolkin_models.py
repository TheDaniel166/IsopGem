"""Venus ↔ Tzolkin overlay models.

These DTOs live in the Time Mechanics pillar because they bridge:
- Shared astronomical phenomena (Venus events)
- The Time Mechanics representation (TzolkinDate)

They are intentionally UI-agnostic so they can be consumed by the calendar grid later.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from .tzolkin_models import TzolkinDate


VenusOverlayKind = Literal[
    "inferior_conjunction",
    "superior_conjunction",
    "greatest_elongation_east",
    "greatest_elongation_west",
    "invisible_start",
    "invisible_end",
]


@dataclass(frozen=True)
class VenusTzolkinOverlayEvent:
    """A Venus event mapped onto a Tzolkin day."""

    dt_utc: datetime
    kind: VenusOverlayKind
    tzolkin: TzolkinDate
    elongation_deg: float
    illumination_fraction: float
