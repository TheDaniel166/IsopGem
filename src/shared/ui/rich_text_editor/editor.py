"""Reusable Rich Text Editor widget with Ribbon UI."""
import html as html_module
import logging
import os
import base64
from typing import Optional, Any, Union, List, Tuple, Dict, Generator, Callable
from collections import OrderedDict

logger = logging.getLogger(__name__)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QComboBox, QFontComboBox, QSpinBox,
    QColorDialog, QMenu, QToolButton, QDialog,
    QLabel, QDialogButtonBox, QFormLayout, QDoubleSpinBox, QMessageBox,
    QSlider, QLineEdit, QStatusBar, QFileDialog, QGridLayout,
    QScrollArea, QFrame, QGroupBox, QPushButton, QTabWidget, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QMimeData, QUrl, QMarginsF, QSizeF, QPoint, QTimer, QBuffer, QByteArray
from PyQt6.QtGui import (
    QFont, QAction, QColor, QTextCharFormat, QTextImageFormat, QTextFragment,
    QTextCursor, QTextListFormat, QTextBlockFormat,
    QActionGroup, QBrush, QDesktopServices, QPageSize, QPageLayout, QKeySequence,
    QTextDocument, QPaintEvent
)
import qtawesome as qta
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog

# Feature modules
from .table_features import TableFeature
from .image_features import ImageInsertFeature, ImageEditFeature
from .image_gateway import ImageGateway
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
    SpecialCharactersDialog, ExportPdfDialog, PageModeDialog
)

# Page settings and constants
from .editor_constants import PageSettings, DEFAULT_PAGE_SETTINGS

# Shared UI
from shared.ui import VirtualKeyboard, get_shared_virtual_keyboard

# Custom block property for pagination margins (avoids collision with user content)
# Using "_PAG" as an integer constant for Qt property system
PAGINATION_PROP = 0x5F504147
PAGINATION_ORIG_PROP = 0x5F504F52  # _PAG_ORIGINAL
PAGEBREAK_PROP = 0x5F504247  # _PBG - Sovereign page break marker


# =============================================================================
# Unified Pagination Mode System
# =============================================================================
from enum import Enum, auto
from dataclasses import dataclass, field


class PageMode(Enum):
    """
    Pagination display and enforcement modes.
    
    Presets provide opinionated defaults; CUSTOM allows granular control.
    """
    FREEFLOW = auto()      # No guides, no enforcement (fast free-flow editor)
    GUIDES_ONLY = auto()   # Show page break lines + gap fill, no enforcement
    ENFORCE_ONLY = auto()  # Enforce pagination, no visual guides
    PAGED = auto()         # Both guides and enforcement (full document mode)
    CUSTOM = auto()        # Manual control via PageModeOptions


@dataclass
class PageModeOptions:
    """
    Granular pagination control for CUSTOM mode or preset overrides.
    
    Presets determine default values; these can be explicitly overridden.
    Option slots include future hooks for guide intensity, page numbers, etc.
    """
    # Core toggles
    show_guides: bool = False        # Dashed lines at page breaks
    show_gap_fill: bool = False      # Shaded gutter between pages
    enforce_pagination: bool = False # Block margin enforcement
    scroll_anchor: bool = True       # Anchor-based scroll restoration
    
    # Coupling policy
    couple_guides_and_enforcement: bool = False  # When True, guides <-> enforcement sync
    
    # Visual tuning
    page_gap: Optional[int] = None   # Override gutter size (None = use default)
    
    # Future hooks (reserved slots)
    # guide_style: str = "dashed"    # Future: solid, dashed, dotted
    # guide_opacity: float = 1.0     # Future: intensity tuning
    # show_page_numbers: bool = False # Future: page numbers in gutter


class SafeTextEdit(QTextEdit):
    """
    A hardened QTextEdit implementing the Mars Seal defensive pattern.
    
    Provides two critical fortifications:
    1. **Paste Protection**: Intercepts large clipboard payloads (text, HTML, images)
       and prompts user confirmation before inserting potentially freezing content.
    2. **Atomic Block Pagination**: Ensures text blocks don't straddle page boundaries
       by dynamically adjusting top margins, creating clean visual page breaks.
    
    Also handles custom `docimg://` resource URLs for database-backed image loading.
    """
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the hardened text editor with pagination and resource handling.
        
        Sets up debounced pagination timers, scroll guards to prevent layout edits
        during active scrolling, and connects the docimg:// resource protocol.
        
        **Pagination Sovereignty**: Pagination is intentionally opt-in (default: disabled).
        This preserves stability for simple text editing while allowing the Magus to
        awaken deeper layout rites via `enable_pagination(True)` when needed. This is
        sovereign design, not incompleteness.
        
        Args:
            parent: Parent widget for Qt ownership hierarchy.
        """
        super().__init__(parent)
        self.resource_provider: Optional[Callable[[int], Optional[Tuple[bytes, str]]]] = None
        self.resource_saver: Optional[Callable[[bytes, str], Optional[int]]] = None
        self._show_page_breaks = False
        self._page_settings = DEFAULT_PAGE_SETTINGS
        self._docimg_cache: "OrderedDict[int, Any]" = OrderedDict()
        
        # Pagination Sovereignty: opt-in by design (see enable_pagination())
        self.pagination_enabled = False
        
        # Pagination State
        # NOTE: Use self.page_height property (from settings) as single source of truth
        self._page_gap = 20 # Gap between visual pages
        self._is_paginating = False
        self._pagination_timer = QTimer(self)
        self._pagination_timer.setSingleShot(True)
        self._pagination_timer.setInterval(400)  # Debounce: slower to avoid post-scroll churn
        self._pagination_timer.timeout.connect(self._do_pagination)
        self.textChanged.connect(self._schedule_pagination)
        
        # Monotonic pagination counter (sovereign, not relying on Qt's revision)
        self._pagination_generation = 0
        self._last_paginated_generation = -1

        # Scroll guard to avoid pagination/layout edits mid-scroll
        self._is_scrolling = False
        self._scroll_timer = QTimer(self)
        self._scroll_timer.setSingleShot(True)
        self._scroll_timer.setInterval(350)
        self._scroll_timer.timeout.connect(self._end_scroll)
        
        # Anchor-based scroll restoration (toggle off with one line if needed)
        self.scroll_anchor_enabled = True
        scrollbar = self.verticalScrollBar()
        if scrollbar is not None:
            scrollbar.valueChanged.connect(self._on_scroll)
    
    def _schedule_pagination(self):
        """Schedule pagination check (debounced to avoid per-keystroke runs)."""
        if not getattr(self, "pagination_enabled", True):
            return
        if getattr(self, "_is_paginating", False):
            return
        if getattr(self, "_is_scrolling", False):
            return
        self._pagination_timer.start()
    
    def enable_pagination(self, enabled: bool = True) -> None:
        """
        Awaken or suspend the pagination rite.
        
        Pagination is intentionally opt-in—guarded for stability by sovereign design.
        When enabled, the editor ensures text blocks do not straddle page boundaries,
        providing clean page break visualization for document layout.
        
        **Why Opt-In**: Pagination involves layout mutation that can interact with
        scrolling, undo/redo, and large content in complex ways. Keeping it disabled
        by default ensures smooth operation for simple text editing, while allowing
        explicit activation when deeper layout rites are needed.
        
        Args:
            enabled: True to awaken pagination, False to suspend.
        
        Example:
            editor.enable_pagination(True)  # Awaken for document layout
            editor.enable_pagination(False)  # Suspend for simple editing
        """
        self.pagination_enabled = enabled
        if enabled:
            # Trigger immediate pagination check
            self._schedule_pagination()
    
    def set_page_mode(self, mode: PageMode, opts: Optional[PageModeOptions] = None) -> None:
        """
        Set pagination mode with unified control.
        
        This is the sovereign entry point for all pagination state changes.
        Presets provide opinionated defaults; CUSTOM mode allows full granular control.
        
        Args:
            mode: The PageMode preset to apply
            opts: Optional PageModeOptions for overrides (required for CUSTOM mode)
        
        Example:
            editor.set_page_mode(PageMode.PAGED)  # Full document mode
            editor.set_page_mode(PageMode.FREEFLOW)  # Fast free-flow editing
            editor.set_page_mode(PageMode.CUSTOM, PageModeOptions(
                show_guides=True,
                show_gap_fill=False,
                enforce_pagination=True
            ))
        """
        # Resolve preset to base options
        if mode == PageMode.FREEFLOW:
            resolved = PageModeOptions(
                show_guides=False,
                show_gap_fill=False,
                enforce_pagination=False,
                scroll_anchor=True
            )
        elif mode == PageMode.GUIDES_ONLY:
            resolved = PageModeOptions(
                show_guides=True,
                show_gap_fill=True,
                enforce_pagination=False,
                scroll_anchor=True
            )
        elif mode == PageMode.ENFORCE_ONLY:
            resolved = PageModeOptions(
                show_guides=False,
                show_gap_fill=False,
                enforce_pagination=True,
                scroll_anchor=True
            )
        elif mode == PageMode.PAGED:
            resolved = PageModeOptions(
                show_guides=True,
                show_gap_fill=True,
                enforce_pagination=True,
                scroll_anchor=True
            )
        elif mode == PageMode.CUSTOM:
            if opts is None:
                # CUSTOM requires explicit options
                resolved = PageModeOptions()
            else:
                resolved = opts
        else:
            resolved = PageModeOptions()
        
        # Apply overrides from opts if provided (for preset customization)
        if opts is not None and mode != PageMode.CUSTOM:
            # Override only explicitly set values (non-default check would require more logic)
            # For simplicity, CUSTOM mode uses opts directly; presets ignore opts currently
            pass
        
        # Handle coupling policy
        if resolved.couple_guides_and_enforcement:
            # Sync enforcement to guides state
            resolved.enforce_pagination = resolved.show_guides
        
        # Apply page_gap override if specified
        if resolved.page_gap is not None:
            self._page_gap = resolved.page_gap
        
        # Commit state to concrete flags
        self._show_page_breaks = resolved.show_guides or resolved.show_gap_fill
        self._show_gap_fill = resolved.show_gap_fill  # Add flag if not exists
        self.pagination_enabled = resolved.enforce_pagination
        self.scroll_anchor_enabled = resolved.scroll_anchor
        
        # Store current mode for introspection
        self._current_page_mode = mode
        self._current_page_options = resolved
        
        # Trigger updates
        if resolved.enforce_pagination:
            self._schedule_pagination()
        
        # Repaint for visual changes
        viewport = self.viewport()
        if viewport is not None:
            viewport.update()

    def _on_scroll(self):
        """Mark scrolling active and debounce end marker."""
        self._is_scrolling = True
        if self._pagination_timer.isActive():
            self._pagination_timer.stop()
        self._scroll_timer.start()

    def _end_scroll(self):
        """End scroll window to allow pagination to resume."""
        self._is_scrolling = False

    def _find_visible_anchor_block_pos(self) -> Optional[int]:
        """
        Return the document position() of the block at the viewport top.
        
        Uses cursorForPosition() to find the cursor at the top-left of the viewport,
        which is stable across margin changes, DPI scaling, and layout mutations.
        """
        from PyQt6.QtCore import QPoint
        
        # Get cursor at top-left corner of viewport (pixel 1,1 to be safe)
        cur = self.cursorForPosition(QPoint(1, 1))
        block = cur.block()
        return int(block.position()) if block.isValid() else None

    def _get_block_viewport_offset_by_pos(self, block_pos: int) -> float:
        """
        Get the block's current vertical offset from the viewport top.
        
        Uses cursorRect() for viewport-stable coordinates rather than mixing
        document layout coords with scrollbar values.
        """
        from PyQt6.QtGui import QTextCursor
        
        doc = self.document()
        if doc is None:
            return 0.0
        
        block = doc.findBlock(block_pos)
        if not block.isValid():
            return 0.0
        
        # Create a cursor positioned at the block start
        cur = QTextCursor(block)
        # cursorRect gives us viewport coordinates directly
        r = self.cursorRect(cur)
        return float(r.top())

    def _calculate_anchor_scroll_by_pos(self, block_pos: int, target_offset: float) -> Optional[int]:
        """
        Compute scrollbar adjustment to restore the block at its original viewport offset.
        
        Returns the raw desired scroll position. Caller should clamp to the
        scrollbar's current min/max range before applying.
        """
        from PyQt6.QtGui import QTextCursor
        
        doc = self.document()
        if doc is None:
            return None
        
        block = doc.findBlock(block_pos)
        if not block.isValid():
            return None
        
        scrollbar = self.verticalScrollBar()
        if scrollbar is None:
            return None
        
        # Create a cursor at the block and get its current viewport position
        cur = QTextCursor(block)
        current_rect = self.cursorRect(cur)
        current_offset = float(current_rect.top())
        
        # How much do we need to scroll to move from current_offset to target_offset?
        # If current_offset > target_offset, we need to scroll UP (decrease scroll value)
        # If current_offset < target_offset, we need to scroll DOWN (increase scroll value)
        delta = current_offset - target_offset
        desired = scrollbar.value() + int(delta)
        return desired

    def _do_pagination(self):
        """
        Atomic Block Pagination: Ensures blocks don't straddle page boundaries.
        
        Algorithm:
        1. Iterate through all text blocks in the document
        2. For each block, check if it would cross a page boundary
        3. If so, add top margin to push it to the next page
        4. Blocks larger than a page are allowed to overflow
        
        Debounced via QTimer to avoid running per-keystroke.
        Uses PAGINATION_PROP to mark blocks we've modified (reliable reset).
        Disables undo/redo to prevent layout edits from polluting history.
        """
        if not getattr(self, "pagination_enabled", True):
            return
        if self._is_paginating or self._is_scrolling:
            return
        doc = self.document()
        if doc is None:
            return
        
        # Monotonic generation gate (sovereign counter, not Qt revision)
        if self._pagination_generation == self._last_paginated_generation:
            return
            
        self._is_paginating = True
        changed = False  # Initialize before try to prevent UnboundLocalError in finally
        try:
            doc = self.document()
            if doc is None:
                return
            layout = doc.documentLayout()
            if layout is None:
                return
            scrollbar = self.verticalScrollBar()
            saved_scroll = scrollbar.value() if scrollbar is not None else None
            
            # Anchor-based scroll restoration: capture visible block position
            anchor_pos: Optional[int] = None
            anchor_offset = 0.0
            if getattr(self, "scroll_anchor_enabled", True) and scrollbar is not None:
                anchor_pos = self._find_visible_anchor_block_pos()
                if anchor_pos is not None:
                    anchor_offset = self._get_block_viewport_offset_by_pos(anchor_pos)
            
            # Capture the revision after any edits we make below
            current_rev = doc.revision()
            margin_offset = 0.0
            if hasattr(doc, "documentMargin"):
                margin_offset = float(doc.documentMargin())
            # Use property as single source of truth for page height
            page_height = self.page_height
            cycle = page_height + self._page_gap
            
            # Disable undo/redo - pagination is view hygiene, not authored content
            undo_enabled = doc.isUndoRedoEnabled()
            doc.setUndoRedoEnabled(False)
            
            try:
                # Use a single cursor for all edits
                edit_cursor = QTextCursor(doc)
                
                edit_cursor.beginEditBlock()
                try:
                    # Iterate all blocks
                    block = doc.begin()
                    while block.isValid():
                        rect = layout.blockBoundingRect(block)
                    
                        # Skip empty or invisible blocks
                        if rect.height() < 1:
                            block = block.next()
                            continue
                        
                        # Get block geometry
                        block_top = rect.y() - margin_offset
                        block_bottom = rect.bottom() - margin_offset
                        block_height = rect.height()
                        
                        # Determine which page this block starts on
                        page_num = int(block_top / cycle)
                        
                        # Position within the current cycle (0 = start of page)
                        local_top = block_top - (page_num * cycle)
                        local_bottom = block_bottom - (page_num * cycle)
                        
                        # Get current block format
                        fmt = block.blockFormat()
                        current_margin = fmt.topMargin()
                        # Deterministic boolean read (QVariant can return None/0/False)
                        is_paginated = fmt.property(PAGINATION_PROP) is True
                        orig_margin = fmt.property(PAGINATION_ORIG_PROP)
                        
                        # Check if block would cross into the gap or next page
                        needs_push = False
                        
                        # Case 1: Block starts in the gap
                        if local_top >= page_height:
                            needs_push = True
                            
                        # Case 2: Block starts on page but extends into gap
                        elif local_bottom > page_height and block_height < page_height:
                            # Only push if block is smaller than a page
                            # (Large blocks like images are allowed to overflow)
                            needs_push = True
                        
                        if needs_push:
                            # Calculate how much to push
                            # We want to move the block to the start of the next page
                            next_page_start = (page_num + 1) * cycle
                            margin_needed = next_page_start - block_top
                            
                            # Idempotent guard: skip if already in perfect paginated state
                            already_correct = (
                                is_paginated and
                                abs(current_margin - margin_needed) <= 1 and
                                orig_margin is not None
                            )
                            if already_correct:
                                block = block.next()
                                continue
                            
                            # Apply pagination margin
                            if not is_paginated:
                                fmt.setProperty(PAGINATION_ORIG_PROP, current_margin)
                            fmt.setTopMargin(margin_needed)
                            fmt.setProperty(PAGINATION_PROP, True)
                            edit_cursor.setPosition(block.position())
                            edit_cursor.setBlockFormat(fmt)
                            changed = True
                        else:
                            # Reset margin if block no longer needs push
                            # Only reset if WE previously set this margin (check our property)
                            if is_paginated:
                                restore_margin = 0.0
                                if orig_margin is not None:
                                    try:
                                        restore_margin = float(orig_margin)
                                    except Exception:
                                        restore_margin = 0.0
                                
                                # Idempotent guard: skip if already restored
                                if abs(current_margin - restore_margin) <= 1:
                                    # Margin already correct, just clear properties
                                    fmt.clearProperty(PAGINATION_PROP)
                                    fmt.clearProperty(PAGINATION_ORIG_PROP)
                                else:
                                    fmt.setTopMargin(restore_margin)
                                    fmt.clearProperty(PAGINATION_PROP)
                                    fmt.clearProperty(PAGINATION_ORIG_PROP)
                                edit_cursor.setPosition(block.position())
                                edit_cursor.setBlockFormat(fmt)
                                changed = True
                        
                        block = block.next()
                finally:
                    edit_cursor.endEditBlock()
            finally:
                # Restore undo/redo state
                doc.setUndoRedoEnabled(undo_enabled)
                if changed:
                    # Advance sovereign generation counter
                    self._pagination_generation += 1
                    # Restore scroll using anchor (semantic) or fallback to raw position
                    if scrollbar is not None:
                        restored = False
                        if getattr(self, "scroll_anchor_enabled", True) and anchor_pos is not None:
                            new_scroll = self._calculate_anchor_scroll_by_pos(anchor_pos, anchor_offset)
                            if new_scroll is not None:
                                # Clamp to current scrollbar range (min and max may shift after reflow)
                                clamped = max(scrollbar.minimum(), min(new_scroll, scrollbar.maximum()))
                                scrollbar.setValue(clamped)
                                restored = True
                        if not restored and saved_scroll is not None:
                            # Fallback also clamped for safety
                            clamped = max(scrollbar.minimum(), min(saved_scroll, scrollbar.maximum()))
                            scrollbar.setValue(clamped)
                
                # Always update seen generation (whether changed or not, to avoid re-running)
                self._last_paginated_generation = self._pagination_generation
                
        finally:
            self._is_paginating = False
    
    @property
    def page_height(self) -> int:
        """
        The effective content height per page in pixels.
        
        Derived from page settings (paper size minus margins). Used as the
        single source of truth for pagination calculations and page break rendering.
        
        Returns:
            Page content height in pixels.
        """
        return self._page_settings.content_height_pixels
    
    @property
    def show_page_breaks(self) -> bool:
        """
        Whether visual page break indicators are displayed.
        
        When True, dashed horizontal lines and page numbers are painted
        at page boundaries during the paint event.
        
        Returns:
            True if page break lines are visible.
        """
        return self._show_page_breaks
    
    @show_page_breaks.setter
    def show_page_breaks(self, value: bool) -> None:
        """
        Toggle visibility of page break indicators.
        
        Args:
            value: True to show dashed page break lines, False to hide them.
        """
        self._show_page_breaks = value
        viewport = self.viewport()
        if viewport:
            viewport.update()
    
    def paintEvent(self, e: Optional[QPaintEvent]) -> None:  # type: ignore[override]
        """Paint the text, then overlay visible page break lines and gap fills."""
        super().paintEvent(e)

        if not self._show_page_breaks:
            return

        from PyQt6.QtGui import QPainter, QPen, QBrush
        from PyQt6.QtCore import QRectF

        viewport = self.viewport()
        if viewport is None:
            return

        scrollbar = self.verticalScrollBar()
        if scrollbar is None:
            return

        doc = self.document()
        if doc is None:
            return

        painter = QPainter(viewport)

        # Define gap fill color (subtle semi-transparent shade)
        gap_fill_color = QColor("#e2e8f0")  # Soft slate-200
        gap_fill_color.setAlpha(80)  # Semi-transparent
        gap_brush = QBrush(gap_fill_color)

        # Dashed line pen for break markers
        pen = QPen(QColor("#94a3b8"))
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setWidth(1)

        scroll_y = scrollbar.value()
        viewport_height = viewport.height()

        page_height = self.page_height
        cycle = page_height + self._page_gap
        if cycle <= 0:
            painter.end()
            return

        doc_height = doc.size().height()

        # Draw only visible page breaks (small padded window)
        pad = 20
        first_page = max(0, int((scroll_y - pad) / cycle))
        last_page = int((scroll_y + viewport_height + pad) / cycle) + 2
        max_page = int(doc_height / cycle) + 2
        last_page = min(last_page, max_page)

        for page in range(first_page, last_page):
            if page <= 0:
                continue

            # Gap region: from break_y to break_y + _page_gap
            break_y = page * cycle - self._page_gap
            gap_start_viewport = break_y - scroll_y
            gap_end_viewport = gap_start_viewport + self._page_gap

            # Fill the gap region with subtle background
            if gap_end_viewport > -10 and gap_start_viewport < viewport_height + 10:
                gap_rect = QRectF(0, gap_start_viewport, viewport.width(), self._page_gap)
                painter.fillRect(gap_rect, gap_brush)
                
                # Draw dashed line at the top of the gap (page break marker)
                painter.setPen(pen)
                painter.drawLine(10, int(gap_start_viewport), viewport.width() - 10, int(gap_start_viewport))
                painter.drawText(15, int(gap_start_viewport) - 5, f"─ Page {page + 1} ─")

        painter.end()
    
    def loadResource(self, type: int, name: QUrl) -> Any:  # type: ignore[override]
        """
        Handle custom resource loading, specifically for docimg:// protocol.

        The docimg:// protocol enables database-backed image persistence without
        embedding large base64 payloads in HTML. Images are stored once in the
        database and referenced by ID.

        URL Formats Supported:
            docimg://123      → Load image with ID 123 (Qt parses as IP 0.0.0.123)
            docimg:///123     → Also accepted (triple slash, ID in path)
            docimg://mermaid/uuid → Special handling for Mermaid diagrams

        Backend Integration:
            Calls self.resource_provider(image_id) to fetch (bytes, mime_type) tuple
            from the database. The resource_provider callback must be set by the
            parent window (e.g., DocumentEditorWindow._fetch_image_resource).

        Caching:
            LRU cache with 32-image limit to avoid repeated database queries.
            Cache entries moved to end on access (OrderedDict FIFO eviction).

        Security:
            - Image IDs must be positive integers (1 to 2^31-1)
            - Images larger than 25MB are rejected with warning
            - Invalid URLs fall back to Qt's default resource loader

        Returns:
            QImage if found in cache or loaded from provider, otherwise None.
            Qt displays a broken image icon when None is returned.

        Example:
            # In HTML: <img src="docimg://42" />
            # This method loads image ID 42 from database via resource_provider
        """
        if name.scheme() == "docimg":
            # Check for mermaid, math, or other named resources
            # Accessing url.path() might return /mermaid/uuid or /math/uuid
            url_str = name.toString()
            if "mermaid" in url_str or "math" in url_str:
                # These resources should have been pre-rendered by setHtml()
                # or added by feature modules during initial insertion
                return super().loadResource(type, name)

            try:
                # Extract image ID
                path = name.path().strip('/')
                host = name.host()
                
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
                    logger.warning(f"Failed to parse image ID from url: {name.toString()}")
                    return super().loadResource(type, name)
                if image_id < 1 or image_id > 2_147_483_647:
                    logger.warning(f"docimg id out of range: {image_id}")
                    return super().loadResource(type, name)

                # Cache lookup
                cache = self._docimg_cache
                if image_id in cache:
                    cached = cache.pop(image_id)
                    cache[image_id] = cached  # move to end
                    return cached

                # Use external resource provider if available
                # This decouples the editor from the document manager pillar
                if hasattr(self, 'resource_provider') and self.resource_provider:
                    result = self.resource_provider(image_id)
                    if result:
                        data, mime_type = result
                        if len(data) > 25 * 1024 * 1024:
                            logger.warning(f"docimg {image_id} rejected: payload too large ({len(data)} bytes)")
                            return super().loadResource(type, name)
                        from PyQt6.QtGui import QImage
                        image = QImage()
                        image.loadFromData(data)
                        cache[image_id] = image
                        if len(cache) > 32:
                            cache.popitem(last=False)
                        return image
                else:
                    # Fallback or error logging if no provider
                    logger.debug(f"No resource provider available for docimg://{image_id}")
                    
            except Exception as e:
                logger.error(f"Failed to load image resource {name.toString()}: {e}")
        
        return super().loadResource(type, name)

    def setHtml(self, html: str) -> None:  # type: ignore[override]
        """
        Override setHtml to pre-render math and mermaid images from alt text.

        When loading HTML that contains docimg://math/ or docimg://mermaid/ images,
        we extract the LaTeX/Mermaid source code from the alt attribute and re-render
        the images, adding them back to the document's resource cache.
        """
        import re

        print("\n=== setHtml: Scanning for math/mermaid images ===")

        # First, scan HTML for math/mermaid images and extract their source
        # Pattern: <img ...> with attributes in any order
        img_pattern = re.compile(r'<img\s+([^>]+)>', re.IGNORECASE)

        for match in img_pattern.finditer(html):
            img_attrs = match.group(1)

            # Extract src and alt from attributes (order-independent)
            src_match = re.search(r'src="(docimg://(?:math|mermaid)/[^"]+)"', img_attrs, re.IGNORECASE)
            alt_match = re.search(r'alt="([^"]*)"', img_attrs, re.IGNORECASE)

            if not src_match:
                continue

            img_url = src_match.group(1)
            alt_text = alt_match.group(1) if alt_match else ""

            print(f"\nFound image: {img_url}")
            print(f"Alt text: {alt_text[:100] if alt_text else 'None'}...")

            if alt_text:
                # Re-render based on type
                if "math" in img_url and alt_text.startswith("LATEX:"):
                    code = alt_text[6:]  # Remove "LATEX:" prefix
                    # Unescape HTML entities
                    code = html_module.unescape(code)
                    print(f"Re-rendering LaTeX: {code[:100]}...")

                    try:
                        from .math_renderer import MathRenderer
                        image = MathRenderer.render_latex(code)
                        if image:
                            print(f"  LaTeX image size: {image.width()}x{image.height()}")
                            # Add to document resources BEFORE setHtml
                            self.document().addResource(
                                QTextDocument.ResourceType.ImageResource,
                                QUrl(img_url),
                                image
                            )
                            print(f"✓ LaTeX image cached: {img_url}")
                        else:
                            print(f"✗ LaTeX render returned None")
                    except Exception as e:
                        print(f"✗ Failed to render LaTeX: {e}")
                        import traceback
                        traceback.print_exc()

                elif "mermaid" in img_url and alt_text.startswith("MERMAID:"):
                    code = alt_text[8:]  # Remove "MERMAID:" prefix
                    code = html_module.unescape(code)
                    print(f"Re-rendering Mermaid: {code[:100]}...")

                    try:
                        from .webview_mermaid_renderer import WebViewMermaidRenderer
                        image = WebViewMermaidRenderer.render_mermaid(code)
                        if image:
                            print(f"  Mermaid image size: {image.width()}x{image.height()}")
                            # Add to document resources BEFORE setHtml
                            self.document().addResource(
                                QTextDocument.ResourceType.ImageResource,
                                QUrl(img_url),
                                image
                            )
                            print(f"✓ Mermaid image cached: {img_url}")
                        else:
                            print(f"✗ Mermaid render returned None")
                    except Exception as e:
                        print(f"✗ Failed to render Mermaid: {e}")
                        import traceback
                        traceback.print_exc()

        # Now load the HTML with images pre-cached
        super().setHtml(html)

    def insertFromMimeData(self, source: Optional[QMimeData]) -> None:  # type: ignore[override]
        """Override paste behavior to protect against freezing."""
        if source is None:
            return
        # Thresholds
        TEXT_WARN = 100000  # approx 20-30 pages of text
        HTML_WARN = 75000   # large HTML payload warning
        MAX_IMAGE_PIXELS = 12_000_000  # ~12 MP
        MAX_IMAGE_BYTES = 12 * 1024 * 1024  # 12 MB
        
        if source.hasText():
            text = source.text()
            if len(text) > TEXT_WARN:
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

        if source.hasHtml():
            html_payload = source.html()
            if len(html_payload) > HTML_WARN:
                reply = QMessageBox.warning(
                    self,
                    "Large HTML Paste",
                    f"The HTML content is {len(html_payload):,} characters.\n"
                    "This may be slow to render. Paste anyway?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            if "data:image" in html_payload and "base64," in html_payload:
                marker = html_payload.find("base64,")
                b64_fragment = html_payload[marker + 7:]
                terminators = [b64_fragment.find(t) for t in ('"', "'", ')', '>') if b64_fragment.find(t) != -1]
                end_idx = min(terminators) if terminators else len(b64_fragment)
                b64_data = b64_fragment[:end_idx]
                approx_bytes = int(len(b64_data) * 0.75)
                if approx_bytes > MAX_IMAGE_BYTES:
                    reply = QMessageBox.warning(
                        self,
                        "Large Data URI Image",
                        f"Embedded data URI image is ~{approx_bytes/1024/1024:.1f} MB.\n"
                        "This may slow the editor. Paste anyway?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.No:
                        return

        if source.hasImage():
            try:
                img = source.imageData()
            except Exception:
                img = None
            if img is not None and hasattr(img, 'size'):
                size = img.size()
                pixel_count = size.width() * size.height()
                approx_bytes = pixel_count * 4
                if pixel_count > MAX_IMAGE_PIXELS or approx_bytes > MAX_IMAGE_BYTES:
                    reply = QMessageBox.warning(
                        self,
                        "Large Image Paste",
                        f"The image is {size.width()}×{size.height()} (~{approx_bytes/1024/1024:.1f} MB).\n"
                        "This may slow the editor. Paste anyway?",
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
        Initialize the rich text editor with ribbon UI and feature modules.
        
        Creates a SafeTextEdit as the core editing surface, optionally wrapped
        with a full ribbon interface (Home, Insert, Page Layout, Reference tabs)
        and status bar with word count and zoom controls.
        
        Args:
            parent: Parent widget for Qt ownership hierarchy.
            placeholder_text: Placeholder shown when editor is empty.
            show_ui: If False, creates a headless editor without ribbon/status bar
                     (useful for testing or embedding in custom layouts).
        """
        super().__init__(parent)
        self.virtual_keyboard: VirtualKeyboard | None = None
        self.page_count_label: QLabel | None = None
        self.word_count_label: QLabel | None = None
        
        # Styles Definition
        self.styles = {
            "Normal": {"size": 12, "weight": QFont.Weight.Normal, "family": "Arial"},
            "Title": {"size": 28, "weight": QFont.Weight.Bold, "family": "Arial"},
            "Heading 1": {"size": 24, "weight": QFont.Weight.Bold, "family": "Arial"},
            "Heading 2": {"size": 18, "weight": QFont.Weight.Bold, "family": "Arial"},
            "Heading 3": {"size": 14, "weight": QFont.Weight.Bold, "family": "Arial"},
            "Code": {"size": 10, "weight": QFont.Weight.Normal, "family": "Courier New"},
        }
        
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
        self.editor: SafeTextEdit = SafeTextEdit(self)
        self.editor.setPlaceholderText(placeholder_text)
        layout.addWidget(self.editor, 1)  # Stretch to fill
        
        # Ensure features initialized
        self._ensure_features_initialized()
        
        # Connect editor signals
        self.editor.textChanged.connect(self._update_word_count)
        self.editor.textChanged.connect(self.text_changed.emit)
        self.editor.textChanged.connect(self._check_wiki_link_trigger)
        self.editor.currentCharFormatChanged.connect(self._update_format_widgets)
        self.editor.cursorPositionChanged.connect(lambda: self._update_format_widgets(self.editor.currentCharFormat()))
        self.editor.selectionChanged.connect(lambda: self._update_format_widgets(self.editor.currentCharFormat()))
        
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
            
            # Sync page mode state: combo defaults to PAGED, so activate it
            if hasattr(self, 'page_mode_combo'):
                # Trigger initial mode application
                self._on_page_mode_changed(self.page_mode_combo.currentIndex())
            
            # Update ribbon state to match current format
            self._update_format_widgets(self.editor.currentCharFormat())
            
            # Initial word count
            self._update_word_count()
    
    
    def _show_search_dialog(self):
        """Show search dialog - delegates to public API."""
        self.show_search()
    
    def _show_spell_dialog(self):
        """Show spell check dialog."""
        self._ensure_features_initialized()
        if self.spell_feature:
            self.spell_feature.show_dialog()
    
    # NOTE: Paste protection is handled in SafeTextEdit.insertFromMimeData()
    # Do NOT add insertFromMimeData here - RichTextEditor is a container,
    # not the actual text widget receiving paste events.

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
            if getattr(self, 'image_edit_feature', None):
                self.image_edit_feature.extend_context_menu(menu)
            if hasattr(self, 'etymology_feature') and self.etymology_feature:
                self.etymology_feature.extend_context_menu(menu)
            if hasattr(self, 'math_feature') and self.math_feature:
                self.math_feature.extend_context_menu(menu)
            if hasattr(self, 'mermaid_feature') and self.mermaid_feature:
                self.mermaid_feature.extend_context_menu(menu)
            menu.exec(self.editor.mapToGlobal(pos))

    def _init_features(self) -> None:
        """Initialize feature slots to None. Actual instantiation happens in _ensure_features_initialized().
        
        ARCHITECTURAL NOTE: This is the ONLY place features should be declared.
        _ensure_features_initialized() is the ONLY place features should be instantiated.
        _init_ribbon() should ONLY wire actions to feature methods, never create features.
        """
        # Set all features to None initially (lazy initialization)
        self.etymology_feature = None
        self.list_feature = None
        self.table_feature = None
        self.image_feature = None
        self.search_feature = None
        self.spell_feature = None
        self.math_feature = None
        self.mermaid_feature = None
        self.shape_feature = None  # Vector shapes in documents
        
        # Optional UI collaborators (may be set by external composition)
        self.substrate = None  # Infinite canvas / zoom substrate
        self.action_rtl = None  # RTL toggle action (created in ribbon if present)
    
    def _ensure_features_initialized(self):
        """Lazy initialization of editor-dependent features.
        
        This is the ONLY place where feature objects should be instantiated.
        Called automatically before ribbon init and context menu display.
        """
        if not self.editor:
            return
        
        if not self.etymology_feature:
            self.etymology_feature = EtymologyFeature(self)
        
        if not self.list_feature:
            self.list_feature = ListFeature(self.editor, self)
        
        if not self.table_feature:
            self.table_feature = TableFeature(self.editor, self)
        
        if not getattr(self, 'image_gateway', None):
            self.image_gateway = ImageGateway(
                self.editor,
                resource_saver=getattr(self, 'resource_saver', None),
                resource_provider=getattr(self, 'resource_provider', None)
            )

        if not getattr(self, 'image_insert_feature', None):
            self.image_insert_feature = ImageInsertFeature(self.editor, self, self.image_gateway)

        if not getattr(self, 'image_edit_feature', None):
            self.image_edit_feature = ImageEditFeature(self.editor, self, self.image_gateway)
        
        if not self.search_feature:
            self.search_feature = SearchReplaceFeature(self.editor, self)
        
        if not self.spell_feature:
            self.spell_feature = SpellFeature(self)
        
        if not self.math_feature:
            self.math_feature = MathFeature(self.editor, self)
        
        if not self.mermaid_feature:
            self.mermaid_feature = MermaidFeature(self.editor, self)
        
        if not self.shape_feature:
            self.shape_feature = ShapeFeature(self)

    def show_search(self) -> None:
        """Public API for Global Ribbon."""
        self._ensure_features_initialized()
        if self.search_feature:
            self.search_feature.show_search_dialog()

    def toggle_list(self, style: QTextListFormat.Style) -> None:
        """Public API for Global Ribbon."""
        self._ensure_features_initialized()
        if self.list_feature:
            self.list_feature.toggle_list(style)

    def set_alignment(self, align: Qt.AlignmentFlag) -> None:
        """Public API for Global Ribbon."""
        self.editor.setAlignment(align)

    def insert_table(self, rows: int = 3, cols: int = 3) -> None:
        """Public API for Global Ribbon."""
        self._ensure_features_initialized()
        if self.table_feature:
            self.table_feature.insert_table(rows, cols)

    def insert_image(self) -> None:
        """Public API for Global Ribbon."""
        self._ensure_features_initialized()
        if getattr(self, 'image_insert_feature', None):
            self.image_insert_feature.insert_image()

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
        Toggle strikethrough formatting on the current selection.
        
        Flips the fontStrikeOut property of the current character format.
        Returns focus to the editor after applying.
        """
        self._toggle_strikethrough()

    def toggle_subscript(self) -> None:
        """
        Toggle subscript vertical alignment on the current selection.
        
        Delegates to _toggle_subscript() which handles mutual exclusivity
        with superscript formatting.
        """
        self._toggle_subscript()

    def toggle_superscript(self) -> None:
        """
        Toggle superscript vertical alignment on the current selection.
        
        Delegates to _toggle_superscript() which handles mutual exclusivity
        with subscript formatting.
        """
        self._toggle_superscript()

    def _init_ribbon(self) -> None:
        """Populate the ribbon with tabs and groups."""
        # Ensure features are initialized before wiring ribbon
        self._ensure_features_initialized()
        assert self.list_feature is not None
        assert self.table_feature is not None
        assert self.image_insert_feature is not None
        assert self.image_edit_feature is not None
        assert self.search_feature is not None
        assert self.spell_feature is not None
        assert self.math_feature is not None
        assert self.mermaid_feature is not None
        assert self.shape_feature is not None
        assert self.etymology_feature is not None
        
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
        file_menu.addSeparator()
        file_menu.addAction("Print...", self._print_document)
        file_menu.addAction("Print Preview...", self._print_preview)
        file_menu.addAction("Export PDF...", self._export_pdf)
        file_menu.addSeparator()
        file_menu.addAction("Convert Symbol Font to Greek...", self._convert_document_symbol_font)
        
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
        self.action_bold = QAction("Bold", self)
        self.action_bold.setShortcut(QKeySequence.StandardKey.Bold)
        self.action_bold.setIcon(qta.icon("fa5s.bold", color="#1e293b"))
        self.action_bold.setToolTip("Bold (Ctrl+B)")
        self.action_bold.setCheckable(True)
        self.action_bold.triggered.connect(lambda _: self._toggle_bold())
        self.addAction(self.action_bold)

        self.btn_bold = QToolButton()
        self.btn_bold.setDefaultAction(self.action_bold)
        self.btn_bold.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_bold.setStyleSheet("""
            QToolButton:checked {
                background-color: #bfdbfe;
                border: 1px solid #3b82f6;
            }
        """)
        grp_basic.add_widget(self.btn_bold)
        
        # Italic
        self.action_italic = QAction("Italic", self)
        self.action_italic.setShortcut(QKeySequence.StandardKey.Italic)
        self.action_italic.setIcon(qta.icon("fa5s.italic", color="#1e293b"))
        self.action_italic.setToolTip("Italic (Ctrl+I)")
        self.action_italic.setCheckable(True)
        self.action_italic.triggered.connect(lambda checked: (self.editor.setFontItalic(checked), self.editor.setFocus()))
        self.addAction(self.action_italic)

        self.btn_italic = QToolButton()
        self.btn_italic.setDefaultAction(self.action_italic)
        self.btn_italic.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_italic.setStyleSheet("""
            QToolButton:checked {
                background-color: #bfdbfe;
                border: 1px solid #3b82f6;
            }
        """)
        grp_basic.add_widget(self.btn_italic)

        # Underline
        self.action_underline = QAction("Underline", self)
        self.action_underline.setShortcut(QKeySequence.StandardKey.Underline)
        self.action_underline.setIcon(qta.icon("fa5s.underline", color="#1e293b"))
        self.action_underline.setToolTip("Underline (Ctrl+U)")
        self.action_underline.setCheckable(True)
        self.action_underline.triggered.connect(lambda checked: (self.editor.setFontUnderline(checked), self.editor.setFocus()))
        self.addAction(self.action_underline)

        self.btn_underline = QToolButton()
        self.btn_underline.setDefaultAction(self.action_underline)
        self.btn_underline.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_underline.setStyleSheet("""
            QToolButton:checked {
                background-color: #bfdbfe;
                border: 1px solid #3b82f6;
            }
        """)
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
        self.action_sub.setShortcut(QKeySequence("Ctrl+="))
        self.action_sub.setToolTip("Subscript (Ctrl+=)")
        self.action_sub.toggled.connect(self._toggle_subscript)
        self.action_sub.setIcon(qta.icon("fa5s.subscript", color="#1e293b"))
        self.addAction(self.action_sub)
        # Mirror bold/italic/underline button styling so checked state is visible
        self.btn_sub = QToolButton()
        self.btn_sub.setDefaultAction(self.action_sub)
        self.btn_sub.setCheckable(True)
        self.btn_sub.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_sub.setStyleSheet("""
            QToolButton:checked {
                background-color: #bfdbfe;
                border: 1px solid #3b82f6;
            }
        """)
        grp_adv.add_widget(self.btn_sub)

        # Superscript
        self.action_super = QAction("", self)
        self.action_super.setCheckable(True)
        self.action_super.setShortcut(QKeySequence("Ctrl+Shift+="))
        self.action_super.setToolTip("Superscript (Ctrl+Shift+=)")
        self.action_super.toggled.connect(self._toggle_superscript)
        self.action_super.setIcon(qta.icon("fa5s.superscript", color="#1e293b"))
        self.addAction(self.action_super)

        self.btn_super = QToolButton()
        self.btn_super.setDefaultAction(self.action_super)
        self.btn_super.setCheckable(True)
        self.btn_super.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_super.setStyleSheet("""
            QToolButton:checked {
                background-color: #bfdbfe;
                border: 1px solid #3b82f6;
            }
        """)
        grp_adv.add_widget(self.btn_super)
        
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
        lf = self.list_feature
        assert lf is not None
        
        self.bullet_btn = QToolButton()
        self.bullet_btn.setIcon(qta.icon("fa5s.list-ul", color="#1e293b"))
        self.bullet_btn.setToolTip("Bullet List")
        self.bullet_btn.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self.bullet_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.bullet_btn.clicked.connect(lambda: self._toggle_list(QTextListFormat.Style.ListDisc))
        
        bullet_menu = QMenu(self)
        for name in BULLET_STYLES:
            act = bullet_menu.addAction(name)
            if act is None:
                continue
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
            if act is None:
                continue
            style = LIST_STYLES[name]
            act.triggered.connect(lambda checked, s=style: self._toggle_list(s))
        number_menu.addSeparator()
        act_start = number_menu.addAction("Set Start Number...")
        if act_start:
            act_start.triggered.connect(lambda lf=lf: lf.show_start_number_dialog())
        self.number_btn.setMenu(number_menu)
        grp_lists.add_widget(self.number_btn)
        
        # Checklist Button
        act_checklist = QAction(qta.icon("fa5s.check-square", color="#1e293b"), "Checklist", self)
        act_checklist.setToolTip("Toggle Checklist")
        act_checklist.triggered.connect(lambda lf=lf: lf.toggle_checklist())
        grp_lists.add_action(act_checklist, Qt.ToolButtonStyle.ToolButtonIconOnly)
        
        # Indent/Outdent
        act_indent = QAction(qta.icon("fa5s.indent", color="#1e293b"), "Increase Indent", self)
        act_indent.triggered.connect(lambda lf=lf: lf.indent())
        grp_lists.add_action(act_indent, Qt.ToolButtonStyle.ToolButtonIconOnly)
        
        act_outdent = QAction(qta.icon("fa5s.outdent", color="#1e293b"), "Decrease Indent", self)
        act_outdent.triggered.connect(lambda lf=lf: lf.outdent())
        grp_lists.add_action(act_outdent, Qt.ToolButtonStyle.ToolButtonIconOnly)
        
        # Remove List
        act_remove_list = QAction(qta.icon("fa5s.times-circle", color="#dc2626"), "Remove List", self)
        act_remove_list.triggered.connect(lambda lf=lf: lf.remove_list())
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
        sf = self.search_feature
        assert sf is not None
        action_replace.triggered.connect(lambda checked, sf=sf: sf.show_search_dialog())
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
        # NOTE: Features are initialized via _ensure_features_initialized(), not here
        grp_tables = tab_insert.add_group("Tables")
        grp_tables.add_widget(self.table_feature.create_toolbar_button())
        
        # Group: Illustrations
        grp_illus = tab_insert.add_group("Illustrations")
        grp_illus.add_action(self.image_insert_feature.create_toolbar_action(), Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # Shapes
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
        mf = self.math_feature
        if mf:
            grp_math.add_action(mf.action_insert_math, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            grp_math.add_action(mf.action_render_doc, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        # Group: Diagrams
        grp_diag = tab_insert.add_group("Diagrams")
        mer = self.mermaid_feature
        if mer:
            grp_diag.add_action(mer.action_insert_mermaid, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            grp_diag.add_action(mer.action_render_doc, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

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
        
        # Page Mode Dropdown (replacing simple toggle)
        self.page_mode_combo = QComboBox()
        self.page_mode_combo.setToolTip("Select Page View Mode")
        self.page_mode_combo.addItem("Freeflow (Fast)", PageMode.FREEFLOW)
        self.page_mode_combo.addItem("Guides Only", PageMode.GUIDES_ONLY)
        self.page_mode_combo.addItem("Enforce Only", PageMode.ENFORCE_ONLY)
        self.page_mode_combo.addItem("Paged Mode", PageMode.PAGED)
        self.page_mode_combo.insertSeparator(4)
        self.page_mode_combo.addItem("Advanced...", PageMode.CUSTOM)
        
        # Select Paged Mode by default (to match previous default)
        self.page_mode_combo.setCurrentIndex(3)
        
        self.page_mode_combo.currentIndexChanged.connect(self._on_page_mode_changed)
        grp_view.add_widget(self.page_mode_combo)

        # =========================================================================
        # TAB: REFERENCE
        # =========================================================================
        tab_ref = self.ribbon.add_ribbon_tab("Reference")
        
        # Group: Language
        grp_lang = tab_ref.add_group("Language")
        
        # Use existing etymology_feature instance (created in _setup_ui)
        ety = self.etymology_feature
        assert ety is not None
        grp_lang.add_action(ety.create_action(self), Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        # Group: Proofing
        grp_proof = tab_ref.add_group("Proofing")
        
        # Spell Check button
        sp = self.spell_feature
        assert sp is not None
        grp_proof.add_action(sp.create_ribbon_action(self), Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # Spell Check toggle
        grp_proof.add_action(sp.create_toggle_action(self), Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        # =========================================================================
        # CONTEXT CATEGORIES
        # =========================================================================
        
        # === CONTEXT CATEGORY: Table Tools ===
        self.ctx_table = self.ribbon.add_context_category("Table Tools", Qt.GlobalColor.darkYellow)
        tf = self.table_feature
        assert tf is not None
        
        # Layout Group - Insert/Delete
        grp_tbl_layout = self.ctx_table.add_group("Layout")
        
        act_ins_row = QAction(qta.icon("fa5s.plus", color="#1e293b"), "Insert Row", self)
        act_ins_row.triggered.connect(lambda tf=tf: tf._insert_row_below())
        grp_tbl_layout.add_action(act_ins_row, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_ins_col = QAction(qta.icon("fa5s.plus", color="#1e293b"), "Insert Col", self)
        act_ins_col.triggered.connect(lambda tf=tf: tf._insert_col_right())
        grp_tbl_layout.add_action(act_ins_col, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        grp_tbl_layout.add_separator()
        
        act_del_row = QAction(qta.icon("fa5s.minus", color="#dc2626"), "Delete Row", self)
        act_del_row.triggered.connect(lambda tf=tf: tf._delete_row())
        grp_tbl_layout.add_action(act_del_row, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_del_col = QAction(qta.icon("fa5s.minus", color="#dc2626"), "Delete Col", self)
        act_del_col.triggered.connect(lambda tf=tf: tf._delete_col())
        grp_tbl_layout.add_action(act_del_col, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_del_table = QAction(qta.icon("fa5s.trash", color="#dc2626"), "Delete Table", self)
        act_del_table.triggered.connect(lambda tf=tf: tf._delete_table())
        grp_tbl_layout.add_action(act_del_table, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        # Merge/Split Group
        grp_tbl_merge = self.ctx_table.add_group("Merge")
        
        act_merge = QAction(qta.icon("fa5s.object-group", color="#1e293b"), "Merge Cells", self)
        act_merge.triggered.connect(lambda tf=tf: tf._merge_cells())
        grp_tbl_merge.add_action(act_merge, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_split = QAction(qta.icon("fa5s.object-ungroup", color="#1e293b"), "Split Cells", self)
        act_split.triggered.connect(lambda tf=tf: tf._split_cells())
        grp_tbl_merge.add_action(act_split, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_distribute = QAction(qta.icon("fa5s.arrows-alt-h", color="#1e293b"), "Distribute", self)
        act_distribute.triggered.connect(lambda tf=tf: tf._distribute_columns())
        grp_tbl_merge.add_action(act_distribute, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        # Style Group
        grp_tbl_style = self.ctx_table.add_group("Style")
        
        act_cell_bg = QAction(qta.icon("fa5s.fill-drip", color="#1e293b"), "Cell Color", self)
        act_cell_bg.triggered.connect(lambda tf=tf: tf._set_cell_background())
        grp_tbl_style.add_action(act_cell_bg, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_cell_border = QAction(qta.icon("fa5s.border-style", color="#1e293b"), "Borders", self)
        act_cell_border.triggered.connect(lambda tf=tf: tf._edit_cell_borders())
        grp_tbl_style.add_action(act_cell_border, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_cell_props = QAction(qta.icon("fa5s.sliders-h", color="#1e293b"), "Cell Props", self)
        act_cell_props.triggered.connect(lambda tf=tf: tf._edit_cell_properties())
        grp_tbl_style.add_action(act_cell_props, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        act_table_props = QAction(qta.icon("fa5s.cog", color="#1e293b"), "Table Props", self)
        act_table_props.triggered.connect(lambda tf=tf: tf._edit_table_properties())
        grp_tbl_style.add_action(act_table_props, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        # === CONTEXT CATEGORY: Image Tools ===
        self.ctx_image = self.ribbon.add_context_category("Image Tools", Qt.GlobalColor.magenta)
        
        # Tools Group
        grp_img_tools = self.ctx_image.add_group("Tools")
        
        if getattr(self, 'image_edit_feature', None):
            # Edit Action (Crop/Filter/Rotate)
            if hasattr(self.image_edit_feature, 'action_edit'):
                grp_img_tools.add_action(self.image_edit_feature.action_edit, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            
            # Properties Action
            if hasattr(self.image_edit_feature, 'action_props'):
                grp_img_tools.add_action(self.image_edit_feature.action_props, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
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

    
    # NOTE: insert_hyperlink() and insert_horizontal_rule() public methods were removed.
    # The ribbon uses _insert_hyperlink() and _insert_horizontal_rule() which have
    # more robust implementations (URL scheme validation, dialog-based HR options).

    def page_setup(self) -> None:
        """Open page setup dialog."""
        dlg = PageSetupDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            # Apply settings (Mock implementation as SafeTextEdit is a Widget, not a full document layout engine)
            # In a real app we'd set document root frame margins or print settings
            pass
    
    # NOTE: Color/highlight/spacing/direction methods are defined later in file
    # with more robust implementations (non-native dialogs, better UX).
    # Do NOT add simple versions here - they will silently override the better ones.

    def _toggle_list(self, style: QTextListFormat.Style) -> None:
        """Wrapper for list feature."""
        self._ensure_features_initialized()
        if self.list_feature:
            self.list_feature.toggle_list(style)
        self.editor.setFocus()

    def _insert_page_break(self) -> None:
        """
        Insert a sovereign page break marker.
        
        Uses a custom block property (PAGEBREAK_PROP) to mark the block as a 
        dedicated page break. This is immutable in the sense that the property
        persists with the block and can be detected/preserved during export.
        The visual is a minimal empty block with distinctive formatting.
        """
        cursor = self.editor.textCursor()
        
        # Insert a new block for the page break
        cursor.insertBlock()
        
        # Configure the block format with page break property
        block_fmt = cursor.blockFormat()
        block_fmt.setProperty(PAGEBREAK_PROP, True)
        block_fmt.setTopMargin(0)
        block_fmt.setBottomMargin(0)
        # Set fixed height to create a visible but minimal break line
        block_fmt.setLineHeight(1, QTextBlockFormat.LineHeightTypes.FixedHeight)
        block_fmt.setBackground(QBrush(QColor("#64748b")))  # Slate-500 for visibility
        cursor.setBlockFormat(block_fmt)
        
        # Insert a minimal content marker (non-breaking space) to ensure block persists
        cursor.insertText("\u00A0")  # NBSP
        
        # Move past the break and insert a new normal block
        cursor.insertBlock()
        # Clear the page break property on the new block
        normal_fmt = QTextBlockFormat()
        normal_fmt.clearProperty(PAGEBREAK_PROP)
        cursor.setBlockFormat(normal_fmt)
        
        self.editor.setTextCursor(cursor)
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

    def _toggle_subscript(self, checked: Optional[bool] = None) -> None:
        """Toggle subscript; uncheck superscript when enabled."""
        # If invoked programmatically without a state, flip the action to drive consistency
        if checked is None and hasattr(self, 'action_sub') and self.action_sub:
            checked = not self.action_sub.isChecked()
            self.action_sub.setChecked(checked)
            return

        fmt = self.editor.currentCharFormat()
        if checked:
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSubScript)
            if hasattr(self, 'action_super') and self.action_super:
                self.action_super.blockSignals(True)
                self.action_super.setChecked(False)
                self.action_super.blockSignals(False)
        else:
            if fmt.verticalAlignment() == QTextCharFormat.VerticalAlignment.AlignSubScript:
                fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignNormal)
        self.editor.mergeCurrentCharFormat(fmt)
        # Force UI sync because Qt may not emit currentCharFormatChanged for verticalAlignment changes
        self._update_format_widgets(self.editor.currentCharFormat())
        self.editor.setFocus()

    def _toggle_superscript(self, checked: Optional[bool] = None) -> None:
        """Toggle superscript; uncheck subscript when enabled."""
        if checked is None and hasattr(self, 'action_super') and self.action_super:
            checked = not self.action_super.isChecked()
            self.action_super.setChecked(checked)
            return

        fmt = self.editor.currentCharFormat()
        if checked:
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSuperScript)
            if hasattr(self, 'action_sub') and self.action_sub:
                self.action_sub.blockSignals(True)
                self.action_sub.setChecked(False)
                self.action_sub.blockSignals(False)
        else:
            if fmt.verticalAlignment() == QTextCharFormat.VerticalAlignment.AlignSuperScript:
                fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignNormal)
        self.editor.mergeCurrentCharFormat(fmt)
        # Force UI sync because Qt may not emit currentCharFormatChanged for verticalAlignment changes
        self._update_format_widgets(self.editor.currentCharFormat())
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
            
            # Reset Color - use QBrush for type safety
            fmt.setForeground(QBrush(QColor(Qt.GlobalColor.black)))
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
        current_qcolor = QColor(current_color)
        initial_color: QColor | Qt.GlobalColor = current_qcolor
        if current_qcolor.lightness() == 0:
            initial_color = QColor(Qt.GlobalColor.red)
            
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
        """
        Apply a semantic style to the current selection/block.
        
        Uses direct format merging instead of HTML insertion to preserve
        document structure (lists, tables, images) while applying styling.
        """
        if style_name not in self.styles:
            return
            
        style = self.styles[style_name]
        cursor = self.editor.textCursor()
        
        # If no selection, apply to the entire block (paragraph)
        if not cursor.hasSelection():
            cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        
        # Apply character formatting via merge (preserves structure)
        char_fmt = QTextCharFormat()
        char_fmt.setFont(QFont(style["family"], style["size"], style["weight"]))
        cursor.mergeCharFormat(char_fmt)
        
        # Apply block formatting for headings/titles (margins)
        if style_name.startswith("Heading") or style_name == "Title":
            block_fmt = cursor.blockFormat()
            block_fmt.setTopMargin(10)
            block_fmt.setBottomMargin(5)
            cursor.setBlockFormat(block_fmt)
        
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()
        
        # Update combo boxes to reflect the change visually in toolbar
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
        """Clear the background highlight without leaving sticky format state."""
        from PyQt6.QtGui import QTextCharFormat, QBrush
        fmt = QTextCharFormat()
        fmt.setBackground(QBrush(Qt.BrushStyle.NoBrush))
        self.editor.mergeCurrentCharFormat(fmt)
        self.editor.setFocus()

    def _on_zoom_changed(self, value: int):
        """Handle zoom slider change."""
        self.zoom_label.setText(f"{value}%")
        # Delegate zoom to the Substrate (Infinite Canvas)
        # This scales the entire view (Paper + Text)
        if self.substrate:
            self.substrate.set_zoom(value / 100.0)

    def _update_word_count(self) -> None:
        """Update the word and character count in status bar."""
        if not self.word_count_label:
            return
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
        
        # Calculate pages based on document height vs page height plus gap
        doc = self.editor.document()
        if doc is None:
            return
        doc_height = doc.size().height()
        
        page_height = self.editor.page_height
        cycle = page_height + getattr(self.editor, "_page_gap", 0)
        if cycle <= 0:
            return
        self._total_pages = max(1, int((doc_height + cycle - 1) / cycle))
        self._update_page_label()
    
    def _update_current_page(self) -> None:
        """Update current page based on cursor position."""
        if not hasattr(self, 'page_count_label'):
            return
        
        cursor = self.editor.textCursor()
        cursor_rect = self.editor.cursorRect(cursor)
        
        # Calculate which "page" the cursor is on using editor settings and gap
        page_height = self.editor.page_height
        cycle = page_height + getattr(self.editor, "_page_gap", 0)
        scrollbar = self.editor.verticalScrollBar()
        if scrollbar is None or cycle <= 0:
            return
        cursor_y = cursor_rect.top() + scrollbar.value()
        
        self._current_page = max(1, min(int(cursor_y / cycle) + 1, getattr(self, '_total_pages', 1)))
        self._update_page_label()
    
    def _update_page_label(self) -> None:
        """Update the page label text."""
        if hasattr(self, 'page_count_label') and self.page_count_label:
            current = getattr(self, '_current_page', 1)
            total = getattr(self, '_total_pages', 1)
            self.page_count_label.setText(f"Page {current} of {total}")

    def _on_page_mode_changed(self, index: int):
        """Handle page mode selection from ribbon dropdown."""
        mode = self.page_mode_combo.currentData()
        
        if mode == PageMode.CUSTOM:
            # Open advanced options dialog
            current_opts = getattr(self.editor, '_current_page_options', PageModeOptions())
            dialog = PageModeDialog(self, current_opts)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_opts = dialog.get_options()
                self.editor.set_page_mode(PageMode.CUSTOM, new_opts)
            else:
                # Revert combo to previous mode if cancelled
                # (simple approach: revert to Freeflow or just stay on Advanced but don't apply)
                # Better: find the index matching current mode
                current_mode = getattr(self.editor, '_current_page_mode', PageMode.FREEFLOW)
                # Find index for this mode (0-3)
                idx = 0
                if current_mode == PageMode.FREEFLOW: idx = 0
                elif current_mode == PageMode.GUIDES_ONLY: idx = 1
                elif current_mode == PageMode.ENFORCE_ONLY: idx = 2
                elif current_mode == PageMode.PAGED: idx = 3
                # Block signals to avoid loop
                self.page_mode_combo.blockSignals(True)
                self.page_mode_combo.setCurrentIndex(idx)
                self.page_mode_combo.blockSignals(False)
        else:
            # Apply preset directly
            self.editor.set_page_mode(mode)
            
    def _toggle_page_breaks(self, checked: bool):
        # Deprecated: kept for compatibility if called programmatically, syncs UI
        mode = PageMode.PAGED if checked else PageMode.FREEFLOW
        self.editor.set_page_mode(mode)
        # Sync combo
        idx = 3 if checked else 0
        self.page_mode_combo.blockSignals(True)
        self.page_mode_combo.setCurrentIndex(idx)
        self.page_mode_combo.blockSignals(False)

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
        block_fmt.setLineHeight(spacing * 100, QTextBlockFormat.LineHeightTypes.ProportionalHeight)
        cursor.setBlockFormat(block_fmt)

    def _toggle_text_direction(self) -> None:
        """Toggle between LTR and RTL text direction."""
        cursor = self.editor.textCursor()
        block_fmt = cursor.blockFormat()
        
        current_dir = block_fmt.layoutDirection()
        if current_dir == Qt.LayoutDirection.RightToLeft:
            block_fmt.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            if self.action_rtl:
                self.action_rtl.setChecked(False)
        else:
            block_fmt.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            if self.action_rtl:
                self.action_rtl.setChecked(True)
        
        cursor.setBlockFormat(block_fmt)

    def _insert_hyperlink(self) -> None:
        """Insert a hyperlink at the current cursor position without HTML parsing."""
        from PyQt6.QtGui import QTextCharFormat

        cursor = self.editor.textCursor()
        selected_text = cursor.selectedText() if cursor.hasSelection() else ""
        
        dialog = HyperlinkDialog(selected_text, self)
        if not dialog.exec():
            return

        url = dialog.url_input.text().strip()
        display_text = (dialog.text_input.text().strip() or url).strip()
        if not url or not display_text:
            return

        allowed_schemes = ("https://", "mailto:", "note://", "app://")
        if not url.startswith(allowed_schemes):
            QMessageBox.warning(self, "Link", "Unsupported link scheme. Allowed: https, mailto, note://, app://")
            return

        fmt = QTextCharFormat()
        fmt.setAnchor(True)
        fmt.setAnchorHref(url)
        fmt.setFontUnderline(True)
        cursor.insertText(display_text, fmt)

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
            doc = self.editor.document()
            if doc is None:
                return
            doc.print(printer)
            
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
            doc = self.editor.document()
            if doc is None:
                return
            doc.print(printer)

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
        preview.paintRequested.connect(lambda p: self._print_doc_safe(p))
        preview.exec()


    def _print_doc_safe(self, printer: QPrinter) -> None:
        """Print the current document if available."""
        doc = self.editor.document()
        if doc is None:
            return
        doc.print(printer)



    def _show_virtual_keyboard(self) -> None:
        self.virtual_keyboard = get_shared_virtual_keyboard(self)
        self.virtual_keyboard.set_target_editor(self.editor)
        self.virtual_keyboard.show()
        self.virtual_keyboard.raise_()
        self.virtual_keyboard.activateWindow()

    def _update_format_widgets(self, fmt: QTextCharFormat) -> None:
        """Update the ribbon widgets based on the current text format.
        
        Safe to call in headless mode - exits early if ribbon widgets don't exist.
        """
        # Early exit if no ribbon (headless mode)
        if not hasattr(self, 'font_combo') or not self.font_combo:
            return
        if not hasattr(self, 'size_combo') or not self.size_combo:
            return

        # Block signals to prevent triggering changes while updating UI
        self.font_combo.blockSignals(True)
        self.size_combo.blockSignals(True)
        
        # New QToolButtons for styling (may not exist)
        btn_bold = getattr(self, 'btn_bold', None)
        btn_italic = getattr(self, 'btn_italic', None)
        btn_underline = getattr(self, 'btn_underline', None)
        btn_strike = getattr(self, 'btn_strike', None)
        action_bold = getattr(self, 'action_bold', None)
        action_italic = getattr(self, 'action_italic', None)
        action_underline = getattr(self, 'action_underline', None)
        
        if btn_bold: btn_bold.blockSignals(True)
        if btn_italic: btn_italic.blockSignals(True)
        if btn_underline: btn_underline.blockSignals(True)
        if btn_strike: btn_strike.blockSignals(True)
        if action_bold: action_bold.blockSignals(True)
        if action_italic: action_italic.blockSignals(True)
        if action_underline: action_underline.blockSignals(True)
        
        # QActions (may not exist in headless mode)
        action_sub = getattr(self, 'action_sub', None)
        action_super = getattr(self, 'action_super', None)
        action_align_left = getattr(self, 'action_align_left', None)
        action_align_center = getattr(self, 'action_align_center', None)
        action_align_right = getattr(self, 'action_align_right', None)
        action_align_justify = getattr(self, 'action_align_justify', None)
        
        if action_sub: action_sub.blockSignals(True)
        if action_super: action_super.blockSignals(True)
        if action_align_left: action_align_left.blockSignals(True)
        if action_align_center: action_align_center.blockSignals(True)
        if action_align_right: action_align_right.blockSignals(True)
        if action_align_justify: action_align_justify.blockSignals(True)
        
        # Update Font & Size
        self.font_combo.setCurrentFont(fmt.font())
        try:
            current_size = int(fmt.fontPointSize())
            if current_size <= 0:
                current_size = 12  # Default fallback
            self.size_combo.setCurrentText(str(current_size))
        except ValueError as e:
            logger.debug("Font size parsing failed: %s. Keeping current selection.", e)
        
        # Update Styles
        bold_checked = fmt.fontWeight() == QFont.Weight.Bold
        italic_checked = fmt.fontItalic()
        underline_checked = fmt.fontUnderline()

        if action_bold:
            action_bold.setChecked(bold_checked)
        if action_italic:
            action_italic.setChecked(italic_checked)
        if action_underline:
            action_underline.setChecked(underline_checked)

        if btn_bold:
            btn_bold.setChecked(bold_checked)
        if btn_italic:
            btn_italic.setChecked(italic_checked)
        if btn_underline:
            btn_underline.setChecked(underline_checked)
        if btn_strike:
            btn_strike.setChecked(fmt.fontStrikeOut())
        
        # Update Sub/Super
        v_align = fmt.verticalAlignment()
        if action_sub:
            action_sub.setChecked(v_align == QTextCharFormat.VerticalAlignment.AlignSubScript)
        if action_super:
            action_super.setChecked(v_align == QTextCharFormat.VerticalAlignment.AlignSuperScript)
        
        # Update Alignment
        align = self.editor.alignment()
        if action_align_left and (align & Qt.AlignmentFlag.AlignLeft):
            action_align_left.setChecked(True)
        elif action_align_center and (align & Qt.AlignmentFlag.AlignHCenter):
            action_align_center.setChecked(True)
        elif action_align_right and (align & Qt.AlignmentFlag.AlignRight):
            action_align_right.setChecked(True)
        elif action_align_justify and (align & Qt.AlignmentFlag.AlignJustify):
            action_align_justify.setChecked(True)
        
        # Unblock signals
        self.font_combo.blockSignals(False)
        self.size_combo.blockSignals(False)
        
        if btn_bold: btn_bold.blockSignals(False)
        if btn_italic: btn_italic.blockSignals(False)
        if btn_underline: btn_underline.blockSignals(False)
        if btn_strike: btn_strike.blockSignals(False)
        if action_bold: action_bold.blockSignals(False)
        if action_italic: action_italic.blockSignals(False)
        if action_underline: action_underline.blockSignals(False)
        
        if action_sub: action_sub.blockSignals(False)
        if action_super: action_super.blockSignals(False)
        if action_align_left: action_align_left.blockSignals(False)
        if action_align_center: action_align_center.blockSignals(False)
        if action_align_right: action_align_right.blockSignals(False)
        if action_align_justify: action_align_justify.blockSignals(False)
        
    # --- Public API ---
    def set_page_mode(self, mode: PageMode, opts: Optional[PageModeOptions] = None) -> None:
        """
        Set pagination mode with unified control (app-level entry point).
        
        Delegates to SafeTextEdit.set_page_mode() where state is enacted.
        
        Args:
            mode: The PageMode preset to apply
            opts: Optional PageModeOptions for overrides
        """
        self.editor.set_page_mode(mode, opts)
    
    def get_html(self) -> str:
        """
        Export the document content as HTML.
        
        Returns:
            Complete HTML representation including formatting, images, and tables.
        """
        return self.editor.toHtml()
        
    def set_html(self, html: str) -> None:
        """
        Load HTML content into the editor.
        
        Replaces all current content. Forces LTR layout direction after loading
        to prevent auto-detection issues with mixed-direction content.
        
        Args:
            html: HTML string to load (can include images, tables, formatting).
        """
        self.editor.setHtml(html)
        # Ensure LTR is maintained after setting content
        self.editor.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        # Re-render generated assets (Mermaid/LaTeX) that rely on in-memory resources
        self._restore_generated_objects()
        
    def get_text(self) -> str:
        """
        Export the document content as plain text.
        
        Strips all formatting, returning only the text content.
        
        Returns:
            Plain text content without any formatting.
        """
        return self.editor.toPlainText()
        
    def set_text(self, text: str) -> None:
        """
        Load plain text content into the editor.
        
        Replaces all current content. Use set_html or set_markdown for
        formatted content.
        
        Args:
            text: Plain text string to load.
        """
        self.editor.setPlainText(text)

    def set_markdown(self, markdown: str):
        """Set the editor content from Markdown."""
        self.editor.setMarkdown(markdown)
        # Ensure LTR is maintained
        self.editor.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self._restore_generated_objects()

    def get_markdown(self) -> str:
        """Get the editor content as Markdown."""
        doc = self.editor.document()
        if doc is None:
            return ""
        return doc.toMarkdown()
        
    def clear(self) -> None:
        """
        Remove all content from the editor.
        
        Clears text, images, tables, and formatting. Does not prompt for
        unsaved changes (use new_document() for that behavior).
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
        viewport = self.editor.viewport()
        scrollbar = self.editor.verticalScrollBar()
        if viewport is None or scrollbar is None:
            return
        viewport_height = viewport.height()
        # Calculate scroll position to center the cursor
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

    def _restore_generated_objects(self) -> None:
        """Re-render Mermaid/LaTeX images after loading persisted content.

        Saved HTML/Markdown only preserves `docimg://...` URLs plus alt text;
        the in-memory resources are not serialized. On reopen, that yields
        broken glyphs. We walk the document, find image fragments with
        alt-text markers, and re-render them via the feature renderers.
        """
        doc = self.editor.document()
        if doc is None:
            return

        mer = getattr(self, 'mermaid_feature', None)
        mth = getattr(self, 'math_feature', None)
        if mer is None and mth is None:
            return

        # Collect replacement tasks first to avoid iterator invalidation while editing
        tasks: list[tuple[int, str, str]] = []  # (position, kind, code)

        block = doc.begin()
        while block.isValid():
            frag_iter = block.begin()
            while not frag_iter.atEnd():
                frag: QTextFragment = frag_iter.fragment()
                if frag.isValid() and frag.charFormat().isImageFormat():
                    fmt: QTextImageFormat = frag.charFormat().toImageFormat()
                    alt = fmt.property(QTextImageFormat.Property.ImageAltText)
                    if isinstance(alt, str):
                        if mer and alt.startswith(getattr(mer, 'MERMAID_PREFIX', 'MERMAID:')):
                            code = alt[len(mer.MERMAID_PREFIX):]
                            tasks.append((frag.position(), 'mermaid', code))
                        elif mth and alt.startswith(getattr(mth, 'LATEX_PREFIX', 'LATEX:')):
                            code = alt[len(mth.LATEX_PREFIX):]
                            tasks.append((frag.position(), 'latex', code))
                frag_iter += 1
            block = block.next()

        for pos, kind, code in tasks:
            cursor = QTextCursor(doc)
            cursor.setPosition(pos)
            cursor.setPosition(pos + 1, QTextCursor.MoveMode.KeepAnchor)
            try:
                if kind == 'mermaid' and mer:
                    self.editor.setTextCursor(cursor)
                    mer.insert_mermaid(code)
                elif kind == 'latex' and mth:
                    self.editor.setTextCursor(cursor)
                    mth.insert_math(code)
            except Exception as exc:
                logger.warning("Failed to restore %s block: %s", kind, exc)

    def _document_with_embedded_images(self, source: QTextDocument) -> QTextDocument:
        """Clone document and embed images as data URIs so saves round-trip.

        Qt does not persist custom docimg:// resources to disk. Embedding ensures
        Mermaid/LaTeX renders survive reopen without relying on in-memory cache.
        """
        clone = source.clone()
        if clone is None:
            return source

        tasks: list[tuple[int, QTextImageFormat]] = []
        block = clone.begin()
        while block.isValid():
            frag_iter = block.begin()
            while not frag_iter.atEnd():
                frag: QTextFragment = frag_iter.fragment()
                if frag.isValid() and frag.charFormat().isImageFormat():
                    fmt: QTextImageFormat = frag.charFormat().toImageFormat()
                    name = fmt.name()
                    if name:
                        img = clone.resource(QTextDocument.ResourceType.ImageResource, QUrl(name))
                        if hasattr(img, 'save'):
                            buffer = QBuffer()
                            buffer.open(QBuffer.OpenModeFlag.WriteOnly)
                            img.save(buffer, 'PNG')
                            data = bytes(buffer.data())
                            data_uri = "data:image/png;base64," + base64.b64encode(data).decode('ascii')
                            fmt.setName(data_uri)
                            tasks.append((frag.position(), fmt))
                frag_iter += 1
            block = block.next()

        for pos, fmt in tasks:
            cursor = QTextCursor(clone)
            cursor.setPosition(pos)
            cursor.setPosition(pos + 1, QTextCursor.MoveMode.KeepAnchor)
            cursor.setCharFormat(fmt)

        return clone

    def new_document(self) -> None:
        """Clear the editor for a new document."""
        doc = self.editor.document()
        if doc is not None and doc.isModified():
            ans = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Are you sure you want to clear the document?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if ans != QMessageBox.StandardButton.Yes:
                return
        self.editor.clear()

    def open_document(self) -> None:
        """Open a file (Markdown, HTML, Text, DOCX, PDF) with automatic encoding detection."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Document", "",
            "All Supported (*.md *.html *.htm *.txt *.docx *.pdf);;"
            "Markdown (*.md);;"
            "HTML (*.html *.htm);;"
            "Text (*.txt);;"
            "Word Document (*.docx);;"
            "PDF Document (*.pdf);;"
            "All Files (*)"
        )
        if not file_path:
            return

        try:
            # Handle DOCX/PDF files - extract plain text only (case insensitive)
            file_path_lower = file_path.lower()

            if file_path_lower.endswith('.docx'):
                content = self._extract_text_from_docx(file_path)
                if content:
                    self.editor.setPlainText(content)
                    doc = self.editor.document()
                    if doc is not None:
                        doc.setModified(False)
                    QMessageBox.information(
                        self,
                        "DOCX Imported",
                        f"Plain text extracted from {os.path.basename(file_path)}\n"
                        f"(Formatting removed - save as UTF-8 text)"
                    )
                    return
                else:
                    QMessageBox.warning(self, "Error", "Could not extract text from DOCX file")
                    return

            elif file_path_lower.endswith('.pdf'):
                content = self._extract_text_from_pdf(file_path)
                if content:
                    self.editor.setPlainText(content)
                    doc = self.editor.document()
                    if doc is not None:
                        doc.setModified(False)
                    QMessageBox.information(
                        self,
                        "PDF Imported",
                        f"Plain text extracted from {os.path.basename(file_path)}\n"
                        f"(Formatting removed - save as UTF-8 text)"
                    )
                    return
                else:
                    QMessageBox.warning(self, "Error", "Could not extract text from PDF file")
                    return

            # Try multiple encodings for robust file opening (text files)
            content = None
            detected_encoding = None
            encodings_to_try = [
                'utf-8',           # Modern standard
                'utf-8-sig',       # UTF-8 with BOM
                'latin-1',         # ISO-8859-1 (Western European)
                'windows-1252',    # Windows Western European
                'cp1252',          # Alternative name for windows-1252
                'iso-8859-1',      # Alternative name for latin-1
                'ascii',           # Basic ASCII
            ]

            for encoding in encodings_to_try:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    detected_encoding = encoding
                    break
                except (UnicodeDecodeError, LookupError):
                    continue

            if content is None:
                # Last resort: read as binary and try to decode with error handling
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                content = raw_data.decode('utf-8', errors='replace')
                detected_encoding = 'utf-8 (with replacements)'

            # Load content into editor
            if file_path.endswith('.md'):
                self.editor.setMarkdown(content)
            elif file_path.endswith(('.html', '.htm')):
                self.editor.setHtml(content)
            else:
                self.editor.setPlainText(content)

            doc = self.editor.document()
            if doc is not None:
                doc.setModified(False)

            # Notify user if non-UTF-8 encoding was detected
            if detected_encoding and detected_encoding not in ['utf-8', 'utf-8-sig']:
                QMessageBox.information(
                    self,
                    "Encoding Detected",
                    f"File opened with {detected_encoding} encoding.\n"
                    f"When saved, it will be normalized to UTF-8."
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file:\n{e}")

    def save_document(self) -> None:
        """Save the document (Markdown, HTML, Text) - always saves as UTF-8."""
        file_path, filter_used = QFileDialog.getSaveFileName(
            self, "Save Document", "",
            "Markdown (*.md);;HTML (*.html);;Text (*.txt)"
        )
        if not file_path:
            return

        try:
            doc = self.editor.document()
            if doc is None:
                return
            export_doc = self._document_with_embedded_images(doc)

            # Ensure a file extension based on the selected filter; default to .txt for safety.
            base, ext = os.path.splitext(file_path)
            if not ext:
                chosen_ext = ".txt"
                normalized_filter = (filter_used or "").lower()
                if "markdown" in normalized_filter:
                    chosen_ext = ".md"
                elif "html" in normalized_filter:
                    chosen_ext = ".html"
                file_path = f"{file_path}{chosen_ext}"
                ext = chosen_ext
            ext = ext.lower()

            if ext == '.md':
                # Convert to Markdown
                # Note: Qt's toMarkdown features are basic but standard compliant.
                content = export_doc.toMarkdown()
            elif ext == '.html':
                content = export_doc.toHtml()
            else:
                content = self.editor.toPlainText()

            # Always save as UTF-8 for universal compatibility
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            doc.setModified(False)
            QMessageBox.information(
                self,
                "Saved",
                f"Document saved to {os.path.basename(file_path)}\n(UTF-8 encoding)"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")

    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract plain text from DOCX file (no formatting/HTML)."""
        try:
            import docx
            doc = docx.Document(file_path)
            # Extract all paragraph text
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            return '\n\n'.join(paragraphs)
        except ImportError:
            QMessageBox.warning(
                self,
                "Missing Library",
                "python-docx library not installed.\n\n"
                "Install with: pip install python-docx"
            )
            return ""
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            return ""

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract plain text from PDF file using DocumentParser (strips HTML)."""
        try:
            from pathlib import Path
            from shared.services.document_manager.utils.parsers import DocumentParser
            from html.parser import HTMLParser

            # Use your comprehensive parser
            text, html, file_type, metadata = DocumentParser.parse_file(
                Path(file_path),
                high_fidelity=True  # Use best quality extraction
            )

            # Strip HTML tags to get plain text
            class HTMLStripper(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.text_parts = []

                def handle_data(self, data):
                    self.text_parts.append(data)

                def get_text(self):
                    return ''.join(self.text_parts)

            # If we have HTML, strip it to plain text
            if html and html.strip():
                stripper = HTMLStripper()
                stripper.feed(html)
                plain_text = stripper.get_text()
                # Clean up extra whitespace
                lines = [line.strip() for line in plain_text.split('\n') if line.strip()]
                plain_text = '\n\n'.join(lines)

                # Don't auto-convert - let user decide via menu
                return plain_text

            # Fallback to direct text extraction
            return text if text else ""

        except ImportError as e:
            logger.error(f"Missing library for PDF parsing: {e}")
            QMessageBox.warning(
                self,
                "Missing Library",
                f"Required library not installed:\n\n{str(e)}\n\n"
                "Install with: pip install pypdf PyMuPDF pdf2docx mammoth"
            )
            return ""
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "PDF Extraction Error",
                f"Could not extract text from PDF:\n\n{str(e)}"
            )
            return ""

    def _convert_document_symbol_font(self) -> None:
        """Manually convert Symbol font in current document to Unicode Greek."""
        current_text = self.editor.toPlainText()

        if not current_text.strip():
            QMessageBox.information(self, "Empty Document", "Document is empty - nothing to convert.")
            return

        # Show preview and ask for confirmation
        converted_text = self._convert_symbol_font_to_greek_with_prompt(current_text)

        if converted_text != current_text:
            # User confirmed and text was converted
            self.editor.setPlainText(converted_text)
            QMessageBox.information(
                self,
                "Conversion Complete",
                "Symbol font characters converted to Unicode Greek.\n\n"
                "Remember to save the document!"
            )

    def _convert_symbol_font_to_greek_with_prompt(self, text: str) -> str:
        """Convert Symbol font with user prompt (returns original if declined)."""
        # Symbol font to Unicode mapping
        symbol_to_unicode = {
            # Lowercase Greek letters
            'a': 'α', 'b': 'β', 'g': 'γ', 'd': 'δ', 'e': 'ε', 'z': 'ζ',
            'h': 'η', 'q': 'θ', 'i': 'ι', 'k': 'κ', 'l': 'λ', 'm': 'μ',
            'n': 'ν', 'x': 'ξ', 'o': 'ο', 'p': 'π', 'r': 'ρ', 's': 'σ',
            't': 'τ', 'u': 'υ', 'f': 'φ', 'c': 'χ', 'y': 'ψ', 'w': 'ω',

            # Uppercase Greek letters
            'A': 'Α', 'B': 'Β', 'G': 'Γ', 'D': 'Δ', 'E': 'Ε', 'Z': 'Ζ',
            'H': 'Η', 'Q': 'Θ', 'I': 'Ι', 'K': 'Κ', 'L': 'Λ', 'M': 'Μ',
            'N': 'Ν', 'X': 'Ξ', 'O': 'Ο', 'P': 'Π', 'R': 'Ρ', 'S': 'Σ',
            'T': 'Τ', 'U': 'Υ', 'F': 'Φ', 'C': 'Χ', 'Y': 'Ψ', 'W': 'Ω',

            # Special variants
            'j': 'ϕ', 'v': 'ς', 'J': 'ϑ', 'V': 'ϖ',
        }

        # Show preview of what conversion would look like
        preview_length = min(200, len(text))
        preview_text = text[:preview_length]
        preview_converted = ''.join(symbol_to_unicode.get(c, c) for c in preview_text)

        reply = QMessageBox.question(
            self,
            "Convert Symbol Font to Greek",
            f"This will convert ASCII characters to Greek letters.\n\n"
            f"Original preview:\n{preview_text}\n\n"
            f"Converted preview:\n{preview_converted}\n\n"
            f"Convert entire document?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return text  # Return unchanged

        # Convert entire document
        converted = []
        for char in text:
            converted.append(symbol_to_unicode.get(char, char))

        return ''.join(converted)

