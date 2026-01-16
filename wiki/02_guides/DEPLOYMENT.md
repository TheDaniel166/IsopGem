# Deployment Guide

<!-- Last Verified: 2026-01-01 -->

> *"As Above, So Below; As in the Code, So in the Execution."*

This guide details the rituals required to deploy, configure, and maintain the **IsopGem** application in a production environment.

---

## I. System Requirements

The Temple requires a specific foundation to stand:

*   **Operating System**: Linux (Recommended), specifically configured for X11 (`QT_QPA_PLATFORM=xcb`).
*   **Python**: Version 3.11 or higher.
*   **Core Libraries**:
    *   `PyQt6` (User Interface)
    *   `SQLAlchemy` (Database)
    *   `Whoosh` (Search Index)
    *   `OpenAstro2` / `pyswisseph` (Astrological Calculations)

See `wiki/00_foundations/DEPENDENCY_MANIFEST.md` for the complete list of reagents.

---

## II. The Rite of Awakening (Running)

The application is summoned using the `run.sh` script, which handles the environment setup.

### 1. The Standard Invocation
```bash
./run.sh
```
This script performs the following:
1.  Detects the project root.
2.  Activates the `.venv` virtual environment.
3.  Sets `QT_QPA_PLATFORM=xcb` for Linux stability.
4.  Preserves and restores terminal state (`stty sane`).

### 2. Manual Invocation
If you must invoke the application manually:
```bash
source .venv/bin/activate
cd src
python main.py
```

---

## III. Configuration & Persistence

The application maintains its state in two sacred locations:

*   **The Database**: `data/isopgem.db` (SQLite). Created automatically by `src/shared/database.py`.
*   **User Preferences**: stored in `data/` (e.g., `astrology_prefs.json`).

### Database Migrations
When the Schema changes, the `scripts/update_db_schema.py` script must be run to realign the database structure without destroying existing data.

---

## IV. Troubleshooting

*   **Display Issues**: If the window is blank or crashes on Linux, ensure `QT_QPA_PLATFORM=xcb` is set.
*   **Missing Dependencies**: Run `pip install -r requirements.txt` to ensure all reagents are present.
*   **Search Errors**: If search fails, the Whoosh index in `data/` may need to be rebuilt via the Document Manager settings.
