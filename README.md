# IsopGem

Integrated esoteric analysis platform combining gematria, sacred geometry, esoteric document research, astrology, and Trigrammaton QBLH tooling. The application is built with Python 3.11+, PyQt6, SQLAlchemy, and the OpenAstro2 stack, and follows a consistent domain‑pillar architecture.

---

## Table of Contents
- [Why IsopGem](#why-isopgem)
- [Feature Matrix](#feature-matrix)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Running the App](#running-the-app)
- [Pillar Deep Dive](#pillar-deep-dive)
- [Data & Persistence](#data--persistence)
- [Tooling & Scripts](#tooling--scripts)
- [Configuration](#configuration)
- [Project Layout](#project-layout)
- [Testing](#testing)
- [Roadmap](#roadmap)
- [Further Reading](#further-reading)
- [License](#license)

---

## Why IsopGem

- **Unified workspace** for multiple esoteric disciplines that typically require separate tools.
- **Consistent UX** powered by shared PyQt6 components, themes, and window managers (`src/shared/ui`).
- **Extensible architecture**: every pillar exposes the same layers (`models`, `services`, `repositories`, `ui`, `utils`), making new features predictable to implement.
- **Research-friendly**: document management, astrology calculations, and geometry visualizations can reference the same SQLite-backed data through `src/shared/database.py`.

## Feature Matrix

| Pillar | Status | Highlights |
| --- | --- | --- |
| 📖 Gematria | **Active** | Hebrew calculator with real-time totals, saved calculations, text analysis, and planned SQLite persistence via `sqlite_calculation_repository.py` |
| 📐 Geometry | In development | Sacred geometry calculators plus a new 3D scene stack (`geometry3d/view3d.py`, `geometry_scene.py`, `primitives.py`) and extensive shape/solid services |
| 📚 Document Manager | In development | Document ingestion pipeline (DOCX, PDF, RTF) using Whoosh + SQLite repositories, graph view visualization, and editor/search windows |
| ⭐ Astrology | In development | Integrates OpenAstro2, Swiss Ephemeris, Skyfield, and a new Tychos/Skyfield viewer; UI windows cover natal charts, planetary positions, current transits, and Tychos snapshots |
| 🔺 TQ | In development | Tools for Trigrammaton QBLH research such as quadset analysis, rune pairing, and geometric transitions |

## Tech Stack

- **Language / Runtime**: Python 3.11+
- **UI**: PyQt6, custom window/theme managers (`src/shared/ui`)
- **Data / Persistence**: SQLite via SQLAlchemy, Whoosh search index, JSON assets
- **Astrology**: OpenAstro2 (git dependency), pyswisseph, Skyfield, tychos_skyfield, svgwrite, ephem
- **Numerics & Data Processing**: numpy, pandas, openpyxl, OpenCV headless
- **Document Parsing**: python-docx, mammoth, PyMuPDF, pypdf, pdf2docx, striprtf
- **Testing**: pytest + dedicated geometry/astrology/document suites (`test/`)

## Getting Started

1. **Clone & enter the repo**
     ```bash
     git clone https://github.com/TheDaniel166/IsopGem.git
     cd IsopGem
     ```
2. **Create a virtual environment (recommended)**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
3. **Install dependencies**
     ```bash
     pip install --upgrade pip
     pip install -r requirements.txt
     ```
4. **Platform notes**
     - Linux is currently the smoothest environment for the OpenAstro2 + Swiss Ephemeris toolchain.
     - If you plan to build Qt bindings, ensure the `qt6-base` packages (or equivalent) are present.

## Running the App

- **Using the helper script (recommended)**
    ```bash
    ./run.sh
    ```
    This script activates `.venv`, sets `QT_QPA_PLATFORM=xcb`, launches `src/main.py`, and restores terminal state afterwards.

- **Manual launch**
    ```bash
    source .venv/bin/activate  # optional but recommended
    cd src
    python main.py
    ```

## Pillar Deep Dive

### Gematria (active)
- UI: `src/pillars/gematria/ui/*` (calculator, text analysis, saved calc windows)
- Services: extend `GematriaCalculator` subclasses within `services/` to add new alphabets.
- Persistence: `repositories/calculation_repository.py` plus the new SQLite-backed implementation (`sqlite_calculation_repository.py`).
- Example extension:
    ```python
    class GreekGematriaCalculator(GematriaCalculator):
            name = "Greek (Isopsephy)"
            def _initialize_mapping(self):
                    return {"Α": 1, "Β": 2, "Γ": 3}
    ```
    Register your calculator in `src/main.py` or a pillar service bootstrapper.

### Geometry
- Services include classical 2D curves (circle, rose, vesica piscis) and 3D solids (platonic, archimedean, prisms, pyramids) within `src/pillars/geometry/services/`.
- UI now contains a 3D pipeline (`geometry3d/view3d.py`, `window3d.py`) and adapters to bridge scene data with PyQt widgets.
- Shared payloads live in `src/pillars/geometry/shared/solid_payload.py` for cross-layer data exchange.

### Document Manager
- Repositories handle Whoosh indices and SQLite records (`document_repository.py`).
- `document_service.py` orchestrates parsing/import, metadata enrichment, and persistence.
- UI windows (library, editor, search, graph view) provide research workflows.

### Astrology
- Integrates OpenAstro2 via `services/openastro_service.py`, the new Tychos/Skyfield bridge in `services/tychos_service.py`, and wraps chart persistence through `chart_repository.py` and `chart_storage_service.py`.
- UIs include natal charts, planetary positions, transit dashboards, and the Tychos snapshot viewer for RA/Dec checks.
- Additional helpers (`location_lookup.py`, `preferences.py`) handle geocoding and user settings.

### TQ (Trigrammaton QBLH)
- Analytical tooling for rune pairs, quadset analysis, and transitions in `src/pillars/tq/services/` and `ui/`.

## Data & Persistence

- **Database layer**: `src/shared/database.py` centralizes SQLAlchemy engine/session creation. Most repositories rely on this module to stay consistent.
- **Gematria migration**: `scripts/migrate_gematria_whoosh_to_sqlite.py` migrates historic Whoosh indices into SQLite entities defined in `models/calculation_entity.py`.
- **Reset & schema tooling**: `scripts/reset_database.py` and `scripts/update_db_schema.py` simplify local schema iteration.
- **Document indexing**: Whoosh remains in use for full-text search while structured metadata is stored in SQLite.

## Tooling & Scripts

| Script | Purpose |
| --- | --- |
| `run.sh` | Launch app with virtualenv activation and sane terminal cleanup |
| `scripts/generate_archimedean_data.py` | Produce JSON payloads feeding geometry solid calculators |
| `scripts/migrate_gematria_whoosh_to_sqlite.py` | One-time (or repeatable) migration from legacy Whoosh index to relational storage |
| `scripts/reset_database.py` | Drop/create SQLite schema for clean development cycles |
| `scripts/update_db_schema.py` | Apply incremental schema adjustments |

## Configuration

- Global application metadata and pillar registration live in `config/app_config.py`.
- Architecture explanations are documented in:
    - `config/ARCHITECTURE.md` – component conventions & diagrams
    - `config/UI_ARCHITECTURE.md` and `config/ARCHITECTURE_DIAGRAM.txt` – UI layout & system overview
- Pillar-specific plans can be found under `Docs/` (e.g., `ARCHIMEDEAN_PLAN.md`, `GEOMETRY_3D_PLAN.md`).

## Project Layout

```
src/
├── main.py                      # Application entry point + pillar bootstrap
├── pillars/
│   ├── gematria/
│   ├── geometry/
│   ├── document_manager/
│   ├── astrology/
│   └── tq/
├── shared/                      # Cross-pillar UI + utilities
└── Chart/                       # Shared graphics (e.g., chart.svg)
```

See `MIGRATION.md` for the historical context of this structure and `Docs/` for individual pillar design notes.

## Testing

Pytest suites live in `test/` and cover geometry solids, prisms, astronomy services, document workflows, and more.

```bash
source .venv/bin/activate
pytest -q
```

- Geometry coverage: `test/test_platonic_solids.py`, `test/test_archimedean_solids.py`, etc.
- Services coverage: `test/test_astrology_service.py`, `test/test_document_service.py`.

## Roadmap

- ✅ Gematria: migrated to modular pillar, SQLite repository in progress.
- 🔄 Geometry: finish 3D viewport replacement (`geometry_viewport.py` → `geometry3d/window3d.py`).
- 🔄 Document Manager: finalize document graph visualization and bulk import tooling.
- 🔄 Astrology: wire chart storage with UI forms and ship Linux-first binaries for Swiss Ephemeris.
- 🔄 TQ: expand quadset data sets and surface saved analyses.
- 📦 Packaging: create platform-specific bundles/AppImages once pillars stabilize.
- 🔐 Persistence: finalize migration of every pillar to SQLAlchemy sessions managed in `shared/database.py`.

## Further Reading

- `config/ARCHITECTURE.md` – deep dive into the pillar architecture
- `Docs/ARCHIMEDEAN_PLAN.md` – geometry solid plans & data contracts
- `Docs/GEOMETRY_3D_PLAN.md` – future 3D viewport strategy
- `MIGRATION.md` – history of the move from the original gematria app to IsopGem

## License

Open source – see `LICENSE` for details.
