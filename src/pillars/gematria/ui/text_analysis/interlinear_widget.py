"""
Interlinear Verse Widget - Word-level display for TQ Concordance.

Displays a verse with each word as a clickable element showing:
- The word itself
- Its TQ gematria value
- Click action to show definitions and cross-references
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QToolTip, QSizePolicy, QDialog, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QFont, QColor, QMouseEvent, QCursor
import re
from typing import List, Optional, Dict, Any

import logging
logger = logging.getLogger(__name__)


class WordLabel(QLabel):
    """
    A clickable word label that displays the word and its TQ value.
    """
    clicked = pyqtSignal(str, int, int)  # word, tq_value, key_id
    
    def __init__(
        self, 
        word: str, 
        tq_value: int, 
        key_id: Optional[int] = None,
        definitions: List[str] = None,
        frequency: int = 0,
        parent=None
    ):
        super().__init__(parent)
        self.word = word
        self.tq_value = tq_value
        self.key_id = key_id
        self.definitions = definitions or []
        self.frequency = frequency
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Configure the word label appearance."""
        # Display format: word with TQ subscript
        display_html = f"""
            <div style='text-align: center; padding: 2px;'>
                <span style='font-size: 14px; font-weight: 500;'>{self.word}</span><br/>
                <span style='font-size: 10px; color: #7c3aed;'>{self.tq_value}</span>
            </div>
        """
        self.setText(display_html)
        self.setTextFormat(Qt.TextFormat.RichText)
        
        # Style based on whether it's indexed
        if self.key_id:
            self.setStyleSheet("""
                QLabel {
                    background-color: #faf5ff;
                    border: 1px solid #e9d5ff;
                    border-radius: 4px;
                    padding: 4px 6px;
                    margin: 2px;
                }
                QLabel:hover {
                    background-color: #ede9fe;
                    border-color: #c4b5fd;
                    cursor: pointer;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    background-color: #f5f5f5;
                    border: 1px solid #e5e5e5;
                    border-radius: 4px;
                    padding: 4px 6px;
                    margin: 2px;
                }
            """)
            
        self.setCursor(Qt.CursorShape.PointingHandCursor if self.key_id else Qt.CursorShape.ArrowCursor)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
    def mousePressEvent(self, event: QMouseEvent):
        """Handle click to emit signal."""
        if event.button() == Qt.MouseButton.LeftButton and self.key_id:
            self.clicked.emit(self.word, self.tq_value, self.key_id)
        super().mousePressEvent(event)
        
    def enterEvent(self, event):
        """Show tooltip with definitions on hover."""
        if self.definitions:
            tooltip_text = f"<b>{self.word}</b> (TQ: {self.tq_value})<br/>"
            if self.frequency > 0:
                tooltip_text += f"<i>Appears {self.frequency}x in corpus</i><br/><br/>"
            for _i, d in enumerate(self.definitions[:3]):
                tooltip_text += f"• {d[:80]}...<br/>" if len(d) > 80 else f"• {d}<br/>"
            if len(self.definitions) > 3:
                tooltip_text += f"<i>...and {len(self.definitions) - 3} more</i>"
            QToolTip.showText(QCursor.pos(), tooltip_text, self)
        super().enterEvent(event)


class InterlinearVerseWidget(QWidget):
    """
    Widget that displays a verse in interlinear format with word-level TQ values.
    
    Each word is displayed with its TQ value beneath it, and clicking a word
    shows its definitions and cross-references from the concordance.
    """
    word_clicked = pyqtSignal(str, int, int)  # word, tq_value, key_id
    
    def __init__(self, calculator=None, key_service=None, parent=None):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        super().__init__(parent)
        self.calculator = calculator
        self.key_service = key_service
        self._verse_text = ""
        self._verse_number = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Initialize the UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Verse header
        self.header_label = QLabel("")
        self.header_label.setStyleSheet("""
            font-weight: bold;
            color: #7c3aed;
            font-size: 12px;
            padding: 4px;
        """)
        layout.addWidget(self.header_label)
        
        # Scroll area for words
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        self.words_container = QWidget()
        self.words_layout = FlowLayout(self.words_container)
        self.words_layout.setSpacing(4)
        
        scroll.setWidget(self.words_container)
        layout.addWidget(scroll)
        
    def set_verse(self, verse_text: str, verse_number: Optional[int] = None):
        """
        Set the verse text and render it in interlinear format.
        
        Args:
            verse_text: The verse content
            verse_number: Optional verse number for display
        """
        self._verse_text = verse_text
        self._verse_number = verse_number
        
        # Update header
        if verse_number:
            self.header_label.setText(f"Verse {verse_number}")
        else:
            self.header_label.setText("")
            
        # Clear existing words
        while self.words_layout.count():
            item = self.words_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Tokenize and create word labels
        words = self._tokenize(verse_text)
        
        for word in words:
            word_data = self._get_word_data(word)
            label = WordLabel(
                word=word,
                tq_value=word_data['tq_value'],
                key_id=word_data.get('key_id'),
                definitions=word_data.get('definitions', []),
                frequency=word_data.get('frequency', 0)
            )
            label.clicked.connect(self._on_word_clicked)
            self.words_layout.addWidget(label)
            
    def _tokenize(self, text: str) -> List[str]:
        """Extract words from text."""
        # Keep only alphabetic words
        words = re.findall(r"[a-zA-Z]+", text)
        return words
        
    def _get_word_data(self, word: str) -> Dict[str, Any]:
        """
        Get TQ value and concordance data for a word.
        
        Returns dict with:
            - tq_value: The TQ gematria value
            - key_id: The master key ID (if indexed)
            - definitions: List of definition strings
            - frequency: Total occurrences
        """
        result = {'tq_value': 0, 'key_id': None, 'definitions': [], 'frequency': 0}
        
        # Calculate TQ value
        if self.calculator:
            try:
                result['tq_value'] = self.calculator.calculate(word)
            except Exception:
                pass
                
        # Look up in key database
        if self.key_service:
            try:
                key_entry = self.key_service.db.get_word(word.lower())  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
                if key_entry:
                    result['key_id'] = key_entry.id
                    result['frequency'] = key_entry.frequency
                    
                    # Get definitions
                    defs = self.key_service.db.get_definitions(key_entry.id)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
                    result['definitions'] = [d.content for d in defs]
            except Exception as e:
                logger.debug(f"Error looking up word '{word}': {e}")
                
        return result
        
    def _on_word_clicked(self, word: str, tq_value: int, key_id: int):
        """Handle word click - emit signal for parent to show details."""
        self.word_clicked.emit(word, tq_value, key_id)


class FlowLayout(QHBoxLayout):
    """
    Simple flow layout that wraps widgets to next line.
    For a proper flow layout, a custom implementation would be needed,
    but this uses a horizontal layout with word wrap via the scroll area.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSpacing(4)
        self.setContentsMargins(4, 4, 4, 4)
        
        # Actually use a VBox with nested HBoxes for row wrapping
        # This is a simplified version - for production, use a proper FlowLayout


class InterlinearDocumentView(QWidget):
    """
    Full document view with interlinear display for all verses.
    """
    def __init__(self, calculator=None, key_service=None, parent=None):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        super().__init__(parent)
        self.calculator = calculator
        self.key_service = key_service
        self._verses = []
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        self.lbl_info = QLabel("Interlinear View")
        self.lbl_info.setStyleSheet("font-weight: bold; font-size: 14px; color: #7c3aed;")
        toolbar.addWidget(self.lbl_info)
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # Scroll area for verses
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background: white;
            }
        """)
        
        self.verses_container = QWidget()
        self.verses_layout = QVBoxLayout(self.verses_container)
        self.verses_layout.setSpacing(8)
        self.verses_layout.setContentsMargins(8, 8, 8, 8)
        self.verses_layout.addStretch()
        
        scroll.setWidget(self.verses_container)
        layout.addWidget(scroll)
        
    def set_verses(self, verses: List[Dict[str, Any]]):
        """
        Load verses into the interlinear view.
        
        Args:
            verses: List of dicts with 'text' and optional 'verse_number'
        """
        self._verses = verses
        
        # Clear existing
        while self.verses_layout.count() > 1:  # Keep stretch
            item = self.verses_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Add verse widgets
        for v in verses:
            verse_widget = InterlinearVerseWidget(
                calculator=self.calculator,
                key_service=self.key_service
            )
            verse_widget.set_verse(
                verse_text=v.get('text', ''),
                verse_number=v.get('verse_number')
            )
            verse_widget.word_clicked.connect(self._on_word_clicked)
            
            # Add separator
            frame = QFrame()
            frame.setFrameShape(QFrame.Shape.HLine)
            frame.setStyleSheet("background-color: #e5e7eb;")
            
            self.verses_layout.insertWidget(self.verses_layout.count() - 1, verse_widget)
            self.verses_layout.insertWidget(self.verses_layout.count() - 1, frame)
            
        self.lbl_info.setText(f"Interlinear View ({len(verses)} verses)")
        
    def _on_word_clicked(self, word: str, tq_value: int, key_id: int):
        """Show word details dialog."""
        from shared.services.lexicon.holy_key_service import HolyKeyService
        
        if not self.key_service:
            self.key_service = HolyKeyService()
            
        # Show simple info dialog
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Word: {word}")
        dlg.resize(400, 300)
        
        layout = QVBoxLayout(dlg)
        
        # Header
        header = QLabel(f"<h2>{word}</h2><p>TQ Value: <b>{tq_value}</b></p>")
        header.setStyleSheet("color: #7c3aed;")
        layout.addWidget(header)
        
        # Definitions
        layout.addWidget(QLabel("<b>Definitions:</b>"))
        def_list = QListWidget()
        definitions = self.key_service.db.get_definitions(key_id)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
        for d in definitions:
            def_list.addItem(QListWidgetItem(f"[{d.type}] {d.content}"))
        if not definitions:
            def_list.addItem(QListWidgetItem("No definitions recorded"))
        layout.addWidget(def_list)
        
        # Occurrences
        layout.addWidget(QLabel("<b>Occurrences:</b>"))
        occ_list = QListWidget()
        occurrences = self.key_service.db.get_word_occurrences(key_id)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
        for occ in occurrences[:10]:
            verse_ref = f"Verse {occ.verse_number}" if occ.verse_number else "(prose)"
            occ_list.addItem(QListWidgetItem(f"{occ.document_title} - {verse_ref}"))
        if not occurrences:
            occ_list.addItem(QListWidgetItem("No occurrences recorded"))
        elif len(occurrences) > 10:
            occ_list.addItem(QListWidgetItem(f"...and {len(occurrences) - 10} more"))
        layout.addWidget(occ_list)
        
        dlg.exec()
