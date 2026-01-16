"""Cymatics pillar hub - launcher interface for cymatics tools."""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QMouseEvent
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from shared.ui import WindowManager
from .cymatics_detector_window import CymaticsDetectorWindow
from .cymatics_simulator_window import CymaticsSimulatorWindow


class CymaticsHub(QWidget):
    """Hub widget for the Cymatics pillar."""

    def __init__(self, window_manager: WindowManager) -> None:
        super().__init__()
        self.window_manager = window_manager
        self._setup_ui()

    def _setup_ui(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(24)
        layout.setContentsMargins(40, 32, 40, 40)

        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setSpacing(8)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("Cymatics")
        title_label.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 32pt;
                font-weight: 700;
                letter-spacing: -1px;
            }
        """)
        header_layout.addWidget(title_label)

        desc_label = QLabel(
            "Vibrational pattern simulation with multiple plate shapes, "
            "3D visualization, particle physics, and pattern detection"
        )
        desc_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 12pt;
            }
        """)
        desc_label.setWordWrap(True)
        header_layout.addWidget(desc_label)

        layout.addWidget(header)

        tools = [
            (
                "S",
                "Cymatics Simulator",
                "Generate patterns with circular/hex plates, Hz input, 3D view, particles & export",
                "#0ea5e9",
                self._open_simulator,
            ),
            (
                "D",
                "Pattern Detector",
                "Analyze nodal lines, symmetry, and frequency content",
                "#14b8a6",
                self._open_detector,
            ),
            (
                "?",
                "Generator Help",
                "Documentation for all cymatics features",
                "#f59e0b",
                self._open_help_dialog,
            ),
        ]

        grid = QGridLayout()
        grid.setSpacing(16)

        for i, (icon, title, desc, color, callback) in enumerate(tools):
            card = self._create_tool_card(icon, title, desc, color, callback)
            grid.addWidget(card, i // 3, i % 3)

        layout.addLayout(grid)
        layout.addStretch()

        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _create_tool_card(
        self,
        icon: str,
        title: str,
        description: str,
        accent_color: str,
        callback: Callable[[], None],
    ) -> QFrame:
        card = QFrame()
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 0;
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f1f5f9);
                border-color: {accent_color};
            }}
        """)
        card.setMinimumSize(200, 140)
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
                font-size: 18pt;
                font-weight: 700;
            }}
        """)
        card_layout.addWidget(icon_container)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 13pt;
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

        def _on_card_press(a0: QMouseEvent | None) -> None:
            callback()

        card.mousePressEvent = _on_card_press
        return card

    def _open_simulator(self) -> None:
        self.window_manager.open_window(
            "cymatics_simulator",
            CymaticsSimulatorWindow,
            allow_multiple=True,
            window_manager=self.window_manager,
        )

    def _open_detector(self) -> None:
        self.window_manager.open_window(
            "cymatics_detector",
            CymaticsDetectorWindow,
            allow_multiple=True,
            window_manager=self.window_manager,
        )

    def _open_help_dialog(self) -> None:
        help_text = self._load_help_text()
        dlg = QDialog(self)
        dlg.setWindowTitle("Cymatics Simulator Help")
        dlg.setMinimumSize(820, 620)

        layout = QVBoxLayout(dlg)
        info = QTextEdit()
        info.setReadOnly(True)
        info.setPlainText(help_text)
        layout.addWidget(info)

        button_row = QHBoxLayout()
        button_row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        button_row.addWidget(close_btn)
        layout.addLayout(button_row)

        dlg.exec()

    def _load_help_text(self) -> str:
        try:
            root = Path(__file__).resolve().parents[4]
            help_path = root / "Docs" / "CYMATICS_GENERATOR_HELP.md"
            if not help_path.exists():
                raise FileNotFoundError(str(help_path))
            return help_path.read_text(encoding="utf-8")
        except Exception:
            return (
                "Cymatics Simulator help file was not found.\n"
                "Create `Docs/CYMATICS_GENERATOR_HELP.md` to override this message."
            )
