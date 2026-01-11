"""Gematria Signal Bus for decoupled calculation requests.

This module provides a signal bus that allows any pillar to request Gematria
calculations WITHOUT importing the Gematria pillar or calculator classes directly.
This preserves pillar sovereignty per The Covenant (Section 2).

Usage:
    # In any service/UI file (no pillar imports needed):
    from shared.signals import gematria_bus
    
    # Request a calculation
    result = gematria_bus.request_calculation("Hello World", "English (TQ)")
    # Returns: int or error string like "#CIPHER?"
    
    # List available ciphers
    ciphers = gematria_bus.request_cipher_list()
    # Returns: list of cipher names

The Gematria pillar subscribes to this bus and provides calculation services,
preserving pillar sovereignty while enabling cross-pillar functionality.
"""
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Any, List, Optional


class GematriaBus(QObject):
    """
    PyQt Signal Bus for cross-pillar Gematria calculations.
    
    Signals:
        calculation_requested: Request a Gematria calculation
            Args:
                text (str): The text to calculate
                cipher (str): The cipher name (e.g., "English (TQ)", "Hebrew Gematria")
                
        calculation_completed: Response with the result
            Args:
                text (str): The original text
                cipher (str): The cipher used
                result (Any): The calculated value (int) or error string
                
        cipher_list_requested: Request list of available ciphers
        
        cipher_list_completed: Response with cipher list
            Args:
                ciphers (list): List of available cipher names
    """
    
    # Request signals
    calculation_requested = pyqtSignal(str, str)  # (text, cipher)
    cipher_list_requested = pyqtSignal()
    
    # Response signals
    calculation_completed = pyqtSignal(str, str, object)  # (text, cipher, result)
    cipher_list_completed = pyqtSignal(list)  # (cipher_names)
    
    def __init__(self):
        """Initialize the Gematria bus."""
        super().__init__()
        self._last_result: Optional[Any] = None
        self._last_cipher_list: Optional[List[str]] = None
        self._result_ready = False
        self._cipher_list_ready = False
    
    def request_calculation(self, text: str, cipher: str = "English (TQ)", timeout_ms: int = 1000) -> Any:
        """
        Synchronous wrapper for calculation requests.
        
        Emits calculation_requested signal and waits for calculation_completed response.
        This enables spreadsheet formulas to get immediate results while maintaining
        architectural decoupling.
        
        Args:
            text: The text to calculate
            cipher: The cipher name
            timeout_ms: Maximum wait time in milliseconds
            
        Returns:
            The calculated value (int) or error string ("#CIPHER?", "#ERROR!", etc.)
        """
        from PyQt6.QtCore import QEventLoop, QTimer
        
        # Reset state
        self._last_result = None
        self._result_ready = False
        
        # Connect to response signal
        def handle_response(resp_text: str, resp_cipher: str, result: Any):
            """Handle the calculation response."""
            if resp_text == text and resp_cipher == cipher:
                self._last_result = result
                self._result_ready = True
        
        self.calculation_completed.connect(handle_response)
        
        # Emit request
        self.calculation_requested.emit(text, cipher)
        
        # Wait for response with timeout
        loop = QEventLoop()
        timer = QTimer()
        timer.timeout.connect(loop.quit)
        timer.start(timeout_ms)
        
        # Exit loop when result is ready or timeout
        while not self._result_ready and timer.isActive():
            loop.processEvents()
        
        timer.stop()
        self.calculation_completed.disconnect(handle_response)
        
        # Return result or timeout error
        if self._result_ready:
            return self._last_result
        else:
            return "#TIMEOUT!"
    
    def request_cipher_list(self, timeout_ms: int = 500) -> List[str]:
        """
        Synchronous wrapper for cipher list requests.
        
        Args:
            timeout_ms: Maximum wait time in milliseconds
            
        Returns:
            List of available cipher names
        """
        from PyQt6.QtCore import QEventLoop, QTimer
        
        # Reset state
        self._last_cipher_list = None
        self._cipher_list_ready = False
        
        # Connect to response signal
        def handle_response(ciphers: List[str]):
            """Handle the cipher list response."""
            self._last_cipher_list = ciphers
            self._cipher_list_ready = True
        
        self.cipher_list_completed.connect(handle_response)
        
        # Emit request
        self.cipher_list_requested.emit()
        
        # Wait for response with timeout
        loop = QEventLoop()
        timer = QTimer()
        timer.timeout.connect(loop.quit)
        timer.start(timeout_ms)
        
        # Exit loop when result is ready or timeout
        while not self._cipher_list_ready and timer.isActive():
            loop.processEvents()
        
        timer.stop()
        self.cipher_list_completed.disconnect(handle_response)
        
        # Return result or empty list
        return self._last_cipher_list if self._cipher_list_ready else []


# Global singleton instance
# All pillars import this same instance
gematria_bus = GematriaBus()
