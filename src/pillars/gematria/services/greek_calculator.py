"""Backward compatibility shim for GreekCalculator."""
from shared.services.gematria.greek_calculator import (
    GreekGematriaCalculator, GreekLetterValueCalculator, GreekOrdinalCalculator,  # type: ignore[reportUnusedImport]
    GreekSmallValueCalculator, GreekKolelCalculator, GreekSquareCalculator,  # type: ignore[reportUnusedImport]
    GreekCubeCalculator, GreekTriangularCalculator, GreekDigitalCalculator,  # type: ignore[reportUnusedImport]
    GreekOrdinalSquareCalculator, GreekFullValueCalculator,
    GreekReverseSubstitutionCalculator, GreekPairMatchingCalculator,
    GreekNextLetterCalculator
)
