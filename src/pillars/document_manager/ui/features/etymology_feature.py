"""
⚠️  GRANDFATHERED VIOLATION - Pre-existing before Law of Substrate (2026-01-13)

SHARED JUSTIFICATION:
- RATIONALE: UI Component (GRANDFATHERED - should move to pillars/document_manager)
- USED BY: Internal shared/ modules only (1 references)
- CRITERION: Violation (Single-pillar UI component)

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md
"""

"""
Etymology Feature for Document Manager.
Provides a research dialog to look up word origins.
"""

import qtawesome as qta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextBrowser, 
    QPushButton, QHBoxLayout, QMenu, QLineEdit, QDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QAction, QTextCursor
from typing import Optional, Any, Dict, Callable, List, TYPE_CHECKING
from urllib.parse import unquote
from shared.services.document_manager.etymology_service import get_etymology_service as _get_etymology_service
from shared.ui.virtual_keyboard import VirtualKeyboard
from shared.ui.rich_text_editor.feature_interface import EditorFeature

if TYPE_CHECKING:
    from shared.ui.rich_text_editor.editor import RichTextEditor


class EtymologyWorker(QThread):
    """Background thread to fetch data without freezing the UI."""
    finished = pyqtSignal(dict)

    def __init__(self, word: str) -> None:
        super().__init__()
        self.word = word

    def run(self) -> None:
        """Fetch etymology data from the service."""
        service = _get_etymology_service()
        result = service.get_word_origin(self.word)
        self.finished.emit(result)


class ResearchDialog(QDialog):
    """Dialog for Etymology Research - modal-less so user can keep editing."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Research & Etymology")
        self.setMinimumSize(450, 500)
        self._keyboard_visible = False
        self._search_callback: Optional[Callable[[str], None]] = None
        self._anchor_callback: Optional[Callable[[str], None]] = None
        self._back_callback: Optional[Callable[[], None]] = None
        self._forward_callback: Optional[Callable[[], None]] = None
        self.setup_ui()
        
        # Make it non-modal so user can continue editing
        self.setModal(False)

    def setup_ui(self) -> None:
        """Initialize and layout visual components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Search bar with keyboard toggle
        search_layout = QHBoxLayout()

        self.btn_back = QPushButton()
        self.btn_back.setIcon(qta.icon("fa5s.arrow-left", color="#1e293b"))
        self.btn_back.setToolTip("Back (history)")
        self.btn_back.setFixedWidth(32)
        self.btn_back.setEnabled(False)
        self.btn_back.clicked.connect(self._on_back)
        search_layout.addWidget(self.btn_back)

        self.btn_forward = QPushButton()
        self.btn_forward.setIcon(qta.icon("fa5s.arrow-right", color="#1e293b"))
        self.btn_forward.setToolTip("Forward (history)")
        self.btn_forward.setFixedWidth(32)
        self.btn_forward.setEnabled(False)
        self.btn_forward.clicked.connect(self._on_forward)
        search_layout.addWidget(self.btn_forward)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter word (λόγος, שלום, robot)...")
        self.input_field.returnPressed.connect(self._on_search)
        search_layout.addWidget(self.input_field)
        
        self.btn_keyboard = QPushButton()
        self.btn_keyboard.setIcon(qta.icon("fa5s.keyboard", color="#1e293b"))
        self.btn_keyboard.setToolTip("Toggle Greek/Hebrew Keyboard")
        self.btn_keyboard.setFixedWidth(36)
        self.btn_keyboard.clicked.connect(self._toggle_keyboard)
        search_layout.addWidget(self.btn_keyboard)
        
        btn_search = QPushButton("Search")
        btn_search.setIcon(qta.icon("fa5s.search", color="#1e293b"))
        btn_search.clicked.connect(self._on_search)
        search_layout.addWidget(btn_search)
        
        layout.addLayout(search_layout)
        
        # Virtual Keyboard (hidden by default)
        self.keyboard = VirtualKeyboard(parent=self)
        self.keyboard.set_target_input(self.input_field)
        self.keyboard.hide()
        layout.addWidget(self.keyboard)

        # Status Label
        self.lbl_status = QLabel("Enter a word or select text and click 'Word Origin'...")
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setStyleSheet("color: #64748b; font-style: italic;")
        layout.addWidget(self.lbl_status)

        # Browser for results
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)
        self.browser.setOpenLinks(False)
        self.browser.anchorClicked.connect(self._on_anchor_clicked)
        self.browser.setStyleSheet("""
            QTextBrowser { 
                border: 1px solid #cbd5e1; 
                background: #f8fafc; 
                padding: 10px;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        layout.addWidget(self.browser)
        
        # Copy button
        self.btn_copy = QPushButton("Copy Contents")
        self.btn_copy.setIcon(qta.icon("fa5s.copy", color="#1e293b"))
        self.btn_copy.clicked.connect(self._copy_to_clipboard)
        layout.addWidget(self.btn_copy)

    def _toggle_keyboard(self) -> None:
        """Toggle the virtual keyboard visibility."""
        self._keyboard_visible = not self._keyboard_visible
        if self._keyboard_visible:
            self.keyboard.show()
            self.btn_keyboard.setIcon(qta.icon("fa5s.keyboard", color="#3b82f6"))
        else:
            self.keyboard.hide()
            self.btn_keyboard.setIcon(qta.icon("fa5s.keyboard", color="#1e293b"))

    def _copy_to_clipboard(self) -> None:
        """Copy current browser text to system clipboard."""
        from PyQt6.QtWidgets import QApplication
        
        text = self.browser.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.lbl_status.setText("Copied to clipboard!")

    def _on_search(self) -> None:
        """Handle search from input field."""
        word = self.input_field.text().strip()
        if word and hasattr(self, '_search_callback'):
            self._search_callback(word)

    def _on_anchor_clicked(self, url: QUrl) -> None:
        """Route anchor clicks to caller; keeps navigation in-app."""
        if self._anchor_callback:
            self._anchor_callback(url.toString())

    def _on_back(self) -> None:
        if self._back_callback:
            self._back_callback()

    def _on_forward(self) -> None:
        if self._forward_callback:
            self._forward_callback()

    def set_search_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for when user searches from the dialog."""
        self._search_callback = callback

    def set_anchor_callback(self, callback: Callable[[str], None]) -> None:
        """Handle anchor clicks inside the browser."""
        self._anchor_callback = callback

    def set_navigation_callbacks(self, on_back: Callable[[], None], on_forward: Callable[[], None]) -> None:
        """Wire navigation callbacks for history traversal."""
        self._back_callback = on_back
        self._forward_callback = on_forward

    def set_nav_state(self, can_back: bool, can_forward: bool) -> None:
        """Enable/disable navigation buttons based on history state."""
        self.btn_back.setEnabled(can_back)
        self.btn_forward.setEnabled(can_forward)

    def show_loading(self, word: str) -> None:
        """Display loading state for a specific word."""
        self.input_field.setText(word)
        self.lbl_status.setText(f"Searching origins for: <b>{word}</b>...")
        self.browser.clear()
        self.show()
        self.raise_()
        self.activateWindow()

    def show_result(self, result: Dict[str, Any]) -> None:
        """Display the research result."""
        source = result.get('source', 'Unknown')
        origin_html = result.get('origin', '')
        
        html = f"""
        <style>
            h3 {{ color: #334155; margin-bottom: 5px; }}
            h4 {{ color: #475569; margin-top: 10px; margin-bottom: 2px; }}
            p, li {{ font-size: 11pt; line-height: 1.5; color: #1e293b; }}
            .source {{ color: #94a3b8; font-size: 9pt; margin-bottom: 10px; }}
            hr {{ border: none; border-top: 1px solid #e2e8f0; margin: 10px 0; }}
        </style>
        <div class="source">Source: {source}</div>
        <hr>
        {origin_html}
        """
        self.browser.setHtml(html)
        self.lbl_status.setText(f"Result via {source}")


class EtymologyFeature(EditorFeature):
    """Feature controller connecting the Editor and Research Dialog."""
    
    def __init__(self, parent_editor: 'RichTextEditor') -> None:
        """
        Initialize the etymology feature.
        
        Args:
            parent_editor: The main RichTextEditor instance.
        """
        super().__init__(parent_editor)
        # self.orchestrator and self.editor are set by super()
        
        self._dialog = None
        self._worker = None
        self._history: List[str] = []
        self._history_index = -1

    def initialize(self) -> None:
        """Perform post-initialization setup."""
        pass

    def _get_dialog(self) -> ResearchDialog:
        """Lazily create or return the research dialog."""
        if self._dialog is None:
            self._dialog = ResearchDialog(parent=self.orchestrator)
            self._dialog.set_search_callback(lambda word: self._do_research(word, record_history=True))
            self._dialog.set_anchor_callback(self._on_anchor_requested)
            self._dialog.set_navigation_callbacks(self._go_back, self._go_forward)
            self._dialog.set_nav_state(False, False)
        return self._dialog
        
    def create_action(self, parent: QWidget) -> QAction:
        """Construct the primary Ribbon action for this feature."""
        action = QAction("Word Origin", parent)
        action.setToolTip("Research selected word (Etymology)")
        action.setIcon(qta.icon("fa5s.book-open", color="#1e293b"))
        action.triggered.connect(self.research_selection)
        return action

    def research_selection(self) -> None:
        """Commence etymology research based on current editor selection."""
        cursor = self.editor.textCursor()
        selected_text = cursor.selectedText().strip()
        
        # If no selection, expand to word under cursor
        if not selected_text:
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
            selected_text = cursor.selectedText().strip()
        
        dialog = self._get_dialog()
        
        if not selected_text:
            dialog.input_field.clear()
            dialog.lbl_status.setText("Please select a word or type one above.")
            dialog.browser.clear()
            dialog.show()
            dialog.raise_()
            return

        self._do_research(selected_text)

    def _do_research(self, word: str, record_history: bool = True) -> None:
        """Perform the actual research lookup."""
        base_word = word.split('|', 1)[0]
        clean_word = base_word.strip()
        if not clean_word:
            return

        if record_history:
            self._push_history(clean_word)

        dialog = self._get_dialog()
        self._update_nav_buttons()
        dialog.show_loading(clean_word)
        
        self._worker = EtymologyWorker(clean_word)
        self._worker.finished.connect(dialog.show_result)
        self._worker.start()

    def _push_history(self, word: str) -> None:
        """Record lookup history with a max depth of five."""
        if not word:
            return

        if self._history_index >= 0 and self._history[self._history_index].lower() == word.lower():
            return

        if self._history_index < len(self._history) - 1:
            self._history = self._history[: self._history_index + 1]

        self._history.append(word)
        if len(self._history) > 5:
            self._history = self._history[-5:]

        self._history_index = len(self._history) - 1

    def _update_nav_buttons(self) -> None:
        dialog = self._get_dialog()
        can_back = self._history_index > 0
        can_forward = self._history_index < len(self._history) - 1 and self._history_index >= 0
        dialog.set_nav_state(can_back, can_forward)

    def _go_back(self) -> None:
        if self._history_index <= 0:
            return

        self._history_index -= 1
        self._update_nav_buttons()
        self._do_research(self._history[self._history_index], record_history=False)

    def _go_forward(self) -> None:
        if self._history_index >= len(self._history) - 1 or self._history_index < 0:
            return

        self._history_index += 1
        self._update_nav_buttons()
        self._do_research(self._history[self._history_index], record_history=False)

    def _on_anchor_requested(self, url_str: str) -> None:
        if not url_str:
            return

        if url_str.startswith('etymology:'):
            payload = url_str.split('etymology:', 1)[1]
            word_part = payload.split('|', 1)[0]
            target_word = unquote(word_part).strip()
            if target_word:
                self._do_research(target_word, record_history=True)

    def extend_context_menu(self, menu: QMenu, pos: Any = None) -> None:
        """Add research option to right-click menu."""
        cursor = self.editor.textCursor()
        text = cursor.selectedText().strip()
        
        if not text:
            # Check word under cursor without changing selection
            temp_cursor = QTextCursor(cursor)
            temp_cursor.select(QTextCursor.SelectionType.WordUnderCursor)
            text = temp_cursor.selectedText().strip()

        if text:
            # Truncate for menu if too long
            display_text = (text[:15] + '..') if len(text) > 15 else text
            action = QAction(
                qta.icon("fa5s.book-open", color="#1e293b"), 
                f"Research '{display_text}'", 
                menu
            )
            action.triggered.connect(self.research_selection)
            
            menu.addSeparator()
            menu.addAction(action)