"""Adyton pillar hub - launcher interface for Inner Sanctuary tools."""
from typing import Callable

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QGraphicsDropShadowEffect, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QMouseEvent
from shared.ui import WindowManager
from .engine.window import AdytonSanctuaryEngine
from .engine.opengl_viewport import AdytonGLViewport
from .engine.wall_window import AdytonWallWindow


class AdytonHub(QWidget):
    """Hub widget for Adyton pillar - displays available tools."""
    
    def __init__(self, window_manager: WindowManager):
        super().__init__()
        self.window_manager = window_manager
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the hub interface."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(24)
        layout.setContentsMargins(40, 32, 40, 40)

        # Header section
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setSpacing(8)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("Adyton")
        title_label.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 32pt;
                font-weight: 700;
                letter-spacing: -1px;
            }
        """)
        header_layout.addWidget(title_label)

        desc_label = QLabel("The Inner Sanctuary - Chamber of the Seven Adepts")
        desc_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 12pt;
            }
        """)
        header_layout.addWidget(desc_label)
        
        layout.addWidget(header)

        # Main sanctuary tools
        tools = [
            ("⛩", "3D Engine", "Enter the Adyton sanctuary", "#3b82f6", self._open_sanctuary),
            ("◈", "OpenGL Depth", "Advanced depth-buffered viewport", "#8b5cf6", self._open_sanctuary_gl),
            ("△", "Enochian Watchtowers", "View the Kamea Tablets (156 Cells)", "#d97706", self._open_watchtowers),
            ("▦", "Constellation Map", "Explore Planetary Constellation Networks", "#10b981", self._open_wall_designer),
        ]

        grid = QGridLayout()
        grid.setSpacing(16)
        
        for i, (icon, title, desc, color, callback) in enumerate(tools):
            card = self._create_tool_card(icon, title, desc, color, callback)
            grid.addWidget(card, 0, i)
        
        layout.addLayout(grid)

        # Wall viewers section
        walls_header = QLabel("Planetary Walls")
        walls_header.setStyleSheet("""
            QLabel {
                color: #475569;
                font-size: 14pt;
                font-weight: 600;
                margin-top: 16px;
            }
        """)
        layout.addWidget(walls_header)

        # Wall viewer cards - using planetary colors
        planet_info = [
            (0, "☉", "Sun", "Solar radiance", "#f59e0b"),
            (1, "☿", "Mercury", "Swift messenger", "#64748b"),
            (2, "☽", "Moon", "Lunar reflection", "#94a3b8"),
            (3, "♀", "Venus", "Morning star", "#ec4899"),
            (4, "♃", "Jupiter", "Jovian expansion", "#8b5cf6"),
            (5, "♂", "Mars", "Martial force", "#dc2626"),
            (6, "♄", "Saturn", "Time's boundary", "#1e293b"),
        ]

        walls_grid = QGridLayout()
        walls_grid.setSpacing(12)
        
        for idx, icon, planet, desc, color in planet_info:
            card = self._create_wall_card(idx, icon, planet, desc, color)
            walls_grid.addWidget(card, idx // 4, idx % 4)
        
        layout.addLayout(walls_grid)
        
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _create_tool_card(self, icon: str, title: str, description: str, accent_color: str, callback: Callable[[], None]) -> QFrame:
        """Create a modern tool card."""
        card = QFrame()
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f1f5f9);
                border-color: {accent_color};
            }}
        """)
        card.setMinimumSize(240, 140)
        card.setMaximumHeight(160)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 25))
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(8)
        
        icon_container = QLabel(icon)
        icon_container.setFixedSize(48, 48)
        icon_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_container.setStyleSheet(f"""
            QLabel {{
                background: {accent_color}20;
                border-radius: 10px;
                font-size: 22pt;
            }}
        """)
        card_layout.addWidget(icon_container)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 14pt;
                font-weight: 600;
                background: transparent;
            }
        """)
        card_layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 9pt;
                background: transparent;
            }
        """)
        desc_label.setWordWrap(True)
        card_layout.addWidget(desc_label)
        
        card_layout.addStretch()

        self._attach_click_handler(card, callback)

        return card
    
    def _create_wall_card(self, wall_index: int, icon: str, planet: str, desc: str, color: str) -> QFrame:
        """Create a compact wall viewer card."""
        card = QFrame()
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }}
            QFrame:hover {{
                border-color: {color};
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f1f5f9);
            }}
        """)
        card.setMinimumHeight(100)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setOffset(0, 1)
        shadow.setColor(QColor(0, 0, 0, 20))
        card.setGraphicsEffect(shadow)
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(12)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                background: {color}20;
                border-radius: 8px;
                font-size: 18pt;
            }}
        """)
        card_layout.addWidget(icon_label)
        
        # Text
        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        
        title_label = QLabel(f"Wall {wall_index + 1} - {planet}")
        title_label.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 11pt;
                font-weight: 600;
                background: transparent;
            }
        """)
        text_layout.addWidget(title_label)
        
        desc_label = QLabel(desc)
        desc_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 9pt;
                background: transparent;
            }
        """)
        text_layout.addWidget(desc_label)
        
        card_layout.addWidget(text_container)
        card_layout.addStretch()

        self._attach_click_handler(card, lambda idx=wall_index: self._open_wall_view(idx))

        return card

    def _attach_click_handler(self, card: QFrame, handler: Callable[[], None]) -> None:
        """Attach a typed mouse press handler that triggers the provided callback."""

        def _on_mouse_press(a0: QMouseEvent | None) -> None:
            handler()
            if a0 is not None:
                a0.accept()

        card.mousePressEvent = _on_mouse_press

    def _open_sanctuary(self) -> None:
        """Launch the Adyton Engine window."""
        self.window_manager.open_window(
            "adyton_sanctuary_engine",
            AdytonSanctuaryEngine,
            allow_multiple=False,
        )

    def _open_sanctuary_gl(self) -> None:
        """Launch the OpenGL depth-buffered viewport."""
        self.window_manager.open_window(
            "adyton_gl_viewport",
            AdytonGLViewport,
            allow_multiple=False,
        )

    def _open_wall_view(self, wall_index: int) -> None:
        """Launch a dedicated window for a specific wall."""
        self.window_manager.open_window(
            f"adyton_wall_{wall_index}",
            AdytonWallWindow,
            allow_multiple=True,
            wall_index=wall_index,
        )

    def _open_watchtowers(self) -> None:
        """Launch the Enochian Watchtowers viewer."""
        import os
        from pillars.adyton.services.kamea_loader_service import KameaLoaderService
        from pillars.adyton.ui.watchtower_view import WatchtowerView
        
        # Determine project root (5 levels up from this file)
        # src/pillars/adyton/ui/adyton_hub.py -> ... -> project_root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
        
        loader = KameaLoaderService(project_root)
        
        self.window_manager.open_window(
            "enochian_watchtowers",
            WatchtowerView,
            allow_multiple=False,
            loader_service=loader
        )

    def _open_wall_designer(self) -> None:
        """Launch the Wall Designer tool."""
        # Need to import locally to avoid circulars if any, 
        # though adyton_hub is high level.
        from .wall_designer import WallDesignerWindow
        
        self.window_manager.open_window(
            "wall_designer",
            WallDesignerWindow,
            allow_multiple=False,
            window_manager=self.window_manager
        )

