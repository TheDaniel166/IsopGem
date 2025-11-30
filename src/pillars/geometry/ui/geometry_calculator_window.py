"""Geometry calculator window with 3-pane layout."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QScrollArea, QCheckBox, QSplitter, QFrame,
    QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator, QCursor
from pillars.geometry.services import GeometricShape
from .geometry_viewport import GeometryViewport


class GeometryCalculatorWindow(QMainWindow):
    """3-pane geometry calculator window."""
    
    def __init__(self, shape: GeometricShape, parent=None):
        """
        Initialize the geometry calculator window.
        
        Args:
            shape: The geometric shape instance to calculate
            parent: Parent widget
        """
        super().__init__(parent)
        self.shape = shape
        self.property_inputs = {}  # key -> QLineEdit
        self.updating = False  # Flag to prevent circular updates
        
        self.setWindowTitle(f"{shape.name} Calculator")
        self.setMinimumSize(1200, 700)
        
        # Set window background
        self.setStyleSheet("background-color: #f8fafc;")
        
        self._setup_ui()
        
        # Star rendering toggle (for hexagram)
        self.star_toggle = None
        
    def _setup_ui(self):
        """Set up the 3-pane interface."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create splitter for resizable panes
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #e2e8f0;
            }
        """)
        
        # Left pane: Calculation controls
        calc_pane = self._create_calculation_pane()
        splitter.addWidget(calc_pane)
        
        # Center pane: Viewport
        viewport_pane = self._create_viewport_pane()
        splitter.addWidget(viewport_pane)
        
        # Right pane: Display controls
        controls_pane = self._create_controls_pane()
        splitter.addWidget(controls_pane)
        
        # Set initial sizes (30% / 50% / 20%)
        splitter.setSizes([360, 600, 240])
        
        layout.addWidget(splitter)
    
    def _create_calculation_pane(self) -> QWidget:
        """Create the left calculation pane."""
        pane = QWidget()
        pane.setStyleSheet("background-color: #ffffff; border-right: 1px solid #e2e8f0;")
        
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
        desc_label.setStyleSheet("color: #64748b; font-size: 10pt; line-height: 1.4;")
        layout.addWidget(desc_label)
        
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
        
        # Only allow positive numbers
        validator = QDoubleValidator(0.0001, 999999999, 6)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        input_field.setValidator(validator)
        
        # Store reference
        self.property_inputs[prop.key] = input_field
        
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
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(input_field.text()))
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
        
        # Viewport container (for shadow/border)
        viewport_container = QFrame()
        viewport_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        viewport_layout = QVBoxLayout(viewport_container)
        viewport_layout.setContentsMargins(1, 1, 1, 1) # Thin border
        
        self.viewport = GeometryViewport()
        # Remove viewport's own border since container has it
        self.viewport.setStyleSheet("background-color: white; border: none; border-radius: 7px;")
        
        viewport_layout.addWidget(self.viewport)
        layout.addWidget(viewport_container)
        
        return pane
    
    def _create_controls_pane(self) -> QWidget:
        """Create the right controls pane."""
        pane = QWidget()
        pane.setStyleSheet("background-color: #ffffff; border-left: 1px solid #e2e8f0;")
        
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(20, 24, 20, 24)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Display Options")
        title_label.setStyleSheet("""
            font-size: 12pt;
            font-weight: 700;
            color: #334155;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(title_label)
        
        # Controls Group
        controls_group = QWidget()
        controls_layout = QVBoxLayout(controls_group)
        controls_layout.setSpacing(12)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        
        # Checkboxes
        self.show_labels_cb = self._create_checkbox("Show Labels", True)
        self.show_labels_cb.toggled.connect(self._on_display_toggle)
        controls_layout.addWidget(self.show_labels_cb)
        
        self.show_grid_cb = self._create_checkbox("Show Grid", True)
        self.show_grid_cb.toggled.connect(self._on_display_toggle)
        controls_layout.addWidget(self.show_grid_cb)
        
        self.show_axes_cb = self._create_checkbox("Show Axes", True)
        self.show_axes_cb.toggled.connect(self._on_display_toggle)
        controls_layout.addWidget(self.show_axes_cb)

        # Optional: Draw as star (hexagram)
        try:
            from pillars.geometry.services import RegularPolygonShape
            if isinstance(self.shape, RegularPolygonShape) and self.shape.num_sides == 6:
                self.star_toggle = self._create_checkbox("Draw as Star (Hexagram)", False)
                self.star_toggle.toggled.connect(self._on_display_toggle)
                controls_layout.addWidget(self.star_toggle)
        except Exception:
            pass
        
        layout.addWidget(controls_group)
        
        layout.addStretch()
        
        # Info section
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #eff6ff;
                border: 1px solid #dbeafe;
                border-radius: 8px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(16, 16, 16, 16)
        
        info_icon = QLabel("💡")
        info_icon.setStyleSheet("font-size: 16pt; border: none; background: transparent;")
        info_layout.addWidget(info_icon)
        
        info_text = QLabel(
            "Enter any property value to calculate all other properties automatically."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("""
            color: #1e40af;
            font-size: 9pt;
            font-weight: 500;
            border: none;
            background: transparent;
        """)
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_frame)
        
        return pane
    
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
            if prop.value is not None:
                input_field = self.property_inputs[prop.key]
                # Format without scientific notation
                formatted_value = f"{prop.value:.{prop.precision}f}".rstrip('0').rstrip('.')
                input_field.setText(formatted_value)
        
        self.updating = False
    
    def _update_viewport(self):
        """Update the viewport with current shape."""
        drawing_data = self.shape.get_drawing_instructions()
        # Inject star flag for hexagram view if toggle exists
        if self.star_toggle is not None and self.star_toggle.isChecked():
            drawing_data['star'] = True
        labels = self.shape.get_label_positions()
        self.viewport.set_drawing_data(drawing_data, labels)
    
    def _clear_all(self):
        """Clear all values."""
        self.updating = True
        
        # Clear shape
        self.shape.clear_all()
        
        # Clear input fields
        for input_field in self.property_inputs.values():
            input_field.clear()
        
        # Clear viewport
        self.viewport.clear()
        
        self.updating = False
    
    def _on_display_toggle(self):
        """Handle display control toggles."""
        self.viewport.show_labels = self.show_labels_cb.isChecked()
        self.viewport.show_grid = self.show_grid_cb.isChecked()
        self.viewport.show_axes = self.show_axes_cb.isChecked()
        self.viewport.update()
