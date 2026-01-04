"""
Verse List - The Sacred Stanza Catalog.
Widget displaying parsed verses with individual value calculation and navigation.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QGroupBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class VerseList(QWidget):
    """
    Widget for displaying a list of parsed verses.
    """
    verse_jump_requested = pyqtSignal(int, int)  # start, end
    verse_save_requested = pyqtSignal(dict)      # verse_data
    save_all_requested = pyqtSignal(list)        # list of verses
    
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.verses_data = []
        self._setup_ui()
        
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header / Status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #64748b; font-size: 9pt;")
        main_layout.addWidget(self.status_label)
        
        # Actions bar
        actions = QHBoxLayout()
        self.save_all_btn = QPushButton("💾 Save All Totals")
        self.save_all_btn.clicked.connect(lambda: self.save_all_requested.emit(self.verses_data))
        self.save_all_btn.setEnabled(False)
        actions.addWidget(self.save_all_btn)
        actions.addStretch()
        main_layout.addLayout(actions)
        
        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(8)
        self.scroll.setWidget(self.container)
        main_layout.addWidget(self.scroll)
        
    def render_verses(self, verses: List[Dict[str, Any]], calculator, include_face_values: bool, source_info: str = ""):
        """
        Render verses into the list.
        """
        self.clear()
        self.status_label.setText(source_info)

        # Filter out ignored and empty verses
        active_verses = []
        for v in verses:
            # Skip ignored verses
            if v.get('status') == 'ignored':
                continue
            # Skip empty verses
            if not v.get('text', '').strip():
                continue
            active_verses.append(v)

        self.verses_data = active_verses
        self.save_all_btn.setEnabled(bool(active_verses))
        
        if not active_verses:
            self.container_layout.addWidget(QLabel("No verses detected."))
            return
            
        from ...utils.numeric_utils import sum_numeric_face_values

        for v in active_verses:
            item = self._create_verse_item(v, calculator, include_face_values)  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
            self.container_layout.addWidget(item)
            
        self.container_layout.addStretch()
        
    def clear(self):
        """
        Clear logic.
        
        """
        while self.container_layout.count():
            child = self.container_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.verses_data = []
        self.save_all_btn.setEnabled(False)
        self.status_label.setText("")

    def _create_verse_item(self, verse, calculator, include_face_values):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        box = QGroupBox(f"Verse {verse['number']}")
        layout = QHBoxLayout(box)
        
        # Text
        text_lbl = QLabel(verse['text'])
        text_lbl.setWordWrap(True)
        text_lbl.setMinimumWidth(300)
        layout.addWidget(text_lbl, 3)
        
        # Value
        try:
            val = calculator.calculate(verse['text'])
            if include_face_values:
                from ...utils.numeric_utils import sum_numeric_face_values
                val += sum_numeric_face_values(verse['text'])
        except (AttributeError, TypeError) as e:
            logger.debug(
                "VerseList: value calculation fallback (%s): %s",
                type(e).__name__,
                e,
            )
            val = 0
            
        val_lbl = QLabel(f"Value: {val}")
        val_lbl.setStyleSheet("font-weight: 600; color: #2563eb;")
        layout.addWidget(val_lbl)
        
        # Actions
        btns = QVBoxLayout()
        jump = QPushButton("Jump")
        jump.clicked.connect(lambda _, s=verse['start'], e=verse['end']: self.verse_jump_requested.emit(s, e))  # type: ignore[reportUnknownArgumentType, reportUnknownLambdaType]
        btns.addWidget(jump)
        
        save = QPushButton("Save")
        save.clicked.connect(lambda _, v=verse: self.verse_save_requested.emit(v))  # type: ignore[reportUnknownArgumentType, reportUnknownLambdaType]
        btns.addWidget(save)
        
        layout.addLayout(btns)
        return box