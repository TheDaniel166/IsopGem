"""Standalone window hosting the 3D geometry view."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtGui import QAction, QDoubleValidator

from ...shared.solid_payload import SolidPayload
from ..calculator.widgets.formula_dialog import FormulaDialog
from shared.ui import WindowManager
from shared.ui.theme import COLORS, set_archetype
from shared.signals.navigation_bus import navigation_bus
from .view3d import Geometry3DView

logger = logging.getLogger(__name__)

# Canon DSL integration (Vault of Hestia first migration)
try:
    from canon_dsl import CanonEngine, CanonValidationError
    from ...canon.vault_of_hestia_solver import VaultOfHestiaSolver
    from ...canon.vault_of_hestia_realizer import VaultOfHestiaRealizer
    # NOTE: VaultOfHestiaSolidCalculator removed - now using VaultOfHestiaSolver for all calculations
    CANON_DSL_AVAILABLE = True
except ImportError as _canon_import_error:
    CANON_DSL_AVAILABLE = False
    CanonValidationError = Exception  # Fallback for type hints
    # Uncomment for debugging: logger.warning(f"Canon DSL import failed: {_canon_import_error}")


class Geometry3DWindow(QMainWindow):
    """Independent window bundling the 3D view with info and control panes."""

    def __init__(self, window_manager: Optional[WindowManager] = None, parent=None):
        """
          init   logic.
        
        Args:
            window_manager: Description of window_manager.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setWindowTitle("Geometry 3D Viewer")
        self.setMinimumSize(1200, 720)

        self._view = Geometry3DView(self)
        self.window_manager = window_manager
        self._solid_title_label: Optional[QLabel] = None
        self._solid_summary_label: Optional[QLabel] = None
        self._default_summary_text = "Choose a solid from the hub to see its parameters and derived metrics."
        self._status_label: Optional[QLabel] = None
        self._axes_checkbox: Optional[QCheckBox] = None
        self._sphere_checkboxes: Dict[str, QCheckBox] = {}
        self._current_payload: Optional[SolidPayload] = None
        self._calculator: Optional[Any] = None
        self._property_layout: Optional[QVBoxLayout] = None
        self._advanced_property_layout: Optional[QVBoxLayout] = None
        self._property_inputs: Dict[str, QLineEdit] = {}
        self._property_placeholder: Optional[QLabel] = None
        self._advanced_property_placeholder: Optional[QLabel] = None
        self._property_error_label: Optional[QLabel] = None
        self._metadata_mode = True
        self._updating_inputs = False
        self._formula_dialogs = []
        
        # Canon DSL integration (for Vault of Hestia and future forms)
        self._use_canon_dsl = False
        self._canon_engine: Optional[CanonEngine] = None
        self._canon_solver: Optional[Any] = None
        self._canon_badge: Optional[QLabel] = None
        # Canon state (source of truth for Canon-compatible forms)
        self._canon_declaration: Optional[Any] = None  # Declaration
        self._canon_verdict: Optional[Any] = None  # Verdict
        self._canon_result: Optional[Any] = None  # RealizeResult
        # Canon UI components
        self._canon_metrics_frame: Optional[QFrame] = None
        self._canon_metrics_layout: Optional[QVBoxLayout] = None
        self._canon_findings_frame: Optional[QFrame] = None
        self._canon_findings_layout: Optional[QVBoxLayout] = None
        if CANON_DSL_AVAILABLE:
            self._canon_engine = CanonEngine()
            self._canon_engine.register_realizer("VaultOfHestia", VaultOfHestiaRealizer())

        central = QWidget(self)
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(16)

        toolbar = self._build_toolbar()
        root_layout.addLayout(toolbar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("QSplitter::handle { background-color: #e2e8f0; }")

        self._details_panel = self._build_details_panel()
        self._viewport_panel = self._build_viewport_panel()
        self._controls_panel = self._build_controls_panel()

        splitter.addWidget(self._details_panel)
        splitter.addWidget(self._viewport_panel)
        splitter.addWidget(self._controls_panel)
        splitter.setSizes([320, 700, 260])
        root_layout.addWidget(splitter, 1)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def set_payload(self, payload: Optional[SolidPayload]):
        """
        Configure payload logic.
        
        Args:
            payload: Description of payload.
        
        """
        self._current_payload = payload
        self._view.set_payload(payload)
        self._update_status(payload)
        if not self._calculator:
            self._render_metadata_only(payload)

    def set_solid_context(self, title: Optional[str] = None, summary: Optional[str] = None):
        """
        Configure solid context logic.
        
        Args:
            title: Description of title.
            summary: Description of summary.
        
        """
        if title and self._solid_title_label:
            self._solid_title_label.setText(title)
        if summary is not None and self._solid_summary_label:
            text = summary or self._default_summary_text
            self._solid_summary_label.setText(text)

    def set_calculator(self, calculator: Any):
        """
        Configure calculator logic.
        
        Args:
            calculator: Description of calculator.
        
        """
        self._calculator = calculator
        self._metadata_mode = False
        
        # Detect if this is a Canon DSL-compatible calculator
        # NOTE: VaultOfHestiaSolidCalculator has been removed. This window (window3d.py) is legacy code.
        # The new unified viewer uses VaultOfHestiaSolver directly. This check will never be true.
        if CANON_DSL_AVAILABLE and False:  # isinstance check removed - calculator class no longer exists
            self._use_canon_dsl = True
            self._canon_solver = VaultOfHestiaSolver()
            # Clear Canon state (will be populated on first realization)
            self._canon_declaration = None
            self._canon_verdict = None
            self._canon_result = None
            # Show Canon badge
            if self._canon_badge:
                self._canon_badge.show()
                self._update_canon_badge()
        else:
            self._use_canon_dsl = False
            self._canon_solver = None
            self._canon_declaration = None
            self._canon_verdict = None
            self._canon_result = None
            # Hide Canon badge
            if self._canon_badge:
                self._canon_badge.hide()
        
        self._rebuild_property_inputs()
        self._sync_property_inputs()
        if self._property_error_label:
            self._property_error_label.hide()

    # ------------------------------------------------------------------
    # UI builders
    # ------------------------------------------------------------------


    def _build_toolbar(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        caption = QLabel("Load a solid to populate the panes. Use the tools on the right for quick camera snaps.")
        caption.setStyleSheet("color: #475569; font-size: 10.5pt;")
        layout.addWidget(caption)
        layout.addStretch(1)

        reset_btn = QPushButton("Reset View")
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.setStyleSheet(self._primary_button_style())
        reset_btn.clicked.connect(self._on_reset_view)
        layout.addWidget(reset_btn)
        return layout

    def _build_details_panel(self) -> QWidget:
        panel = QFrame()
        panel.setMinimumWidth(300)
        panel.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 16px;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Select a solid")
        title.setStyleSheet("font-size: 18pt; font-weight: 700; color: #0f172a; letter-spacing: -0.3px;")
        layout.addWidget(title)
        self._solid_title_label = title

        summary = QLabel("Choose a solid from the hub to see its parameters and derived metrics.")
        summary.setWordWrap(True)
        summary.setStyleSheet("color: #475569; font-size: 10.5pt;")
        layout.addWidget(summary)
        self._solid_summary_label = summary

        layout.addSpacing(6)

        # Tabbed property sections
        property_tabs = QTabWidget()
        property_tabs.setDocumentMode(True)
        property_tabs.setStyleSheet(
            """
            QTabWidget::pane { border: 1px solid #e2e8f0; border-radius: 10px; background-color: transparent; }
            QTabBar::tab { padding: 8px 16px; margin: 2px; font-weight: 600; }
            QTabBar::tab:selected { background-color: #e0e7ff; border-radius: 6px; color: #1d4ed8; }
            QTabBar::tab:!selected { background-color: #f8fafc; color: #64748b; }
            """
        )
        
        # Core properties tab
        core_scroll = QScrollArea()
        core_scroll.setWidgetResizable(True)
        core_scroll.setStyleSheet("QScrollArea {border: none; background-color: transparent;}")
        core_widget = QWidget()
        self._property_layout = QVBoxLayout(core_widget)
        self._property_layout.setContentsMargins(8, 8, 8, 8)
        self._property_layout.setSpacing(10)
        placeholder = QLabel("Load a 3D solid to edit its measurements.")
        placeholder.setWordWrap(True)
        placeholder.setStyleSheet("color: #94a3b8; font-style: italic; font-size: 10pt;")
        self._property_layout.addWidget(placeholder)
        self._property_layout.addStretch(1)
        self._property_placeholder = placeholder
        core_scroll.setWidget(core_widget)
        property_tabs.addTab(core_scroll, "Core")
        
        # Advanced properties tab
        advanced_scroll = QScrollArea()
        advanced_scroll.setWidgetResizable(True)
        advanced_scroll.setStyleSheet("QScrollArea {border: none; background-color: transparent;}")
        advanced_widget = QWidget()
        self._advanced_property_layout = QVBoxLayout(advanced_widget)
        self._advanced_property_layout.setContentsMargins(8, 8, 8, 8)
        self._advanced_property_layout.setSpacing(10)
        advanced_placeholder = QLabel("Advanced properties (physics, topology, symmetry) appear here.")
        advanced_placeholder.setWordWrap(True)
        advanced_placeholder.setStyleSheet("color: #94a3b8; font-style: italic; font-size: 10pt;")
        self._advanced_property_layout.addWidget(advanced_placeholder)
        self._advanced_property_layout.addStretch(1)
        self._advanced_property_placeholder = advanced_placeholder
        advanced_scroll.setWidget(advanced_widget)
        property_tabs.addTab(advanced_scroll, "Advanced")
        
        layout.addWidget(property_tabs, 1)

        error_label = QLabel()
        error_label.setStyleSheet("color: #dc2626; font-size: 10pt;")
        error_label.hide()
        layout.addWidget(error_label)
        self._property_error_label = error_label

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        clear_btn = QPushButton("Clear All")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setStyleSheet(self._secondary_button_style())
        clear_btn.clicked.connect(self._clear_calculator)
        button_row.addWidget(clear_btn)
        layout.addLayout(button_row)

        return panel

    def _build_viewport_panel(self) -> QWidget:
        panel = QFrame()
        panel.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 16px;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Viewport")
        title.setStyleSheet("color: #0f172a; font-size: 15pt; font-weight: 700;")
        header.addWidget(title)
        header.addStretch(1)
        
        # Canon DSL badge (clickable - shows validation status and findings)
        canon_badge = QPushButton("✓ Canon")
        canon_badge.setObjectName("CanonBadge")
        canon_badge.setCursor(Qt.CursorShape.PointingHandCursor)
        canon_badge.setStyleSheet(f"""
            QPushButton#CanonBadge {{
                color: {COLORS['scribe_dark']};
                background-color: {COLORS['scribe_soft']};
                border: 1px solid {COLORS['scribe']};
                border-radius: 8px;
                padding: 4px 10px;
                font-size: 9pt;
                font-weight: 700;
            }}
            QPushButton#CanonBadge:hover {{
                background-color: {COLORS['scribe_mute']};
                border-color: {COLORS['scribe_dark']};
            }}
        """)
        canon_badge.setToolTip("Click for Canon Details\nHover for validation summary")
        canon_badge.hide()  # Hidden by default, shown when Canon path is active
        canon_badge.clicked.connect(self._show_canon_details_dialog)
        header.addWidget(canon_badge)
        self._canon_badge = canon_badge
        
        status = QLabel("No solid loaded")
        status.setStyleSheet(f"color: {COLORS['muted']}; font-size: 10.5pt;")
        header.addWidget(status)
        self._status_label = status
        layout.addLayout(header)

        frame = QFrame()
        frame.setObjectName("ViewportFrame")
        frame.setStyleSheet(f"QFrame#ViewportFrame {{background-color: {COLORS['void']}; border-radius: 12px;}}")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.addWidget(self._view)
        layout.addWidget(frame, 1)
        return panel

    def _build_controls_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("ControlsPanel")
        panel.setMinimumWidth(260)
        panel.setStyleSheet(f"""
            QFrame#ControlsPanel {{
                background-color: {COLORS['light']};
                border: 1px solid {COLORS['ash']};
                border-radius: 16px;
            }}
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        title = QLabel("Viewport Console")
        title.setStyleSheet(f"color: {COLORS['void']}; font-size: 14pt; font-weight: 700;")
        layout.addWidget(title)

        tabs = QTabWidget()
        tabs.setObjectName("ControlsTabs")
        tabs.setDocumentMode(True)
        tabs.setStyleSheet(f"""
            QTabWidget#ControlsTabs::pane {{ border: 1px solid {COLORS['ash']}; border-radius: 10px; }}
            QTabBar::tab {{ padding: 6px 12px; margin: 2px; }}
            QTabBar::tab:selected {{ background-color: {COLORS['magus_soft']}; border-radius: 6px; }}
        """)
        tabs.addTab(self._build_display_tab(), "Display")
        tabs.addTab(self._build_camera_tab(), "Camera")
        tabs.addTab(self._build_output_tab(), "Output")
        layout.addWidget(tabs, 1)
        return panel

    def _build_display_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        axes_cb = self._create_checkbox("Show axis triad", self._view.axes_visible())
        axes_cb.toggled.connect(self._view.set_axes_visible)
        layout.addWidget(axes_cb)
        self._axes_checkbox = axes_cb

        labels_cb = self._create_checkbox("Show labels", self._view.labels_visible())
        labels_cb.toggled.connect(self._view.set_labels_visible)
        layout.addWidget(labels_cb)

        vertices_cb = self._create_checkbox("Show vertices", self._view.vertices_visible())
        vertices_cb.toggled.connect(self._view.set_vertices_visible)
        layout.addWidget(vertices_cb)

        dual_cb = self._create_checkbox("Show Dual Solid (Ghost)", self._view.dual_visible())
        dual_cb.toggled.connect(self._view.set_dual_visible)
        layout.addWidget(dual_cb)

        sphere_toggles = (
            ('incircle', 'Show insphere (inradius)'),
            ('midsphere', 'Show midsphere'),
            ('circumsphere', 'Show circumsphere'),
        )
        for key, label in sphere_toggles:
            cb = self._create_checkbox(label, self._view.sphere_visible(key))
            cb.toggled.connect(lambda checked, k=key: self._view.set_sphere_visible(k, checked))  # type: ignore[reportUnknownArgumentType, reportUnknownLambdaType]
            layout.addWidget(cb)
            self._sphere_checkboxes[key] = cb

        # Measure tool button
        measure_btn = QPushButton("📏 Measure Tool")
        measure_btn.setObjectName("MeasureToolBtn")
        measure_btn.setCheckable(True)
        measure_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        measure_btn.setStyleSheet(f"""
            QPushButton#MeasureToolBtn {{
                background-color: {COLORS['marble']};
                border: 1px solid {COLORS['ash']};
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: 600;
            }}
            QPushButton#MeasureToolBtn:checked {{
                background-color: {COLORS['seeker_soft']};
                border-color: {COLORS['seeker']};
                color: {COLORS['seeker_text_disabled']};
            }}
            QPushButton#MeasureToolBtn:hover {{
                background-color: {COLORS['surface_hover']};
            }}
        """)
        measure_btn.toggled.connect(self._on_measure_mode_toggled)
        layout.addWidget(measure_btn)
        self._measure_button = measure_btn

        # Canon Metrics Section (hidden until Canon path active)
        canon_metrics = QFrame()
        canon_metrics.setObjectName("CanonMetricsFrame")
        canon_metrics.setStyleSheet(f"""
            QFrame#CanonMetricsFrame {{
                background-color: {COLORS['scribe_soft']};
                border: 1px solid {COLORS['scribe_mute']};
                border-radius: 8px;
            }}
        """)
        canon_metrics.hide()
        metrics_layout = QVBoxLayout(canon_metrics)
        metrics_layout.setContentsMargins(12, 10, 12, 10)
        metrics_layout.setSpacing(6)
        
        metrics_header = QLabel("✦ Canon Metrics")
        metrics_header.setStyleSheet(f"color: {COLORS['scribe_text_disabled']}; font-weight: 700; font-size: 10pt;")
        metrics_layout.addWidget(metrics_header)
        
        # Metrics content populated dynamically
        self._canon_metrics_frame = canon_metrics
        self._canon_metrics_layout = metrics_layout
        layout.addWidget(canon_metrics)

        layout.addStretch(1)
        return tab

    def _build_camera_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        layout.addWidget(self._build_quick_view_section())

        zoom_row = QHBoxLayout()
        zoom_in_btn = QPushButton("Zoom In")
        zoom_in_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        zoom_in_btn.setStyleSheet(self._secondary_button_style())
        zoom_in_btn.clicked.connect(self._on_zoom_in)
        zoom_row.addWidget(zoom_in_btn)

        zoom_out_btn = QPushButton("Zoom Out")
        zoom_out_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        zoom_out_btn.setStyleSheet(self._secondary_button_style())
        zoom_out_btn.clicked.connect(self._on_zoom_out)
        zoom_row.addWidget(zoom_out_btn)
        layout.addLayout(zoom_row)

        view_row = QHBoxLayout()
        fit_btn = QPushButton("Fit Solid")
        fit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        fit_btn.setStyleSheet(self._secondary_button_style())
        fit_btn.clicked.connect(self._on_fit_view)
        view_row.addWidget(fit_btn)

        reset_btn = QPushButton("Reset View")
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.setStyleSheet(self._secondary_button_style())
        reset_btn.clicked.connect(self._on_reset_view)
        view_row.addWidget(reset_btn)
        layout.addLayout(view_row)

        layout.addWidget(self._build_instructions_section(), 1)
        return tab

    def _build_output_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Standard export buttons
        snapshot_btn = QPushButton("Copy Snapshot")
        snapshot_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        snapshot_btn.setStyleSheet(self._secondary_button_style())
        snapshot_btn.clicked.connect(self._capture_snapshot)
        layout.addWidget(snapshot_btn)

        summary_btn = QPushButton("Copy Measurements")
        summary_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        summary_btn.setStyleSheet(self._secondary_button_style())
        summary_btn.clicked.connect(self._copy_measurement_summary)
        layout.addWidget(summary_btn)

        # Canon Export Section (hidden until Canon path active)
        canon_section = QFrame()
        canon_section.setObjectName("CanonExportSection")
        canon_section.setStyleSheet(f"""
            QFrame#CanonExportSection {{
                background-color: {COLORS['scribe_soft']};
                border: 1px solid {COLORS['scribe_mute']};
                border-radius: 8px;
            }}
        """)
        canon_section.hide()
        canon_layout = QVBoxLayout(canon_section)
        canon_layout.setContentsMargins(12, 10, 12, 10)
        canon_layout.setSpacing(8)
        
        canon_header = QLabel("📜 Canon Exports")
        canon_header.setStyleSheet(f"color: {COLORS['scribe_text_disabled']}; font-weight: 700; font-size: 10pt;")
        canon_layout.addWidget(canon_header)
        
        decl_btn = QPushButton("Copy Declaration (JSON)")
        decl_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        set_archetype(decl_btn, "scribe")
        decl_btn.clicked.connect(self._copy_canon_declaration)
        canon_layout.addWidget(decl_btn)
        
        report_btn = QPushButton("Copy Validation Report")
        report_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        set_archetype(report_btn, "scribe")
        report_btn.clicked.connect(self._copy_canon_validation_report)
        canon_layout.addWidget(report_btn)
        
        layout.addWidget(canon_section)
        self._canon_export_section = canon_section

        # Canon Findings Panel (hidden until findings exist)
        findings_frame = QFrame()
        findings_frame.setObjectName("CanonFindingsFrame")
        findings_frame.setStyleSheet(f"""
            QFrame#CanonFindingsFrame {{
                background-color: {COLORS['seeker_soft']};
                border: 1px solid {COLORS['seeker_mute']};
                border-radius: 8px;
            }}
        """)
        findings_frame.hide()
        findings_layout = QVBoxLayout(findings_frame)
        findings_layout.setContentsMargins(12, 10, 12, 10)
        findings_layout.setSpacing(6)
        
        findings_header = QLabel("⚠ Canon Findings")
        findings_header.setStyleSheet(f"color: {COLORS['seeker_text_disabled']}; font-weight: 700; font-size: 10pt;")
        findings_layout.addWidget(findings_header)
        
        # Findings content will be populated dynamically
        self._canon_findings_frame = findings_frame
        self._canon_findings_layout = findings_layout
        layout.addWidget(findings_frame)

        # Info text
        info_frame = QFrame()
        info_frame.setObjectName("OutputInfoFrame")
        info_frame.setStyleSheet(f"""
            QFrame#OutputInfoFrame {{
                background-color: {COLORS['magus_soft']};
                border: 1px solid {COLORS['magus_mute']};
                border-radius: 8px;
            }}
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(14, 12, 14, 12)
        info_text = QLabel("Snapshots and measurement summaries copy directly to your clipboard.")
        info_text.setWordWrap(True)
        info_text.setStyleSheet(f"color: {COLORS['magus']}; font-size: 9pt;")
        info_layout.addWidget(info_text)
        layout.addWidget(info_frame)

        layout.addStretch(1)
        return tab

    @staticmethod
    def _create_checkbox(text: str, checked: bool) -> QCheckBox:
        checkbox = QCheckBox(text)
        checkbox.setChecked(checked)
        checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        checkbox.setStyleSheet(
            """
            QCheckBox {
                font-size: 10pt;
                color: #475569;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #cbd5e1;
                border-radius: 4px;
                background: white;
            }
            QCheckBox::indicator:checked {
                background-color: #3b82f6;
                border-color: #3b82f6;
            }
            QCheckBox::indicator:hover {
                border-color: #3b82f6;
            }
            """
        )
        return checkbox

    def _build_quick_view_section(self) -> QWidget:
        container = QFrame()
        container.setStyleSheet("QFrame {background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px;}")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        label = QLabel("Quick Views")
        label.setStyleSheet("color: #475569; font-weight: 700;")
        layout.addWidget(label)

        button_row = QHBoxLayout()
        presets = [
            ("Isometric", 30.0, 25.0),
            ("Top", 0.0, 89.0),
        ]
        for text, yaw, pitch in presets:
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(self._secondary_button_style())
            btn.clicked.connect(lambda _, y=yaw, p=pitch: self._view.set_camera_angles(y, p))
            button_row.addWidget(btn)
        layout.addLayout(button_row)

        button_row2 = QHBoxLayout()
        more_presets = [
            ("Front", 0.0, 0.0),
            ("Right", 90.0, 0.0),
        ]
        for text, yaw, pitch in more_presets:
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(self._secondary_button_style())
            btn.clicked.connect(lambda _, y=yaw, p=pitch: self._view.set_camera_angles(y, p))
            button_row2.addWidget(btn)
        layout.addLayout(button_row2)
        return container

    def _build_instructions_section(self) -> QWidget:
        container = QFrame()
        container.setStyleSheet("QFrame {background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px;}")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        label = QLabel("Mouse & Touchpad Controls")
        label.setStyleSheet("color: #475569; font-weight: 700;")
        layout.addWidget(label)

        description = QLabel(
            "- Left-drag: rotate\n"
            "- Shift+drag or middle-drag: pan\n"
            "- Scroll: zoom in/out"
        )
        description.setStyleSheet("color: #475569; line-height: 1.4;")
        description.setWordWrap(True)
        layout.addWidget(description)
        layout.addStretch(1)
        return container

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _build_metadata_row(self, key: str, value) -> QWidget:
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame {background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px;}"
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        name_label = QLabel(key.replace('_', ' ').title())
        name_label.setStyleSheet("color: #475569; font-weight: 700;")
        layout.addWidget(name_label)
        value_label = QLabel(self._format_value(value))
        value_label.setStyleSheet("color: #0f172a; font-size: 12pt;")
        layout.addWidget(value_label)
        return frame

    def _update_status(self, payload: Optional[SolidPayload]):
        """Update status label with geometry stats and Canon provenance."""
        if not self._status_label:
            return
        if not payload:
            self._status_label.setText("No solid loaded")
            return
        
        vertex_count = len(payload.vertices)
        edge_count = len(payload.edges)
        face_count = len(payload.faces)
        
        # Base geometry stats
        status_parts = [f"{vertex_count} vertices", f"{edge_count} edges", f"{face_count} faces"]
        
        # Add Canon provenance if available
        if self._use_canon_dsl and self._canon_verdict:
            # Add φ resonance for Vault of Hestia
            if self._canon_result and hasattr(payload, 'metadata') and payload.metadata:
                phi = payload.metadata.get('phi') or payload.metadata.get('phi_ratio')
                if phi:
                    status_parts.append(f"φ={phi:.6f}")
            
            # Add validation status
            if self._canon_verdict.ok:
                warn_count = self._canon_verdict.warn_count()
                if warn_count > 0:
                    status_parts.append(f"⚠ {warn_count} warning{'s' if warn_count > 1 else ''}")
                else:
                    status_parts.append("✓ Canon")
            else:
                blocking = len(self._canon_verdict.blocking_findings())
                status_parts.append(f"✗ {blocking} issue{'s' if blocking > 1 else ''}")
            
            # Add short signature
            if self._canon_result:
                sig = self._canon_result.get_declaration_signature()
                if sig:
                    status_parts.append(f"sig:{sig[:8]}")
        
        self._status_label.setText(" · ".join(status_parts))

    def _render_metadata_only(self, payload: Optional[SolidPayload]):
        layout = self._property_layout
        if layout is None:
            return
        self._metadata_mode = True
        self._clear_layout(layout)
        if not payload or not payload.metadata:
            placeholder = QLabel("Metrics will appear here once a solid is loaded.")
            placeholder.setWordWrap(True)
            placeholder.setStyleSheet("color: #94a3b8; font-style: italic; font-size: 10pt;")
            layout.addWidget(placeholder)
            layout.addStretch(1)
            self._property_placeholder = placeholder
            return

        for key, value in payload.metadata.items():  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
            layout.addWidget(self._build_metadata_row(key, value))  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
        layout.addStretch(1)
        self._property_placeholder = None

    def _rebuild_property_inputs(self):
        core_layout = self._property_layout
        advanced_layout = self._advanced_property_layout
        calculator = self._calculator
        if core_layout is None or calculator is None:
            return
        self._metadata_mode = False
        self._clear_layout(core_layout)
        if advanced_layout is not None:
            self._clear_layout(advanced_layout)
        self._property_inputs.clear()
        
        # Keys for advanced properties (define locally for reliability)
        advanced_keys = {
            'moment_inertia_solid', 'moment_inertia_shell',
            'angular_defect_vertex_deg', 'total_angular_defect_deg', 'euler_characteristic',
            'packing_density',
            'symmetry_group_order', 'rotational_symmetry_order', 'symmetry_group_name',
            'dual_solid_name', 'golden_ratio_factor',
        }
        
        # Separate properties into Core and Advanced
        for prop in calculator.properties():
            widget = self._create_property_input(prop)
            key = prop.key
            is_adv = key in advanced_keys
            # Use `is not None` - QVBoxLayout's __bool__ returns False when empty!
            if is_adv and advanced_layout is not None:
                advanced_layout.addWidget(widget)
            else:
                core_layout.addWidget(widget)
        
        core_layout.addStretch(1)
        if advanced_layout is not None:
            advanced_layout.addStretch(1)
        self._property_placeholder = None
        self._advanced_property_placeholder = None

    def _create_property_input(self, prop: Any) -> QWidget:
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame {background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px;}"
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        header = QHBoxLayout()
        name_label = QLabel(prop.name)
        name_label.setStyleSheet("color: #0f172a; font-weight: 700;")
        header.addWidget(name_label)
        if getattr(prop, 'unit', ''):
            unit_label = QLabel(prop.unit)
            unit_label.setStyleSheet("color: #94a3b8; font-size: 10pt;")
            header.addWidget(unit_label)
        formula = getattr(prop, 'formula', None)
        if formula:
            info_btn = QPushButton("?")
            info_btn.setFixedSize(18, 18)
            info_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            info_btn.setToolTip("Show formula")
            info_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #e0e7ff;
                    color: #312e81;
                    border: 1px solid #6366f1;
                    border-radius: 9px;
                    font-weight: 700;
                    font-size: 9pt;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #c7d2fe;
                }
                """
            )
            info_btn.clicked.connect(lambda _, p=prop: self._show_formula_dialog(p))
            header.addWidget(info_btn)
        header.addStretch(1)
        layout.addLayout(header)

        input_field = QLineEdit()
        input_field.setPlaceholderText("0.0")
        editable = bool(getattr(prop, 'editable', True))
        base_style = (
            f"QLineEdit {{background-color: %s; border: 1px solid {COLORS['ash']}; border-radius: 6px; padding: 8px;"
            f"font-size: 11pt; color: {COLORS['void']};}} QLineEdit:focus {{border-color: {COLORS['focus']};}}"
        )
        bg_color = COLORS['light'] if editable else COLORS['marble']
        input_field.setStyleSheet(base_style % bg_color)
        input_field.setReadOnly(not editable)
        validator = QDoubleValidator(0.0001, 1e9, prop.precision)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        input_field.setValidator(validator)
        if editable:
            input_field.editingFinished.connect(
                lambda key=prop.key, field=input_field: self._commit_property_change(key, field)  # type: ignore[reportUnknownArgumentType, reportUnknownLambdaType]
            )
        self._install_value_context_menu(input_field)
        layout.addWidget(input_field)
        self._property_inputs[prop.key] = input_field
        return frame

    def _show_formula_dialog(self, prop: Any):
        formula = getattr(prop, 'formula', None)
        if not formula:
            return
        dialog = FormulaDialog(property_name=prop.name, formula_latex=formula, parent=self)
        self._formula_dialogs.append(dialog)
        dialog.destroyed.connect(
            lambda _, d=dialog: self._formula_dialogs.remove(d) if d in self._formula_dialogs else None
        )
        dialog.show()

    def _commit_property_change(self, key: str, field: QLineEdit):
        """
        Commit a property change from user input.
        
        For Canon DSL-compatible forms (Vault of Hestia), uses the Solver
        to create a Declaration and realize via CanonEngine.
        For legacy forms, uses the calculator's set_property method.
        """
        if self._updating_inputs or not self._calculator:
            return
        text = field.text().strip()
        if not text:
            return
        try:
            value = float(text)
        except ValueError:
            self._show_property_error("Enter a valid number")
            return
        
        # Canon DSL path: Use Solver for bidirectional solving
        if self._use_canon_dsl and self._canon_solver and self._canon_engine:
            self._commit_property_via_canon(key, value)
        else:
            # Legacy path: Direct calculator update
            if not self._calculator.set_property(key, value):
                self._show_property_error("Value outside valid range")
                return
            self._show_property_error(None)
            self._sync_property_inputs()
    
    def _commit_property_via_canon(self, key: str, value: float):
        """
        Commit property change via Canon DSL path.
        
        FULL COMMITMENT: No legacy fallback. If Canon validation fails, we show
        the findings to the user and do not proceed.
        
        Uses the Solver to solve from the changed property, creates a Declaration,
        validates and realizes it, then stores as source of truth.
        
        Canon References: ADR-010, Hermetic Geometry Canon v1.0
        """
        solver = self._canon_solver
        engine = self._canon_engine
        
        if not solver or not engine:
            logger.error("Canon DSL components not available")
            self._show_property_error("Canon DSL unavailable")
            return
        
        # Solve from the changed property to get canonical parameter
        solve_result = solver.solve_from(key, value)
        
        if not solve_result.ok:
            self._show_property_error(
                solve_result.reason or f"Invalid value for {key}"
            )
            logger.warning(f"Canon DSL solve failed for {key}={value}: {solve_result.reason}")
            return
        
        # Create Declaration from solved canonical parameter
        decl = solver.create_declaration(solve_result.canonical_parameter)
        
        # Validate first (to get verdict and findings)
        try:
            verdict = engine.validate(decl)
            self._canon_verdict = verdict
            
            # Realize via CanonEngine (will re-validate, but we already have verdict)
            result = engine.realize(decl)
            
            # Store as source of truth
            self._canon_declaration = decl
            self._canon_result = result
            
            # Get the artifact (SolidPayload)
            payload = result.get_artifact("vault")
            
            if not payload:
                logger.error("Canon DSL realization returned no artifact")
                self._show_property_error("Realization failed: no artifact produced")
                return
            
            # Update payload and view
            self._current_payload = payload
            self._view.set_payload(payload)
            self._update_status(payload)
            
            # Update property inputs from Canon state (will be read by _sync_property_inputs)
            self._sync_property_inputs()
            
            # Update badge with validation status
            self._update_canon_badge()
            
            self._show_property_error(None)
            
            # Log provenance
            sig = result.get_declaration_signature()
            if sig:
                logger.info(f"Canon DSL realized Vault of Hestia (signature: {sig[:16]}...)")
            
        except CanonValidationError as e:
            # Canon validation failed - show findings to user
            self._canon_verdict = e.verdict
            self._canon_declaration = decl
            self._canon_result = None
            
            # Surface findings in error message
            blocking = e.verdict.blocking_findings()
            if blocking:
                error_msg = f"Canon validation failed:\n"
                for finding in blocking[:3]:  # Show first 3 blocking findings
                    error_msg += f"• {finding.message}\n"
                if len(blocking) > 3:
                    error_msg += f"... and {len(blocking) - 3} more"
            else:
                error_msg = "Canon validation failed"
            
            self._show_property_error(error_msg.strip())
            self._update_canon_badge()
            logger.error(f"Canon validation failed: {e.verdict.summary()}")
            
        except Exception as e:
            # System error (not validation failure)
            logger.error(f"Canon DSL realization system error: {e}", exc_info=True)
            self._show_property_error(f"System error: {str(e)}")
            self._canon_declaration = None
            self._canon_verdict = None
            self._canon_result = None
            self._update_canon_badge()

    def _sync_property_inputs(self):
        """
        Sync property inputs from source of truth.
        
        For Canon DSL-compatible forms: reads from Canon state (solver properties).
        For legacy forms: reads from calculator properties.
        """
        calculator = self._calculator
        if not calculator:
            return
        
        self._updating_inputs = True
        
        # Canon DSL path: Read from solver's computed properties (source of truth)
        if self._use_canon_dsl and self._canon_solver and self._canon_result:
            # Get canonical parameter from current declaration
            if self._canon_declaration and self._canon_declaration.forms:
                form = self._canon_declaration.forms[0]
                side_length = form.params.get("side_length", 10.0)
                all_props = self._canon_solver.get_all_properties(side_length)
                
                # Update fields from Canon state
                for prop_key, prop_value in all_props.items():
                    field = self._property_inputs.get(prop_key)
                    if field:
                        try:
                            formatted = f"{prop_value:.6f}".rstrip('0').rstrip('.')
                            field.setText(formatted)
                        except RuntimeError:
                            continue
        else:
            # Legacy path: Read from calculator
            for prop in calculator.properties():
                field = self._property_inputs.get(prop.key)
                if field is None:
                    continue
                try:
                    if prop.value is None:
                        field.clear()
                    elif isinstance(prop.value, str):
                        field.setText(prop.value)
                    else:
                        formatted = f"{prop.value:.{prop.precision}f}".rstrip('0').rstrip('.')
                        field.setText(formatted)
                except RuntimeError:
                    continue
        
        self._updating_inputs = False
        
        # Canon DSL path: Use CanonEngine for validated realization
        if self._use_canon_dsl and self._canon_engine and self._canon_solver:
            self._realize_via_canon()
            return
        
        # Legacy path: Direct payload from calculator
        payload = calculator.payload()
        self._current_payload = payload
        self._view.set_payload(payload)
        self._update_status(payload)
    
    def _realize_via_canon(self):
        """
        Realize geometry via the Canon DSL path.
        
        FULL COMMITMENT: Reads from Canon state if available, otherwise initializes
        from calculator. No legacy fallback - if Canon fails, we show error.
        
        This method:
        1. Gets canonical parameter from Canon state or calculator
        2. Creates a Declaration via the Solver
        3. Validates via CanonEngine (stores verdict)
        4. Realizes via CanonEngine (stores result)
        5. Updates badge with validation status
        
        Canon References: ADR-010
        """
        calculator = self._calculator
        solver = self._canon_solver
        engine = self._canon_engine
        
        if not calculator or not solver or not engine:
            return
        
        # Get canonical parameter from Canon state (source of truth) or calculator (initial load)
        side_length = None
        if self._canon_declaration and self._canon_declaration.forms:
            # Use existing Canon state
            form = self._canon_declaration.forms[0]
            side_length = form.params.get("side_length")
        
        if side_length is None:
            # Initial load: read from calculator
            for prop in calculator.properties():
                if prop.key == "side_length" and prop.value is not None:
                    side_length = prop.value
                    break
        
        if side_length is None:
            logger.warning("No side_length available for Canon realization")
            return
        
        # Create Declaration via Solver
        decl = solver.create_declaration(side_length)
        
        try:
            # Validate first to get verdict
            verdict = engine.validate(decl)
            self._canon_verdict = verdict
            
            # Realize via CanonEngine
            result = engine.realize(decl)
            
            # Store as source of truth
            self._canon_declaration = decl
            self._canon_result = result
            
            # Get the artifact (SolidPayload)
            payload = result.get_artifact("vault")
            
            if payload:
                self._current_payload = payload
                self._view.set_payload(payload)
                self._update_status(payload)
                
                # Update badge
                self._update_canon_badge()
                
                # Log provenance
                sig = result.get_declaration_signature()
                if sig:
                    logger.info(f"Canon DSL realized Vault of Hestia (signature: {sig[:16]}...)")
            else:
                logger.error("Canon DSL realization returned no artifact")
                self._show_property_error("Realization failed: no artifact")
                
        except CanonValidationError as e:
            # Canon validation failed
            self._canon_verdict = e.verdict
            self._canon_declaration = decl
            self._canon_result = None
            
            # Show validation failure
            blocking = e.verdict.blocking_findings()
            if blocking:
                error_msg = f"Canon validation failed:\n"
                for finding in blocking[:2]:
                    error_msg += f"• {finding.message}\n"
                self._show_property_error(error_msg.strip())
            else:
                self._show_property_error("Canon validation failed")
            
            self._update_canon_badge()
            logger.error(f"Canon validation failed: {e.verdict.summary()}")
            
        except Exception as e:
            # System error
            logger.error(f"Canon DSL realization system error: {e}", exc_info=True)
            self._show_property_error(f"System error: {str(e)}")
            self._canon_declaration = None
            self._canon_verdict = None
            self._canon_result = None
            self._update_canon_badge()
    
    def _update_canon_badge(self):
        """
        Update the Canon badge to show validation status and findings.
        
        Badge shows:
        - Green ✓: Validation passed
        - Yellow ⚠: Validation passed with warnings
        - Red ✗: Validation failed
        - Tooltip: Detailed findings and declaration signature
        """
        if not self._canon_badge:
            return
        
        if not self._use_canon_dsl:
            self._canon_badge.hide()
            self._update_canon_ui_sections(show=False)
            return
        
        self._canon_badge.show()
        self._update_canon_ui_sections(show=True)
        
        if not self._canon_verdict:
            # No validation yet - Navigator (Slate) style
            self._canon_badge.setText("⏳ Canon")
            self._canon_badge.setStyleSheet(f"""
                QPushButton#CanonBadge {{
                    color: {COLORS['navigator']};
                    background-color: {COLORS['marble']};
                    border: 1px solid {COLORS['ash']};
                    border-radius: 8px;
                    padding: 4px 10px;
                    font-size: 9pt;
                    font-weight: 700;
                }}
                QPushButton#CanonBadge:hover {{
                    background-color: {COLORS['surface_hover']};
                }}
            """)
            self._canon_badge.setToolTip("Click for Canon Details\nValidation pending...")
            return
        
        # Build tooltip with validation details
        tooltip_lines = ["Click for Canon Details", "─" * 20]
        
        if self._canon_verdict.ok:
            if self._canon_verdict.warn_count() > 0:
                # Passed with warnings - Seeker (Gold/Amber) style
                self._canon_badge.setText("⚠ Canon")
                self._canon_badge.setStyleSheet(f"""
                    QPushButton#CanonBadge {{
                        color: {COLORS['seeker_dark']};
                        background-color: {COLORS['seeker_soft']};
                        border: 1px solid {COLORS['seeker']};
                        border-radius: 8px;
                        padding: 4px 10px;
                        font-size: 9pt;
                        font-weight: 700;
                    }}
                    QPushButton#CanonBadge:hover {{
                        background-color: {COLORS['seeker_mute']};
                        border-color: {COLORS['seeker_dark']};
                    }}
                """)
                tooltip_lines.append(f"✓ PASSED with {self._canon_verdict.warn_count()} warning(s)")
            else:
                # Passed cleanly - Scribe (Emerald) style
                self._canon_badge.setText("✓ Canon")
                self._canon_badge.setStyleSheet(f"""
                    QPushButton#CanonBadge {{
                        color: {COLORS['scribe_dark']};
                        background-color: {COLORS['scribe_soft']};
                        border: 1px solid {COLORS['scribe']};
                        border-radius: 8px;
                        padding: 4px 10px;
                        font-size: 9pt;
                        font-weight: 700;
                    }}
                    QPushButton#CanonBadge:hover {{
                        background-color: {COLORS['scribe_mute']};
                        border-color: {COLORS['scribe_dark']};
                    }}
                """)
                tooltip_lines.append("✓ PASSED")
        else:
            # Failed - Destroyer (Crimson) style
            self._canon_badge.setText("✗ Canon")
            self._canon_badge.setStyleSheet(f"""
                QPushButton#CanonBadge {{
                    color: {COLORS['destroyer_dark']};
                    background-color: {COLORS['destroyer_soft']};
                    border: 1px solid {COLORS['destroyer']};
                    border-radius: 8px;
                    padding: 4px 10px;
                    font-size: 9pt;
                    font-weight: 700;
                }}
                QPushButton#CanonBadge:hover {{
                    background-color: {COLORS['destroyer_mute']};
                    border-color: {COLORS['destroyer_dark']};
                }}
            """)
            blocking = self._canon_verdict.blocking_findings()
            tooltip_lines.append(f"✗ FAILED ({len(blocking)} blocking issue(s))")
        
        # Add declaration signature
        if self._canon_result:
            sig = self._canon_result.get_declaration_signature()
            if sig:
                tooltip_lines.append(f"Signature: {sig[:16]}...")
        
        # Add findings summary
        if self._canon_verdict.findings:
            tooltip_lines.append(f"Findings: {len(self._canon_verdict.findings)} total")
        
        self._canon_badge.setToolTip("\n".join(tooltip_lines))
        
        # Update Canon metrics and findings panels
        self._update_canon_metrics_panel()
        self._update_canon_findings_panel()
    
    def _update_canon_ui_sections(self, show: bool):
        """Show or hide Canon-specific UI sections."""
        if hasattr(self, '_canon_export_section') and self._canon_export_section:
            if show:
                self._canon_export_section.show()
            else:
                self._canon_export_section.hide()
        
        if self._canon_metrics_frame:
            if show:
                self._canon_metrics_frame.show()
            else:
                self._canon_metrics_frame.hide()
        
        if self._canon_findings_frame:
            # Findings only shown when there are findings
            self._canon_findings_frame.hide()
    
    def _update_canon_metrics_panel(self):
        """Populate Canon metrics panel with invariants and references."""
        if not self._canon_metrics_layout:
            return
        
        # Clear existing metrics (keep header)
        while self._canon_metrics_layout.count() > 1:
            item = self._canon_metrics_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
        
        if not self._canon_result or not self._canon_declaration:
            return
        
        # Get payload metadata for metrics
        payload = self._current_payload
        if not payload or not hasattr(payload, 'metadata') or not payload.metadata:
            return
        
        metrics_style = f"color: {COLORS['scribe_text_disabled']}; font-size: 9pt;"
        
        # Declaration signature
        sig = self._canon_result.get_declaration_signature()
        if sig:
            sig_label = QLabel(f"Signature: {sig[:16]}...")
            sig_label.setStyleSheet(metrics_style)
            sig_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            self._canon_metrics_layout.addWidget(sig_label)
        
        # Phi ratio (golden ratio) - key metric for Vault of Hestia
        phi = payload.metadata.get('phi') or payload.metadata.get('phi_ratio')
        if phi:
            phi_label = QLabel(f"φ (Golden Ratio): {phi:.10f}")
            phi_label.setStyleSheet(metrics_style)
            self._canon_metrics_layout.addWidget(phi_label)
        
        # Void ratios if present
        void_ratio = payload.metadata.get('void_ratio') or payload.metadata.get('void_percentage')
        if void_ratio:
            void_label = QLabel(f"Void Ratio: {void_ratio:.4f}")
            void_label.setStyleSheet(metrics_style)
            self._canon_metrics_layout.addWidget(void_label)
        
        # Show form type
        if self._canon_declaration.forms:
            form = self._canon_declaration.forms[0]
            form_label = QLabel(f"Form: {form.kind}")
            form_label.setStyleSheet(metrics_style)
            self._canon_metrics_layout.addWidget(form_label)
        
        # Canon references
        ref_label = QLabel("Ref: Hermetic Geometry Canon v1.0")
        ref_label.setStyleSheet(f"color: {COLORS['muted']}; font-size: 8pt; font-style: italic;")
        self._canon_metrics_layout.addWidget(ref_label)
    
    def _update_canon_findings_panel(self):
        """Populate Canon findings panel with validation warnings/errors."""
        if not self._canon_findings_layout or not self._canon_findings_frame:
            return
        
        # Clear existing findings (keep header)
        while self._canon_findings_layout.count() > 1:
            item = self._canon_findings_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
        
        if not self._canon_verdict or not self._canon_verdict.findings:
            self._canon_findings_frame.hide()
            return
        
        # Only show if there are warnings or errors
        warn_count = self._canon_verdict.warn_count()
        error_count = self._canon_verdict.error_count()
        fatal_count = self._canon_verdict.fatal_count()
        
        if warn_count == 0 and error_count == 0 and fatal_count == 0:
            self._canon_findings_frame.hide()
            return
        
        self._canon_findings_frame.show()
        
        # Update header color based on severity (using object-name selector)
        if fatal_count > 0 or error_count > 0:
            # Destroyer (Crimson) for errors
            self._canon_findings_frame.setStyleSheet(f"""
                QFrame#CanonFindingsFrame {{
                    background-color: {COLORS['destroyer_soft']};
                    border: 1px solid {COLORS['destroyer_mute']};
                    border-radius: 8px;
                }}
            """)
        else:
            # Seeker (Amber) for warnings
            self._canon_findings_frame.setStyleSheet(f"""
                QFrame#CanonFindingsFrame {{
                    background-color: {COLORS['seeker_soft']};
                    border: 1px solid {COLORS['seeker_mute']};
                    border-radius: 8px;
                }}
            """)
        
        # Show up to 3 findings
        shown = 0
        for finding in self._canon_verdict.findings:
            if finding.level.name in ('FATAL', 'ERROR', 'WARN'):
                icon = "✗" if finding.level.name in ('FATAL', 'ERROR') else "⚠"
                color = COLORS['destroyer'] if finding.level.name in ('FATAL', 'ERROR') else COLORS['seeker_dark']
                
                finding_label = QLabel(f"{icon} {finding.message}")
                finding_label.setWordWrap(True)
                finding_label.setStyleSheet(f"color: {color}; font-size: 9pt;")
                self._canon_findings_layout.addWidget(finding_label)
                
                # Show article reference if available
                if finding.article_ref:
                    ref_label = QLabel(f"   → {finding.article_ref}")
                    ref_label.setStyleSheet(f"color: {COLORS['muted']}; font-size: 8pt; font-style: italic;")
                    self._canon_findings_layout.addWidget(ref_label)
                
                shown += 1
                if shown >= 3:
                    break
        
        # Show count of remaining findings
        remaining = (warn_count + error_count + fatal_count) - shown
        if remaining > 0:
            more_label = QLabel(f"... and {remaining} more finding(s)")
            more_label.setStyleSheet(f"color: {COLORS['muted']}; font-size: 8pt; font-style: italic;")
            self._canon_findings_layout.addWidget(more_label)
    
    def _show_canon_details_dialog(self):
        """Show a dialog with full Canon validation details."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Canon Validation Details")
        dialog.setMinimumSize(500, 400)
        dialog.setStyleSheet(f"background-color: {COLORS['cloud']};")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("📜 Canon Validation Report")
        header.setStyleSheet(f"color: {COLORS['void']}; font-size: 16pt; font-weight: 700;")
        layout.addWidget(header)
        
        # Status badge
        if self._canon_verdict:
            if self._canon_verdict.ok:
                status_text = "✓ VALIDATION PASSED"
                status_color = COLORS['scribe_dark']
            else:
                status_text = "✗ VALIDATION FAILED"
                status_color = COLORS['destroyer']
            
            status = QLabel(status_text)
            status.setStyleSheet(f"color: {status_color}; font-size: 12pt; font-weight: 700;")
            layout.addWidget(status)
        
        # Declaration info
        if self._canon_declaration:
            decl_frame = QFrame()
            decl_frame.setObjectName("DialogDeclFrame")
            decl_frame.setStyleSheet(f"""
                QFrame#DialogDeclFrame {{
                    background-color: {COLORS['scribe_soft']};
                    border: 1px solid {COLORS['scribe_mute']};
                    border-radius: 8px;
                }}
            """)
            decl_layout = QVBoxLayout(decl_frame)
            decl_layout.setContentsMargins(12, 10, 12, 10)
            
            decl_header = QLabel("Declaration")
            decl_header.setStyleSheet(f"color: {COLORS['scribe_text_disabled']}; font-weight: 700;")
            decl_layout.addWidget(decl_header)
            
            if self._canon_declaration.forms:
                form = self._canon_declaration.forms[0]
                form_info = QLabel(f"Form: {form.kind}\nParameters: {form.params}")
                form_info.setStyleSheet(f"color: {COLORS['scribe_text_disabled']}; font-size: 9pt;")
                form_info.setWordWrap(True)
                decl_layout.addWidget(form_info)
            
            if self._canon_result:
                sig = self._canon_result.get_declaration_signature()
                if sig:
                    sig_label = QLabel(f"Signature: {sig}")
                    sig_label.setStyleSheet(f"color: {COLORS['scribe_text_disabled']}; font-size: 9pt;")
                    sig_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                    decl_layout.addWidget(sig_label)
            
            layout.addWidget(decl_frame)
        
        # Findings section
        if self._canon_verdict and self._canon_verdict.findings:
            findings_frame = QFrame()
            findings_frame.setObjectName("DialogFindingsFrame")
            findings_frame.setStyleSheet(f"""
                QFrame#DialogFindingsFrame {{
                    background-color: {COLORS['light']};
                    border: 1px solid {COLORS['ash']};
                    border-radius: 8px;
                }}
            """)
            findings_layout = QVBoxLayout(findings_frame)
            findings_layout.setContentsMargins(12, 10, 12, 10)
            
            findings_header = QLabel(f"Findings ({len(self._canon_verdict.findings)})")
            findings_header.setStyleSheet(f"color: {COLORS['void']}; font-weight: 700;")
            findings_layout.addWidget(findings_header)
            
            # Scrollable findings list
            findings_text = QTextEdit()
            findings_text.setObjectName("DialogFindingsText")
            findings_text.setReadOnly(True)
            findings_text.setStyleSheet(f"""
                QTextEdit#DialogFindingsText {{
                    border: none;
                    background-color: transparent;
                    font-size: 9pt;
                    color: {COLORS['stone']};
                }}
            """)
            
            findings_content = []
            for finding in self._canon_verdict.findings:
                icon = {"FATAL": "✗", "ERROR": "✗", "WARN": "⚠", "INFO": "ℹ"}.get(finding.level.name, "•")
                line = f"{icon} [{finding.level.name}] {finding.message}"
                if finding.article_ref:
                    line += f"\n   → {finding.article_ref}"
                findings_content.append(line)
            
            findings_text.setPlainText("\n\n".join(findings_content))
            findings_layout.addWidget(findings_text)
            
            layout.addWidget(findings_frame, 1)
        else:
            # No findings
            no_findings = QLabel("No findings recorded.")
            no_findings.setStyleSheet(f"color: {COLORS['muted']}; font-style: italic;")
            layout.addWidget(no_findings)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(self._secondary_button_style())
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def _copy_canon_declaration(self):
        """Copy Canon declaration as JSON to clipboard."""
        if not self._canon_declaration:
            return
        
        import json
        
        # Build declaration dict using actual Declaration attributes
        decl_dict: dict = {
            "title": getattr(self._canon_declaration, 'title', None),
            "forms": [],
            "constraints": [],
            "epsilon": getattr(self._canon_declaration, 'epsilon', None),
            "metadata": getattr(self._canon_declaration, 'metadata', {}),
        }
        
        # Export forms
        for form in self._canon_declaration.forms:
            form_dict = {
                "id": getattr(form, 'id', None),
                "kind": form.kind,
                "params": form.params,
            }
            # Include optional Form attributes if present
            if hasattr(form, 'symmetry_class') and form.symmetry_class:
                form_dict["symmetry_class"] = form.symmetry_class
            if hasattr(form, 'notes') and form.notes:
                form_dict["notes"] = form.notes
            decl_dict["forms"].append(form_dict)
        
        # Export constraints if present
        if hasattr(self._canon_declaration, 'constraints'):
            for constraint in self._canon_declaration.constraints:
                constraint_dict = {
                    "name": getattr(constraint, 'name', None),
                    "expr": getattr(constraint, 'expr', None),
                    "scope": getattr(constraint, 'scope', []),
                }
                decl_dict["constraints"].append(constraint_dict)
        
        # Add signature if available
        if self._canon_result:
            sig = self._canon_result.get_declaration_signature()
            if sig:
                decl_dict["signature"] = sig
        
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(json.dumps(decl_dict, indent=2, default=str))
    
    def _copy_canon_validation_report(self):
        """Copy Canon validation report to clipboard."""
        lines = ["═" * 50, "CANON VALIDATION REPORT", "═" * 50, ""]
        
        # Verdict
        if self._canon_verdict:
            if self._canon_verdict.ok:
                lines.append("Status: ✓ PASSED")
            else:
                lines.append("Status: ✗ FAILED")
            
            lines.append(f"Summary: {self._canon_verdict.summary()}")
            lines.append("")
            
            # Counts
            lines.append("Findings Summary:")
            lines.append(f"  FATAL: {self._canon_verdict.fatal_count()}")
            lines.append(f"  ERROR: {self._canon_verdict.error_count()}")
            lines.append(f"  WARN:  {self._canon_verdict.warn_count()}")
            lines.append(f"  INFO:  {self._canon_verdict.info_count()}")
            lines.append("")
            
            # All findings
            if self._canon_verdict.findings:
                lines.append("─" * 50)
                lines.append("DETAILED FINDINGS:")
                lines.append("─" * 50)
                for finding in self._canon_verdict.findings:
                    lines.append(f"\n[{finding.level.name}] {finding.message}")
                    if finding.article_ref:
                        lines.append(f"  Reference: {finding.article_ref}")
        else:
            lines.append("No validation performed.")
        
        lines.append("")
        lines.append("─" * 50)
        
        # Declaration
        if self._canon_declaration:
            lines.append("DECLARATION:")
            if self._canon_declaration.forms:
                form = self._canon_declaration.forms[0]
                lines.append(f"  Form: {form.kind}")
                lines.append(f"  Parameters: {form.params}")
            
            if self._canon_result:
                sig = self._canon_result.get_declaration_signature()
                if sig:
                    lines.append(f"  Signature: {sig}")
        
        lines.append("")
        lines.append("═" * 50)
        lines.append("Generated by Hermetic Geometry Canon v1.0")
        
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText("\n".join(lines))

    def _show_property_error(self, message: Optional[str]):
        if not self._property_error_label:
            return
        if not message:
            self._property_error_label.hide()
        else:
            self._property_error_label.setText(message)
            self._property_error_label.show()

    def _clear_calculator(self):
        if not self._calculator:
            return
        self._calculator.clear()
        self._updating_inputs = True
        for field in self._property_inputs.values():
            field.clear()
        self._updating_inputs = False
        self._show_property_error(None)
        self._current_payload = None
        self._view.set_payload(None)
        self._update_status(None)

    @staticmethod
    def _clear_layout(layout: QVBoxLayout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
                continue
            child_layout = item.layout()
            if child_layout is not None:
                Geometry3DWindow._clear_layout(child_layout)  # type: ignore[arg-type]
                continue
            spacer = item.spacerItem()
            if spacer is not None:
                continue

    @staticmethod
    def _format_value(value) -> str:
        if isinstance(value, float):
            return f"{value:.4f}".rstrip('0').rstrip('.')
        return str(value)

    # ------------------------------------------------------------------
    # View + clipboard helpers
    # ------------------------------------------------------------------
    def _on_zoom_in(self):
        self._view.zoom_in()

    def _on_zoom_out(self):
        self._view.zoom_out()

    def _on_fit_view(self):
        self._view.fit_scene()

    def _on_reset_view(self):
        self._view.reset_view()

    def _on_measure_mode_toggled(self, enabled: bool):
        self._view.set_measure_mode(enabled)
        if enabled:
            self._status_label.setText("Measure mode: Click two vertices to measure distance")
        else:
            self._update_status(self._current_payload)

    def _capture_snapshot(self):
        pixmap = self._view.grab()
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setPixmap(pixmap)

    def _copy_measurement_summary(self):
        title = self.windowTitle() or "3D Solid"
        lines = [f"{title} Measurements"]
        lines.append("═" * 40)
        appended = False
        
        # Include Canon provenance if available
        if self._use_canon_dsl and self._canon_verdict:
            lines.append("")
            lines.append("Canon Validation:")
            if self._canon_verdict.ok:
                lines.append("  ✓ Validated")
            else:
                lines.append("  ✗ Validation Failed")
            
            if self._canon_result:
                sig = self._canon_result.get_declaration_signature()
                if sig:
                    lines.append(f"  Signature: {sig[:24]}...")
            
            if self._canon_declaration and self._canon_declaration.forms:
                form = self._canon_declaration.forms[0]
                lines.append(f"  Form: {form.kind}")
            
            lines.append("")
            lines.append("─" * 40)
        
        # Properties from calculator or Canon state
        if self._calculator:
            lines.append("")
            lines.append("Properties:")
            for prop in self._calculator.properties():
                if prop.value is None:
                    continue
                formatted = f"{prop.value:.{prop.precision}f}".rstrip('0').rstrip('.')
                unit = f" {prop.unit}" if prop.unit else ""
                lines.append(f"  • {prop.name}: {formatted}{unit}")
                appended = True
        
        # Metadata from payload (includes Canon metrics)
        if self._current_payload and self._current_payload.metadata:
            lines.append("")
            lines.append("Derived Metrics:")
            for key, value in self._current_payload.metadata.items():  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
                pretty = key.replace('_', ' ').title()  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
                lines.append(f"  • {pretty}: {self._format_value(value)}")
                appended = True
        
        # Geometry stats
        if self._current_payload:
            lines.append("")
            lines.append("Geometry:")
            lines.append(f"  • Vertices: {len(self._current_payload.vertices)}")
            lines.append(f"  • Edges: {len(self._current_payload.edges)}")
            lines.append(f"  • Faces: {len(self._current_payload.faces)}")
            appended = True
        
        if not appended:
            lines.append("No values calculated yet.")
        
        lines.append("")
        lines.append("═" * 40)
        
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText("\n".join(lines))

    @staticmethod
    @staticmethod
    def _primary_button_style() -> str:
        # Visual Liturgy: Use Magus (Violet) for primary actions
        return (
            f"QPushButton {{background-color: {COLORS['magus']}; color: {COLORS['light']}; border: none; padding: 10px 18px;"
            f"border-radius: 10px; font-weight: 600;}}"
            f"QPushButton:hover {{background-color: {COLORS['magus_hover']};}}"
            f"QPushButton:pressed {{background-color: {COLORS['magus_dark']};}}"
        )

    @staticmethod
    def _secondary_button_style() -> str:
        # Visual Liturgy: Neutral secondary style using canonical tokens
        return (
            f"QPushButton {{background-color: {COLORS['light']}; color: {COLORS['void']}; border: 1px solid {COLORS['ash']}; padding: 6px 10px;"
            f"border-radius: 8px; font-weight: 600;}}"
            f"QPushButton:hover {{background-color: {COLORS['magus_soft']}; border-color: {COLORS['mist']};}}"
            f"QPushButton:pressed {{background-color: {COLORS['surface_hover']};}}"
        )

    # ------------------------------------------------------------------
    # Cross-pillar actions
    # ------------------------------------------------------------------
    def _install_value_context_menu(self, input_field: QLineEdit):
        if not input_field:
            return
        input_field.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        input_field.customContextMenuRequested.connect(
            lambda pos, field=input_field: self._show_value_context_menu(field, pos)  # type: ignore[reportUnknownArgumentType, reportUnknownLambdaType, reportUnknownMemberType]
        )

    def _show_value_context_menu(self, line_edit: QLineEdit, position):
        menu = line_edit.createStandardContextMenu()
        if menu is None:
            menu = QMenu(line_edit)
        self._style_value_menu(menu)
        numeric_value = self._parse_numeric_value(line_edit.text())
        if numeric_value is not None:
            menu.addSeparator()
            send_action = QAction("Send to Quadset Analysis", menu)
            send_action.triggered.connect(
                lambda _, value=numeric_value: self._send_value_to_quadset(value)
            )
            lookup_action = QAction("Look up in Database", menu)
            lookup_action.triggered.connect(
                lambda _, value=numeric_value: self._lookup_value_in_database(value)
            )
            if not self.window_manager:
                send_action.setEnabled(False)
                lookup_action.setEnabled(False)
            menu.addAction(send_action)
            menu.addAction(lookup_action)
        menu.exec(line_edit.mapToGlobal(position))

    @staticmethod
    def _style_value_menu(menu: QMenu):
        if not menu:
            return
        menu.setStyleSheet(
            """
            QMenu {
                background-color: #ffffff;
                color: #0f172a;
                border: 1px solid #cbd5e1;
                padding: 4px 0px;
            }
            QMenu::item {
                padding: 6px 16px;
            }
            QMenu::item:selected {
                background-color: #e0e7ff;
                color: #1d4ed8;
            }
            QMenu::separator {
                height: 1px;
                margin: 4px 6px;
                background-color: #e2e8f0;
            }
            """
        )

    @staticmethod
    def _parse_numeric_value(text: str) -> Optional[float]:
        if not text:
            return None
        try:
            return float(text)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _round_cross_pillar_value(value: float) -> int:
        return int(round(value))

    def _send_value_to_quadset(self, value: float):
        rounded_value = self._round_cross_pillar_value(value)
        navigation_bus.request_window.emit(
            "quadset_analysis",
            {
                "window_manager": self.window_manager,
                "initial_value": rounded_value
            }
        )

    def _lookup_value_in_database(self, value: float):
        rounded_value = self._round_cross_pillar_value(value)
        navigation_bus.request_window.emit(
            "gematria_saved_calculations",
            {
                "window_manager": self.window_manager,
                "initial_value": rounded_value,
                "allow_multiple": False 
            }
        )