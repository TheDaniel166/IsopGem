"""
⚠️  GRANDFATHERED VIOLATION - Pre-existing before Law of Substrate (2026-01-13)

SHARED JUSTIFICATION:
- RATIONALE: GRANDFATHERED - Needs manual review
- USED BY: Geometry (2 references)
- CRITERION: Unknown - requires categorization

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md
"""

"""
Centralized path management for IsopGem.

This module handles resource resolution for both development environments
(running from source) and frozen environments (running as a PyInstaller executable).
It abstracts away the complexity of `sys._MEIPASS` and relative path calculations.
"""


import sys
import os
from pathlib import Path

def is_frozen() -> bool:
    """Check if the application is running in a frozen (packaged) state."""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def get_app_root() -> Path:
    """
    Get the application root directory.
    
    In development: The 'src' directory.
    In frozen state: The temporary directory where the app is unpacked (_MEIPASS).
    """
    if is_frozen():
        return Path(sys._MEIPASS)
    
    # In dev, this file is in src/shared/paths.py
    # So we go up two levels to get to src/
    return Path(__file__).resolve().parent.parent

def get_project_root() -> Path:
    """
    Get the project root directory.
    
    In development: The directory containing 'src', 'data', 'config', etc.
    In frozen state: This concept is ambiguous, as assets are usually bundled into _MEIPASS.
                     However, for external user data, we might look elsewhere.
                     For bundled read-only assets, this falls back to App Root.
    """
    if is_frozen():
        return get_app_root()
        
    return get_app_root().parent

def get_resource_path(relative_path: str) -> str:
    """
    Get the absolute path to a resource file.
    
    Args:
        relative_path: Path relative to the app root (e.g. "assets/icons/icon.png")
        
    Returns:
        Absolute path as a string.
    """
    root = get_app_root()
    path = root / relative_path
    return str(path)

def get_data_path(filename: str = "") -> Path:
    """
    Get the path for data files (like the database).
    
    In development: PROJECT_ROOT/data
    In frozen: user's data directory or local application data (depends on strategy).
               For now, we will default to a 'data' folder next to the executable
               if we want persistence, OR bundled data if read-only.
               
               Current strategy for DB: Use local 'data' folder relative to CWD in dev,
               or next to executable in prod.
    """
    if is_frozen():
        # Use directory where executable is located
        base_dir = Path(sys.executable).parent
    else:
        # Use project root data dir
        base_dir = get_project_root()
        
    data_dir = base_dir / "data"
    data_dir.mkdir(exist_ok=True)
    
    if filename:
        return data_dir / filename
    return data_dir

def get_ephemeris_path(filename: str) -> str:
    """
    Locate an ephemeris file.
    
    Checks:
    1. Bundled resources (frozen)
    2. 'data' directory in project root (dev)
    3. 'data' directory next to executable (prod external)
    """
    # 1. Check bundled/frozen path or src relative path
    # If we bundled it into the exe, it will be here
    bundled_path = get_app_root() / "assets" / "ephemeris" / filename
    if bundled_path.exists():
        return str(bundled_path)
        
    # 2. Check standard data directory
    data_path = get_data_path(filename)
    if data_path.exists():
        return str(data_path)
        
    # 3. Fallback check for dev environment direct relative path often used in scripts
    # Check project_root directly (some scripts incorrectly look there)
    project_root_file = get_project_root() / filename
    if project_root_file.exists():
        return str(project_root_file)

    return str(data_path) # Return standard location even if missing (for download)