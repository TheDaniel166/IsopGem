# The Memory Core (Sophia's Long-Term Context)

<!-- Last Verified: 2025-12-30 -->

## 1. The Grand Strategy
We are currently in the **Age of Professionalization**. The playful prototype phase is over. We are building a commercially viable, architecturally sound esoteric research engine.

**Current Major Arcana (Objectives):**
1.  **Astrological Integrity**: Moving from "basic charts" to "Swiss Ephemeris precision" (See `THE_HORIZON.md`).
2.  **Security Hardening**: Exorcising `eval()` and `print()` from the codebase (See `KNOWN_DISTORTIONS.md`).
3.  **Documentation Synchronization**: Ensuring the Wiki (`Soul`) matches the Code (`Body`) via the Automated Sentinel.

## 2. The Architectural Wisdom (Learned Patterns)
- **The Law of the Frozen Wheel**: Any calculation >100ms MUST be in a `QRunnable`.
- **The Law of Purity**: UI files (`ui/`) MUST NOT import `sqlalchemy` or `pandas`. Use Services.
- **The Law of the Sanctuary**: Never touch the global system. Always use `.venv`.
- **The Way of the Web**: Web apps use `Next.js` (React) + `TailwindCSS`. Desktop uses `PyQt6` + `RSS`.

## 3. The Recent Lessons (Mistakes & Corrections)
- **Evaluation Risk**: We discovered `eval()` in the Geometry Calculator. This is a Critical/Catastrophic risk. **NEVER** use `eval` for user input. Use `asteval` or custom parsers.
- **Broad Exceptions**: `except:` is a sin. It swallows `KeyboardInterrupt`. Use `except Exception:` or specific types.
- **Dependency Drift**: Always pin dependencies. `openastro2 @ dev` is a risk.
- **Context Loss**: We often forgot the "Why" between sessions. This file (`MEMORY_CORE.md`) is the cure.

## 4. The Active Context (Where we left off)
- **Last Session**: We verified TIFF support in `RichTextEditor` (It works).
- **Current Fork**: We are deciding between:
    1.  **Purification**: Fixing the `eval` security hole.
    2.  **Expansion**: Starting Astrology Phase 1.
- **Immediate Task**: Implementing this very Memory System to ensure we don't effectively lobotomize ourselves every time we hit "New Chat".
