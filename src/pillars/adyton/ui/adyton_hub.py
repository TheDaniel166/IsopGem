"""Adyton pillar hub - launcher interface for Inner Sanctuary tools."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from shared.ui import WindowManager
from .engine.window import AdytonSanctuaryEngine
from .engine.opengl_viewport import AdytonGLViewport
from .engine.wall_window import AdytonWallWindow

class AdytonHub(QWidget):
    """Hub widget for Adyton pillar - displays available tools."""
    
    def __init__(self, window_manager: WindowManager):
        """
        Initialize the Adyton hub.
        
        Args:
            window_manager: Shared window manager instance
        """
        super().__init__()
        self.window_manager = window_manager
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the hub interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("Adyton Mechanics")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            "The Inner Sanctuary of the Seven.\n\n"
            "Chamber of the Adepts, Amun Color Map, and Sacred Geometry."
        )
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_font = QFont()
        desc_font.setPointSize(12)
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet("color: #666; margin-top: 20px;")
        layout.addWidget(desc_label)

        self._create_action_buttons(layout)
        
        layout.addStretch()

    def _create_action_buttons(self, layout: QVBoxLayout) -> None:
        """Add launchers for Adyton tools."""
        container = QWidget()
        buttons_layout = QVBoxLayout(container)
        buttons_layout.setSpacing(12)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        def style_button(button: QPushButton, width: int = 360) -> None:
            button.setMinimumHeight(48)
            button.setFixedWidth(width)
            button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            button.setStyleSheet(
                "QPushButton {"
                " background-color: #2563eb;"
                " color: white;"
                " font-size: 14pt;"
                " font-weight: 600;"
                " border-radius: 10px;"
                " padding: 10px 16px;"
                " }"
                " QPushButton:hover {"
                " background-color: #1d4ed8;"
                " }"
            )

        sanctuary_btn = QPushButton("Enter the Adyton (3D Engine)")
        style_button(sanctuary_btn)
        sanctuary_btn.clicked.connect(self._open_sanctuary)
        buttons_layout.addWidget(sanctuary_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        gl_btn = QPushButton("Enter the Adyton (OpenGL Depth)")
        style_button(gl_btn)
        gl_btn.clicked.connect(self._open_sanctuary_gl)
        buttons_layout.addWidget(gl_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        walls_label = QLabel("Wall Viewers")
        walls_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        walls_label.setStyleSheet("color: #444; margin-top: 8px;")
        buttons_layout.addWidget(walls_label)

        planet_names = ["Sun", "Mercury", "Moon", "Venus", "Jupiter", "Mars", "Saturn"]
        for idx, planet in enumerate(planet_names):
            wall_btn = QPushButton(f"Open Wall {idx + 1} - {planet}")
            style_button(wall_btn, width=280)
            wall_btn.clicked.connect(lambda _=False, i=idx: self._open_wall_view(i))
            buttons_layout.addWidget(wall_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignHCenter)

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
