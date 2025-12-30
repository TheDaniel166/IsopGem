# IsopGem Codebase Audit Report

Date: 2025-12-15

This report is based on a repository scan (docs + static analysis searches + spot-check reads of high-risk files). I attempted to run tests, but the initial `pytest` invocation failed because `pytest` wasn’t on PATH; the correct venv invocation was started but cancelled, so this report does **not** include verified test outcomes.

## Executive Summary

IsopGem has a clear, scalable **pillar architecture** and a consistent UI workflow (Hub-and-Spoke + WindowManager). The project is ambitious and already contains substantial implementations beyond what the top-level docs label as “planned” (e.g., Adyton and Correspondences pillars are present and wired into `src/main.py`).

Top risks found:

- **Expression evaluation (`eval`) reachable from UI** (geometry calculator) and from scripts that fetch and parse remote content.
- **Broad exception handling** (`except:` / `except Exception:`) in multiple pillars, which can hide data corruption and make debugging difficult.
- **Logging/print noise and debug statements** scattered through UI, risking performance regressions and leaking internal data to stdout.
- **Dependency + packaging gaps**: no `pyproject.toml`/`pytest.ini` discovered in repo root; dependency installation and test execution are likely inconsistent across environments.

## Scope & Method

**What I reviewed**

- Docs: `README.md`, `MIGRATION.md`, `config/ARCHITECTURE.md`, `config/UI_ARCHITECTURE.md`.
- **Linux Window Management (Wayland/X11)**
  - **Issue:** Transient Windows (`setTransientParent`) are often forcefully locked to the same monitor as the Parent by the OS compositor.
  - **Issue:** "Free" Windows (No Parent) can be completely obscured if the Main Window is Maximized, as Compositors often treat Maximized windows as a dedicated layer.
  - **Workaround:** We implemented a "Gravity Toggle" (Anchor/Sail) to let users choose between parenting (Locked) and independence (Free). We also default to non-maximized launch to encourage better z-order behavior.
  - **Status:** **Accepted**. This is an OS-level constraint we cannot code around without violating standard window protocols.
- Entry points: `src/main.py`, `run.sh`, assorted scripts.
- Static searches across codebase for:
  - dangerous functions (`eval`, `exec`, `subprocess`, `shell=True`, etc.)
  - secrets (`token`, `api_key`, key blocks)
  - broad exception catches
  - debug prints / logging config

**What I did not verify**

- Full runtime behavior (GUI launch, workflows) and test results (test run cancelled).

## Repository Overview

- **Main app entry**: `src/main.py`
- **Launcher**: `run.sh` (activates `.venv`, exports `QT_QPA_PLATFORM=xcb`, launches `src/main.py`)
- **Architecture**: pillar-based (`src/pillars/*`) + shared components (`src/shared/*`)
- **DB**: SQLite via SQLAlchemy in `src/shared/database.py`, DB stored under `data/isopgem.db`

### Architecture Alignment Notes

- `config/app_config.py` lists only 5 pillars, but `src/main.py` also adds:
  - `pillars.adyton.ui.AdytonHub`
  - `pillars.correspondences.ui.CorrespondenceHub`

This is not inherently wrong, but it is a “docs drift” risk: the config and docs imply one thing; the application wiring implies another.

## Findings (Prioritized)

Severity scale:
- **Critical**: user-triggerable vulnerability / data loss
- **High**: likely failure or serious security footgun
- **Medium**: correctness/reliability issues likely over time
- **Low**: polish/maintainability

### 1) `eval()` in UI expression evaluation (False Positive / Secured)

**Where**
- `src/pillars/geometry/ui/advanced_scientific_calculator_window.py`

**Status**
- **VERIFIED SAFE**: Analysis confirms `_safe_eval` uses `ast.parse` with a strict manual node walker. It does *not* use `eval()` on the raw string.
- **Verification**: `tests/rituals/rite_of_calculator_security.py` passes all injection attempts.

### 2) `eval()` used in a network-fetching script (Fixed/Secured)

**Where**
- `scripts/generate_archimedean_data.py`

**Status**
- **SECURED**: The script has been restored but purified. The `_eval` function now uses `ast.parse` and a strict whitelist of math operators. It no longer accepts arbitrary code execution.
- **Verification**: Code inspection of `scripts/generate_archimedean_data.py`.

### 3) Subprocess usage to open browsers (Medium)

**Where**
- `src/pillars/astrology/ui/natal_chart_window.py`
  - uses `subprocess.Popen([... chrome_path, ..., svg_path])`

**Notes**
- This is safer than `shell=True` (not found in the scanned code), because args are passed as a list.
- Still consider:
  - validating `svg_path` exists
  - using `webbrowser.open()` consistently (you already have fallback)

### 4) Broad exception handling (High for reliability)

**Where (examples)**
- `src/pillars/gematria/services/text_analysis_service.py` uses `except:` multiple times.
- Many files match patterns `except:` or `except Exception:`.

**Why it matters**
- `except:` catches `KeyboardInterrupt`/`SystemExit` too.
- Swallowing exceptions can create silent failures (incorrect totals, missing parsed results, corrupt DB writes not surfaced).

**Recommendation**
- Replace `except:` with specific exceptions (e.g., `ValueError`, `KeyError`, parsing exceptions).
- For “best-effort” workflows, at least log a warning at a rate-limited level.

### 5) Debug prints in production paths (Medium)

**Where**
- Many occurrences of `print(...)` and `[DEBUG]` strings in UI modules:
  - `src/pillars/geometry/ui/geometry_scene.py`
  - `src/pillars/geometry/ui/polygonal_number_window.py`
  - `src/pillars/correspondences/ui/spreadsheet_window.py`
  - `src/pillars/document_manager/ui/mindscape_window.py`
  - `src/pillars/tq/ui/ternary_sound_widget.py`
  - etc.

**Why it matters**
- Can slow down UI interactions (lots of prints during mouse events).
- Makes logs noisy and harder to debug real issues.

**Recommendation**
- Convert to `logging.getLogger(__name__)`.
- Gate debug logs behind a config flag or environment variable.

### 6) Config/doc drift and “enabled” flags not enforced (Low → Medium)

**Where**
- `config/app_config.py` includes `enabled` flags, but `src/main.py` initializes all tabs regardless.

**Why it matters**
- Confusing for future contributors and releases.

**Recommendation**
- Decide whether `config/app_config.py` is authoritative.
  - If yes: build tabs dynamically from `PILLARS`.
  - If no: update docs/config to reflect reality.

### 7) Testing & tooling gaps (Medium)

**Observations**
- There are tests under both `test/` and `tests/`, plus `experiments/` with test-like scripts.
- No repo-level `pytest.ini`, `pyproject.toml`, or `setup.cfg` detected in root (search results were dominated by `.venv`).

**Why it matters**
- Test discovery and execution can be inconsistent.

**Recommendation**
- Add one canonical configuration:
  - `pyproject.toml` with `[tool.pytest.ini_options]`
  - define testpaths, markers, and ignore `experiments/` if desired

### 8) Dependency risks (Medium)

**Where**
- `requirements.txt` includes:
  - `openastro2 @ git+https://github.com/dimmastro/openastro2.git@dev` (unpinned dev branch)

**Why it matters**
- Builds become non-reproducible; upstream changes can break you.

**Recommendation**
- Pin to a specific commit SHA (or tag) rather than `@dev`.

## Positive Notes / Strengths

- **Clear UI workflow design** documented in `config/UI_ARCHITECTURE.md`.
- **WindowManager pattern** is a good fit for multi-tool desktop workflows.
- **Database path handling** in `src/shared/database.py` correctly avoids CWD issues by anchoring to repo root.
- The codebase is already structured in a way that supports future separation into installable packages.

## Recommended Roadmap (Practical)

### Phase 0 (Immediate: 1–2 hours)
- Replace `except:` with specific exceptions in the most important service layers.
- Convert noisy `print` statements in hot UI paths (mouse events) to logging.

### Phase 1 (Security hardening: 0.5–1 day)
- Remove/replace UI `eval` with AST-based safe evaluator.
- Remove/replace `eval` in `scripts/generate_archimedean_data.py` with a safe math expression parser.

### Phase 2 (Tooling + CI: 0.5–1 day)
- Add `pyproject.toml` (pytest config + formatting tools).
- Standardize tests under one folder or configure pytest testpaths.

### Phase 3 (Packaging: later)
- Introduce a `src/isopgem/` package layout (or keep `src/` but make it installable).
- Split optional pillars into extras dependencies.

## How to Run Tests (Current Workspace)

Because the environment is using a venv at `.venv`, prefer running pytest via the venv interpreter:

```bash
cd /home/burkettdaniel927/projects/isopgem
/home/burkettdaniel927/projects/isopgem/.venv/bin/python -m pytest -q
```

If you don’t have the venv created yet:

```bash
cd /home/burkettdaniel927/projects/isopgem
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
```

## Appendix: High-Risk Spots (File List)

- `src/pillars/geometry/ui/advanced_scientific_calculator_window.py` (UI `eval`)
- `scripts/generate_archimedean_data.py` (remote fetch + `eval`)
- `src/pillars/gematria/services/text_analysis_service.py` (broad `except:`)


---

If you want, I can follow this report by actually implementing the top two fixes (replacing `eval` safely) and adding a minimal `pyproject.toml` pytest config—keeping changes small and targeted.
---

## Fixed/Exorcised
- **2025-12-29**: `src/shared/services/document_manager/utils/parsers.py` - Purified.
    - **Distortion**: Broad `except:` clauses swallowing interrupts; debug `print` noise; inadequate list/table parsing.
    - **The Fix**: Replaced with `except Exception`, removed prints, implemented recursive table extraction and `numbering.xml` list parsing.
    - **The Test**: `tests/verify_fixes.py` (Pass).
