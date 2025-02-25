"""
IsopGem Application Singleton
Manages the core application state and initialization
"""
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal
import sys


class IsopGemApp(QApplication):
    """
    Main application singleton class for IsopGem
    Handles core application functionality
    """
    instance = None
    initialized = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if IsopGemApp.instance is not None:
            raise RuntimeError("Only one instance of IsopGemApp can exist!")
        
        IsopGemApp.instance = self

    @classmethod
    def get_instance(cls):
        """Get the singleton instance of the application"""
        if cls.instance is None:
            raise RuntimeError("IsopGemApp has not been initialized!")
        return cls.instance
