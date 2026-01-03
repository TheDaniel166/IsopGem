# AI Quick Reference (Foundations)

This page is the **fast-loading entrypoint** for AI agents working in this repository.
It exists to minimize context while maximizing correctness.

## What To Read (In Order)

1. **Primary rules index**: [THE_COVENANT.md](THE_COVENANT.md)
2. **If you are writing or changing code** (usually):
   - Persona / rules of engagement: [covenant/00_persona.md](covenant/00_persona.md)
   - Architecture / Pillars / sovereignty: [covenant/02_spheres.md](covenant/02_spheres.md)
   - Verification / Seals / rituals: [covenant/03_verification.md](covenant/03_verification.md)
3. **If you are changing docs**:
   - Documentation hall structure and intent: [THE_COMPLETE_COVENANT.md](THE_COMPLETE_COVENANT.md)

## What To Load (Minimal)

- Foundations scope + DRY map: [FOUNDATIONS_MAP.md](FOUNDATIONS_MAP.md)

## Non‑Negotiables (Project Constraints)

- **Pillar Sovereignty**: Pillars must not directly import from each other; use shared substrate or signal bus patterns instead.
- **UI Purity**: `ui/` should not import database/network/heavy libs; long work must not block the UI thread.
- **Truth Over Vibes**: Documentation must match code reality; fix drift at the root.
- **No Hidden Rules**: If rules change, update the canonical Covenant scrolls in `wiki/00_foundations/covenant/`.

## “Done” Means Verified

Before calling work complete, run the smallest relevant verification:

- **Doc integrity (Hall 2 / references)**: `./.venv/bin/python scripts/verify_manifest.py`
- **Dual inscription (Covenant sync)**: see [covenant/03_verification.md](covenant/03_verification.md)

## Where Things Live

- **Foundations (rules, setup, standards)**: `wiki/00_foundations/`
- **Blueprints (architecture, ADRs)**: `wiki/01_blueprints/`
- **Grimoires (per-pillar docs)**: `wiki/02_pillars/`
- **Lexicon (glossaries, dictionaries)**: `wiki/03_lexicon/`
- **Prophecies (backlog, known distortions)**: `wiki/04_prophecies/`

## Quick “Which Scroll?” Map

- You are unsure how to behave / present work → [covenant/00_persona.md](covenant/00_persona.md)
- You are unsure where code should live / boundaries → [covenant/02_spheres.md](covenant/02_spheres.md)
- You need the verification rituals / Seals → [covenant/03_verification.md](covenant/03_verification.md)
- You are adding dependencies / changing patterns → [DEPENDENCY_MANIFEST.md](DEPENDENCY_MANIFEST.md)
