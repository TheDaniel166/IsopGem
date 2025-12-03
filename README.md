# IsopGem

**Integrated Esoteric Analysis Platform**

IsopGem is a comprehensive esoteric analysis platform built with Python and PyQt6, following a domain-pillar architecture with five main pillars of functionality.

## Five Pillars

### 1. 📖 Gematria (Active)
Hebrew, Greek, and English numerical analysis tools
- **Hebrew Gematria**: Standard Hebrew letter values (1-400)
- **Real-time Calculation**: Results update as you type
- **Detailed Breakdown**: See individual letter values
- **Modular Design**: Easy to add Greek and English systems

### 2. 📐 Geometry (Planned)
Sacred geometry visualization and calculation tools

### 3. 📚 Document Manager (Planned)
Analysis and organization of texts and documents

### 4. ⭐ Astrology (Planned)
Cosmic calendar and zodiacal mappings

### 5. 🔺 TQ (Planned)
Trigrammaton QBLH integration and pattern analysis

## Requirements

- Python 3.11+
- PyQt6
- OpenAstro2 stack (pyswisseph, skyfield, svgwrite, numpy, etc.) for the Astrology pillar

> **Platform note:** OpenAstro2 currently ships Swiss Ephemeris binaries that are easiest to configure on modern Linux distributions. macOS and Windows support is planned, but Linux is the primary target for astrology tooling today.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
cd src
python main.py
```

## Architecture

IsopGem follows a domain-pillar architecture where each pillar is organized into consistent components:

```
src/
├── main.py                        # Application entry point
├── pillars/
│   ├── gematria/                  # Gematria pillar
│   │   ├── ui/                    # User interface components
│   │   ├── services/              # Business logic (calculators)
│   │   ├── models/                # Data structures
│   │   ├── repositories/          # Data access
│   │   └── utils/                 # Helper functions
│   ├── geometry/                  # Geometry pillar
│   ├── document_manager/          # Document Manager pillar
│   ├── astrology/                 # Astrology pillar
│   └── tq/                        # TQ pillar
├── shared/                        # Shared components
│   ├── ui/                        # Common UI widgets
│   ├── models/                    # Shared data models
│   └── utils/                     # General utilities
└── config/                        # Configuration files
```

See `config/ARCHITECTURE.md` for detailed architecture documentation.

## Extending the Gematria Pillar

Add new gematria systems by creating a calculator in `src/pillars/gematria/services/`:

```python
from .base_calculator import GematriaCalculator
from typing import Dict

class GreekGematriaCalculator(GematriaCalculator):
    @property
    def name(self) -> str:
        return "Greek (Isopsephy)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        return {
            'Α': 1,
            'Β': 2,
            # ... etc
        }
```

Then add it to the calculators list in `src/main.py`.

## Development

The modular pillar architecture makes it easy to:
- Add new pillars independently
- Extend existing pillars with new features
- Share common functionality across pillars
- Maintain clean separation of concerns

## License

Open source - see LICENSE file for details.
