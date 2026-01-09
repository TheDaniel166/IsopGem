# Isopgem Test Suite

## Overview

This directory contains the test suite for Isopgem. Tests are organized using **pytest markers** to enable selective execution and fast development feedback.

## Quick Start

```bash
# Run all tests
pytest

# Run only fast unit tests (< 5 seconds)
pytest -m unit

# Run without slow tests
pytest -m "not slow"

# Run without network tests (for offline work)
pytest -m "not network"

# Run specific test file
pytest tests/examples/test_markers_demo.py
```

## Test Organization

```
tests/
├── conftest.py              # Shared fixtures and pytest configuration
├── examples/
│   └── test_markers_demo.py # Examples of how to use markers
├── unit/                    # Fast unit tests (auto-marked)
├── integration/             # Integration tests (auto-marked)
└── ui/                      # UI tests (auto-marked)
```

## Test Markers

Tests are categorized with markers to enable selective execution:

- `@pytest.mark.unit` - Fast tests with no I/O
- `@pytest.mark.integration` - Tests that touch filesystem/database
- `@pytest.mark.slow` - Tests taking >5 seconds
- `@pytest.mark.network` - Tests requiring internet
- `@pytest.mark.ui` - Tests requiring PyQt6
- `@pytest.mark.memory_intensive` - Tests using >100MB
- `@pytest.mark.requires_data` - Tests needing data files
- `@pytest.mark.experimental` - Unstable features

See [TESTING_WITH_MARKERS.md](../docs/TESTING_WITH_MARKERS.md) for detailed documentation.

## Available Fixtures

Defined in [conftest.py](conftest.py):

### Configuration Fixtures
- `project_root` - Path to project root
- `data_dir` - Path to data directory
- `reset_config()` - Reset app config before/after test
- `test_env_vars` - Clean environment variables for testing

### Service Fixtures
- `etymology_service()` - EtymologyService instance
- `lexicon_resolver()` - LexiconResolver instance

### Mock Fixtures
- `mock_lexicon_data` - Fake lexicon data for unit tests

## Writing Tests

### Unit Test Example

```python
import pytest

@pytest.mark.unit
def test_calculate_gematria():
    """Fast unit test - no I/O"""
    from shared.services.gematria.calculator import GematriaCalculator

    calc = GematriaCalculator()
    result = calc.calculate_value("א")

    assert result == 1  # Aleph = 1
```

### Integration Test Example

```python
import pytest

@pytest.mark.integration
@pytest.mark.requires_data
def test_lexicon_lookup(lexicon_resolver):
    """Integration test - uses real lexicon files"""
    results = lexicon_resolver.lookup_hebrew("שלום")

    assert len(results) > 0
    assert any("peace" in r.definition.lower() for r in results)
```

### Using Config Fixture

```python
import pytest

@pytest.mark.unit
def test_config_feature_flag(reset_config):
    """Test with clean config state"""
    from shared.config import get_config

    config = get_config()

    # Test default values
    assert config.features.enable_multi_language_gematria
    assert config.paths.data_root.exists()
```

### Using Environment Variables

```python
import pytest
import os

@pytest.mark.unit
def test_config_env_override(test_env_vars, reset_config):
    """Test config respects environment variables"""
    # Set test environment variable
    test_env_vars['ISOPGEM_ETY_WEB'] = '0'
    os.environ.update(test_env_vars)

    # Reset config to reload with new env
    from shared.config import reset_config as _reset, get_config
    _reset()

    config = get_config()

    # Verify env var was respected
    assert not config.features.enable_etymology_web_fallback
```

## Development Workflow

### Fast Iteration (< 5 seconds)
```bash
# Run only unit tests while coding
pytest -m unit

# Watch mode (requires pytest-watch)
ptw -- -m unit
```

### Before Committing (~1-2 minutes)
```bash
# Run all except slow/experimental
pytest -m "not slow and not experimental"
```

### Full Test Suite (~5+ minutes)
```bash
# Run everything
pytest

# With coverage report
pytest --cov=src --cov-report=html
```

## CI/CD Integration

Tests are organized for staged CI/CD pipelines:

```yaml
# Stage 1: Fast unit tests (30 seconds)
- pytest -m "unit and not slow"

# Stage 2: Integration tests (2 minutes)
- pytest -m "integration and not network"

# Stage 3: Full suite (5+ minutes)
- pytest
```

## Test Coverage

To generate coverage reports:

```bash
# Install pytest-cov
pip install pytest-cov

# Generate HTML report
pytest --cov=src --cov-report=html

# Open report
open htmlcov/index.html
```

## Troubleshooting

### Import Errors

If tests fail with import errors, the [conftest.py](conftest.py) should handle path setup automatically. If issues persist:

```python
# Verify src/ is on sys.path
import sys
from pathlib import Path

src_path = Path(__file__).resolve().parents[1] / "src"
assert str(src_path) in sys.path
```

### Missing Markers Warning

If you see "PytestUnknownMarkWarning", ensure the marker is registered in [pytest.ini](../pytest.ini).

### Data File Issues

Tests marked with `@pytest.mark.requires_data` need data files. Ensure:
- `data/lexicons/` exists and has lexicon files
- `data/etymology_db/` exists and has etymology files
- Config can find data paths

### PyQt6 Issues

UI tests may fail in headless environments. Use:

```python
@pytest.mark.ui
@pytest.mark.skipif(not HAS_DISPLAY, reason="No display available")
def test_ui_component():
    pass
```

## Best Practices

1. **Always mark tests** - Use at least one marker (unit/integration)
2. **Keep unit tests fast** - Unit tests should run in < 1 second each
3. **Use fixtures** - Leverage shared fixtures from conftest.py
4. **Isolate tests** - Each test should be independent
5. **Mock expensive operations** - Use `mock_lexicon_data` instead of loading real files in unit tests
6. **Document requirements** - Use `@pytest.mark.requires_data` if test needs data files

## Examples

See [test_markers_demo.py](examples/test_markers_demo.py) for comprehensive examples of:
- Using markers
- Writing unit vs integration tests
- Using fixtures
- Parameterized tests
- Skipping tests conditionally

## Documentation

- [TESTING_WITH_MARKERS.md](../docs/TESTING_WITH_MARKERS.md) - Detailed marker documentation
- [pytest.ini](../pytest.ini) - Pytest configuration
- [conftest.py](conftest.py) - Shared fixtures

## Contributing

When adding tests:
1. Place in appropriate directory (unit/, integration/, ui/)
2. Add appropriate markers
3. Use existing fixtures where possible
4. Document what the test validates
5. Ensure test is isolated and repeatable
