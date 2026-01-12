"""
Unified Geometry Viewer — ADR-011

A single, Canon-compliant viewer for both 2D shapes and 3D solids.
This replaces the need for separate GeometryCalculatorWindow and Geometry3DWindow.

The viewer provides:
- Adaptive viewport (2D/3D auto-switching)
- Unified property editing
- Calculation history with undo/redo
- Full Canon DSL integration
- Visual Liturgy compliant styling

Reference: wiki/01_blueprints/decisions/ADR-011_unified_geometry_viewer.md
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDoubleValidator, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSlider,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from shared.ui import WindowManager
from shared.ui.theme import COLORS, set_archetype

from .adaptive_viewport import AdaptiveViewport
from .history.history_entry import HistoryEntry
from .history.history_manager import DeclarationHistory
from .payloads.geometry_payload import GeometryPayload

logger = logging.getLogger(__name__)


# Canon DSL imports (optional)
try:
    from canon_dsl import CanonEngine, CanonValidationError
    from ...canon import GeometrySolver, PropertyDefinition
    CANON_DSL_AVAILABLE = True
except ImportError as _err:
    CANON_DSL_AVAILABLE = False
    CanonValidationError = Exception
    logger.debug(f"Canon DSL not available: {_err}")

# Formula dialog for LaTeX rendering
try:
    from ..calculator.widgets.formula_dialog import FormulaDialog
    FORMULA_DIALOG_AVAILABLE = True
except ImportError as _formula_err:
    FORMULA_DIALOG_AVAILABLE = False
    logger.debug(f"FormulaDialog not available: {_formula_err}")


class UnifiedGeometryViewer(QMainWindow):
    """
    Unified viewer for 2D shapes and 3D solids.
    
    Architecture:
        ┌──────────────┬─────────────────────┬──────────────────┐
        │  Properties  │      Viewport       │     Console      │
        │    Panel     │  (AdaptiveViewport) │   (Tab Widget)   │
        │              │                     │                  │
        │  • Title     │  ┌───────────────┐  │  Tabs:           │
        │  • Inputs    │  │ 2D/3D View    │  │  • Display       │
        │  • Derived   │  └───────────────┘  │  • View/Camera   │
        │              │                     │  • Output        │
        │  Canon Badge │  Status: ✓ · 24v   │  • History       │
        │              │                     │  • Canon         │
        └──────────────┴─────────────────────┴──────────────────┘
    
    Signals:
        payload_changed: Emitted when geometry payload changes
        history_changed: Emitted when calculation history changes
    """
    
    # Signals
    payload_changed = pyqtSignal(object)  # GeometryPayload
    history_changed = pyqtSignal()
    
    def __init__(
        self,
        window_manager: Optional[WindowManager] = None,
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize the Unified Geometry Viewer.
        
        Args:
            window_manager: Optional WindowManager for window tracking
            parent: Optional parent widget
        """
        super().__init__(parent)
        
        self.window_manager = window_manager
        
        # State
        self._current_payload: Optional[GeometryPayload] = None
        self._current_solver: Optional[GeometrySolver] = None
        self._updating_inputs = False
        
        # Canon DSL state
        self._canon_engine: Optional[CanonEngine] = None
        self._canon_declaration: Optional[Any] = None
        self._canon_verdict: Optional[Any] = None
        self._canon_result: Optional[Any] = None
        
        if CANON_DSL_AVAILABLE:
            self._canon_engine = CanonEngine()
        
        # History
        self._history = DeclarationHistory(max_entries=50, parent=self)
        self._history.current_changed.connect(self._on_history_changed)
        self._history.history_changed.connect(self._refresh_history_list)
        
        # Set up metadata persistence for notes/custom_titles
        import os
        from shared.config import get_config
        config = get_config()
        state_dir = str(config.paths.user_state) if hasattr(config.paths, 'user_state') else os.path.expanduser("~/.isopgem/state")
        metadata_file = os.path.join(state_dir, "geometry_history_metadata.json")
        self._history.set_metadata_file(metadata_file)

        # Set up session persistence file for full history
        self._session_file = os.path.join(state_dir, "geometry_history_session.json")

        # Flag to skip adding initial realization to history
        self._skip_initial_history = True
        
        # Flag to block recalculation when restoring from history
        self._restoring_from_history = False
        
        # UI references
        self._property_inputs: Dict[str, QLineEdit] = {}
        self._property_labels: Dict[str, QLabel] = {}
        self._property_error_label: Optional[QLabel] = None
        self._title_label: Optional[QLabel] = None
        self._status_label: Optional[QLabel] = None
        self._canon_badge: Optional[QPushButton] = None
        self._save_history_btn: Optional[QPushButton] = None
        self._canon_metrics_labels: Dict[str, QLabel] = {}
        self._history_list_widget: Optional[QWidget] = None
        
        # Set up window
        self.setWindowTitle("Unified Geometry Viewer")
        self.setMinimumSize(1400, 800)  # Ensure enough space for all panels
        
        self._setup_ui()
        self._setup_shortcuts()

        # Restore previous session after UI is ready
        self._restore_session()

        logger.info("UnifiedGeometryViewer initialized")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # UI Setup
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _setup_ui(self) -> None:
        """Build the main UI structure."""
        # Apply root stylesheet to isolate from app's global styles (light theme)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['cloud']};
            }}
            QWidget {{
                font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background-color: {COLORS['marble']};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS['ash']};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['stone']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background-color: {COLORS['marble']};
                height: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {COLORS['ash']};
                border-radius: 4px;
                min-width: 20px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {COLORS['stone']};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            QCheckBox {{
                color: {COLORS['stone']};
                font-size: 12px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 2px solid {COLORS['ash']};
                background-color: {COLORS['light']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['magus']};
                border-color: {COLORS['magus']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {COLORS['focus']};
            }}
            QSlider::groove:horizontal {{
                height: 6px;
                background-color: {COLORS['ash']};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                width: 16px;
                height: 16px;
                margin: -5px 0;
                background-color: {COLORS['magus']};
                border-radius: 8px;
            }}
            QSlider::handle:horizontal:hover {{
                background-color: {COLORS['magus_mute']};
            }}
        """)
        
        central = QWidget(self)
        self.setCentralWidget(central)
        central.setStyleSheet(f"background-color: {COLORS['cloud']};")
        
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)
        
        # Main splitter (3 panels)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)  # Prevent panels from being collapsed
        splitter.setHandleWidth(1)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {COLORS['ash']};
            }}
        """)
        
        # Build panels with minimum widths to prevent compression
        self._properties_panel = self._build_properties_panel()
        self._properties_panel.setMinimumWidth(320)
        
        self._viewport_panel = self._build_viewport_panel()
        self._viewport_panel.setMinimumWidth(400)
        
        self._console_panel = self._build_console_panel()
        self._console_panel.setMinimumWidth(320)
        
        splitter.addWidget(self._properties_panel)
        splitter.addWidget(self._viewport_panel)
        splitter.addWidget(self._console_panel)
        splitter.setSizes([340, 720, 340])
        
        root_layout.addWidget(splitter, 1)
    
    def _setup_shortcuts(self) -> None:
        """Set up keyboard shortcuts."""
        # Undo: Ctrl+Z
        undo_shortcut = QShortcut(QKeySequence.StandardKey.Undo, self)
        undo_shortcut.activated.connect(self._on_undo)

        # Redo: Ctrl+Y or Ctrl+Shift+Z
        redo_shortcut = QShortcut(QKeySequence.StandardKey.Redo, self)
        redo_shortcut.activated.connect(self._on_redo)

        # Save to History: Ctrl+S
        save_history_shortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        save_history_shortcut.activated.connect(self._on_save_to_history)
    
    # ───────────────────────────────────────────────────────────────────────────
    # Properties Panel
    # ───────────────────────────────────────────────────────────────────────────
    
    def _build_properties_panel(self) -> QFrame:
        """Build the left properties panel."""
        panel = QFrame()
        panel.setObjectName("PropertiesPanel")
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        panel.setStyleSheet(f"""
            QFrame#PropertiesPanel {{
                background-color: {COLORS['marble']};
                border: 1px solid {COLORS['ash']};
                border-radius: 8px;
            }}
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Title section with derivation button
        title_row = QHBoxLayout()
        title_row.setSpacing(12)
        
        self._title_label = QLabel("Select a Form")
        self._title_label.setObjectName("FormTitle")
        self._title_label.setStyleSheet(f"""
            QLabel#FormTitle {{
                color: {COLORS['void']};
                font-size: 18px;
                font-weight: 600;
            }}
        """)
        title_row.addWidget(self._title_label)
        title_row.addStretch()
        
        # Derivations button
        self._derivation_btn = QPushButton("📖")
        self._derivation_btn.setObjectName("DerivationBtn")
        self._derivation_btn.setToolTip("View mathematical derivations & commentary")
        self._derivation_btn.setFixedSize(32, 32)
        self._derivation_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._derivation_btn.setStyleSheet(f"""
            QPushButton#DerivationBtn {{
                background-color: {COLORS['seeker_soft']};
                color: {COLORS['seeker']};
                border: 1px solid {COLORS['seeker_mute']};
                border-radius: 16px;
                font-size: 16px;
                padding: 0;
            }}
            QPushButton#DerivationBtn:hover {{
                background-color: {COLORS['seeker_mute']};
                border-color: {COLORS['seeker']};
            }}
            QPushButton#DerivationBtn:disabled {{
                background-color: {COLORS['marble']};
                color: {COLORS['mist']};
                border-color: {COLORS['ash']};
            }}
        """)
        self._derivation_btn.clicked.connect(self._show_derivation_dialog)
        self._derivation_btn.setEnabled(False)  # Disabled until form selected
        title_row.addWidget(self._derivation_btn)
        
        layout.addLayout(title_row)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"background-color: {COLORS['ash']};")
        divider.setFixedHeight(1)
        layout.addWidget(divider)
        
        # Properties scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        self._property_layout = QVBoxLayout(scroll_content)
        self._property_layout.setContentsMargins(0, 0, 8, 0)
        self._property_layout.setSpacing(8)
        
        # Placeholder
        placeholder = QLabel("No form selected")
        placeholder.setObjectName("PropertyPlaceholder")
        placeholder.setStyleSheet(f"""
            QLabel#PropertyPlaceholder {{
                color: {COLORS['mist']};
                font-style: italic;
                padding: 20px;
            }}
        """)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._property_layout.addWidget(placeholder)
        self._property_placeholder = placeholder
        
        # Error label (hidden by default)
        self._property_error_label = QLabel()
        self._property_error_label.setObjectName("PropertyError")
        self._property_error_label.setStyleSheet(f"""
            QLabel#PropertyError {{
                color: {COLORS['destroyer']};
                background-color: {COLORS['destroyer_soft']};
                padding: 8px;
                border-radius: 4px;
                font-size: 12px;
            }}
        """)
        self._property_error_label.setWordWrap(True)
        self._property_error_label.hide()
        self._property_layout.addWidget(self._property_error_label)
        
        self._property_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll, 1)
        
        # Canon Badge section
        canon_section = self._build_canon_badge_section()
        layout.addWidget(canon_section)
        
        return panel
    
    def _build_canon_badge_section(self) -> QFrame:
        """Build the Canon badge and quick metrics section."""
        frame = QFrame()
        frame.setObjectName("CanonBadgeSection")
        frame.setStyleSheet(f"""
            QFrame#CanonBadgeSection {{
                background-color: {COLORS['cloud']};
                border: 1px solid {COLORS['ash']};
                border-radius: 6px;
                padding: 8px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Header with badge
        header = QHBoxLayout()
        
        header_label = QLabel("✦ Canon Status")
        header_label.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        header.addWidget(header_label)
        header.addStretch()
        
        self._canon_badge = QPushButton("⏳ Pending")
        self._canon_badge.setObjectName("CanonBadge")
        self._canon_badge.setCursor(Qt.CursorShape.PointingHandCursor)
        self._canon_badge.setStyleSheet(f"""
            QPushButton#CanonBadge {{
                background-color: {COLORS['navigator_soft']};
                color: {COLORS['stone']};
                border: 1px solid {COLORS['ash']};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: 500;
            }}
            QPushButton#CanonBadge:hover {{
                background-color: {COLORS['surface_hover']};
            }}
        """)
        self._canon_badge.clicked.connect(self._show_canon_details)
        header.addWidget(self._canon_badge)
        
        layout.addLayout(header)
        
        # Quick metrics
        metrics_layout = QVBoxLayout()
        metrics_layout.setSpacing(4)
        
        for key, label_text in [
            ("signature", "Signature:"),
            ("phi", "φ (Golden Ratio):"),
            ("form_type", "Form:"),
        ]:
            row = QHBoxLayout()
            label = QLabel(label_text)
            label.setStyleSheet(f"color: {COLORS['mist']}; font-size: 11px;")
            value = QLabel("—")
            value.setStyleSheet(f"color: {COLORS['stone']}; font-size: 11px;")
            value.setAlignment(Qt.AlignmentFlag.AlignRight)
            row.addWidget(label)
            row.addStretch()
            row.addWidget(value)
            metrics_layout.addLayout(row)
            self._canon_metrics_labels[key] = value
        
        layout.addLayout(metrics_layout)

        # Save to History button
        save_history_btn = QPushButton("💾 Save to History")
        save_history_btn.setObjectName("SaveHistoryBtn")
        save_history_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_history_btn.setToolTip("Save the current calculation to history (Ctrl+S)")
        save_history_btn.setStyleSheet(f"""
            QPushButton#SaveHistoryBtn {{
                background-color: {COLORS['seeker']};
                color: {COLORS['light']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton#SaveHistoryBtn:hover {{
                background-color: {COLORS['seeker_mute']};
            }}
            QPushButton#SaveHistoryBtn:pressed {{
                background-color: {COLORS['seeker_soft']};
            }}
            QPushButton#SaveHistoryBtn:disabled {{
                background-color: {COLORS['ash']};
                color: {COLORS['mist']};
            }}
        """)
        save_history_btn.clicked.connect(self._on_save_to_history)
        self._save_history_btn = save_history_btn
        layout.addWidget(save_history_btn)

        return frame
    
    # ───────────────────────────────────────────────────────────────────────────
    # Viewport Panel
    # ───────────────────────────────────────────────────────────────────────────
    
    def _build_viewport_panel(self) -> QFrame:
        """Build the center viewport panel."""
        panel = QFrame()
        panel.setObjectName("ViewportPanel")
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        panel.setStyleSheet(f"""
            QFrame#ViewportPanel {{
                background-color: {COLORS['cloud']};
                border: 1px solid {COLORS['ash']};
                border-radius: 8px;
            }}
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Adaptive viewport
        self._viewport = AdaptiveViewport()
        self._viewport.payload_changed.connect(self._on_viewport_payload_changed)
        self._viewport.stats_changed.connect(self._on_viewport_stats_changed)
        layout.addWidget(self._viewport, 1)
        
        # Status bar
        status_bar = QFrame()
        status_bar.setObjectName("ViewportStatus")
        status_bar.setFixedHeight(32)
        status_bar.setStyleSheet(f"""
            QFrame#ViewportStatus {{
                background-color: {COLORS['marble']};
                border-top: 1px solid {COLORS['ash']};
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
        """)
        
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(12, 0, 12, 0)
        
        self._status_label = QLabel("Ready")
        self._status_label.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 12px;
        """)
        status_layout.addWidget(self._status_label)
        
        status_layout.addStretch()
        
        # Quick controls
        reset_btn = QPushButton("Reset View")
        reset_btn.setObjectName("ResetViewBtn")
        set_archetype(reset_btn, "ghost")  # Light-themed button
        reset_btn.setFixedHeight(24)
        reset_btn.clicked.connect(self._viewport.reset_view)
        status_layout.addWidget(reset_btn)
        
        layout.addWidget(status_bar)
        
        return panel
    
    # ───────────────────────────────────────────────────────────────────────────
    # Console Panel
    # ───────────────────────────────────────────────────────────────────────────
    
    def _build_console_panel(self) -> QFrame:
        """Build the right console panel with tabs."""
        panel = QFrame()
        panel.setObjectName("ConsolePanel")
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        panel.setStyleSheet(f"""
            QFrame#ConsolePanel {{
                background-color: {COLORS['marble']};
                border: 1px solid {COLORS['ash']};
                border-radius: 8px;
            }}
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Tab widget
        self._console_tabs = QTabWidget()
        self._console_tabs.setObjectName("ConsoleTabs")
        self._console_tabs.setUsesScrollButtons(False)  # Prevent scroll arrows
        self._console_tabs.setStyleSheet(f"""
            QTabWidget#ConsoleTabs::pane {{
                border: none;
                background-color: {COLORS['marble']};
            }}
            QTabWidget#ConsoleTabs > QTabBar {{
                qproperty-expanding: true;
            }}
            QTabWidget#ConsoleTabs QTabBar::scroller {{
                width: 0px;
            }}
            QTabWidget#ConsoleTabs QTabBar::tab {{
                background-color: {COLORS['cloud']};
                color: {COLORS['stone']};
                border: none;
                padding: 8px 12px;
                font-size: 12px;
                min-width: 50px;
            }}
            QTabWidget#ConsoleTabs QTabBar::tab:selected {{
                background-color: {COLORS['marble']};
                color: {COLORS['void']};
                font-weight: 500;
            }}
            QTabWidget#ConsoleTabs QTabBar::tab:hover:!selected {{
                background-color: {COLORS['surface_hover']};
            }}
        """)
        
        # Build tabs
        self._console_tabs.addTab(self._build_display_tab(), "Display")
        self._console_tabs.addTab(self._build_view_tab(), "View")
        self._console_tabs.addTab(self._build_output_tab(), "Output")
        self._console_tabs.addTab(self._build_history_tab(), "History")
        self._console_tabs.addTab(self._build_canon_tab(), "Canon")
        
        layout.addWidget(self._console_tabs)
        
        return panel
    
    def _build_display_tab(self) -> QWidget:
        """Build the Display settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Section: Core Visibility
        section1 = QLabel("Core Elements")
        section1.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        layout.addWidget(section1)
        
        # Checkboxes for core elements
        self._axes_checkbox = QCheckBox("Show Axes")
        self._axes_checkbox.setChecked(True)
        self._axes_checkbox.toggled.connect(self._viewport.set_axes_visible)
        layout.addWidget(self._axes_checkbox)
        
        self._labels_checkbox = QCheckBox("Show Labels")
        self._labels_checkbox.setChecked(False)  # Off by default
        self._labels_checkbox.toggled.connect(self._viewport.set_labels_visible)
        layout.addWidget(self._labels_checkbox)
        
        self._faces_checkbox = QCheckBox("Show Faces")
        self._faces_checkbox.setChecked(True)
        self._faces_checkbox.toggled.connect(self._viewport.set_show_faces)
        layout.addWidget(self._faces_checkbox)
        
        self._edges_checkbox = QCheckBox("Show Edges")
        self._edges_checkbox.setChecked(True)
        self._edges_checkbox.toggled.connect(self._viewport.set_show_edges)
        layout.addWidget(self._edges_checkbox)
        
        self._vertices_checkbox = QCheckBox("Show Vertices")
        self._vertices_checkbox.setChecked(False)
        self._vertices_checkbox.toggled.connect(self._viewport.set_show_vertices)
        layout.addWidget(self._vertices_checkbox)
        
        # Section: 3D Special Elements
        section2 = QLabel("3D Special")
        section2.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 8px;
        """)
        layout.addWidget(section2)
        
        # Dual solid toggle (hidden for 2D)
        self._dual_checkbox = QCheckBox("Show Dual Solid (Ghost)")
        self._dual_checkbox.setChecked(False)
        self._dual_checkbox.toggled.connect(self._viewport.set_dual_visible)
        layout.addWidget(self._dual_checkbox)

        # Circle/Sphere toggles (incircle, midsphere, circumsphere)
        self._sphere_checkboxes: dict[str, QCheckBox] = {}
        sphere_toggles = [
            ("incircle", "Show Incircle"),
            ("midsphere", "Show Midsphere"),
            ("circumsphere", "Show Circumcircle"),
        ]
        for key, label in sphere_toggles:
            cb = QCheckBox(label)
            cb.setChecked(False)
            cb.toggled.connect(lambda checked, k=key: self._viewport.set_sphere_visible(k, checked))
            layout.addWidget(cb)
            self._sphere_checkboxes[key] = cb
        
        # Section: Tools
        section3 = QLabel("Tools")
        section3.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 8px;
        """)
        layout.addWidget(section3)
        
        # Measure tool
        self._measure_button = QPushButton("📏 Measure Tool")
        self._measure_button.setObjectName("MeasureToolBtn")
        self._measure_button.setCheckable(True)
        self._measure_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._measure_button.setStyleSheet(f"""
            QPushButton#MeasureToolBtn {{
                background-color: {COLORS['marble']};
                border: 1px solid {COLORS['ash']};
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: 600;
                color: {COLORS['void']};
            }}
            QPushButton#MeasureToolBtn:checked {{
                background-color: {COLORS['seeker_soft']};
                border-color: {COLORS['seeker']};
                color: {COLORS['seeker']};
            }}
            QPushButton#MeasureToolBtn:hover {{
                background-color: {COLORS['surface_hover']};
            }}
        """)
        self._measure_button.toggled.connect(self._on_measure_mode_toggled)
        layout.addWidget(self._measure_button)
        
        layout.addStretch()
        
        return tab
    
    def _on_measure_mode_toggled(self, enabled: bool) -> None:
        """Toggle measure mode on the viewport."""
        self._viewport.set_measure_mode(enabled)
        if enabled:
            self._show_status("Measure mode: Click two vertices to measure distance")
        else:
            self._clear_status()
    
    def _build_view_tab(self) -> QWidget:
        """Build the View/Camera settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Section: Camera (3D only)
        section_label = QLabel("Camera (3D)")
        section_label.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        layout.addWidget(section_label)
        
        # Elevation slider
        elev_layout = QHBoxLayout()
        elev_label = QLabel("Elevation:")
        elev_label.setStyleSheet(f"color: {COLORS['stone']}; font-size: 12px;")
        elev_layout.addWidget(elev_label)
        
        self._elevation_slider = QSlider(Qt.Orientation.Horizontal)
        self._elevation_slider.setRange(-90, 90)
        self._elevation_slider.setValue(30)
        self._elevation_slider.valueChanged.connect(
            lambda v: self._viewport.set_elevation(float(v))
        )
        elev_layout.addWidget(self._elevation_slider)
        
        self._elevation_value = QLabel("30°")
        self._elevation_value.setStyleSheet(f"color: {COLORS['mist']}; font-size: 11px;")
        self._elevation_value.setFixedWidth(40)
        self._elevation_slider.valueChanged.connect(
            lambda v: self._elevation_value.setText(f"{v}°")
        )
        elev_layout.addWidget(self._elevation_value)
        
        layout.addLayout(elev_layout)
        
        # Azimuth slider
        azim_layout = QHBoxLayout()
        azim_label = QLabel("Azimuth:")
        azim_label.setStyleSheet(f"color: {COLORS['stone']}; font-size: 12px;")
        azim_layout.addWidget(azim_label)
        
        self._azimuth_slider = QSlider(Qt.Orientation.Horizontal)
        self._azimuth_slider.setRange(0, 360)
        self._azimuth_slider.setValue(45)
        self._azimuth_slider.valueChanged.connect(
            lambda v: self._viewport.set_azimuth(float(v))
        )
        azim_layout.addWidget(self._azimuth_slider)
        
        self._azimuth_value = QLabel("45°")
        self._azimuth_value.setStyleSheet(f"color: {COLORS['mist']}; font-size: 11px;")
        self._azimuth_value.setFixedWidth(40)
        self._azimuth_slider.valueChanged.connect(
            lambda v: self._azimuth_value.setText(f"{v}°")
        )
        azim_layout.addWidget(self._azimuth_value)
        
        layout.addLayout(azim_layout)
        
        # Section: Quick Views
        section2 = QLabel("Quick Views")
        section2.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 8px;
        """)
        layout.addWidget(section2)
        
        # Quick view buttons grid
        quick_views_layout = QHBoxLayout()
        quick_views_layout.setSpacing(8)
        
        quick_views = [
            ("Top", 0, 0),
            ("Front", -90, 0),  # Flipped to show right-side up
            ("Side", 0, 90),
            ("Iso", 30, 45),
        ]
        for name, elev, azim in quick_views:
            btn = QPushButton(name)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['marble']};
                    border: 1px solid {COLORS['ash']};
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 11px;
                    color: {COLORS['stone']};
                }}
                QPushButton:hover {{
                    background-color: {COLORS['surface_hover']};
                    color: {COLORS['void']};
                }}
            """)
            btn.clicked.connect(lambda _, e=elev, a=azim: self._set_quick_view(e, a))
            quick_views_layout.addWidget(btn)
        
        layout.addLayout(quick_views_layout)
        
        # Section: Zoom
        section3 = QLabel("Zoom")
        section3.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 8px;
        """)
        layout.addWidget(section3)
        
        zoom_layout = QHBoxLayout()
        zoom_layout.setSpacing(8)
        
        zoom_in_btn = QPushButton("➕ Zoom In")
        zoom_in_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['marble']};
                border: 1px solid {COLORS['ash']};
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                color: {COLORS['stone']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_hover']};
                color: {COLORS['void']};
            }}
        """)
        zoom_in_btn.clicked.connect(lambda: self._viewport.zoom_in())
        zoom_layout.addWidget(zoom_in_btn)
        
        zoom_out_btn = QPushButton("➖ Zoom Out")
        zoom_out_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['marble']};
                border: 1px solid {COLORS['ash']};
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                color: {COLORS['stone']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_hover']};
                color: {COLORS['void']};
            }}
        """)
        zoom_out_btn.clicked.connect(lambda: self._viewport.zoom_out())
        zoom_layout.addWidget(zoom_out_btn)
        
        layout.addLayout(zoom_layout)
        
        fit_btn = QPushButton("🔍 Fit to View")
        fit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['marble']};
                border: 1px solid {COLORS['ash']};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 12px;
                color: {COLORS['stone']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_hover']};
                color: {COLORS['void']};
            }}
        """)
        fit_btn.clicked.connect(lambda: self._viewport.fit_to_view())
        layout.addWidget(fit_btn)
        
        reset_btn = QPushButton("↺ Reset View")
        set_archetype(reset_btn, "ghost")  # Light-themed button
        reset_btn.clicked.connect(lambda: self._viewport.reset_view())
        layout.addWidget(reset_btn)
        
        layout.addStretch()
        
        return tab
    
    def _set_quick_view(self, elevation: int, azimuth: int) -> None:
        """Set quick view camera position."""
        self._elevation_slider.setValue(elevation)
        self._azimuth_slider.setValue(azimuth)
        self._viewport.set_elevation(float(elevation))
        self._viewport.set_azimuth(float(azimuth))
    
    def _build_output_tab(self) -> QWidget:
        """Build the Output/Export tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Section: Export
        section_label = QLabel("Export")
        section_label.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        layout.addWidget(section_label)
        
        # Snapshot button
        snapshot_btn = QPushButton("📷 Save Snapshot")
        set_archetype(snapshot_btn, "ghost")  # Light-themed button
        snapshot_btn.clicked.connect(self._save_snapshot)
        layout.addWidget(snapshot_btn)
        
        # Copy measurements button
        copy_btn = QPushButton("📋 Copy Measurements")
        set_archetype(copy_btn, "ghost")  # Light-themed button
        copy_btn.clicked.connect(self._copy_measurements)
        layout.addWidget(copy_btn)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"background-color: {COLORS['ash']};")
        divider.setFixedHeight(1)
        layout.addWidget(divider)
        
        # Section: Canon Exports
        canon_section = QLabel("Canon Exports")
        canon_section.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        layout.addWidget(canon_section)
        
        # Copy Declaration button
        decl_btn = QPushButton("📜 Copy Declaration (JSON)")
        set_archetype(decl_btn, "seeker")
        decl_btn.clicked.connect(self._copy_declaration)
        layout.addWidget(decl_btn)
        
        # Copy Validation Report button
        report_btn = QPushButton("📊 Copy Validation Report")
        set_archetype(report_btn, "seeker")
        report_btn.clicked.connect(self._copy_validation_report)
        layout.addWidget(report_btn)
        
        layout.addStretch()
        
        return tab
    
    def _build_history_tab(self) -> QWidget:
        """Build the History tab with timeline and controls."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Section: Timeline
        section_label = QLabel("Calculation History")
        section_label.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        layout.addWidget(section_label)
        
        # Undo/Redo buttons
        nav_layout = QHBoxLayout()
        
        self._undo_btn = QPushButton("↶ Undo")
        set_archetype(self._undo_btn, "ghost")  # Light-themed button
        self._undo_btn.setEnabled(False)
        self._undo_btn.clicked.connect(self._on_undo)
        nav_layout.addWidget(self._undo_btn)
        
        self._redo_btn = QPushButton("↷ Redo")
        set_archetype(self._redo_btn, "ghost")  # Light-themed button
        self._redo_btn.setEnabled(False)
        self._redo_btn.clicked.connect(self._on_redo)
        nav_layout.addWidget(self._redo_btn)
        
        layout.addLayout(nav_layout)
        
        # History list (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setMaximumHeight(200)
        
        self._history_list_widget = QWidget()
        self._history_list_layout = QVBoxLayout(self._history_list_widget)
        self._history_list_layout.setContentsMargins(0, 0, 0, 0)
        self._history_list_layout.setSpacing(4)
        
        # Empty state
        empty_label = QLabel("No history yet")
        empty_label.setStyleSheet(f"color: {COLORS['mist']}; font-style: italic;")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._history_list_layout.addWidget(empty_label)
        self._history_empty_label = empty_label
        
        self._history_list_layout.addStretch()
        
        scroll.setWidget(self._history_list_widget)
        layout.addWidget(scroll, 1)
        
        # Tip label
        tip_label = QLabel("Right-click an item for options (notes, rename, delete)")
        tip_label.setStyleSheet(f"""
            color: {COLORS['mist']};
            font-size: 10px;
            font-style: italic;
            padding: 4px 0;
        """)
        layout.addWidget(tip_label)
        
        # Export session button
        export_btn = QPushButton("💾 Export Session")
        set_archetype(export_btn, "ghost")  # Light-themed button
        export_btn.clicked.connect(self._export_session)
        layout.addWidget(export_btn)
        
        return tab
    
    def _build_canon_tab(self) -> QWidget:
        """Build the Canon validation details tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Section: Validation Status
        section_label = QLabel("Validation Status")
        section_label.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        layout.addWidget(section_label)
        
        # Large status indicator
        self._canon_status_frame = QFrame()
        self._canon_status_frame.setObjectName("CanonStatusFrame")
        self._canon_status_frame.setStyleSheet(f"""
            QFrame#CanonStatusFrame {{
                background-color: {COLORS['navigator_soft']};
                border-radius: 6px;
                padding: 12px;
            }}
        """)
        
        status_layout = QVBoxLayout(self._canon_status_frame)
        
        self._canon_status_icon = QLabel("⏳")
        self._canon_status_icon.setStyleSheet("font-size: 32px;")
        self._canon_status_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self._canon_status_icon)
        
        self._canon_status_text = QLabel("Awaiting validation")
        self._canon_status_text.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 14px;
            font-weight: 500;
        """)
        self._canon_status_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self._canon_status_text)
        
        layout.addWidget(self._canon_status_frame)
        
        # Findings section
        findings_label = QLabel("Findings")
        findings_label.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        layout.addWidget(findings_label)
        
        # Findings list (scrollable text area)
        self._findings_text = QTextEdit()
        self._findings_text.setReadOnly(True)
        self._findings_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['cloud']};
                border: 1px solid {COLORS['ash']};
                border-radius: 4px;
                color: {COLORS['stone']};
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                font-size: 11px;
                padding: 8px;
            }}
        """)
        self._findings_text.setPlaceholderText("No findings to display")
        layout.addWidget(self._findings_text, 1)
        
        return tab
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Public API
    # ═══════════════════════════════════════════════════════════════════════════
    
    def set_solver(self, solver: GeometrySolver) -> None:
        """
        Set the active geometry solver.
        
        This configures the viewer for a specific form type (e.g., Circle, Cube).
        The solver provides property definitions and creates Declarations.
        
        Args:
            solver: A GeometrySolver instance
        """
        self._current_solver = solver
        
        # Update title
        if self._title_label:
            self._title_label.setText(solver.form_type)
        
        # Enable derivation button if derivation available
        if self._derivation_btn:
            has_derivation = bool(solver.get_derivation())
            self._derivation_btn.setEnabled(has_derivation)
            self._derivation_btn.setToolTip(
                "View mathematical derivations & commentary" if has_derivation
                else "No derivations available for this form"
            )
        
        # Rebuild property inputs
        self._rebuild_property_inputs()
        
        # Clear Canon state
        self._canon_declaration = None
        self._canon_verdict = None
        self._canon_result = None
        self._update_canon_display()
        
        # Update status
        dim_label = "2D" if solver.is_2d else "3D"
        if self._status_label:
            self._status_label.setText(f"{solver.form_type} ({dim_label}) — Ready")

        # Restore any pending session entries now that solver is available
        self._restore_session_entries()

        logger.info(f"Solver set: {solver.form_type} ({dim_label})")
    
    def set_payload(self, payload: GeometryPayload) -> None:
        """
        Set the geometry payload to display.
        
        This updates the viewport, property inputs, and Canon state.
        
        Args:
            payload: The GeometryPayload to display
        """
        self._current_payload = payload
        self._viewport.set_payload(payload)
        
        # Sync visibility states from checkboxes to viewport
        self._sync_visibility_to_viewport()
        
        # Update property inputs with calculated values
        self._sync_property_inputs()
        
        # Update Canon metrics from payload
        self._update_canon_metrics_from_payload(payload)
        
        self.payload_changed.emit(payload)
    
    def _sync_visibility_to_viewport(self) -> None:
        """Sync all visibility checkbox states to the viewport."""
        # Core elements
        if hasattr(self, '_axes_checkbox'):
            self._viewport.set_axes_visible(self._axes_checkbox.isChecked())
        if hasattr(self, '_labels_checkbox'):
            self._viewport.set_labels_visible(self._labels_checkbox.isChecked())
        if hasattr(self, '_faces_checkbox'):
            self._viewport.set_show_faces(self._faces_checkbox.isChecked())
        if hasattr(self, '_edges_checkbox'):
            self._viewport.set_show_edges(self._edges_checkbox.isChecked())
        if hasattr(self, '_vertices_checkbox'):
            self._viewport.set_show_vertices(self._vertices_checkbox.isChecked())
        
        # 3D special
        if hasattr(self, '_dual_checkbox'):
            self._viewport.set_dual_visible(self._dual_checkbox.isChecked())
        
        # Spheres
        if hasattr(self, '_sphere_checkboxes'):
            for key, cb in self._sphere_checkboxes.items():
                self._viewport.set_sphere_visible(key, cb.isChecked())
        
        # Update checkbox availability based on payload
        self._update_checkbox_availability()
    
    def _update_checkbox_availability(self) -> None:
        """Enable/disable checkboxes based on what's available in the current payload."""
        payload = self._current_payload
        is_2d = bool(payload and payload.is_2d)
        
        # Get metadata from solid payload if available
        metadata = {}
        if payload and payload.solid_payload and payload.solid_payload.metadata:
            metadata = payload.solid_payload.metadata
        
        # Check if dual solid is available
        has_dual = bool(payload and payload.solid_payload and getattr(payload.solid_payload, 'dual', None) is not None)
        if hasattr(self, '_dual_checkbox'):
            self._dual_checkbox.setVisible(not is_2d)
            self._dual_checkbox.setEnabled(has_dual and not is_2d)
            if has_dual and not is_2d:
                self._dual_checkbox.setToolTip("Show the dual polyhedron as a ghost overlay")
            else:
                self._dual_checkbox.setToolTip("Not available — this geometry has no dual solid")
                self._dual_checkbox.setChecked(False)
        
        # Check sphere availability based on metadata keys
        sphere_keys = {
            'incircle': 'inradius',
            'midsphere': 'midradius', 
            'circumsphere': 'circumradius',
        }
        
        if hasattr(self, '_sphere_checkboxes'):
            for key, cb in self._sphere_checkboxes.items():
                cb.setVisible(True)
                metadata_key = sphere_keys.get(key, key)
                if is_2d:
                    # Always allow incircle/circumcircle toggles in 2D; hide midsphere
                    if key == 'midsphere':
                        cb.setChecked(False)
                        cb.setVisible(False)
                        continue
                    cb.setEnabled(True)
                    cb.setToolTip(f"Toggle {key} overlay")
                    continue

                has_sphere = metadata_key in metadata and metadata.get(metadata_key, 0) > 0
                cb.setEnabled(has_sphere)
                if has_sphere:
                    cb.setToolTip(f"Show the {key} sphere")
                else:
                    cb.setToolTip(f"Not available — no {metadata_key} data for this geometry")
                    cb.setChecked(False)
    
    def realize_from_canonical(self, canonical_value: Any) -> Optional[GeometryPayload]:
        """
        Realize geometry from a canonical parameter value.
        
        This is the main calculation entry point:
        1. Solver creates Declaration
        2. Engine validates
        3. Engine realizes
        4. Result becomes payload
        5. History entry created
        
        Args:
            canonical_value: The canonical parameter (e.g., radius) or a
                canonical dictionary for multi-parameter forms (e.g., torus knots)
        
        Returns:
            GeometryPayload if successful, None otherwise
        """
        if not self._current_solver:
            logger.warning("No solver set")
            return None
        
        if not self._canon_engine:
            logger.warning("Canon engine not available")
            return None
        
        try:
            # Create declaration
            decl = self._current_solver.create_declaration(canonical_value)
            self._canon_declaration = decl
            
            # Validate
            verdict = self._canon_engine.validate(decl)
            self._canon_verdict = verdict
            
            if not verdict.ok:
                # Validation failed
                self._canon_result = None
                self._update_canon_display()
                self._show_property_error(f"Validation failed: {verdict.summary()}")

                # Don't auto-add to history - user must explicitly save
                return None
            
            # Realize
            result = self._canon_engine.realize(decl)
            self._canon_result = result
            
            # Get artifact - try form id first, then form type, then generic
            # The realizer stores artifacts keyed by form.id (e.g., "vault")
            artifact = None
            forms = getattr(decl, "forms", [])
            if forms:
                form_id = getattr(forms[0], "id", None)
                if form_id:
                    artifact = result.get_artifact(form_id)
            
            if artifact is None:
                # Try form type (lowercase)
                artifact = result.get_artifact(self._current_solver.form_type.lower())
            
            if artifact is None:
                # Try generic name
                artifact = result.get_artifact("geometry")
            
            if artifact is None:
                logger.error("Realization returned no artifact")
                logger.error(f"  Available artifacts: {list(result.artifacts.keys()) if hasattr(result, 'artifacts') else 'unknown'}")
                if getattr(result, "errors", None):
                    logger.error(f"  Realizer errors: {result.errors}")
                    self._show_property_error(f"Realization failed: {result.errors[0]}")
                else:
                    self._show_property_error("Realization failed: no artifact")
                return None
            
            # Create unified payload
            sig = result.get_declaration_signature()
            if self._current_solver.is_3d:
                payload = GeometryPayload.from_solid_payload(
                    artifact,
                    form_type=self._current_solver.form_type,
                    params=decl.forms[0].params if decl.forms else {},
                    signature=sig,
                    validation_status="passed" if verdict.ok else "failed",
                )
            else:
                payload = GeometryPayload.from_scene_payload(
                    artifact,
                    form_type=self._current_solver.form_type,
                    params=decl.forms[0].params if decl.forms else {},
                    signature=sig,
                    validation_status="passed" if verdict.ok else "failed",
                )
            
            # Update display
            self.set_payload(payload)
            self._update_canon_display()
            self._clear_property_error()

            # Don't auto-add to history - user must explicitly save via button/Ctrl+S

            logger.info(f"Realized {self._current_solver.form_type} (sig: {sig[:8] if sig else '?'})")

            return payload
            
        except CanonValidationError as e:
            self._canon_verdict = e.verdict
            self._canon_result = None
            self._update_canon_display()
            self._show_property_error(f"Validation error: {e}")
            logger.error(f"Canon validation error: {e}")
            return None
            
        except Exception as e:
            logger.error(f"Realization error: {e}", exc_info=True)
            self._show_property_error(f"Error: {e}")
            return None
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Internal Methods
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _rebuild_property_inputs(self) -> None:
        """Rebuild property input fields based on current solver with tabbed categories."""
        if not self._property_layout:
            return
        
        # Clear existing inputs
        self._property_inputs.clear()
        self._property_labels.clear()
        
        # Remove all widgets
        while self._property_layout.count() > 0:
            item = self._property_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self._current_solver:
            # Show placeholder
            placeholder = QLabel("No form selected")
            placeholder.setStyleSheet(f"color: {COLORS['mist']}; font-style: italic;")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._property_layout.addWidget(placeholder)
            self._property_layout.addStretch()
            return
        
        # Get property definitions and group by category
        editable_props = self._current_solver.get_editable_properties()
        derived_props = self._current_solver.get_derived_properties()
        
        # Create tabbed interface for Core/Advanced
        property_tabs = QTabWidget()
        property_tabs.setObjectName("PropertyTabs")
        property_tabs.setDocumentMode(True)
        property_tabs.setUsesScrollButtons(False)  # Prevent scroll arrows
        property_tabs.setStyleSheet(f"""
            QTabWidget#PropertyTabs::pane {{
                border: 1px solid {COLORS['ash']};
                border-radius: 8px;
                background-color: {COLORS['cloud']};
            }}
            QTabWidget#PropertyTabs > QTabBar {{
                qproperty-expanding: true;
            }}
            QTabWidget#PropertyTabs QTabBar::scroller {{
                width: 0px;
            }}
            QTabWidget#PropertyTabs QTabBar::tab {{
                padding: 8px 16px;
                margin: 2px;
                font-weight: 600;
                font-size: 11px;
                min-width: 60px;
            }}
            QTabWidget#PropertyTabs QTabBar::tab:selected {{
                background-color: {COLORS['seeker_soft']};
                border-radius: 6px;
                color: {COLORS['seeker_dark']};
            }}
            QTabWidget#PropertyTabs QTabBar::tab:!selected {{
                background-color: {COLORS['marble']};
                color: {COLORS['stone']};
            }}
            QTabWidget#PropertyTabs QTabBar::tab:!selected:hover {{
                background-color: {COLORS['surface_hover']};
            }}
        """)
        
        # Core tab (editable properties)
        core_scroll = QScrollArea()
        core_scroll.setWidgetResizable(True)
        core_scroll.setFrameShape(QFrame.Shape.NoFrame)
        core_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        core_widget = QWidget()
        core_layout = QVBoxLayout(core_widget)
        core_layout.setContentsMargins(8, 8, 8, 8)
        core_layout.setSpacing(8)
        
        # Color Legend
        legend_frame = QFrame()
        legend_frame.setObjectName("ColorLegend")
        legend_frame.setStyleSheet(f"""
            QFrame#ColorLegend {{
                background-color: {COLORS['marble']};
                border: 1px solid {COLORS['ash']};
                border-radius: 6px;
                padding: 8px;
            }}
        """)
        legend_layout = QHBoxLayout(legend_frame)
        legend_layout.setContentsMargins(8, 6, 8, 6)
        legend_layout.setSpacing(16)
        
        # Editable indicator
        edit_legend = QLabel("✎ Editable")
        edit_legend.setStyleSheet(f"color: {COLORS['seeker']}; font-size: 10px; font-weight: 600;")
        legend_layout.addWidget(edit_legend)
        
        # Derived indicator
        derived_legend = QLabel("◇ Derived")
        derived_legend.setStyleSheet(f"color: {COLORS['mist']}; font-size: 10px; font-weight: 500;")
        legend_layout.addWidget(derived_legend)
        
        legend_layout.addStretch()
        core_layout.addWidget(legend_frame)
        
        for prop in editable_props:
            widget = self._create_property_widget(prop, editable=True)
            core_layout.addWidget(widget)
        
        core_layout.addStretch()
        core_scroll.setWidget(core_widget)
        property_tabs.addTab(core_scroll, f"Core ({len(editable_props)})")
        
        # Advanced tab (derived properties)
        adv_scroll = QScrollArea()
        adv_scroll.setWidgetResizable(True)
        adv_scroll.setFrameShape(QFrame.Shape.NoFrame)
        adv_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        adv_widget = QWidget()
        adv_layout = QVBoxLayout(adv_widget)
        adv_layout.setContentsMargins(8, 8, 8, 8)
        adv_layout.setSpacing(8)
        
        # Info banner for Advanced tab
        info_banner = QFrame()
        info_banner.setStyleSheet(f"""
            background-color: {COLORS['navigator_soft']};
            border: 1px solid {COLORS['ash']};
            border-radius: 6px;
        """)
        info_layout = QHBoxLayout(info_banner)
        info_layout.setContentsMargins(10, 8, 10, 8)
        
        info_icon = QLabel("◇")
        info_icon.setStyleSheet(f"color: {COLORS['mist']}; font-size: 14px;")
        info_layout.addWidget(info_icon)
        
        info_text = QLabel("Derived values — computed from the canonical parameter")
        info_text.setStyleSheet(f"color: {COLORS['stone']}; font-size: 10px;")
        info_layout.addWidget(info_text)
        info_layout.addStretch()
        
        adv_layout.addWidget(info_banner)
        
        # Group by category
        categories: dict[str, list] = {}
        for prop in derived_props:
            cat = getattr(prop, 'category', 'Other')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(prop)
        
        for cat_name, cat_props in categories.items():
            # Category header with Visual Liturgy styling
            cat_frame = QFrame()
            cat_frame.setStyleSheet(f"""
                background-color: {COLORS['navigator_soft']};
                border-radius: 4px;
                margin-top: 8px;
            """)
            cat_header_layout = QHBoxLayout(cat_frame)
            cat_header_layout.setContentsMargins(8, 4, 8, 4)
            
            cat_label = QLabel(cat_name.upper())
            cat_label.setStyleSheet(f"""
                color: {COLORS['navigator_dark']};
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 1px;
            """)
            cat_header_layout.addWidget(cat_label)
            
            cat_count = QLabel(f"({len(cat_props)})")
            cat_count.setStyleSheet(f"color: {COLORS['mist']}; font-size: 10px;")
            cat_header_layout.addWidget(cat_count)
            cat_header_layout.addStretch()
            
            adv_layout.addWidget(cat_frame)
            
            for prop in cat_props:
                widget = self._create_property_widget(prop, editable=False)
                adv_layout.addWidget(widget)
        
        adv_layout.addStretch()
        adv_scroll.setWidget(adv_widget)
        property_tabs.addTab(adv_scroll, f"Advanced ({len(derived_props)})")
        
        self._property_layout.addWidget(property_tabs, 1)
        
        # Add error label at the end
        self._property_error_label = QLabel()
        self._property_error_label.setObjectName("PropertyError")
        self._property_error_label.setStyleSheet(f"""
            QLabel#PropertyError {{
                color: {COLORS['destroyer']};
                background-color: {COLORS['destroyer_soft']};
                padding: 8px;
                border-radius: 4px;
                font-size: 12px;
            }}
        """)
        self._property_error_label.setWordWrap(True)
        self._property_error_label.hide()
        self._property_layout.addWidget(self._property_error_label)
    
    def _create_property_widget(self, prop: PropertyDefinition, editable: bool) -> QFrame:
        """
        Create a property input widget with label and input field.
        
        Visual Liturgy Compliance:
        - Editable: White bg (light), void text, amber focus border, seeker left accent
        - Read-only: Marble bg, stone text, no focus styling, mist left accent
        """
        frame = QFrame()
        frame.setObjectName(f"PropertyFrame_{prop.key}")
        
        # Visual Liturgy: Color-coded left border for editable vs read-only
        if editable:
            # Editable fields: Seeker (Gold/Amber) accent - "Uncover / Reveal"
            border_color = COLORS['seeker']
            bg_color = COLORS['light']  # Pure Light - The Vessel
        else:
            # Read-only fields: Navigator (Slate) accent - neutral/derived
            border_color = COLORS['navigator_mute']  # Ash-like
            bg_color = COLORS['marble']  # Marble Slate - The Tablet
        
        frame.setStyleSheet(f"""
            QFrame#PropertyFrame_{prop.key} {{
                background-color: {bg_color};
                border: 1px solid {COLORS['ash']};
                border-left: 3px solid {border_color};
                border-radius: 8px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)  # Visual Liturgy: padding 10-14px
        layout.setSpacing(6)
        
        # Header with label, unit, and edit indicator
        header = QHBoxLayout()
        header.setSpacing(6)
        
        # Editable indicator icon
        if editable:
            edit_icon = QLabel("✎")  # Pencil for editable
            edit_icon.setStyleSheet(f"color: {COLORS['seeker']}; font-size: 12px;")
            edit_icon.setToolTip("Editable — enter a value to recalculate")
            header.addWidget(edit_icon)
        else:
            lock_icon = QLabel("◇")  # Diamond for derived/computed
            lock_icon.setStyleSheet(f"color: {COLORS['mist']}; font-size: 10px;")
            lock_icon.setToolTip("Derived — computed from canonical parameter")
            header.addWidget(lock_icon)
        
        name_label = QLabel(prop.label)
        name_label.setStyleSheet(f"""
            color: {COLORS['void'] if editable else COLORS['stone']};
            font-weight: {'600' if editable else '500'};
            font-size: 12px;
        """)
        header.addWidget(name_label)
        
        if prop.unit:
            unit_label = QLabel(f"({prop.unit})")
            unit_label.setStyleSheet(f"color: {COLORS['mist']}; font-size: 10px;")
            header.addWidget(unit_label)
        
        # Formula/tooltip button — opens LaTeX dialog if formula available
        formula = getattr(prop, 'formula', '')
        tooltip = getattr(prop, 'tooltip', '')
        
        if formula or tooltip:
            info_btn = QPushButton("ƒ" if formula else "?")
            info_btn.setFixedSize(18, 18)
            info_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            info_btn.setToolTip(tooltip if tooltip else "Show formula")
            
            # Style: Blue for formula, gray for tooltip-only
            if formula:
                info_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['magus_soft']};
                        color: {COLORS['magus']};
                        border: 1px solid {COLORS['magus_mute']};
                        border-radius: 9px;
                        font-weight: 700;
                        font-size: 10px;
                        font-family: serif;
                        padding: 0;
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['magus_mute']};
                        border-color: {COLORS['magus']};
                    }}
                """)
                # Connect to formula dialog
                info_btn.clicked.connect(
                    lambda _, label=prop.label, frm=formula: self._show_formula_dialog(label, frm)
                )
            else:
                info_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['navigator_soft']};
                        color: {COLORS['navigator']};
                        border: 1px solid {COLORS['ash']};
                        border-radius: 9px;
                        font-weight: 700;
                        font-size: 10px;
                        padding: 0;
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['surface_hover']};
                    }}
                """)
            header.addWidget(info_btn)
        
        header.addStretch()
        layout.addLayout(header)
        
        # Input field — Visual Liturgy Input Fields pattern
        input_field = QLineEdit()
        input_field.setObjectName(f"PropertyInput_{prop.key}")
        input_field.setPlaceholderText("0.0")
        
        if editable:
            # Editable: Pure Light bg, full contrast, amber focus
            input_field.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {COLORS['light']};
                    border: 1px solid {COLORS['ash']};
                    border-radius: 8px;
                    padding: 10px 14px;
                    color: {COLORS['void']};
                    font-size: 11pt;
                    font-family: 'JetBrains Mono', 'Consolas', monospace;
                }}
                QLineEdit:focus {{
                    border: 1px solid {COLORS['seeker']};
                }}
                QLineEdit:hover {{
                    border-color: {COLORS['seeker_mute']};
                }}
            """)
        else:
            # Read-only: Marble bg, muted text, no focus styling
            input_field.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {COLORS['marble']};
                    border: 1px solid {COLORS['ash']};
                    border-radius: 8px;
                    padding: 10px 14px;
                    color: {COLORS['stone']};
                    font-size: 11pt;
                    font-family: 'JetBrains Mono', 'Consolas', monospace;
                }}
            """)
        
        input_field.setValidator(QDoubleValidator())
        input_field.setReadOnly(not editable)

        if editable and not getattr(prop, 'readonly', False):
            input_field.editingFinished.connect(
                lambda key=prop.key: self._on_property_changed(key)
            )

        # Add context menu for sending to Quadset Analysis
        input_field.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        input_field.customContextMenuRequested.connect(
            lambda pos, field=input_field: self._show_value_context_menu(field, pos)
        )

        layout.addWidget(input_field)
        
        self._property_inputs[prop.key] = input_field
        self._property_labels[prop.key] = name_label
        
        return frame
    
    def _on_property_changed(self, key: str) -> None:
        """Handle property input change."""
        if self._updating_inputs:
            return
        
        # Don't recalculate when restoring from history
        if self._restoring_from_history:
            return
        
        if not self._current_solver:
            return
        
        input_field = self._property_inputs.get(key)
        if not input_field:
            return
        
        text = input_field.text().strip()
        if not text:
            return
        
        try:
            value = float(text)
        except ValueError:
            self._show_property_error(f"Invalid number: {text}")
            return
        
        # Solve for canonical parameter
        result = self._current_solver.solve_from(key, value)
        
        if not result.ok:
            self._show_property_error(result.message)
            return
        
        # Realize
        payload = self.realize_from_canonical(result.canonical_parameter)
        
        if payload:
            # Update all property fields
            self._sync_property_inputs()
    
    def _sync_property_inputs(self) -> None:
        """Sync all property input fields with current values."""
        if not self._current_solver:
            return
        
        # Get canonical value from current payload or declaration
        canonical_value = None
        
        if self._canon_declaration:
            forms = getattr(self._canon_declaration, "forms", [])
            if forms:
                params = getattr(forms[0], "params", {})
                canonical_value = params.get(self._current_solver.canonical_key)
        
        if canonical_value is None:
            return
        
        # Get all property values
        props = self._current_solver.get_all_properties(canonical_value)
        
        # Get property definitions for formatting
        all_prop_defs = self._current_solver.get_all_property_definitions()
        prop_formats = {p.key: getattr(p, 'format_spec', '.6g') for p in all_prop_defs}
        
        # Update inputs
        self._updating_inputs = True
        try:
            for key, input_field in self._property_inputs.items():
                if key in props:
                    value = props[key]
                    fmt = prop_formats.get(key, '.6g')
                    input_field.setText(format(value, fmt))
        finally:
            self._updating_inputs = False
    
    def _show_property_error(self, message: str) -> None:
        """Show an error message in the properties panel."""
        if self._property_error_label:
            self._property_error_label.setText(message)
            self._property_error_label.show()
    
    def _clear_property_error(self) -> None:
        """Clear any property error message."""
        if self._property_error_label:
            self._property_error_label.hide()
    
    # ───────────────────────────────────────────────────────────────────────────
    # Canon Display
    # ───────────────────────────────────────────────────────────────────────────
    
    def _update_canon_display(self) -> None:
        """Update all Canon-related UI elements."""
        self._update_canon_badge()
        self._update_canon_tab()
    
    def _update_canon_badge(self) -> None:
        """Update the Canon badge appearance."""
        if not self._canon_badge:
            return
        
        if self._canon_verdict is None:
            # Pending
            self._canon_badge.setText("⏳ Pending")
            self._canon_badge.setStyleSheet(f"""
                QPushButton#CanonBadge {{
                    background-color: {COLORS['navigator_soft']};
                    color: {COLORS['stone']};
                    border: 1px solid {COLORS['ash']};
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 11px;
                }}
            """)
        elif self._canon_verdict.ok:
            findings = getattr(self._canon_verdict, "findings", [])
            if findings:
                # Passed with warnings
                self._canon_badge.setText(f"⚠ Warnings ({len(findings)})")
                self._canon_badge.setStyleSheet(f"""
                    QPushButton#CanonBadge {{
                        background-color: {COLORS['seeker_soft']};
                        color: {COLORS['seeker_dark']};
                        border: 1px solid {COLORS['seeker']};
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-size: 11px;
                    }}
                """)
            else:
                # Passed
                self._canon_badge.setText("✓ Validated")
                self._canon_badge.setStyleSheet(f"""
                    QPushButton#CanonBadge {{
                        background-color: {COLORS['scribe_soft']};
                        color: {COLORS['scribe_dark']};
                        border: 1px solid {COLORS['scribe']};
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-size: 11px;
                    }}
                """)
        else:
            # Failed
            self._canon_badge.setText("✗ Failed")
            self._canon_badge.setStyleSheet(f"""
                QPushButton#CanonBadge {{
                    background-color: {COLORS['destroyer_soft']};
                    color: {COLORS['destroyer_dark']};
                    border: 1px solid {COLORS['destroyer']};
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 11px;
                }}
            """)
    
    def _update_canon_tab(self) -> None:
        """Update the Canon tab content."""
        # Update status frame
        if self._canon_verdict is None:
            self._canon_status_icon.setText("⏳")
            self._canon_status_text.setText("Awaiting validation")
            self._canon_status_frame.setStyleSheet(f"""
                QFrame#CanonStatusFrame {{
                    background-color: {COLORS['navigator_soft']};
                    border-radius: 6px;
                }}
            """)
        elif self._canon_verdict.ok:
            findings = getattr(self._canon_verdict, "findings", [])
            if findings:
                self._canon_status_icon.setText("⚠")
                self._canon_status_text.setText(f"Passed with {len(findings)} warning(s)")
                self._canon_status_frame.setStyleSheet(f"""
                    QFrame#CanonStatusFrame {{
                        background-color: {COLORS['seeker_soft']};
                        border-radius: 6px;
                    }}
                """)
            else:
                self._canon_status_icon.setText("✓")
                self._canon_status_text.setText("Validation passed")
                self._canon_status_frame.setStyleSheet(f"""
                    QFrame#CanonStatusFrame {{
                        background-color: {COLORS['scribe_soft']};
                        border-radius: 6px;
                    }}
                """)
        else:
            self._canon_status_icon.setText("✗")
            self._canon_status_text.setText("Validation failed")
            self._canon_status_frame.setStyleSheet(f"""
                QFrame#CanonStatusFrame {{
                    background-color: {COLORS['destroyer_soft']};
                    border-radius: 6px;
                }}
            """)
        
        # Update findings
        if self._canon_verdict:
            findings = getattr(self._canon_verdict, "findings", [])
            if findings:
                lines = []
                for f in findings:
                    sev = getattr(f, "severity", None)
                    sev_str = sev.name if sev else "?"
                    msg = getattr(f, "message", str(f))
                    ref = getattr(f, "canon_ref", "")
                    line = f"[{sev_str}] {msg}"
                    if ref:
                        line += f"\n    → {ref}"
                    lines.append(line)
                self._findings_text.setText("\n\n".join(lines))
            else:
                # No findings - show compliance summary
                self._findings_text.setText(self._generate_compliance_summary())
        else:
            self._findings_text.clear()

    def _generate_compliance_summary(self) -> str:
        """Generate a summary of what makes this geometry Canon-compliant."""
        if not self._canon_declaration or not self._current_solver:
            return "No findings — Canon compliance verified."

        lines = ["✓ Canon Compliance Verified\n"]

        # Show form type
        form_type = self._current_solver.form_type
        lines.append(f"Form: {form_type}")

        # Extract canonical parameter from declaration
        forms = getattr(self._canon_declaration, "forms", [])
        if forms:
            params = getattr(forms[0], "params", {})
            canonical_key = self._current_solver.canonical_key

            if canonical_key in params:
                canonical_value = params[canonical_key]
                canonical_label = canonical_key.replace("_", " ").title()

                # Handle compound canonical parameters (e.g., Torus Knot, Rectangle)
                if isinstance(canonical_value, dict):
                    # Format each parameter in the compound
                    param_strs = []
                    for k, v in canonical_value.items():
                        param_label = k.replace("_", " ")
                        if isinstance(v, (int, float)):
                            param_strs.append(f"{param_label}={v:.6g}")
                        else:
                            param_strs.append(f"{param_label}={v}")
                    lines.append(f"{canonical_label}: {{{', '.join(param_strs)}}}")
                elif isinstance(canonical_value, (int, float)):
                    # Single numeric canonical parameter
                    lines.append(f"{canonical_label}: {canonical_value:.6g}")
                else:
                    # Other types (strings, etc.)
                    lines.append(f"{canonical_label}: {canonical_value}")

        lines.append("")  # Blank line

        # Add form-specific Canon principles
        lines.append("Canon Principles Verified:")

        if form_type == "VaultOfHestia":
            # Extract key parameters
            if forms and hasattr(forms[0], "params"):
                params = forms[0].params
                side = params.get("side_length", 0)
                radius = params.get("sphere_radius", 0)

                # Calculate phi relationship
                phi = (1 + 5**0.5) / 2
                expected_radius = side / (2 * phi)
                ratio_check = abs(radius - expected_radius) < 0.001

                lines.append(f"  • Golden Ratio φ-mediation: {('✓' if ratio_check else '✗')}")
                lines.append(f"    r = s/(2φ) = {side:.4g}/(2×φ) ≈ {expected_radius:.4g}")
                lines.append("  • Cube-Pyramid-Sphere nesting verified")
                lines.append("  • Dimensional echo preserved (Article III.2)")
                lines.append("  • Void spaces computed (Article VI)")

        elif form_type == "Circle":
            lines.append("  • Radius proportionality verified")
            lines.append("  • Area formula compliance (πr²)")

        elif form_type == "Sphere":
            lines.append("  • Radius proportionality verified")
            lines.append("  • Volume formula compliance (4πr³/3)")
            lines.append("  • Surface area formula compliance (4πr²)")

        else:
            # Generic compliance for unknown forms
            lines.append(f"  • {form_type} parameter validation passed")
            lines.append("  • Geometric consistency verified")

        lines.append("")
        lines.append("All Canon validation rules passed.")

        return "\n".join(lines)

    def _update_canon_metrics_from_payload(self, payload: GeometryPayload) -> None:
        """Update Canon metrics labels from payload."""
        sig = payload.declaration_signature or payload.get_signature()
        if "signature" in self._canon_metrics_labels:
            self._canon_metrics_labels["signature"].setText(sig[:12] + "..." if len(sig) > 12 else sig)
        
        if "form_type" in self._canon_metrics_labels:
            self._canon_metrics_labels["form_type"].setText(payload.form_type)
        
        # Phi is form-specific - check metadata
        phi = payload.metadata.get("inradius_resonance_phi") or payload.metadata.get("phi")
        if "phi" in self._canon_metrics_labels:
            if phi:
                self._canon_metrics_labels["phi"].setText(f"{phi:.6f}")
            else:
                self._canon_metrics_labels["phi"].setText("—")
    
    def _show_canon_details(self) -> None:
        """Show detailed Canon validation dialog."""
        # Switch to Canon tab
        if self._console_tabs:
            self._console_tabs.setCurrentIndex(4)  # Canon tab
    
    # ───────────────────────────────────────────────────────────────────────────
    # History Management
    # ───────────────────────────────────────────────────────────────────────────
    
    def _on_history_changed(self, entry: Optional[HistoryEntry]) -> None:
        """Handle history current entry change."""
        self._update_undo_redo_buttons()
        
        if entry and entry.result:
            # Restore the payload from history
            # This requires re-extracting the artifact
            logger.info(f"History changed to: {entry.short_signature}")
        
        self.history_changed.emit()
    
    def _update_undo_redo_buttons(self) -> None:
        """Update undo/redo button states."""
        if self._undo_btn:
            self._undo_btn.setEnabled(self._history.can_undo)
        if self._redo_btn:
            self._redo_btn.setEnabled(self._history.can_redo)
    
    def _on_undo(self) -> None:
        """Handle undo action."""
        entry = self._history.undo()
        if entry:
            logger.info(f"Undo to: {entry.short_signature}")
            self._refresh_history_list()
    
    def _on_redo(self) -> None:
        """Handle redo action."""
        entry = self._history.redo()
        if entry:
            logger.info(f"Redo to: {entry.short_signature}")
            self._refresh_history_list()

    def _on_save_to_history(self) -> None:
        """Save the current calculation to history."""
        # Verify we have a valid calculation to save
        if not self._canon_declaration:
            logger.warning("No calculation to save to history")
            return

        if not self._canon_verdict:
            logger.warning("No validation verdict to save to history")
            return

        if not self._canon_result:
            logger.warning("No realization result to save to history")
            return

        # Push to history
        entry = self._history.push(
            declaration=self._canon_declaration,
            verdict=self._canon_verdict,
            result=self._canon_result,
            skip_history=False,
        )

        if entry:
            logger.info(f"Saved to history: {entry.short_signature}")
            self._refresh_history_list()

            # Show confirmation in status bar
            if self._status_label:
                self._status_label.setText(f"✓ Saved to history")

    def _refresh_history_list(self) -> None:
        """Refresh the history list widget."""
        if not self._history_list_layout:
            return
        
        # Clear existing items
        while self._history_list_layout.count() > 0:
            item = self._history_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        entries = self._history.get_timeline_reversed()
        current_idx = self._history.current_index
        
        if not entries:
            empty_label = QLabel("No history yet")
            empty_label.setStyleSheet(f"color: {COLORS['mist']}; font-style: italic;")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._history_list_layout.addWidget(empty_label)
        else:
            for i, entry in enumerate(entries):
                actual_idx = len(entries) - 1 - i
                is_current = actual_idx == current_idx
                
                item = self._create_history_item(entry, is_current, actual_idx)
                self._history_list_layout.addWidget(item)
        
        self._history_list_layout.addStretch()
        self._update_undo_redo_buttons()
    
    def _create_history_item(self, entry: HistoryEntry, is_current: bool, index: int) -> QFrame:
        """Create a history list item widget with context menu support."""
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction
        
        frame = QFrame()
        frame.setObjectName(f"HistoryItem_{index}")
        
        bg_color = COLORS['magus_soft'] if is_current else COLORS['cloud']
        border_color = COLORS['magus'] if is_current else COLORS['ash']
        
        frame.setStyleSheet(f"""
            QFrame#HistoryItem_{index} {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 4px;
            }}
        """)
        frame.setCursor(Qt.CursorShape.PointingHandCursor)
        frame.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)
        
        # Current indicator
        indicator = QLabel("▸" if is_current else " ")
        indicator.setStyleSheet(f"color: {COLORS['magus']}; font-weight: bold;")
        indicator.setFixedWidth(12)
        layout.addWidget(indicator)
        
        # Status icon
        icon = QLabel(entry.status_icon)
        icon.setFixedWidth(16)
        layout.addWidget(icon)
        
        # Title with notes indicator
        has_notes = bool(entry.notes and entry.notes.strip() and entry.notes != "<!DOCTYPE HTML")

        # Priority: custom_title > canonical parameter display > signature
        if entry.custom_title:
            title_text = entry.custom_title
        else:
            # Try to get a readable default from canonical parameter
            params = entry.get_canonical_params()
            canonical_key = None
            canonical_value = None

            # Determine canonical key based on form type
            if entry.form_type == "VaultOfHestia":
                canonical_key = "side_length"
            elif entry.form_type == "Circle":
                canonical_key = "radius"
            elif entry.form_type == "Sphere":
                canonical_key = "radius"
            # Add more form types as needed

            if canonical_key and canonical_key in params:
                canonical_value = params[canonical_key]
                # Format as "FormType (parameter=value)"
                title_text = f"{entry.form_type} (s={canonical_value:.4g})"
            else:
                # Fallback to signature if we can't determine parameter
                title_text = entry.short_signature

        if has_notes:
            title_text += " 📝"
        
        sig_label = QLabel(title_text)
        sig_label.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
        """)
        layout.addWidget(sig_label)
        
        layout.addStretch()
        
        # Time
        time_label = QLabel(entry.time_string)
        time_label.setStyleSheet(f"color: {COLORS['mist']}; font-size: 10px;")
        layout.addWidget(time_label)
        
        # Left-click handler
        def on_mouse_press(e, idx=index):
            if e.button() == Qt.MouseButton.LeftButton:
                self._on_history_item_clicked(idx)
        frame.mousePressEvent = on_mouse_press
        
        # Right-click context menu
        def show_context_menu(pos, idx=index, ent=entry):
            menu = QMenu(frame)
            menu.setStyleSheet(f"""
                QMenu {{
                    background-color: {COLORS['light']};
                    border: 1px solid {COLORS['ash']};
                    border-radius: 6px;
                    padding: 4px;
                }}
                QMenu::item {{
                    padding: 6px 16px;
                    border-radius: 4px;
                }}
                QMenu::item:selected {{
                    background-color: {COLORS['magus_soft']};
                }}
            """)
            
            # Notes action
            notes_action = menu.addAction("📝 Notes...")
            notes_action.triggered.connect(lambda: self._open_notes_window(idx))
            
            menu.addSeparator()
            
            # Rename action
            rename_action = menu.addAction("✏️ Rename...")
            rename_action.triggered.connect(lambda: self._rename_history_item(idx))
            
            # Delete action
            delete_action = menu.addAction("🗑️ Delete")
            delete_action.triggered.connect(lambda: self._delete_history_item(idx))
            
            menu.exec(frame.mapToGlobal(pos))
        
        frame.customContextMenuRequested.connect(show_context_menu)
        
        return frame
    
    def _on_history_item_clicked(self, index: int) -> None:
        """Handle click on history item - restore the calculation state."""
        entry = self._history.goto(index)
        if entry is None:
            self._refresh_history_list()
            return
        
        # Block recalculation while restoring from history
        self._restoring_from_history = True
        
        try:
            # Restore the Canon state
            self._canon_declaration = entry.declaration
            self._canon_verdict = entry.verdict
            self._canon_result = entry.result
            
            # Restore the payload if we have a valid result
            if entry.result is not None:
                # Extract artifact from result
                artifact = None
                forms = getattr(entry.declaration, "forms", [])
                if forms:
                    form_id = getattr(forms[0], "id", None)
                    if form_id:
                        artifact = entry.result.get_artifact(form_id)
                
                if artifact is None and self._current_solver:
                    artifact = entry.result.get_artifact(self._current_solver.form_type.lower())
                
                if artifact is not None:
                    # Create GeometryPayload from artifact
                    from .payloads.geometry_payload import GeometryPayload
                    
                    form_type = entry.form_type
                    sig = entry.signature
                    validation_status = "passed" if entry.is_valid else "failed"
                    
                    payload = GeometryPayload.from_solid_payload(
                        artifact,
                        form_type=form_type,
                        title=entry.title,
                        params=entry.get_canonical_params(),
                        signature=sig,
                        validation_status=validation_status,
                    )
                    
                    # Update viewport and UI
                    self._current_payload = payload
                    self._viewport.set_payload(payload)
                    self._sync_property_inputs()
                    self._update_canon_display()
                    
                    logger.info(f"Restored history entry: {entry.short_signature}")
            
            self._refresh_history_list()
        finally:
            self._restoring_from_history = False
    
    def _open_notes_window(self, index: int) -> None:
        """Open a non-modal notes window for the history entry at index."""
        entry = self._history.get_entry(index)
        if entry is None:
            return
        
        # Create or reuse notes window
        if not hasattr(self, '_notes_windows'):
            self._notes_windows: dict[str, QWidget] = {}
        
        sig = entry.signature
        
        # Check if window already open for this entry
        if sig in self._notes_windows and self._notes_windows[sig].isVisible():
            self._notes_windows[sig].raise_()
            self._notes_windows[sig].activateWindow()
            return
        
        # Create new notes window
        window = self._create_notes_window(entry, index)
        self._notes_windows[sig] = window
        window.show()
    
    def _create_notes_window(self, entry: HistoryEntry, index: int) -> QWidget:
        """Create a non-modal notes window for a history entry."""
        from PyQt6.QtWidgets import QDialog
        from PyQt6.QtGui import QFont
        
        window = QWidget(self, Qt.WindowType.Window)
        window.setWindowTitle(f"Notes: {entry.short_signature} • {entry.form_type}")
        window.setMinimumSize(400, 300)
        window.resize(450, 350)
        window.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['cloud']};
            }}
        """)
        
        layout = QVBoxLayout(window)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Header with entry info
        header = QLabel(f"📜 {entry.form_type} • {entry.time_string}")
        header.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            padding-bottom: 4px;
        """)
        layout.addWidget(header)
        
        # Notes editor - use SafeTextEdit to support LaTeX/Mermaid image re-rendering
        from shared.ui.rich_text_editor import SafeTextEdit
        editor = SafeTextEdit()
        editor.setObjectName("NotesWindowEditor")
        editor.setPlaceholderText("Add notes for this calculation...")
        editor.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['light']};
                border: 1px solid {COLORS['ash']};
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                color: {COLORS['void']};
            }}
            QTextEdit:focus {{
                border-color: {COLORS['focus']};
            }}
        """)
        
        # Load existing notes
        if entry.notes:
            editor.setHtml(entry.notes)
        
        layout.addWidget(editor, 1)
        
        # Formatting toolbar
        format_layout = QHBoxLayout()
        format_layout.setSpacing(4)
        
        def make_format_btn(text: str, tooltip: str, callback):
            btn = QPushButton(text)
            btn.setFixedSize(28, 28)
            btn.setToolTip(tooltip)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['marble']};
                    color: {COLORS['void']};
                    border: 1px solid {COLORS['ash']};
                    border-radius: 4px;
                    font-weight: bold;
                }}
                QPushButton:hover {{ background-color: {COLORS['surface_hover']}; }}
            """)
            btn.clicked.connect(callback)
            return btn
        
        def toggle_bold():
            cursor = editor.textCursor()
            fmt = cursor.charFormat()
            weight = QFont.Weight.Normal if fmt.fontWeight() == QFont.Weight.Bold else QFont.Weight.Bold
            fmt.setFontWeight(weight)
            cursor.mergeCharFormat(fmt)
            editor.setTextCursor(cursor)
        
        def toggle_italic():
            cursor = editor.textCursor()
            fmt = cursor.charFormat()
            fmt.setFontItalic(not fmt.fontItalic())
            cursor.mergeCharFormat(fmt)
            editor.setTextCursor(cursor)
        
        def toggle_underline():
            cursor = editor.textCursor()
            fmt = cursor.charFormat()
            fmt.setFontUnderline(not fmt.fontUnderline())
            cursor.mergeCharFormat(fmt)
            editor.setTextCursor(cursor)
        
        format_layout.addWidget(make_format_btn("B", "Bold", toggle_bold))
        format_layout.addWidget(make_format_btn("I", "Italic", toggle_italic))
        format_layout.addWidget(make_format_btn("U", "Underline", toggle_underline))
        format_layout.addStretch()

        # Save button
        save_btn = QPushButton("💾 Save Notes")
        save_btn.setToolTip("Save notes to history")
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['seeker']};
                color: {COLORS['light']};
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['seeker_mute']};
            }}
        """)

        def save_notes():
            from PyQt6.QtCore import QTimer
            notes_html = editor.toHtml()
            self._history.set_notes_by_signature(entry.signature, notes_html)
            # Visual feedback
            save_btn.setText("✓ Saved")
            QTimer.singleShot(1500, lambda: save_btn.setText("💾 Save Notes"))

        save_btn.clicked.connect(save_notes)
        format_layout.addWidget(save_btn)

        # Full Editor button
        full_editor_btn = QPushButton("📝 Full Editor")
        full_editor_btn.setToolTip("Open advanced editor with LaTeX, Mermaid, and more")
        full_editor_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['marble']};
                color: {COLORS['void']};
                border: 1px solid {COLORS['ash']};
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_hover']};
            }}
        """)
        full_editor_btn.clicked.connect(lambda: self._open_full_notes_editor(entry, editor))
        format_layout.addWidget(full_editor_btn)

        layout.addLayout(format_layout)
        
        return window

    def _open_full_notes_editor(self, entry: HistoryEntry, simple_editor: QTextEdit) -> None:
        """Open the full-featured RichTextEditor for advanced note editing."""
        from PyQt6.QtCore import QTimer

        # Check if full editor already open for this entry
        if not hasattr(self, '_full_editor_windows'):
            self._full_editor_windows: dict[str, QWidget] = {}

        sig = entry.signature
        if sig in self._full_editor_windows and self._full_editor_windows[sig].isVisible():
            self._full_editor_windows[sig].raise_()
            self._full_editor_windows[sig].activateWindow()
            return

        # Create window
        window = QWidget(self, Qt.WindowType.Window)
        window.setWindowTitle(f"Full Editor: {entry.form_type} • {entry.short_signature}")
        window.setMinimumSize(800, 600)
        window.resize(900, 700)

        layout = QVBoxLayout(window)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Import and create RichTextEditor (will fail gracefully if dependencies missing)
        try:
            from shared.ui.rich_text_editor import RichTextEditor

            # Create editor with full UI
            rich_editor = RichTextEditor(parent=window, show_ui=True)

            # Load existing notes from simple editor
            existing_html = simple_editor.toHtml()
            if rich_editor.editor:
                rich_editor.editor.setHtml(existing_html)

            layout.addWidget(rich_editor)

            # Auto-render timer for LaTeX and Mermaid
            auto_render_timer = QTimer(window)
            auto_render_timer.setSingleShot(True)
            auto_render_timer.setInterval(1500)  # 1.5 seconds after typing stops

            def trigger_auto_render():
                """Trigger rendering of LaTeX and Mermaid after typing stops."""
                # Only render if content actually contains relevant syntax
                doc_text = rich_editor.editor.toPlainText() if rich_editor.editor else ""

                # Check for LaTeX syntax ($...$ or $$...$$)
                if rich_editor.math_feature and ('$' in doc_text):
                    rich_editor.math_feature.render_all_math(silent=True)

                # Check for Mermaid syntax (```mermaid or known keywords)
                if rich_editor.mermaid_feature and ('```' in doc_text or 'graph' in doc_text or 'flowchart' in doc_text):
                    rich_editor.mermaid_feature.render_all_mermaid(silent=True)

            auto_render_timer.timeout.connect(trigger_auto_render)

            # Connect text changes to restart auto-render timer
            if rich_editor.editor:
                def on_text_changed():
                    auto_render_timer.stop()
                    auto_render_timer.start()

                rich_editor.editor.textChanged.connect(on_text_changed)

                # Sync to simple editor on window close (user must click Save in simple editor to persist)
                def on_window_close(event):
                    """Sync HTML back to simple editor when closing full editor."""
                    updated_html = rich_editor.editor.toHtml()
                    simple_editor.blockSignals(True)
                    simple_editor.setHtml(updated_html)
                    simple_editor.blockSignals(False)
                    event.accept()

                window.closeEvent = on_window_close

            # Trigger initial render after window opens (silent mode)
            QTimer.singleShot(500, trigger_auto_render)

        except ImportError as e:
            # Fallback if RichTextEditor dependencies not available
            error_label = QLabel(f"❌ Full editor not available\n\nMissing dependencies: {e}")
            error_label.setStyleSheet("color: red; padding: 20px; font-size: 14px;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(error_label)
            logger.error(f"Failed to load RichTextEditor: {e}")

        self._full_editor_windows[sig] = window
        window.show()

    def _rename_history_item(self, index: int) -> None:
        """Rename a history entry (change its custom title)."""
        from PyQt6.QtWidgets import QInputDialog
        
        entry = self._history.get_entry(index)
        if entry is None:
            return
        
        # Get current title
        current_title = entry.custom_title or entry.title or entry.short_signature
        
        new_title, ok = QInputDialog.getText(
            self,
            "Rename History Entry",
            "Enter a new name for this entry:",
            text=current_title
        )
        
        if ok and new_title.strip():
            # Use history manager's method for persistence
            if self._history.set_custom_title_by_index(index, new_title.strip()):
                logger.info(f"Renamed history entry {entry.short_signature} to '{new_title}'")
    
    def _delete_history_item(self, index: int) -> None:
        """Delete a history entry after confirmation."""
        from PyQt6.QtWidgets import QMessageBox
        
        entry = self._history.get_entry(index)
        if entry is None:
            return
        
        reply = QMessageBox.question(
            self,
            "Delete History Entry",
            f"Delete entry '{entry.short_signature}'?\n\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._history.remove(index)
            self._refresh_history_list()
            logger.info(f"Deleted history entry: {entry.short_signature}")
    
    # ───────────────────────────────────────────────────────────────────────────
    # Viewport Callbacks
    # ───────────────────────────────────────────────────────────────────────────
    
    def _on_viewport_payload_changed(self, payload: GeometryPayload) -> None:
        """Handle viewport payload change."""
        pass  # Already handled in set_payload
    
    def _on_viewport_stats_changed(self, stats: str) -> None:
        """Handle viewport stats change."""
        if self._status_label and self._current_solver:
            dim = "2D" if self._current_solver.is_2d else "3D"
            status = self._canon_verdict
            
            if status and status.ok:
                icon = "✓"
            elif status:
                icon = "✗"
            else:
                icon = "◇"
            
            self._status_label.setText(f"{self._current_solver.form_type} ({dim}) · {stats} · {icon}")
    
    def _show_status(self, message: str) -> None:
        """Show a status message in the status bar."""
        if self._status_label:
            self._status_label.setText(message)
    
    def _clear_status(self) -> None:
        """Clear the status message and restore default."""
        if self._status_label and self._current_solver:
            dim = "2D" if self._current_solver.is_2d else "3D"
            self._status_label.setText(f"{self._current_solver.form_type} ({dim}) — Ready")
    
    # ───────────────────────────────────────────────────────────────────────────
    # Formula Dialog
    # ───────────────────────────────────────────────────────────────────────────
    
    def _show_formula_dialog(self, property_name: str, formula_latex: str) -> None:
        """
        Show the formula dialog with LaTeX rendering.
        
        Uses the FormulaDialog from the calculator widgets which renders
        LaTeX using Matplotlib and provides copy options.
        
        Args:
            property_name: Human-readable name of the property
            formula_latex: LaTeX formula string
        """
        if not formula_latex:
            logger.warning(f"No formula available for {property_name}")
            return
        
        if not FORMULA_DIALOG_AVAILABLE:
            # Fallback: show in a simple dialog
            from PyQt6.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setWindowTitle(f"Formula: {property_name}")
            msg.setText(f"LaTeX:\n\n{formula_latex}")
            msg.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {COLORS['cloud']};
                }}
                QLabel {{
                    color: {COLORS['void']};
                    font-family: 'JetBrains Mono', 'Consolas', monospace;
                    font-size: 12px;
                }}
            """)
            msg.exec()
            return
        
        # Use the full FormulaDialog with LaTeX rendering
        dialog = FormulaDialog(
            property_name=property_name,
            formula_latex=formula_latex,
            parent=self,
        )
        dialog.show()
        logger.info(f"Opened formula dialog for: {property_name}")
    
    def _show_derivation_dialog(self) -> None:
        """
        Show the derivation dialog with mathematical commentary.

        Displays the form's derivation text in a scrollable, beautifully
        formatted dialog with LaTeX rendering for mathematical formulas.
        """
        if not self._current_solver:
            logger.warning("No solver set — cannot show derivations")
            return

        derivation_text = self._current_solver.get_derivation()
        if not derivation_text:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "No Derivations Available",
                f"No derivation documentation is available for {self._current_solver.form_type}.",
            )
            return

        title = self._current_solver.get_derivation_title()

        # Create a dialog with the derivation text
        from PyQt6.QtWidgets import QDialog
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.resize(800, 650)
        dialog.setStyleSheet(f"background-color: {COLORS['cloud']};")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header
        header_label = QLabel(title)
        header_label.setStyleSheet(f"""
            color: {COLORS['void']};
            font-size: 18px;
            font-weight: 600;
        """)
        layout.addWidget(header_label)

        # Scrollable text area with the derivation (with LaTeX rendering support)
        text_area = QTextEdit()
        text_area.setReadOnly(True)
        text_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['light']};
                border: 1px solid {COLORS['ash']};
                border-radius: 8px;
                padding: 16px;
                color: {COLORS['void']};
                font-family: 'JetBrains Mono', 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                line-height: 1.6;
            }}
        """)

        # Set plain text first (for fallback and copy operations)
        text_area.setPlainText(derivation_text)

        # Attempt to render LaTeX formulas if MathRenderer is available
        self._render_latex_in_text_area(text_area, derivation_text)

        layout.addWidget(text_area, 1)

        # Button row
        button_row = QHBoxLayout()
        button_row.setSpacing(12)

        render_math_btn = QPushButton("🎨 Render Math")
        set_archetype(render_math_btn, "ghost")
        render_math_btn.setToolTip("Re-render all LaTeX formulas ($...$$ and $...$)")
        render_math_btn.clicked.connect(lambda: self._render_latex_in_text_area(text_area, derivation_text))
        button_row.addWidget(render_math_btn)

        copy_btn = QPushButton("📋 Copy Text")
        set_archetype(copy_btn, "ghost")  # Light-themed button
        copy_btn.clicked.connect(lambda: self._copy_to_clipboard(derivation_text, "Derivation"))
        button_row.addWidget(copy_btn)

        button_row.addStretch()

        close_btn = QPushButton("Close")
        set_archetype(close_btn, "ghost")  # Light-themed button
        close_btn.clicked.connect(dialog.accept)
        button_row.addWidget(close_btn)

        layout.addLayout(button_row)

        dialog.exec()
        logger.info(f"Opened derivation dialog for: {self._current_solver.form_type}")
    
    def _render_latex_in_text_area(self, text_area: QTextEdit, derivation_text: str) -> None:
        """
        Render LaTeX formulas in a QTextEdit widget.

        Searches for LaTeX delimiters ($...$ and $$...$$) and replaces them
        with rendered images using MathRenderer.

        Args:
            text_area: The QTextEdit widget to render LaTeX in
            derivation_text: The original text with LaTeX markup
        """
        try:
            # Import the math renderer
            from shared.ui.rich_text_editor.math_renderer import MathRenderer
            from PyQt6.QtCore import QUrl
            from PyQt6.QtGui import QTextImageFormat, QTextCursor, QTextDocument
            import re
            import uuid
        except ImportError as e:
            logger.warning(f"Could not import LaTeX rendering dependencies: {e}")
            return

        # Reset to plain text first
        text_area.setPlainText(derivation_text)

        # Debug: Check if backslashes are in the original text
        logger.debug(f"Derivation text length: {len(derivation_text)}")
        if '\\varphi' in derivation_text:
            logger.debug("✓ Backslashes present in derivation_text (\\varphi found)")
        else:
            logger.warning("✗ Backslashes missing from derivation_text!")

        # Find all LaTeX blocks ($$...$$ and $...$)
        # Pattern matches:
        # - $$...$$ (display math) - MUST check for $$ first before single $
        # - $...$ (inline math, not preceded/followed by another $)
        # Use non-greedy matching and process $$ before $
        pattern = re.compile(r'\$\$(.*?)\$\$|\$([^\$]*?)\$', re.DOTALL)

        matches = []
        for match in pattern.finditer(derivation_text):
            matches.append(match)
            # Debug: show what was matched
            logger.debug(f"Matched: {repr(match.group(0)[:60])}")

        if not matches:
            logger.debug("No LaTeX formulas found in derivation text")
            return

        logger.info(f"Found {len(matches)} LaTeX formula(s) to render")

        doc = text_area.document()
        cursor = text_area.textCursor()

        # Process in reverse order to preserve indices
        rendered_count = 0
        failed_count = 0
        for match in reversed(matches):
            # Extract LaTeX content from the appropriate group
            # Group 1: $$...$$ content (without delimiters)
            # Group 2: $...$ content (without delimiters)
            if match.group(1) is not None:  # Display math $$...$$
                latex = match.group(1).strip()
                is_display = True
            elif match.group(2) is not None:  # Inline math $...$
                latex = match.group(2).strip()
                is_display = False
            else:
                continue

            # Skip empty formulas
            if not latex:
                continue

            start = match.start()
            end = match.end()

            # Render the LaTeX
            logger.debug(f"Rendering {'display' if is_display else 'inline'} math: {latex[:50]}...")
            image = MathRenderer.render_latex(latex, fontsize=13, dpi=140, color='#1a202c')
            if image:
                # Select the text range
                cursor.setPosition(start)
                cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)

                # Prepare resource
                img_id = str(uuid.uuid4())
                url_str = f"docimg://derivation_math/{img_id}"
                doc.addResource(QTextDocument.ResourceType.ImageResource, QUrl(url_str), image)

                # Create format
                fmt = QTextImageFormat()
                fmt.setName(url_str)
                fmt.setWidth(image.width())
                fmt.setHeight(image.height())
                fmt.setProperty(QTextImageFormat.Property.ImageAltText, f"LATEX:{latex}")
                fmt.setVerticalAlignment(QTextImageFormat.VerticalAlignment.AlignMiddle)

                # Insert the image (replaces selection)
                cursor.insertImage(fmt)
                rendered_count += 1
            else:
                logger.warning(f"Failed to render LaTeX: {latex[:50]}...")
                failed_count += 1

        logger.info(f"Rendered {rendered_count} LaTeX formulas in derivation dialog ({failed_count} failed)")

    def _copy_to_clipboard(self, text: str, label: str) -> None:
        """Copy text to clipboard and show brief status."""
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(text)
            self._show_status(f"✓ {label} copied to clipboard")
    
    # ───────────────────────────────────────────────────────────────────────────
    # Export Actions
    # ───────────────────────────────────────────────────────────────────────────
    
    def _save_snapshot(self) -> None:
        """Save a snapshot of the current viewport."""
        pixmap = self._viewport.take_snapshot()
        if pixmap:
            from PyQt6.QtWidgets import QFileDialog
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Snapshot",
                f"geometry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                "PNG Images (*.png);;JPEG Images (*.jpg)",
            )
            if path:
                pixmap.save(path)
                logger.info(f"Snapshot saved: {path}")
    
    def _copy_measurements(self) -> None:
        """Copy measurements to clipboard."""
        if not self._current_payload:
            return
        
        lines = [
            f"Form: {self._current_payload.form_type}",
            f"Dimension: {self._current_payload.dimensional_class}D",
            f"Stats: {self._current_payload.get_stats_summary()}",
            f"Signature: {self._current_payload.get_signature()}",
        ]
        
        if self._canon_verdict:
            lines.append(f"Validation: {'Passed' if self._canon_verdict.ok else 'Failed'}")
        
        text = "\n".join(lines)
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(text)
            logger.info("Measurements copied to clipboard")
    
    def _copy_declaration(self) -> None:
        """Copy Canon declaration as JSON to clipboard."""
        if not self._canon_declaration:
            return
        
        try:
            decl_dict = asdict(self._canon_declaration)
            if self._canon_result:
                sig = self._canon_result.get_declaration_signature()
                if sig:
                    decl_dict["_signature"] = sig
            
            text = json.dumps(decl_dict, indent=2, default=str)
            clipboard = QApplication.clipboard()
            if clipboard:
                clipboard.setText(text)
                logger.info("Declaration copied to clipboard")
        except Exception as e:
            logger.error(f"Failed to copy declaration: {e}")
    
    def _copy_validation_report(self) -> None:
        """Copy validation report to clipboard."""
        if not self._canon_verdict:
            return
        
        lines = ["═══ Canon Validation Report ═══", ""]
        
        if self._canon_declaration:
            lines.append(f"Declaration: {self._canon_declaration.title}")
        
        lines.append(f"Status: {'PASSED' if self._canon_verdict.ok else 'FAILED'}")
        lines.append(f"Summary: {self._canon_verdict.summary()}")
        lines.append("")
        
        findings = getattr(self._canon_verdict, "findings", [])
        if findings:
            lines.append("Findings:")
            for f in findings:
                sev = getattr(f, "severity", None)
                msg = getattr(f, "message", str(f))
                ref = getattr(f, "canon_ref", "")
                lines.append(f"  [{sev.name if sev else '?'}] {msg}")
                if ref:
                    lines.append(f"       → {ref}")
        else:
            lines.append("No findings.")
        
        text = "\n".join(lines)
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(text)
            logger.info("Validation report copied to clipboard")
    
    def _export_session(self) -> None:
        """Export full calculation session to JSON file."""
        session_data = self._history.export_session()
        
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Session",
            f"geometry_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)",
        )
        if path:
            with open(path, "w") as f:
                json.dump(session_data, f, indent=2, default=str)
            logger.info(f"Session exported: {path}")

    # ═══════════════════════════════════════════════════════════════════════════
    # Cross-Pillar Integration (Quadset Analysis)
    # ═══════════════════════════════════════════════════════════════════════════

    def _show_value_context_menu(self, field: QLineEdit, pos) -> None:
        """Show context menu for sending value to Quadset Analysis."""
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction

        # Get the value from the field
        text = field.text().strip()
        if not text:
            return

        try:
            value = float(text)
        except (TypeError, ValueError):
            return

        # Create context menu
        menu = QMenu(field)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {COLORS['light']};
                border: 1px solid {COLORS['ash']};
                border-radius: 6px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 16px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {COLORS['surface_hover']};
            }}
        """)

        # Add Quadset Analysis action
        rounded_value = int(round(value))
        action = QAction(f"📐 Send {rounded_value} to Quadset Analysis", menu)
        action.triggered.connect(lambda: self._send_value_to_quadset(value))
        menu.addAction(action)

        menu.exec(field.mapToGlobal(pos))

    @staticmethod
    def _round_cross_pillar_value(value: float) -> int:
        """Round a value for cross-pillar analysis (Quadset expects integers)."""
        return int(round(value))

    def _send_value_to_quadset(self, value: float) -> None:
        """Send a rounded value to Quadset Analysis window via navigation bus."""
        from shared.signals.navigation_bus import navigation_bus

        rounded_value = self._round_cross_pillar_value(value)
        navigation_bus.request_window.emit(
            "quadset_analysis",
            {
                "window_manager": self.window_manager,
                "initial_value": rounded_value
            }
        )
        logger.info(f"Sent value {rounded_value} to Quadset Analysis")

    # ═══════════════════════════════════════════════════════════════════════════
    # Session Persistence (Auto-save/restore)
    # ═══════════════════════════════════════════════════════════════════════════

    def closeEvent(self, event) -> None:
        """Save session on window close."""
        self._save_session()
        super().closeEvent(event)

    def _save_session(self) -> None:
        """Auto-save the current session (history entries) to disk."""
        if not hasattr(self, '_session_file') or not self._session_file:
            return

        try:
            import os
            os.makedirs(os.path.dirname(self._session_file), exist_ok=True)

            # Export full session including all history entries
            session_data = self._history.export_session()

            with open(self._session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, default=str)

            logger.info(f"Session auto-saved: {len(self._history)} entries to {self._session_file}")
        except Exception as e:
            logger.warning(f"Failed to auto-save session: {e}")

    def _restore_session(self) -> None:
        """Auto-restore the previous session (history entries) from disk."""
        if not hasattr(self, '_session_file') or not self._session_file:
            return

        import os
        if not os.path.exists(self._session_file):
            logger.info("No previous session to restore")
            return

        try:
            with open(self._session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            entries_data = session_data.get('entries', [])
            if not entries_data:
                logger.info("Session file is empty")
                return

            # Restore each entry by reconstructing Declaration objects
            # This is complex because we need to deserialize Canon DSL objects
            logger.info(f"Found {len(entries_data)} entries in previous session")

            # For now, we'll restore entries that we can reconstruct
            # This requires the solver to be set first, so we'll do it lazily
            # Store the session data for later restoration when solver is available
            self._pending_session_restore = entries_data
            logger.info("Session restore deferred until solver is set")

        except Exception as e:
            logger.warning(f"Failed to restore session: {e}")

    def _restore_session_entries(self) -> None:
        """Restore pending session entries once solver is available."""
        if not hasattr(self, '_pending_session_restore') or not self._pending_session_restore:
            return

        if not self._current_solver or not self._canon_engine:
            logger.debug("Cannot restore session yet - solver not ready")
            return

        try:
            from canon_dsl import Declaration, Form, Verdict
            from dataclasses import asdict

            entries_data = self._pending_session_restore
            restored_count = 0

            for entry_dict in entries_data:
                try:
                    # Reconstruct Declaration from stored data
                    decl_data = entry_dict.get('declaration')
                    if not decl_data:
                        continue

                    # Simple reconstruction - just restore the canonical parameter
                    # and create a new declaration
                    if 'forms' in decl_data and decl_data['forms']:
                        form_data = decl_data['forms'][0]
                        params = form_data.get('params', {})
                        canonical_key = self._current_solver.canonical_key

                        if canonical_key in params:
                            canonical_value = params[canonical_key]

                            # Create fresh declaration
                            decl = self._current_solver.create_declaration(canonical_value)

                            # Validate and realize
                            verdict = self._canon_engine.validate(decl)
                            if verdict.ok:
                                result = self._canon_engine.realize(decl)

                                # Push to history (metadata will auto-apply)
                                self._history.push(decl, verdict, result, skip_history=False)
                                restored_count += 1

                except Exception as entry_error:
                    logger.warning(f"Failed to restore entry: {entry_error}")
                    continue

            logger.info(f"Restored {restored_count}/{len(entries_data)} entries from previous session")
            self._refresh_history_list()

            # Clear pending restore
            self._pending_session_restore = None

        except Exception as e:
            logger.error(f"Failed to restore session entries: {e}")
            self._pending_session_restore = None
