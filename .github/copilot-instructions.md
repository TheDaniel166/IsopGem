# Copilot Instructions (IsopGem)

These instructions are the **entrypoint for AI assistance** in this repository.

## Load This First

- Primary AI context: [wiki/00_foundations/AI_QUICK_REFERENCE.md](../wiki/00_foundations/AI_QUICK_REFERENCE.md)
- Canonical rules index: [wiki/00_foundations/THE_COVENANT.md](../wiki/00_foundations/THE_COVENANT.md)

## Default Operating Rules

- Prefer the smallest correct change that fixes the root cause.
- Keep docs aligned with code reality (no stale paths, no invented files).
- Respect Pillar boundaries (no direct inter-pillar imports).
- Keep UI responsive (no heavy work on the main thread).
- When in doubt, ask 1–3 precise clarifying questions.

## Verification

- If you touch Hall 2 docs or references, run: `./.venv/bin/python scripts/verify_manifest.py`
