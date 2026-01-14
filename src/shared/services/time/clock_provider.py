"""
Clock Provider: Deterministic Time for Testability.

Removes time from the realm of fate and places it under Law.
Instead of services asking the cosmos "What time is it?", time is handed to them.
"""
"""
SHARED JUSTIFICATION:
- RATIONALE: Port (Boundary abstraction)
- USED BY: Gematria (2 references)
- CRITERION: 1 (Cross-pillar infrastructure port)
"""

from datetime import datetime
from typing import Protocol


class ClockProvider(Protocol):
    """Protocol for providing the current time."""
    
    def now(self) -> datetime:
        """Return the current datetime."""
        ...


class SystemClock:
    """Production clock that returns real system time."""
    
    def now(self) -> datetime:
        """Return the current system datetime."""
        return datetime.now()


class FixedClock:
    """Test clock that returns a fixed datetime."""
    
    def __init__(self, fixed_time: datetime):
        """
        Initialize with a fixed datetime.
        
        Args:
            fixed_time: The datetime to always return
        """
        self._time = fixed_time
    
    def now(self) -> datetime:
        """Return the fixed datetime."""
        return self._time
    
    def set_time(self, new_time: datetime) -> None:
        """
        Update the fixed time.
        
        Args:
            new_time: The new datetime to return
        """
        self._time = new_time


# Singleton instance for application-wide use
_system_clock = SystemClock()


def get_system_clock() -> ClockProvider:
    """Get the singleton system clock instance."""
    return _system_clock