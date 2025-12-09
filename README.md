# IsopGem

**Integrated Esoteric Analysis Platform** combining gematria, sacred geometry, esoteric document research, astrology, and Trigrammaton QBLH tooling.

The application is built with Python 3.11+, PyQt6, SQLAlchemy, and the OpenAstro2 stack, designed for a premium, immersive desktop experience.

<p align="center">
  <img src="src/assets/icons/app_icon.png" alt="IsopGem Icon" width="128"/>
</p>

---

## Table of Contents
- [Why IsopGem](#why-isopgem)
- [Modern Desktop Experience](#modern-desktop-experience)
- [Feature Matrix](#feature-matrix)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Running the App](#running-the-app)
- [Pillar Deep Dive](#pillar-deep-dive)
- [Data & Persistence](#data--persistence)
- [Configuration](#configuration)
- [Roadmap](#roadmap)
- [License](#license)

---

## Why IsopGem

- **Unified workspace** for multiple esoteric disciplines that typically require separate tools.
- **Consistent UX** powered by shared PyQt6 components, themes, and window managers.
- **Extensible architecture**: every pillar exposes the same layers (`models`, `services`, `repositories`, `ui`), making new features predictable to implement.
- **Research-friendly**: document management, astrology calculations, and geometry visualizations can reference the same database.

## Modern Desktop Experience

IsopGem is designed for power users and researchers:

- **Immersive Startup**: Launches in full-screen mode to maximize your workspace.
- **Multi-Monitor Ready**: Tools (Calculators, Charts, Viewers) open as **floating palettes**. You can move them to any monitor while they remain "pinned" to the main application, ensuring they never get lost behind other windows.
- **Custom Branding**: Features a unique "Sacred Geometry" visual identity and custom window icons for easy taskbar navigation.

## Feature Matrix

| Pillar | Status | Highlights |
| --- | --- | --- |
| 📖 Gematria | **Active** | Hebrew/Greek/English calculator with real-time totals, stats, saved calculations, and text analysis tools. |
| 📐 Geometry | In development | Sacred geometry calculators (2D/3D), 3D visualization stack (`geometry3d`), and extensive solid/polyhedra database. |
| 📚 Document Manager | In development | Ingestion pipeline (DOCX, PDF, RTF), full-text search (Whoosh), and metadata graph visualization. |
| ⭐ Astrology | In development | Native Swiss Ephemeris integration. Natal charts, planetary positions, transit dashboards. |
| 🔺 TQ | In development | Trigrammaton QBLH research tools: quadset analysis, rune pairing, and geometric transition logic. |

## Tech Stack

- **Language**: Python 3.11+
- **UI Framework**: PyQt6 with custom Window Manager (combining MDI ease with multi-monitor power)
- **Data**: SQLite (SQLAlchemy ORM) + Whoosh (Search Index)
- **Astrology Engine**: OpenAstro2, Skyfield, pyswisseph
- **Processing**: numpy, pandas, cv2

## Getting Started

1. **Clone & enter the repo**
     ```bash
     git clone https://github.com/TheDaniel166/IsopGem.git
     cd IsopGem
     ```
2. **Create a virtual environment**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
3. **Install dependencies**
     ```bash
     pip install --upgrade pip
     pip install -r requirements.txt
     ```

## Running the App

**Recommended Method**:
```bash
./run.sh
```
This script handles virtual environment activation, sets necessary Qt platform flags (`QT_QPA_PLATFORM=xcb` for Linux stability), and launches the application.

**Manual Launch**:
```bash
source .venv/bin/activate
cd src
python main.py
```

## Pillar Deep Dive

### Gematria
- **UI**: Standalone calculators, "Holy Book" teacher mode, methods reference.
- **Data**: SQLite-backed calculation repository for persistent research notes.

### Geometry
- **Engine**: Parametric generation of primitives (Circle, Vesica Piscis) and solids (Platonic, Archimedean).
- **Viz**: Custom 3D viewport widget (`geometry3d`) embedding PyOpenGL/PyQt6 logic.

### Document Manager
- **Indexing**: Hybrid SQLite (metadata) + Whoosh (content) system.
- **Tools**: Library browser, integrated document editor, search dashboard.

### Astrology
- **Core**: Wraps robust astronomy libraries for high-precision celestial data.
- **Features**: Planetary positions table, interactive charts (SVG), location/time management.

## Data & Persistence

- **Database**: `isopgem.db` (SQLite) created automatically in `data/`.
- **Assets**: JSON/Text data stored in `src/data/` for immutable references (star catalogs, number definitions).
- **Maintenance**: Scripts in `scripts/` handle schema updates and database resets.

## Configuration

- **Global Config**: `config/app_config.py`
- **Architecture Docs**:
    - `config/ARCHITECTURE.md`: System design principles.
    - `Docs/`: Detailed plans for each pillar.

## Roadmap

- ✅ **UI Polish**: Full-screen startup, robust Z-ordering, app icons.
- ✅ **Gematria**: Core calculator and persistence.
- 🔄 **Geometry**: Complete 3D viewport integration.
- 🔄 **Document Manager**: Advanced bulk import and graph connections.
- 🔄 **Astrology**: Finalize Chart UI and transit search.
- 📦 **Packaging**: Build platform-specific installers.

## License

Open Source.
