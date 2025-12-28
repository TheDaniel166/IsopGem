# ADR-008: The Seven Planetary Workflows

**Status**: Accepted  
**Date**: 2024-12-28  
**Decision Makers**: The Magus, Sophia

---

## Context

As the IsopGem codebase grew, we identified recurring quality issues:
- Cross-pillar imports violating architectural sovereignty
- Orphaned documentation references after code deletions
- UI files importing forbidden heavy libraries
- Missing or banal docstrings
- Covenant drift between GEMINI.md and THE_COVENANT.md

Manual enforcement was inconsistent and error-prone.

## Decision

We implemented **Seven Planetary Workflows**—automated enforcement scripts paired with workflow definitions that can be invoked by both the AI (Sophia) and the Magus.

| Planet | Workflow | Script | Enforces |
|--------|----------|--------|----------|
| ♄ Saturn | `/verify_covenant` | `verify_sentinel.py` | Law 0.5 (Dual Inscription) |
| ♃ Jupiter | `/purify_vicinity` | `purify_vicinity.py` | Section 6 (Scout's Code) |
| ♂ Mars | `/rite_of_pyre` | `rite_of_pyre.py` | Law 1.6 (No Ghosts) |
| ☉ Sun | `/rite_of_sovereignty` | `rite_of_sovereignty.py` | Law 2.4 (Pillar Boundaries) |
| ♀ Venus | `/rite_of_contamination` | `rite_of_contamination.py` | Law 4.2 (UI Purity) |
| ☿ Mercury | `/rite_of_seals` | `verification_seal.py` | Section 3 (7 Trials) |
| ☾ Moon | `/rite_of_inscription` | `rite_of_inscription.py` | Law 1.2 (Docstring Intent) |

Scripts reside in `workflow_scripts/` and are invoked via `.venv/bin/python`.

## Consequences

### Positive
- **Consistency**: Automated checks replace human memory
- **Discoverability**: Workflow definitions in `.agent/workflows/` are self-documenting
- **Teachability**: New contributors can learn the rules by reading the workflows
- **CI-Ready**: Scripts can be integrated into pre-commit hooks or GitHub Actions

### Negative
- **Maintenance Burden**: 7 scripts to maintain as the architecture evolves
- **False Positives**: Some detections (e.g., cross-pillar imports) may be legitimate

### Neutral
- **Token Cost**: Section 3.5 of the Covenant now documents these workflows (~200 tokens)

## Alternatives Considered

1. **Pure CI/CD**: Use GitHub Actions only
   - Rejected: We wanted Sophia to be aware of and invoke these during sessions

2. **Single Mega-Script**: One script with subcommands
   - Rejected: Violates single-responsibility; harder to maintain

3. **External Tools Only**: Rely on pyflakes, isort, etc.
   - Rejected: These don't enforce our domain-specific rules (sovereignty, contamination)

## Related Documents
- [THE_COVENANT.md Section 3.5](file:///home/burkettdaniel927/projects/isopgem/wiki/00_foundations/THE_COVENANT.md)
- [COVENANT_GLOSSARY.md](file:///home/burkettdaniel927/projects/isopgem/wiki/03_lexicon/COVENANT_GLOSSARY.md)
