from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QGroupBox, QFrame
)
from PyQt6.QtCore import Qt

class StatsPanel(QWidget):
    """
    Panel for displaying document statistics.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        group = QGroupBox("Document Statistics")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cbd5e1;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 16px; 
                padding-left: 8px;
                padding-right: 8px;
                font-size: 11pt;
            }
        """)
        group_layout = QFormLayout(group)
        group_layout.setSpacing(10)
        
        # Styles for labels
        lbl_style = "font-size: 10pt; color: #475569;"
        val_style = "font-size: 11pt; font-weight: 600; color: #0f172a;"
        
        self.word_count_lbl = QLabel("0")
        self.word_count_lbl.setStyleSheet(val_style)
        l1 = QLabel("Word Count:")
        l1.setStyleSheet(lbl_style)
        group_layout.addRow(l1, self.word_count_lbl)
        
        self.char_count_lbl = QLabel("0")
        self.char_count_lbl.setStyleSheet(val_style)
        l2 = QLabel("Character Count:")
        l2.setStyleSheet(lbl_style)
        group_layout.addRow(l2, self.char_count_lbl)
        
        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #e2e8f0;")
        group_layout.addRow(line)
        
        self.total_val_lbl = QLabel("0")
        self.total_val_lbl.setStyleSheet(f"{val_style} color: #2563eb;")
        l3 = QLabel("Total Gematria:")
        l3.setStyleSheet(lbl_style)
        group_layout.addRow(l3, self.total_val_lbl)
        
        self.avg_val_lbl = QLabel("0")
        self.avg_val_lbl.setStyleSheet(val_style)
        l4 = QLabel("Avg. Word Value:")
        l4.setStyleSheet(lbl_style)
        group_layout.addRow(l4, self.avg_val_lbl)
        
        layout.addWidget(group)
        layout.addStretch()
        
    def update_stats(self, stats: dict):
        """Update labels with stats dict."""
        self.word_count_lbl.setText(f"{stats.get('word_count', 0):,}")
        self.char_count_lbl.setText(f"{stats.get('char_count', 0):,}")
        self.total_val_lbl.setText(f"{stats.get('total_value', 0):,}")
        self.avg_val_lbl.setText(f"{stats.get('avg_word_val', 0):.2f}")
