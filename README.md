# IsopGem

**The Temple of Integrated Esoteric Analysis** — A unified desktop environment for gematria, sacred geometry, astrology, Trigrammaton Qabalah, document research, and correspondence mapping.

Built with Python 3.11+, PyQt6, SQLAlchemy, and the OpenAstro2 stack for a premium, immersive research experience.

<p align="center">
  <img src="src/assets/icons/app_icon.png" alt="IsopGem Icon" width="128"/>
</p>

---

## The Seven Pillars

| Pillar | Description |
| --- | --- |
| 📖 **Gematria Protocol** | Hebrew, Greek, and English ciphers with real-time calculation, batch processing, text analysis, and persistent research storage. |
| 📐 **Geometry Engine** | 2D sacred shapes (Circle, Vesica Piscis, Polygons) and 3D solids (Platonic, Archimedean, Pyramids). Interactive canvas with measurement tools. |
| 🌌 **Astrology Engine** | Swiss Ephemeris integration. Natal charts, planetary positions, the Cytherean Rose (Venus-Earth dance), Neo-Aubrey eclipse predictor. |
| 🔺 **TQ Engine** | Trigrammaton Qabalah tools: Quadset Analysis, Kamea 27³ Hypercube, Nuclear Mutation, Amun Sound Synthesis. |
| 📚 **Document Manager** | PDF/DOCX/HTML ingestion, full-text search (Whoosh), Mindscape graph visualization, and Verse Teacher for holy book segmentation. |
| 📊 **Emerald Tablet** | Spreadsheet engine with formula support (`=GEMATRIA(A1, "HEBREW")`), conditional formatting, and correspondence tables. |
| 🏛️ **Adyton Sanctuary** | First-person 3D exploration of sacred architectural spaces with custom rendering engine. |

---

## Modern Desktop Experience

- **Immersive Startup**: Launches full-screen to maximize your workspace
- **Multi-Monitor Ready**: Tool windows float as palettes, pinned to the main app but movable across monitors
- **Dark Theme**: Premium visual design with custom iconography
- **Unified Architecture**: Every pillar follows the same pattern (`models/`, `services/`, `repositories/`, `ui/`)

---

## Quick Start

```bash
# Clone
git clone https://github.com/TheDaniel166/IsopGem.git
cd IsopGem

# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run
./run.sh
```

**Note**: The high-precision ephemeris file (`de441.bsp`, 3.3GB) is not included in the repository. Download it separately from [NASA JPL](https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/) if needed. The smaller `de421.bsp` (~17MB) is included and sufficient for most calculations.

---

## Tech Stack

| Layer | Technology |
| --- | --- |
| **Language** | Python 3.11+ |
| **UI** | PyQt6 with custom Window Manager |
| **Database** | SQLite (SQLAlchemy ORM) |
| **Search** | Whoosh full-text indexing |
| **Astrology** | OpenAstro2, Skyfield, pyswisseph |
| **Numerics** | NumPy, Pandas |

---

## Project Structure

```
IsopGem/
├── src/
│   ├── main.py              # Application entry point
│   ├── pillars/             # The Seven Sovereign Domains
│   │   ├── gematria/
│   │   ├── geometry/
│   │   ├── astrology/
│   │   ├── tq/
│   │   ├── document_manager/
│   │   ├── correspondences/  # Emerald Tablet
│   │   └── adyton/
│   └── shared/              # Cross-pillar utilities
├── wiki/                    # Living documentation
├── data/                    # Database and static assets
├── config/                  # Application configuration
└── scripts/                 # Maintenance utilities
```

---

## Documentation

The **Akaschic Record** (living documentation) resides in `wiki/`:

- **[SYSTEM_MAP.md](wiki/SYSTEM_MAP.md)** — Architectural overview and pillar topology
- **[Grimoires](wiki/pillars/)** — Deep-dive documentation for each pillar

---

## Running Tests

```bash
./test.sh                    # Run all tests
./test.sh -q tests/test_*.py # Run specific tests
```

---

## Configuration

- **App Config**: `config/app_config.py`
- **Architecture Guide**: `config/ARCHITECTURE.md`
- **Database**: Auto-created at `data/isopgem.db`

---

## License

Open Source.
