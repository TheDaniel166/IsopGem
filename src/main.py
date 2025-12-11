"""Main entry point for the IsopGem application."""
import sys
import os
import signal
import logging

# Force Qt to use X11 instead of Wayland (more stable with PyQt6)
os.environ['QT_QPA_PLATFORM'] = 'xcb'

# Suppress Qt Wayland warnings if desired
# os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'

from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QCloseEvent, QIcon
from shared.ui import WindowManager, get_app_stylesheet
from shared.database import init_db
from pillars.gematria.ui import GematriaHub
from pillars.geometry.ui import GeometryHub
from pillars.document_manager.ui import DocumentManagerHub
from pillars.astrology.ui import AstrologyHub
from pillars.tq.ui import TQHub
from pillars.adyton.ui import AdytonHub


class IsopGemMainWindow(QMainWindow):
    """Main window for IsopGem application."""
    
    def __init__(self):
        """Initialize the main window with all pillar tabs."""
        super().__init__()
        self.setWindowTitle("IsopGem - Integrated Esoteric Analysis Platform")
        self.setMinimumSize(1100, 750)
        
        # Set app icon
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icons", "app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f9fafb;
            }
        """)
        
        # Ensure this window WILL close the app when closed
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, True)
        
        # Create centralized window manager
        self.window_manager = WindowManager(self)
        
        # Create tab widget for pillars
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Initialize pillars
        self._init_gematria_pillar()
        self._init_geometry_pillar()
        self._init_document_manager_pillar()
        self._init_astrology_pillar()
        self._init_tq_pillar()
        self._init_adyton_pillar()
        
        # Connect tab change to raise all tool windows
        self.tabs.currentChanged.connect(self.window_manager.raise_all_windows)
    
    def changeEvent(self, event):
        """Handle window state changes."""
        if event.type() == QEvent.Type.ActivationChange:
            if self.isActiveWindow():
                self.window_manager.raise_all_windows()
        super().changeEvent(event)

    def _init_gematria_pillar(self):
        """Initialize the Gematria pillar."""
        gematria_hub = GematriaHub(self.window_manager)
        self.tabs.addTab(gematria_hub, "📖 Gematria")
    
    def _init_geometry_pillar(self):
        """Initialize the Geometry pillar."""
        geometry_hub = GeometryHub(self.window_manager)
        self.tabs.addTab(geometry_hub, "📐 Geometry")
    
    def _init_document_manager_pillar(self):
        """Initialize the Document Manager pillar."""
        document_hub = DocumentManagerHub(self.window_manager)
        self.tabs.addTab(document_hub, "📚 Documents")
    
    def _init_astrology_pillar(self):
        """Initialize the Astrology pillar."""
        astrology_hub = AstrologyHub(self.window_manager)
        self.tabs.addTab(astrology_hub, "⭐ Astrology")
    
    def _init_tq_pillar(self):
        """Initialize the TQ pillar."""
        tq_hub = TQHub(self.window_manager)
        self.tabs.addTab(tq_hub, "🔺 TQ")

    def _init_adyton_pillar(self):
        """Initialize the Adyton pillar."""
        adyton_hub = AdytonHub(self.window_manager)
        self.tabs.addTab(adyton_hub, "🏛️ Adyton")
    
    def closeEvent(self, a0: QCloseEvent | None):
        """Handle main window close event."""
        # Close all managed windows
        self.window_manager.close_all_windows()
        if a0:
            a0.accept()


def main():
    """Initialize and run the application."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True,
    )

    # Initialize Database
    init_db()

    # Create application instance
    app = QApplication(sys.argv)
    
    # Set application-wide icon
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "icons", "app_icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Apply modern theme
    app.setStyleSheet(get_app_stylesheet())
    
    # Configure app behavior - allow quit on last window close
    app.setQuitOnLastWindowClosed(True)
    
    # Set up signal handler for Ctrl+C
    def signal_handler(sig, frame):
        """Handle interrupt signal (Ctrl+C)."""
        print("\nReceived interrupt signal, shutting down...")
        app.quit()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and show main window
    window = IsopGemMainWindow()
    window.showMaximized()
    
    # Run application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
