"""
Formula Dialog - Display and interact with mathematical formulas.
Shows LaTeX-rendered equations with copy and screenshot capabilities.
"""
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QFrame, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QImage

from pillars.document_manager.ui.features.math_renderer import MathRenderer
from ...liturgy_styles import LiturgyColors, LiturgyButtons


class FormulaDialog(QDialog):
    """Dialog displaying mathematical formula with interaction options."""
    
    def __init__(self, property_name: str, formula_latex: str, parent=None):
        """
        Initialize the formula dialog.
        
        Args:
            property_name: Name of the property (e.g., "Area")
            formula_latex: LaTeX formula string
            parent: Parent widget
        """
        super().__init__(parent)
        self.property_name = property_name
        self.formula_latex = formula_latex
        self.rendered_image: Optional[QImage] = None
        
        self.setWindowTitle(f"Formula: {property_name}")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.resize(500, 400)
        
        self._setup_ui()
        self._render_formula()
    
    def _setup_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header = QLabel(f"Formula for {self.property_name}")
        header.setStyleSheet(f"font-size: 18pt; font-weight: 600; color: {LiturgyColors.VOID};")
        layout.addWidget(header)
        
        # Rendered Formula Display
        self.formula_display = QLabel()
        self.formula_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formula_display.setStyleSheet(f"""
            QLabel {{
                background-color: white;
                border: 2px solid {LiturgyColors.ASH};
                border-radius: 12px;
                padding: 24px;
                min-height: 100px;
            }}
        """)
        layout.addWidget(self.formula_display)
        
        # LaTeX Source Section
        latex_label = QLabel("LaTeX Source:")
        latex_label.setStyleSheet(f"font-weight: 600; color: {LiturgyColors.VOID_SLATE};")
        layout.addWidget(latex_label)
        
        self.latex_edit = QTextEdit()
        self.latex_edit.setPlainText(self.formula_latex)
        self.latex_edit.setReadOnly(True)
        self.latex_edit.setMaximumHeight(80)
        self.latex_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {LiturgyColors.CLOUD_SLATE};
                border: 1px solid {LiturgyColors.ASH};
                border-radius: 8px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
                color: {LiturgyColors.VOID};
            }}
        """)
        layout.addWidget(self.latex_edit)
        
        # Action Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.copy_latex_btn = QPushButton("📋 Copy LaTeX")
        self.copy_latex_btn.setToolTip("Copy LaTeX source to clipboard")
        self.copy_latex_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_latex_btn.setStyleSheet(LiturgyButtons.scribe())
        self.copy_latex_btn.clicked.connect(self._copy_latex)
        
        self.screenshot_btn = QPushButton("📸 Copy Image")
        self.screenshot_btn.setToolTip("Copy rendered formula as image")
        self.screenshot_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.screenshot_btn.setStyleSheet(LiturgyButtons.scribe())
        self.screenshot_btn.clicked.connect(self._copy_screenshot)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet(LiturgyButtons.secondary())
        self.close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(self.copy_latex_btn)
        button_layout.addWidget(self.screenshot_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def _render_formula(self):
        """Render the LaTeX formula using MathRenderer."""
        self.rendered_image = MathRenderer.render_latex(
            self.formula_latex, 
            fontsize=16, 
            dpi=150,
            color='#0f172a'  # VOID color for clarity
        )
        
        if self.rendered_image:
            pixmap = QPixmap.fromImage(self.rendered_image)
            # Scale if too large
            if pixmap.width() > 450:
                pixmap = pixmap.scaledToWidth(450, Qt.TransformationMode.SmoothTransformation)
            self.formula_display.setPixmap(pixmap)
        else:
            self.formula_display.setText("⚠️ Could not render formula")
            self.formula_display.setStyleSheet(
                self.formula_display.styleSheet() + 
                f"color: {LiturgyColors.CRIMSON}; font-size: 12pt;"
            )
            self.screenshot_btn.setEnabled(False)
    
    def _copy_latex(self):
        """Copy LaTeX source to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.formula_latex)
        
        # Visual feedback
        original_text = self.copy_latex_btn.text()
        self.copy_latex_btn.setText("✓ Copied!")
        self.copy_latex_btn.setEnabled(False)
        
        # Reset after delay
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1500, lambda: (
            self.copy_latex_btn.setText(original_text),
            self.copy_latex_btn.setEnabled(True)
        ))
    
    def _copy_screenshot(self):
        """Copy rendered formula image to clipboard."""
        if not self.rendered_image:
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setImage(self.rendered_image)
        
        # Visual feedback
        original_text = self.screenshot_btn.text()
        self.screenshot_btn.setText("✓ Copied!")
        self.screenshot_btn.setEnabled(False)
        
        # Reset after delay
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1500, lambda: (
            self.screenshot_btn.setText(original_text),
            self.screenshot_btn.setEnabled(True)
        ))
