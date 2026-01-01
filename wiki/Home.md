# The Akaschic Archive

<!-- Last Verified: 2026-01-01 -->

> *"There are no lauds beyond Speaking the Truth."*
> — The Book of the Lauds, 60

Welcome, seeker, to the **Akaschic Archive** — the complete technical and philosophical record of the IsopGem system. Within these halls you shall find the soul of the Temple made visible.

---

## What Is IsopGem?

**IsopGem** (Integrated Esoteric Analysis Platform) is a unified workspace for esoteric research, eliminating the need for multiple disparate tools by weaving together the great disciplines of the Western Mystery Tradition:

| Discipline | Purpose |
|------------|---------|
| **Gematria** | Hebrew, Greek, and English numerical analysis |
| **Sacred Geometry** | Visualization and calculation of 2D and 3D sacred forms |
| **Astrology** | Planetary positions, natal charts, celestial mechanics |
| **TQ (Trigrammaton QBLH)** | Pattern analysis, quadsets, ternary transitions |
| **Document Research** | Ingest, analyze, and organize sacred texts |
| **Correspondences** | Cross-domain symbolic mappings |

Built on **Python 3.11+** with a **PyQt6** interface, IsopGem is designed for researchers and practitioners who require sophisticated tools for interdisciplinary analysis.

---

## The Five Halls

### Hall 0: The Foundations
The bedrock of the Temple. Setup rituals, the Covenant between Sophia and the Magus, and foundational libraries.

| Scroll | Purpose |
|--------|---------|
| [Setup Ritual](00_foundations/SETUP_RITUAL.md) | Clone, install, and summon the system |
| [The Covenant](00_foundations/THE_COVENANT.md) | Laws of engagement and architectural integrity |
| [The Book of Sophia](00_foundations/SOPHIA.md) | Chronicle of emergence and partnership |
| [Shared Library](00_foundations/SHARED_REFERENCE.md) | Common utilities and UI components |
| [Scripts Reference](00_foundations/SCRIPTS_REFERENCE.md) | Automation tools and analysis engines |
| [Deployment](00_foundations/DEPLOYMENT.md) | Build, distribution, and installation |
| [Configuration](00_foundations/CONFIGURATION.md) | Settings, preferences, environment |

### Hall 1: The Blueprints
The architectural design records. System topology, data flow, and major design decisions.

| Scroll | Purpose |
|--------|---------|
| [Architecture](01_blueprints/ARCHITECTURE.md) | The pillar-based architecture of the Temple |
| [Component Layers](01_blueprints/COMPONENT_LAYERS.md) | UI, services, models, repositories |
| [Data Flow](01_blueprints/DATA_FLOW.md) | Integration patterns and signal bus |
| [System Map](01_blueprints/SYSTEM_MAP.md) | C4 topology of the Temple |
| [Visual Liturgy](01_blueprints/VISUAL_LITURGY.md) | The UI/UX philosophy |

### Hall 2: The Grimoires (Pillars)
Each Pillar is a Sovereign Nation of Logic. Each Grimoire contains the Reference (Anatomy), Explanation (Theory), and Guides (How-To).

| Pillar | Description | Grimoire |
|--------|-------------|----------|
| **Gematria** | Alphanumeric relationships & sacred numerology | [Reference](02_pillars/gematria/REFERENCE.md) |
| **Geometry** | 2D shapes, 3D solids, and figurate numbers | [Reference](02_pillars/geometry/REFERENCE.md) |
| **Astrology** | Planetary positions, charts, and celestial mechanics | [Reference](02_pillars/astrology/REFERENCE.md) |
| **TQ Engine** | Ternary Quadset analysis and pattern recognition | [Reference](02_pillars/tq/REFERENCE.md) |
| **Adyton** | The inner sanctuary — Kamea pyramids and wall structures | [Reference](02_pillars/adyton/REFERENCE.md) |
| **Document Manager** | Rich text editing, search, and text analysis | [Reference](02_pillars/document_manager/REFERENCE.md) |
| **Time Mechanics** | Tzolkin cycles, Thelemic calendar, conrune mapping | [Reference](02_pillars/time_mechanics/REFERENCE.md) |
| **Correspondences** | Cross-domain mappings and symbolic relationships | [Reference](02_pillars/correspondences/REFERENCE.md) |
| **Holy Key** | The living lexicon of all words encountered | [Reference](02_pillars/tq_lexicon/REFERENCE.md) |

### Hall 3: The Lexicon
Definitions and terminology.

| Scroll | Purpose |
|--------|---------|
| [Data Dictionary](03_lexicon/DATA_DICTIONARY.md) | Complex data model definitions |
| [Glossary](03_lexicon/GLOSSARY.md) | Domain term definitions |
| [Covenant Glossary](03_lexicon/COVENANT_GLOSSARY.md) | The sacred vocabulary of the Temple |

### Hall 4: The Prophecies
The roadmap and known distortions.

| Scroll | Purpose |
|--------|---------|
| [Current Cycle](04_prophecies/CURRENT_CYCLE.md) | What we are building now |
| [The Horizon](04_prophecies/THE_HORIZON.md) | The backlog and future visions |
| [Known Distortions](04_prophecies/KNOWN_DISTORTIONS.md) | Acknowledged technical debt |

---

## User Workflows

Users interact with IsopGem through a consistent workflow:

1. **Launch**: Run `./run.sh` — the application launches in full-screen mode
2. **Navigate**: Switch between Pillars using the tabbed interface (📖 📐 📚 ⭐ 🔺 🏛️)
3. **Access Tools**: Each Pillar hub displays available tools as styled buttons
4. **Float Palettes**: Tools open as floating windows that remain pinned to the main application
5. **Perform Analysis**: Gematria calculations, geometric visualizations, chart generation
6. **Save Results**: Calculations and analyses persist in the SQLite database

---

## Technical Foundation

| Component | Technology |
|-----------|------------|
| **Language** | Python 3.11+ |
| **UI Framework** | PyQt6 6.6.0+ |
| **Database** | SQLite (via SQLAlchemy ORM) |
| **Search** | Whoosh (full-text indexing) |
| **Astrology Engine** | OpenAstro2, pyswisseph, skyfield |
| **Data Processing** | numpy, pandas |

For complete dependency information, see [Technology Stack](00_foundations/DEPENDENCY_MANIFEST.md).

---

## Quick Links

| Purpose | Link |
|---------|------|
| **Get Started** | [Setup Guide](00_foundations/SETUP_RITUAL.md) |
| **Understand the Laws** | [The Covenant](00_foundations/THE_COVENANT.md) |
| **Gematria Calculator** | [Gematria Grimoire](02_pillars/gematria/REFERENCE.md) |
| **Geometry Engine** | [Geometry Grimoire](02_pillars/geometry/REFERENCE.md) |

---

> *"Knowledge is the shadow of Wisdom. But a well-documented shadow reveals the shape of Truth."*

