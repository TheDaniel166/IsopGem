"""Backward compatibility shim for HebrewCalculator."""
from shared.services.gematria.hebrew_calculator import (
    HebrewGematriaCalculator, HebrewSofitCalculator, HebrewLetterValueCalculator,  # type: ignore[reportUnusedImport]
    HebrewOrdinalCalculator, HebrewSmallValueCalculator, HebrewAtBashCalculator,  # type: ignore[reportUnusedImport]
    HebrewAlbamCalculator, HebrewKolelCalculator, HebrewSquareCalculator,  # type: ignore[reportUnusedImport]
    HebrewCubeCalculator, HebrewTriangularCalculator, HebrewIntegralReducedCalculator,  # type: ignore[reportUnusedImport]
    HebrewOrdinalSquareCalculator, HebrewFullValueCalculator
)
