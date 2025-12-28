"""Shape Picker Dialog - Visual Liturgy styled shape selection.

A custom dialog that replaces QInputDialog with a grid of shape cards
following the Visual Liturgy design principles.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QWidget, QGridLayout, QLineEdit,
    QGraphicsDropShadowEffect, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from .liturgy_styles import LiturgyColors, LiturgyButtons


class ShapeCard(QFrame):
    """Individual shape card in the picker grid."""
    
    clicked = pyqtSignal(dict)  # Emits the shape definition
    
    def __init__(self, shape_def: dict, accent_color: str, parent=None):
        """
          init   logic.
        
        Args:
            shape_def: Description of shape_def.
            accent_color: Description of accent_color.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self._shape_def = shape_def
        self._accent_color = accent_color
        self._setup_ui()
        
    def _setup_ui(self):
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(100)
        self.setMinimumWidth(180)
        
        # Check if shape is "Coming Soon"
        is_disabled = self._shape_def.get('status') == 'Coming Soon'
        
        if is_disabled:
            self.setStyleSheet(f"""
                QFrame {{
                    background: {LiturgyColors.MARBLE};
                    border: 1px solid {LiturgyColors.ASH};
                    border-radius: 16px;
                }}
            """)
            self.setCursor(Qt.CursorShape.ForbiddenCursor)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff, stop:1 #f8fafc);
                    border: 1px solid {LiturgyColors.ASH};
                    border-radius: 16px;
                }}
                QFrame:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff, stop:1 #f1f5f9);
                    border-color: {self._accent_color};
                }}
            """)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)
        
        # Title
        name = self._shape_def.get('name', 'Unknown')
        title = QLabel(name)
        title.setStyleSheet(f"""
            QLabel {{
                color: {LiturgyColors.VOID if not is_disabled else LiturgyColors.VOID_SLATE};
                font-size: 12pt;
                font-weight: 700;
                background: transparent;
            }}
        """)
        layout.addWidget(title)
        
        # Summary
        summary_text = self._shape_def.get('summary', '')
        if is_disabled:
            summary_text = "Coming Soon"
        summary = QLabel(summary_text)
        summary.setWordWrap(True)
        summary.setStyleSheet(f"""
            QLabel {{
                color: {LiturgyColors.STONE if not is_disabled else LiturgyColors.VOID_SLATE};
                font-size: 9pt;
                background: transparent;
            }}
        """)
        layout.addWidget(summary)
        layout.addStretch()
        
        self._is_disabled = is_disabled
        
    def mousePressEvent(self, event):
        """
        Mousepressevent logic.
        
        Args:
            event: Description of event.
        
        """
        if not self._is_disabled:
            self.clicked.emit(self._shape_def)
        super().mousePressEvent(event)


class ShapePickerDialog(QDialog):
    """Custom dialog for selecting a shape from a category.
    
    Follows Visual Liturgy design with a grid of shape cards,
    search/filter capability, and smooth animations.
    """
    
    shape_selected = pyqtSignal(dict)  # Emits the selected shape definition
    
    # Category accent colors
    CATEGORY_COLORS = {
        'Circles': '#3b82f6',
        'Triangles': '#10b981',
        'Quadrilaterals': '#f97316',
        'Polygons': '#06b6d4',
        'Sacred Geometry': '#8b5cf6',
        'Pyramids': '#ec4899',
        'Prisms': '#14b8a6',
        'Antiprisms': '#f43f5e',
        'Platonic Solids': '#eab308',
        'Archimedean Solids': '#a855f7',
        'Curves & Surfaces': '#0ea5e9',
        'Other Solids': '#0ea5e9',
        'Hypercube': '#7c3aed',
    }
    
    def __init__(self, category: dict, parent=None):
        """
          init   logic.
        
        Args:
            category: Description of category.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self._category = category
        self._shapes = category.get('shapes', [])
        self._cards: List[ShapeCard] = []
        self._selected_shape: Optional[dict] = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        self.setWindowTitle(f"Select {self._category.get('name', 'Shape')}")
        self.setModal(True)
        self.resize(700, 500)
        
        # Window styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {LiturgyColors.CLOUD_SLATE};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header = self._build_header()
        layout.addWidget(header)
        
        # Search bar
        search_container = self._build_search_bar()
        layout.addWidget(search_container)
        
        # Shape grid (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; }
            QScrollArea > QWidget > QWidget { background: transparent; }
        """)
        
        self._grid_container = QWidget()
        self._grid_container.setStyleSheet("background: transparent;")
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setSpacing(12)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)
        
        self._populate_grid(self._shapes)
        
        scroll.setWidget(self._grid_container)
        layout.addWidget(scroll, 1)
        
        # Footer with cancel button
        footer = self._build_footer()
        layout.addWidget(footer)
        
    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setStyleSheet("background: transparent;")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(4)
        
        # Category icon + name
        cat_name = self._category.get('name', 'Shapes')
        cat_icon = self._category.get('icon', '◯')
        
        title_row = QHBoxLayout()
        
        icon_label = QLabel(cat_icon)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24pt;
                color: {self.CATEGORY_COLORS.get(cat_name, '#64748b')};
                background: transparent;
            }}
        """)
        title_row.addWidget(icon_label)
        
        title = QLabel(f"Select {cat_name}")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 22pt;
                font-weight: 800;
                color: {LiturgyColors.VOID};
                background: transparent;
            }}
        """)
        title_row.addWidget(title)
        title_row.addStretch()
        
        header_layout.addLayout(title_row)
        
        # Tagline
        tagline = QLabel(self._category.get('tagline', ''))
        tagline.setStyleSheet(f"""
            QLabel {{
                font-size: 10pt;
                color: {LiturgyColors.STONE};
                background: transparent;
            }}
        """)
        header_layout.addWidget(tagline)
        
        return header
        
    def _build_search_bar(self) -> QWidget:
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("🔍 Filter shapes...")
        self._search_input.setStyleSheet(f"""
            QLineEdit {{
                background: {LiturgyColors.LIGHT};
                border: 1px solid {LiturgyColors.ASH};
                border-radius: 12px;
                padding: 10px 16px;
                font-size: 11pt;
                color: {LiturgyColors.VOID};
            }}
            QLineEdit:focus {{
                border-color: {self.CATEGORY_COLORS.get(self._category.get('name', ''), '#64748b')};
            }}
        """)
        self._search_input.textChanged.connect(self._on_search_changed)
        layout.addWidget(self._search_input)
        
        return container
        
    def _build_footer(self) -> QWidget:
        footer = QWidget()
        footer.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(0, 8, 0, 0)
        
        layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(LiturgyButtons.navigator())
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
        
        return footer
        
    def _populate_grid(self, shapes: List[dict]):
        # Clear existing cards
        for card in self._cards:
            card.setParent(None)
            card.deleteLater()
        self._cards.clear()
        
        # Clear grid layout
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # Get accent color for this category
        cat_name = self._category.get('name', '')
        accent = self.CATEGORY_COLORS.get(cat_name, '#64748b')
        
        # Add shape cards (3 columns)
        cols = 3
        for i, shape_def in enumerate(shapes):
            card = ShapeCard(shape_def, accent)
            card.clicked.connect(self._on_shape_selected)
            self._cards.append(card)
            self._grid_layout.addWidget(card, i // cols, i % cols)
        
        # Add stretch at the bottom
        self._grid_layout.setRowStretch(len(shapes) // cols + 1, 1)
        
    def _on_search_changed(self, text: str):
        """Filter shapes based on search text."""
        if not text.strip():
            self._populate_grid(self._shapes)
            return
            
        query = text.lower()
        filtered = [
            s for s in self._shapes
            if query in s.get('name', '').lower() or query in s.get('summary', '').lower()
        ]
        self._populate_grid(filtered)
        
    def _on_shape_selected(self, shape_def: dict):
        """Handle shape card click."""
        self._selected_shape = shape_def
        self.shape_selected.emit(shape_def)
        self.accept()
        
    def get_selected_shape(self) -> Optional[dict]:
        """Return the selected shape definition."""
        return self._selected_shape