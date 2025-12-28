"""SQLAlchemy entity for persisting gematria calculations (Shim).
Moves actual implementation to shared.models.gematria.
"""
from shared.models.gematria import CalculationEntity

__all__ = ["CalculationEntity"]
