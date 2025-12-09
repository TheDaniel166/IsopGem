from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, 
    QPushButton, QLabel, QColorDialog, QComboBox, QStackedWidget,
    QFontComboBox, QSpinBox, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QFont
import json

class NodeInspectorWidget(QWidget):
    """
    Side panel for viewing and editing Node and Edge details.
    """
    node_updated = pyqtSignal(dict) # Emits updated node data (dict)
    edge_updated = pyqtSignal(dict) # Emits updated edge data (dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_data = None
        self.current_type = None # "node" or "edge"
        
        self.layout = QVBoxLayout(self)
        self.stack = QStackedWidget()
        
        # --- Page 1: Node Inspector ---
        self.node_page = QWidget()
        self.node_layout = QVBoxLayout(self.node_page)
        self.node_form = QFormLayout()
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Node Title")
        
        self.shape_combo = QComboBox()
        for name, key in [
            ("Capsule (Default)", "capsule"), ("Circle (Orb)", "circle"),
            ("Diamond (Active)", "diamond"), ("Hexagon (System)", "hexagon"),
            ("Cartouche (Entity)", "cartouche"), ("Triangle Up (Fire)", "triangle_up"),
            ("Triangle Down (Water)", "triangle_down")
        ]:
            self.shape_combo.addItem(name, key)
        self.shape_combo.currentIndexChanged.connect(self._save_node)

        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Tags (comma separated)")
        
        # Font Controls
        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self._save_node)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 72)
        self.font_size.setValue(12)
        self.font_size.valueChanged.connect(self._save_node)
        
        self.text_color_btn = QPushButton("Text Color")
        self.text_color_btn.clicked.connect(lambda: self._pick_color("text"))

        self.node_color_btn = QPushButton("Fill Color")
        self.node_color_btn.clicked.connect(lambda: self._pick_color("node"))
        
        # Border Controls
        self.border_width = QSpinBox()
        self.border_width.setRange(0, 20)
        self.border_width.setSuffix(" px")
        self.border_width.valueChanged.connect(self._save_node)
        
        self.border_style = QComboBox()
        self.border_style.addItem("None", "none")
        self.border_style.addItem("Solid", "solid")
        self.border_style.addItem("Dashed", "dashed")
        self.border_style.addItem("Dotted", "dotted")
        self.border_style.currentIndexChanged.connect(self._save_node)
        
        self.border_color_btn = QPushButton("Border Color")
        self.border_color_btn.clicked.connect(lambda: self._pick_color("border"))

        self.node_form.addRow("Title:", self.title_edit)
        self.node_form.addRow("Shape:", self.shape_combo)
        self.node_form.addRow("Tags:", self.tags_edit)
        self.node_form.addRow("Font:", self.font_combo)
        self.node_form.addRow("Size:", self.font_size)
        
        color_layout = QHBoxLayout()
        color_layout.addWidget(self.node_color_btn)
        color_layout.addWidget(self.text_color_btn)
        self.node_form.addRow("Colors:", color_layout)
        
        border_layout = QHBoxLayout()
        border_layout.addWidget(self.border_width)
        border_layout.addWidget(self.border_style)
        
        self.node_form.addRow("Border:", border_layout)
        self.node_form.addRow("", self.border_color_btn)
        
        # self.content_edit = QTextEdit()
        # self.content_edit.setPlaceholderText("Notes (Markdown)")
        self.node_save_btn = QPushButton("Save Node")
        self.node_save_btn.clicked.connect(self._save_node)

        self.node_layout.addLayout(self.node_form)
        # self.node_layout.addWidget(QLabel("Content:"))
        # self.node_layout.addWidget(self.content_edit)
        self.node_layout.addWidget(self.node_save_btn)
        
        # --- Page 2: Edge Inspector ---
        self.edge_page = QWidget()
        self.edge_layout = QVBoxLayout(self.edge_page)
        self.edge_form = QFormLayout()
        
        self.relation_label = QLabel("Relation")
        
        self.edge_style_combo = QComboBox()
        self.edge_style_combo.addItem("Solid", "solid")
        self.edge_style_combo.addItem("Dashed", "dashed")
        self.edge_style_combo.addItem("Dotted", "dotted")
        self.edge_style_combo.currentIndexChanged.connect(self._save_edge)
        
        self.edge_color_btn = QPushButton("Edge Color")
        self.edge_color_btn.clicked.connect(lambda: self._pick_color("edge"))
        
        self.edge_form.addRow("Type:", self.relation_label)
        self.edge_form.addRow("Style:", self.edge_style_combo)
        self.edge_form.addRow("Color:", self.edge_color_btn)
        
        self.edge_save_btn = QPushButton("Save Connection")
        self.edge_save_btn.clicked.connect(self._save_edge)
        
        self.edge_layout.addLayout(self.edge_form)
        self.edge_layout.addWidget(self.edge_save_btn)
        self.edge_layout.addStretch()

        # Stack Assembly
        self.stack.addWidget(self.node_page)
        self.stack.addWidget(self.edge_page)
        self.layout.addWidget(self.stack)
        
        # State Tracking
        self._current_colors = {"node": None, "text": None, "edge": None, "border": None}

    def set_data(self, dto, type="node"):
        self.current_data = dto
        self.current_type = type
        self.blockSignals(True) # Block broad signals if any
        self._block_field_signals(True)
        
        if not dto:
            self.setEnabled(False)
            self._block_field_signals(False)
            self.blockSignals(False)
            return
            
        self.setEnabled(True)
        
        if type == "node":
            self.stack.setCurrentIndex(0)
            self._populate_node(dto)
        else:
            self.stack.setCurrentIndex(1)
            self._populate_edge(dto)
            
        self._block_field_signals(False)
        self.blockSignals(False)

    def set_node(self, node_dto):
        """Legacy compatibility wrapper."""
        self.set_data(node_dto, "node")

    def _block_field_signals(self, block: bool):
        self.shape_combo.blockSignals(block)
        self.font_combo.blockSignals(block)
        self.font_size.blockSignals(block)
        self.edge_style_combo.blockSignals(block)
        self.border_width.blockSignals(block)
        self.border_style.blockSignals(block)

    def _populate_node(self, dto):
        self.title_edit.setText(dto.title)
        # self.content_edit.setText(dto.content or "")
        try:
            tags = json.loads(dto.tags) if dto.tags else []
            self.tags_edit.setText(", ".join(tags))
        except:
            self.tags_edit.setText("")
            
        style = {}
        if dto.appearance:
            try: style = json.loads(dto.appearance)
            except: pass
            
        # Shape
        idx = self.shape_combo.findData(style.get("shape", "capsule"))
        self.shape_combo.setCurrentIndex(idx if idx >= 0 else 0)
        
        # Colors
        self._update_color_btn("node", style.get("color_override"))
        self._update_color_btn("text", style.get("textColor"))
        self._update_color_btn("border", style.get("borderColor"))
        
        # Font
        fam = style.get("fontFamily")
        if fam: self.font_combo.setCurrentFont(QFont(fam))
        
        size = style.get("fontSize")
        if size: self.font_size.setValue(int(size))
        
        # Border
        b_width = style.get("borderWidth", 0)
        self.border_width.setValue(int(b_width))
        
        b_style = style.get("borderStyle", "none")
        idx = self.border_style.findData(b_style)
        self.border_style.setCurrentIndex(idx if idx >= 0 else 0)


    def _populate_edge(self, dto):
        self.relation_label.setText(dto.relation_type.capitalize())
        
        style = {}
        if dto.appearance:
            try: style = json.loads(dto.appearance)
            except: pass
            
        # Style
        idx = self.edge_style_combo.findData(style.get("style", "solid"))
        self.edge_style_combo.setCurrentIndex(idx if idx >= 0 else 0)
        
        # Color
        self._update_color_btn("edge", style.get("color"))

    def _update_color_btn(self, key, color_hex):
        self._current_colors[key] = color_hex
        btn = getattr(self, f"{key}_color_btn")
        if color_hex:
            btn.setStyleSheet(f"background-color: {color_hex}; color: white;")
            btn.setText(color_hex)
        else:
            btn.setStyleSheet("")
            btn.setText(f"{key.capitalize()} Color")

    def _pick_color(self, key):
        current = self._current_colors.get(key)
        initial = QColor(current) if current else Qt.GlobalColor.white
        color = QColorDialog.getColor(initial, self, f"Pick {key.capitalize()} Color")
        if color.isValid():
            self._update_color_btn(key, color.name())
            if self.current_type == "node":
                self._save_node()
            else:
                self._save_edge()

    def _save_node(self):
        if self.current_type != "node" or not self.current_data: return
        
        raw_tags = self.tags_edit.text().split(',')
        tags = [t.strip() for t in raw_tags if t.strip()]
        
        appearance = {}
        if self.current_data.appearance:
            try: appearance = json.loads(self.current_data.appearance)
            except: pass
            
        appearance["shape"] = self.shape_combo.currentData()
        appearance["color_override"] = self._current_colors["node"]
        appearance["textColor"] = self._current_colors["text"]
        appearance["fontFamily"] = self.font_combo.currentFont().family()
        appearance["fontSize"] = self.font_size.value()
        
        # Border
        appearance["borderColor"] = self._current_colors["border"]
        appearance["borderWidth"] = self.border_width.value()
        appearance["borderStyle"] = self.border_style.currentData()
        
        # Clean None values? No, keep logic simple
        
        data = {
            "id": self.current_data.id,
            "title": self.title_edit.text(),
            # "content": self.content_edit.toPlainText(),
            "tags": tags,
            "appearance": appearance
        }
        self.node_updated.emit(data)

    def _save_edge(self):
        if self.current_type != "edge" or not self.current_data: return
        
        appearance = {}
        if self.current_data.appearance:
            try: appearance = json.loads(self.current_data.appearance)
            except: pass
            
        appearance["style"] = self.edge_style_combo.currentData()
        appearance["color"] = self._current_colors["edge"]
        
        data = {
            "id": self.current_data.id,
            "relation_type": self.current_data.relation_type, # Keep existing type
            "appearance": appearance
        }
        print(f"[Inspector] Saving Edge: {data}")
        self.edge_updated.emit(data)
