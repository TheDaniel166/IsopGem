"""Reusable Rich Text Editor widget with Ribbon UI."""
from typing import Optional, Any, Union, List, Tuple, Dict, Generator
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QComboBox, QFontComboBox, QSpinBox,
    QColorDialog, QMenu, QToolButton, QDialog,
    QLabel, QDialogButtonBox, QFormLayout, QDoubleSpinBox, QMessageBox,
    QSlider, QLineEdit, QStatusBar, QFileDialog, QGridLayout,
    QScrollArea, QFrame, QGroupBox, QPushButton, QTabWidget, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QMimeData, QUrl, QMarginsF, QSizeF, QPoint
from PyQt6.QtGui import (
    QFont, QAction, QColor, QTextCharFormat,
    QTextCursor, QTextListFormat, QTextBlockFormat,
    QActionGroup, QBrush, QDesktopServices, QPageSize, QPageLayout, QKeySequence,
    QTextDocument
)
import qtawesome as qta
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog

# Feature modules
from .table_features import TableFeature
from .image_features import ImageFeature
from .list_features import ListFeature
from .search_features import SearchReplaceFeature
from .shape_features import ShapeFeature
from .ribbon_widget import RibbonWidget
from .etymology_feature import EtymologyFeature
from .spell_feature import SpellFeature
from .math_feature import MathFeature
from .mermaid_feature import MermaidFeature

# Dialog modules (extracted for modularity)
from .dialogs import (
    HyperlinkDialog, HorizontalRuleDialog, PageSetupDialog,
    SpecialCharactersDialog, ExportPdfDialog
)

# Page settings and constants
from .editor_constants import PageSettings, DEFAULT_PAGE_SETTINGS

# Shared UI
from shared.ui import VirtualKeyboard, get_shared_virtual_keyboard


class SafeTextEdit(QTextEdit):
    """
    A hardened QTextEdit that protects against 'Paste Attacks' (Mars Seal).
    Also supports visual page break indicators.
    """
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        Returns:
            Result of __init__ operation.
        """
        super().__init__(parent)
        self._show_page_breaks = False
        self._page_settings = DEFAULT_PAGE_SETTINGS
        
        # Pagination State
        self._page_height = 1056 # Matches Substrate
        self._page_gap = 20 # Matches Substrate
        self._is_paginating = False
        self.textChanged.connect(self._check_pagination)

    def _check_pagination(self):
        """
        Atomic Block Pagination: Ensures blocks don't straddle page boundaries.
        
        Algorithm:
        1. Iterate through all text blocks in the document
        2. For each block, check if it would cross a page boundary
        3. If so, add top margin to push it to the next page
        4. Blocks larger than a page are allowed to overflow
        """
        if self._is_paginating:
            return
            
        self._is_paginating = True
        try:
            doc = self.document()
            layout = doc.documentLayout()
            cycle = self._page_height + self._page_gap
            
            # Iterate all blocks
            block = doc.begin()
            while block.isValid():
                rect = layout.blockBoundingRect(block)
                
                # Skip empty or invisible blocks
                if rect.height() < 1:
                    block = block.next()
                    continue
                
                # Get block geometry
                block_top = rect.y()
                block_bottom = rect.bottom()
                block_height = rect.height()
                
                # Determine which page this block starts on
                page_num = int(block_top / cycle)
                
                # Position within the current cycle (0 = start of page)
                local_top = block_top - (page_num * cycle)
                local_bottom = block_bottom - (page_num * cycle)
                
                # Check if block would cross into the gap or next page
                needs_push = False
                
                # Case 1: Block starts in the gap
                if local_top >= self._page_height:
                    needs_push = True
                    
                # Case 2: Block starts on page but extends into gap
                elif local_bottom > self._page_height and block_height < self._page_height:
                    # Only push if block is smaller than a page
                    # (Large blocks like images are allowed to overflow)
                    needs_push = True
                
                if needs_push:
                    # Calculate how much to push
                    # We want to move the block to the start of the next page
                    next_page_start = (page_num + 1) * cycle
                    margin_needed = next_page_start - block_top
                    
                    # Apply margin to this block
                    fmt = block.blockFormat()
                    current_margin = fmt.topMargin()
                    
                    # Only add margin if not already set (avoid duplicates)
                    if abs(current_margin - margin_needed) > 1:
                        fmt.setTopMargin(margin_needed)
                        cursor = QTextCursor(block)
                        cursor.setBlockFormat(fmt)
                
                block = block.next()
                
        finally:
            self._is_paginating = False
    
    @property
    def page_height(self) -> int:
        """Get page height from settings."""
        return self._page_settings.content_height_pixels
    
    @property
    def show_page_breaks(self) -> bool:
        """
        Display page breaks logic.
        
        Returns:
            Result of show_page_breaks operation.
        """
        return self._show_page_breaks
    
    @show_page_breaks.setter
    def show_page_breaks(self, value: bool):
        """
        Display page breaks logic.
        
        Args:
            value: Description of value.
        
        """
        self._show_page_breaks = value
        self.viewport().update()
    
    def paintEvent(self, event: Any) -> None:
        """Paint the text, then overlay page break lines."""
        # Let the base class paint the text first
        super().paintEvent(event)
        
        if not self._show_page_breaks:
            return
        
        # Paint page break lines
        from PyQt6.QtGui import QPainter, QPen
        
        painter = QPainter(self.viewport())
        
        # Dashed line style
        pen = QPen(QColor("#94a3b8"))  # Light gray
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setWidth(1)
        painter.setPen(pen)
        
        # Get scroll position
        scroll_y = self.verticalScrollBar().value()
        viewport_height = self.viewport().height()
        
        # Calculate which page breaks are visible
        doc_height = self.document().size().height()
        
        page = 1
        while page * self.page_height < doc_height:
            # Y position of this page break (in document coordinates)
            break_y = page * self.page_height
            
            # Convert to viewport coordinates
            viewport_y = break_y - scroll_y
            
            # Only draw if visible
            if -10 < viewport_y < viewport_height + 10:
                # Draw the line
                painter.drawLine(10, int(viewport_y), self.viewport().width() - 10, int(viewport_y))
                
                # Draw page number label
                painter.drawText(15, int(viewport_y) - 5, f"─ Page {page + 1} ─")
            
            page += 1
        
        painter.end()
    
    def loadResource(self, type_id: int, url: QUrl) -> Any:
        """
        Handle custom resource loading, specifically for docimg:// scheme.
        """
        if url.scheme() == "docimg":
            # Check for mermaid or other named resources
            # Accessing url.path() might return /mermaid/uuid
            if "mermaid" in url.toString():
                 # Default handling should find it in the resource cache
                 return super().loadResource(type_id, url)
            
            try:
                # Extract image ID
                path = url.path().strip('/')
                host = url.host()
                
                image_id = None
                
                # Case 1: docimg:///123 (Triple slash, stored in path)
                if path and path.isdigit():
                    image_id = int(path)
                
                # Case 2: docimg://123 (Double slash, Qt parses 123 as '0.0.0.123' host)
                elif host:
                    # Check for IP address format 
                    parts = host.split('.')
                    if len(parts) == 4 and all(p.isdigit() for p in parts):
                        # Decode IP to Int: a.b.c.d -> (a<<24) + (b<<16) + (c<<8) + d
                        p = [int(part) for part in parts]
                        image_id = (p[0] << 24) + (p[1] << 16) + (p[2] << 8) + p[3]
                    elif host.isdigit():
                        # Direct integer host (unlikely with QUrl but possible)
                        image_id = int(host)
                
                if image_id is None:
                     print(f"Failed to parse image ID from url: {url.toString()}")
                     return super().loadResource(type_id, url)

                # Use external resource provider if available
                # This decouples the editor from the document manager pillar
                if hasattr(self, 'resource_provider') and self.resource_provider:
                     result = self.resource_provider(image_id)
                     if result:
                        data, mime_type = result
                        from PyQt6.QtGui import QImage
                        image = QImage()
                        image.loadFromData(data)
                        return image
                else:
                    # Fallback or error logging if no provider
                    print(f"No resource provider available for docimg://{image_id}")
                    
            except Exception as e:
                print(f"Failed to load image resource {url.toString()}: {e}")
                
        return super().loadResource(type_id, url)

    def insertFromMimeData(self, source: QMimeData) -> None:
        """
        Override paste behavior to protect against freezing.
        """
        # Threshold: 100,000 chars (approx 20-30 pages of text)
        WARN_THRESHOLD = 100000
        
        if source.hasText():
            text = source.text()
            if len(text) > WARN_THRESHOLD:
                # Mars Warning: Chaos detected
                reply = QMessageBox.warning(
                    self, 
                    "Large Paste Detected",
                    f"You are attempting to paste {len(text):,} characters.\n"
                    "This may temporarily freeze the application.\n\n"
                    "Do you wish to proceed?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
        
        super().insertFromMimeData(source)




# Dialog classes have been moved to ui/dialogs/ for modularity:
# - HyperlinkDialog
# - HorizontalRuleDialog  
# - PageSetupDialog
# - SpecialCharactersDialog
# - ExportPdfDialog


class RichTextEditor(QWidget):
    """
    A comprehensive rich text editor widget with a Ribbon interface.
    """
    
    # Signal emitted when text changes
    text_changed = pyqtSignal()
    
    # Signal emitted when [[ is typed
    wiki_link_requested = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None, placeholder_text: str = "Start typing...", show_ui: bool = True) -> None:
        """
          init   logic.
        
        Args:
            parent: Description of parent.
            placeholder_text: Description of placeholder_text.
            show_ui: Description of show_ui.
        
        Returns:
            Result of __init__ operation.
        """
        super().__init__(parent)
        self.virtual_keyboard: VirtualKeyboard | None = None
        
        # Styles Definition
        self.styles = {
            "Normal": {"size": 12, "weight": QFont.Weight.Normal, "family": "Arial"},
            "Title": {"size": 28, "weight": QFont.Weight.Bold, "family": "Arial"},
            "Heading 1": {"size": 24, "weight": QFont.Weight.Bold, "family": "Arial"},
            "Heading 2": {"size": 18, "weight": QFont.Weight.Bold, "family": "Arial"},
            "Heading 3": {"size": 14, "weight": QFont.Weight.Bold, "family": "Arial"},
            "Code": {"size": 10, "weight": QFont.Weight.Normal, "family": "Courier New"},
        }
        
        # Initialize self.editor to None (will be set by _on_active_page_changed)
        self.editor = None
        
        # Initialize features FIRST (sets attributes to None)
        self._init_features()
        
        # Then setup UI (which may call _ensure_features_initialized)
        self._setup_ui(placeholder_text, show_ui)
        
        # Force LTR by default to prevent auto-detection issues
        if self.editor:
            self.editor.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        
    def _setup_ui(self, placeholder_text: str, show_ui: bool) -> None:
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # --- Ribbon (if UI is shown) ---
        if show_ui:
            self.ribbon = RibbonWidget()
            layout.addWidget(self.ribbon)
        
        # --- Text Editor ---
        self.editor = SafeTextEdit(self)
        self.editor.setPlaceholderText(placeholder_text)
        layout.addWidget(self.editor, 1)  # Stretch to fill
        
        # Ensure features initialized
        self._ensure_features_initialized()
        
        # Connect editor signals
        self.editor.textChanged.connect(self._update_word_count)
        self.editor.textChanged.connect(self.text_changed.emit)
        self.editor.textChanged.connect(self._check_wiki_link_trigger)
        self.editor.currentCharFormatChanged.connect(self._update_format_widgets)
        
        # Context menu
        self.editor.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.editor.customContextMenuRequested.connect(self._show_context_menu)
        
        # Create keyboard shortcuts (needed before ribbon init)
        self.action_find = QAction("Find", self)
        self.action_find.setShortcut("Ctrl+F")
        self.action_find.triggered.connect(self._show_search_dialog)
        self.addAction(self.action_find)
        
        self.action_spell_check = QAction("Spelling", self)
        self.action_spell_check.setShortcut("F7")
        self.action_spell_check.triggered.connect(self._show_spell_dialog)
        self.addAction(self.action_spell_check)
        
        if show_ui:
            # --- Status Bar ---
            self.status_bar = QStatusBar()
            self.status_bar.setStyleSheet("""
                QStatusBar {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f8fafc, stop:1 #e2e8f0);
                    border-top: 1px solid #cbd5e1;
                    padding: 2px 8px;
                }
                QStatusBar QLabel {
                    color: #475569;
                    font-size: 9pt;
                }
                QSlider::groove:horizontal {
                    height: 6px;
                    background: #e2e8f0;
                    border-radius: 3px;
                }
                QSlider::handle:horizontal {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff, stop:1 #e2e8f0);
                    border: 1px solid #94a3b8;
                    width: 14px;
                    margin: -4px 0;
                    border-radius: 7px;
                }
                QSlider::handle:horizontal:hover {
                    background: #dbeafe;
                    border-color: #3b82f6;
                }
                QToolButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff, stop:1 #f1f5f9);
                    border: 1px solid #cbd5e1;
                    border-radius: 4px;
                    padding: 3px 8px;
                    color: #475569;
                    font-weight: 500;
                }
                QToolButton:hover {
                    background: #eff6ff;
                    border-color: #93c5fd;
                    color: #1d4ed8;
                }
            """)
            
            # Word count
            self.word_count_label = QLabel("Words: 0")
            self.status_bar.addWidget(self.word_count_label)
            
            # Spacer
            self.status_bar.addWidget(QLabel(""), 1)  # Stretch
            
            # Zoom controls
            zoom_widget = QWidget()
            zoom_layout = QHBoxLayout(zoom_widget)
            zoom_layout.setContentsMargins(0, 0, 0, 0)
            zoom_layout.setSpacing(5)
            
            self.zoom_label = QLabel("100%")
            self.zoom_label.setMinimumWidth(40)
            
            self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
            self.zoom_slider.setRange(25, 300)
            self.zoom_slider.setValue(100)
            self.zoom_slider.setFixedWidth(100)
            self.zoom_slider.valueChanged.connect(self._on_zoom_changed)
            
            btn_zoom_out = QToolButton()
            btn_zoom_out.setText("-")
            btn_zoom_out.clicked.connect(lambda: self.zoom_slider.setValue(max(25, self.zoom_slider.value() - 25)))
            
            btn_zoom_in = QToolButton()
            btn_zoom_in.setText("+")
            btn_zoom_in.clicked.connect(lambda: self.zoom_slider.setValue(min(300, self.zoom_slider.value() + 25)))
            
            btn_zoom_reset = QToolButton()
            btn_zoom_reset.setText("100%")
            btn_zoom_reset.setToolTip("Reset Zoom")
            btn_zoom_reset.clicked.connect(lambda: self.zoom_slider.setValue(100))
            
            zoom_layout.addWidget(btn_zoom_out)
            zoom_layout.addWidget(self.zoom_slider)
            zoom_layout.addWidget(btn_zoom_in)
            zoom_layout.addWidget(self.zoom_label)
            zoom_layout.addWidget(btn_zoom_reset)
            
            self.status_bar.addPermanentWidget(zoom_widget)
            layout.addWidget(self.status_bar)
            
            # Initialize ribbon tabs and groups
            self._init_ribbon()
            
            # Update ribbon state to match current format
            self._update_format_widgets(self.editor.currentCharFormat())
            
            # Initial word count
            self._update_word_count()
    
    
    def _show_search_dialog(self):
        """Placeholder for search feature."""
        if hasattr(self, 'search_feature') and self.search_feature:
            self.search_feature.show_search_dialog()
    
    def _show_spell_dialog(self):
        """Placeholder for spell feature."""
        if hasattr(self, 'spell_feature') and self.spell_feature:
            self.spell_feature.show_dialog()
    

    def insertFromMimeData(self, source: QMimeData) -> None:
        """
        Override paste behavior to protect against 'Paste Attacks' (Mars Seal).
        Warns user if pasting massive content that could freeze the UI.
        """
        # Threshold: 100,000 chars (approx 20-30 pages of text)
        WARN_THRESHOLD = 100000
        
        if source.hasText():
            text = source.text()
            if len(text) > WARN_THRESHOLD:
                # Mars Warning: Chaos detected
                reply = QMessageBox.warning(
                    self, 
                    "Large Paste Detected",
                    f"You are attempting to paste {len(text):,} characters.\n"
                    "This may temporarily freeze the application.\n\n"
                    "Do you wish to proceed?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
        
        # Standard Qt behavior if safe or approved
        super().insertFromMimeData(source) # type: ignore

    def _check_wiki_link_trigger(self) -> None:
        """Check if the user just typed '[['."""
        cursor = self.editor.textCursor()
        position = cursor.position()
        
        if position < 2:
            return
            
        cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, 2)
        text = cursor.selectedText()
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, 2)
        
        if text == "[[":
            self.wiki_link_requested.emit()

    def _show_context_menu(self, pos: QPoint) -> None:
        """Show context menu for the editor."""
        if not self.editor:
            return
        
        # Ensure all features are initialized
        self._ensure_features_initialized()
        
        # If there's no selection, move cursor to click position
        current_cursor = self.editor.textCursor()
        if not current_cursor.hasSelection():
            cursor = self.editor.cursorForPosition(pos)
            self.editor.setTextCursor(cursor)
        
        menu = self.editor.createStandardContextMenu()
        
        if menu is not None:
            # Spell check suggestions first (at top of menu)
            if hasattr(self, 'spell_feature') and self.spell_feature:
                self.spell_feature.extend_context_menu(menu, pos)
            if hasattr(self, 'table_feature') and self.table_feature:
                self.table_feature.extend_context_menu(menu)
            if hasattr(self, 'image_feature') and self.image_feature:
                self.image_feature.extend_context_menu(menu)
            if hasattr(self, 'etymology_feature') and self.etymology_feature:
                self.etymology_feature.extend_context_menu(menu)
            if hasattr(self, 'math_feature') and self.math_feature:
                self.math_feature.extend_context_menu(menu)
            if hasattr(self, 'mermaid_feature') and self.mermaid_feature:
                self.mermaid_feature.extend_context_menu(menu)
            menu.exec(self.editor.mapToGlobal(pos))

    def _init_features(self) -> None:
        """Initialize features that don't require the Ribbon UI."""
        # Features will be initialized lazily when first accessed
        # since editor is now dynamic (changes per page)
        
        # Set all features to None initially
        self.etymology_feature = None
        self.list_feature = None
        self.table_feature = None
        self.image_feature = None
        self.search_feature = None
        self.spell_feature = None
        self.math_feature = None
        self.mermaid_feature = None
    
    def _ensure_features_initialized(self):
        """Lazy initialization of editor-dependent features."""
        if not self.editor:
            return
        
        if not self.etymology_feature:
            self.etymology_feature = EtymologyFeature(self)
        
        if not self.list_feature:
            self.list_feature = ListFeature(self.editor, self)
        
        if not self.table_feature:
            self.table_feature = TableFeature(self.editor, self)
        
        if not self.image_feature:
            self.image_feature = ImageFeature(self.editor, self)
        
        if not self.search_feature:
            self.search_feature = SearchReplaceFeature(self.editor, self)
        
        if not self.spell_feature:
            self.spell_feature = SpellFeature(self)
        
        if not self.math_feature:
            self.math_feature = MathFeature(self.editor, self)
        
        if not self.mermaid_feature:
            self.mermaid_feature = MermaidFeature(self.editor, self)

    def show_search(self) -> None:
        """Public API for Global Ribbon."""
        # Initialize if strictly needed or assume _init_features did it
        if not hasattr(self, 'search_feature'):
             self.search_feature = SearchReplaceFeature(self.editor, self)
        self.search_feature.show_search_dialog()

    def toggle_list(self, style: QTextListFormat.Style) -> None:
        """Public API for Global Ribbon."""
        if hasattr(self, 'list_feature'):
            self.list_feature.toggle_list(style)

    def set_alignment(self, align: Qt.AlignmentFlag) -> None:
        """Public API for Global Ribbon."""
        self.editor.setAlignment(align)

    def insert_table(self, rows: int = 3, cols: int = 3) -> None:
        """Public API for Global Ribbon."""
        if hasattr(self, 'table_feature'):
             self.table_feature.insert_table(rows, cols)

    def insert_image(self) -> None:
        """Public API for Global Ribbon."""
        if hasattr(self, 'image_feature'):
            self.image_feature.insert_image()

    def set_highlight(self, color: QColor) -> None:
        """Public API for Global Ribbon."""
        fmt = QTextCharFormat()
        fmt.setBackground(color)
        self.editor.mergeCurrentCharFormat(fmt)
    
    def clear_formatting(self) -> None:
        """Public API"""
        self._clear_formatting()

    def toggle_strikethrough(self) -> None:
        """
        Toggle strikethrough logic.
        
        Returns:
            Result of toggle_strikethrough operation.
        """
        self._toggle_strikethrough()

    def toggle_subscript(self) -> None:
        """
        Toggle subscript logic.
        
        Returns:
            Result of toggle_subscript operation.
        """
        self._toggle_subscript()

    def toggle_superscript(self) -> None:
        """
        Toggle superscript logic.
        
        Returns:
            Result of toggle_superscript operation.
        """
        self._toggle_superscript()

    def _init_ribbon(self) -> None:
        """Populate the ribbon with tabs and groups."""
        
        # === Define Core Actions First ===
        self.action_undo = QAction("Undo", self)
        self.action_undo.setShortcut("Ctrl+Z")
        self.action_undo.setIcon(qta.icon("fa5s.undo", color="#1e293b"))
        self.action_undo.triggered.connect(self.editor.undo)
        
        self.action_redo = QAction("Redo", self)
        self.action_redo.setShortcut("Ctrl+Y")
        self.action_redo.setIcon(qta.icon("fa5s.redo", color="#1e293b"))
        self.action_redo.triggered.connect(self.editor.redo)

        # === Application Button (File) ===
        file_menu = self.ribbon.add_file_menu()
        file_menu.addAction("New", self.new_document)
        file_menu.addAction("Open...", self.open_document)
        file_menu.addAction("Save As...", self.save_document)
        
        # === Quick Access Toolbar ===
        self.ribbon.add_quick_access_button(self.action_undo)
        self.ribbon.add_quick_access_button(self.action_redo)

        # =========================================================================
        # TAB: HOME
        # =========================================================================
        tab_home = self.ribbon.add_ribbon_tab("Home")
        
        # --- Group: Clipboard ---
        grp_clip = tab_home.add_group("Clipboard")
        
        # Paste
        action_paste = QAction("Paste", self)
        action_paste.setShortcut("Ctrl+V")
        action_paste.setIcon(qta.icon("fa5s.paste", color="#1e293b"))
        action_paste.triggered.connect(self.editor.paste)
        grp_clip.add_action(action_paste, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # Cut (small)
        action_cut = QAction("Cut", self)
        action_cut.setShortcut("Ctrl+X")
        action_cut.setIcon(qta.icon("fa5s.cut", color="#1e293b"))
        action_cut.triggered.connect(self.editor.cut)
        grp_clip.add_action(action_cut)
        
        # Copy (small)
        action_copy = QAction("Copy", self)
        action_copy.setShortcut("Ctrl+C")
        action_copy.setIcon(qta.icon("fa5s.copy", color="#1e293b"))
        action_copy.triggered.connect(self.editor.copy)
        grp_clip.add_action(action_copy)
        
        # --- Group: Typeface ---
        grp_face = tab_home.add_group("Typeface")
        
        self.font_combo = QFontComboBox()
        self.font_combo.setMaximumWidth(150)
        self.font_combo.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.font_combo.currentFontChanged.connect(self.editor.setCurrentFont)
        grp_face.add_widget(self.font_combo)
        
        self.size_combo = QComboBox()
        self.size_combo.setEditable(True)
        self.size_combo.setMaximumWidth(60)
        self.size_combo.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]
        self.size_combo.addItems([str(s) for s in sizes])
        self.size_combo.setCurrentText("12")
        self.size_combo.textActivated.connect(self._set_font_size)
        grp_face.add_widget(self.size_combo)

        # --- Group: Basic Formatting ---
        # --- Group: Basic Formatting ---
        grp_basic = tab_home.add_group("Basic")
        
        # Helper to create buttons (using add_action directly where possible for layout)
        # Bold
        self.btn_bold = QToolButton()
        self.btn_bold.setIcon(qta.icon("fa5s.bold", color="#1e293b"))
        self.btn_bold.setToolTip("Bold (Ctrl+B)")
        self.btn_bold.setCheckable(True)
        self.btn_bold.setShortcut("Ctrl+B")
        self.btn_bold.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_bold.setStyleSheet("""
            QToolButton:checked {
                background-color: #bfdbfe;
                border: 1px solid #3b82f6;
            }
        """)
        self.btn_bold.clicked.connect(self._toggle_bold)
        grp_basic.add_widget(self.btn_bold)
        
        # Italic
        self.btn_italic = QToolButton()
        self.btn_italic.setIcon(qta.icon("fa5s.italic", color="#1e293b"))
        self.btn_italic.setToolTip("Italic (Ctrl+I)")
        self.btn_italic.setCheckable(True)
        self.btn_italic.setShortcut("Ctrl+I")
        self.btn_italic.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_italic.setStyleSheet("""
            QToolButton:checked {
                background-color: #bfdbfe;
                border: 1px solid #3b82f6;
            }
        """)
        self.btn_italic.clicked.connect(lambda checked: (self.editor.setFontItalic(checked), self.editor.setFocus()))
        grp_basic.add_widget(self.btn_italic)

        # Underline
        self.btn_underline = QToolButton()
        self.btn_underline.setIcon(qta.icon("fa5s.underline", color="#1e293b"))
        self.btn_underline.setToolTip("Underline (Ctrl+U)")
        self.btn_underline.setCheckable(True)
        self.btn_underline.setShortcut("Ctrl+U")
        self.btn_underline.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_underline.setStyleSheet("""
            QToolButton:checked {
                background-color: #bfdbfe;
                border: 1px solid #3b82f6;
            }
        """)
        self.btn_underline.clicked.connect(lambda checked: (self.editor.setFontUnderline(checked), self.editor.setFocus()))
        grp_basic.add_widget(self.btn_underline)
        
        # --- Group: Advanced Formatting ---
        grp_adv = tab_home.add_group("Advanced")

        # Strikethrough
        self.btn_strike = QToolButton()
        self.btn_strike.setCheckable(True)
        self.btn_strike.setToolTip("Strikethrough")
        self.btn_strike.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_strike.setStyleSheet("""
            QToolButton:checked {
                background-color: #bfdbfe;
                border: 1px solid #3b82f6;
            }
        """)
        self.btn_strike.clicked.connect(self._toggle_strikethrough)
        self.btn_strike.setIcon(qta.icon("fa5s.strikethrough", color="#1e293b"))
        grp_adv.add_widget(self.btn_strike)

        # Subscript
        self.action_sub = QAction("", self)
        self.action_sub.setCheckable(True)
        self.action_sub.setToolTip("Subscript")
        self.action_sub.triggered.connect(self._toggle_subscript)
        self.action_sub.setIcon(qta.icon("fa5s.subscript", color="#1e293b"))
        # Note: QAction styling handled by ribbon widget
        grp_adv.add_action(self.action_sub, Qt.ToolButtonStyle.ToolButtonIconOnly)

        # Superscript
        self.action_super = QAction("", self)
        self.action_super.setCheckable(True)
        self.action_super.setToolTip("Superscript")
        self.action_super.triggered.connect(self._toggle_superscript)
        self.action_super.setIcon(qta.icon("fa5s.superscript", color="#1e293b"))
        # Note: QAction styling handled by ribbon widget
        grp_adv.add_action(self.action_super, Qt.ToolButtonStyle.ToolButtonIconOnly)
        
        # Clear Formatting
        self.action_clear = QAction("", self)
        self.action_clear.setToolTip("Clear Formatting")
        self.action_clear.triggered.connect(self._clear_formatting)
        self.action_clear.setIcon(qta.icon("fa5s.eraser", color="#d94848")) # Red eraser
        grp_adv.add_action(self.action_clear, Qt.ToolButtonStyle.ToolButtonIconOnly)
        
        # --- Group: Colors ---
        grp_color = tab_home.add_group("Colors")
        
        # Colors
        btn_color = QToolButton()
        btn_color.setIcon(qta.icon("fa5s.palette", color="#2563eb")) 
        btn_color.setText("Color")
        btn_color.setToolTip("Text Color")
        btn_color.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_color.clicked.connect(self._pick_color)
        grp_color.add_widget(btn_color)
        
        btn_highlight = QToolButton()
        btn_highlight.setIcon(qta.icon("fa5s.highlighter", color="#ca8a04"))
        btn_highlight.setText("High")
        btn_highlight.setToolTip("Highlight")
        btn_highlight.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_highlight.clicked.connect(self._pick_highlight)
        grp_color.add_widget(btn_highlight)
        
        btn_clear_bg = QToolButton()
        btn_clear_bg.setIcon(qta.icon("fa5s.ban", color="#94a3b8"))
        btn_clear_bg.setText("X")
        btn_clear_bg.setToolTip("No Highlight")
        btn_clear_bg.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_clear_bg.clicked.connect(self._clear_highlight)
        grp_color.add_widget(btn_clear_bg)
        
        # --- Group: Paragraph ---
        grp_para = tab_home.add_group("Paragraph")
        
        # Alignment
        align_group = QActionGroup(self)
        
        self.action_align_left = QAction("", self)
        self.action_align_left.setToolTip("Align Left")
        self.action_align_left.setCheckable(True)
        self.action_align_left.setIcon(qta.icon("fa5s.align-left", color="#1e293b"))
        self.action_align_left.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignLeft))
        align_group.addAction(self.action_align_left)
        grp_para.add_action(self.action_align_left, Qt.ToolButtonStyle.ToolButtonIconOnly)

        self.action_align_center = QAction("", self)
        self.action_align_center.setToolTip("Align Center")
        self.action_align_center.setCheckable(True)
        self.action_align_center.setIcon(qta.icon("fa5s.align-center", color="#1e293b"))
        self.action_align_center.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignCenter))
        align_group.addAction(self.action_align_center)
        grp_para.add_action(self.action_align_center, Qt.ToolButtonStyle.ToolButtonIconOnly)
        
        self.action_align_right = QAction("", self)
        self.action_align_right.setToolTip("Align Right")
        self.action_align_right.setCheckable(True)
        self.action_align_right.setIcon(qta.icon("fa5s.align-right", color="#1e293b"))
        self.action_align_right.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignRight))
        align_group.addAction(self.action_align_right)
        grp_para.add_action(self.action_align_right, Qt.ToolButtonStyle.ToolButtonIconOnly)
        
        self.action_align_justify = QAction("", self)
        self.action_align_justify.setToolTip("Justify")
        self.action_align_justify.setCheckable(True)
        self.action_align_justify.setIcon(qta.icon("fa5s.align-justify", color="#1e293b"))
        self.action_align_justify.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignJustify))
        align_group.addAction(self.action_align_justify)
        grp_para.add_action(self.action_align_justify, Qt.ToolButtonStyle.ToolButtonIconOnly)
        
        # --- Group: Lists ---
        grp_lists = tab_home.add_group("Lists")
        
        # Bullet List Button with Dropdown
        from .list_features import LIST_STYLES, BULLET_STYLES, NUMBER_STYLES
        
        self.bullet_btn = QToolButton()
        self.bullet_btn.setIcon(qta.icon("fa5s.list-ul", color="#1e293b"))
        self.bullet_btn.setToolTip("Bullet List")
        self.bullet_btn.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self.bullet_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.bullet_btn.clicked.connect(lambda: self._toggle_list(QTextListFormat.Style.ListDisc))
        
        bullet_menu = QMenu(self)
        for name in BULLET_STYLES:
            act = bullet_menu.addAction(name)
            style = LIST_STYLES[name]
            act.triggered.connect(lambda checked, s=style: self._toggle_list(s))
        self.bullet_btn.setMenu(bullet_menu)
        grp_lists.add_widget(self.bullet_btn)
        
        # Number List Button with Dropdown
        self.number_btn = QToolButton()
        self.number_btn.setIcon(qta.icon("fa5s.list-ol", color="#1e293b"))
        self.number_btn.setToolTip("Numbered List")
        self.number_btn.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self.number_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.number_btn.clicked.connect(lambda: self._toggle_list(QTextListFormat.Style.ListDecimal))
        
        number_menu = QMenu(self)
        for name in NUMBER_STYLES:
            act = number_menu.addAction(name)
            style = LIST_STYLES[name]
            act.triggered.connect(lambda checked, s=style: self._toggle_list(s))
        number_menu.addSeparator()
        act_start = number_menu.addAction("Set Start Number...")
        act_start.triggered.connect(lambda: self.list_feature.show_start_number_dialog())
        self.number_btn.setMenu(number_menu)
        grp_lists.add_widget(self.number_btn)
        
        # Checklist Button
        act_checklist = QAction(qta.icon("fa5s.check-square", color="#1e293b"), "Checklist", self)
        act_checklist.setToolTip("Toggle Checklist")
        act_checklist.triggered.connect(lambda: self.list_feature.toggle_checklist())
        grp_lists.add_action(act_checklist, Qt.ToolButtonStyle.ToolButtonIconOnly)
        
        # Indent/Outdent
        act_indent = QAction(qta.icon("fa5s.indent", color="#1e293b"), "Increase Indent", self)
        act_indent.triggered.connect(lambda: self.list_feature.indent())
        grp_lists.add_action(act_indent, Qt.ToolButtonStyle.ToolButtonIconOnly)
        
        act_outdent = QAction(qta.icon("fa5s.outdent", color="#1e293b"), "Decrease Indent", self)
        act_outdent.triggered.connect(lambda: self.list_feature.outdent())
        grp_lists.add_action(act_outdent, Qt.ToolButtonStyle.ToolButtonIconOnly)
        
        # Remove List
        act_remove_list = QAction(qta.icon("fa5s.times-circle", color="#dc2626"), "Remove List", self)
        act_remove_list.triggered.connect(lambda: self.list_feature.remove_list())
        grp_lists.add_action(act_remove_list, Qt.ToolButtonStyle.ToolButtonIconOnly)
        
        # --- Group: Styles (Gallery) ---
        grp_style = tab_home.add_group("Styles")
        self.style_gallery = grp_style.add_gallery(min_width=200)
        
        for name in self.styles.keys():
            # Select specific icons for different styles
            if name == "Title":
                icon = qta.icon("fa5s.heading", color="#1e293b", scale_factor=1.2)
            elif name.startswith("Heading"):
                # Use hashtag as a distinct symbol for headers (markdown style)
                icon = qta.icon("fa5s.hashtag", color="#2563eb") # Blue for headers
            elif name == "Code":
                icon = qta.icon("fa5s.code", color="#d94848") # Red for code
            else:
                icon = qta.icon("fa5s.paragraph", color="#64748b")
                
            self.style_gallery.add_item(name, icon, lambda checked, s=name: self._apply_style(s))
            
        # --- Group: Editing ---
        grp_edit = tab_home.add_group("Search")
        
        # Find
        self.action_find.setIcon(qta.icon("fa5s.search", color="#1e293b"))
        grp_edit.add_action(self.action_find, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # Replace
        action_replace = QAction("Replace", self)
        action_replace.triggered.connect(lambda: self.search_feature.show_search_dialog())
        action_replace.setIcon(qta.icon("fa5s.sync-alt", color="#1e293b"))
        grp_edit.add_action(action_replace, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # Select All
        action_select_all = QAction("Select All", self)
        action_select_all.setShortcut("Ctrl+A")
        action_select_all.triggered.connect(self.editor.selectAll)
        action_select_all.setIcon(qta.icon("fa5s.mouse-pointer", color="#1e293b"))
        grp_edit.add_action(action_select_all, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        # =========================================================================
        # TAB: INSERT
        # =========================================================================
        # === TAB: INSERT ===
        tab_insert = self.ribbon.add_ribbon_tab("Insert")
        
        # Group: Pages
        grp_pages = tab_insert.add_group("Pages")
        action_break = QAction("Page Break", self)
        action_break.setToolTip("Insert Page Break (Ctrl+Enter)")
        action_break.setShortcut("Ctrl+Return")
        action_break.triggered.connect(self._insert_page_break)
        action_break.setIcon(qta.icon("fa5s.unlink", color="#1e293b"))
        grp_pages.add_action(action_break, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # Group: Tables
        grp_tables = tab_insert.add_group("Tables")
        self.table_feature = TableFeature(self.editor, self)
        grp_tables.add_widget(self.table_feature.create_toolbar_button())
        
        # Group: Illustrations
        grp_illus = tab_insert.add_group("Illustrations")
        self.image_feature = ImageFeature(self.editor, self)
        # Assuming image_feature checks for icon internally, if not we rely on text
        grp_illus.add_action(self.image_feature.create_toolbar_action(), Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # Shapes
        self.shape_feature = ShapeFeature(self)
        grp_illus.add_widget(self.shape_feature.create_toolbar_button())
        
        # Group: Symbols
        grp_sym = tab_insert.add_group("Symbols")
        
        action_kb = QAction("Keyboard", self)
        action_kb.setToolTip("Open Virtual Keyboard")
        action_kb.triggered.connect(self._show_virtual_keyboard)
        action_kb.setIcon(qta.icon("fa5s.keyboard", color="#1e293b"))
        grp_sym.add_action(action_kb, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # Group: Math
        grp_math = tab_insert.add_group("Math")
        if hasattr(self, 'math_feature'):
            grp_math.add_action(self.math_feature.action_insert_math, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            grp_math.add_action(self.math_feature.action_render_doc, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        # Group: Diagrams
        grp_diag = tab_insert.add_group("Diagrams")
        if hasattr(self, 'mermaid_feature'):
            grp_diag.add_action(self.mermaid_feature.action_insert_mermaid, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            grp_diag.add_action(self.mermaid_feature.action_render_doc, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        # Group: Links
        grp_links = tab_insert.add_group("Links")
        
        action_hyperlink = QAction("Hyperlink", self)
        action_hyperlink.setToolTip("Insert Hyperlink (Ctrl+K)")
        action_hyperlink.setShortcut("Ctrl+K")
        action_hyperlink.triggered.connect(self._insert_hyperlink)
        action_hyperlink.setIcon(qta.icon("fa5s.link", color="#1e293b"))
        grp_links.add_action(action_hyperlink, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addAction(action_hyperlink)
        
        # Group: Elements
        grp_elements = tab_insert.add_group("Elements")
        
        action_hr = QAction("Horiz. Rule", self)
        action_hr.setToolTip("Insert Horizontal Rule")
        action_hr.triggered.connect(self._insert_horizontal_rule)
        action_hr.setIcon(qta.icon("fa5s.minus", color="#1e293b"))
        grp_elements.add_action(action_hr, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        action_special = QAction("Symbol", self)
        action_special.setToolTip("Insert Special Characters")
        action_special.triggered.connect(self._show_special_characters)
        action_special.setIcon(qta.icon("fa5s.copyright", color="#1e293b"))
        grp_elements.add_action(action_special, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # === TAB: PAGE LAYOUT ===
        tab_page = self.ribbon.add_ribbon_tab("Page Layout")
        
        # Group: Page Setup
        grp_page = tab_page.add_group("Page Setup")
        
        action_page_setup = QAction("Page Setup", self)
        action_page_setup.setToolTip("Set page size, orientation, margins")
        action_page_setup.triggered.connect(self._show_page_setup)
        action_page_setup.setIcon(qta.icon("fa5s.cog", color="#1e293b"))
        grp_page.add_action(action_page_setup, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # Group: Page View
        grp_view = tab_page.add_group("View")
        
        self.action_page_breaks = QAction("Page Breaks", self)
        self.action_page_breaks.setToolTip("Show/Hide Page Break Lines")
        self.action_page_breaks.setIcon(qta.icon("fa5s.grip-lines", color="#1e293b"))
        self.action_page_breaks.setCheckable(True)
        self.action_page_breaks.setChecked(True)  # Default: show page breaks
        self.action_page_breaks.triggered.connect(self._toggle_page_breaks)
        grp_view.add_action(self.action_page_breaks, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        # =========================================================================
        # TAB: REFERENCE
        # =========================================================================
        tab_ref = self.ribbon.add_ribbon_tab("Reference")
        
        # Group: Language
        grp_lang = tab_ref.add_group("Language")
        
        # Use existing etymology_feature instance (created in _setup_ui)
        grp_lang.add_action(self.etymology_feature.create_action(self), Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        # Group: Proofing
        grp_proof = tab_ref.add_group("Proofing")
        
        # Spell Check button
        grp_proof.add_action(self.spell_feature.create_ribbon_action(self), Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # Spell Check toggle
        grp_proof.add_action(self.spell_feature.create_toggle_action(self), Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        # =========================================================================
        # CONTEXT CATEGORIES
        # =========================================================================
        
        # === CONTEXT CATEGORY: Table Tools ===
        self.ctx_table = self.ribbon.add_context_category("Table Tools", Qt.GlobalColor.darkYellow)
        
        # Layout Group - Insert/Delete
        grp_tbl_layout = self.ctx_table.add_group("Layout")
        
        act_ins_row = QAction(qta.icon("fa5s.plus", color="#1e293b"), "Insert Row", self)
        act_ins_row.triggered.connect(lambda: self.table_feature._insert_row_below() if hasattr(self, 'table_feature') else None)
        grp_tbl_layout.add_action(act_ins_row, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_ins_col = QAction(qta.icon("fa5s.plus", color="#1e293b"), "Insert Col", self)
        act_ins_col.triggered.connect(lambda: self.table_feature._insert_col_right() if hasattr(self, 'table_feature') else None)
        grp_tbl_layout.add_action(act_ins_col, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        grp_tbl_layout.add_separator()
        
        act_del_row = QAction(qta.icon("fa5s.minus", color="#dc2626"), "Delete Row", self)
        act_del_row.triggered.connect(lambda: self.table_feature._delete_row() if hasattr(self, 'table_feature') else None)
        grp_tbl_layout.add_action(act_del_row, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_del_col = QAction(qta.icon("fa5s.minus", color="#dc2626"), "Delete Col", self)
        act_del_col.triggered.connect(lambda: self.table_feature._delete_col() if hasattr(self, 'table_feature') else None)
        grp_tbl_layout.add_action(act_del_col, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_del_table = QAction(qta.icon("fa5s.trash", color="#dc2626"), "Delete Table", self)
        act_del_table.triggered.connect(lambda: self.table_feature._delete_table() if hasattr(self, 'table_feature') else None)
        grp_tbl_layout.add_action(act_del_table, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        # Merge/Split Group
        grp_tbl_merge = self.ctx_table.add_group("Merge")
        
        act_merge = QAction(qta.icon("fa5s.object-group", color="#1e293b"), "Merge Cells", self)
        act_merge.triggered.connect(lambda: self.table_feature._merge_cells() if hasattr(self, 'table_feature') else None)
        grp_tbl_merge.add_action(act_merge, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_split = QAction(qta.icon("fa5s.object-ungroup", color="#1e293b"), "Split Cells", self)
        act_split.triggered.connect(lambda: self.table_feature._split_cells() if hasattr(self, 'table_feature') else None)
        grp_tbl_merge.add_action(act_split, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_distribute = QAction(qta.icon("fa5s.arrows-alt-h", color="#1e293b"), "Distribute", self)
        act_distribute.triggered.connect(lambda: self.table_feature._distribute_columns() if hasattr(self, 'table_feature') else None)
        grp_tbl_merge.add_action(act_distribute, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        # Style Group
        grp_tbl_style = self.ctx_table.add_group("Style")
        
        act_cell_bg = QAction(qta.icon("fa5s.fill-drip", color="#1e293b"), "Cell Color", self)
        act_cell_bg.triggered.connect(lambda: self.table_feature._set_cell_background() if hasattr(self, 'table_feature') else None)
        grp_tbl_style.add_action(act_cell_bg, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_cell_border = QAction(qta.icon("fa5s.border-style", color="#1e293b"), "Borders", self)
        act_cell_border.triggered.connect(lambda: self.table_feature._edit_cell_borders() if hasattr(self, 'table_feature') else None)
        grp_tbl_style.add_action(act_cell_border, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_cell_props = QAction(qta.icon("fa5s.sliders-h", color="#1e293b"), "Cell Props", self)
        act_cell_props.triggered.connect(lambda: self.table_feature._edit_cell_properties() if hasattr(self, 'table_feature') else None)
        grp_tbl_style.add_action(act_cell_props, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_table_props = QAction(qta.icon("fa5s.cog", color="#1e293b"), "Table Props", self)
        act_table_props.triggered.connect(lambda: self.table_feature._edit_table_properties() if hasattr(self, 'table_feature') else None)
        grp_tbl_style.add_action(act_table_props, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        # === CONTEXT CATEGORY: Image Tools ===
        self.ctx_image = self.ribbon.add_context_category("Image Tools", Qt.GlobalColor.magenta)
        
        # Adjust Group - Size, Crop
        grp_img_adj = self.ctx_image.add_group("Adjust")
        
        act_props = QAction(qta.icon("fa5s.expand-alt", color="#1e293b"), "Size", self)
        act_props.triggered.connect(lambda: self._edit_image_size())
        grp_img_adj.add_action(act_props, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_crop = QAction(qta.icon("fa5s.crop", color="#1e293b"), "Crop", self)
        act_crop.triggered.connect(lambda: self._crop_image())
        grp_img_adj.add_action(act_crop, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        # Transform Group
        grp_img_transform = self.ctx_image.add_group("Transform")
        
        act_align_left = QAction(qta.icon("fa5s.align-left", color="#1e293b"), "Left", self)
        act_align_left.triggered.connect(lambda: self._align_image(Qt.AlignmentFlag.AlignLeft))
        grp_img_transform.add_action(act_align_left, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_align_center = QAction(qta.icon("fa5s.align-center", color="#1e293b"), "Center", self)
        act_align_center.triggered.connect(lambda: self._align_image(Qt.AlignmentFlag.AlignHCenter))
        grp_img_transform.add_action(act_align_center, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_align_right = QAction(qta.icon("fa5s.align-right", color="#1e293b"), "Right", self)
        act_align_right.triggered.connect(lambda: self._align_image(Qt.AlignmentFlag.AlignRight))
        grp_img_transform.add_action(act_align_right, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        # Manage Group
        grp_img_manage = self.ctx_image.add_group("Manage")
        
        act_replace = QAction(qta.icon("fa5s.exchange-alt", color="#1e293b"), "Replace", self)
        act_replace.triggered.connect(lambda: self._replace_image())
        grp_img_manage.add_action(act_replace, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_delete = QAction(qta.icon("fa5s.trash", color="#dc2626"), "Delete", self)
        act_delete.triggered.connect(lambda: self._delete_selected_image())
        grp_img_manage.add_action(act_delete, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        # Color Effects Group
        grp_img_color = self.ctx_image.add_group("Color")
        
        act_grayscale = QAction(qta.icon("fa5s.adjust", color="#1e293b"), "Grayscale", self)
        act_grayscale.triggered.connect(lambda: self._apply_image_filter("Grayscale"))
        grp_img_color.add_action(act_grayscale, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_sepia = QAction(qta.icon("fa5s.sun", color="#b45309"), "Sepia", self)
        act_sepia.triggered.connect(lambda: self._apply_image_filter("Sepia"))
        grp_img_color.add_action(act_sepia, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_warm = QAction(qta.icon("fa5s.fire", color="#f97316"), "Warm", self)
        act_warm.triggered.connect(lambda: self._apply_image_filter("Warm"))
        grp_img_color.add_action(act_warm, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_cool = QAction(qta.icon("fa5s.snowflake", color="#0ea5e9"), "Cool", self)
        act_cool.triggered.connect(lambda: self._apply_image_filter("Cool"))
        grp_img_color.add_action(act_cool, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_vintage = QAction(qta.icon("fa5s.film", color="#78716c"), "Vintage", self)
        act_vintage.triggered.connect(lambda: self._apply_image_filter("Vintage"))
        grp_img_color.add_action(act_vintage, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_invert = QAction(qta.icon("fa5s.exchange-alt", color="#1e293b"), "Invert", self)
        act_invert.triggered.connect(lambda: self._apply_image_filter("Invert"))
        grp_img_color.add_action(act_invert, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        # Artistic Effects Group
        grp_img_art = self.ctx_image.add_group("Artistic")
        
        act_blur = QAction(qta.icon("fa5s.water", color="#1e293b"), "Blur", self)
        act_blur.triggered.connect(lambda: self._apply_image_filter("Blur"))
        grp_img_art.add_action(act_blur, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_sharpen = QAction(qta.icon("fa5s.search-plus", color="#1e293b"), "Sharpen", self)
        act_sharpen.triggered.connect(lambda: self._apply_image_filter("Sharpen"))
        grp_img_art.add_action(act_sharpen, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_emboss = QAction(qta.icon("fa5s.stamp", color="#1e293b"), "Emboss", self)
        act_emboss.triggered.connect(lambda: self._apply_image_filter("Emboss"))
        grp_img_art.add_action(act_emboss, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_edge = QAction(qta.icon("fa5s.border-style", color="#1e293b"), "Edges", self)
        act_edge.triggered.connect(lambda: self._apply_image_filter("Find Edges"))
        grp_img_art.add_action(act_edge, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_auto = QAction(qta.icon("fa5s.magic", color="#1e293b"), "Auto", self)
        act_auto.triggered.connect(lambda: self._apply_image_filter("Auto Contrast"))
        grp_img_art.add_action(act_auto, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        # Rotate Group
        grp_img_rotate = self.ctx_image.add_group("Rotate")
        
        act_rot_left = QAction(qta.icon("fa5s.undo", color="#1e293b"), "↶ 90°", self)
        act_rot_left.triggered.connect(lambda: self._rotate_image(-90))
        grp_img_rotate.add_action(act_rot_left, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_rot_right = QAction(qta.icon("fa5s.redo", color="#1e293b"), "↷ 90°", self)
        act_rot_right.triggered.connect(lambda: self._rotate_image(90))
        grp_img_rotate.add_action(act_rot_right, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        # Connect cursor/selection change to context switches
        self.editor.cursorPositionChanged.connect(self._update_context_tabs)
        
    def _update_context_tabs(self) -> None:
        """Show/Hide context tabs based on cursor position."""
        cursor = self.editor.textCursor()
        
        # Check Table
        if cursor.currentTable():
            self.ribbon.show_context_category(self.ctx_table)
        else:
            self.ribbon.hide_context_category(self.ctx_table)
            
        # Check Image (naive check, usually relies on format)
        img_format = cursor.charFormat().toImageFormat()
        if img_format.isValid():
            self.ribbon.show_context_category(self.ctx_image)
        else:
            self.ribbon.hide_context_category(self.ctx_image)

    def _get_image_cursor(self) -> QTextCursor:
        """Get a cursor positioned to select the current image, or None."""
        from PyQt6.QtGui import QTextCursor
        cursor = self.editor.textCursor()
        
        # Check if cursor is on or near an image
        fmt_before = cursor.charFormat()
        if fmt_before.isImageFormat():
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor)
            return cursor
            
        cursor_after = QTextCursor(cursor)
        cursor_after.movePosition(QTextCursor.MoveOperation.Right)
        fmt_after = cursor_after.charFormat()
        if fmt_after.isImageFormat():
            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor)
            return cursor
            
        return None

    def _edit_image_size(self) -> None:
        """Open a dialog to resize the selected image."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QSpinBox, QDialogButtonBox, QCheckBox
        from PyQt6.QtGui import QTextImageFormat
        
        cursor = self.editor.textCursor()
        
        # Find the image format
        fmt = cursor.charFormat()
        if not fmt.isImageFormat():
            # Try character after
            test_cursor = QTextCursor(cursor)
            test_cursor.movePosition(QTextCursor.MoveOperation.Right)
            fmt = test_cursor.charFormat()
            if not fmt.isImageFormat():
                return
        
        img_fmt = fmt.toImageFormat()
        current_w = int(img_fmt.width()) if img_fmt.width() > 0 else 100
        current_h = int(img_fmt.height()) if img_fmt.height() > 0 else 100
        
        # Create resize dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Image Size")
        dialog.setMinimumWidth(250)
        
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        
        width_spin = QSpinBox()
        width_spin.setRange(10, 4000)
        width_spin.setValue(current_w)
        width_spin.setSuffix(" px")
        form.addRow("Width:", width_spin)
        
        height_spin = QSpinBox()
        height_spin.setRange(10, 4000)
        height_spin.setValue(current_h)
        height_spin.setSuffix(" px")
        form.addRow("Height:", height_spin)
        
        lock_aspect = QCheckBox("Lock aspect ratio")
        lock_aspect.setChecked(True)
        form.addRow(lock_aspect)
        
        aspect_ratio = current_w / current_h if current_h > 0 else 1.0
        
        def on_width_changed(val):
            """
            Handle width changed logic.
            
            Args:
                val: Description of val.
            
            """
            if lock_aspect.isChecked():
                height_spin.blockSignals(True)
                height_spin.setValue(int(val / aspect_ratio))
                height_spin.blockSignals(False)
        
        def on_height_changed(val):
            """
            Handle height changed logic.
            
            Args:
                val: Description of val.
            
            """
            if lock_aspect.isChecked():
                width_spin.blockSignals(True)
                width_spin.setValue(int(val * aspect_ratio))
                width_spin.blockSignals(False)
        
        width_spin.valueChanged.connect(on_width_changed)
        height_spin.valueChanged.connect(on_height_changed)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_w = width_spin.value()
            new_h = height_spin.value()
            
            # Apply new size - need to select the image and update its format
            edit_cursor = self.editor.textCursor()
            f = edit_cursor.charFormat()
            if not f.isImageFormat():
                edit_cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor)
                f = edit_cursor.charFormat()
            else:
                edit_cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor)
            
            if f.isImageFormat():
                new_fmt = f.toImageFormat()
                new_fmt.setWidth(new_w)
                new_fmt.setHeight(new_h)
                edit_cursor.setCharFormat(new_fmt)

    def _align_image(self, alignment: Qt.AlignmentFlag) -> None:
        """Align the image block to the specified alignment."""
        cursor = self._get_image_cursor()
        if cursor:
            block_fmt = cursor.blockFormat()
            block_fmt.setAlignment(alignment)
            cursor.mergeBlockFormat(block_fmt)

    def _delete_selected_image(self) -> None:
        """Delete the currently selected image."""
        cursor = self._get_image_cursor()
        if cursor:
            cursor.removeSelectedText()

    def _replace_image(self) -> None:
        """Replace the current image with a new one."""
        cursor = self._get_image_cursor()
        if cursor:
            # Delete the old image first
            cursor.removeSelectedText()
            # Then insert a new one using the image feature
            if hasattr(self, 'image_feature'):
                self.image_feature.insert_image()

    def _get_current_image_data(self) -> Tuple[Optional[Any], Optional[QTextCursor], Optional[Any]]:
        """Get the current image as PIL Image, cursor, and format."""
        try:
            from PIL import Image
            from io import BytesIO
        except ImportError:
            return None, None, None
        
        from PyQt6.QtGui import QTextDocument, QTextCursor
        from PyQt6.QtCore import QUrl, QBuffer, QIODevice
        
        cursor = self.editor.textCursor()
        fmt = cursor.charFormat()
        
        if not fmt.isImageFormat():
            test_cursor = QTextCursor(cursor)
            test_cursor.movePosition(QTextCursor.MoveOperation.Right)
            fmt = test_cursor.charFormat()
            if not fmt.isImageFormat():
                return None, None, None
        
        img_fmt = fmt.toImageFormat()
        img_name = img_fmt.name()
        
        # Load the image from the document's resources
        doc = self.editor.document()
        resource = doc.resource(QTextDocument.ResourceType.ImageResource, QUrl(img_name))
        
        if resource.isNull():
            # Try loading from file path
            try:
                pil_img = Image.open(img_name)
                return pil_img, cursor, img_fmt
            except:
                return None, None, None
        
        # Convert QImage to PIL
        qimg = resource
        if hasattr(qimg, 'toImage'):
            qimg = qimg.toImage()
        
        # Convert to bytes
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        from PyQt6.QtGui import QImage
        if isinstance(qimg, QImage):
            qimg.save(buffer, "PNG")
            pil_img = Image.open(BytesIO(buffer.data()))
            return pil_img, cursor, img_fmt
        
        return None, None, None

    def _save_and_insert_image(self, pil_img: Any, old_fmt: Any) -> None:
        """Save PIL image and replace the old image in the document."""
        import uuid
        import os
        from io import BytesIO
        from PyQt6.QtGui import QImage, QTextImageFormat, QTextDocument
        from PyQt6.QtCore import QUrl
        
        # Convert PIL to QImage
        if pil_img.mode != "RGBA":
            pil_img = pil_img.convert("RGBA")
        data = pil_img.tobytes("raw", "RGBA")
        qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
        
        # Save to file
        temp_dir = os.path.join(os.getcwd(), "saved_documents", ".cache_images")
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}.png")
        
        buf = BytesIO()
        pil_img.save(buf, format="PNG")
        with open(temp_path, "wb") as f:
            f.write(buf.getvalue())
        
        # Add as resource
        image_id = f"image://edited/{uuid.uuid4().hex}.png"
        self.editor.document().addResource(
            QTextDocument.ResourceType.ImageResource, 
            QUrl(image_id), 
            qimg
        )
        
        # Delete old image and insert new one
        cursor = self._get_image_cursor()
        if cursor:
            cursor.removeSelectedText()
            
            new_fmt = QTextImageFormat()
            new_fmt.setName(temp_path)
            new_fmt.setWidth(old_fmt.width() if old_fmt.width() > 0 else pil_img.width)
            new_fmt.setHeight(old_fmt.height() if old_fmt.height() > 0 else pil_img.height)
            cursor.insertImage(new_fmt)

    def _apply_image_filter(self, filter_name: str):
        """Apply a filter to the current image."""
        try:
            from PIL import Image, ImageFilter, ImageOps, ImageEnhance
        except ImportError:
            return
        
        pil_img, cursor, img_fmt = self._get_current_image_data()
        if pil_img is None:
            return
        
        # Ensure RGBA
        if pil_img.mode != "RGBA":
            pil_img = pil_img.convert("RGBA")
        
        r, g, b, a = pil_img.split()
        
        if filter_name == "Grayscale":
            gray = pil_img.convert("L")
            pil_img = Image.merge("RGBA", (gray, gray, gray, a))
        
        elif filter_name == "Sepia":
            # Sepia transformation
            def sepia_pixel(r, g, b):
                """
                Sepia pixel logic.
                
                Args:
                    r: Description of r.
                    g: Description of g.
                    b: Description of b.
                
                """
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                return min(255, tr), min(255, tg), min(255, tb)
            
            pixels = list(zip(r.getdata(), g.getdata(), b.getdata()))
            new_r, new_g, new_b = [], [], []
            for pr, pg, pb in pixels:
                sr, sg, sb = sepia_pixel(pr, pg, pb)
                new_r.append(sr)
                new_g.append(sg)
                new_b.append(sb)
            
            r.putdata(new_r)
            g.putdata(new_g)
            b.putdata(new_b)
            pil_img = Image.merge("RGBA", (r, g, b, a))
        
        elif filter_name == "Warm":
            # Shift colors warmer (more red, less blue)
            def shift_channel(channel, shift):
                """
                Shift channel logic.
                
                Args:
                    channel: Description of channel.
                    shift: Description of shift.
                
                """
                return channel.point(lambda x: max(0, min(255, x + shift)))
            r = shift_channel(r, 20)
            b = shift_channel(b, -20)
            pil_img = Image.merge("RGBA", (r, g, b, a))
        
        elif filter_name == "Cool":
            # Shift colors cooler (more blue, less red)
            def shift_channel(channel, shift):
                """
                Shift channel logic.
                
                Args:
                    channel: Description of channel.
                    shift: Description of shift.
                
                """
                return channel.point(lambda x: max(0, min(255, x + shift)))
            r = shift_channel(r, -20)
            b = shift_channel(b, 20)
            pil_img = Image.merge("RGBA", (r, g, b, a))
        
        elif filter_name == "Vintage":
            # Reduce saturation, add warm tint, slight contrast boost
            pil_img = ImageEnhance.Color(pil_img).enhance(0.7)
            r, g, b, a = pil_img.split()
            def shift_channel(channel, shift):
                """
                Shift channel logic.
                
                Args:
                    channel: Description of channel.
                    shift: Description of shift.
                
                """
                return channel.point(lambda x: max(0, min(255, x + shift)))
            r = shift_channel(r, 15)
            g = shift_channel(g, 5)
            b = shift_channel(b, -10)
            pil_img = Image.merge("RGBA", (r, g, b, a))
            pil_img = ImageEnhance.Contrast(pil_img).enhance(1.1)
        
        elif filter_name == "Invert":
            rgb = Image.merge("RGB", (r, g, b))
            rgb = ImageOps.invert(rgb)
            r, g, b = rgb.split()
            pil_img = Image.merge("RGBA", (r, g, b, a))
        
        elif filter_name == "Blur":
            pil_img = pil_img.filter(ImageFilter.GaussianBlur(radius=2))
        
        elif filter_name == "Sharpen":
            pil_img = pil_img.filter(ImageFilter.SHARPEN)
        
        elif filter_name == "Emboss":
            pil_img = pil_img.filter(ImageFilter.EMBOSS)
        
        elif filter_name == "Find Edges":
            pil_img = pil_img.filter(ImageFilter.FIND_EDGES)
        
        elif filter_name == "Auto Contrast":
            rgb = Image.merge("RGB", (r, g, b))
            rgb = ImageOps.autocontrast(rgb)
            r, g, b = rgb.split()
            pil_img = Image.merge("RGBA", (r, g, b, a))
        
        self._save_and_insert_image(pil_img, img_fmt)

    def _rotate_image(self, degrees: int) -> None:
        """Rotate the current image by the specified degrees."""
        try:
            from PIL import Image
        except ImportError:
            return
        
        pil_img, cursor, img_fmt = self._get_current_image_data()
        if pil_img is None:
            return
        
        pil_img = pil_img.rotate(-degrees, expand=True)  # Negative for clockwise
        
        # Swap width/height for 90 degree rotations
        new_fmt = img_fmt
        if abs(degrees) == 90:
            old_w = img_fmt.width()
            old_h = img_fmt.height()
            new_fmt.setWidth(old_h)
            new_fmt.setHeight(old_w)
        
        self._save_and_insert_image(pil_img, new_fmt)

    def _crop_image(self) -> None:
        """Open a crop dialog to crop the current image."""
        from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                                      QSpinBox, QDialogButtonBox, QLabel, QGroupBox)
        from PyQt6.QtGui import QPixmap, QImage
        from PyQt6.QtCore import Qt
        
        try:
            from PIL import Image
        except ImportError:
            return
        
        pil_img, cursor, img_fmt = self._get_current_image_data()
        if pil_img is None:
            return
        
        img_w, img_h = pil_img.size
        
        # Create crop dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Crop Image")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Preview label
        preview_label = QLabel()
        preview_label.setFixedSize(300, 200)
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_label.setStyleSheet("border: 1px solid #ccc; background: #f0f0f0;")
        
        # Convert PIL to QPixmap for preview
        if pil_img.mode != "RGBA":
            pil_img = pil_img.convert("RGBA")
        data = pil_img.tobytes("raw", "RGBA")
        qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
        pix = QPixmap.fromImage(qimg)
        scaled_pix = pix.scaled(280, 180, Qt.AspectRatioMode.KeepAspectRatio, 
                                 Qt.TransformationMode.SmoothTransformation)
        preview_label.setPixmap(scaled_pix)
        layout.addWidget(preview_label)
        
        # Size info
        info_label = QLabel(f"Original size: {img_w} × {img_h} px")
        layout.addWidget(info_label)
        
        # Crop region inputs
        crop_group = QGroupBox("Crop Region")
        crop_layout = QHBoxLayout(crop_group)
        
        form1 = QFormLayout()
        x_spin = QSpinBox()
        x_spin.setRange(0, img_w - 1)
        x_spin.setValue(0)
        x_spin.setSuffix(" px")
        form1.addRow("X:", x_spin)
        
        y_spin = QSpinBox()
        y_spin.setRange(0, img_h - 1)
        y_spin.setValue(0)
        y_spin.setSuffix(" px")
        form1.addRow("Y:", y_spin)
        crop_layout.addLayout(form1)
        
        form2 = QFormLayout()
        w_spin = QSpinBox()
        w_spin.setRange(1, img_w)
        w_spin.setValue(img_w)
        w_spin.setSuffix(" px")
        form2.addRow("Width:", w_spin)
        
        h_spin = QSpinBox()
        h_spin.setRange(1, img_h)
        h_spin.setValue(img_h)
        h_spin.setSuffix(" px")
        form2.addRow("Height:", h_spin)
        crop_layout.addLayout(form2)
        
        layout.addWidget(crop_group)
        
        # Clamp width/height when X/Y changes
        def update_w_range():
            """
            Update w range logic.
            
            """
            max_w = img_w - x_spin.value()
            w_spin.setMaximum(max_w)
            if w_spin.value() > max_w:
                w_spin.setValue(max_w)
        
        def update_h_range():
            """
            Update h range logic.
            
            """
            max_h = img_h - y_spin.value()
            h_spin.setMaximum(max_h)
            if h_spin.value() > max_h:
                h_spin.setValue(max_h)
        
        x_spin.valueChanged.connect(update_w_range)
        y_spin.valueChanged.connect(update_h_range)
        
        # OK/Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            x = x_spin.value()
            y = y_spin.value()
            w = w_spin.value()
            h = h_spin.value()
            
            # Apply crop
            cropped = pil_img.crop((x, y, x + w, y + h))
            
            # Update format dimensions
            img_fmt.setWidth(w)
            img_fmt.setHeight(h)
            
            self._save_and_insert_image(cropped, img_fmt)

    def insert_hyperlink(self) -> None:
        """Open dialog to insert a hyperlink."""
        if not hasattr(self, '_insert_hyperlink_dialog'):
             # Lazy load or just use dialog directly if imported
             pass
        
        # Determine selection
        cursor = self.editor.textCursor()
        text = cursor.selectedText()
        
        dlg = HyperlinkDialog(text, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            url, display_text = dlg.get_data()
            if url:
                self.editor.insertHtml(f'<a href="{url}">{display_text}</a>')

    def page_setup(self) -> None:
        """Open page setup dialog."""
        dlg = PageSetupDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            # Apply settings (Mock implementation as SafeTextEdit is a Widget, not a full document layout engine)
            # In a real app we'd set document root frame margins or print settings
            pass

    def insert_horizontal_rule(self) -> None:
        """Insert a horizontal rule."""
        cursor = self.editor.textCursor()
        cursor.insertHtml("<hr>")
        cursor.insertBlock()
        self.editor.setFocus()
    
    def _pick_color(self) -> None:
        """Pick text color."""
        color = QColorDialog.getColor(self.editor.textColor(), self, "Select Text Color")
        if color.isValid():
            self.editor.setTextColor(color)
            
    def _pick_highlight(self) -> None:
        """Pick highlight color."""
        color = QColorDialog.getColor(self.editor.textBackgroundColor(), self, "Select Highlight Color")
        if color.isValid():
            self.editor.setTextBackgroundColor(color)
            
    def _clear_highlight(self) -> None:
        """Clear text background color."""
        self.editor.setTextBackgroundColor(QColor(Qt.GlobalColor.transparent))
        self.editor.setFocus()

    def _set_line_spacing(self, value_str: str) -> None:
        """Set paragraph line spacing."""
        try:
            spacing = float(value_str)
            block_fmt = QTextBlockFormat()
            block_fmt.setLineHeight(spacing * 100, 1) # 1 = ProportionalHeight
            cursor = self.editor.textCursor()
            cursor.mergeBlockFormat(block_fmt)
            self.editor.setFocus()
        except ValueError:
            pass

    def _toggle_text_direction(self) -> None:
        """Toggle between LTR and RTL."""
        is_rtl = self.editor.layoutDirection() == Qt.LayoutDirection.RightToLeft
        new_dir = Qt.LayoutDirection.LeftToRight if is_rtl else Qt.LayoutDirection.RightToLeft
        self.editor.setLayoutDirection(new_dir)
        self.editor.setFocus()
        # Also set alignment for convenience?
        # self.editor.setAlignment(Qt.AlignmentFlag.AlignRight if not is_rtl else Qt.AlignmentFlag.AlignLeft)

    def _toggle_list(self, style: QTextListFormat.Style) -> None:
        """Wrapper for list feature."""
        if hasattr(self, 'list_feature'):
            self.list_feature.toggle_list(style)
        self.editor.setFocus()

    def _insert_page_break(self) -> None:
        """Insert a page break marker."""
        # HTML/RTF page breaks are tricky. We use a CSS break-after or special char.
        # For visual purpose in editor:
        cursor = self.editor.textCursor()
        cursor.insertHtml('<br><hr style="border-top: 1px dashed #ccc;"/><br>')
        self.editor.setFocus()


    def _set_font_size(self, size_str: str) -> None:
        try:
            size = float(size_str)
            self.editor.setFontPointSize(size)
        except ValueError:
            pass
        self.editor.setFocus()

    def _toggle_bold(self) -> None:
        font_weight = self.editor.fontWeight()
        if font_weight == QFont.Weight.Bold:
            self.editor.setFontWeight(QFont.Weight.Normal)
        else:
            self.editor.setFontWeight(QFont.Weight.Bold)
        self.editor.setFocus()

    def _toggle_strikethrough(self) -> None:
        """Toggle strikethrough formatting."""
        fmt = self.editor.currentCharFormat()
        fmt.setFontStrikeOut(not fmt.fontStrikeOut())
        self.editor.mergeCurrentCharFormat(fmt)
        self.editor.setFocus()

    def _toggle_subscript(self) -> None:
        """Toggle subscript, exclusive with superscript."""
        fmt = self.editor.currentCharFormat()
        if fmt.verticalAlignment() == QTextCharFormat.VerticalAlignment.AlignSubScript:
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignNormal)
        else:
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSubScript)
        self.editor.mergeCurrentCharFormat(fmt)
        self.editor.setFocus()

    def _toggle_superscript(self) -> None:
        """Toggle superscript, exclusive with subscript."""
        fmt = self.editor.currentCharFormat()
        if fmt.verticalAlignment() == QTextCharFormat.VerticalAlignment.AlignSuperScript:
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignNormal)
        else:
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSuperScript)
        self.editor.mergeCurrentCharFormat(fmt)
        self.editor.setFocus()

    def _clear_formatting(self) -> None:
        """
        Reset character formatting to default for the current selection, 
        preserves block formatting.
        """
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            # Create a clean format
            fmt = QTextCharFormat()
            # We can't just use empty fmt because merge won't unset properties.
            # We have to explicitly set default properties.
            
            # Reset Font
            default_font = QFont("Arial", 12)
            fmt.setFont(default_font)
            fmt.setFontWeight(QFont.Weight.Normal)
            fmt.setFontItalic(False)
            fmt.setFontUnderline(False)
            fmt.setFontStrikeOut(False)
            
            # Reset Color
            fmt.setForeground(Qt.GlobalColor.black)
            fmt.setBackground(QBrush(Qt.BrushStyle.NoBrush))
            
            # Reset Alignment
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignNormal)
            
            # Apply
            # setCharFormat applied to selection replaces all char properties
            cursor.setCharFormat(fmt)
            self.editor.setFocus()


    def _pick_color(self) -> None:
        """
        Open a color picker to set the text color.
        Uses non-native dialog to avoid linux platform integration issues.
        """
        cursor = self.editor.textCursor()
        # Get current color
        fmt = cursor.charFormat()
        current_color = fmt.foreground().color()
        if not current_color.isValid():
            current_color = Qt.GlobalColor.black
        
        # UX Improvement: If color is Black (Value 0), the picker opens in "The Abyss" (Slider at bottom).
        # We default to Red to force the Value Slider to Max, allowing immediate color selection.
        initial_color = current_color
        if current_color.lightness() == 0:
            initial_color = Qt.GlobalColor.red
            
        dialog = QColorDialog(initial_color, self)
        dialog.setWindowTitle("Select Text Color")
        dialog.setOptions(QColorDialog.ColorDialogOption.ShowAlphaChannel | 
                          QColorDialog.ColorDialogOption.DontUseNativeDialog)
        
        if dialog.exec():
            color = dialog.currentColor()
            if color.isValid():
                # Apply using mergeCharFormat for robustness
                new_fmt = QTextCharFormat()
                new_fmt.setForeground(color)
                self.editor.mergeCurrentCharFormat(new_fmt)
                self.editor.setFocus()

    def _apply_style(self, style_name: str) -> None:
        """Apply a semantic style to the current selection/block."""
        if style_name not in self.styles:
            return
            
        style = self.styles[style_name]
        cursor = self.editor.textCursor()
        
        # If no selection, apply to the entire block (paragraph)
        if not cursor.hasSelection():
            cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        
        
        
        # Fallback to HTML insertion for robust styling if direct formatting fails
        # This is a bit heavier but guarantees the style is applied by the engine parser
        
        
        selected_text = cursor.selectedText()
        # Replace Paragraph Separator with space or nothing, as we are wrapping in block tag
        selected_text = selected_text.replace('\u2029', '')
            
        # Determine tag
        tag = "p"
        if style_name == "Heading 1": tag = "h1"
        elif style_name == "Heading 2": tag = "h2"
        elif style_name == "Heading 3": tag = "h3"
        elif style_name == "Title": tag = "h1" # Title as h1 for now
        elif style_name == "Code": tag = "pre"
        
        # Build HTML with inline style to enforce our specific look (font, size)
        # Note: h1 in Qt might have default margins, we can override if needed
        pt_size = style["size"]
        family = style["family"]
        # font-weight is handled by h1 usually, but we enforce specific
        weight_css = "bold" if style["weight"] == QFont.Weight.Bold else "normal"
        
        # We need to ensure the styling applies. 
        # Using a span inside the block tag often helps Qt parser.
        html = f'<{tag} style="margin-top: 10px; margin-bottom: 5px;"><span style="font-family: {family}; font-size: {pt_size}pt; font-weight: {weight_css};">{selected_text}</span></{tag}>'
        
        self.editor.blockSignals(True)
        cursor.insertHtml(html)
        self.editor.blockSignals(False)
        self.editor.setFocus()
        
        # Update combo boxes manually to reflect the change visually in toolbar
        self.size_combo.setCurrentText(str(style["size"]))
        self.font_combo.setCurrentFont(QFont(style["family"]))

    def _pick_highlight(self) -> None:
        cursor = self.editor.textCursor()
        fmt = cursor.charFormat()
        current_bg = fmt.background().color()
        if not current_bg.isValid():
            current_bg = Qt.GlobalColor.white

        dialog = QColorDialog(current_bg, self)
        dialog.setWindowTitle("Select Highlight Color")
        dialog.setOptions(QColorDialog.ColorDialogOption.ShowAlphaChannel | 
                          QColorDialog.ColorDialogOption.DontUseNativeDialog)
                          
        if dialog.exec():
            color = dialog.currentColor()
            if color.isValid():
                new_fmt = QTextCharFormat()
                new_fmt.setBackground(color)
                self.editor.mergeCurrentCharFormat(new_fmt)
                self.editor.setFocus()

    def _clear_highlight(self) -> None:
        """Clear the background highlight."""
        self.editor.setTextBackgroundColor(QColor(Qt.GlobalColor.transparent))

    def _on_zoom_changed(self, value: int):
        """Handle zoom slider change."""
        self.zoom_label.setText(f"{value}%")
        # Delegate zoom to the Substrate (Infinite Canvas)
        # This scales the entire view (Paper + Text)
        if hasattr(self, 'substrate'):
            self.substrate.set_zoom(value / 100.0)
        else:
            # Fallback for headless or legacy modes (though setup always creates substrate now)
            pass

    def _update_word_count(self) -> None:
        """Update the word and character count in status bar."""
        text = self.editor.toPlainText()
        char_count = len(text)
        # Word count: split by whitespace, filter empty
        words = [w for w in text.split() if w.strip()]
        word_count = len(words)
        # Paragraph count: split by newlines
        paragraphs = [p for p in text.split('\n') if p.strip()]
        para_count = len(paragraphs) if paragraphs else 0
        
        self.word_count_label.setText(
            f"Words: {word_count:,} | Characters: {char_count:,} | Paragraphs: {para_count:,}"
        )

    def _update_page_count(self) -> None:
        """Update total page count based on document size."""
        if not hasattr(self, 'page_count_label'):
            return
        
        # Calculate pages based on document height vs page height
        doc = self.editor.document()
        doc_height = doc.size().height()
        
        # Get page height from editor settings
        page_height = self.editor.page_height
        
        self._total_pages = max(1, int(doc_height / page_height) + (1 if doc_height % page_height > 50 else 0))
        self._update_page_label()
    
    def _update_current_page(self) -> None:
        """Update current page based on cursor position."""
        if not hasattr(self, 'page_count_label'):
            return
        
        cursor = self.editor.textCursor()
        cursor_rect = self.editor.cursorRect(cursor)
        
        # Calculate which "page" the cursor is on using editor settings
        page_height = self.editor.page_height
        cursor_y = cursor_rect.top() + self.editor.verticalScrollBar().value()
        
        self._current_page = max(1, min(int(cursor_y / page_height) + 1, getattr(self, '_total_pages', 1)))
        self._update_page_label()
    
    def _update_page_label(self) -> None:
        """Update the page label text."""
        if hasattr(self, 'page_count_label'):
            current = getattr(self, '_current_page', 1)
            total = getattr(self, '_total_pages', 1)
            self.page_count_label.setText(f"Page {current} of {total}")

    def _toggle_page_breaks(self, checked: bool):
        """Toggle visibility of page break lines."""
        self.editor.show_page_breaks = checked

    def _set_line_spacing(self, spacing_str: str) -> None:
        """Set line spacing for the current paragraph."""
        try:
            spacing = float(spacing_str)
        except ValueError:
            return
        
        cursor = self.editor.textCursor()
        block_fmt = cursor.blockFormat()
        
        # Qt uses line height as percentage (100 = single, 150 = 1.5, etc.)
        # Or we can use setLineHeight with specific type
        from PyQt6.QtGui import QTextBlockFormat
        block_fmt.setLineHeight(spacing * 100, QTextBlockFormat.LineHeightTypes.ProportionalHeight.value)
        cursor.setBlockFormat(block_fmt)

    def _toggle_text_direction(self) -> None:
        """Toggle between LTR and RTL text direction."""
        cursor = self.editor.textCursor()
        block_fmt = cursor.blockFormat()
        
        current_dir = block_fmt.layoutDirection()
        if current_dir == Qt.LayoutDirection.RightToLeft:
            block_fmt.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            self.action_rtl.setChecked(False)
        else:
            block_fmt.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            self.action_rtl.setChecked(True)
        
        cursor.setBlockFormat(block_fmt)

    def _insert_hyperlink(self) -> None:
        """Insert a hyperlink at the current cursor position."""
        cursor = self.editor.textCursor()
        selected_text = cursor.selectedText() if cursor.hasSelection() else ""
        
        dialog = HyperlinkDialog(selected_text, self)
        if dialog.exec():
            url = dialog.url_input.text().strip()
            display_text = dialog.text_input.text().strip() or url
            
            if url:
                # Ensure URL has a scheme
                if not url.startswith(('http://', 'https://', 'mailto:', 'file://')):
                    url = 'https://' + url
                
                # Insert as HTML anchor
                html = f'<a href="{url}">{display_text}</a>'
                cursor.insertHtml(html)

    def _insert_horizontal_rule(self) -> None:
        """Insert a horizontal rule at the current cursor position."""
        dialog = HorizontalRuleDialog(self)
        if dialog.exec():
            cursor = self.editor.textCursor()
            # Insert the HR - no need for insertBlock as HR is a block element
            cursor.insertHtml(dialog.get_html())

    def _show_special_characters(self) -> None:
        """Show the special characters dialog."""
        if not hasattr(self, '_special_chars_dialog') or self._special_chars_dialog is None:
            self._special_chars_dialog = SpecialCharactersDialog(self)
            self._special_chars_dialog.char_selected.connect(self._insert_special_char)
        self._special_chars_dialog.show()
        self._special_chars_dialog.raise_()

    def _insert_special_char(self, char: str):
        """Insert a special character at cursor position."""
        cursor = self.editor.textCursor()
        cursor.insertText(char)
        self.editor.setFocus()

    def _show_page_setup(self) -> None:
        """Show page setup dialog."""
        dialog = PageSetupDialog(self)
        if dialog.exec():
            # Store page settings for later use in printing/export
            self._page_size = dialog.get_page_size()
            self._page_orientation = dialog.get_orientation()
            self._page_margins = dialog.get_margins()
            QMessageBox.information(self, "Page Setup", "Page settings saved for printing/export.")

    def _export_pdf(self) -> None:
        """Export document to PDF."""
        dialog = ExportPdfDialog(self)
        if dialog.exec():
            file_path = dialog.get_file_path()
            if not file_path:
                QMessageBox.warning(self, "Export PDF", "Please specify an output file.")
                return
            
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)
            
            # Set page layout
            page_layout = QPageLayout(
                dialog.get_page_size(),
                dialog.get_orientation(),
                dialog.get_margins(),
                QPageLayout.Unit.Millimeter
            )
            printer.setPageLayout(page_layout)
            
            # Print document to PDF
            self.editor.document().print(printer)
            
            QMessageBox.information(self, "Export PDF", f"Document exported to:\n{file_path}")

    def _print_document(self) -> None:
        """Print the document."""
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        
        # Apply saved page settings if available
        if hasattr(self, '_page_size'):
            page_layout = QPageLayout(
                self._page_size,
                getattr(self, '_page_orientation', QPageLayout.Orientation.Portrait),
                getattr(self, '_page_margins', QMarginsF(20, 20, 20, 20)),
                QPageLayout.Unit.Millimeter
            )
            printer.setPageLayout(page_layout)
        
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            self.editor.document().print(printer)

    def _print_preview(self) -> None:
        """Show print preview dialog."""
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        
        # Apply saved page settings if available
        if hasattr(self, '_page_size'):
            page_layout = QPageLayout(
                self._page_size,
                getattr(self, '_page_orientation', QPageLayout.Orientation.Portrait),
                getattr(self, '_page_margins', QMarginsF(20, 20, 20, 20)),
                QPageLayout.Unit.Millimeter
            )
            printer.setPageLayout(page_layout)
        
        preview = QPrintPreviewDialog(printer, self)
        preview.setMinimumSize(800, 600)
        preview.resize(1000, 750)
        preview.paintRequested.connect(lambda p: self.editor.document().print(p))
        preview.exec()



    def _show_virtual_keyboard(self) -> None:
        self.virtual_keyboard = get_shared_virtual_keyboard(self)
        self.virtual_keyboard.set_target_editor(self.editor)
        self.virtual_keyboard.show()
        self.virtual_keyboard.raise_()
        self.virtual_keyboard.activateWindow()

    def _update_format_widgets(self, fmt: QTextCharFormat) -> None:
        """Update the ribbon widgets based on the current text format."""
        if not hasattr(self, 'font_combo'):
            return

        # Block signals to prevent triggering changes while updating UI
        self.font_combo.blockSignals(True)
        self.size_combo.blockSignals(True)
        
        # New QToolButtons for styling
        if hasattr(self, 'btn_bold'): self.btn_bold.blockSignals(True)
        if hasattr(self, 'btn_italic'): self.btn_italic.blockSignals(True)
        if hasattr(self, 'btn_underline'): self.btn_underline.blockSignals(True)
        if hasattr(self, 'btn_strike'): self.btn_strike.blockSignals(True)
        
        # QActions
        self.action_sub.blockSignals(True)
        self.action_super.blockSignals(True)
        self.action_align_left.blockSignals(True)
        self.action_align_center.blockSignals(True)
        self.action_align_right.blockSignals(True)
        self.action_align_justify.blockSignals(True)
        
        # Update Font & Size
        self.font_combo.setCurrentFont(fmt.font())
        try:
            current_size = int(fmt.fontPointSize())
            if current_size <= 0: current_size = 12 # Default fallback
            self.size_combo.setCurrentText(str(current_size))
        except:
            pass
        
        # Update Styles
        if hasattr(self, 'btn_bold'): 
            self.btn_bold.setChecked(fmt.fontWeight() == QFont.Weight.Bold)
        if hasattr(self, 'btn_italic'):
            self.btn_italic.setChecked(fmt.fontItalic())
        if hasattr(self, 'btn_underline'):
            self.btn_underline.setChecked(fmt.fontUnderline())
        if hasattr(self, 'btn_strike'):
            self.btn_strike.setChecked(fmt.fontStrikeOut())
        
        # Update Sub/Super
        v_align = fmt.verticalAlignment()
        self.action_sub.setChecked(v_align == QTextCharFormat.VerticalAlignment.AlignSubScript)
        self.action_super.setChecked(v_align == QTextCharFormat.VerticalAlignment.AlignSuperScript)
        
        # Update Alignment
        align = self.editor.alignment()
        if align & Qt.AlignmentFlag.AlignLeft:
            self.action_align_left.setChecked(True)
        elif align & Qt.AlignmentFlag.AlignHCenter:
            self.action_align_center.setChecked(True)
        elif align & Qt.AlignmentFlag.AlignRight:
            self.action_align_right.setChecked(True)
        elif align & Qt.AlignmentFlag.AlignJustify:
            self.action_align_justify.setChecked(True)
        
        # Unblock signals
        self.font_combo.blockSignals(False)
        self.size_combo.blockSignals(False)
        
        if hasattr(self, 'btn_bold'): self.btn_bold.blockSignals(False)
        if hasattr(self, 'btn_italic'): self.btn_italic.blockSignals(False)
        if hasattr(self, 'btn_underline'): self.btn_underline.blockSignals(False)
        if hasattr(self, 'btn_strike'): self.btn_strike.blockSignals(False)
        
        self.action_sub.blockSignals(False)
        self.action_super.blockSignals(False)
        self.action_align_left.blockSignals(False)
        self.action_align_center.blockSignals(False)
        self.action_align_right.blockSignals(False)
        self.action_align_justify.blockSignals(False)
        
    # --- Public API ---
    def get_html(self) -> str:
        """
        Retrieve html logic.
        
        Returns:
            Result of get_html operation.
        """
        return self.editor.toHtml()
        
    def set_html(self, html: str) -> None:
        """
        Configure html logic.
        
        Args:
            html: Description of html.
        
        Returns:
            Result of set_html operation.
        """
        self.editor.setHtml(html)
        # Ensure LTR is maintained after setting content
        self.editor.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        
    def get_text(self) -> str:
        """
        Retrieve text logic.
        
        Returns:
            Result of get_text operation.
        """
        return self.editor.toPlainText()
        
    def set_text(self, text: str) -> None:
        """
        Configure text logic.
        
        Args:
            text: Description of text.
        
        Returns:
            Result of set_text operation.
        """
        self.editor.setPlainText(text)

    def set_markdown(self, markdown: str):
        """Set the editor content from Markdown."""
        self.editor.setMarkdown(markdown)
        # Ensure LTR is maintained
        self.editor.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

    def get_markdown(self) -> str:
        """Get the editor content as Markdown."""
        return self.editor.document().toMarkdown()
        
    def clear(self) -> None:
        """
        Clear logic.
        
        Returns:
            Result of clear operation.
        """
        self.editor.clear()

    def find_text(self, text: str) -> bool:
        """Find first occurrence of text and select it."""
        if not text:
            return False
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)
        found = self.editor.find(text)
        if found:
            self.editor.setFocus()
            return True
        return False
    
    def find_all_matches(self, text: str) -> int:
        """Count all matches and position cursor at first. Returns match count."""
        if not text:
            self._search_term = None
            self._match_count = 0
            self._current_match = 0
            return 0
        
        self._search_term = text
        self._match_count = 0
        self._current_match = 0
        
        # Count all matches by iterating through document
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.editor.setTextCursor(cursor)
        
        # Count matches
        while self.editor.find(text):
            self._match_count += 1
        
        # Move back to start and find first match
        if self._match_count > 0:
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.editor.setTextCursor(cursor)
            self.editor.find(text)
            self._current_match = 1
            self.editor.setFocus()
            # Center the view on the match
            self._center_cursor_in_view()
        
        return self._match_count
    
    def _center_cursor_in_view(self) -> None:
        """Scroll the viewport to center the cursor vertically."""
        cursor_rect = self.editor.cursorRect()
        viewport_height = self.editor.viewport().height()
        # Calculate scroll position to center the cursor
        scrollbar = self.editor.verticalScrollBar()
        current_scroll = scrollbar.value()
        cursor_y = cursor_rect.top()
        # Center: move cursor to middle of viewport
        target_scroll = current_scroll + cursor_y - (viewport_height // 2)
        scrollbar.setValue(max(0, target_scroll))
    
    def find_next(self) -> bool:
        """Navigate to next match. Returns True if found."""
        if not hasattr(self, '_search_term') or not self._search_term:
            return False
        
        found = self.editor.find(self._search_term)
        if found:
            self._current_match = min(self._current_match + 1, self._match_count)
            self._center_cursor_in_view()
            return True
        else:
            # Wrap to start
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.editor.setTextCursor(cursor)
            found = self.editor.find(self._search_term)
            if found:
                self._current_match = 1
                self._center_cursor_in_view()
                return True
        return False
    
    def find_previous(self) -> bool:
        """Navigate to previous match. Returns True if found."""
        if not hasattr(self, '_search_term') or not self._search_term:
            return False
        
        # QTextEdit.find() only goes forward, so use FindBackward flag
        found = self.editor.find(self._search_term, QTextDocument.FindFlag.FindBackward)
        if found:
            self._current_match = max(self._current_match - 1, 1)
            self._center_cursor_in_view()
            return True
        else:
            # Wrap to end
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.editor.setTextCursor(cursor)
            found = self.editor.find(self._search_term, QTextDocument.FindFlag.FindBackward)
            if found:
                self._current_match = self._match_count
                self._center_cursor_in_view()
                return True
        return False
    
    def get_match_info(self) -> Tuple[int, int]:
        """Get current match position info. Returns (current, total)."""
        current = getattr(self, '_current_match', 0)
        total = getattr(self, '_match_count', 0)
        return (current, total)
    
    def clear_search(self) -> None:
        """Clear search state."""
        self._search_term = None
        self._match_count = 0
        self._current_match = 0

    def new_document(self) -> None:
        """Clear the editor for a new document."""
        if self.editor.document().isModified():
            ans = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Are you sure you want to clear the document?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if ans != QMessageBox.StandardButton.Yes:
                return
        self.editor.clear()

    def open_document(self) -> None:
        """Open a file (Markdown, HTML, Text)."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Document", "",
            "Markdown (*.md);;HTML (*.html *.htm);;Text (*.txt);;All Files (*)"
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if file_path.endswith('.md'):
                self.editor.setMarkdown(content)
            elif file_path.endswith(('.html', '.htm')):
                self.editor.setHtml(content)
            else:
                self.editor.setPlainText(content)
                
            self.editor.document().setModified(False)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file:\n{e}")

    def save_document(self) -> None:
        """Save the document (Markdown, HTML, Text)."""
        file_path, filter_used = QFileDialog.getSaveFileName(
            self, "Save Document", "",
            "Markdown (*.md);;HTML (*.html);;Text (*.txt)"
        )
        if not file_path:
            return

        try:
            if file_path.endswith('.md'):
                # Convert to Markdown
                # Note: Qt's toMarkdown features are basic but standard compliant.
                content = self.editor.document().toMarkdown()
            elif file_path.endswith('.html'):
                content = self.editor.toHtml()
            else:
                content = self.editor.toPlainText()

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.editor.document().setModified(False)
            QMessageBox.information(self, "Saved", f"Document saved to {os.path.basename(file_path)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")