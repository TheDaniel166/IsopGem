"""Session store for sharing the latest cymatics simulation result."""
from __future__ import annotations

from typing import Optional

from ..models import SimulationResult


class CymaticsSessionStore:
    """Singleton-style store for the most recent simulation result."""
    _last_simulation: Optional[SimulationResult] = None

    @classmethod
    def set_last_simulation(cls, result: SimulationResult) -> None:
        cls._last_simulation = result

    @classmethod
    def get_last_simulation(cls) -> Optional[SimulationResult]:
        return cls._last_simulation
