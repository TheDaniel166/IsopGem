"""
Flowchart Visual Builder Panel.

**Purpose**:
Provide a point-and-click interface for building Mermaid flowcharts without
knowing the syntax. Users can add nodes, connect them, and style them visually.

**Features**:
- Add/edit/delete nodes with live preview
- Create connections between nodes
- Choose shapes and arrow types from dropdowns
- Apply styles visually
- Automatic code generation
- Bidirectional sync with code editor

**Usage**:
```python
# Standalone usage
builder = FlowchartBuilderPanel()
builder.code_changed.connect(lambda code: print(code))
builder.show()

# Integrated with editor
editor_dialog.add_builder_panel(builder)
```

**Thread Safety**: Qt widgets must be used from main thread only.
"""

import qtawesome as qta
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFrame, QScrollArea, QGroupBox,
    QMessageBox, QColorDialog
)
from PyQt6.QtGui import QColor, QKeySequence, QShortcut

from shared.ui.theme import COLORS, set_archetype

from .mermaid_ast import (
    FlowchartAST, NodeShape, ArrowType, StyleDefinition
)
from .mermaid_parser import FlowchartParser
from .mermaid_generator import FlowchartGenerator

import logging
logger = logging.getLogger(__name__)


# ============================================================================
# MAIN BUILDER PANEL
# ============================================================================

class FlowchartBuilderPanel(QWidget):
    """
    Visual builder for flowchart diagrams.
    
    **Signals**:
        code_changed: Emitted when AST changes, passes generated code
        ast_changed: Emitted when AST structure changes
    
    **Public Methods**:
        load_code(code): Parse code and populate builder
        get_code(): Get current generated code
        get_ast(): Get current AST structure
        clear(): Reset to empty diagram
    """
    
    code_changed = pyqtSignal(str)  # Emitted when user makes changes
    ast_changed = pyqtSignal(object)  # Emitted with FlowchartAST
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Internal state
        self.ast = FlowchartAST(direction="TD")
        self._suppress_signals = False  # Flag to prevent infinite loops
        
        # Remember last selections for convenience
        self._last_shape_index = 0  # Rectangle
        self._last_arrow_index = 0  # Solid Arrow
        
        self._setup_ui()
        self._setup_shortcuts()
        self._apply_styles()
    
    def _setup_ui(self):
        """Build the builder panel UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(16)
        
        # Direction selector
        content_layout.addWidget(self._create_direction_group())
        
        # Node controls
        content_layout.addWidget(self._create_node_group())
        
        # Edge controls
        content_layout.addWidget(self._create_edge_group())
        
        # Style controls
        content_layout.addWidget(self._create_style_group())
        
        # Stretch to push everything to top
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
    
    def _create_header(self) -> QWidget:
        """Create the panel header with title and clear button."""
        header = QFrame()
        header.setObjectName("builderHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 12, 8)
        
        # Title
        title = QLabel("🔧 Visual Builder")
        title.setStyleSheet(f"font-weight: bold; font-size: 12pt; color: {COLORS['text_primary']};")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Clear button
        clear_btn = QPushButton(qta.icon("fa5s.trash", color=COLORS["destroyer"]), "")
        clear_btn.setToolTip("Clear diagram")
        clear_btn.setFixedSize(32, 32)
        clear_btn.clicked.connect(self._on_clear_diagram)
        header_layout.addWidget(clear_btn)
        
        return header
    
    def _create_direction_group(self) -> QGroupBox:
        """Create direction selector group."""
        group = QGroupBox("📐 Diagram Direction")
        layout = QVBoxLayout(group)
        
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["TD (Top → Down)", "LR (Left → Right)", "TB (Top → Bottom)", 
                                       "BT (Bottom → Top)", "RL (Right → Left)"])
        self.direction_combo.setCurrentText("TD (Top → Down)")
        self.direction_combo.currentTextChanged.connect(self._on_direction_changed)
        layout.addWidget(self.direction_combo)
        
        return group
    
    def _create_node_group(self) -> QGroupBox:
        """Create node manipulation controls."""
        group = QGroupBox("📦 Nodes")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        
        # Node ID input
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("ID:"))
        self.node_id_input = QLineEdit()
        self.node_id_input.setPlaceholderText("Auto (A, B, C...)")
        id_layout.addWidget(self.node_id_input)
        layout.addLayout(id_layout)
        
        # Node label input
        label_layout = QHBoxLayout()
        label_layout.addWidget(QLabel("Label:"))
        self.node_label_input = QLineEdit()
        self.node_label_input.setPlaceholderText("Node text... (press Enter to add)")
        self.node_label_input.returnPressed.connect(self._on_add_node)  # Enter key support
        label_layout.addWidget(self.node_label_input)
        layout.addLayout(label_layout)
        
        # Shape selector
        shape_layout = QHBoxLayout()
        shape_layout.addWidget(QLabel("Shape:"))
        self.node_shape_combo = QComboBox()
        self.node_shape_combo.addItems([
            "Rectangle [  ]",
            "Rounded (  )",
            "Stadium ([  ])",
            "Diamond {  }",
            "Circle ((  ))",
            "Hexagon {{  }}",
            "Parallelogram [/  /]",
            "Trapezoid [\\  /]"
        ])
        self.node_shape_combo.currentIndexChanged.connect(self._on_shape_changed)
        shape_layout.addWidget(self.node_shape_combo)
        layout.addLayout(shape_layout)
        
        # Add node button
        add_node_btn = QPushButton(qta.icon("fa5s.plus-circle", color="white"), "Add Node")
        add_node_btn.setMinimumHeight(36)
        add_node_btn.clicked.connect(self._on_add_node)
        set_archetype(add_node_btn, "seeker")
        layout.addWidget(add_node_btn)
        
        # Node list/management section
        list_label = QLabel("Existing Nodes:")
        list_label.setStyleSheet(f"font-weight: bold; margin-top: 8px; color: {COLORS['text_secondary']};")
        layout.addWidget(list_label)
        
        self.node_list_combo = QComboBox()
        self.node_list_combo.addItem("(No nodes yet)")
        self.node_list_combo.setEnabled(False)
        self.node_list_combo.currentTextChanged.connect(self._on_node_selected)
        layout.addWidget(self.node_list_combo)
        
        # Node action buttons
        node_actions = QHBoxLayout()
        
        edit_node_btn = QPushButton(qta.icon("fa5s.edit", color=COLORS["stone"]), "")
        edit_node_btn.setToolTip("Edit selected node")
        edit_node_btn.setFixedSize(32, 32)
        edit_node_btn.clicked.connect(self._on_edit_node)
        node_actions.addWidget(edit_node_btn)
        
        delete_node_btn = QPushButton(qta.icon("fa5s.trash", color=COLORS["destroyer"]), "")
        delete_node_btn.setToolTip("Delete selected node")
        delete_node_btn.setFixedSize(32, 32)
        delete_node_btn.clicked.connect(self._on_delete_node)
        node_actions.addWidget(delete_node_btn)
        
        node_actions.addStretch()
        layout.addLayout(node_actions)
        
        return group
    
    def _create_edge_group(self) -> QGroupBox:
        """Create edge/connection controls."""
        group = QGroupBox("🔗 Connections")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        
        # From selector
        from_layout = QHBoxLayout()
        from_layout.addWidget(QLabel("From:"))
        self.edge_from_combo = QComboBox()
        self.edge_from_combo.addItem("(Select node)")
        self.edge_from_combo.setEnabled(False)
        from_layout.addWidget(self.edge_from_combo)
        layout.addLayout(from_layout)
        
        # To selector
        to_layout = QHBoxLayout()
        to_layout.addWidget(QLabel("To:"))
        self.edge_to_combo = QComboBox()
        self.edge_to_combo.addItem("(Select node)")
        self.edge_to_combo.setEnabled(False)
        to_layout.addWidget(self.edge_to_combo)
        layout.addLayout(to_layout)
        
        # Arrow type
        arrow_layout = QHBoxLayout()
        arrow_layout.addWidget(QLabel("Type:"))
        self.edge_arrow_combo = QComboBox()
        self.edge_arrow_combo.addItems([
            "Solid Arrow -->",
            "Solid Line ---",
            "Dotted Arrow -.->",
            "Dotted Line -..-",
            "Thick Arrow ==>",
            "Thick Line ===",
            "Invisible ~~~"
        ])
        self.edge_arrow_combo.currentIndexChanged.connect(self._on_arrow_changed)
        arrow_layout.addWidget(self.edge_arrow_combo)
        layout.addLayout(arrow_layout)
        
        # Label
        label_layout = QHBoxLayout()
        label_layout.addWidget(QLabel("Label:"))
        self.edge_label_input = QLineEdit()
        self.edge_label_input.setPlaceholderText("Optional text... (press Enter to add)")
        self.edge_label_input.returnPressed.connect(self._on_add_edge)  # Enter key support
        label_layout.addWidget(self.edge_label_input)
        layout.addLayout(label_layout)
        
        # Add edge button
        add_edge_btn = QPushButton(qta.icon("fa5s.link", color="white"), "Add Connection")
        add_edge_btn.setMinimumHeight(36)
        add_edge_btn.clicked.connect(self._on_add_edge)
        set_archetype(add_edge_btn, "seeker")
        layout.addWidget(add_edge_btn)
        
        return group
    
    def _create_style_group(self) -> QGroupBox:
        """Create style controls for visual styling."""
        group = QGroupBox("🎨 Styles")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        
        # Style class name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Class Name:"))
        self.style_name_input = QLineEdit()
        self.style_name_input.setPlaceholderText("e.g., highlight, error...")
        name_layout.addWidget(self.style_name_input)
        layout.addLayout(name_layout)
        
        # Color pickers in a grid
        colors_group = QGroupBox("Colors")
        colors_layout = QVBoxLayout(colors_group)
        
        # Fill color
        fill_layout = QHBoxLayout()
        fill_layout.addWidget(QLabel("Fill:"))
        self.fill_color_btn = QPushButton("Choose Color")
        self.fill_color_btn.clicked.connect(self._choose_fill_color)
        self.fill_color_preview = QLabel("      ")
        self.fill_color_preview.setStyleSheet("background-color: #fff; border: 1px solid #999;")
        self._current_fill_color = "#ffffff"
        fill_layout.addWidget(self.fill_color_btn)
        fill_layout.addWidget(self.fill_color_preview)
        fill_layout.addStretch()
        colors_layout.addLayout(fill_layout)
        
        # Stroke color
        stroke_layout = QHBoxLayout()
        stroke_layout.addWidget(QLabel("Stroke:"))
        self.stroke_color_btn = QPushButton("Choose Color")
        self.stroke_color_btn.clicked.connect(self._choose_stroke_color)
        self.stroke_color_preview = QLabel("      ")
        self.stroke_color_preview.setStyleSheet("background-color: #333; border: 1px solid #999;")
        self._current_stroke_color = "#333333"
        stroke_layout.addWidget(self.stroke_color_btn)
        stroke_layout.addWidget(self.stroke_color_preview)
        stroke_layout.addStretch()
        colors_layout.addLayout(stroke_layout)
        
        # Text color
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("Text:"))
        self.text_color_btn = QPushButton("Choose Color")
        self.text_color_btn.clicked.connect(self._choose_text_color)
        self.text_color_preview = QLabel("      ")
        self.text_color_preview.setStyleSheet("background-color: #000; border: 1px solid #999;")
        self._current_text_color = "#000000"
        text_layout.addWidget(self.text_color_btn)
        text_layout.addWidget(self.text_color_preview)
        text_layout.addStretch()
        colors_layout.addLayout(text_layout)
        
        layout.addWidget(colors_group)
        
        # Font size
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Font Size:"))
        self.font_size_input = QLineEdit()
        self.font_size_input.setPlaceholderText("e.g., 14px, 1.2em...")
        font_layout.addWidget(self.font_size_input)
        layout.addLayout(font_layout)
        
        # Stroke width
        stroke_width_layout = QHBoxLayout()
        stroke_width_layout.addWidget(QLabel("Stroke Width:"))
        self.stroke_width_input = QLineEdit()
        self.stroke_width_input.setPlaceholderText("e.g., 2px, 3px...")
        stroke_width_layout.addWidget(self.stroke_width_input)
        layout.addLayout(stroke_width_layout)
        
        # Add style button
        add_style_btn = QPushButton(qta.icon("fa5s.palette", color="white"), "Add Style Class")
        add_style_btn.setMinimumHeight(36)
        add_style_btn.clicked.connect(self._on_add_style)
        set_archetype(add_style_btn, "magus")
        layout.addWidget(add_style_btn)
        
        # Existing styles list
        list_label = QLabel("Existing Styles:")
        list_label.setStyleSheet(f"font-weight: bold; margin-top: 8px; color: {COLORS['text_secondary']};")
        layout.addWidget(list_label)
        
        self.style_list_combo = QComboBox()
        self.style_list_combo.addItem("(No styles yet)")
        self.style_list_combo.setEnabled(False)
        layout.addWidget(self.style_list_combo)
        
        # Apply style to node section
        apply_label = QLabel("Apply to Node:")
        apply_label.setStyleSheet(f"font-weight: bold; margin-top: 8px; color: {COLORS['text_secondary']};")
        layout.addWidget(apply_label)
        
        apply_layout = QHBoxLayout()
        self.apply_node_combo = QComboBox()
        self.apply_node_combo.addItem("(Select node)")
        self.apply_node_combo.setEnabled(False)
        apply_layout.addWidget(self.apply_node_combo)
        
        apply_btn = QPushButton(qta.icon("fa5s.paint-brush", color=COLORS["magus"]), "")
        apply_btn.setFixedSize(32, 32)
        apply_btn.setToolTip("Apply style to selected node")
        apply_btn.clicked.connect(self._on_apply_style_to_node)
        apply_layout.addWidget(apply_btn)
        layout.addLayout(apply_layout)
        
        return group
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Ctrl+N: Add new node (focus label input)
        new_node_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_node_shortcut.activated.connect(lambda: self.node_label_input.setFocus())
        
        # Ctrl+L: Add connection (focus from selector)
        new_edge_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        new_edge_shortcut.activated.connect(lambda: self.edge_from_combo.setFocus())
        
        # Ctrl+Shift+C: Clear diagram
        clear_shortcut = QShortcut(QKeySequence("Ctrl+Shift+C"), self)
        clear_shortcut.activated.connect(self._on_clear_diagram)
    
    def _apply_styles(self):
        """Apply Visual Liturgy styling."""
        self.setStyleSheet(f"""
            QGroupBox {{
                background-color: {COLORS['marble']};
                border: 1px solid {COLORS['ash']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                font-weight: bold;
                color: {COLORS['text_primary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
            }}
            QFrame#builderHeader {{
                background-color: {COLORS['surface']};
                border-bottom: 1px solid {COLORS['border']};
            }}
            QLineEdit, QComboBox {{
                background-color: {COLORS['light']};
                border: 1px solid {COLORS['ash']};
                border-radius: 6px;
                padding: 6px;
                min-height: 28px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 2px solid {COLORS['focus']};
            }}
        """)
    
    # ========================================================================
    # SLOT HANDLERS
    # ========================================================================
    
    def _on_shape_changed(self, index: int):
        """Remember last shape selection."""
        self._last_shape_index = index
    
    def _on_arrow_changed(self, index: int):
        """Remember last arrow selection."""
        self._last_arrow_index = index
    
    def _on_direction_changed(self, text: str):
        """Handle direction dropdown change."""
        # Extract direction code (e.g., "TD" from "TD (Top → Down)")
        direction = text.split()[0]
        self.ast.direction = direction
        self._emit_code_changed()
    
    def _on_add_node(self):
        """Handle Add Node button click."""
        # Get inputs
        node_id = self.node_id_input.text().strip()
        label = self.node_label_input.text().strip()
        
        # Validate label
        if not label:
            QMessageBox.warning(self, "Missing Label", "Please enter a node label.")
            self.node_label_input.setFocus()
            return
        
        # Auto-generate ID if empty
        if not node_id:
            node_id = self.ast.get_next_node_id()
        
        # Check for duplicate ID
        if self.ast.get_node(node_id):
            QMessageBox.warning(self, "Duplicate ID", 
                              f"Node ID '{node_id}' already exists. Please choose a different ID.")
            self.node_id_input.setFocus()
            return
        
        # Get shape
        shape_index = self.node_shape_combo.currentIndex()
        shape_map = [
            NodeShape.RECTANGLE,
            NodeShape.ROUNDED,
            NodeShape.STADIUM,
            NodeShape.DIAMOND,
            NodeShape.CIRCLE,
            NodeShape.HEXAGON,
            NodeShape.PARALLELOGRAM,
            NodeShape.TRAPEZOID
        ]
        shape = shape_map[shape_index]
        
        # Add node to AST
        try:
            self.ast.add_node(node_id, label, shape)
            self._refresh_node_list()
            self._refresh_edge_selectors()
            self._emit_code_changed()
            
            # Clear inputs
            self.node_id_input.clear()
            self.node_label_input.clear()
            
            # Restore last shape selection
            self.node_shape_combo.setCurrentIndex(self._last_shape_index)
            
            # Auto-focus label for next node
            self.node_label_input.setFocus()
            
            # Show brief success (no blocking dialog for better UX)
            # Just rely on the preview updating
            logger.info(f"Node '{node_id}' ({label}) added to diagram")
        
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
    
    def _on_add_edge(self):
        """Handle Add Connection button click."""
        # Get selections
        from_id = self.edge_from_combo.currentText()
        to_id = self.edge_to_combo.currentText()
        label = self.edge_label_input.text().strip() or None
        
        # Validate
        if from_id == "(Select node)" or to_id == "(Select node)":
            QMessageBox.warning(self, "Incomplete Selection", 
                              "Please select both source and target nodes.")
            return
        
        # Get arrow type
        arrow_index = self.edge_arrow_combo.currentIndex()
        arrow_map = [
            ArrowType.SOLID,
            ArrowType.SOLID_LINE,
            ArrowType.DOTTED,
            ArrowType.DOTTED_LINE,
            ArrowType.THICK,
            ArrowType.THICK_LINE,
            ArrowType.INVISIBLE
        ]
        arrow_type = arrow_map[arrow_index]
        
        # Add edge to AST
        try:
            self.ast.add_edge(from_id, to_id, arrow_type, label)
            self._emit_code_changed()
            
            # Clear label input
            self.edge_label_input.clear()
            
            # Restore last arrow selection
            self.edge_arrow_combo.setCurrentIndex(self._last_arrow_index)
            
            # Show brief success
            msg = f"Connection added: {from_id} → {to_id}"
            if label:
                msg += f" ({label})"
            logger.info(msg)
        
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
    
    def _on_node_selected(self, node_id: str):
        """Handle node selection from list."""
        if node_id == "(No nodes yet)":
            return
        
        node = self.ast.get_node(node_id)
        if node:
            # Populate inputs for editing
            self.node_id_input.setText(node.id)
            self.node_label_input.setText(node.label)
            
            # Set shape combo
            shape_to_index = {
                NodeShape.RECTANGLE: 0,
                NodeShape.ROUNDED: 1,
                NodeShape.STADIUM: 2,
                NodeShape.DIAMOND: 3,
                NodeShape.CIRCLE: 4,
                NodeShape.HEXAGON: 5,
                NodeShape.PARALLELOGRAM: 6,
                NodeShape.TRAPEZOID: 7
            }
            self.node_shape_combo.setCurrentIndex(shape_to_index[node.shape])
    
    def _on_edit_node(self):
        """Handle Edit Node button click."""
        selected_id = self.node_list_combo.currentText()
        if selected_id == "(No nodes yet)":
            return
        
        # Get new values from inputs
        new_label = self.node_label_input.text().strip()
        if not new_label:
            QMessageBox.warning(self, "Missing Label", "Please enter a node label.")
            return
        
        shape_index = self.node_shape_combo.currentIndex()
        shape_map = [
            NodeShape.RECTANGLE, NodeShape.ROUNDED, NodeShape.STADIUM,
            NodeShape.DIAMOND, NodeShape.CIRCLE, NodeShape.HEXAGON,
            NodeShape.PARALLELOGRAM, NodeShape.TRAPEZOID
        ]
        new_shape = shape_map[shape_index]
        
        # Update AST
        if self.ast.update_node(selected_id, label=new_label, shape=new_shape):
            self._emit_code_changed()
            QMessageBox.information(self, "Node Updated", 
                                  f"Node '{selected_id}' has been updated.")
        else:
            QMessageBox.warning(self, "Error", f"Could not find node '{selected_id}'.")
    
    def _on_delete_node(self):
        """Handle Delete Node button click."""
        selected_id = self.node_list_combo.currentText()
        if selected_id == "(No nodes yet)":
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Delete Node",
            f"Delete node '{selected_id}' and all its connections?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.ast.remove_node(selected_id):
                self._refresh_node_list()
                self._refresh_edge_selectors()
                self._emit_code_changed()
                
                # Clear inputs
                self.node_id_input.clear()
                self.node_label_input.clear()
                
                QMessageBox.information(self, "Node Deleted", 
                                      f"Node '{selected_id}' has been removed.")
    
    def _on_clear_diagram(self):
        """Handle Clear button click."""
        if not self.ast.nodes:
            return
        
        reply = QMessageBox.question(
            self, "Clear Diagram",
            "Clear all nodes and connections?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.clear()
    
    def _choose_fill_color(self):
        """Open color picker for fill color."""
        color = QColorDialog.getColor(QColor(self._current_fill_color), self, "Choose Fill Color")
        if color.isValid():
            self._current_fill_color = color.name()
            self.fill_color_preview.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #999;")
    
    def _choose_stroke_color(self):
        """Open color picker for stroke color."""
        color = QColorDialog.getColor(QColor(self._current_stroke_color), self, "Choose Stroke Color")
        if color.isValid():
            self._current_stroke_color = color.name()
            self.stroke_color_preview.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #999;")
    
    def _choose_text_color(self):
        """Open color picker for text color."""
        color = QColorDialog.getColor(QColor(self._current_text_color), self, "Choose Text Color")
        if color.isValid():
            self._current_text_color = color.name()
            self.text_color_preview.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #999;")
    
    def _on_add_style(self):
        """Handle Add Style Class button click."""
        class_name = self.style_name_input.text().strip()
        
        if not class_name:
            QMessageBox.warning(self, "Missing Name", "Please enter a style class name.")
            self.style_name_input.setFocus()
            return
        
        # Check for duplicate
        if class_name in self.ast.styles:
            QMessageBox.warning(self, "Duplicate Style", 
                              f"Style class '{class_name}' already exists.")
            return
        
        # Create style definition
        style = StyleDefinition(class_name=class_name)
        style.fill = self._current_fill_color
        style.stroke = self._current_stroke_color
        style.color = self._current_text_color
        
        if self.font_size_input.text().strip():
            style.font_size = self.font_size_input.text().strip()
        
        if self.stroke_width_input.text().strip():
            style.stroke_width = self.stroke_width_input.text().strip()
        
        # Add to AST
        self.ast.add_style(style)
        self._refresh_style_list()
        self._emit_code_changed()
        
        # Clear inputs
        self.style_name_input.clear()
        self.font_size_input.clear()
        self.stroke_width_input.clear()
        
        logger.info(f"Style class '{class_name}' added")
    
    def _on_apply_style_to_node(self):
        """Apply selected style to selected node."""
        node_id = self.apply_node_combo.currentText()
        style_name = self.style_list_combo.currentText()
        
        if node_id == "(Select node)" or style_name == "(No styles yet)":
            QMessageBox.warning(self, "Incomplete Selection", 
                              "Please select both a node and a style class.")
            return
        
        # Update node
        if self.ast.update_node(node_id, style_class=style_name):
            self._emit_code_changed()
            logger.info(f"Applied style '{style_name}' to node '{node_id}'")
        else:
            QMessageBox.warning(self, "Error", f"Could not find node '{node_id}'.")
    
    # ========================================================================
    # UI UPDATE HELPERS
    # ========================================================================
    
    def _refresh_node_list(self):
        """Update the node list combobox."""
        self.node_list_combo.clear()
        
        if not self.ast.nodes:
            self.node_list_combo.addItem("(No nodes yet)")
            self.node_list_combo.setEnabled(False)
        else:
            for node in self.ast.nodes:
                self.node_list_combo.addItem(node.id)
            self.node_list_combo.setEnabled(True)
    
    def _refresh_edge_selectors(self):
        """Update the edge from/to comboboxes."""
        self.edge_from_combo.clear()
        self.edge_to_combo.clear()
        self.apply_node_combo.clear()
        
        if not self.ast.nodes:
            self.edge_from_combo.addItem("(Select node)")
            self.edge_to_combo.addItem("(Select node)")
            self.apply_node_combo.addItem("(Select node)")
            self.edge_from_combo.setEnabled(False)
            self.edge_to_combo.setEnabled(False)
            self.apply_node_combo.setEnabled(False)
        else:
            self.edge_from_combo.addItem("(Select node)")
            self.edge_to_combo.addItem("(Select node)")
            self.apply_node_combo.addItem("(Select node)")
            
            for node in self.ast.nodes:
                self.edge_from_combo.addItem(node.id)
                self.edge_to_combo.addItem(node.id)
                self.apply_node_combo.addItem(node.id)
            
            self.edge_from_combo.setEnabled(True)
            self.edge_to_combo.setEnabled(True)
            self.apply_node_combo.setEnabled(True)
    
    def _refresh_style_list(self):
        """Update the style list combobox."""
        self.style_list_combo.clear()
        
        if not self.ast.styles:
            self.style_list_combo.addItem("(No styles yet)")
            self.style_list_combo.setEnabled(False)
        else:
            for style_name in self.ast.styles.keys():
                self.style_list_combo.addItem(style_name)
            self.style_list_combo.setEnabled(True)
    
    def _emit_code_changed(self):
        """Generate code from AST and emit signal."""
        if self._suppress_signals:
            return
        
        code = FlowchartGenerator.generate(self.ast)
        self.code_changed.emit(code)
        self.ast_changed.emit(self.ast)
    
    # ========================================================================
    # PUBLIC API
    # ========================================================================
    
    def load_code(self, code: str):
        """
        Parse Mermaid code and populate the builder.
        
        **Args**:
            code: Mermaid flowchart code to load
        
        **Example**:
        ```python
        code = "flowchart TD\\n    A[Start]-->B[End]"
        builder.load_code(code)
        ```
        """
        try:
            self._suppress_signals = True
            
            # Parse code to AST
            self.ast = FlowchartParser.parse(code)
            
            # Update UI
            direction_map = {
                "TD": 0, "LR": 1, "TB": 2, "BT": 3, "RL": 4
            }
            self.direction_combo.setCurrentIndex(direction_map.get(self.ast.direction, 0))
            
            self._refresh_node_list()
            self._refresh_edge_selectors()
            
        except Exception as e:
            logger.error(f"Failed to load code into builder: {e}")
            QMessageBox.warning(self, "Parse Error", 
                              f"Could not parse the diagram code:\n{str(e)}")
        finally:
            self._suppress_signals = False
    
    def get_code(self) -> str:
        """
        Get the current generated Mermaid code.
        
        **Returns**:
            str: Generated Mermaid code
        """
        return FlowchartGenerator.generate(self.ast)
    
    def get_ast(self) -> FlowchartAST:
        """
        Get the current AST structure.
        
        **Returns**:
            FlowchartAST: Current diagram structure
        """
        return self.ast
    
    def clear(self):
        """
        Clear all nodes and edges, reset to empty diagram.
        """
        self.ast.clear()
        self.ast.direction = "TD"
        
        self._refresh_node_list()
        self._refresh_edge_selectors()
        self.node_id_input.clear()
        self.node_label_input.clear()
        self.edge_label_input.clear()
        
        self._emit_code_changed()
