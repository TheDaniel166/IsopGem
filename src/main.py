"""Main entry point for the IsopGem application."""
import sys
import os
import signal
import logging

# Force Qt to use X11 instead of Wayland (more stable with PyQt6)
os.environ['QT_QPA_PLATFORM'] = 'xcb'

# Suppress Qt Wayland warnings if desired
# os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'

from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QCloseEvent, QIcon, QFont, QColor
from shared.ui import WindowManager, get_app_stylesheet
from shared.database import init_db
from pillars.gematria.ui import GematriaHub
from pillars.geometry.ui import GeometryHub
from pillars.document_manager.ui import DocumentManagerHub
from pillars.astrology.ui import AstrologyHub
from pillars.tq.ui import TQHub
from pillars.adyton.ui import AdytonHub
from pillars.correspondences.ui import CorrespondenceHub
from pillars.time_mechanics.ui import TimeMechanicsHub


class IsopGemMainWindow(QMainWindow):
    """Main window for IsopGem application."""
    
    def __init__(self):
        """Initialize the main window with all pillar tabs."""
        super().__init__()
        self.setWindowTitle("IsopGem - Integrated Esoteric Analysis Platform")
        self.setMinimumSize(1200, 800)
        
        # Set app icon
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icons", "app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Set window style with dark sidebar
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8fafc;
            }
        """)
        
        # Ensure this window WILL close the app when closed
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, True)
        
        # Create centralized window manager
        self.window_manager = WindowManager(self)
        
        # Create main container
        main_container = QWidget()
        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar navigation
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Create content area with tabs
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Header bar
        header = self._create_header()
        content_layout.addWidget(header)
        
        # Tab content (without visible tab bar - we use sidebar)
        self.tabs = QTabWidget()
        self.tabs.tabBar().setVisible(False)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: #f8fafc;
            }
        """)
        content_layout.addWidget(self.tabs)
        
        main_layout.addWidget(content_area, 1)
        
        self.setCentralWidget(main_container)
        
        # Initialize pillars
        self._init_gematria_pillar()
        self._init_geometry_pillar()
        self._init_document_manager_pillar()
        self._init_astrology_pillar()
        self._init_tq_pillar()
        self._init_adyton_pillar()
        self._init_correspondences_pillar()
        self._init_time_mechanics_pillar()
        
        # Connect tab change to raise all tool windows
        self.tabs.currentChanged.connect(self.window_manager.raise_all_windows)
        self.tabs.currentChanged.connect(self._update_header_title)
    
    def _create_sidebar(self) -> QWidget:
        """Create the navigation sidebar."""
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0f172a, stop:0.5 #1e293b, stop:1 #0f172a);
                border: none;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo/Brand area
        brand = QLabel("✦ IsopGem")
        brand.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 20pt;
                font-weight: 700;
                padding: 24px 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3b82f6, stop:1 #8b5cf6);
                letter-spacing: 1px;
            }
        """)
        layout.addWidget(brand)
        
        # Navigation buttons
        self.nav_buttons = []
        nav_items = [
            ("📖", "Gematria", "Sacred numerology"),
            ("📐", "Geometry", "Sacred geometry"),
            ("📚", "Documents", "Document manager"),
            ("⭐", "Astrology", "Celestial charts"),
            ("🔺", "TQ", "Ternary quadsets"),
            ("🏛️", "Adyton", "Inner sanctuary"),
            ("💎", "Emerald", "Correspondences"),
            ("⏳", "Time", "Time Mechanics"),
        ]
        
        for i, (icon, name, tooltip) in enumerate(nav_items):
            btn = self._create_nav_button(icon, name, tooltip, i)
            layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        layout.addStretch()
        
        # Footer
        footer = QLabel("v1.0")
        footer.setStyleSheet("""
            QLabel {
                color: #475569;
                font-size: 9pt;
                padding: 16px;
            }
        """)
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(3, 0)
        shadow.setColor(QColor(0, 0, 0, 60))
        sidebar.setGraphicsEffect(shadow)
        
        return sidebar
    
    def _create_nav_button(self, icon: str, name: str, tooltip: str, index: int) -> QFrame:
        """Create a navigation button."""
        btn = QFrame()
        btn.setToolTip(tooltip)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setProperty("index", index)
        btn.setProperty("selected", index == 0)
        
        layout = QHBoxLayout(btn)
        layout.setContentsMargins(20, 14, 16, 14)
        layout.setSpacing(12)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 18pt; background: transparent;")
        layout.addWidget(icon_label)
        
        text_label = QLabel(name)
        text_label.setStyleSheet("font-size: 11pt; font-weight: 500; background: transparent;")
        layout.addWidget(text_label)
        layout.addStretch()
        
        self._update_nav_button_style(btn, index == 0)
        
        # Click handler
        btn.mousePressEvent = lambda e, idx=index: self._on_nav_click(idx)
        
        return btn
    
    def _update_nav_button_style(self, btn: QFrame, selected: bool):
        """Update navigation button style based on selection."""
        if selected:
            btn.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(59, 130, 246, 0.3), stop:1 transparent);
                    border-left: 4px solid #3b82f6;
                    border-radius: 0;
                }
                QFrame:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(59, 130, 246, 0.35), stop:1 transparent);
                }
                QLabel {
                    color: #ffffff;
                }
            """)
        else:
            btn.setStyleSheet("""
                QFrame {
                    background: transparent;
                    border-left: 4px solid transparent;
                }
                QFrame:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(148, 163, 184, 0.15), stop:1 transparent);
                    border-left: 4px solid #64748b;
                }
                QLabel {
                    color: #94a3b8;
                }
                QFrame:hover QLabel {
                    color: #e2e8f0;
                }
            """)
    
    def _on_nav_click(self, index: int):
        """Handle navigation button click."""
        self.tabs.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            self._update_nav_button_style(btn, i == index)
    
    def _create_header(self) -> QFrame:
        """Create the header bar."""
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)
        
        self.header_title = QLabel("📖 Gematria")
        self.header_title.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 16pt;
                font-weight: 600;
                background: transparent;
            }
        """)
        layout.addWidget(self.header_title)
        
        layout.addStretch()
        
        # Could add search bar, notifications, etc. here
        
        return header
    
    def _update_header_title(self, index: int):
        """Update header title when tab changes."""
        titles = [
            "📖 Gematria",
            "📐 Sacred Geometry",
            "📚 Document Manager",
            "⭐ Astrology Charts",
            "🔺 TQ Analysis",
            "🏛️ Adyton Sanctuary",
            "💎 Emerald Tablet",
            "⏳ Time Mechanics",
        ]
        if 0 <= index < len(titles):
            self.header_title.setText(titles[index])
    
    def changeEvent(self, event):
        """Handle window state changes."""
        if event.type() == QEvent.Type.ActivationChange:
            if self.isActiveWindow():
                self.window_manager.raise_all_windows()
        super().changeEvent(event)

    def _init_gematria_pillar(self):
        """Initialize the Gematria pillar."""
        gematria_hub = GematriaHub(self.window_manager)
        self.tabs.addTab(gematria_hub, "Gematria")
    
    def _init_geometry_pillar(self):
        """Initialize the Geometry pillar."""
        geometry_hub = GeometryHub(self.window_manager)
        self.tabs.addTab(geometry_hub, "Geometry")
    
    def _init_document_manager_pillar(self):
        """Initialize the Document Manager pillar."""
        document_hub = DocumentManagerHub(self.window_manager)
        self.tabs.addTab(document_hub, "Documents")
    
    def _init_astrology_pillar(self):
        """Initialize the Astrology pillar."""
        astrology_hub = AstrologyHub(self.window_manager)
        self.tabs.addTab(astrology_hub, "Astrology")
    
    def _init_tq_pillar(self):
        """Initialize the TQ pillar."""
        tq_hub = TQHub(self.window_manager)
        self.tabs.addTab(tq_hub, "TQ")

    def _init_adyton_pillar(self):
        """Initialize the Adyton pillar."""
        adyton_hub = AdytonHub(self.window_manager)
        self.tabs.addTab(adyton_hub, "Adyton")

    def _init_correspondences_pillar(self):
        """Initialize the Emerald Tablet pillar."""
        correspondence_hub = CorrespondenceHub(self.window_manager)
        self.tabs.addTab(correspondence_hub, "Emerald Tablet")

    def _init_time_mechanics_pillar(self):
        """Initialize the Time Mechanics pillar."""
        time_hub = TimeMechanicsHub(self.window_manager)
        self.tabs.addTab(time_hub, "Time Mechanics")
    
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
