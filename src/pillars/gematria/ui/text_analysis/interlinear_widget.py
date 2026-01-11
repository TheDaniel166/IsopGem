"""
Interlinear Verse Widget - Word-level display for TQ Concordance.

Displays a verse with each word as a clickable element showing:
- The word itself
- Its TQ gematria value
- Click action to show definitions and cross-references
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QToolTip, QSizePolicy, QDialog, QListWidget, QListWidgetItem,
    QLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect, QSize
from PyQt6.QtGui import QFont, QColor, QMouseEvent, QCursor
import re
from typing import List, Optional, Dict, Any

import logging
logger = logging.getLogger(__name__)

# Visual Liturgy compliance
from shared.ui.theme import COLORS


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
        language: Optional[str] = None,
        cipher: Optional[str] = None,
        parent=None
    ):
        super().__init__(parent)
        self.word = word
        self.tq_value = tq_value
        self.key_id = key_id
        self.definitions = definitions or []
        self.frequency = frequency
        self.language = language
        self.cipher = cipher

        self._setup_ui()
        
    def _setup_ui(self):
        """Configure the word label appearance."""
        logger.info(f"WordLabel._setup_ui: word={self.word}, tq={self.tq_value}, key_id={self.key_id}, has_key={self.key_id is not None}")

        # Language-specific icons and Visual Liturgy-compliant colors
        lang_config = {
            "Hebrew": {"icon": "🕎", "bg": COLORS['seeker_soft'], "border": COLORS['seeker'], "hover_bg": COLORS['seeker_soft'], "hover_border": COLORS['seeker_hover']},
            "Greek": {"icon": "🏛️", "bg": COLORS['cloud'], "border": COLORS['focus'], "hover_bg": COLORS['marble'], "hover_border": COLORS['focus']},
            "Arabic": {"icon": "🕌", "bg": COLORS['scribe_soft'], "border": COLORS['scribe'], "hover_bg": COLORS['scribe_soft'], "hover_border": COLORS['scribe_hover']},
            "Latin": {"icon": "🏛️", "bg": COLORS['destroyer_soft'], "border": COLORS['destroyer'], "hover_bg": COLORS['destroyer_soft'], "hover_border": COLORS['destroyer']},
        }

        config = lang_config.get(self.language, None)

        # Display format: word with value and optional language badge
        if config:
            # Non-English: show language icon
            display_html = f"""
                <div style='text-align: center; padding: 2px;'>
                    <span style='font-size: 11px;'>{config['icon']}</span>
                    <span style='font-size: 14px; font-weight: 500;'>{self.word}</span><br/>
                    <span style='font-size: 10px; color: {COLORS['magus_hover']};'>{self.tq_value}</span>
                </div>
            """
        else:
            # English: no icon
            display_html = f"""
                <div style='text-align: center; padding: 2px;'>
                    <span style='font-size: 14px; font-weight: 500;'>{self.word}</span><br/>
                    <span style='font-size: 10px; color: {COLORS['magus_hover']};'>{self.tq_value}</span>
                </div>
            """

        self.setText(display_html)
        self.setTextFormat(Qt.TextFormat.RichText)

        # Style based on language and indexed status
        if config:
            # Non-English word
            if self.key_id:
                # Indexed + non-English
                self.setStyleSheet(f"""
                    QLabel {{
                        background-color: {config['bg']};
                        border: 2px solid {config['border']};
                        border-radius: 4px;
                        padding: 4px 6px;
                        margin: 2px;
                    }}
                    QLabel:hover {{
                        background-color: {config['hover_bg']};
                        border-color: {config['hover_border']};
                    }}
                """)
            else:
                # Not indexed + non-English
                self.setStyleSheet(f"""
                    QLabel {{
                        background-color: {config['bg']};
                        border: 1px solid {config['border']};
                        border-radius: 4px;
                        padding: 4px 6px;
                        margin: 2px;
                    }}
                """)
        else:
            # English word (Visual Liturgy styling)
            if self.key_id:
                self.setStyleSheet(f"""
                    QLabel {{
                        background-color: {COLORS['magus_soft']};
                        border: 1px solid {COLORS['magus_soft']};
                        border-radius: 4px;
                        padding: 4px 6px;
                        margin: 2px;
                    }}
                    QLabel:hover {{
                        background-color: {COLORS['magus_soft']};
                        border-color: {COLORS['magus_mute']};
                    }}
                """)
            else:
                self.setStyleSheet(f"""
                    QLabel {{
                        background-color: {COLORS['marble']};
                        border: 1px solid {COLORS['ash']};
                        border-radius: 4px;
                        padding: 4px 6px;
                        margin: 2px;
                    }}
                """)
            
        self.setCursor(Qt.CursorShape.PointingHandCursor if self.key_id else Qt.CursorShape.ArrowCursor)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
    def mousePressEvent(self, event: QMouseEvent):
        """Handle click to emit signal."""
        logger.info(f"WordLabel.mousePressEvent: {self.word}, button={event.button()}, has_key_id={self.key_id is not None}")
        if event.button() == Qt.MouseButton.LeftButton and self.key_id:
            logger.info(f"WordLabel emitting clicked signal: {self.word}, {self.tq_value}, {self.key_id}")
            self.clicked.emit(self.word, self.tq_value, self.key_id)
        super().mousePressEvent(event)
        
    # Tooltips disabled - click words to see full details
    # def enterEvent(self, event):
    #     """Show tooltip with definitions on hover."""
    #     if self.definitions:
    #         tooltip_text = f"<b>{self.word}</b> (TQ: {self.tq_value})<br/>"
    #         if self.frequency > 0:
    #             tooltip_text += f"<i>Appears {self.frequency}x in corpus</i><br/><br/>"
    #         for _i, d in enumerate(self.definitions[:3]):
    #             tooltip_text += f"• {d[:80]}...<br/>" if len(d) > 80 else f"• {d}<br/>"
    #         if len(self.definitions) > 3:
    #             tooltip_text += f"<i>...and {len(self.definitions) - 3} more</i>"
    #         QToolTip.showText(QCursor.pos(), tooltip_text, self)
    #     super().enterEvent(event)


class InterlinearVerseWidget(QWidget):
    """
    Widget that displays a verse in interlinear format with word-level TQ values.
    
    Each word is displayed with its TQ value beneath it, and clicking a word
    shows its definitions and cross-references from the concordance.
    """
    word_clicked = pyqtSignal(str, int, int)  # word, tq_value, key_id
    
    def __init__(self, calculator=None, key_service=None, multi_lang_calculator=None, parent=None):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        super().__init__(parent)
        self.calculator = calculator  # Legacy single calculator (fallback)
        self.multi_lang_calculator = multi_lang_calculator  # Multi-language calculator (preferred)
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
        self.header_label.setStyleSheet(f"""
            font-weight: bold;
            color: {COLORS['magus_hover']};
            font-size: 12px;
            padding: 4px;
        """)
        layout.addWidget(self.header_label)

        # Words container - NO scroll area, just expand naturally
        self.words_container = QWidget()
        self.words_layout = FlowLayout(self.words_container)
        self.words_layout.setSpacing(4)

        layout.addWidget(self.words_container)
        
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
        
        logger.info(f"Creating {len(words)} word labels for verse")
        for word in words:
            word_data = self._get_word_data(word)
            logger.info(f"Word '{word}': TQ={word_data['tq_value']}, key_id={word_data.get('key_id')}, lang={word_data.get('language')}, cipher={word_data.get('cipher')}")
            label = WordLabel(
                word=word,
                tq_value=word_data['tq_value'],
                key_id=word_data.get('key_id'),
                definitions=word_data.get('definitions', []),
                frequency=word_data.get('frequency', 0),
                language=word_data.get('language'),
                cipher=word_data.get('cipher')
            )
            label.clicked.connect(self._on_word_clicked)
            self.words_layout.addWidget(label)
            
    def _tokenize(self, text: str) -> List[str]:
        """Extract words from text (Unicode-aware for Hebrew, Greek, etc.)."""
        # Unicode-aware word extraction (includes Hebrew, Greek, etc.)
        # \w matches Unicode word characters including Hebrew/Greek letters
        words = re.findall(r"\w+", text, re.UNICODE)
        return words
        
    def _get_word_data(self, word: str) -> Dict[str, Any]:
        """
        Get gematria value and concordance data for a word.

        Uses multi-language calculator if available to auto-detect language
        and use appropriate cipher.

        Returns dict with:
            - tq_value: The gematria value (using language-appropriate cipher)
            - key_id: The master key ID (if indexed)
            - definitions: List of definition strings
            - frequency: Total occurrences
            - language: Detected language (if using multi-lang calculator)
            - cipher: Cipher name used for calculation
        """
        result = {'tq_value': 0, 'key_id': None, 'definitions': [], 'frequency': 0, 'language': None, 'cipher': None}

        # Calculate gematria value using language-aware calculator
        if self.multi_lang_calculator:
            try:
                from shared.services.gematria.language_detector import LanguageDetector

                # Detect word language
                lang = LanguageDetector.detect_word_language(word)
                result['language'] = lang.value

                # Get appropriate calculator
                calc = self.multi_lang_calculator.get_calculator_for_word(word)
                if calc:
                    result['tq_value'] = calc.calculate(word)
                    result['cipher'] = calc.name
                    logger.debug(f"Multi-lang calc: '{word}' → {result['tq_value']} ({lang.value}, {calc.name})")
                else:
                    logger.warning(f"No calculator found for word '{word}' (language: {lang.value})")
            except Exception as e:
                logger.error(f"Multi-lang calc error for '{word}': {e}", exc_info=True)
        elif self.calculator:
            # Fallback to single calculator
            try:
                result['tq_value'] = self.calculator.calculate(word)
                result['cipher'] = self.calculator.name if hasattr(self.calculator, 'name') else 'Unknown'
            except Exception:
                pass
                
        # Look up in key database
        if self.key_service:
            try:
                key_id = self.key_service.db.get_id_by_word(word.lower())  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
                
                # AUTO-INDEX: If word not found and it's non-English, add it to lexicon
                if not key_id and result.get('language') and result['language'] not in ['English', 'Unknown']:
                    logger.info(f"Auto-indexing non-English word: '{word}' ({result['language']}, value={result['tq_value']})")
                    try:
                        key_id = self.key_service.db.add_word(word.lower(), result['tq_value'])  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
                        logger.info(f"Successfully auto-indexed '{word}' with key_id={key_id}")
                    except Exception as e:
                        logger.error(f"Failed to auto-index '{word}': {e}", exc_info=True)
                
                if key_id:
                    result['key_id'] = key_id
                    
                    # Get frequency from word_occurrences
                    occurrences = self.key_service.db.get_word_occurrences(key_id)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
                    result['frequency'] = len(occurrences)
                    
                    # Get definitions
                    defs = self.key_service.db.get_definitions(key_id)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
                    result['definitions'] = [d.content for d in defs]
            except Exception as e:
                logger.debug(f"Error looking up word '{word}': {e}")
                
        return result
        
    def _on_word_clicked(self, word: str, tq_value: int, key_id: int):
        """Handle word click - emit signal for parent to show details."""
        logger.info(f"InterlinearVerseWidget._on_word_clicked: {word}, {tq_value}, {key_id}")
        self.word_clicked.emit(word, tq_value, key_id)


class FlowLayout(QLayout):
    """
    Flow layout that wraps widgets to next line when they exceed width.
    Properly implements word wrapping for interlinear display.
    """
    def __init__(self, parent=None, margin=4, spacing=4):
        super().__init__(parent)
        self.item_list = []
        self.m_spacing = spacing

        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.item_list.append(item)

    def count(self):
        return len(self.item_list)

    def itemAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())

        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def _do_layout(self, rect, test_only=False):
        """Perform the layout - arrange items in rows that wrap."""
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.m_spacing

        for item in self.item_list:
            widget = item.widget()
            if widget is None:
                continue

            space_x = spacing
            space_y = spacing

            next_x = x + item.sizeHint().width() + space_x

            if next_x - space_x > rect.right() and line_height > 0:
                # Move to next line
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()


class InterlinearDocumentView(QWidget):
    """
    Full document view with interlinear display for all verses.
    """
    def __init__(self, calculator=None, key_service=None, multi_lang_calculator=None, parent=None):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        super().__init__(parent)
        self.calculator = calculator
        self.multi_lang_calculator = multi_lang_calculator
        self.key_service = key_service
        self._verses = []

        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        self.lbl_info = QLabel("Interlinear View")
        self.lbl_info.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {COLORS['magus_hover']};")
        toolbar.addWidget(self.lbl_info)
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # Scroll area for verses
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {COLORS['ash']};
                border-radius: 8px;
                background: {COLORS['light']};
            }}
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
                key_service=self.key_service,
                multi_lang_calculator=self.multi_lang_calculator
            )
            verse_widget.set_verse(
                verse_text=v.get('text', ''),
                verse_number=v.get('verse_number')
            )
            verse_widget.word_clicked.connect(self._on_word_clicked)
            
            # Add separator
            frame = QFrame()
            frame.setFrameShape(QFrame.Shape.HLine)
            frame.setStyleSheet(f"background-color: {COLORS['ash']};")
            
            self.verses_layout.insertWidget(self.verses_layout.count() - 1, verse_widget)
            self.verses_layout.insertWidget(self.verses_layout.count() - 1, frame)
            
        self.lbl_info.setText(f"Interlinear View ({len(verses)} verses)")
        
    def _on_word_clicked(self, word: str, tq_value: int, key_id: int, etymology_chain: Optional[List[str]] = None):
        """Show word details dialog with enriched data.
        
        Args:
            word: The word to display
            tq_value: TQ value of the word
            key_id: Database key ID
            etymology_chain: Optional list of ancestor words for breadcrumb navigation
        """
        logger.info(f"Word clicked: {word} (TQ: {tq_value}, key_id: {key_id})")
        
        from shared.services.lexicon.holy_key_service import HolyKeyService
        from PyQt6.QtWidgets import QTextBrowser
        
        if not self.key_service:
            self.key_service = HolyKeyService()
            
        # Initialize etymology chain
        if etymology_chain is None:
            etymology_chain = []
            
        try:
            # Create formatted dialog
            dlg = QDialog(self)
            dlg.setWindowTitle(f"Word Analysis: {word}")
            dlg.resize(700, 600)
        
            layout = QVBoxLayout(dlg)
            layout.setSpacing(10)
            
            # Use QTextBrowser for rich formatting
            browser = QTextBrowser()
            browser.setOpenExternalLinks(False)  # We'll handle links ourselves
            browser.setOpenLinks(False)  # Prevent browser from navigating
            browser.setStyleSheet("""
                QTextBrowser {
                    background-color: white;
                    font-size: 13px;
                    padding: 15px;
                }
            """)
            
            # Store the HTML content so we can restore it if needed
            html_content = None
            
            # Connect link handler for etymology exploration
            def handle_link(url):
                from PyQt6.QtCore import QUrl
                from urllib.parse import unquote
                url_str = url.toString() if isinstance(url, QUrl) else str(url)
                
                # Decode URL-encoded characters
                url_str = unquote(url_str)
                
                # Prevent browser navigation - restore content after processing
                if url_str.startswith('etymology:'):
                    # Extract word and language from link
                    parts = url_str[10:].split('|')
                    if len(parts) >= 1:
                        ancestor_word = parts[0]
                        ancestor_lang = parts[1] if len(parts) > 1 else 'English'
                        # Restore the browser content before opening new dialog
                        if html_content:
                            browser.setHtml(html_content)
                        # Don't close main dialog - keep it open
                        self._explore_etymology(ancestor_word, ancestor_lang, etymology_chain + [word], parent_dialog=dlg)
                elif url_str.startswith('http'):
                    import webbrowser
                    webbrowser.open(url_str)
                    # Restore content after external link
                    if html_content:
                        browser.setHtml(html_content)
            
            browser.anchorClicked.connect(handle_link)
            
            # Auto-detect language from script (language awareness) - Do this FIRST
            detected_lang = "English"  # Default
            lang_icon = "🔤"  # Default icon
            for char in word:
                if '\u0590' <= char <= '\u05ff':  # Hebrew
                    detected_lang = "Hebrew"
                    lang_icon = "🕎"
                    break
                elif ('\u0370' <= char <= '\u03ff') or ('\u1f00' <= char <= '\u1fff'):  # Greek
                    detected_lang = "Ancient Greek"
                    lang_icon = "🏛️"
                    break

            # Build HTML content
            html_parts = []

            # Header with breadcrumb navigation and detected language
            breadcrumb_html = ""
            if etymology_chain:
                breadcrumb_html = "<p style='margin: 10px 0 0 0; font-size: 13px; opacity: 0.8;'>🔗 Etymology trail: " + " → ".join(etymology_chain) + f" → <b>{word}</b></p>"

            html_parts.append(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 20px; margin: -15px -15px 15px -15px; color: white; border-radius: 8px 8px 0 0;'>
                <h1 style='margin: 0; font-size: 32px; font-weight: bold;'>{word}</h1>
                <p style='margin: 5px 0 0 0; font-size: 16px; opacity: 0.9;'>TQ Value: <b>{tq_value}</b> | {lang_icon} Language: <b>{detected_lang}</b></p>
                {breadcrumb_html}
            </div>
            """)

            # Get all data
            definitions = self.key_service.db.get_definitions(key_id)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
            occurrences = self.key_service.db.get_word_occurrences(key_id)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]

            # Query etymology database for ancestor words (use detected language)
            from shared.services.lexicon.etymology_db_service import EtymologyDbService
            etym_service = EtymologyDbService()
            etym_relations = etym_service.get_etymologies(word.lower(), detected_lang, max_results=15)
            
            # Etymology Chain section (interactive)
            if etym_relations:
                html_parts.append("<h2 style='color: #9333ea; border-bottom: 2px solid #e9d5ff; padding-bottom: 5px; margin-top: 20px;'>🔗 Etymology Chain (clickable)</h2>")
                
                # Group by relationship type
                from collections import defaultdict
                etym_by_type: defaultdict[str, list] = defaultdict(list)
                for rel in etym_relations:
                    etym_by_type[rel.reltype].append(rel)
                
                type_icons = {
                    'inherited_from': '👪',
                    'borrowed_from': '🔄',
                    'learned_borrowing_from': '📚',
                    'derived_from': '🌱',
                    'has_root': '🌳',
                    'compound_of': '🧩'
                }
                
                for rel_type in ['inherited_from', 'borrowed_from', 'learned_borrowing_from', 'derived_from', 'has_root', 'compound_of']:
                    if rel_type in etym_by_type:
                        icon = type_icons.get(rel_type, '•')
                        type_title = rel_type.replace('_', ' ').title()
                        html_parts.append(f"<h3 style='color: #9333ea; margin-top: 12px; margin-bottom: 6px;'>{icon} {type_title}</h3>")
                        
                        for rel in etym_by_type[rel_type]:
                            if rel.related_term:
                                lang_display = rel.related_lang if rel.related_lang else 'English'
                                clickable_term = f"<a href='etymology:{rel.related_term}|{lang_display}' style='color: #7c3aed; font-weight: bold; text-decoration: underline; cursor: pointer;' title='Click to explore {rel.related_term}'>{rel.related_term}</a>"
                                
                                html_parts.append(f"""
                                <div style='background: #f3e8ff; padding: 10px; margin: 5px 0; 
                                            border-left: 3px solid #9333ea; border-radius: 4px;'>
                                    From <span style='color: #6b7280;'>{lang_display}</span>: {clickable_term}
                                </div>
                                """)
            
            # Group definitions by type (normalize to uppercase for consistency)
            from collections import defaultdict
            def_by_type: defaultdict[str, list] = defaultdict(list)
            for d in definitions:
                def_by_type[d.type.upper()].append(d.content)
            
            # Definitions section
            if definitions:
                html_parts.append("<h2 style='color: #7c3aed; border-bottom: 2px solid #e9d5ff; padding-bottom: 5px; margin-top: 20px;'>📖 Definitions</h2>")
                
                # Priority order for definition types
                type_order = ['THEOSOPHICAL', 'ETYMOLOGY', 'STANDARD', 'WIKTIONARY', 'OPENOCCULT', 'FREEDICT', 'MANUAL']
                type_icons = {
                    'THEOSOPHICAL': '✨',
                    'ETYMOLOGY': '🌍',
                    'STANDARD': '📖',
                    'WIKTIONARY': '📚',
                    'OPENOCCULT': '🔮',
                    'FREEDICT': '📖',
                    'MANUAL': '✍️'
                }
                
                for def_type in type_order:
                    if def_type in def_by_type:
                        icon = type_icons.get(def_type, '•')
                        html_parts.append(f"<h3 style='color: #6366f1; margin-top: 15px; margin-bottom: 8px;'>{icon} {def_type.title()}</h3>")
                        
                        # Special handling for STANDARD definitions - group by part of speech
                        if def_type == 'STANDARD':
                            grouped_defs = self._group_definitions_by_pos(def_by_type[def_type])
                            
                            # Display each part of speech group
                            pos_order = ['noun', 'verb', 'adjective', 'adverb', 'preposition', 'conjunction', 'pronoun', 'interjection']
                            for pos in pos_order:
                                if pos in grouped_defs:
                                    pos_display = pos.capitalize()
                                    html_parts.append(f"<h4 style='color: #8b5cf6; margin-top: 12px; margin-bottom: 6px; font-size: 14px;'>• {pos_display}</h4>")
                                    
                                    for idx, content in enumerate(grouped_defs[pos], 1):
                                        content_clean = content.strip()
                                        if len(content_clean) > 500:
                                            content_clean = content_clean[:500] + "..."
                                        
                                        html_parts.append(f"""
                                        <div style='background: #f9fafb; padding: 10px; margin: 4px 0 4px 15px; 
                                                    border-left: 3px solid #c4b5fd; border-radius: 4px;'>
                                            <span style='color: #7c3aed; font-weight: bold; margin-right: 8px;'>{idx}.</span>{content_clean}
                                        </div>
                                        """)
                            
                            # Display ungrouped definitions (no clear part of speech)
                            if 'other' in grouped_defs:
                                html_parts.append(f"<h4 style='color: #8b5cf6; margin-top: 12px; margin-bottom: 6px; font-size: 14px;'>• Other</h4>")
                                for idx, content in enumerate(grouped_defs['other'], 1):
                                    content_clean = content.strip()
                                    if len(content_clean) > 500:
                                        content_clean = content_clean[:500] + "..."
                                    
                                    html_parts.append(f"""
                                    <div style='background: #f9fafb; padding: 10px; margin: 4px 0 4px 15px; 
                                                border-left: 3px solid #d1d5db; border-radius: 4px;'>
                                        <span style='color: #6b7280; font-weight: bold; margin-right: 8px;'>{idx}.</span>{content_clean}
                                    </div>
                                    """)
                        else:
                            # Regular display for other definition types
                            for content in def_by_type[def_type]:
                                # Clean up and format content
                                content_clean = content.strip()
                                
                                # Make etymology terms clickable
                                if def_type == 'ETYMOLOGY':
                                    content_clean = self._make_etymology_clickable(content_clean)
                                
                                if len(content_clean) > 500:
                                    content_clean = content_clean[:500] + "..."
                                
                                html_parts.append(f"""
                                <div style='background: #f9fafb; padding: 12px; margin: 5px 0; 
                                            border-left: 3px solid #c4b5fd; border-radius: 4px;'>
                                    {content_clean}
                                </div>
                                """)
                
                # Other types not in priority list
                for def_type, contents in def_by_type.items():
                    if def_type not in type_order:
                        html_parts.append(f"<h3 style='color: #6366f1; margin-top: 15px;'>• {def_type.title()}</h3>")
                        for content in contents:
                            content_clean = content.strip()
                            if len(content_clean) > 300:
                                content_clean = content_clean[:300] + "..."
                            html_parts.append(f"""
                            <div style='background: #f9fafb; padding: 12px; margin: 5px 0; 
                                        border-left: 3px solid #d1d5db; border-radius: 4px;'>
                                {content_clean}
                            </div>
                            """)
            else:
                html_parts.append("""
                <div style='background: #fef3c7; padding: 15px; margin: 20px 0; border-radius: 4px; 
                            border-left: 4px solid #f59e0b;'>
                    <b>⚠️ No definitions recorded</b><br>
                    <span style='font-size: 12px; color: #92400e;'>
                    Use the Lexicon window to enrich this word with definitions.
                    </span>
                </div>
                """)
            
            # Occurrences section
            if occurrences:
                html_parts.append(f"""
                <h2 style='color: #7c3aed; border-bottom: 2px solid #e9d5ff; padding-bottom: 5px; margin-top: 25px;'>
                    📍 Occurrences ({len(occurrences)})
                </h2>
                """)
                
                # Group by document
                from collections import defaultdict
                occ_by_doc: defaultdict[str, list] = defaultdict(list)
                for occ in occurrences:
                    occ_by_doc[occ.document_title].append(occ)
                
                for doc_title, doc_occs in occ_by_doc.items():
                    html_parts.append(f"<h3 style='color: #6366f1; margin-top: 12px;'>📜 {doc_title} ({len(doc_occs)})</h3>")
                    
                    for occ in doc_occs[:10]:  # Limit to 10 per document
                        verse_ref = f"Verse {occ.verse_number}" if occ.verse_number else "prose"
                        context = occ.context_snippet[:100] if occ.context_snippet else ""
                        
                        context_html = ""
                        if context:
                            context_html = f"<br><span style='font-size: 12px; color: #6b7280;'>&quot;{context}...&quot;</span>"
                        
                        html_parts.append(f"""
                        <div style='background: #ede9fe; padding: 10px; margin: 5px 0; border-radius: 4px;'>
                            <span style='color: #7c3aed; font-weight: bold;'>{verse_ref}</span>
                            {context_html}
                        </div>
                        """)
                    
                    if len(doc_occs) > 10:
                        html_parts.append(f"<p style='font-size: 12px; color: #9ca3af; margin-left: 10px;'>...and {len(doc_occs) - 10} more</p>")
            else:
                html_parts.append("""
                <div style='background: #fef3c7; padding: 15px; margin: 20px 0; border-radius: 4px; 
                            border-left: 4px solid #f59e0b;'>
                    <b>⚠️ No occurrences recorded</b><br>
                    <span style='font-size: 12px; color: #92400e;'>
                    This word hasn't been indexed in any documents yet.
                    </span>
                </div>
                """)
            
            # Summary footer
            html_parts.append(f"""
            <div style='background: #f3f4f6; padding: 12px; margin-top: 25px; border-radius: 4px; 
                        border-top: 2px solid #d1d5db; font-size: 12px; color: #6b7280;'>
                <b>Summary:</b> {len(definitions)} definitions from {len(def_by_type)} sources | 
                {len(occurrences)} occurrences in {len(occ_by_doc) if occurrences else 0} documents
            </div>
            """)
            
            # Store the HTML content for restoration after link clicks
            html_content = "".join(html_parts)
            browser.setHtml(html_content)
            layout.addWidget(browser)
            
            # Close button
            from PyQt6.QtWidgets import QPushButton, QHBoxLayout
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            btn_close = QPushButton("Close")
            btn_close.clicked.connect(dlg.accept)
            btn_close.setStyleSheet("""
                QPushButton {
                    background: #7c3aed;
                    color: white;
                    border: none;
                    padding: 8px 24px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #6d28d9;
                }
            """)
            btn_layout.addWidget(btn_close)
            layout.addLayout(btn_layout)
            
            dlg.exec()
            
        except Exception as e:
            logger.error(f"Error showing word details for '{word}': {e}", exc_info=True)
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", f"Could not load word details:\n{e}")
    
    def _group_definitions_by_pos(self, definitions: List[str]) -> Dict[str, List[str]]:
        """Group definitions by part of speech, normalizing variations.
        
        Extracts part of speech from patterns like:
        - (Noun) definition
        - (adjective) definition
        - (Adverb) definition
        
        Returns dict with normalized POS as keys and lists of cleaned definitions as values.
        """
        import re
        grouped: Dict[str, List[str]] = {}
        
        for definition in definitions:
            # Extract part of speech from first parentheses
            match = re.match(r'\(([^)]+)\)\s*(.*)', definition.strip())
            
            if match:
                pos_raw = match.group(1).strip()
                content = match.group(2).strip()
                
                # Normalize part of speech (lowercase, extract main word)
                pos_normalized = pos_raw.lower()
                
                # Map variations to standard forms
                if 'noun' in pos_normalized:
                    pos_key = 'noun'
                elif 'verb' in pos_normalized:
                    pos_key = 'verb'
                elif 'adjective' in pos_normalized or 'adjectiv' in pos_normalized:
                    pos_key = 'adjective'
                elif 'adverb' in pos_normalized:
                    pos_key = 'adverb'
                elif 'preposition' in pos_normalized:
                    pos_key = 'preposition'
                elif 'conjunction' in pos_normalized:
                    pos_key = 'conjunction'
                elif 'pronoun' in pos_normalized:
                    pos_key = 'pronoun'
                elif 'interjection' in pos_normalized:
                    pos_key = 'interjection'
                else:
                    # Keep it in "other" category
                    pos_key = 'other'
                
                # Store the cleaned definition (without the POS prefix)
                if pos_key not in grouped:
                    grouped[pos_key] = []
                grouped[pos_key].append(content)
            else:
                # No part of speech found - add to "other"
                if 'other' not in grouped:
                    grouped['other'] = []
                grouped['other'].append(definition.strip())
        
        return grouped
    
    def _make_etymology_clickable(self, content: str) -> str:
        """Make etymology terms clickable in definitions.

        Converts patterns like:
        - From Ancient Greek 'word' → extracts language and makes clickable
        - From 'word' → assumes English
        - *word* → reconstructed Proto forms
        """
        import re
        import html

        # First escape any HTML in the content to prevent injection
        content = html.escape(content)

        # Pattern 1: From Language 'word' - extract language context
        def replace_with_language(match):
            lang = match.group(1)
            term = match.group(2)
            # Normalize language names
            lang = lang.strip()
            if lang.lower() in ['greek', 'ancient greek']:
                lang = 'Ancient Greek'
            elif lang.lower() == 'hebrew':
                lang = 'Hebrew'

            # Create clickable link with extracted language
            link = f'<a href="etymology:{html.escape(term)}|{html.escape(lang)}" style="color: #7c3aed; font-weight: bold; text-decoration: underline;" title="Explore {html.escape(term)} ({html.escape(lang)})">{html.escape(term)}</a>'
            return f"From {html.escape(lang)} {link}"

        # Match: "From Language 'term'" or "From Language/language 'term'"
        content = re.sub(r"From\s+([\w\s]+?)\s+&#x27;([^&#x27;]+)&#x27;", replace_with_language, content)

        # Pattern 2: From 'word' (no language specified - assume English)
        def replace_single_quotes(match):
            term = match.group(1)
            link = f'<a href="etymology:{html.escape(term)}|English" style="color: #7c3aed; font-weight: bold; text-decoration: underline;" title="Explore {html.escape(term)}">{html.escape(term)}</a>'
            return f"From {link}"
        content = re.sub(r"From\s+&#x27;([^&#x27;]+)&#x27;", replace_single_quotes, content)

        # Pattern 3: *word* (asterisks - reconstructed Proto forms)
        def replace_asterisks(match):
            term = match.group(1)
            link = f'<a href="etymology:{html.escape(term)}|Proto-Indo-European" style="color: #9333ea; font-weight: bold; text-decoration: underline;" title="Explore Proto form {html.escape(term)}">*{html.escape(term)}*</a>'
            return link
        content = re.sub(r"\*([^\*]+)\*", replace_asterisks, content)

        return content
    
    def _explore_etymology(self, word: str, language: str, chain: List[str], parent_dialog=None):
        """Open etymology explorer for an ancestor word.

        Args:
            word: The word to explore
            language: The language of the word
            chain: Current etymology chain for breadcrumb navigation
            parent_dialog: Optional parent dialog to keep alive
        """
        from shared.services.lexicon.etymology_db_service import EtymologyDbService
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout
        from urllib.parse import unquote

        # Clean the word (remove URL encoding artifacts)
        word = unquote(word).strip()

        try:
            etym_service = EtymologyDbService()
            relations = etym_service.get_etymologies(word, language, max_results=20)

            # Detect if word contains Greek or Hebrew characters (do this early for error messages)
            import unicodedata
            has_greek = any('\u0370' <= c <= '\u03FF' or '\u1F00' <= c <= '\u1FFF' for c in word)
            has_hebrew = any('\u0590' <= c <= '\u05FF' for c in word)

            # Check language parameter or auto-detect from script
            is_greek = (language.lower() in ['greek', 'ancient greek']) or has_greek
            is_hebrew = (language.lower() == 'hebrew') or has_hebrew

            # If no etymology data, try classical lexicons for Greek/Hebrew, then comprehensive lexicon
            lexicon_entries = []
            if not relations:
                if is_greek:
                    from shared.services.lexicon.classical_lexicon_service import ClassicalLexiconService
                    lexicon_service = ClassicalLexiconService()
                    lexicon_entries = lexicon_service.lookup_greek(word, prefer_classical=True)
                elif is_hebrew:
                    from shared.services.lexicon.classical_lexicon_service import ClassicalLexiconService
                    lexicon_service = ClassicalLexiconService()
                    lexicon_entries = lexicon_service.lookup_hebrew(word)
                else:
                    # For other languages, try comprehensive lexicon service
                    from shared.services.lexicon.comprehensive_lexicon_service import ComprehensiveLexiconService
                    comp_service = ComprehensiveLexiconService()
                    lexicon_entries = comp_service.lookup(word, language)

            if not relations and not lexicon_entries:
                from PyQt6.QtWidgets import QMessageBox
                msg = QMessageBox(self)
                msg.setWindowTitle("No Data")

                # Provide helpful context based on language
                if is_greek or is_hebrew:
                    lang_name = "Greek" if is_greek else "Hebrew"
                    detailed_msg = f"The word '{word}' appears to be {lang_name}, but:\n\n"
                    detailed_msg += f"• Not found in Strong's {lang_name} Dictionary (Biblical words)\n"
                    detailed_msg += f"• Not indexed as a main entry in etymology database\n\n"
                    detailed_msg += f"This word may be:\n"
                    detailed_msg += f"• A Classical {lang_name} word not in Biblical texts\n"
                    detailed_msg += f"• An inflected/declined form (not the lemma/dictionary form)\n"
                    detailed_msg += f"• Referenced in etymology chains but not directly indexed\n\n"

                    if is_greek:
                        detailed_msg += f"For Classical Greek, try:\n"
                        detailed_msg += f"• Logeion LSJ: logeion.uchicago.edu/{word}\n"
                        detailed_msg += f"• Perseus Digital Library: perseus.tufts.edu"
                else:
                    # Get list of available languages from comprehensive service
                    from shared.services.lexicon.comprehensive_lexicon_service import ComprehensiveLexiconService
                    comp_service = ComprehensiveLexiconService()
                    available_langs = comp_service.get_available_languages()

                    detailed_msg = f"No etymology or lexicon data found for '{word}' ({language})\n\n"
                    if available_langs:
                        detailed_msg += f"Available offline languages:\n"
                        detailed_msg += f"• {', '.join(available_langs[:10])}"
                        if len(available_langs) > 10:
                            detailed_msg += f" (+{len(available_langs)-10} more)"
                    else:
                        detailed_msg += f"No offline lexicons available."

                msg.setText(detailed_msg)
                msg.setIcon(QMessageBox.Icon.Information)
                msg.exec()
                # Don't close parent - just return
                return
            
            # Create etymology explorer dialog
            dlg = QDialog(self)
            dlg.setWindowTitle(f"Etymology: {word} ({language})")
            dlg.resize(700, 500)
            
            layout = QVBoxLayout(dlg)
            layout.setSpacing(10)
            
            browser = QTextBrowser()
            browser.setOpenExternalLinks(False)
            browser.setStyleSheet("""
                QTextBrowser {
                    background-color: white;
                    font-size: 13px;
                    padding: 15px;
                }
            """)
            
            # Handle nested etymology clicks
            def handle_nested_link(url):
                from PyQt6.QtCore import QUrl
                from urllib.parse import unquote
                url_str = url.toString() if isinstance(url, QUrl) else str(url)
                
                # Decode URL-encoded characters
                url_str = unquote(url_str)
                
                if url_str.startswith('etymology:'):
                    parts = url_str[10:].split('|')
                    if len(parts) >= 1:
                        nested_word = parts[0]
                        nested_lang = parts[1] if len(parts) > 1 else language
                        dlg.close()  # Close current dialog
                        self._explore_etymology(nested_word, nested_lang, chain + [word], parent_dialog)
            
            browser.anchorClicked.connect(handle_nested_link)
            
            # Build HTML
            html_parts = []
            
            # Header with breadcrumb
            breadcrumb_html = ""
            if chain:
                breadcrumb_html = "<p style='margin: 10px 0 0 0; font-size: 13px; opacity: 0.8;'>🔗 Etymology trail: " + " → ".join(chain) + f" → <b>{word}</b></p>"
            
            html_parts.append(f"""
            <div style='background: linear-gradient(135deg, #9333ea 0%, #581c87 100%); 
                        padding: 20px; margin: -15px -15px 15px -15px; color: white; border-radius: 8px 8px 0 0;'>
                <h1 style='margin: 0; font-size: 28px; font-weight: bold;'>{word}</h1>
                <p style='margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;'>Language: {language}</p>
                {breadcrumb_html}
            </div>
            """)
            
            # Display etymology relations OR lexicon entries
            if relations:
                html_parts.append(f"<h2 style='color: #7c3aed; border-bottom: 2px solid #e9d5ff; padding-bottom: 5px;'>📜 Etymology ({len(relations)} relationships)</h2>")

                # Group by relationship type
                from collections import defaultdict
                rels_by_type: defaultdict[str, list] = defaultdict(list)
                for rel in relations:
                    rels_by_type[rel.reltype].append(rel)

                # Display each type
                type_icons = {
                    'inherited_from': '👪',
                    'borrowed_from': '🔄',
                    'learned_borrowing_from': '📚',
                    'derived_from': '🌱',
                    'has_root': '🌳',
                    'compound_of': '🧩'
                }

                for rel_type, rels in rels_by_type.items():
                    icon = type_icons.get(rel_type, '•')
                    type_title = rel_type.replace('_', ' ').title()
                    html_parts.append(f"<h3 style='color: #6366f1; margin-top: 15px;'>{icon} {type_title}</h3>")

                    for rel in rels:
                        if rel.related_term:
                            # Make related term clickable
                            related_lang_display = rel.related_lang if rel.related_lang else language
                            clickable_term = f"<a href='etymology:{rel.related_term}|{related_lang_display}' style='color: #7c3aed; font-weight: bold; text-decoration: underline; cursor: pointer;' title='Explore {rel.related_term}'>{rel.related_term}</a>"

                            html_parts.append(f"""
                            <div style='background: #f3e8ff; padding: 10px; margin: 5px 0; border-left: 3px solid #9333ea; border-radius: 4px;'>
                                From {related_lang_display}: {clickable_term}
                            </div>
                            """)

            # Display lexicon entries if no etymology data
            if lexicon_entries:
                html_parts.append(f"<h2 style='color: #7c3aed; border-bottom: 2px solid #e9d5ff; padding-bottom: 5px;'>📖 Lexicon ({len(lexicon_entries)} entries)</h2>")

                for entry in lexicon_entries:
                    # Source badge
                    source_color = "#9333ea" if "Strong" in entry.source else "#2563eb"
                    html_parts.append(f"""
                    <div style='background: #f9fafb; padding: 15px; margin: 10px 0; border-radius: 6px; border: 1px solid #e5e7eb;'>
                        <div style='margin-bottom: 8px;'>
                            <span style='background: {source_color}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;'>{entry.source}</span>
                    """)

                    if entry.strong_number:
                        html_parts.append(f"<span style='color: #6b7280; font-size: 12px; margin-left: 8px;'>Strong's {entry.strong_number}</span>")

                    html_parts.append("</div>")

                    # Word and transliteration
                    html_parts.append(f"<div style='font-size: 18px; font-weight: bold; color: #1f2937; margin-bottom: 5px;'>{entry.word}</div>")

                    if entry.transliteration:
                        html_parts.append(f"<div style='color: #6b7280; font-style: italic; margin-bottom: 10px;'>{entry.transliteration}</div>")

                    # Definition
                    if entry.definition:
                        html_parts.append(f"""
                        <div style='background: white; padding: 10px; border-left: 3px solid {source_color}; margin-top: 8px;'>
                            <b>Definition:</b><br>
                            {entry.definition}
                        </div>
                        """)

                    # Etymology/Derivation
                    if entry.etymology:
                        html_parts.append(f"""
                        <div style='background: #fef3c7; padding: 10px; border-left: 3px solid #f59e0b; margin-top: 8px;'>
                            <b>Etymology:</b><br>
                            {entry.etymology}
                        </div>
                        """)

                    html_parts.append("</div>")
            
            browser.setHtml("".join(html_parts))
            layout.addWidget(browser)
            
            # Close button
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            btn_close = QPushButton("Close")
            btn_close.clicked.connect(dlg.accept)
            btn_close.setStyleSheet("""
                QPushButton {
                    background: #7c3aed;
                    color: white;
                    border: none;
                    padding: 8px 24px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #6d28d9;
                }
            """)
            btn_layout.addWidget(btn_close)
            layout.addLayout(btn_layout)
            
            dlg.exec()
            
        except Exception as e:
            logger.error(f"Error exploring etymology for '{word}': {e}", exc_info=True)
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", f"Could not explore etymology:\n{e}")
