"""
Demonstration of pytest markers in Isopgem.

This file shows how to use markers to categorize tests.
Run with different marker filters to see the effect:

    # Run only fast unit tests
    pytest -m unit tests/examples/test_markers_demo.py

    # Run everything except slow tests
    pytest -m "not slow" tests/examples/test_markers_demo.py

    # Run only integration tests
    pytest -m integration tests/examples/test_markers_demo.py

    # Run tests that need network
    pytest -m network tests/examples/test_markers_demo.py

    # Combine markers - run integration tests that aren't slow
    pytest -m "integration and not slow" tests/examples/test_markers_demo.py
"""
import pytest
import time


# ============================================================================
# Unit Tests - Fast, No I/O
# ============================================================================

@pytest.mark.unit
def test_gematria_calculation():
    """Fast unit test - pure calculation, no I/O."""
    from shared.services.gematria.calculator import GematriaCalculator

    calc = GematriaCalculator()
    result = calc.calculate_value("א")

    # Aleph = 1 in standard Hebrew
    assert result > 0


@pytest.mark.unit
def test_script_detection():
    """Fast unit test - text analysis, no I/O."""
    from shared.utils.text_utils import detect_script

    # Test Hebrew detection
    assert detect_script("שלום") == "hebrew"

    # Test Greek detection
    assert detect_script("λόγος") == "greek"

    # Test Latin/English detection
    assert detect_script("hello") == "latin"


@pytest.mark.unit
def test_verse_parser():
    """Fast unit test - string parsing, no I/O."""
    from shared.utils.verse_parser import parse_verse_reference

    result = parse_verse_reference("Genesis 1:1")

    assert result["book"] == "Genesis"
    assert result["chapter"] == 1
    assert result["verse"] == 1


# ============================================================================
# Integration Tests - Touch Filesystem/Services
# ============================================================================

@pytest.mark.integration
@pytest.mark.requires_data
def test_lexicon_lookup_hebrew(lexicon_resolver):
    """Integration test - loads real Hebrew lexicon."""
    results = lexicon_resolver.lookup_hebrew("אלהים")

    assert len(results) > 0
    assert any("God" in r.definition for r in results)


@pytest.mark.integration
@pytest.mark.requires_data
def test_etymology_lookup_english(etymology_service):
    """Integration test - loads etymology database."""
    result = etymology_service.get_word_origin("logic")

    assert result.word == "logic"
    assert len(result.etymology) > 0


@pytest.mark.integration
@pytest.mark.requires_data
def test_config_loads_paths(reset_config):
    """Integration test - verifies config can find data directories."""
    from shared.config import get_config

    config = get_config()

    # These should exist in your project
    assert config.paths.data_root.exists()
    assert config.paths.lexicons.exists()
    assert config.paths.etymology_db.exists()


# ============================================================================
# Slow Tests - Take >5 seconds
# ============================================================================

@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.memory_intensive
def test_enrich_multiple_keys():
    """
    Slow integration test - enriches multiple lexicon keys.

    This test takes 10+ seconds and uses significant memory.
    Skip during development with: pytest -m "not slow"
    """
    from shared.services.lexicon.enrichment_service import EnrichmentService

    service = EnrichmentService()

    # Enrich a few test keys
    test_words = ["אלהים", "λόγος", "שלום"]

    for word in test_words:
        service.enrich_word(word)
        # Simulate slow processing
        time.sleep(0.5)

    # This test is intentionally slow to demonstrate the 'slow' marker


@pytest.mark.slow
@pytest.mark.integration
def test_load_all_lexicons():
    """
    Slow test - loads ALL lexicon indexes.

    This can take 10+ seconds and use 100+ MB of memory.
    """
    from shared.services.lexicon.comprehensive_lexicon_service import ComprehensiveLexiconService

    service = ComprehensiveLexiconService()

    # Force load all indexes
    service._load_compact_index("hebrew")
    service._load_compact_index("greek")
    service._load_compact_index("latin")
    service._load_compact_index("english")

    # Verify they loaded
    assert len(service._compact_indexes) > 0


# ============================================================================
# Network Tests - Require Internet
# ============================================================================

@pytest.mark.network
@pytest.mark.slow
def test_sefaria_api_lookup():
    """
    Network test - calls Sefaria API.

    Requires internet connection. Skip offline with: pytest -m "not network"
    """
    from shared.services.document_manager.etymology_service import EtymologyService

    service = EtymologyService()

    # This will attempt network call to Sefaria
    # (only if enable_sefaria_api is True in config)
    result = service._try_online_api("word")

    # May return empty if network unavailable or API down
    # Just verify it doesn't crash


@pytest.mark.network
def test_wiktionary_scraping():
    """
    Network test - scrapes Wiktionary.

    Very slow and requires internet. Usually disabled in config.
    """
    pytest.skip("Wiktionary scraping is slow and flaky - skip by default")


# ============================================================================
# UI Tests - Require PyQt6
# ============================================================================

@pytest.mark.ui
def test_create_main_window():
    """
    UI test - creates PyQt6 window.

    Requires PyQt6 and may need display/X server.
    """
    from PyQt6.QtWidgets import QApplication
    import sys

    # Qt tests need QApplication
    app = QApplication.instance() or QApplication(sys.argv)

    from src.ui.main_window import MainWindow

    window = MainWindow()
    assert window is not None

    # Don't show window in tests
    window.close()


# ============================================================================
# Experimental Tests - For Features In Development
# ============================================================================

@pytest.mark.experimental
@pytest.mark.unit
def test_ai_suggestions():
    """
    Experimental test - for features not yet stable.

    These tests may fail and are excluded from CI.
    """
    from shared.config import get_config

    config = get_config()

    # AI suggestions are experimental
    if config.features.enable_ai_suggestions:
        # Test AI suggestion logic
        pass
    else:
        pytest.skip("AI suggestions not enabled")


# ============================================================================
# Parameterized Test Example
# ============================================================================

@pytest.mark.unit
@pytest.mark.parametrize("word,expected_script", [
    ("שלום", "hebrew"),
    ("λόγος", "greek"),
    ("hello", "latin"),
    ("你好", "unknown"),  # Chinese - not supported
])
def test_script_detection_parametrized(word, expected_script):
    """
    Parameterized unit test - runs multiple times with different inputs.

    This creates 4 separate test cases automatically.
    """
    from shared.utils.text_utils import detect_script

    result = detect_script(word)
    assert result == expected_script or expected_script == "unknown"
