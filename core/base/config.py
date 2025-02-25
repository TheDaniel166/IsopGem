"""
IsopGem Configuration Management
Handles application settings and configuration
"""
from PyQt6.QtCore import QSettings
from typing import Any, Optional
from pathlib import Path


class ConfigManager:
    """
    Manages application configuration and settings
    Uses QSettings for persistent storage
    """
    _instance = None

    def __init__(self):
        if ConfigManager._instance is not None:
            raise RuntimeError("Use get_instance() instead")
        
        self.settings = QSettings("IsopGem", "IsopGem")
        ConfigManager._instance = self
        
        # Create documents directory if it doesn't exist
        docs_dir = self.get_documents_dir()
        docs_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_instance(cls) -> 'ConfigManager':
        """Get the singleton instance of the configuration manager"""
        if cls._instance is None:
            cls._instance = ConfigManager()
        return cls._instance

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self.settings.value(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value"""
        self.settings.setValue(key, value)
        self.settings.sync()

    def remove(self, key: str) -> None:
        """Remove a configuration value"""
        self.settings.remove(key)
        self.settings.sync()

    def clear(self) -> None:
        """Clear all settings"""
        self.settings.clear()
        self.settings.sync()

    def load(self) -> None:
        """Load configuration from storage"""
        # Nothing to do - QSettings loads automatically
        pass

    def get_documents_dir(self) -> Path:
        """Get the documents directory path"""
        default = Path.home() / "IsopGem" / "Documents"
        path_str = self.settings.value("paths/documents", str(default))
        return Path(path_str)
    
    def set_documents_dir(self, path: Path):
        """Set the documents directory path"""
        self.settings.setValue("paths/documents", str(path))
        path.mkdir(parents=True, exist_ok=True)
