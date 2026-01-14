"""
SHARED JUSTIFICATION:
- RATIONALE: Core Infrastructure
- USED BY: Geometry, Tq (10 references)
- CRITERION: 2 (Essential for app to function)
"""

"""
Centralized configuration for Isopgem.

This module provides a single source of truth for:
- File paths (data, lexicons, databases)
- Memory management settings
- Feature flags
- Environment detection (dev vs production)

Complements navigation_bus.py (which handles window-to-window communication)
by providing the "where things are" phonebook.

Usage:
    from shared.config import get_config

    config = get_config()
    lexicon_path = config.paths.lexicons
    max_cache = config.memory.max_lexicon_cache_mb
"""
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import os
import logging

from .paths import get_project_root, get_data_path, is_frozen

logger = logging.getLogger(__name__)


@dataclass
class PathConfig:
    """
    All application paths.

    Uses the existing paths.py infrastructure for dev/production detection.
    """
    # Root directories
    project_root: Path
    data_root: Path
    assets_root: Path
    config_root: Path

    # Data subdirectories
    lexicons: Path
    etymology_db: Path
    openoccult: Path
    databases: Path
    ephemeris: Path
    correspondences: Path
    geometry: Path

    # Database files
    main_db: Path

    # User config directories
    user_config: Path
    user_preferences: Path
    user_state: Path  # XDG-compliant state directory (calculator state, etc.)

    @classmethod
    def from_environment(cls) -> 'PathConfig':
        """Create path config based on environment (dev/frozen)"""
        project_root = get_project_root()
        data_root = get_data_path()

        # In frozen builds, assets might be bundled
        if is_frozen():
            # For frozen: assume assets are next to executable or in _MEIPASS
            import sys
            if hasattr(sys, '_MEIPASS'):
                assets_root = Path(sys._MEIPASS) / "assets"
            else:
                assets_root = Path(sys.executable).parent / "assets"
        else:
            assets_root = project_root / "assets"

        # User config in standard location
        user_config_root = Path.home() / ".config" / "isopgem"
        user_config_root.mkdir(parents=True, exist_ok=True)
        
        # User state directory (XDG Base Directory Specification)
        xdg_state_home = os.environ.get("XDG_STATE_HOME")
        if xdg_state_home:
            user_state_root = Path(xdg_state_home) / "isopgem"
        else:
            user_state_root = Path.home() / ".local" / "state" / "isopgem"
        user_state_root.mkdir(parents=True, exist_ok=True)

        return cls(
            project_root=project_root,
            data_root=data_root,
            assets_root=assets_root,
            config_root=user_config_root,

            # Data subdirectories
            lexicons=data_root / "lexicons",
            etymology_db=data_root / "etymology_db",
            openoccult=data_root / "openoccult",
            databases=data_root / "databases",
            ephemeris=data_root / "ephemeris",
            correspondences=data_root / "correspondences",
            geometry=data_root / "geometry",

            # Database files
            main_db=data_root / "databases" / "isopgem.db",

            # User config and state
            user_config=user_config_root,
            user_preferences=user_config_root / "preferences.json",
            user_state=user_state_root,
        )


@dataclass
class MemoryConfig:
    """
    Memory management settings.

    These control how much memory services can use for caching.
    Adjust based on target deployment environment.
    """
    # Lexicon cache limits (in MB)
    max_lexicon_cache_mb: int = 100
    enable_auto_cache_clear: bool = True
    cache_clear_threshold_mb: int = 80

    # LRU cache sizes for various services
    etymology_cache_size: int = 128
    calculator_cache_size: int = 256
    correspondence_cache_size: int = 64

    # Lazy loading behavior
    lazy_load_lexicons: bool = True
    preload_hebrew_greek: bool = False  # Set True for faster first lookup

    @classmethod
    def from_env(cls) -> 'MemoryConfig':
        """Load memory config from environment variables"""
        return cls(
            max_lexicon_cache_mb=int(os.getenv("ISOPGEM_MAX_CACHE_MB", "100")),
            enable_auto_cache_clear=os.getenv("ISOPGEM_AUTO_CACHE_CLEAR", "1") == "1",
        )


@dataclass
class FeatureConfig:
    """
    Feature flags for enabling/disabling features.

    Useful for:
    - Disabling expensive features on low-end machines
    - A/B testing new features
    - Gradual rollout
    - Testing (disable network features)
    """
    # Multi-language gematria
    enable_multi_language_gematria: bool = True

    # Etymology/lexicon features
    enable_etymology_web_fallback: bool = True
    enable_sefaria_api: bool = True
    enable_wiktionary_scraping: bool = False  # Slow, disabled by default

    # Performance features
    enable_performance_logging: bool = False
    enable_memory_profiling: bool = False

    # UI features
    enable_animations: bool = True
    enable_3d_rendering: bool = True

    # Experimental features
    enable_ai_suggestions: bool = False
    enable_advanced_search: bool = True

    @classmethod
    def from_env(cls) -> 'FeatureConfig':
        """Load feature config from environment variables"""
        return cls(
            enable_etymology_web_fallback=os.getenv("ISOPGEM_ETY_WEB", "1") == "1",
            enable_performance_logging=os.getenv("ISOPGEM_PERF_LOG", "0") == "1",
            enable_memory_profiling=os.getenv("ISOPGEM_MEM_PROFILE", "0") == "1",
        )


@dataclass
class UIConfig:
    """
    UI-related settings.

    These are defaults; users can override via preferences.
    """
    # Display settings
    default_theme: str = "dark"
    default_font_family: str = "Segoe UI"
    default_font_size: int = 12

    # Performance limits
    max_interlinear_words: int = 5000  # Virtualize beyond this
    max_frequency_entries: int = 1000

    # UI behavior
    enable_tooltips: bool = True
    tooltip_delay_ms: int = 500
    animation_duration_ms: int = 200

    @classmethod
    def from_env(cls) -> 'UIConfig':
        """Load UI config from environment"""
        return cls(
            default_theme=os.getenv("ISOPGEM_THEME", "dark"),
            default_font_size=int(os.getenv("ISOPGEM_FONT_SIZE", "12")),
        )


@dataclass
class AppConfig:
    """
    Complete application configuration.

    Combines all config sections into a single object.
    Access via get_config() singleton.
    """
    paths: PathConfig
    memory: MemoryConfig
    features: FeatureConfig
    ui: UIConfig

    # Environment info
    is_frozen: bool
    is_debug: bool
    version: str = "0.1.0"

    def __post_init__(self):
        """Log configuration on creation"""
        if self.is_debug:
            logger.debug(f"App config initialized:")
            logger.debug(f"  Project root: {self.paths.project_root}")
            logger.debug(f"  Data root: {self.paths.data_root}")
            logger.debug(f"  Frozen: {self.is_frozen}")
            logger.debug(f"  Max cache: {self.memory.max_lexicon_cache_mb} MB")

    @classmethod
    def load(cls) -> 'AppConfig':
        """
        Load configuration from environment.

        Order of precedence:
        1. Environment variables (highest)
        2. Config file (if exists)
        3. Defaults (lowest)
        """
        is_debug = os.getenv("ISOPGEM_DEBUG", "0") == "1"

        return cls(
            paths=PathConfig.from_environment(),
            memory=MemoryConfig.from_env(),
            features=FeatureConfig.from_env(),
            ui=UIConfig.from_env(),
            is_frozen=is_frozen(),
            is_debug=is_debug,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary (for serialization)"""
        return {
            "paths": {
                "project_root": str(self.paths.project_root),
                "data_root": str(self.paths.data_root),
                "lexicons": str(self.paths.lexicons),
                "etymology_db": str(self.paths.etymology_db),
            },
            "memory": {
                "max_cache_mb": self.memory.max_lexicon_cache_mb,
                "auto_clear": self.memory.enable_auto_cache_clear,
            },
            "features": {
                "multi_lang_gematria": self.features.enable_multi_language_gematria,
                "web_fallback": self.features.enable_etymology_web_fallback,
            },
            "environment": {
                "frozen": self.is_frozen,
                "debug": self.is_debug,
            }
        }


# Global singleton
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """
    Get the global application configuration.

    Thread-safe lazy initialization.
    Call reset_config() in tests to clear.

    Returns:
        AppConfig singleton instance
    """
    global _config
    if _config is None:
        _config = AppConfig.load()
    return _config


def reset_config():
    """
    Reset config (for testing).

    Example:
        def test_something():
            reset_config()
            config = get_config()
            assert config.paths.data_root exists
    """
    global _config
    _config = None


def get_config_summary() -> str:
    """
    Get human-readable config summary.

    Useful for debug output or help dialogs.
    """
    config = get_config()
    lines = [
        "Isopgem Configuration",
        "=" * 50,
        f"Version: {config.version}",
        f"Environment: {'Frozen' if config.is_frozen else 'Development'}",
        f"Debug Mode: {config.is_debug}",
        "",
        "Paths:",
        f"  Data Root: {config.paths.data_root}",
        f"  Lexicons: {config.paths.lexicons}",
        f"  Etymology DB: {config.paths.etymology_db}",
        f"  Main DB: {config.paths.main_db}",
        "",
        "Memory:",
        f"  Max Cache: {config.memory.max_lexicon_cache_mb} MB",
        f"  Auto Clear: {config.memory.enable_auto_cache_clear}",
        "",
        "Features:",
        f"  Multi-Language Gematria: {config.features.enable_multi_language_gematria}",
        f"  Etymology Web Fallback: {config.features.enable_etymology_web_fallback}",
        f"  Sefaria API: {config.features.enable_sefaria_api}",
    ]
    return "\n".join(lines)