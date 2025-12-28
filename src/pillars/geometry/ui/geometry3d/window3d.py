"""Standalone window hosting the 3D geometry view."""
from __future__ import annotations

from typing import Any, Dict, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
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
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtGui import QAction, QDoubleValidator

from ...shared.solid_payload import SolidPayload
from shared.ui import WindowManager
from shared.signals.navigation_bus import navigation_bus
from .view3d import Geometry3DView


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
            QTabWidget::pane { border: 1px solid #e2e8f0; border-radius: 10px; background: transparent; }
            QTabBar::tab { padding: 8px 16px; margin: 2px; font-weight: 600; }
            QTabBar::tab:selected { background: #e0e7ff; border-radius: 6px; color: #1d4ed8; }
            QTabBar::tab:!selected { background: #f8fafc; color: #64748b; }
            """
        )
        
        # Core properties tab
        core_scroll = QScrollArea()
        core_scroll.setWidgetResizable(True)
        core_scroll.setStyleSheet("QScrollArea {border: none; background: transparent;}")
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
        advanced_scroll.setStyleSheet("QScrollArea {border: none; background: transparent;}")
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
        status = QLabel("No solid loaded")
        status.setStyleSheet("color: #64748b; font-size: 10.5pt;")
        header.addWidget(status)
        self._status_label = status
        layout.addLayout(header)

        frame = QFrame()
        frame.setStyleSheet("QFrame {background-color: #0f172a; border-radius: 12px;}")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.addWidget(self._view)
        layout.addWidget(frame, 1)
        return panel

    def _build_controls_panel(self) -> QWidget:
        panel = QFrame()
        panel.setMinimumWidth(260)
        panel.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 16px;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        title = QLabel("Viewport Console")
        title.setStyleSheet("color: #0f172a; font-size: 14pt; font-weight: 700;")
        layout.addWidget(title)

        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        tabs.setStyleSheet(
            """
            QTabWidget::pane { border: 1px solid #e2e8f0; border-radius: 10px; }
            QTabBar::tab { padding: 6px 12px; margin: 2px; }
            QTabBar::tab:selected { background: #e0e7ff; border-radius: 6px; }
            """
        )
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
            cb.toggled.connect(lambda checked, k=key: self._view.set_sphere_visible(k, checked))
            layout.addWidget(cb)
            self._sphere_checkboxes[key] = cb

        # Measure tool button
        measure_btn = QPushButton("📏 Measure Tool")
        measure_btn.setCheckable(True)
        measure_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        measure_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: 600;
            }
            QPushButton:checked {
                background-color: #fef3c7;
                border-color: #f59e0b;
                color: #92400e;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        measure_btn.toggled.connect(self._on_measure_mode_toggled)
        layout.addWidget(measure_btn)
        self._measure_button = measure_btn

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

        info_frame = QFrame()
        info_frame.setStyleSheet(
            """
            QFrame {
                background-color: #eff6ff;
                border: 1px solid #dbeafe;
                border-radius: 8px;
            }
            """
        )
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(14, 12, 14, 12)
        info_text = QLabel("Snapshots and measurement summaries copy directly to your clipboard.")
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #1e40af; font-size: 9pt;")
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
        if not self._status_label:
            return
        if not payload:
            self._status_label.setText("No solid loaded")
            return
        vertex_count = len(payload.vertices)
        edge_count = len(payload.edges)
        face_count = len(payload.faces)
        self._status_label.setText(f"{vertex_count} vertices · {edge_count} edges · {face_count} faces")

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

        for key, value in payload.metadata.items():
            layout.addWidget(self._build_metadata_row(key, value))
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
        header.addStretch(1)
        layout.addLayout(header)

        input_field = QLineEdit()
        input_field.setPlaceholderText("0.0")
        editable = bool(getattr(prop, 'editable', True))
        base_style = (
            "QLineEdit {background-color: %s; border: 1px solid #cbd5e1; border-radius: 6px; padding: 8px;"
            "font-size: 11pt; color: #0f172a;} QLineEdit:focus {border-color: #6366f1;}"
        )
        bg_color = "white" if editable else "#f1f5f9"
        input_field.setStyleSheet(base_style % bg_color)
        input_field.setReadOnly(not editable)
        validator = QDoubleValidator(0.0001, 1e9, prop.precision)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        input_field.setValidator(validator)
        if editable:
            input_field.editingFinished.connect(
                lambda key=prop.key, field=input_field: self._commit_property_change(key, field)
            )
        self._install_value_context_menu(input_field)
        layout.addWidget(input_field)
        self._property_inputs[prop.key] = input_field
        return frame

    def _commit_property_change(self, key: str, field: QLineEdit):
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
        if not self._calculator.set_property(key, value):
            self._show_property_error("Value outside valid range")
            return
        self._show_property_error(None)
        self._sync_property_inputs()

    def _sync_property_inputs(self):
        calculator = self._calculator
        if not calculator:
            return
        self._updating_inputs = True
        for prop in calculator.properties():
            field = self._property_inputs.get(prop.key)
            if field is None:
                continue
            # Safety check: ensure Qt widget still exists
            try:
                if prop.value is None:
                    field.clear()
                elif isinstance(prop.value, str):
                    # String values (e.g., symmetry_group_name, dual_solid_name)
                    field.setText(prop.value)
                else:
                    # Numeric values
                    formatted = f"{prop.value:.{prop.precision}f}".rstrip('0').rstrip('.')
                    field.setText(formatted)
            except RuntimeError:
                # Widget was deleted, skip it
                continue
        self._updating_inputs = False
        payload = calculator.payload()
        self._current_payload = payload
        self._view.set_payload(payload)
        self._update_status(payload)

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
        appended = False
        if self._calculator:
            for prop in self._calculator.properties():
                if prop.value is None:
                    continue
                formatted = f"{prop.value:.{prop.precision}f}".rstrip('0').rstrip('.')
                unit = f" {prop.unit}" if prop.unit else ""
                lines.append(f"• {prop.name}: {formatted}{unit}")
                appended = True
        elif self._current_payload and self._current_payload.metadata:
            for key, value in self._current_payload.metadata.items():
                pretty = key.replace('_', ' ').title()
                lines.append(f"• {pretty}: {self._format_value(value)}")
                appended = True
        if not appended:
            lines.append("No values calculated yet.")
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText("\n".join(lines))

    @staticmethod
    def _primary_button_style() -> str:
        return (
            "QPushButton {background-color: #1d4ed8; color: white; border: none; padding: 10px 18px;"
            "border-radius: 10px; font-weight: 600;}"
            "QPushButton:hover {background-color: #2563eb;}"
            "QPushButton:pressed {background-color: #1e3a8a;}"
        )

    @staticmethod
    def _secondary_button_style() -> str:
        return (
            "QPushButton {background-color: white; color: #0f172a; border: 1px solid #cbd5e1; padding: 6px 10px;"
            "border-radius: 8px; font-weight: 600;}"
            "QPushButton:hover {background-color: #eef2ff; border-color: #94a3b8;}"
            "QPushButton:pressed {background-color: #e0e7ff;}"
        )

    # ------------------------------------------------------------------
    # Cross-pillar actions
    # ------------------------------------------------------------------
    def _install_value_context_menu(self, input_field: QLineEdit):
        if not input_field:
            return
        input_field.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        input_field.customContextMenuRequested.connect(
            lambda pos, field=input_field: self._show_value_context_menu(field, pos)
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
            "tq_quadset_analysis",
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