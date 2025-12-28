"""Horizontal rule insertion dialog for Rich Text Editor."""
from PyQt6.QtWidgets import (
    QVBoxLayout, QFormLayout, QHBoxLayout,
    QSpinBox, QComboBox, QToolButton, QWidget, QLabel
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from .base_dialog import BaseEditorDialog


class HorizontalRuleDialog(BaseEditorDialog):
    """Dialog for customizing horizontal rule options."""
    
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        self.line_color = QColor("#cccccc")
        super().__init__("Insert Horizontal Line", parent, min_width=350)
    
    def _setup_ui(self):
        form = self.create_form_layout()
        
        # Line thickness
        self.thickness_spin = QSpinBox()
        self.thickness_spin.setRange(1, 20)
        self.thickness_spin.setValue(1)
        self.thickness_spin.setSuffix(" px")
        form.addRow("Thickness:", self.thickness_spin)
        
        # Line width
        self.width_spin = QSpinBox()
        self.width_spin.setRange(10, 100)
        self.width_spin.setValue(100)
        self.width_spin.setSuffix("%")
        form.addRow("Width:", self.width_spin)
        
        # Line style
        self.style_combo = QComboBox()
        self.style_combo.addItems(["Solid", "Dashed", "Dotted", "Double"])
        form.addRow("Style:", self.style_combo)
        
        # Line color - using base class utility
        self.color_button = QToolButton()
        self.color_button.setText("Choose Color")
        self.color_button.setStyleSheet(f"background-color: {self.line_color.name()}; min-width: 100px;")
        self.color_button.clicked.connect(self._on_color_click)
        form.addRow("Color:", self.color_button)
        
        # Alignment
        self.align_combo = QComboBox()
        self.align_combo.addItems(["Center", "Left", "Right"])
        form.addRow("Alignment:", self.align_combo)
        
        # Margins
        margin_widget = QWidget()
        margin_layout = QHBoxLayout(margin_widget)
        margin_layout.setContentsMargins(0, 0, 0, 0)
        
        self.margin_top_spin = QSpinBox()
        self.margin_top_spin.setRange(0, 100)
        self.margin_top_spin.setValue(10)
        self.margin_top_spin.setSuffix(" px")
        margin_layout.addWidget(QLabel("Top:"))
        margin_layout.addWidget(self.margin_top_spin)
        
        self.margin_bottom_spin = QSpinBox()
        self.margin_bottom_spin.setRange(0, 100)
        self.margin_bottom_spin.setValue(10)
        self.margin_bottom_spin.setSuffix(" px")
        margin_layout.addWidget(QLabel("Bottom:"))
        margin_layout.addWidget(self.margin_bottom_spin)
        
        form.addRow("Margins:", margin_widget)
        
        # Preview using a QFrame which respects styling
        self.layout.addWidget(QLabel("Preview:"))
        self.preview_frame = QWidget()
        self.preview_frame.setMinimumHeight(50)
        self.preview_frame.setStyleSheet("background: white; border: 1px solid #ddd;")
        preview_layout = QVBoxLayout(self.preview_frame)
        preview_layout.setContentsMargins(10, 10, 10, 10)
        
        self.preview_line = QWidget()
        self.preview_line.setFixedHeight(1)
        preview_layout.addWidget(self.preview_line, 0, Qt.AlignmentFlag.AlignCenter)
        
        self.layout.addWidget(self.preview_frame)
        self._update_preview()
        
        # Connect signals for live preview
        self.thickness_spin.valueChanged.connect(self._update_preview)
        self.width_spin.valueChanged.connect(self._update_preview)
        self.style_combo.currentTextChanged.connect(self._update_preview)
        self.align_combo.currentTextChanged.connect(self._update_preview)
        
        # Add OK/Cancel buttons using base class
        self.add_ok_cancel_buttons()
    
    def _on_color_click(self):
        """Handle color picker using base class utility."""
        new_color = self.pick_color(self.line_color, "Line Color")
        if new_color:
            self.line_color = new_color
            self.color_button.setStyleSheet(f"background-color: {self.line_color.name()}; min-width: 100px;")
            self._update_preview()
    
    def _update_preview(self):
        """Update the preview line widget."""
        color = self.line_color.name()
        thickness = self.thickness_spin.value()
        style = self.style_combo.currentText().lower()
        width_pct = self.width_spin.value()
        align = self.align_combo.currentText()
        
        # Calculate actual width based on preview container
        container_width = self.preview_frame.width() - 20  # minus padding
        if container_width < 100:
            container_width = 300  # default before shown
        line_width = int(container_width * width_pct / 100)
        
        # For double, use border-style: double which needs more height
        if style == "double":
            thickness = max(3, thickness)
        
        # Build border style for QWidget
        border_style = f"{thickness}px {style} {color}"
        
        self.preview_line.setFixedHeight(thickness if style != "double" else thickness)
        self.preview_line.setFixedWidth(line_width)
        self.preview_line.setStyleSheet(f"background: transparent; border-top: {border_style}; border-bottom: none; border-left: none; border-right: none;")
        
        # Update alignment
        preview_layout = self.preview_frame.layout()
        if align == "Left":
            preview_layout.setAlignment(self.preview_line, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        elif align == "Right":
            preview_layout.setAlignment(self.preview_line, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        else:
            preview_layout.setAlignment(self.preview_line, Qt.AlignmentFlag.AlignCenter)
    
    def _get_border_style(self) -> str:
        style_map = {
            "Solid": "solid",
            "Dashed": "dashed",
            "Dotted": "dotted",
            "Double": "double"
        }
        return style_map.get(self.style_combo.currentText(), "solid")
    
    def _get_alignment(self) -> str:
        align_map = {
            "Center": "center",
            "Left": "left",
            "Right": "right"
        }
        return align_map.get(self.align_combo.currentText(), "center")
    
    def get_html(self) -> str:
        """Generate HTML for the horizontal rule using a table (better QTextEdit support)."""
        color = self.line_color.name()
        thickness = self.thickness_spin.value()
        width = self.width_spin.value()
        margin_top = self.margin_top_spin.value()
        margin_bottom = self.margin_bottom_spin.value()
        align = self._get_alignment()
        style = self._get_border_style()
        
        # Use a table-based approach for better QTextEdit compatibility
        align_attr = 'align="center"' if align == "center" else f'align="{align}"'
        
        # For dashed/dotted, we use multiple small cells to simulate
        if style == "dashed":
            dash_cells = ''.join([f'<td style="background-color:{color}; width:8px;"></td><td style="width:4px;"></td>' for _ in range(40)])
            return f'''<table {align_attr} width="{width}%" cellspacing="0" cellpadding="0" border="0" style="margin-top:{margin_top}px; margin-bottom:{margin_bottom}px; border-collapse:collapse;">
                <tr style="height:{thickness}px; line-height:{thickness}px; font-size:1px;">{dash_cells}</tr>
            </table>'''
        elif style == "dotted":
            dot_cells = ''.join([f'<td style="background-color:{color}; width:{max(2,thickness)}px;"></td><td style="width:{max(2,thickness)}px;"></td>' for _ in range(60)])
            return f'''<table {align_attr} width="{width}%" cellspacing="0" cellpadding="0" border="0" style="margin-top:{margin_top}px; margin-bottom:{margin_bottom}px; border-collapse:collapse;">
                <tr style="height:{max(2,thickness)}px; line-height:{max(2,thickness)}px; font-size:1px;">{dot_cells}</tr>
            </table>'''
        elif style == "double":
            gap = max(2, thickness)
            return f'''<table {align_attr} width="{width}%" cellspacing="0" cellpadding="0" border="0" style="margin-top:{margin_top}px; margin-bottom:{margin_bottom}px; border-collapse:collapse;">
                <tr><td style="border-top:{thickness}px solid {color}; border-bottom:{thickness}px solid {color}; height:{gap}px; line-height:{gap}px; font-size:1px;"></td></tr>
            </table>'''
        else:
            return f'''<table {align_attr} width="{width}%" cellspacing="0" cellpadding="0" border="0" style="margin-top:{margin_top}px; margin-bottom:{margin_bottom}px; border-collapse:collapse;">
                <tr><td style="border-top:{thickness}px solid {color}; height:0; line-height:0; font-size:1px; padding:0;"></td></tr>
            </table>'''