# Test Suite Quick Start

Your test suite has been reorganized for fast, efficient testing.

## Structure

```
tests/
├── unit/              # 26 fast tests (geometry, calculations)
│   ├── geometry/      # All geometry calculation tests
│   ├── gematria/      # Gematria logic tests
│   └── ...
├── integration/       # 7 tests (database, services)
│   ├── astrology/
│   ├── document/
│   └── gematria/
├── ui/                # 4 tests (PyQt6 components)
│   ├── common/
│   └── document/
├── manual/            # 53 verification scripts (not run in CI)
│   ├── rituals/       # Manual test rituals
│   └── verification/  # Manual verification scripts
└── examples/          # Example tests showing best practices
```

## Quick Commands

### Fast Development Loop (< 5 seconds)

```bash
# Run only fast unit tests
pytest -m unit

# Results: 129 tests in ~2-3 seconds
```

### Integration Tests (~1-2 minutes)

```bash
# Run integration tests (database, services)
pytest -m integration

# Results: ~10-15 tests
```

### Skip Manual Tests

```bash
# Run all automated tests (skip manual verification)
pytest tests/unit/ tests/integration/ tests/ui/
```

### Run Everything

```bash
# Full suite
pytest

# Note: Includes manual/ tests which may require human interaction
```

## Auto-Marking

Tests are **automatically marked** based on directory:

- Tests in `tests/unit/` → `@pytest.mark.unit`
- Tests in `tests/integration/` → `@pytest.mark.integration`
- Tests in `tests/ui/` → `@pytest.mark.ui`

**No decorators needed!** Just put the test in the right directory.

## Example Workflow

### 1. Working on Geometry Feature

```bash
# Run only geometry tests
pytest tests/unit/geometry/ -v

# Fast feedback loop
```

### 2. Before Committing

```bash
# Run unit + integration (skip manual)
pytest -m "unit or integration"

# Should complete in ~1-2 minutes
```

### 3. CI/CD Pipeline

```yaml
# Stage 1: Unit tests (fast smoke test)
- pytest -m unit

# Stage 2: Integration tests
- pytest -m integration

# Stage 3: UI tests (if needed)
- pytest -m ui
```

## Statistics

After reorganization:

- **Total**: 175 test items collected
- **Unit**: 129 tests (auto-marked)
- **Integration**: ~15 tests (auto-marked)
- **UI**: ~4 tests (auto-marked)
- **Manual**: 53 scripts (for verification)

## Adding New Tests

Just place the test in the appropriate directory:

```python
# tests/unit/gematria/test_new_cipher.py
def test_cipher_calculation():
    """This automatically gets @pytest.mark.unit"""
    calc = NewCipher()
    assert calc.calculate("test") == 42
```

```python
# tests/integration/database/test_new_storage.py
def test_save_to_database(tmp_path):
    """This automatically gets @pytest.mark.integration"""
    service = StorageService(tmp_path)
    result = service.save(data)
    assert result.success
```

## Common Patterns

### Run Tests for Specific Pillar

```bash
pytest tests/unit/geometry/      # Geometry tests only
pytest tests/unit/gematria/      # Gematria tests only
pytest tests/integration/astrology/  # Astrology integration tests
```

### Skip Slow Tests

```bash
pytest -m "unit and not slow"
```

### Skip UI Tests (Headless CI)

```bash
pytest -m "not ui"
```

## Benefits

### Before Reorganization
- Run all 175+ tests on every change
- Wait 5+ minutes for feedback
- Hard to find specific tests

### After Reorganization
- Run only 129 unit tests in 2-3 seconds
- Fast development loop
- Clear organization
- Auto-marking (no decorators)

## Manual Tests

The `manual/` directory contains verification scripts and "rituals":

```bash
# These are NOT run by default
pytest tests/manual/  # Skip in CI

# Run specific manual test
.venv/bin/python tests/manual/rituals/rite_of_genesis_verification.py
```

These are for manual verification and shouldn't be in CI/CD.

## Documentation

- **This File**: Quick start commands
- [TESTING_WITH_MARKERS.md](TESTING_WITH_MARKERS.md): Detailed marker documentation
- [tests/README.md](../tests/README.md): Complete test suite documentation
- [pytest.ini](../pytest.ini): Pytest configuration

## Summary

Your test suite is now organized for speed:

```bash
# Development (< 5 seconds)
pytest -m unit

# Pre-commit (~1 minute)
pytest -m "unit or integration"

# Full suite (~2 minutes)
pytest tests/unit/ tests/integration/ tests/ui/

# Everything including manual (~5+ minutes)
pytest
```

Tests are auto-marked based on directory location - no decorators needed!
