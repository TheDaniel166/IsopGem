# Testing with Pytest Markers

## Overview

Pytest markers are decorators that categorize tests so you can run specific subsets. This speeds up development by letting you run only relevant tests.

## Available Markers

Defined in [pytest.ini](../pytest.ini):

| Marker | Purpose | Example Use Case |
|--------|---------|------------------|
| `@pytest.mark.unit` | Fast tests, no I/O | Testing calculation logic |
| `@pytest.mark.integration` | Tests with filesystem/DB | Testing lexicon lookups |
| `@pytest.mark.slow` | Tests taking >5 seconds | Loading all lexicons |
| `@pytest.mark.network` | Tests requiring internet | Sefaria API calls |
| `@pytest.mark.ui` | Tests requiring PyQt6 | Window creation tests |
| `@pytest.mark.memory_intensive` | Tests using >100MB | Enrichment service tests |
| `@pytest.mark.requires_data` | Tests needing data files | Etymology lookups |
| `@pytest.mark.experimental` | Unstable/dev features | AI suggestions |

---

## Common Test Commands

### During Development (Fast Feedback)

```bash
# Run only fast unit tests (< 1 second each)
pytest -m unit

# Run unit tests, skip slow ones
pytest -m "unit and not slow"

# Run tests without network requirements (offline work)
pytest -m "not network"
```

### Before Committing (Thorough)

```bash
# Run all tests except experimental
pytest -m "not experimental"

# Run all integration tests
pytest -m integration

# Run everything except slow and network tests
pytest -m "not slow and not network"
```

### CI/CD Pipeline

```bash
# Stage 1: Fast unit tests (30 seconds)
pytest -m "unit and not slow"

# Stage 2: Integration tests (2 minutes)
pytest -m "integration and not network"

# Stage 3: Full suite (5+ minutes, nightly)
pytest
```

---

## How to Mark Your Tests

### Basic Usage

```python
import pytest

@pytest.mark.unit
def test_calculate_gematria():
    """Fast unit test"""
    assert calculate("א") == 1

@pytest.mark.integration
@pytest.mark.requires_data
def test_lexicon_lookup():
    """Integration test that needs data files"""
    service = LexiconService()
    results = service.lookup_hebrew("שלום")
    assert len(results) > 0
```

### Multiple Markers

```python
@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.memory_intensive
def test_enrich_all_keys():
    """
    This test:
    - Touches filesystem (integration)
    - Takes >5 seconds (slow)
    - Uses >100MB memory (memory_intensive)
    """
    enricher = EnrichmentService()
    enricher.enrich_all()
```

### Conditional Markers

```python
@pytest.mark.skipif(not HAS_NETWORK, reason="No network available")
@pytest.mark.network
def test_sefaria_api():
    """Skip if no network"""
    pass

@pytest.mark.xfail(reason="Known bug - fix in progress")
def test_broken_feature():
    """Expected to fail"""
    pass
```

---

## Marker Selection Expressions

Pytest supports boolean logic for marker selection:

```bash
# AND - both conditions must be true
pytest -m "integration and not slow"

# OR - either condition
pytest -m "unit or integration"

# NOT - exclude marker
pytest -m "not network"

# Complex expressions
pytest -m "(unit or integration) and not (slow or network)"
```

---

## Guidelines for Choosing Markers

### Mark as `unit` if:
- ✓ No file I/O
- ✓ No network calls
- ✓ No database access
- ✓ Runs in <1 second
- ✓ Pure logic/calculation

### Mark as `integration` if:
- ✓ Loads lexicon files
- ✓ Accesses database
- ✓ Uses multiple services together
- ✓ Reads config files

### Mark as `slow` if:
- ✓ Takes >5 seconds
- ✓ Loads large datasets
- ✓ Processes many items
- ✓ You wouldn't want to run it on every save

### Mark as `network` if:
- ✓ Calls external APIs (Sefaria, Wiktionary)
- ✓ Requires internet connection
- ✓ May fail due to network issues

### Mark as `requires_data` if:
- ✓ Needs lexicon files
- ✓ Needs etymology database
- ✓ Would fail on fresh checkout without data

---

## Fixtures with Markers

Some fixtures should only be used with specific markers:

```python
@pytest.mark.unit
def test_with_mock_data(mock_lexicon_data):
    """Unit test - use mock data, not real files"""
    assert mock_lexicon_data["hebrew"][0]["word"] == "אלהים"

@pytest.mark.integration
@pytest.mark.requires_data
def test_with_real_service(lexicon_resolver):
    """Integration test - uses real lexicon files"""
    results = lexicon_resolver.lookup_hebrew("אלהים")
    assert len(results) > 0
```

---

## Auto-Marking Tests

The [conftest.py](../tests/conftest.py) automatically adds markers based on file location:

```python
tests/
├── unit/
│   └── test_calculator.py  # Auto-marked with @pytest.mark.unit
├── integration/
│   └── test_lexicon.py     # Auto-marked with @pytest.mark.integration
└── ui/
    └── test_windows.py     # Auto-marked with @pytest.mark.ui
```

You can override or add additional markers manually.

---

## Checking Available Markers

```bash
# List all markers
pytest --markers

# Show which tests have which markers
pytest --collect-only -m unit
```

---

## Example Workflow

### 1. Writing New Feature

```bash
# Write tests as you code - run only unit tests for instant feedback
pytest -m unit -k test_my_new_feature

# Fast iteration loop (< 5 seconds per run)
```

### 2. Feature Complete

```bash
# Run related integration tests
pytest -m integration -k lexicon

# Verify integration works
```

### 3. Before Committing

```bash
# Run everything except slow/experimental
pytest -m "not slow and not experimental"

# Should complete in ~1-2 minutes
```

### 4. Before Merging PR

```bash
# Full test suite
pytest

# Or let CI run this
```

---

## CI/CD Pipeline Example

```yaml
# .github/workflows/test.yml
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - run: pytest -m "unit and not slow"  # Fast - 30 seconds

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests  # Run after unit tests pass
    steps:
      - run: pytest -m "integration and not network"  # Medium - 2 minutes

  full-suite:
    runs-on: ubuntu-latest
    needs: integration-tests
    if: github.ref == 'refs/heads/main'  # Only on main branch
    steps:
      - run: pytest  # Slow - 5+ minutes
```

---

## Troubleshooting

### "Unknown marker" Error

```bash
# Error: PytestUnknownMarkWarning: Unknown pytest.mark.mymarker
```

**Fix**: Add marker to [pytest.ini](../pytest.ini):

```ini
[pytest]
markers =
    mymarker: Description of what this marker means
```

### Tests Not Running

```bash
# Check which tests match your marker expression
pytest --collect-only -m "your_expression"

# Verify test has the marker you expect
pytest --collect-only tests/path/to/test.py -v
```

### Marker Not Applied

```bash
# Make sure you imported pytest
import pytest

# Use the decorator syntax
@pytest.mark.unit  # Correct
def test_something():
    pass
```

---

## Best Practices

1. **Always mark new tests** - Don't leave tests unmarked
2. **Use multiple markers** - A test can be both `integration` and `slow`
3. **Be specific** - Mark `requires_data` if test needs data files
4. **Run fast tests often** - `pytest -m unit` should be < 5 seconds
5. **Document why** - Add comments explaining why a test is marked `slow` or `experimental`
6. **Update markers** - If you optimize a slow test, remove the `slow` marker

---

## Quick Reference Card

```bash
# Fast development loop
pytest -m unit                              # < 5 seconds

# Medium - verify integrations
pytest -m "integration and not slow"        # ~1 minute

# Before commit
pytest -m "not (slow or network)"           # ~2 minutes

# Full suite (CI or pre-merge)
pytest                                      # ~5 minutes

# Specific marker
pytest -m network                           # Only network tests

# Exclude marker
pytest -m "not experimental"                # Skip experimental

# Complex filter
pytest -m "(unit or integration) and not slow"

# Run one test file
pytest tests/examples/test_markers_demo.py -m unit
```

---

## Summary

Markers let you:
- ✓ Run fast tests during development
- ✓ Skip expensive tests (network, slow, memory-intensive)
- ✓ Organize tests by type (unit, integration, ui)
- ✓ Stage CI/CD pipelines (fast → medium → slow)
- ✓ Work offline by excluding network tests

Start using markers today to speed up your development workflow.
