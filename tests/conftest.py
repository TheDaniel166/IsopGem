"""
Pytest configuration and shared fixtures for Isopgem tests.

This file is automatically loaded by pytest before running tests.
It provides:
- Path setup for importing src/ modules
- Common fixtures for tests
- Test environment configuration
"""
from __future__ import annotations

import sys
import os
from pathlib import Path
from typing import Generator

import pytest


def pytest_configure() -> None:
    """
    Ensure `src/` is importable during tests.

    Some tests import modules as `pillars.*` / `shared.*`, which live under
    `<repo>/src`. When pytest runs from the repo root, that directory is not
    automatically on `sys.path`.
    """
    repo_root = Path(__file__).resolve().parents[1]
    src_path = repo_root / "src"

    if src_path.exists() and str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


# Ignore legacy code
collect_ignore = ['_legacy']


# Root directories - available to all tests
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
DATA_DIR = ROOT_DIR / "data"
TEST_DIR = ROOT_DIR / "tests"


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get project root directory."""
    return ROOT_DIR


@pytest.fixture(scope="session")
def data_dir() -> Path:
    """Get data directory (for test data)."""
    return DATA_DIR


@pytest.fixture(scope="function")
def reset_config():
    """
    Reset application config before and after each test.

    Use this fixture for tests that modify config state.

    Example:
        def test_config_feature_flag(reset_config):
            from shared.config import get_config
            config = get_config()
            assert config.features.enable_multi_language_gematria
    """
    from shared.config import reset_config as _reset_config

    # Reset before test
    _reset_config()

    yield

    # Reset after test
    _reset_config()


@pytest.fixture(scope="function")
def test_env_vars() -> Generator[dict, None, None]:
    """
    Provide clean environment variables for tests.

    Saves current env vars, yields empty dict you can modify,
    then restores original env vars after test.

    Example:
        def test_config_with_env(test_env_vars):
            test_env_vars['ISOPGEM_ETY_WEB'] = '0'
            os.environ.update(test_env_vars)

            from shared.config import get_config, reset_config
            reset_config()  # Force reload with new env
            config = get_config()

            assert not config.features.enable_etymology_web_fallback
    """
    # Save original environment
    original_env = dict(os.environ)

    # Yield empty dict for test to populate
    test_vars = {}
    yield test_vars

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


# ============================================================================
# Service Fixtures (add more as needed)
# ============================================================================

@pytest.fixture(scope="function")
def etymology_service():
    """
    Provide an EtymologyService instance for testing.

    Note: Marked as requires_data because it needs etymology_db files.
    """
    from shared.services.document_manager.etymology_service import EtymologyService
    return EtymologyService()


@pytest.fixture(scope="function")
def lexicon_resolver():
    """
    Provide a LexiconResolver instance for testing.

    Note: Marked as requires_data because it needs lexicon files.
    """
    from shared.services.lexicon.lexicon_resolver import LexiconResolver
    return LexiconResolver()


# ============================================================================
# Mock Fixtures (for tests that should avoid I/O)
# ============================================================================

@pytest.fixture
def mock_lexicon_data():
    """
    Provide mock lexicon data for unit tests.

    Use this instead of loading real lexicons in unit tests.

    Example:
        @pytest.mark.unit
        def test_lexicon_parsing(mock_lexicon_data):
            # Test parsing logic without loading real files
            pass
    """
    return {
        "hebrew": [
            {"word": "אלהים", "definition": "God, gods", "strongs": "H430"},
            {"word": "שלום", "definition": "peace, completeness", "strongs": "H7965"},
        ],
        "greek": [
            {"word": "λόγος", "definition": "word, reason", "strongs": "G3056"},
            {"word": "ἀγάπη", "definition": "love", "strongs": "G26"},
        ],
    }


# ============================================================================
# Pytest Hooks
# ============================================================================

def pytest_collection_modifyitems(config, items):
    """
    Automatically mark tests based on their characteristics.

    This hook runs after test collection and can add markers based on:
    - Test file location
    - Test name patterns
    - Imports used in the test
    """
    for item in items:
        # Mark UI tests
        if "ui" in str(item.fspath).lower() or "qt" in item.name.lower():
            item.add_marker(pytest.mark.ui)

        # Mark integration tests (tests in integration/ folder)
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Mark unit tests (tests in unit/ folder)
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)


def pytest_configure(config):
    """Add custom header to pytest output."""
    config.addinivalue_line(
        "markers",
        "Test session configuration loaded successfully"
    )
