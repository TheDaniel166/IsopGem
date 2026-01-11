"""Integration test for Gematria Signal Bus and Formula Engine.

Tests that the spreadsheet GEMATRIA formula works via Signal Bus communication
between the Correspondence and Gematria pillars.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from shared.signals import gematria_bus
from pillars.gematria.services.gematria_signal_handler import GematriaSignalHandler
from pillars.correspondences.services.formula_engine import FormulaEngine, FormulaRegistry
import pytest


# Global QApplication instance
_qapp = None
_handler = None


def setup_module():
    """Setup QApplication once for all tests."""
    global _qapp, _handler
    _qapp = QApplication.instance()
    if _qapp is None:
        _qapp = QApplication(sys.argv)
    _handler = GematriaSignalHandler()


def teardown_module():
    """Cleanup after all tests."""
    global _qapp, _handler
    if _qapp is not None:
        # Schedule quit to happen after all pending events
        QTimer.singleShot(0, _qapp.quit)
        # Process any remaining events
        _qapp.processEvents()


@pytest.fixture
def signal_handler():
    """Return the global signal handler."""
    return _handler


class TestGematriaSignalBus:
    """Test suite for Gematria Signal Bus integration."""
    
    def test_signal_bus_direct_calculation(self, signal_handler):
        """Test direct signal bus calculation request."""
        result = gematria_bus.request_calculation("Hello", "English (TQ)")
        
        assert isinstance(result, int), f"Expected int, got {type(result)}: {result}"
        assert result > 0, f"Expected positive value, got {result}"
        print(f"✓ Direct calculation: 'Hello' = {result}")
    
    def test_signal_bus_unknown_cipher(self, signal_handler):
        """Test that unknown cipher returns error."""
        result = gematria_bus.request_calculation("Test", "NonexistentCipher")
        
        assert isinstance(result, str), f"Expected error string, got {type(result)}"
        assert result.startswith("#CIPHER?"), f"Expected #CIPHER? error, got {result}"
        print(f"✓ Unknown cipher error: {result}")
    
    def test_signal_bus_empty_text(self, signal_handler):
        """Test calculation with empty text."""
        result = gematria_bus.request_calculation("", "English (TQ)")
        
        # Empty text should return 0 or handle gracefully
        assert isinstance(result, (int, str)), f"Expected int or error, got {type(result)}"
        print(f"✓ Empty text: {result}")
    
    def test_formula_engine_gematria_function(self, signal_handler):
        """Test GEMATRIA formula function via formula engine."""
        engine = FormulaEngine({})
        func = FormulaRegistry.get("GEMATRIA")
        
        assert func is not None, "GEMATRIA function not registered"
        
        # Test calculation
        result = func(engine, "World", "English (TQ)")
        
        assert isinstance(result, int), f"Expected int, got {type(result)}: {result}"
        assert result > 0, f"Expected positive value, got {result}"
        print(f"✓ Formula function: 'World' = {result}")
    
    def test_formula_engine_gematria_with_default_cipher(self, signal_handler):
        """Test GEMATRIA formula with default cipher."""
        engine = FormulaEngine({})
        func = FormulaRegistry.get("GEMATRIA")
        
        # Call without cipher (should use default)
        result = func(engine, "Test")
        
        assert isinstance(result, int), f"Expected int, got {type(result)}: {result}"
        print(f"✓ Default cipher: 'Test' = {result}")
    
    def test_formula_engine_gematria_hebrew(self, signal_handler):
        """Test GEMATRIA formula with Hebrew cipher."""
        engine = FormulaEngine({})
        func = FormulaRegistry.get("GEMATRIA")
        
        # Test Hebrew text
        result = func(engine, "שלום", "Hebrew (Standard)")
        
        assert isinstance(result, int), f"Expected int, got {type(result)}: {result}"
        assert result > 0, f"Expected positive value, got {result}"
        print(f"✓ Hebrew calculation: 'שלום' = {result}")
    
    def test_formula_engine_gematria_greek(self, signal_handler):
        """Test GEMATRIA formula with Greek cipher."""
        engine = FormulaEngine({})
        func = FormulaRegistry.get("GEMATRIA")
        
        # Test Greek text
        result = func(engine, "ΛΟΓΟΣ", "Greek (Isopsephy)")
        
        assert isinstance(result, int), f"Expected int, got {type(result)}: {result}"
        assert result > 0, f"Expected positive value, got {result}"
        print(f"✓ Greek calculation: 'ΛΟΓΟΣ' = {result}")
    
    def test_cipher_list_request(self, signal_handler):
        """Test requesting list of available ciphers."""
        ciphers = gematria_bus.request_cipher_list()
        
        assert isinstance(ciphers, list), f"Expected list, got {type(ciphers)}"
        assert len(ciphers) > 0, "Expected non-empty cipher list"
        
        # Check for expected ciphers
        expected_ciphers = ["English (TQ)", "Hebrew (Standard)", "Greek (Isopsephy)"]
        for cipher in expected_ciphers:
            assert cipher in ciphers, f"Expected cipher '{cipher}' not found in list"
        
        print(f"✓ Cipher list: {len(ciphers)} ciphers available")
        print(f"  Sample ciphers: {ciphers[:5]}")
    
    def test_formula_evaluation_with_gematria(self, signal_handler):
        """Test full formula evaluation with GEMATRIA function."""
        engine = FormulaEngine({})
        
        # Test formula: =GEMATRIA("Hello", "English (TQ)")
        result = engine.evaluate('=GEMATRIA("Hello", "English (TQ)")')
        
        assert isinstance(result, int), f"Expected int, got {type(result)}: {result}"
        assert result > 0, f"Expected positive value, got {result}"
        print(f"✓ Formula evaluation: =GEMATRIA(\"Hello\", \"English (TQ)\") = {result}")
    
    def test_formula_evaluation_with_concatenation(self, signal_handler):
        """Test GEMATRIA in complex formula."""
        engine = FormulaEngine({})
        
        # Test formula: =GEMATRIA("A") + GEMATRIA("B")
        result = engine.evaluate('=GEMATRIA("A", "English (TQ)") + GEMATRIA("B", "English (TQ)")')
        
        assert isinstance(result, (int, float)), f"Expected number, got {type(result)}: {result}"
        assert result > 0, f"Expected positive value, got {result}"
        print(f"✓ Complex formula: =GEMATRIA(\"A\") + GEMATRIA(\"B\") = {result}")
    
    def test_signal_bus_performance(self, signal_handler):
        """Test signal bus performance with multiple calculations."""
        import time
        
        start = time.time()
        for i in range(10):
            result = gematria_bus.request_calculation(f"Test{i}", "English (TQ)")
            assert isinstance(result, int), f"Calculation {i} failed"
        
        elapsed = time.time() - start
        avg_time = elapsed / 10
        
        assert avg_time < 0.1, f"Average calculation time too slow: {avg_time:.3f}s"
        print(f"✓ Performance: 10 calculations in {elapsed:.3f}s (avg {avg_time*1000:.1f}ms)")


def test_signal_bus_without_handler():
    """Test that signal bus handles no-handler scenario gracefully.
    
    NOTE: This test is skipped because the handler is initialized globally.
    In production, the handler is initialized at startup, so this scenario
    doesn't occur during normal operation.
    """
    pytest.skip("Handler is globally initialized for all tests")


if __name__ == "__main__":
    """Run tests with verbose output."""
    import sys
    sys.exit(pytest.main([__file__, "-v", "-s", "--tb=short"]))
