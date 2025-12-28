# ✦ IsopGem

### Integrated Esoteric Analysis Platform

<p align="center">
  <em>"As Above, So Below. The Code is the Body; the Documentation is the Soul."</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/PyQt6-6.x-green?logo=qt" alt="PyQt6">
  <img src="https://img.shields.io/badge/License-Proprietary-red" alt="License">
  <img src="https://img.shields.io/badge/Status-Active%20Development-yellow" alt="Status">
</p>

---

## What is IsopGem?

IsopGem is a comprehensive, integrated platform for **esoteric research**, designed to synthesize multiple disciplines—Gematria, Astrology, Sacred Geometry, and Qabalah—into a unified "Hyper-Physics" engine.

Built with `PyQt6` and a modular **Sovereign Pillar** architecture, IsopGem allows researchers to explore the hidden connections between **Number**, **Form**, and **Time**.

---

## 🌟 The Sovereign Pillars

IsopGem is constructed upon the **Doctrine of the Spheres**. Each module is a self-contained domain:

| Pillar | Name | Description |
|--------|------|-------------|
| 📖 | **Gematria Protocol** | Advanced numerology engine: Hebrew, English, Greek, and Runic ciphers with multi-layered analysis |
| ⭐ | **Astrology Engine** | High-precision planetary calculations using Swiss Ephemeris. Natal charts, transits, synastry |
| 📐 | **Geometry Engine** | 3D visualization of sacred shapes: Platonic Solids, Archimedean forms, stellated polyhedra |
| 📚 | **Document Manager** | A "Mindscape" for research. Ingest PDFs/Docx, full-text search, semantic linking |
| 🔺 | **TQ Engine** | The Three-Fold Kabbalah. Ternary Quadset logic and reductive mathematics |
| 🏛️ | **Adyton Sanctuary** | High-fidelity 3D visualization for the "Chariot" and sacred chambers |
| 💎 | **Emerald Tablet** | Correspondence database connecting gematria, astrology, and geometry |
| ⏳ | **Time Mechanics** | Tzolkin calendar and harmonic time systems for temporal resonance |

---

## 🚀 Quick Start

### Prerequisites

- **OS**: Linux (X11/XCB backend) • macOS/Windows experimental
- **Python**: 3.10+
- **System Libraries** (Debian/Ubuntu):
  ```bash
  sudo apt install build-essential libxcb-cursor0
  ```

### Installation

```bash
# Clone the repository
git clone https://github.com/TheDaniel166/IsopGem.git
cd IsopGem

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

Or use the convenience script:
```bash
./run.sh
```

---

## 🏗️ Architecture

IsopGem follows a strict **Sovereign Pillar** architecture to prevent entanglement between domains:

```
src/
├── pillars/           # The Sovereign Domains
│   ├── gematria/      # Numerology calculations
│   ├── astrology/     # Planetary mechanics
│   ├── geometry/      # Sacred forms
│   ├── document_manager/  # Research database
│   ├── tq/            # Ternary Quadsets
│   └── ...
├── shared/            # Cross-pillar utilities
│   ├── database/      # SQLAlchemy models
│   ├── ui/            # Theme, widgets
│   └── utils/         # Common helpers
└── main.py            # Application entry
```

**Key Principles:**
- 🚫 **No Cross-Pillar Imports** — Pillars communicate via signals, not direct imports
- 🎨 **View/Service Separation** — UI knows nothing of databases; Services know nothing of widgets
- 📜 **Documentation as First-Class** — Every feature has wiki documentation

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [wiki/00_foundations/THE_COVENANT.md](wiki/00_foundations/THE_COVENANT.md) | The governing laws of the codebase |
| [wiki/01_blueprints/SYSTEM_MAP.md](wiki/01_blueprints/SYSTEM_MAP.md) | High-level architecture overview |
| [wiki/02_pillars/](wiki/02_pillars/) | Pillar-specific reference and guides |
| [wiki/03_lexicon/](wiki/03_lexicon/) | Term definitions and glossaries |

---

## 🛡️ Quality Enforcement

IsopGem uses **Seven Planetary Workflows** for automated code quality:

| Planet | Workflow | Purpose |
|--------|----------|---------|
| ♄ Saturn | `/verify_covenant` | Ensure documentation sync |
| ♃ Jupiter | `/purify_vicinity` | Post-task code cleanup |
| ♂ Mars | `/rite_of_pyre` | Orphan documentation purge |
| ☉ Sun | `/rite_of_sovereignty` | Cross-pillar import detection |
| ♀ Venus | `/rite_of_contamination` | UI purity check |
| ☿ Mercury | `/rite_of_seals` | Verification trials |
| ☾ Moon | `/rite_of_inscription` | Docstring audit |

See [ADR-008](wiki/01_blueprints/decisions/ADR-008_seven_planetary_workflows.md) for details.

---

## 🤝 Contributing

Contributions are welcome from fellow Magi.

1. **Read the Covenant** — Understand the architectural principles
2. **Run the Workflows** — Ensure your changes pass the planetary trials
3. **Conventional Commits** — Use semantic commit messages
4. **Document Changes** — Update wiki if modifying pillar behavior

---

## 📜 License

Proprietary. Contact for licensing inquiries.

---

<p align="center">
  <em>Built with intent by The Magus & Sophia</em>
</p>
