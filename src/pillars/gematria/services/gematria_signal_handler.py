"""Gematria Signal Handler - Signal Bus responder for cross-pillar calculations.

This service subscribes to the GematriaBus and provides Gematria calculations
to any pillar that requests them, preserving pillar sovereignty per The Covenant.

The handler is initialized at application startup and remains active for the
entire session, responding to calculation requests via PyQt signals.
"""
from PyQt6.QtCore import QObject
from shared.signals import gematria_bus
from typing import Dict
import logging

# Import all calculator classes
from pillars.gematria.services import (
    GematriaCalculator,
    HebrewGematriaCalculator, HebrewSofitCalculator, HebrewLetterValueCalculator,
    HebrewOrdinalCalculator, HebrewSmallValueCalculator, HebrewAtBashCalculator,
    HebrewAlbamCalculator, HebrewKolelCalculator, HebrewSquareCalculator,
    HebrewCubeCalculator, HebrewTriangularCalculator, HebrewIntegralReducedCalculator,
    HebrewOrdinalSquareCalculator, HebrewFullValueCalculator,
    GreekGematriaCalculator, GreekLetterValueCalculator, GreekOrdinalCalculator,
    GreekSmallValueCalculator, GreekKolelCalculator, GreekSquareCalculator,
    GreekCubeCalculator, GreekTriangularCalculator, GreekDigitalCalculator,
    GreekOrdinalSquareCalculator, GreekFullValueCalculator,
    GreekReverseSubstitutionCalculator, GreekPairMatchingCalculator,
    GreekNextLetterCalculator,
    TQGematriaCalculator, TQReducedCalculator, TQSquareCalculator,
    TQTriangularCalculator, TQPositionCalculator,
    ArabicGematriaCalculator, ArabicMaghrebiCalculator, ArabicSmallValueCalculator,
    ArabicOrdinalCalculator, SanskritKatapayadiCalculator
)

logger = logging.getLogger(__name__)


class GematriaSignalHandler(QObject):
    """
    Handles Gematria calculation requests from other pillars via Signal Bus.
    
    This handler:
    - Subscribes to gematria_bus signals at initialization
    - Maintains a registry of all available calculators
    - Responds to calculation_requested with calculation_completed
    - Responds to cipher_list_requested with cipher_list_completed
    
    The handler preserves pillar sovereignty by allowing other pillars to
    request calculations without importing Gematria pillar classes directly.
    """
    
    def __init__(self):
        """Initialize the handler and subscribe to signals."""
        super().__init__()
        self._registry: Dict[str, GematriaCalculator] = self._build_registry()
        
        # Subscribe to signals
        gematria_bus.calculation_requested.connect(self._handle_calculation)
        gematria_bus.cipher_list_requested.connect(self._handle_cipher_list)
        
        logger.info(f"GematriaSignalHandler initialized with {len(self._registry)} calculators")
    
    def _build_registry(self) -> Dict[str, GematriaCalculator]:
        """
        Build the calculator registry.
        
        Instantiates all calculator classes and indexes them by their
        uppercase name for case-insensitive lookup.
        
        Returns:
            Dictionary mapping uppercase cipher names to calculator instances
        """
        calculators = [
            # Hebrew calculators
            HebrewGematriaCalculator(),
            HebrewSofitCalculator(),
            HebrewLetterValueCalculator(),
            HebrewOrdinalCalculator(),
            HebrewSmallValueCalculator(),
            HebrewAtBashCalculator(),
            HebrewAlbamCalculator(),
            HebrewKolelCalculator(),
            HebrewSquareCalculator(),
            HebrewCubeCalculator(),
            HebrewTriangularCalculator(),
            HebrewIntegralReducedCalculator(),
            HebrewOrdinalSquareCalculator(),
            HebrewFullValueCalculator(),
            
            # Greek calculators
            GreekGematriaCalculator(),
            GreekLetterValueCalculator(),
            GreekOrdinalCalculator(),
            GreekSmallValueCalculator(),
            GreekKolelCalculator(),
            GreekSquareCalculator(),
            GreekCubeCalculator(),
            GreekTriangularCalculator(),
            GreekDigitalCalculator(),
            GreekOrdinalSquareCalculator(),
            GreekFullValueCalculator(),
            GreekReverseSubstitutionCalculator(),
            GreekPairMatchingCalculator(),
            GreekNextLetterCalculator(),
            
            # TQ (English) calculators
            TQGematriaCalculator(),
            TQReducedCalculator(),
            TQSquareCalculator(),
            TQTriangularCalculator(),
            TQPositionCalculator(),
            
            # Arabic calculators
            ArabicGematriaCalculator(),
            ArabicMaghrebiCalculator(),
            ArabicSmallValueCalculator(),
            ArabicOrdinalCalculator(),
            
            # Sanskrit calculators
            SanskritKatapayadiCalculator(),
        ]
        
        return {c.name.upper(): c for c in calculators}
    
    def _handle_calculation(self, text: str, cipher: str):
        """
        Handle a calculation request and emit the result.
        
        Args:
            text: The text to calculate
            cipher: The cipher name (case-insensitive)
        """
        cipher_key = cipher.upper()
        calculator = self._registry.get(cipher_key)
        
        if not calculator:
            logger.warning(f"Unknown cipher requested: {cipher}")
            result = f"#CIPHER? ({cipher})"
        else:
            try:
                result = calculator.calculate(text)
                logger.debug(f"Calculated '{text}' using {cipher}: {result}")
            except Exception as e:
                logger.error(f"Calculation error for '{text}' using {cipher}: {e}")
                result = "#ERROR!"
        
        # Emit response
        gematria_bus.calculation_completed.emit(text, cipher, result)
    
    def _handle_cipher_list(self):
        """Handle a cipher list request and emit the result."""
        cipher_names = sorted([c.name for c in self._registry.values()])
        logger.debug(f"Cipher list requested: {len(cipher_names)} ciphers")
        gematria_bus.cipher_list_completed.emit(cipher_names)
