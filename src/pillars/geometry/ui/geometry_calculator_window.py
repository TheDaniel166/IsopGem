"""Geometry calculator window with 3-pane layout."""
from typing import Dict, Optional
import math

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QCheckBox, QSplitter, QFrame,
    QApplication, QComboBox, QTabWidget, QToolButton, QMenu, QGroupBox
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QDoubleValidator, QCursor, QAction, QColor
from pillars.geometry.services import GeometricShape
from shared.ui import WindowManager
from .geometry_scene import GeometryScene
from .geometry_view import GeometryView
from .scene_adapter import build_scene_payload


class GeometryCalculatorWindow(QMainWindow):
    """3-pane geometry calculator window."""
    
    def __init__(
        self,
        shape: GeometricShape,
        window_manager: Optional[WindowManager] = None,
        parent=None,
    ):
        """
        Initialize the geometry calculator window.
        
        Args:
            shape: The geometric shape instance to calculate
            parent: Parent widget
        """
        super().__init__(parent)
        self.shape = shape
        self.window_manager = window_manager
        self.property_inputs: Dict[str, QLineEdit] = {}
        self.updating = False  # Flag to prevent circular updates
        self.scene = GeometryScene()
        self.splitter = None
        self.calc_pane = None
        self.viewport_pane = None
        self.viewport = None
        self.controls_pane = None
        self.calc_collapsed = False
        self.controls_collapsed = False
        self._saved_splitter_sizes = [360, 600, 240]
        self.calc_toggle_btn: Optional[QPushButton] = None
        self.controls_toggle_btn: Optional[QPushButton] = None
        self.show_labels_cb: Optional[QCheckBox] = None
        self.show_axes_cb: Optional[QCheckBox] = None
        self.theme_combo: Optional[QComboBox] = None
        self.overlay_axes_btn: Optional[QToolButton] = None
        self.overlay_labels_btn: Optional[QToolButton] = None
        self.overlay_measure_btn: Optional[QToolButton] = None
        self.overlay_snapshot_btn: Optional[QToolButton] = None
        
        self.setWindowTitle(f"{shape.name} Calculator")
        self.setMinimumSize(1200, 700)
        
        # Set window background
        self.setStyleSheet("background-color: #f8fafc;")
        
        # Star rendering toggle (for hexagram)
        self.star_toggle = None
        
        # Track widget containers for styling
        self.property_cards = {}

        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the 3-pane interface."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        toolbar = self._create_layout_toolbar()
        layout.addWidget(toolbar)
        
        # Create splitter for resizable panes
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #e2e8f0;
            }
        """)
        splitter.setChildrenCollapsible(False)
        
        # Build panes (controls first so overlay can bind to toggles)
        calc_pane = self._create_calculation_pane()
        controls_pane = self._create_controls_pane()
        viewport_pane = self._create_viewport_pane()

        splitter.addWidget(calc_pane)
        splitter.addWidget(viewport_pane)
        splitter.addWidget(controls_pane)
        
        # Set initial sizes (30% / 50% / 20%)
        splitter.setSizes([360, 600, 240])
        layout.addWidget(splitter, 1)

        self.splitter = splitter
        self.calc_pane = calc_pane
        self.viewport_pane = viewport_pane
        self.controls_pane = controls_pane
        splitter.splitterMoved.connect(self._record_splitter_sizes)
        self._update_splitter_sizes()
        
        # Initialize fields from shape state
        self._update_all_fields()
        self._update_viewport()
    
    def _create_calculation_pane(self) -> QWidget:
        """Create the left calculation pane."""
        pane = QWidget()
        pane.setStyleSheet("background-color: #ffffff; border-right: 1px solid #e2e8f0;")
        pane.setMinimumWidth(320)
        
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Title
        title_label = QLabel(f"📐 {self.shape.name}")
        title_label.setStyleSheet("""
            font-size: 20pt;
            font-weight: 800;
            color: #0f172a;
            letter-spacing: -0.5px;
        """)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(self.shape.description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #64748b; font-size: 11pt;")
        layout.addWidget(desc_label)
        
        # Calculation Hint
        hint_label = QLabel(self.shape.calculation_hint)
        hint_label.setStyleSheet("color: #0f172a; font-size: 10pt; font-style: italic; background-color: #f1f5f9; padding: 6px; border-radius: 4px;")
        hint_label.setWordWrap(True)
        layout.addWidget(hint_label)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #e2e8f0;")
        layout.addWidget(line)
        
        layout.addSpacing(8)
        
        # Scroll area for properties
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f5f9;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
        """)
        
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: transparent;")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(12)
        scroll_layout.setContentsMargins(0, 0, 4, 0) # Right margin for scrollbar
        
        # Create input fields for all properties
        for prop in self.shape.get_all_properties():
            prop_widget = self._create_property_input(prop)
            scroll_layout.addWidget(prop_widget)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear All")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #fee2e2;
                color: #dc2626;
                padding: 10px;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #fecaca;
            }
            QPushButton:pressed {
                background-color: #fca5a5;
            }
        """)
        clear_btn.clicked.connect(self._clear_all)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        return pane
    
    def _create_property_input(self, prop) -> QWidget:
        """Create an input field for a property."""
        from pillars.geometry.services import ShapeProperty
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QFrame:hover {
                border-color: #cbd5e1;
                background-color: #f1f5f9;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Header (Name + Unit)
        header_layout = QHBoxLayout()
        name_label = QLabel(prop.name)
        name_label.setStyleSheet("""
            font-weight: 600;
            color: #334155;
            font-size: 10pt;
            border: none;
            background: transparent;
        """)
        header_layout.addWidget(name_label)
        
        if prop.unit:
            unit_label = QLabel(prop.unit)
            unit_label.setStyleSheet("""
                color: #94a3b8;
                font-size: 9pt;
                border: none;
                background: transparent;
            """)
            header_layout.addWidget(unit_label)
            
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Input area
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)
        
        input_field = QLineEdit()
        input_field.setPlaceholderText("0.0")
        input_field.setStyleSheet("""
            QLineEdit {
                font-size: 11pt;
                padding: 6px 8px;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                background-color: white;
                color: #0f172a;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                border-width: 2px;
                padding: 5px 7px; /* Adjust for border width */
            }
        """)
        self._install_value_context_menu(input_field)
        
        # Only allow positive numbers
        validator = QDoubleValidator(0.0001, 999999999, 6)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        input_field.setValidator(validator)
        
        # Store reference
        self.property_inputs[prop.key] = input_field
        self.property_cards[prop.key] = container
        
        # Apply initial style (Amber for editable, Slate for readonly)
        if not prop.readonly:
            container.setStyleSheet("""
                QFrame {
                    background-color: #fffbeb; 
                    border: 1px solid #fcd34d;
                    border-radius: 8px;
                }
                QFrame:hover {
                    border-color: #fbbf24;
                }
            """)
        
        # Connect signal
        
        # Connect signal
        if not prop.readonly:
            input_field.textChanged.connect(
                lambda text, key=prop.key: self._on_property_changed(key, text)
            )
        else:
            input_field.setReadOnly(True)
            input_field.setStyleSheet("""
                QLineEdit {
                    font-size: 11pt;
                    padding: 6px 8px;
                    border: 1px solid #e2e8f0;
                    border-radius: 4px;
                    background-color: #f1f5f9;
                    color: #64748b;
                }
            """)
        
        input_layout.addWidget(input_field)
        
        # Copy button
        copy_btn = QPushButton("📋")
        copy_btn.setFixedSize(32, 32)
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.setToolTip("Copy value")
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                color: #64748b;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                color: #3b82f6;
                border-color: #cbd5e1;
            }
            QPushButton:pressed {
                background-color: #e2e8f0;
            }
        """)
        def copy_value():
            clipboard = QApplication.clipboard()
            if clipboard:
                clipboard.setText(input_field.text())
        copy_btn.clicked.connect(copy_value)
        input_layout.addWidget(copy_btn)
        
        layout.addLayout(input_layout)
        
        return container
    
    def _create_viewport_pane(self) -> QWidget:
        """Create the center viewport pane."""
        pane = QWidget()
        pane.setStyleSheet("background-color: #f8fafc;")
        
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Visualization")
        title_label.setStyleSheet("""
            font-size: 14pt;
            font-weight: 700;
            color: #334155;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)

        overlay_row = QHBoxLayout()
        overlay_row.setContentsMargins(0, 0, 0, 0)
        overlay_row.addStretch()
        overlay = self._build_viewport_overlay()
        overlay_row.addWidget(overlay)
        layout.addLayout(overlay_row)
        
        # Viewport container (for shadow/border)
        viewport_container = QFrame()
        viewport_container.setStyleSheet(
            "QFrame {background-color: white; border: 1px solid #e2e8f0; border-radius: 8px;}"
        )
        viewport_layout = QVBoxLayout(viewport_container)
        viewport_layout.setContentsMargins(1, 1, 1, 1) # Thin border
        
        self.viewport = GeometryView(self.scene)
        self.viewport.setStyleSheet("border: none; border-radius: 7px; background-color: transparent;")

        self.scene.set_axes_visible(True)
        self.scene.set_labels_visible(True)
        
        viewport_layout.addWidget(self.viewport)
        layout.addWidget(viewport_container)

        self._sync_overlay_toggles()
        
        return pane
    
    def _create_controls_pane(self) -> QWidget:
        """Create the right controls pane with advanced tabs."""
        pane = QWidget()
        pane.setStyleSheet("background-color: #ffffff; border-left: 1px solid #e2e8f0;")
        pane.setMinimumWidth(260)

        layout = QVBoxLayout(pane)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title_label = QLabel("Visualization Console")
        title_label.setStyleSheet(
            "color: #0f172a; font-size: 13pt; font-weight: 700; letter-spacing: 0.5px;"
        )
        layout.addWidget(title_label)

        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        tabs.setStyleSheet(
            """
            QTabWidget::pane { border: 1px solid #e2e8f0; border-radius: 10px; }
            QTabBar::tab { padding: 6px 12px; }
            QTabBar::tab:selected { background: #e0e7ff; border-radius: 6px; }
            """
        )
        tabs.addTab(self._build_display_tab(), "Display")
        tabs.addTab(self._build_camera_tab(), "Camera")
        tabs.addTab(self._build_measure_tab(), "Measure")
        tabs.addTab(self._build_output_tab(), "Output")
        layout.addWidget(tabs)

        return pane

    def _create_layout_toolbar(self) -> QWidget:
        bar = QFrame()
        bar.setStyleSheet(
            """
            QFrame {
                background-color: #eef2ff;
                border-bottom: 1px solid #e2e8f0;
            }
            """
        )
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(18, 10, 18, 10)
        layout.setSpacing(12)

        hint = QLabel("Layout Controls")
        hint.setStyleSheet("color: #1e3a8a; font-weight: 600; letter-spacing: 0.4px;")
        layout.addWidget(hint)
        layout.addStretch()

        self.calc_toggle_btn = QPushButton("Hide Inputs")
        self.calc_toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.calc_toggle_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e0e7ff;
                color: #312e81;
                padding: 6px 12px;
                border: 1px solid #c7d2fe;
                border-radius: 999px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #c7d2fe;
            }
            """
        )
        self.calc_toggle_btn.clicked.connect(self._toggle_calculation_pane)
        layout.addWidget(self.calc_toggle_btn)

        self.controls_toggle_btn = QPushButton("Hide Display Options")
        self.controls_toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.controls_toggle_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e0e7ff;
                color: #312e81;
                padding: 6px 12px;
                border: 1px solid #c7d2fe;
                border-radius: 999px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #c7d2fe;
            }
            """
        )
        self.controls_toggle_btn.clicked.connect(self._toggle_controls_pane)
        layout.addWidget(self.controls_toggle_btn)

        return bar

    def _build_viewport_overlay(self) -> QWidget:
        chip = QFrame()
        chip.setStyleSheet(
            """
            QFrame {
                background: rgba(15,23,42,0.08);
                border: 1px solid rgba(148,163,184,0.6);
                border-radius: 999px;
            }
            """
        )
        layout = QHBoxLayout(chip)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(6)



        self.overlay_axes_btn = self._create_overlay_toggle(
            "Axes",
            lambda state: self.show_axes_cb.setChecked(state) if self.show_axes_cb else None,
        )
        layout.addWidget(self.overlay_axes_btn)

        self.overlay_labels_btn = self._create_overlay_toggle(
            "Labels",
            lambda state: self.show_labels_cb.setChecked(state) if self.show_labels_cb else None,
        )
        layout.addWidget(self.overlay_labels_btn)

        self.overlay_measure_btn = self._create_overlay_toggle(
            "Measure",
            lambda state: self.viewport.set_measurement_mode(state),
        )
        layout.addWidget(self.overlay_measure_btn)

        self.overlay_snapshot_btn = QToolButton()
        self.overlay_snapshot_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.overlay_snapshot_btn.setToolTip("Copy snapshot to clipboard")
        self.overlay_snapshot_btn.setText("📸")
        self.overlay_snapshot_btn.setStyleSheet(
            """
            QToolButton {
                border: none;
                font-size: 12pt;
                padding: 4px;
            }
            QToolButton:hover {
                color: #1d4ed8;
            }
            """
        )
        self.overlay_snapshot_btn.clicked.connect(self._capture_snapshot)
        layout.addWidget(self.overlay_snapshot_btn)

        return chip

    def _create_overlay_toggle(self, label: str, callback) -> QToolButton:
        btn = QToolButton()
        btn.setText(label)
        btn.setCheckable(True)
        btn.setAutoRaise(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(
            """
            QToolButton {
                padding: 4px 10px;
                border-radius: 999px;
                color: #0f172a;
            }
            QToolButton:checked {
                background-color: #e0e7ff;
                color: #1d4ed8;
            }
            """
        )
        btn.toggled.connect(callback)
        return btn

    def _secondary_button_style(self) -> str:
        return (
            "QPushButton {background-color: #f1f5f9; color: #1f2937; border: 1px solid #cbd5e1;"
            "border-radius: 8px; padding: 8px 12px; font-weight: 600;}"
            "QPushButton:hover {background-color: #e2e8f0;}"
            "QPushButton:pressed {background-color: #cbd5e1;}"
        )

    def _build_display_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        self.show_labels_cb = self._create_checkbox("Show Labels", True)
        self.show_labels_cb.toggled.connect(self._on_display_toggle)
        layout.addWidget(self.show_labels_cb)



        self.show_axes_cb = self._create_checkbox("Show Axes", True)
        self.show_axes_cb.toggled.connect(self._on_display_toggle)
        layout.addWidget(self.show_axes_cb)

        try:
            from pillars.geometry.services import RegularPolygonShape

            if isinstance(self.shape, RegularPolygonShape) and getattr(self.shape, "num_sides", 0) == 6:
                self.star_toggle = self._create_checkbox("Draw as Star (Hexagram)", False)
                self.star_toggle.toggled.connect(self._on_display_toggle)
                layout.addWidget(self.star_toggle)
        except Exception:
            pass

        theme_label = QLabel("Scene Theme")
        theme_label.setStyleSheet("color: #475569; font-weight: 600;")
        layout.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Daylight", "Midnight", "Slate", "Pearl"])
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        layout.addWidget(self.theme_combo)
        self.theme_combo.setCurrentText("Daylight")
        self._on_theme_changed("Daylight")

        layout.addStretch()
        return tab

    def _build_camera_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

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
        fit_btn = QPushButton("Fit Shape")
        fit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        fit_btn.setStyleSheet(self._secondary_button_style())
        fit_btn.clicked.connect(self._on_fit_shape)
        view_row.addWidget(fit_btn)

        reset_btn = QPushButton("Reset View")
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.setStyleSheet(self._secondary_button_style())
        reset_btn.clicked.connect(self._on_reset_view)
        view_row.addWidget(reset_btn)
        layout.addLayout(view_row)

        layout.addStretch()
        return tab

    def _build_measure_tab(self) -> QWidget:
        """Create controls for customizing measurements."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Stats Group
        stats_group = QGroupBox("Current Measurement")
        stats_group.setStyleSheet("QGroupBox { font-weight: bold; color: #1e3a8a; }")
        stats_layout = QVBoxLayout(stats_group)
        stats_layout.setSpacing(8)
        
        self.lbl_perim = QLabel("Perimeter: -")
        self.lbl_perim.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.lbl_perim.customContextMenuRequested.connect(lambda p: self._show_measurement_context_menu(p, "perimeter"))
        
        self.lbl_area = QLabel("Area: -")
        self.lbl_area.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.lbl_area.customContextMenuRequested.connect(lambda p: self._show_measurement_context_menu(p, "area"))
        self.btn_open_shape = QPushButton("Open as Shape")
        self.btn_open_shape.setEnabled(False)
        self.btn_open_shape.setStyleSheet(self._secondary_button_style())
        self.btn_open_shape.clicked.connect(self._open_measured_shape)
        
        stats_layout.addWidget(self.lbl_perim)
        stats_layout.addWidget(self.lbl_area)
        stats_layout.addWidget(self.btn_open_shape)
        layout.addWidget(stats_group)
        
        # Show Area Control
        area_layout = QHBoxLayout()
        self.show_area_cb = QCheckBox("Calculate Area (3+ points)")
        self.show_area_cb.setChecked(True)
        self.show_area_cb.setStyleSheet("""
            QCheckBox { color: #475569; font-weight: 600; }
            QCheckBox::indicator { width: 16px; height: 16px; }
        """)
        
        def toggle_area(state):
            if hasattr(self.scene, "set_measurement_show_area"):
                self.scene.set_measurement_show_area(state)
        
        self.show_area_cb.toggled.connect(toggle_area)
        area_layout.addWidget(self.show_area_cb)
        layout.addLayout(area_layout)

        # Font Size Control
        size_layout = QVBoxLayout()
        size_layout.setSpacing(4)
        
        size_label_row = QHBoxLayout()
        size_label = QLabel("Font Size")
        size_label.setStyleSheet("color: #475569; font-weight: 600;")
        self.size_val_label = QLabel("9.0pt")
        self.size_val_label.setStyleSheet("color: #64748b; font-weight: 600;")
        size_label_row.addWidget(size_label)
        size_label_row.addStretch()
        size_label_row.addWidget(self.size_val_label)
        size_layout.addLayout(size_label_row)
        
        from PyQt6.QtWidgets import QSlider
        size_slider = QSlider(Qt.Orientation.Horizontal)
        size_slider.setMinimum(8)
        size_slider.setMaximum(24)
        size_slider.setValue(9)
        size_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #cbd5e1;
                height: 4px;
                background: #f1f5f9;
                margin: 2px 0;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #3b82f6;
                border: 1px solid #3b82f6;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
        """)
        
        def update_size(val):
            self.size_val_label.setText(f"{val}pt")
            if hasattr(self.scene, "set_measurement_font_size"):
                self.scene.set_measurement_font_size(float(val))
                
        size_slider.valueChanged.connect(update_size)
        size_layout.addWidget(size_slider)
        layout.addLayout(size_layout)
        
        # Line Color Control
        line_col_layout = QVBoxLayout()
        line_col_layout.setSpacing(6)
        line_col_label = QLabel("Line Color")
        line_col_label.setStyleSheet("color: #475569; font-weight: 600;")
        line_col_layout.addWidget(line_col_label)
        
        line_combo = QComboBox()
        line_combo.addItems(["Orange", "Blue", "Emerald", "Black", "Red"])
        
        def get_color(name):
            if name == "Orange": return QColor(234, 88, 12)
            if name == "Blue": return QColor(37, 99, 235)
            if name == "Emerald": return QColor(16, 185, 129)
            if name == "Black": return QColor(0, 0, 0)
            if name == "Red": return QColor(220, 38, 38)
            return QColor(234, 88, 12)

        def update_line_color(name):
            if hasattr(self.scene, "set_measurement_line_color"):
                self.scene.set_measurement_line_color(get_color(name))
                
        line_combo.currentTextChanged.connect(update_line_color)
        line_col_layout.addWidget(line_combo)
        layout.addLayout(line_col_layout)

        # Text Color Control
        text_col_layout = QVBoxLayout()
        text_col_layout.setSpacing(6)
        text_col_label = QLabel("Text Color")
        text_col_label.setStyleSheet("color: #475569; font-weight: 600;")
        text_col_layout.addWidget(text_col_label)
        
        text_combo = QComboBox()
        text_combo.addItems(["White", "Black", "Match Line"])
        
        def update_text_color(name):
            col = QColor(255, 255, 255)
            if name == "Black":
                col = QColor(0, 0, 0)
            elif name == "Match Line":
                # Special logic handled in scene or we update here dynamically?
                # Scene handles 'use_line_color' flag or we just push the color.
                # Let's check current line combo
                col = get_color(line_combo.currentText())
            
            if hasattr(self.scene, "set_measurement_text_color"):
                self.scene.set_measurement_text_color(col)
        
        # Connect both combos to text update if match line is selected
        text_combo.currentTextChanged.connect(update_text_color)
        line_combo.currentTextChanged.connect(lambda _: update_text_color(text_combo.currentText()))

        text_col_layout.addWidget(text_combo)
        layout.addLayout(text_col_layout)

        layout.addStretch()
        
        # Connect signal
        if hasattr(self.scene, "measurementChanged"):
            self.scene.measurementChanged.connect(self._on_measurement_changed)
            
        return tab

    def _on_measurement_changed(self, data: dict):
        """Update stats labels based on measurement."""
        self._last_measurement_data = data # Store for context menu
        perim = data.get("perimeter", 0.0)
        area = data.get("area", 0.0)
        points = data.get("points", [])
        count = len(points)
        
        self.lbl_perim.setText(f"Perimeter: {perim:.2f}")
        self.lbl_area.setText(f"Area: {area:.2f}" if count >= 3 else "Area: -")
        
        # Update Open Button
        self._measured_points = points # Store for opening
        if count == 3:
            self.btn_open_shape.setText("Open as Triangle")
            self.btn_open_shape.setEnabled(True)
        elif count == 4:
            self.btn_open_shape.setText("Open as Quadrilateral")
            self.btn_open_shape.setEnabled(True)
        elif count >= 5:
            self.btn_open_shape.setText(f"Open as {count}-Gon")
            self.btn_open_shape.setEnabled(True)
        else:
            self.btn_open_shape.setText("Open as Shape")
            self.btn_open_shape.setEnabled(False)

    def _show_measurement_context_menu(self, pos: QPoint, type_key: str):
        """Show context menu for measurement labels."""
        if not hasattr(self, "_last_measurement_data"):
            return
            
        value = self._last_measurement_data.get(type_key, 0.0)
        if value <= 0:
            return
            
        menu = QMenu()
        
        # Copy Action
        copy_action = QAction("Copy Value", self)
        copy_action.triggered.connect(lambda: QApplication.clipboard().setText(str(value)))
        menu.addAction(copy_action)
        
        menu.addSeparator()
        
        # Send to Quadset Action
        send_action = QAction(f"Send {type_key.title()} to Quadset Analysis", self)
        send_action.triggered.connect(lambda: self._send_value_to_quadset(value))
        menu.addAction(send_action)
        
        # Map press to global coordinates
        sender = self.sender()
        if isinstance(sender, QLabel):
             menu.exec(sender.mapToGlobal(pos))
             
    def _open_measured_shape(self):
        """Open a new calculator window with the measured points."""
        if not hasattr(self, "_measured_points") or len(self._measured_points) < 3:
            return
            
        # Convert QPoints to tuples for the service
        points = [(p.x(), p.y()) for p in self._measured_points]
        
        from pillars.geometry.services.shape_detection_service import ShapeDetectionService
        shape = ShapeDetectionService.detect_from_points(points)
        
        if shape:
            if self.window_manager:
                self.window_manager.open_window(
                    f"geometry_{shape.name.lower().replace(' ', '_')}",
                    self.__class__,
                    allow_multiple=True,
                    shape=shape,
                    window_manager=self.window_manager
                )

    def _build_output_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

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
        info_layout.setContentsMargins(16, 16, 16, 16)

        info_text = QLabel("Snapshots and summaries copy directly to your clipboard for quick sharing.")
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #1e40af; font-size: 9pt;")
        info_layout.addWidget(info_text)
        layout.addWidget(info_frame)

        layout.addStretch()
        return tab
    
    def _create_checkbox(self, text: str, checked: bool) -> QCheckBox:
        """Create a styled checkbox."""
        cb = QCheckBox(text)
        cb.setChecked(checked)
        cb.setCursor(Qt.CursorShape.PointingHandCursor)
        cb.setStyleSheet("""
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
        """)
        return cb
    
    def _on_property_changed(self, key: str, text: str):
        """Handle property value change."""
        if self.updating:
            return
        
        if not text:
            return
        
        try:
            value = float(text)
            if value <= 0:
                return
            
            # Calculate all properties from this value
            if self.shape.set_property(key, value):
                self._update_all_fields()
                self._update_viewport()
        
        except ValueError:
            pass
    
    def _update_all_fields(self):
        """Update all input fields with current shape property values."""
        self.updating = True
        
        for prop in self.shape.get_all_properties():
            input_field = self.property_inputs[prop.key]
            if prop.value is not None:
                # Format without scientific notation
                formatted_value = f"{prop.value:.{prop.precision}f}".rstrip('0').rstrip('.')
                input_field.setText(formatted_value)
                
                # Solved State: Green
                if prop.key in self.property_cards:
                    self.property_cards[prop.key].setStyleSheet("""
                        QFrame {
                            background-color: #f0fdf4;
                            border: 1px solid #86efac;
                            border-radius: 8px;
                        }
                    """)
            else:
                input_field.clear()
                # Unsolved State: Revert to default
                if prop.key in self.property_cards:
                    if not prop.readonly:
                        # Required: Amber
                        self.property_cards[prop.key].setStyleSheet("""
                            QFrame {
                                background-color: #fffbeb; 
                                border: 1px solid #fcd34d;
                                border-radius: 8px;
                            }
                            QFrame:hover {
                                border-color: #fbbf24;
                            }
                        """)
                    else:
                        # Output: Default Slate
                        self.property_cards[prop.key].setStyleSheet("""
                            QFrame {
                                background-color: #f8fafc;
                                border: 1px solid #e2e8f0;
                                border-radius: 8px;
                            }
                        """)
        
        self.updating = False
    
    def _update_viewport(self):
        """Update the viewport with current shape."""
        drawing_data = self.shape.get_drawing_instructions()
        # Inject star flag for hexagram view if toggle exists
        if self.star_toggle is not None and self.star_toggle.isChecked():
            drawing_data['star'] = True
        labels = self.shape.get_label_positions()
        payload = build_scene_payload(drawing_data, labels)
        if payload.primitives:
            self.scene.set_payload(payload)
            self.viewport.fit_to_bounds(payload.bounds)
        else:
            self.scene.clear_payload()
    
    def _clear_all(self):
        """Clear all values."""
        self.updating = True
        
        # Clear shape
        self.shape.clear_all()
        
        # Clear input fields
        for input_field in self.property_inputs.values():
            input_field.clear()
        
        # Clear viewport
        self.scene.clear_payload()
        self.viewport.fit_to_bounds(None)
        
        self.updating = False
    
    def _on_display_toggle(self):
        """Handle display control toggles."""
        if self.show_labels_cb is not None:
            self.scene.set_labels_visible(self.show_labels_cb.isChecked())

        if self.show_axes_cb is not None:
            self.scene.set_axes_visible(self.show_axes_cb.isChecked())
        if self.star_toggle is not None and self.sender() is self.star_toggle:
            self._update_viewport()
        self._sync_overlay_toggles()

    def _sync_overlay_toggles(self):
        pairs = (

            (self.overlay_axes_btn, self.show_axes_cb),
            (self.overlay_labels_btn, self.show_labels_cb),
        )
        for btn, checkbox in pairs:
            if btn is None or checkbox is None:
                continue
            btn.blockSignals(True)
            btn.setChecked(checkbox.isChecked())
            btn.blockSignals(False)

    def _on_theme_changed(self, theme: str):
        self.scene.apply_theme(theme)
        if self.viewport:
            self.viewport.setBackgroundBrush(self.scene.backgroundBrush())

    def _on_zoom_in(self):
        if hasattr(self, "viewport") and self.viewport is not None:
            self.viewport.zoom_in()

    def _on_zoom_out(self):
        if hasattr(self, "viewport") and self.viewport is not None:
            self.viewport.zoom_out()

    def _on_fit_shape(self):
        if hasattr(self, "viewport") and self.viewport is not None:
            self.viewport.fit_scene()

    def _on_reset_view(self):
        if hasattr(self, "viewport") and self.viewport is not None:
            self.viewport.reset_view()

    def _capture_snapshot(self):
        if not hasattr(self, "viewport") or self.viewport is None:
            return
        pixmap = self.viewport.grab()
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setPixmap(pixmap)

    def _copy_measurement_summary(self):
        lines = [f"{self.shape.name} Measurements"]
        for prop in self.shape.get_all_properties():
            if prop.value is None:
                continue
            formatted_value = f"{prop.value:.{prop.precision}f}".rstrip('0').rstrip('.')
            unit = f" {prop.unit}" if prop.unit else ""
            lines.append(f"• {prop.name}: {formatted_value}{unit}")
        if len(lines) == 1:
            lines.append("No values calculated yet.")
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText("\n".join(lines))

    def _install_value_context_menu(self, input_field: QLineEdit):
        """Attach cross-pillar context menu actions to calculator inputs."""
        if not input_field:
            return
        input_field.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        input_field.customContextMenuRequested.connect(
            lambda pos, field=input_field: self._show_value_context_menu(field, pos)
        )

    def _show_value_context_menu(self, line_edit: QLineEdit, position):
        """Append cross-pillar actions to the standard edit menu."""
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
        """Apply a readable light theme to context menus."""
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
        """Safely parse text into a floating point number."""
        if not text:
            return None
        try:
            return float(text)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _round_cross_pillar_value(value: float) -> int:
        """Round values before sending to other tool windows."""
        return int(round(value))

    def _send_value_to_quadset(self, value: float):
        """Send rounded number to the Quadset Analysis tool."""
        if not self.window_manager:
            return
        rounded_value = self._round_cross_pillar_value(value)
        from pillars.tq.ui.quadset_analysis_window import QuadsetAnalysisWindow

        window = self.window_manager.open_window(
            "quadset_analysis",
            QuadsetAnalysisWindow,
            window_manager=self.window_manager
        )
        if not window:
            return
        input_widget = getattr(window, "input_field", None)
        if input_widget is not None:
            input_widget.setText(str(rounded_value))
            window.raise_()
            window.activateWindow()

    def _lookup_value_in_database(self, value: float):
        """Open Saved Calculations with the value filter pre-filled."""
        if not self.window_manager:
            return
        rounded_value = self._round_cross_pillar_value(value)
        from pillars.gematria.ui.saved_calculations_window import SavedCalculationsWindow

        window = self.window_manager.open_window(
            "saved_calculations",
            SavedCalculationsWindow,
            allow_multiple=False,
        )
        if not window:
            return
        value_field = getattr(window, "value_input", None)
        if value_field is not None:
            value_field.setText(str(rounded_value))
        search_method = getattr(window, "_search", None)
        if callable(search_method):
            search_method()
        window.raise_()
        window.activateWindow()

    def _toggle_calculation_pane(self):
        if not self.calc_pane or not self.splitter:
            return
        self.calc_collapsed = not self.calc_collapsed
        self.calc_pane.setVisible(not self.calc_collapsed)
        if self.calc_toggle_btn:
            label = "Show Inputs" if self.calc_collapsed else "Hide Inputs"
            self.calc_toggle_btn.setText(label)
        self._update_splitter_sizes()

    def _toggle_controls_pane(self):
        if not self.controls_pane or not self.splitter:
            return
        self.controls_collapsed = not self.controls_collapsed
        self.controls_pane.setVisible(not self.controls_collapsed)
        if self.controls_toggle_btn:
            label = "Show Display Options" if self.controls_collapsed else "Hide Display Options"
            self.controls_toggle_btn.setText(label)
        self._update_splitter_sizes()

    def _update_splitter_sizes(self):
        if not self.splitter:
            return
        sizes = list(self._saved_splitter_sizes)
        if self.calc_collapsed:
            sizes[1] += sizes[0]
            sizes[0] = 0
        if self.controls_collapsed:
            sizes[1] += sizes[2]
            sizes[2] = 0
        if sizes[1] <= 0:
            sizes[1] = 1
        self.splitter.setSizes(sizes)

    def _record_splitter_sizes(self, *_):
        if not self.splitter:
            return
        if self.calc_collapsed or self.controls_collapsed:
            return
        self._saved_splitter_sizes = self.splitter.sizes()
