"""Dedicated viewer for a single Adyton wall."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .opengl_viewport import AdytonGLViewport


PLANET_NAMES = [
    "Sun",
    "Mercury",
    "Moon",
    "Venus",
    "Jupiter",
    "Mars",
    "Saturn",
]


class AdytonWallWindow(QWidget):
    """Displays one wall in isolation with context ring."""

    def __init__(self, wall_index: int, parent=None):
        super().__init__(parent)
        self.wall_index = wall_index
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        title = QLabel(self._title_text())
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        viewport = AdytonGLViewport(wall_index=self.wall_index)
        layout.addWidget(viewport)

        self.setWindowTitle(self._title_text())
        self.resize(1024, 768)

    def _title_text(self) -> str:
        planet = PLANET_NAMES[self.wall_index % len(PLANET_NAMES)]
        return f"Adyton Wall {self.wall_index + 1} - {planet}"
