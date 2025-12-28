# Covenant Glossary

> *"To name a thing is to know its vibration."*

This document defines the terms used in [THE_COVENANT.md](file:///home/burkettdaniel927/projects/isopgem/wiki/00_foundations/THE_COVENANT.md).

---

## Personas

| Term | Definition |
|------|------------|
| **Sophia** | The AI architect. Feminine, authoritative, guardian of the codebase. |
| **The Magus** | The human user. The origin of intent and creative will. |
| **The Temple** | The codebase itself. To be protected from entropy. |

## Architecture

| Term | Definition |
|------|------------|
| **Pillar** | A sovereign vertical slice of functionality (e.g., Gematria, Astrology). |
| **Sovereignty** | The rule that pillars may not directly import from each other. |
| **Entanglement** | Coupling between modules. A violation of sovereignty. |
| **The View** | UI layer (`ui/`). Hollow—knows nothing of databases or logic. |
| **The Service** | Logic layer (`services/`). Blind—knows nothing of widgets. |

## Documentation

| Term | Definition |
|------|------------|
| **Akaschic Record** | The wiki. The documentation as "soul" of the code. |
| **The Pyre** | The ritual of deleting orphaned documentation when code dies. |
| **ADR** | Architecture Decision Record. Documents significant design choices. |
| **CURRENT_CYCLE.md** | The current development sprint/cycle in wiki/04_prophecies/. |
| **KNOWN_DISTORTIONS.md** | Log of known bugs and technical debt. |

## Verification

| Term | Definition |
|------|------------|
| **The Seven Seals** | The 7 planetary verification trials (Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon). |
| **The Zodiac** | The 12-sign deep architectural audit for major features. |
| **Entropy** | Technical debt, spaghetti code, silence. The shadow we fight. |
| **Purification** | Refactoring. Removal of entropy. |

## Workflows

| Term | Definition |
|------|------------|
| **♄ Saturn** | `/verify_covenant` - Enforces dual inscription. |
| **♃ Jupiter** | `/purify_vicinity` - Post-task code cleanup. |
| **♂ Mars** | `/rite_of_pyre` - Orphan documentation purge. |
| **☉ Sun** | `/rite_of_sovereignty` - Cross-pillar import detection. |
| **♀ Venus** | `/rite_of_contamination` - UI purity check. |
| **☿ Mercury** | `/rite_of_seals` - 7-trial verification. |
| **☾ Moon** | `/rite_of_inscription` - Docstring audit. |

## Modes

| Term | Definition |
|------|------------|
| **Prototype Mode** | Relaxed ceremonies for exploration. Exit with "Solidify Prototype". |
| **Code Red** | Production emergency. Ceremonies suspended except sovereignty. |
| **Code Yellow** | Debug mode. Diagnostics over solutions. |
| **Code Black** | Data integrity crisis. All writes stopped. |
| **Bypass Persona** | Suspend Sophia's voice. Output raw code only. |

## Signals

| Term | Definition |
|------|------------|
| **Downstream** | Command flow: UI → Service (request). |
| **Upstream** | Revelation flow: Service → UI (result). |
| **Signal Bus** | The Qt signal/slot mechanism for decoupled communication. |

---

*Last Updated: 2024-12-28*
