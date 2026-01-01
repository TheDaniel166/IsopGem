# Development Guide

<!-- Last Verified: 2026-01-01 -->

> *"The Code is the Temple; Maintain its Purity."*

This guide outlines the protocols for contributing to, testing, and extending the **IsopGem** codebase.

---

## I. The Development Environment

To enter the sanctum of development:

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/TheDaniel166/IsopGem.git
    ```
2.  **Create the Virtual Environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  **Install Reagents**:
    ```bash
    pip install -r requirements.txt
    ```

---

## II. The Architecture of Pillars

The project follows a **Domain-Pillar** architecture. Each major domain (Gematria, Geometry, etc.) is a "Pillar" with a consistent internal structure:

```
src/pillars/<name>/
├── ui/              # The Face (PyQt6 Widgets)
├── services/        # The Will (Business Logic)
├── models/          # The Form (Data Structures)
├── repositories/    # The Memory (Data Access)
└── utils/           # The Tools (Helpers)
```

**Rule**: Cross-pillar imports should be minimized. Use `src/shared/` for common functionality.

---

## III. Contribution Protocols

1.  **Branching**: Create feature branches (`feature/geometry-fix`) from `main`.
2.  **Linting**: Ensure code follows PEP 8.
3.  **Testing**:
    *   Tests live in `test/`.
    *   Run tests with `pytest`.
    *   Ensure new features have accompanying tests.

---

## IV. Extending the System

### Adding a New Calculator
Inherit from `GematriaCalculator` in `src/pillars/gematria/services/base_calculator.py`. Implement the `_initialize_mapping` method.

### Adding a New Pillar
1.  Create the directory structure in `src/pillars/`.
2.  Register the pillar in `src/main.py`.
3.  Add configuration in `config/app_config.py`.

> *"Build upon the foundation, but do not crack the stone."*
