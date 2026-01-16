"""
SHARED JUSTIFICATION:
- RATIONALE: Shared UI Capability
- USED BY: Document_manager (Primary), Geometry (Unified Viewer - Dynamic Import)
- CRITERION: 4 (Cross-Pillar Capability)

The Rich Text Editor is a heavy UI component used primarily by the Document Manager
but also invoked dynamically by the Geometry Pillar's Unified Viewer for advanced
note-taking. As a reusable, self-contained editor widget, it correctly resides
in shared/ui/ to prevent the Geometry pillar from depending on the Document Manager pillar.

CONSTRAINT: shared/ui/ must never import from pillars/ (Shared is lower than all Pillars).
All Pillar-specific functionality must be injected via callbacks or feature classes.
"""

"""
Reusable Rich Text Editor with Ribbon UI and Plugin Architecture.

ARCHITECTURE OVERVIEW
=====================

This module contains two primary classes that work together:

1. SafeTextEdit (QTextEdit subclass)
   - The editing surface with embedded engines
   - Handles: pagination, resource loading, paste protection, rendering
   - Pure Qt widget - no business logic
   
2. RichTextEditor (QWidget container)
   - Orchestrates SafeTextEdit + Ribbon + Status Bar + Features
   - Manages: feature injection, UI composition, file I/O
   - Public API for embedding in parent windows

EMBEDDED ENGINES IN SafeTextEdit
=================================

SafeTextEdit is not a simple QTextEdit - it contains 5 specialized engines:

1. PAGINATION ENGINE (lines ~183-574)
   - Atomic block pagination: ensures text blocks don't straddle page boundaries
   - Debounced via QTimer to avoid per-keystroke runs
   - Anchor-based scroll restoration to maintain viewport position
   - Properties: pagination_enabled, _pagination_timer, _pagination_generation
   
2. RESOURCE PROTOCOL (lines ~688-792, ~908-971)
   - Custom docimg:// URL scheme for database-backed images
   - LRU cache (32 images max) via OrderedDict
   - Callbacks: resource_provider, resource_saver (injected by parent)
   
3. PASTE GUARD (lines ~892-971)
   - Mars Seal defensive pattern: prompts before large pastes
   - Thresholds: 100K chars text, 75K HTML, 12MB images
   - Prevents UI freezing from clipboard bombs
   
4. ASSET RESTORATION (lines ~794-891, ~2910-2961)
   - Pre-renders LaTeX/Mermaid images when loading HTML
   - Uses injected callbacks: latex_renderer, mermaid_renderer
   - Ensures generated content survives save/load cycles
   
5. PAGE BREAK RENDERING (lines ~615-686)
   - Paints dashed lines + gap fill at page boundaries
   - Visual guides for document layout mode
   - Toggleable via show_page_breaks property

FEATURE INJECTION SYSTEM
=========================

RichTextEditor uses dependency injection for extensibility:

- Features passed as List[Type[EditorFeature]] to constructor
- Features instantiated lazily in _ensure_features_initialized()
- Ribbon adapts to available features (graceful degradation)
- Document Manager injects full suite; Geometry injects minimal set

Example:
    editor = RichTextEditor(
        features=[
            ListFeature,
            TableFeature,
            SearchReplaceFeature,
            # ... more features
        ]
    )

RENDERER INJECTION
==================

For LaTeX/Mermaid rendering (Pillar-specific functionality):

    editor.editor.latex_renderer = MathRenderer.render_latex
    editor.editor.mermaid_renderer = WebViewMermaidRenderer.render_mermaid

This keeps Shared code decoupled from Pillar implementations.

FILE STRUCTURE (3300+ lines)
=============================

Lines 1-117:    Imports, constants, enums, dataclasses
Lines 118-971:  SafeTextEdit class (editing surface + engines)
Lines 972-983:  RichTextEditor class starts
Lines 984-1196: RichTextEditor initialization & setup
Lines 1197-1426: RichTextEditor feature system
Lines 1427-2044: RichTextEditor ribbon construction (4 tabs + context)
Lines 2045-2454: RichTextEditor formatting/layout methods
Lines 2455-2584: RichTextEditor print/export methods
Lines 2585-2709: RichTextEditor format sync & updates
Lines 2710-2909: RichTextEditor public API (get/set HTML/text/markdown)
Lines 2910-3337: RichTextEditor file I/O & utility methods

NAVIGATION TIPS
===============

- Search for "# ===" to jump between major sections
- Search for "TAB:" to find ribbon tab definitions
- Search for "def _init_" to find initialization sequences
- Search for "Engine:" in comments to find engine boundaries
- Each embedded engine has inline documentation at its entry point
"""
import html as html_module
import logging
import os
import base64
from typing import Optional, Any, Union, List, Tuple, Dict, Generator, Callable, Type
from collections import OrderedDict
from html.parser import HTMLParser

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
# from .table_features import TableFeature <-- Removed
# from .image_features import ImageInsertFeature, ImageEditFeature, ImageGateway <-- Removed
# from .list_features import ListFeature <-- Removed
# from .search_features import SearchReplaceFeature
# from .shape_features import ShapeFeature <-- Removed
from .ribbon_widget import RibbonWidget
# from .etymology_feature import EtymologyFeature  <-- Removed
# from .spell_feature import SpellFeature
# from .math_feature import MathFeature <-- Removed
# from .mermaid_feature import MermaidFeature <-- Removed
from .feature_interface import EditorFeature

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
    Pagination display and enforcement modes for the rich text editor.

    These presets control two independent systems:
    1. **Visual Guides**: Dashed lines and shaded gaps at page boundaries
    2. **Block Enforcement**: Dynamic margin adjustment to prevent blocks from
       straddling page boundaries

    Presets provide opinionated defaults for common use cases. Use CUSTOM mode
    with PageModeOptions for fine-grained control over individual settings.

    Attributes:
        FREEFLOW: No visual guides, no enforcement. Fast free-flow editing mode
            suitable for drafting or when pagination isn't needed.
        GUIDES_ONLY: Shows page break lines and gap fill for visual reference.
            When page outlines or margin guides are enabled, enforcement is
            forced to keep content inside visible page boundaries.
        ENFORCE_ONLY: Enforces block pagination (no straddling) but hides visual
            guides. For clean editing with proper page breaks on export.
        PAGED: Full document mode with both visual guides and block enforcement.
            Closest to WYSIWYG print preview behavior.
        CUSTOM: Manual control via PageModeOptions dataclass. Allows independent
            toggling of each feature.

    Example:
        >>> editor.set_page_mode(PageMode.PAGED)  # Full document mode
        >>> editor.set_page_mode(PageMode.FREEFLOW)  # Fast editing
        >>> editor.set_page_mode(PageMode.CUSTOM, PageModeOptions(
        ...     show_guides=True,
        ...     enforce_pagination=False
        ... ))
    """
    FREEFLOW = auto()
    GUIDES_ONLY = auto()
    ENFORCE_ONLY = auto()
    PAGED = auto()
    CUSTOM = auto()


@dataclass
class PageModeOptions:
    """
    Granular pagination control for CUSTOM mode or preset overrides.

    This dataclass provides fine-grained control over the editor's pagination
    behavior. Use with PageMode.CUSTOM for full control, or pass to other
    PageMode presets to override specific settings.

    The pagination system has two independent subsystems:
    - **Visual**: Renders dashed lines and shaded gaps at page boundaries
    - **Enforcement**: Adjusts block margins to prevent page-straddling

    Attributes:
        show_guides: When True, renders dashed horizontal lines at page break
            positions. These lines appear at the bottom margin of each page.
            Default: False.
        show_gap_fill: When True, fills the inter-page gap with a subtle
            semi-transparent shade (slate-200 at 80% opacity). Helps visualize
            the non-printable area between pages. Default: False.
        show_page_outline: When True, draws a light border around each page
            to visualize paper size. Default: False.
        show_margin_guides: When True, draws dashed lines for the content
            margins inside each page. Default: False.
        enforce_pagination: When True, activates the pagination engine which
            dynamically adjusts block top margins to push blocks that would
            straddle page boundaries to the next page. Uses cumulative baseline
            calculation for stable convergence. Default: False.
        scroll_anchor: When True, uses anchor-based scroll restoration after
            pagination adjustments. Captures visible cursor or block position
            before pagination and restores viewport alignment after margins
            change. Prevents visual "jumping" during edits. Default: True.
        couple_guides_and_enforcement: When True, automatically syncs
            enforce_pagination to match show_guides state. Useful for UIs
            where guides and enforcement should toggle together. Default: False.
        page_gap: Override the default inter-page gap size in pixels. When None,
            uses the editor's default (typically 20px). Set to 0 for no visible
            gap between pages. Default: None.

    Note:
        When page outlines or margin guides are enabled, pagination enforcement
        is forced on to keep content inside the visible page boundaries.

    Example:
        >>> # Full WYSIWYG mode with custom gap
        >>> opts = PageModeOptions(
        ...     show_guides=True,
        ...     show_gap_fill=True,
        ...     enforce_pagination=True,
        ...     page_gap=30
        ... )
        >>> editor.set_page_mode(PageMode.CUSTOM, opts)

        >>> # Visual preview only (no enforcement)
        >>> opts = PageModeOptions(show_guides=True, show_gap_fill=True)
        >>> editor.set_page_mode(PageMode.CUSTOM, opts)
    """
    show_guides: bool = False
    show_gap_fill: bool = False
    show_page_outline: bool = False
    show_margin_guides: bool = False
    enforce_pagination: bool = False
    scroll_anchor: bool = True
    couple_guides_and_enforcement: bool = False
    page_gap: Optional[int] = None


@dataclass(frozen=True)
class _GeneratedAssetTask:
    """
    Immutable task descriptor for restoring generated assets (LaTeX/Mermaid).

    When HTML containing docimg://math/ or docimg://mermaid/ images is loaded,
    the editor queues these tasks for background re-rendering. The source code
    is extracted from the image's alt attribute and passed to the appropriate
    renderer callback.

    Attributes:
        kind: The asset type, either "latex" or "mermaid". Determines which
            renderer callback to invoke.
        url: The full docimg:// URL from the img src attribute. Used to register
            the rendered image back into the document's resource cache.
        code: The source code to render. For LaTeX, this is the TeX markup.
            For Mermaid, this is the diagram definition DSL.

    Note:
        This class is frozen (immutable) to ensure task integrity during
        queued processing. Tasks are processed in batches by
        _process_asset_restore_queue().
    """
    kind: str
    url: str
    code: str


class _GeneratedImageParser(HTMLParser):
    """
    HTML parser that extracts generated asset references from document HTML.

    Scans for <img> tags with docimg://math/ or docimg://mermaid/ src URLs
    and collects their metadata for asset restoration. The alt attribute
    contains the source code prefixed with "LATEX:" or "MERMAID:".

    This parser is used during setHtml() to identify images that need
    re-rendering, since generated assets are not persisted as binary data
    but reconstructed from their source code on load.

    Attributes:
        images: List of dicts containing 'src' and 'alt' for each found
            generated image. Populated by handle_starttag().

    Example:
        >>> parser = _GeneratedImageParser()
        >>> parser.feed('<img src="docimg://math/uuid" alt="LATEX:E=mc^2">')
        >>> parser.images
        [{'src': 'docimg://math/uuid', 'alt': 'LATEX:E=mc^2'}]
    """

    def __init__(self) -> None:
        """Initialize the parser with an empty images list."""
        super().__init__()
        self.images: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        """
        Process an opening HTML tag, extracting generated image metadata.

        Only processes <img> tags with docimg://math/ or docimg://mermaid/
        src URLs. Other tags and images are ignored.

        Args:
            tag: The HTML tag name (e.g., 'img', 'div').
            attrs: List of (name, value) tuples for tag attributes.
        """
        if tag.lower() != "img":
            return
        attr_map = {name.lower(): (value or "") for name, value in attrs if name}
        src = attr_map.get("src", "")
        if not (src.startswith("docimg://math/") or src.startswith("docimg://mermaid/")):
            return
        self.images.append({"src": src, "alt": attr_map.get("alt", "")})


# =============================================================================
# SAFETEXTEDIT: EDITING SURFACE + EMBEDDED ENGINES
# =============================================================================

class SafeTextEdit(QTextEdit):
    """
    A hardened QTextEdit with 5 embedded engines for document editing.

    SafeTextEdit is the core editing surface for the rich text editor. It extends
    QTextEdit with specialized subsystems for paginated document editing, custom
    resource protocols, and defensive input handling. This class handles low-level
    document operations while remaining decoupled from UI chrome and business logic.

    RESPONSIBILITY BOUNDARY:
        - OWNS: Editing surface, pagination logic, resource loading, paste protection
        - DELEGATES: UI (ribbon/status bar), file I/O, feature orchestration to RichTextEditor

    EMBEDDED ENGINES:
        1. **Pagination Engine** (ENGINE 1):
            - Ensures text blocks don't straddle page boundaries
            - Uses cumulative baseline calculation for stable convergence
            - Debounced via QTimer (700ms) to avoid per-keystroke runs
            - Anchor-based scroll restoration maintains viewport position
            - Controlled via: pagination_enabled, set_page_mode()

        2. **Resource Protocol** (ENGINE 2):
            - Custom docimg:// URL scheme for database-backed images
            - LRU cache (32 images max) prevents repeated DB queries
            - Supports both docimg://123 and docimg:///123 URL formats
            - Security: validates IDs, rejects payloads > 25MB

        3. **Paste Guard** (ENGINE 3):
            - Mars Seal defensive pattern against clipboard bombs
            - Prompts user before pasting: >100K text, >75K HTML, >12MB images
            - Prevents UI freezing from unexpectedly large content

        4. **Asset Restoration** (ENGINE 4):
            - Re-renders LaTeX/Mermaid images when loading saved HTML
            - Extracts source from alt attributes (LATEX:/MERMAID: prefix)
            - Processes in batches to avoid blocking UI thread

        5. **Page Break Rendering** (ENGINE 5):
            - Paints dashed lines and shaded gaps at page boundaries
            - Viewport culling for performance (only visible breaks rendered)
            - Toggled via show_page_breaks property

    INJECTION POINTS (callbacks set by parent window):
        resource_provider: Callable[[int], Optional[Tuple[bytes, str]]]
            Fetches image data from database by ID. Returns (bytes, mime_type).
        resource_saver: Callable[[bytes, str], Optional[int]]
            Saves image data to database. Returns assigned ID.
        latex_renderer: Callable[[str], Optional[QImage]]
            Renders LaTeX markup to QImage.
        mermaid_renderer: Callable[[str], Optional[QImage]]
            Renders Mermaid DSL to QImage.

    DEBUG SUPPORT:
        Set ISOPGEM_PAGINATION_DEBUG=1 (or "verbose") environment variable
        to enable detailed pagination logging. Set ISOPGEM_RTE_MUTATION_DEBUG=1
        for document mutation tracing.

    Example:
        >>> editor = SafeTextEdit(parent_widget)
        >>> editor.resource_provider = lambda id: database.fetch_image(id)
        >>> editor.enable_pagination(True)
        >>> editor.set_page_mode(PageMode.PAGED)
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the hardened text editor with all embedded engines.

        Sets up the 5 embedded engines with their timers, guards, and callbacks.
        Pagination is disabled by default (opt-in sovereignty design) to ensure
        stability for simple text editing use cases.

        Initialization Sequence:
            1. Resource callbacks initialized to None (set by parent later)
            2. Page settings initialized to defaults (8.5x11", 1" margins)
            3. Pagination timer configured (700ms debounce, single-shot)
            4. Scroll guard timer configured (350ms scroll-end detection)
            5. Document signals connected for mutation tracking
            6. Debug handlers initialized if env vars are set

        Args:
            parent: Parent widget for Qt ownership hierarchy. Typically a
                RichTextEditor instance that will inject callbacks.

        Note:
            Pagination is intentionally opt-in. Call enable_pagination(True)
            or set_page_mode(PageMode.PAGED) to activate the pagination engine.
            This preserves fast, stable behavior for simple editing scenarios.
        """
        super().__init__(parent)
        # Resource loading callbacks (injected by parent)
        self.resource_provider: Optional[Callable[[int], Optional[Tuple[bytes, str]]]] = None
        self.resource_saver: Optional[Callable[[bytes, str], Optional[int]]] = None
        
        # Generated asset renderers (injected by parent, e.g., Document Manager)
        self.latex_renderer: Optional[Callable[[str], Optional[Any]]] = None
        self.mermaid_renderer: Optional[Callable[[str], Optional[Any]]] = None
        
        self._show_page_breaks = False
        self._show_gap_fill = False
        self._show_page_outline = False
        self._show_margin_guides = False
        self._fixed_width_layout = False
        self._page_settings = DEFAULT_PAGE_SETTINGS
        self._docimg_cache: "OrderedDict[int, Any]" = OrderedDict()
        self._asset_restore_queue: list[_GeneratedAssetTask] = []
        self._asset_restore_generation = 0
        self._asset_restore_queue_generation = 0
        self._asset_restore_batch_size = 2
        self._asset_restore_timer = QTimer(self)
        self._asset_restore_timer.setSingleShot(True)
        self._asset_restore_timer.timeout.connect(self._process_asset_restore_queue)
        
        # Pagination Sovereignty: opt-in by design (see enable_pagination())
        self.pagination_enabled = False
        
        # Pagination State
        # NOTE: Use self.page_height property (from settings) as single source of truth
        self._page_gap = 20 # Gap between visual pages
        self._is_paginating = False
        self._pagination_timer = QTimer(self)
        self._pagination_timer.setSingleShot(True)
        self._pagination_timer.setInterval(700)  # Debounce: less frequent runs during rapid typing
        self._pagination_interval_ms = 700
        self._pagination_cooldown_interval_ms = 900
        self._pagination_timer.timeout.connect(self._do_pagination)
        self.textChanged.connect(self._on_text_changed_debug)
        
        # Monotonic pagination counter (sovereign, not relying on Qt's revision)
        self._pagination_generation = 0
        self._last_paginated_generation = -1
        self._pagination_converge_passes = 0
        self._pagination_converge_max = 3
        self._pagination_converge_pending = False
        # Track doc revision when we last wrote, to skip redundant runs
        self._pagination_last_write_revision: Optional[int] = None
        # Track if pagination is stable (last run found no changes needed)
        self._pagination_stable = False
        # Track last seen document revision and stable run count for cooldown
        self._last_seen_revision: Optional[int] = None
        self._pagination_idle_runs = 0
        debug_env = os.getenv("ISOPGEM_PAGINATION_DEBUG", "").strip().lower()
        self._pagination_debug = debug_env in ("1", "true", "yes", "on", "debug", "verbose", "trace", "2")
        self._pagination_debug_verbose = debug_env in ("2", "verbose", "trace")
        mutation_env = os.getenv("ISOPGEM_RTE_MUTATION_DEBUG", "").strip().lower()
        if mutation_env:
            self._mutation_debug = mutation_env in ("1", "true", "yes", "on", "debug", "verbose", "trace", "2")
            self._mutation_debug_verbose = mutation_env in ("2", "verbose", "trace")
        else:
            self._mutation_debug = self._pagination_debug
            self._mutation_debug_verbose = self._pagination_debug_verbose
        self._pagination_debug_handler: Optional[logging.Handler] = None
        self._pagination_debug_prev_level: Optional[int] = None
        self._pagination_debug_prev_propagate: Optional[bool] = None
        if self._pagination_debug or self._mutation_debug:
            self._ensure_pagination_debug_handler()
        self._contents_change_seen = False
        self._formatting_pass_active = False

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
        doc = self.document()
        if doc is not None:
            doc.contentsChange.connect(self._on_contents_change)
            doc.contentsChanged.connect(self._on_contents_changed_debug)
    
    # -------------------------------------------------------------------------
    # ENGINE 1: PAGINATION (Atomic Block Layout)
    # -------------------------------------------------------------------------
    # Ensures text blocks don't straddle page boundaries by dynamically
    # adjusting top margins. Debounced via QTimer, uses monotonic generation
    # counter for idempotency, and employs anchor-based scroll restoration.
    # -------------------------------------------------------------------------
    
    def _schedule_pagination(self, *args, converge: bool = False, reason: Optional[str] = None) -> None:
        """
        Schedule a pagination check with debouncing to avoid per-keystroke runs.

        This method is the entry point for triggering pagination. It implements
        several guard mechanisms to prevent unnecessary or harmful pagination runs:

        Guard Mechanisms:
            1. **Disabled check**: Skips if pagination_enabled is False
            2. **Busy check**: Skips if already paginating (_is_paginating)
            3. **Scroll check**: Skips if user is actively scrolling (_is_scrolling)
            4. **Revision check**: Skips if document hasn't changed since last check
            5. **Stability check**: Skips if pagination is stable and doc unchanged

        Debounce Behavior:
            - Normal interval: 700ms (allows typing to settle)
            - Cooldown interval: 900ms (after 3+ idle runs, reduces CPU usage)
            - Timer is NOT restarted if already running (prevents starvation)

        The generation counter (_pagination_generation) is incremented on each
        schedule request to signal to _do_pagination() that content may have changed.

        Args:
            *args: Ignored. Allows this method to be connected to Qt signals
                that pass arguments (e.g., contentsChange).
            converge: If True, this is a convergence pass (pagination just ran
                and needs to verify stability). Convergence passes skip the
                stability check and don't reset convergence state.
            reason: Debug label for logging. Helps trace what triggered the
                pagination request (e.g., "textChanged", "contentsChange").

        Note:
            This method only schedules pagination - actual work happens in
            _do_pagination() when the timer fires.
        """
        if self._pagination_debug:
            self._log_pagination(
                "schedule-request",
                reason=reason or "unknown",
                converge=converge,
                is_paginating=self._is_paginating,
                is_scrolling=self._is_scrolling,
                timer_active=self._pagination_timer.isActive(),
                generation=self._pagination_generation,
                last_generation=self._last_paginated_generation,
            )
        if not getattr(self, "pagination_enabled", True):
            if self._pagination_debug:
                self._log_pagination("schedule-skip", reason=reason or "unknown", cause="disabled")
            return
        if getattr(self, "_is_paginating", False):
            if self._pagination_debug:
                self._log_pagination("schedule-skip", reason=reason or "unknown", cause="paginating")
            return
        if getattr(self, "_is_scrolling", False):
            if self._pagination_debug:
                self._log_pagination("schedule-skip", reason=reason or "unknown", cause="scrolling")
            return
        if not converge:
            doc = self.document()
            if doc is not None:
                current_rev = doc.revision()
                if self._last_seen_revision is not None and current_rev == self._last_seen_revision:
                    if self._pagination_debug:
                        self._log_pagination(
                            "schedule-skip",
                            reason=reason or "unknown",
                            cause="same_revision",
                            doc_revision=current_rev,
                        )
                    return
            # Check if we can skip due to stable pagination
            if (self._pagination_stable and doc is not None and
                self._pagination_last_write_revision is not None and
                doc.revision() == self._pagination_last_write_revision):
                if self._pagination_debug:
                    self._log_pagination(
                        "schedule-skip",
                        reason=reason or "unknown",
                        cause="stable_no_doc_change",
                    )
                return
            self._pagination_converge_passes = 0
            self._pagination_converge_pending = False
            # New content change invalidates stable state
            self._pagination_stable = False
        else:
            self._pagination_converge_pending = True
        # Advance generation so _do_pagination knows content/layout changed.
        self._pagination_generation += 1
        interval = self._pagination_interval_ms
        if self._pagination_idle_runs >= 3 and not converge:
            interval = self._pagination_cooldown_interval_ms
        self._pagination_timer.setInterval(interval)
        # Only start timer if not already running - don't restart on every keystroke
        if not self._pagination_timer.isActive():
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
            self._schedule_pagination(reason="enable_pagination")
    
    def set_page_mode(self, mode: PageMode, opts: Optional[PageModeOptions] = None) -> None:
        """
        Set pagination mode with unified control over visual guides and enforcement.

        This is the primary entry point for configuring the editor's pagination
        behavior. It controls both the visual page break rendering (guides, gap fill)
        and the block margin enforcement system.

        Mode Resolution:
            - FREEFLOW: All pagination features disabled (fast editing)
            - GUIDES_ONLY: Visual guides on, enforcement off (preview mode)
            - ENFORCE_ONLY: Enforcement on, visual guides off (clean editing)
            - PAGED: Both guides and enforcement on (full WYSIWYG)
            - CUSTOM: Uses provided PageModeOptions for granular control

        Side Effects:
            - Updates _show_page_breaks and _show_gap_fill flags
            - Sets pagination_enabled and scroll_anchor_enabled
            - Updates _page_gap if specified in options
            - Triggers immediate pagination if enforcement is enabled
            - Requests viewport repaint for visual changes
            - Stores mode in _current_page_mode for introspection

        Args:
            mode: The PageMode preset to apply. Determines default values for
                all pagination settings.
            opts: Optional PageModeOptions for granular control. Required when
                mode is CUSTOM; ignored for other presets (future: may allow
                preset overrides).

        Example:
            >>> # Full document mode with visual guides
            >>> editor.set_page_mode(PageMode.PAGED)

            >>> # Fast editing without pagination overhead
            >>> editor.set_page_mode(PageMode.FREEFLOW)

            >>> # Custom configuration
            >>> editor.set_page_mode(PageMode.CUSTOM, PageModeOptions(
            ...     show_guides=True,
            ...     show_gap_fill=False,
            ...     enforce_pagination=True,
            ...     page_gap=30
            ... ))
        """
        # Resolve preset to base options
        if mode == PageMode.FREEFLOW:
            resolved = PageModeOptions(
                show_guides=False,
                show_gap_fill=False,
                show_page_outline=False,
                show_margin_guides=False,
                enforce_pagination=False,
                scroll_anchor=True
            )
        elif mode == PageMode.GUIDES_ONLY:
            resolved = PageModeOptions(
                show_guides=True,
                show_gap_fill=True,
                show_page_outline=True,
                show_margin_guides=True,
                enforce_pagination=False,
                scroll_anchor=True
            )
        elif mode == PageMode.ENFORCE_ONLY:
            resolved = PageModeOptions(
                show_guides=False,
                show_gap_fill=False,
                show_page_outline=False,
                show_margin_guides=False,
                enforce_pagination=True,
                scroll_anchor=True
            )
        elif mode == PageMode.PAGED:
            resolved = PageModeOptions(
                show_guides=True,
                show_gap_fill=True,
                show_page_outline=True,
                show_margin_guides=True,
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

        # Handle coupling policy
        if resolved.couple_guides_and_enforcement:
            # Sync enforcement to guides state
            resolved.enforce_pagination = resolved.show_guides

        if resolved.show_page_outline or resolved.show_margin_guides:
            # Keep visible margins/gutters honest by enforcing pagination.
            resolved.enforce_pagination = True
        
        # Apply page_gap override if specified
        if resolved.page_gap is not None:
            self._page_gap = resolved.page_gap
        
        # Commit state to concrete flags
        self._show_page_breaks = resolved.show_guides or resolved.show_gap_fill
        self._show_gap_fill = resolved.show_gap_fill
        self._show_page_outline = resolved.show_page_outline
        self._show_margin_guides = resolved.show_margin_guides
        self.pagination_enabled = resolved.enforce_pagination
        self.scroll_anchor_enabled = resolved.scroll_anchor

        if self._pagination_debug:
            self._log_pagination(
                "mode-set",
                mode=mode.name,
                show_guides=resolved.show_guides,
                show_gap_fill=resolved.show_gap_fill,
                enforce_pagination=resolved.enforce_pagination,
                page_gap=self._page_gap,
                scroll_anchor=resolved.scroll_anchor,
            )
        
        # Store current mode for introspection
        self._current_page_mode = mode
        self._current_page_options = resolved
        
        use_fixed_width = resolved.show_page_outline or resolved.show_margin_guides
        if use_fixed_width != self._fixed_width_layout:
            self._apply_document_geometry(fixed_width=use_fixed_width)
            self._fixed_width_layout = use_fixed_width

        # Trigger updates
        if resolved.enforce_pagination:
            self._schedule_pagination(reason=f"set_page_mode:{mode.name}")
        
        # Repaint for visual changes
        viewport = self.viewport()
        if viewport is not None:
            viewport.update()

    def apply_layout(self, page_width_in: float, page_height_in: float, margins_in: tuple) -> None:
        """
        Apply a fixed page layout for WYSIWYG document editing.

        Configures the editor to use a specific page size and margins, typically
        matching an imported document's original layout. This enables accurate
        WYSIWYG editing where text wraps at the same positions as the source.

        The layout is applied by:
            1. Creating a PageSettings object with custom dimensions
            2. Setting QTextDocument page size
            3. Configuring root frame margins
            4. Enabling fixed-width line wrapping
            5. Triggering pagination recalculation

        Validation:
            - Page dimensions must be positive (returns early if not)
            - Margins must be a 4-tuple (falls back to defaults if not)
            - Individual margins are clamped to at most half the page dimension

        Args:
            page_width_in: Page width in inches. Standard US Letter is 8.5".
            page_height_in: Page height in inches. Standard US Letter is 11".
            margins_in: Tuple of (top, right, bottom, left) margins in inches.
                Typical document margins are 1" on all sides.

        Example:
            >>> # US Letter with 1" margins
            >>> editor.apply_layout(8.5, 11.0, (1.0, 1.0, 1.0, 1.0))

            >>> # A4 with narrow margins
            >>> editor.apply_layout(8.27, 11.69, (0.5, 0.5, 0.5, 0.5))
        """
        if page_width_in <= 0 or page_height_in <= 0:
            return
        if not margins_in or len(margins_in) != 4:
            margins_in = DEFAULT_PAGE_SETTINGS.margins_inches
        if self._pagination_debug:
            self._log_pagination(
                "layout-apply",
                page_width_in=page_width_in,
                page_height_in=page_height_in,
                margins_in=margins_in,
            )
        top, right, bottom, left = (max(0.0, float(m)) for m in margins_in)
        max_h = max(page_height_in / 2.0, 0.1)
        max_w = max(page_width_in / 2.0, 0.1)
        top = min(top, max_h)
        bottom = min(bottom, max_h)
        left = min(left, max_w)
        right = min(right, max_w)
        self._page_settings = PageSettings(
            page_size="custom",
            margins=(top, right, bottom, left),
            custom_dimensions=(page_width_in, page_height_in),
        )
        self._apply_document_geometry(fixed_width=True)
        self._fixed_width_layout = True

    def reset_layout(self) -> None:
        """Return to the default, flexible layout mode."""
        if self._pagination_debug:
            self._log_pagination("layout-reset")
        self._page_settings = DEFAULT_PAGE_SETTINGS
        self._apply_document_geometry(fixed_width=False)
        self._fixed_width_layout = False

    def _apply_document_geometry(self, fixed_width: bool) -> None:
        doc = self.document()
        if doc is None:
            return

        page_settings = self._page_settings
        dpi_x, dpi_y = self._resolve_screen_dpi()
        page_settings.set_screen_dpi(dpi_x, dpi_y)
        page_width_px = page_settings.page_width_pixels
        page_height_px = page_settings.page_height_pixels
        top_in, right_in, bottom_in, left_in = page_settings.margins_inches
        top_px = int(top_in * dpi_y)
        right_px = int(right_in * dpi_x)
        bottom_px = int(bottom_in * dpi_y)
        left_px = int(left_in * dpi_x)
        content_width_px = max(50, page_width_px - left_px - right_px)
        if self._pagination_debug:
            self._log_pagination(
                "geometry-apply",
                fixed_width=fixed_width,
                page_width_px=page_width_px,
                page_height_px=page_height_px,
                content_width_px=content_width_px,
                margins_px=(top_px, right_px, bottom_px, left_px),
                dpi_x=dpi_x,
                dpi_y=dpi_y,
            )

        doc.setPageSize(QSizeF(page_width_px, page_height_px))
        frame = doc.rootFrame()
        frame_format = frame.frameFormat()
        frame_format.setTopMargin(top_px)
        frame_format.setRightMargin(right_px)
        frame_format.setBottomMargin(bottom_px)
        frame_format.setLeftMargin(left_px)
        frame.setFrameFormat(frame_format)

        if fixed_width:
            self.setLineWrapMode(QTextEdit.LineWrapMode.FixedPixelWidth)
            self.setLineWrapColumnOrWidth(int(content_width_px))
            doc.setTextWidth(content_width_px)
        else:
            self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
            viewport = self.viewport()
            doc.setTextWidth(viewport.width() if viewport else content_width_px)

        self._schedule_pagination(reason="apply_document_geometry")
        if self._show_page_breaks:
            viewport = self.viewport()
            if viewport is not None:
                viewport.update()

    def _resolve_screen_dpi(self) -> tuple[float, float]:
        """Resolve logical DPI for the current widget/screen."""
        try:
            dpi_x = float(self.logicalDpiX())
            dpi_y = float(self.logicalDpiY())
        except Exception:
            dpi_x = PageSettings.SCREEN_DPI
            dpi_y = PageSettings.SCREEN_DPI
        if dpi_x <= 0:
            dpi_x = PageSettings.SCREEN_DPI
        if dpi_y <= 0:
            dpi_y = PageSettings.SCREEN_DPI
        return dpi_x, dpi_y

    def _on_scroll(self):
        """Mark scrolling active and debounce end marker."""
        if self._pagination_debug and not self._is_scrolling:
            scrollbar = self.verticalScrollBar()
            self._log_pagination(
                "scroll-start",
                scroll_value=scrollbar.value() if scrollbar is not None else None,
                timer_active=self._pagination_timer.isActive(),
            )
        self._is_scrolling = True
        if self._pagination_timer.isActive():
            self._pagination_timer.stop()
        self._scroll_timer.start()

    def _end_scroll(self):
        """End scroll window to allow pagination to resume."""
        self._is_scrolling = False
        if self._pagination_debug:
            scrollbar = self.verticalScrollBar()
            self._log_pagination(
                "scroll-end",
                scroll_value=scrollbar.value() if scrollbar is not None else None,
            )

    def _on_text_changed_debug(self) -> None:
        """Log textChanged events to trace revision churn."""
        if not getattr(self, "_mutation_debug", False):
            return
        doc = self.document()
        rev = doc.revision() if doc is not None else "None"
        logger.debug(
            "mutation: textChanged | revision=%s, is_paginating=%s",
            rev,
            self._is_paginating,
        )

    def _on_contents_change(self, position: int, chars_removed: int, chars_added: int) -> None:
        """Log and schedule pagination on document content changes."""
        self._contents_change_seen = True
        if getattr(self, "_mutation_debug", False):
            doc = self.document()
            rev = doc.revision() if doc is not None else "None"
            logger.debug(
                "mutation: contentsChange | pos=%s, removed=%s, added=%s, revision=%s",
                position,
                chars_removed,
                chars_added,
                rev,
            )
        if chars_removed == 0 and chars_added == 0:
            return
        self._schedule_pagination(reason=f"contentsChange:{chars_removed}->{chars_added}")

    def _on_contents_changed_debug(self) -> None:
        """Log contentsChanged to see post-change revisions."""
        if not getattr(self, "_mutation_debug", False):
            if not self._contents_change_seen:
                if not self._formatting_pass_active:
                    self._schedule_pagination(reason="contentsChanged:format")
            self._contents_change_seen = False
            return
        doc = self.document()
        rev = doc.revision() if doc is not None else "None"
        logger.debug("mutation: contentsChanged | revision=%s", rev)
        if not self._contents_change_seen:
            if self._formatting_pass_active:
                logger.debug("mutation: contentsChanged ignored (formatting pass)")
            else:
                self._schedule_pagination(reason="contentsChanged:format")
        self._contents_change_seen = False

    def set_pagination_debug(self, enabled: bool, verbose: bool = False) -> None:
        """Enable or disable pagination debug logging."""
        self._pagination_debug = bool(enabled)
        self._pagination_debug_verbose = bool(verbose) if enabled else False
        if self._pagination_debug:
            self._ensure_pagination_debug_handler()
        else:
            if not getattr(self, "_mutation_debug", False):
                self._disable_pagination_debug_handler()

    def _ensure_pagination_debug_handler(self) -> None:
        """Ensure pagination debug output is visible even if global log level is higher."""
        if not (self._pagination_debug or getattr(self, "_mutation_debug", False)):
            return
        root_level = logging.getLogger().getEffectiveLevel()
        if root_level <= logging.DEBUG:
            logger.setLevel(logging.DEBUG)
            return
        if self._pagination_debug_handler is None:
            for handler in logger.handlers:
                if getattr(handler, "_isopgem_pagination_debug", False):
                    self._pagination_debug_handler = handler
                    break
        if self._pagination_debug_handler is not None:
            logger.setLevel(logging.DEBUG)
            return
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        setattr(handler, "_isopgem_pagination_debug", True)
        if self._pagination_debug_prev_level is None:
            self._pagination_debug_prev_level = logger.level
        if self._pagination_debug_prev_propagate is None:
            self._pagination_debug_prev_propagate = logger.propagate
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        self._pagination_debug_handler = handler

    def _disable_pagination_debug_handler(self) -> None:
        if self._pagination_debug_handler is None:
            return
        try:
            logger.removeHandler(self._pagination_debug_handler)
        except Exception:
            pass
        if self._pagination_debug_prev_level is not None:
            logger.setLevel(self._pagination_debug_prev_level)
        if self._pagination_debug_prev_propagate is not None:
            logger.propagate = self._pagination_debug_prev_propagate
        self._pagination_debug_handler = None
        self._pagination_debug_prev_level = None
        self._pagination_debug_prev_propagate = None

    def _log_pagination(self, message: str, **fields) -> None:
        """Emit a structured pagination debug line when enabled."""
        if not self._pagination_debug:
            return
        if fields:
            parts = []
            for key in sorted(fields.keys()):
                value = fields[key]
                if isinstance(value, float):
                    parts.append(f"{key}={value:.2f}")
                else:
                    parts.append(f"{key}={value}")
            logger.debug("pagination: %s | %s", message, ", ".join(parts))
        else:
            logger.debug("pagination: %s", message)

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

    def _find_visible_cursor_pos(self) -> Optional[int]:
        """Return the current cursor position if it is visible in the viewport."""
        viewport = self.viewport()
        if viewport is None:
            return None
        cur = self.textCursor()
        if cur is None:
            return None
        rect = self.cursorRect(cur)
        if rect.isNull():
            return None
        if rect.intersects(viewport.rect()):
            return int(cur.position())
        return None

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

    def _get_cursor_viewport_offset_by_pos(self, cursor_pos: int) -> float:
        """Get the cursor's current vertical offset from the viewport top."""
        from PyQt6.QtGui import QTextCursor

        doc = self.document()
        if doc is None:
            return 0.0
        cur = QTextCursor(doc)
        cur.setPosition(cursor_pos)
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

    def _calculate_anchor_scroll_by_cursor_pos(self, cursor_pos: int, target_offset: float) -> Optional[int]:
        """Compute scrollbar adjustment to restore cursor to a viewport offset."""
        from PyQt6.QtGui import QTextCursor

        doc = self.document()
        if doc is None:
            return None
        scrollbar = self.verticalScrollBar()
        if scrollbar is None:
            return None
        cur = QTextCursor(doc)
        cur.setPosition(cursor_pos)
        current_rect = self.cursorRect(cur)
        current_offset = float(current_rect.top())
        delta = current_offset - target_offset
        return scrollbar.value() + int(delta)

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
            if self._pagination_debug:
                self._log_pagination(
                    "run-skip",
                    cause="busy_or_scrolling",
                    is_paginating=self._is_paginating,
                    is_scrolling=self._is_scrolling,
                )
            return
        doc = self.document()
        if doc is None:
            return

        # Skip if pagination is stable and doc hasn't changed since we last checked
        # This prevents redundant runs when pagination has converged
        current_rev = doc.revision()
        if (self._pagination_stable and
            self._pagination_last_write_revision is not None and
            current_rev == self._pagination_last_write_revision and
            not self._pagination_converge_pending):
            if self._pagination_debug:
                self._log_pagination(
                    "run-skip",
                    cause="stable_no_doc_change",
                    doc_revision=current_rev,
                    last_write_revision=self._pagination_last_write_revision,
                )
            return

        # Monotonic generation gate (sovereign counter, not Qt revision)
        if self._pagination_generation == self._last_paginated_generation:
            if self._pagination_debug:
                self._log_pagination(
                    "run-skip",
                    cause="no_generation_change",
                    generation=self._pagination_generation,
                    last_generation=self._last_paginated_generation,
                )
            return

        self._is_paginating = True
        changed = False  # Initialize before try to prevent UnboundLocalError in finally
        needs_converge = False
        push_count = 0
        baseline_resets = 0
        manual_breaks = 0
        manual_forced = 0
        invisible_blocks = 0
        oversize_blocks = 0
        total_blocks = 0
        changed_samples: list[str] = []
        try:
            doc = self.document()
            if doc is None:
                return
            scrollbar = self.verticalScrollBar()
            saved_scroll = scrollbar.value() if scrollbar is not None else None
            
            # Anchor-based scroll restoration: capture visible cursor or block position
            anchor_pos: Optional[int] = None
            anchor_offset = 0.0
            anchor_is_cursor = False
            if getattr(self, "scroll_anchor_enabled", True) and scrollbar is not None:
                cursor_pos = self._find_visible_cursor_pos()
                if cursor_pos is not None:
                    anchor_pos = cursor_pos
                    anchor_offset = self._get_cursor_viewport_offset_by_pos(cursor_pos)
                    anchor_is_cursor = True
                else:
                    anchor_pos = self._find_visible_anchor_block_pos()
                    if anchor_pos is not None:
                        anchor_offset = self._get_block_viewport_offset_by_pos(anchor_pos)
            anchor_type = "cursor" if anchor_is_cursor else ("block" if anchor_pos is not None else "none")
            
            # Capture the revision after any edits we make below
            current_rev = doc.revision()
            dpi_x, dpi_y = self._resolve_screen_dpi()
            self._page_settings.set_screen_dpi(dpi_x, dpi_y)
            origin_offset = self._page_origin_offset()
            # Use property as single source of truth for page height
            page_height = self.page_height
            top_in, _, bottom_in, _ = self._page_settings.margins_inches
            top_px = int(top_in * self._page_settings.screen_dpi_y)
            bottom_px = int(bottom_in * self._page_settings.screen_dpi_y)
            cycle = page_height + top_px + bottom_px + self._page_gap
            if self._pagination_debug:
                self._log_pagination(
                    "run-start",
                    generation=self._pagination_generation,
                    last_generation=self._last_paginated_generation,
                    converge_pending=self._pagination_converge_pending,
                    doc_revision=current_rev,
                    doc_height=doc.size().height(),
                    doc_blocks=doc.blockCount(),
                    scroll_start=saved_scroll,
                    anchor_type=anchor_type,
                    anchor_pos=anchor_pos,
                    anchor_offset=anchor_offset,
                    page_height=page_height,
                    page_gap=self._page_gap,
                    margins_top=top_px,
                    margins_bottom=bottom_px,
                    cycle=cycle,
                    dpi_x=dpi_x,
                    dpi_y=dpi_y,
                )
            
            # Disable undo/redo - pagination is view hygiene, not authored content
            undo_enabled = doc.isUndoRedoEnabled()
            doc.setUndoRedoEnabled(False)
            
            try:
                signals_prev = doc.blockSignals(True)
                editor_signals_prev = self.blockSignals(True)
                updates_prev = self.updatesEnabled()
                self.setUpdatesEnabled(False)
                try:
                    # Use a single cursor for all edits
                    edit_cursor = QTextCursor(doc)

                    # Phase 1: Read-only scan to collect current pagination state
                    layout = doc.documentLayout()
                    if layout is None:
                        return

                    # Collect current state: block_num -> current_total_margin (with pagination applied)
                    current_paginated: dict[int, float] = {}
                    block = doc.begin()
                    while block.isValid():
                        fmt = block.blockFormat()
                        if bool(fmt.property(PAGINATION_PROP)):
                            current_paginated[block.blockNumber()] = fmt.topMargin()
                            baseline_resets += 1
                        block = block.next()

                    # Phase 2: Calculate desired pagination using CUMULATIVE BASELINE
                    #
                    # Key insight: We walk the document once, accumulating positions using
                    # only original margins (ignoring any existing pagination margins).
                    # This gives us a stable "what if no pagination existed" baseline for
                    # every block, without needing to strip margins or force reflows.
                    #
                    # cumulative_baseline = position just BEFORE current block's margin
                    # baseline_top = cumulative_baseline + orig_margin = where block starts
                    #
                    # This makes every pass see identical geometry → converges in 1-2 passes.

                    desired_paginated: dict[int, tuple[float, float]] = {}  # block_num -> (orig_margin, target_margin)
                    block = doc.begin()
                    cumulative_baseline = 0.0  # Position just before current block (clean, no pagination)
                    manual_next_page_start: Optional[float] = None

                    while block.isValid():
                        total_blocks += 1
                        rect = layout.blockBoundingRect(block)
                        block_height = rect.height()

                        fmt = block.blockFormat()
                        is_paginated = bool(fmt.property(PAGINATION_PROP))
                        is_page_break = bool(fmt.property(PAGEBREAK_PROP))

                        # Get the original (baseline) margin - this is what the margin
                        # WOULD be without any pagination applied
                        if is_paginated:
                            orig_margin_prop = fmt.property(PAGINATION_ORIG_PROP)
                            orig_margin = 0.0
                            if orig_margin_prop is not None:
                                try:
                                    orig_margin = float(orig_margin_prop)
                                except Exception:
                                    orig_margin = 0.0
                        else:
                            orig_margin = fmt.topMargin()

                        # Handle invisible/empty blocks - still accumulate their space
                        if block_height < 1:
                            invisible_blocks += 1
                            cumulative_baseline += orig_margin + block_height
                            block = block.next()
                            continue

                        # True baseline position (computed from accumulation, not Qt layout)
                        baseline_top = cumulative_baseline + orig_margin
                        baseline_bottom = baseline_top + block_height

                        # Determine which page this block starts on
                        page_num = int(baseline_top / cycle)

                        # Position within the current cycle (0 = start of page content area)
                        local_top = baseline_top - (page_num * cycle)
                        local_bottom = baseline_bottom - (page_num * cycle)

                        if is_page_break:
                            manual_breaks += 1
                            if self._pagination_debug_verbose and len(changed_samples) < 8:
                                changed_samples.append(
                                    f"pagebreak block#{block.blockNumber()} pos={block.position()}"
                                )
                            manual_next_page_start = (page_num + 1) * cycle
                            cumulative_baseline += orig_margin + block_height
                            block = block.next()
                            continue

                        # Check if block would cross into the gap or next page
                        needs_push = False
                        margin_needed: Optional[float] = None

                        if manual_next_page_start is not None:
                            delta = manual_next_page_start - baseline_top
                            if delta > 1:
                                needs_push = True
                                margin_needed = orig_margin + delta
                                manual_forced += 1
                            manual_next_page_start = None

                        # Case 1: Block starts in the gap (between pages)
                        if not needs_push and local_top >= page_height:
                            needs_push = True

                        # Case 2: Block starts on page but extends into gap
                        elif not needs_push and local_bottom > page_height:
                            if block_height < page_height:
                                needs_push = True
                            else:
                                oversize_blocks += 1

                        if needs_push:
                            # Calculate target margin: push block to next page start
                            # margin_needed = next_page_start - cumulative_baseline
                            # When applied: new_top = cumulative_baseline + margin_needed = next_page_start
                            if margin_needed is None:
                                next_page_start = (page_num + 1) * cycle
                                margin_needed = next_page_start - cumulative_baseline

                            desired_paginated[block.blockNumber()] = (orig_margin, margin_needed)
                            push_count += 1

                        # Advance cumulative baseline using ORIGINAL margin + height
                        # This is the key: we always use orig_margin, never the paginated margin
                        cumulative_baseline += orig_margin + block_height
                        block = block.next()

                    # Phase 3: Compare desired vs current and only write if different
                    blocks_to_update: list[tuple[int, float, float]] = []  # (block_num, orig_margin, target_margin)
                    blocks_to_remove: list[int] = []  # block_nums that should no longer be paginated
                    total_delta = 0.0  # Sum of margin deltas for threshold check

                    # Find blocks that need updating or adding
                    for block_num, (orig_margin, target_margin) in desired_paginated.items():
                        current_margin = current_paginated.get(block_num)
                        if current_margin is None:
                            blocks_to_update.append((block_num, orig_margin, target_margin))
                            total_delta += abs(target_margin - orig_margin)
                        elif abs(current_margin - target_margin) > 1:
                            blocks_to_update.append((block_num, orig_margin, target_margin))
                            total_delta += abs(current_margin - target_margin)

                    # Find blocks that should no longer be paginated
                    for block_num in current_paginated:
                        if block_num not in desired_paginated:
                            blocks_to_remove.append(block_num)
                            total_delta += current_paginated[block_num]  # Full margin being removed

                    # Only mark as changed if total delta exceeds threshold
                    # This avoids writes for minor float precision differences
                    if total_delta > 10.0:
                        changed = True

                    # Phase 4: Apply changes only if needed
                    if changed and (blocks_to_update or blocks_to_remove):
                        edit_cursor.beginEditBlock()
                        try:
                            # Apply updates
                            for block_num, orig_margin, target_margin in blocks_to_update:
                                block = doc.findBlockByNumber(block_num)
                                if block.isValid():
                                    fmt = block.blockFormat()
                                    fmt.setProperty(PAGINATION_ORIG_PROP, orig_margin)
                                    fmt.setTopMargin(target_margin)
                                    fmt.setProperty(PAGINATION_PROP, True)
                                    edit_cursor.setPosition(block.position())
                                    edit_cursor.setBlockFormat(fmt)
                                    if self._pagination_debug_verbose and len(changed_samples) < 8:
                                        changed_samples.append(
                                            f"push block#{block_num} margin={orig_margin:.1f}->{target_margin:.1f}"
                                        )

                            # Remove pagination from blocks that no longer need it
                            for block_num in blocks_to_remove:
                                block = doc.findBlockByNumber(block_num)
                                if block.isValid():
                                    fmt = block.blockFormat()
                                    orig_margin_prop = fmt.property(PAGINATION_ORIG_PROP)
                                    restore_margin = 0.0
                                    if orig_margin_prop is not None:
                                        try:
                                            restore_margin = float(orig_margin_prop)
                                        except Exception:
                                            restore_margin = 0.0
                                    fmt.setTopMargin(restore_margin)
                                    fmt.clearProperty(PAGINATION_PROP)
                                    fmt.clearProperty(PAGINATION_ORIG_PROP)
                                    edit_cursor.setPosition(block.position())
                                    edit_cursor.setBlockFormat(fmt)
                                    if self._pagination_debug_verbose and len(changed_samples) < 8:
                                        changed_samples.append(
                                            f"reset block#{block_num} margin->{restore_margin:.1f}"
                                        )
                        finally:
                            edit_cursor.endEditBlock()
                finally:
                    doc.blockSignals(signals_prev)
                    self.blockSignals(editor_signals_prev)
                    self.setUpdatesEnabled(updates_prev)
            finally:
                # Restore undo/redo state
                doc.setUndoRedoEnabled(undo_enabled)
                # Record doc revision to detect future changes
                self._pagination_last_write_revision = doc.revision()
                self._last_seen_revision = self._pagination_last_write_revision
                if changed:
                    self._pagination_idle_runs = 0
                else:
                    self._pagination_idle_runs += 1
                if changed:
                    # Not stable - we made changes
                    self._pagination_stable = False
                    # Advance sovereign generation counter
                    self._pagination_generation += 1
                    if self._pagination_converge_passes < self._pagination_converge_max:
                        self._pagination_converge_passes += 1
                        needs_converge = True
                    else:
                        self._pagination_converge_passes = 0
                    # Restore scroll using anchor (semantic) or fallback to raw position
                    if scrollbar is not None and not self._pagination_converge_pending:
                        restored = False
                        if getattr(self, "scroll_anchor_enabled", True) and anchor_pos is not None:
                            if anchor_is_cursor:
                                new_scroll = self._calculate_anchor_scroll_by_cursor_pos(anchor_pos, anchor_offset)
                            else:
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

                else:
                    # Pagination is stable - no changes needed
                    self._pagination_stable = True
                    self._pagination_converge_passes = 0

                # Always update seen generation (whether changed or not, to avoid re-running)
                self._last_paginated_generation = self._pagination_generation
                self._pagination_converge_pending = False
                if self._pagination_debug:
                    scroll_end = scrollbar.value() if scrollbar is not None else None
                    scroll_delta = None
                    if scroll_end is not None and saved_scroll is not None:
                        scroll_delta = scroll_end - saved_scroll
                    self._log_pagination(
                        "run-end",
                        changed=changed,
                        pushes=push_count,
                        baseline_resets=baseline_resets,
                        manual_breaks=manual_breaks,
                        manual_forced=manual_forced,
                        invisible_blocks=invisible_blocks,
                        oversize_blocks=oversize_blocks,
                        total_blocks=total_blocks,
                        scroll_end=scroll_end,
                        scroll_delta=scroll_delta,
                        converge_scheduled=needs_converge,
                        converge_passes=self._pagination_converge_passes,
                    )
                    if self._pagination_debug_verbose and changed_samples:
                        self._log_pagination("run-samples", samples=" | ".join(changed_samples))
                
        finally:
            self._is_paginating = False
            if needs_converge:
                self._schedule_pagination(converge=True, reason="converge")

    def _page_origin_offset(self) -> float:
        """
        Return the vertical offset from document origin to page content origin.

        This accounts for QTextDocument margins and the root frame's top margin,
        keeping pagination math aligned with the visible content area.
        """
        doc = self.document()
        if doc is None:
            return 0.0
        doc_margin = float(doc.documentMargin()) if hasattr(doc, "documentMargin") else 0.0
        frame = doc.rootFrame()
        frame_margin = float(frame.frameFormat().topMargin()) if frame is not None else 0.0
        return doc_margin + frame_margin
    
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

    def keyPressEvent(self, e) -> None:  # type: ignore[override]
        is_return = e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
        prev_cursor_pos = None
        prev_block_pos = None
        prev_paginated = False
        if is_return:
            cursor = self.textCursor()
            prev_cursor_pos = int(cursor.position())
            prev_block = cursor.block()
            if prev_block.isValid():
                prev_block_pos = int(prev_block.position())
                prev_paginated = bool(prev_block.blockFormat().property(PAGINATION_PROP))

        super().keyPressEvent(e)

        if not (is_return and prev_paginated and self.pagination_enabled):
            return
        if prev_cursor_pos is None or prev_block_pos is None:
            return
        if prev_cursor_pos == prev_block_pos:
            return

        cur_block = self.textCursor().block()
        if not cur_block.isValid():
            return
        fmt = cur_block.blockFormat()
        if not bool(fmt.property(PAGINATION_PROP)):
            return
        orig_margin_prop = fmt.property(PAGINATION_ORIG_PROP)
        restore_margin = 0.0
        if orig_margin_prop is not None:
            try:
                restore_margin = float(orig_margin_prop)
            except Exception:
                restore_margin = 0.0
        if abs(fmt.topMargin() - restore_margin) < 0.5:
            return

        fmt.setTopMargin(restore_margin)
        fmt.clearProperty(PAGINATION_PROP)
        fmt.clearProperty(PAGINATION_ORIG_PROP)
        cursor = self.textCursor()
        cursor.setBlockFormat(fmt)
    
    # -------------------------------------------------------------------------
    # ENGINE 5: PAGE BREAK RENDERING (Visual Guides)
    # -------------------------------------------------------------------------
    # Paints dashed horizontal lines and shaded gaps at page boundaries
    # during the paint event. Only renders visible page breaks (viewport
    # culling) for performance. Toggled via show_page_breaks property.
    # -------------------------------------------------------------------------
    
    def paintEvent(self, e: Optional[QPaintEvent]) -> None:  # type: ignore[override]
        """Paint the text, then overlay visible page break lines and gap fills."""
        super().paintEvent(e)

        if not (self._show_page_breaks or self._show_page_outline or self._show_margin_guides):
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

        gap_brush = None
        if self._show_gap_fill:
            gap_fill_color = QColor("#e2e8f0")  # Soft slate-200
            gap_fill_color.setAlpha(80)  # Semi-transparent
            gap_brush = QBrush(gap_fill_color)

        break_pen = None
        if self._show_page_breaks:
            break_pen = QPen(QColor("#94a3b8"))
            break_pen.setStyle(Qt.PenStyle.DashLine)
            break_pen.setWidth(1)

        outline_pen = None
        if self._show_page_outline:
            outline_pen = QPen(QColor("#cbd5e1"))
            outline_pen.setWidth(1)

        margin_pen = None
        if self._show_margin_guides:
            margin_pen = QPen(QColor("#cbd5e1"))
            margin_pen.setStyle(Qt.PenStyle.DashLine)
            margin_pen.setWidth(1)

        scroll_y = scrollbar.value()
        h_scroll = self.horizontalScrollBar().value() if self.horizontalScrollBar() else 0
        viewport_height = viewport.height()
        viewport_width = viewport.width()

        dpi_x, dpi_y = self._resolve_screen_dpi()
        self._page_settings.set_screen_dpi(dpi_x, dpi_y)
        page_height = self.page_height
        page_width = self._page_settings.page_width_pixels
        origin_offset = self._page_origin_offset()
        top_in, right_in, bottom_in, left_in = self._page_settings.margins_inches
        top_px = int(top_in * self._page_settings.screen_dpi_y)
        bottom_px = int(bottom_in * self._page_settings.screen_dpi_y)
        left_px = int(left_in * self._page_settings.screen_dpi_x)
        right_px = int(right_in * self._page_settings.screen_dpi_x)
        page_height_total = page_height + top_px + bottom_px
        cycle = page_height_total + self._page_gap
        if cycle <= 0:
            painter.end()
            return

        page_top_base = origin_offset - top_px
        doc_margin = float(doc.documentMargin()) if hasattr(doc, "documentMargin") else 0.0
        page_left = doc_margin
        page_left_view = page_left - h_scroll
        doc_height = doc.size().height() - page_top_base

        # Draw only visible page breaks (small padded window)
        pad = 20
        first_page = max(0, int((scroll_y - page_top_base - pad) / cycle))
        last_page = int((scroll_y - page_top_base + viewport_height + pad) / cycle) + 2
        max_page = int(max(0.0, doc_height) / cycle) + 2
        last_page = min(last_page, max_page)

        for page in range(first_page, last_page):
            page_top = page_top_base + page * cycle
            page_top_view = page_top - scroll_y

            if outline_pen is not None:
                page_rect = QRectF(page_left_view, page_top_view, page_width, page_height_total)
                painter.setPen(outline_pen)
                painter.drawRect(page_rect)

            if margin_pen is not None:
                left_x = page_left_view + left_px
                right_x = page_left_view + page_width - right_px
                top_y = page_top_view + top_px
                bottom_y = page_top_view + page_height_total - bottom_px
                painter.setPen(margin_pen)
                painter.drawLine(int(left_x), int(top_y), int(right_x), int(top_y))
                painter.drawLine(int(left_x), int(bottom_y), int(right_x), int(bottom_y))
                painter.drawLine(int(left_x), int(top_y), int(left_x), int(bottom_y))
                painter.drawLine(int(right_x), int(top_y), int(right_x), int(bottom_y))

            if page <= 0:
                continue

            # Gap region: from break_y to break_y + _page_gap
            break_y = page_top_base + page * cycle - self._page_gap
            gap_start_viewport = break_y - scroll_y
            gap_end_viewport = gap_start_viewport + self._page_gap

            # Fill the gap region with subtle background
            if gap_end_viewport > -10 and gap_start_viewport < viewport_height + 10:
                if gap_brush is not None:
                    gap_rect = QRectF(0, gap_start_viewport, viewport_width, self._page_gap)
                    painter.fillRect(gap_rect, gap_brush)

                if break_pen is not None:
                    # Draw dashed line at the top of the gap (page break marker)
                    painter.setPen(break_pen)
                    painter.drawLine(10, int(gap_start_viewport), viewport_width - 10, int(gap_start_viewport))
                    painter.drawText(15, int(gap_start_viewport) - 5, f"─ Page {page + 1} ─")

        painter.end()
    
    # -------------------------------------------------------------------------
    # ENGINE 2: RESOURCE PROTOCOL (docimg:// + LRU Cache)
    # -------------------------------------------------------------------------
    # Custom URL scheme for database-backed images. Decouples editor from
    # database by using injected resource_provider callback. LRU cache (32
    # images) prevents repeated DB queries. Security: validates IDs, rejects
    # payloads > 25MB, supports both docimg://123 and docimg:///123 formats.
    # -------------------------------------------------------------------------
    
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
                    if getattr(self, "_mutation_debug", False):
                        doc = self.document()
                        logger.debug(
                            "mutation: resource_provider start | id=%s, revision=%s",
                            image_id,
                            doc.revision() if doc is not None else "None",
                        )
                    result = self.resource_provider(image_id)
                    if getattr(self, "_mutation_debug", False):
                        doc = self.document()
                        size = len(result[0]) if result else None
                        logger.debug(
                            "mutation: resource_provider end | id=%s, found=%s, bytes=%s, revision=%s",
                            image_id,
                            bool(result),
                            size,
                            doc.revision() if doc is not None else "None",
                        )
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

    # -------------------------------------------------------------------------
    # ENGINE 4: ASSET RESTORATION (Pre-render Generated Content)
    # -------------------------------------------------------------------------
    # When loading HTML with docimg://math/ or docimg://mermaid/ images,
    # extracts source code from alt attributes and re-renders using injected
    # latex_renderer/mermaid_renderer callbacks. This ensures generated content
    # survives save/load cycles without embedding in HTML.
    # -------------------------------------------------------------------------
    
    def _collect_generated_assets(self, html: str) -> list[_GeneratedAssetTask]:
        parser = _GeneratedImageParser()
        parser.feed(html)
        tasks: list[_GeneratedAssetTask] = []
        for image in parser.images:
            src = image.get("src", "")
            alt_text = image.get("alt", "")
            if src.startswith("docimg://math/") and alt_text.startswith("LATEX:"):
                code = html_module.unescape(alt_text[len("LATEX:"):])
                if code.strip():
                    tasks.append(_GeneratedAssetTask("latex", src, code))
            elif src.startswith("docimg://mermaid/") and alt_text.startswith("MERMAID:"):
                code = html_module.unescape(alt_text[len("MERMAID:"):])
                if code.strip():
                    tasks.append(_GeneratedAssetTask("mermaid", src, code))
        return tasks

    def _schedule_asset_restoration(self) -> None:
        if not self._asset_restore_queue:
            return
        if not self._asset_restore_timer.isActive():
            self._asset_restore_timer.start(0)

    def _process_asset_restore_queue(self) -> None:
        if self._asset_restore_queue_generation != self._asset_restore_generation:
            return
        if not self._asset_restore_queue:
            return
        batch = self._asset_restore_queue[:self._asset_restore_batch_size]
        del self._asset_restore_queue[:self._asset_restore_batch_size]
        if getattr(self, "_mutation_debug", False):
            doc = self.document()
            logger.debug(
                "mutation: asset-restore batch | count=%s, revision=%s",
                len(batch),
                doc.revision() if doc is not None else "None",
            )
        for task in batch:
            self._render_generated_asset(task)
        if batch:
            self.document().markContentsDirty(0, self.document().characterCount())
            self.viewport().update()
        if self._asset_restore_queue:
            self._asset_restore_timer.start(0)

    def _render_generated_asset(self, task: _GeneratedAssetTask) -> None:
        if getattr(self, "_mutation_debug", False):
            doc = self.document()
            logger.debug(
                "mutation: render-generated start | kind=%s, url=%s, revision=%s",
                task.kind,
                task.url,
                doc.revision() if doc is not None else "None",
            )
        renderer = self.latex_renderer if task.kind == "latex" else self.mermaid_renderer
        if renderer is None:
            logger.debug("Generated asset renderer missing for %s", task.kind)
            return
        try:
            image = renderer(task.code)
        except Exception:
            logger.debug("Failed to render %s asset", task.kind, exc_info=True)
            return
        if not image:
            logger.debug("Renderer returned no image for %s asset", task.kind)
            return
        self.document().addResource(
            QTextDocument.ResourceType.ImageResource,
            QUrl(task.url),
            image,
        )
        if getattr(self, "_mutation_debug", False):
            doc = self.document()
            logger.debug(
                "mutation: render-generated end | kind=%s, url=%s, revision=%s",
                task.kind,
                task.url,
                doc.revision() if doc is not None else "None",
            )

    def setHtml(self, html: str) -> None:  # type: ignore[override]
        """
        Override setHtml to restore math and mermaid images from alt text.

        We parse docimg://math/ and docimg://mermaid/ images, queue their sources,
        and re-render them in small batches to avoid blocking the UI thread.
        """
        tasks = self._collect_generated_assets(html)
        self._asset_restore_generation += 1
        self._asset_restore_queue_generation = self._asset_restore_generation
        self._asset_restore_queue = tasks
        if tasks:
            logger.debug("setHtml: queued %s generated assets", len(tasks))
        super().setHtml(html)
        self._schedule_asset_restoration()

    # -------------------------------------------------------------------------
    # ENGINE 3: PASTE GUARD (Mars Seal Defensive Pattern)
    # -------------------------------------------------------------------------
    # Intercepts large clipboard payloads and prompts for confirmation before
    # inserting. Prevents UI freezing from: massive text dumps (>100K chars),
    # large HTML (>75K), embedded data URIs (>12MB), and huge images (>12MP).
    # User can cancel paste after seeing size warning.
    # -------------------------------------------------------------------------
    
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




# =============================================================================
# RICHTEXTEDITOR: ORCHESTRATOR + UI SHELL
# =============================================================================
# This class composes SafeTextEdit with Ribbon UI, feature injection system,
# status bar, and public API. It does NOT contain editing logic - that lives
# in SafeTextEdit. RichTextEditor is the "window dressing" around the engine.
#
# Dialog classes have been moved to ui/dialogs/ for modularity:
# - HyperlinkDialog, HorizontalRuleDialog, PageSetupDialog
# - SpecialCharactersDialog, ExportPdfDialog, PageModeDialog
# =============================================================================


class RichTextEditor(QWidget):
    """
    A comprehensive rich text editor widget with Ribbon interface and plugin system.
    
    RESPONSIBILITY: Orchestrate SafeTextEdit + Ribbon + Features + File I/O.
    Does NOT handle: Low-level editing, pagination logic, resource loading.
    
    ARCHITECTURE:
    -------------
    - SafeTextEdit (self.editor): The editing surface (QTextEdit)
    - RibbonWidget (self.ribbon): The toolbar (Home/Insert/Page/Reference tabs)
    - Features (self.features): Injected plugins (tables, lists, search, etc.)
    - Status Bar: Word count + zoom controls
    
    FEATURE INJECTION:
    ------------------
    Pass List[Type[EditorFeature]] to constructor to enable plugins.
    Missing features result in disabled ribbon controls (graceful degradation).
    
    Example:
        editor = RichTextEditor(
            features=[ListFeature, TableFeature, SearchReplaceFeature]
        )
    
    PUBLIC API:
    -----------
    - get_html() / set_html(): Export/load formatted content
    - get_text() / set_text(): Export/load plain text
    - get_markdown() / set_markdown(): Markdown conversion
    - save_document() / open_document(): File I/O with encoding detection
    - find_text() / find_next() / find_previous(): Search navigation
    """
    
    # Signal emitted when text changes
    text_changed = pyqtSignal()
    
    # Signal emitted when [[ is typed
    wiki_link_requested = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None, placeholder_text: str = "Start typing...", show_ui: bool = True, features: Optional[List[Type[EditorFeature]]] = None) -> None:
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
            features: Optional list of EditorFeature classes to enable.
                      If None, loads the default set of features (legacy mode).
        """
        super().__init__(parent)
        self._injected_feature_classes: Optional[List[Type[EditorFeature]]] = features
        self.features: Dict[str, EditorFeature] = {}
        self.virtual_keyboard: VirtualKeyboard | None = None
        self.page_count_label: QLabel | None = None
        self.word_count_label: QLabel | None = None
        
        # Initialize Feature Attributes to None
        self.etymology_feature = None
        self.table_feature = None
        self.mermaid_feature = None
        self.math_feature = None
        self.shape_feature = None
        self.list_feature = None
        self.search_feature = None
        self.spell_feature = None
        self.image_insert_feature = None
        self.image_edit_feature = None
        self.image_gateway = None
        self._assets_restored = False
        
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

    # =========================================================================
    # FEATURE INJECTION SYSTEM
    # =========================================================================
    # Features are passed as classes to __init__, instantiated lazily, and
    # stored in self.features dict. Ribbon adapts to available features.
    # This allows Document Manager to inject full suite while Geometry injects
    # minimal set, both without crashes or forced dependencies.
    # =========================================================================
    
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
            
        # 1. Plugin Injection Mode (Sovereign Injection)
        if self._injected_feature_classes is not None:
            # Only run if not already populated
            if self.features: 
                return
            
            # Pre-initialize Gateway (Removed: ImageGateway is now in Pillar)
            # Features needing it must auto-initialize it.

            for cls in self._injected_feature_classes:
                try:
                    # Try injecting with gateway first (for image features)
                    # We pass the gateway if it exists on editor, else None.
                    # The Feature is responsible for fallback.
                    try:
                         # We can't predict arg names easily, but we know Image features might take 2 args.
                         # If we pass None for gateway, it works with our updated Feature __init__.
                         instance = cls(self, getattr(self, 'image_gateway', None))
                    except TypeError:
                        # Fallback to standard init
                        instance = cls(self)
                    if hasattr(instance, 'initialize'): 
                        instance.initialize()
                    
                    name = instance.name() if hasattr(instance, 'name') else cls.__name__
                    self.features[name] = instance
                    
                    # Compatibility Mapping for legacy code expecting specific attributes
                    if name == "etymology_feature":
                        self.etymology_feature = instance
                    elif name == "table_feature":
                        self.table_feature = instance
                    elif name == "mermaid_feature":
                        self.mermaid_feature = instance
                    elif name == "math_feature":
                        self.math_feature = instance
                    elif name == "shape_feature":
                        self.shape_feature = instance
                    elif name == "list_feature":
                        self.list_feature = instance
                    elif name == "search_replace_feature":
                        self.search_feature = instance
                    elif name == "spell_feature":
                        self.spell_feature = instance
                    elif name == "image_insert_feature":
                        self.image_insert_feature = instance
                    elif name == "image_edit_feature":
                        self.image_edit_feature = instance
                    # Add mappings for future refactored features here
                    
                except Exception as e:
                    logger.error(f"Failed to initialize plugin {cls.__name__}: {e}")
            return

        # 2. Legacy Monolith Mode (Deprecated)
        # All features should now be injected via the 'features' argument.
        # This block ensures attributes are at least stable (None) if not injected.
        
        # If any legacy logic attempts to access these attributes, 
        # providing None is safer than AttributeError, but functionality will be missing.
        pass

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

    # =========================================================================
    # RIBBON CONSTRUCTION (4 Tabs + 2 Context Categories)
    # =========================================================================
    # Builds Home, Insert, Page Layout, and Reference tabs.
    # Context categories (Table Tools, Image Tools) appear when relevant.
    # Ribbon adapts to available features - missing features = disabled buttons.
    # =========================================================================
    
    def _init_ribbon(self) -> None:
        """Populate the ribbon with tabs and groups.
        
        Graceful Degradation: Ribbon groups adapt to available features.
        Missing features result in hidden/disabled controls, not crashes.
        This allows Geometry to inject minimal features while Document Manager
        injects the full suite.
        """
        # Ensure features are initialized before wiring ribbon
        self._ensure_features_initialized()
        
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
        
        # Only build list controls if ListFeature is available
        lf = self.list_feature
        if lf is not None:
            from .editor_constants import LIST_STYLES, BULLET_STYLES, NUMBER_STYLES
            
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
                act_start.triggered.connect(lambda: lf.show_start_number_dialog())
            self.number_btn.setMenu(number_menu)
            grp_lists.add_widget(self.number_btn)
            
            # Checklist Button
            act_checklist = QAction(qta.icon("fa5s.check-square", color="#1e293b"), "Checklist", self)
            act_checklist.setToolTip("Toggle Checklist")
            act_checklist.triggered.connect(lambda: lf.toggle_checklist())
            grp_lists.add_action(act_checklist, Qt.ToolButtonStyle.ToolButtonIconOnly)
            
            # Indent/Outdent
            act_indent = QAction(qta.icon("fa5s.indent", color="#1e293b"), "Increase Indent", self)
            act_indent.triggered.connect(lambda: lf.indent())
            grp_lists.add_action(act_indent, Qt.ToolButtonStyle.ToolButtonIconOnly)
            
            act_outdent = QAction(qta.icon("fa5s.outdent", color="#1e293b"), "Decrease Indent", self)
            act_outdent.triggered.connect(lambda: lf.outdent())
            grp_lists.add_action(act_outdent, Qt.ToolButtonStyle.ToolButtonIconOnly)
            
            # Remove List
            act_remove_list = QAction(qta.icon("fa5s.times-circle", color="#dc2626"), "Remove List", self)
            act_remove_list.triggered.connect(lambda: lf.remove_list())
            grp_lists.add_action(act_remove_list, Qt.ToolButtonStyle.ToolButtonIconOnly)
        else:
            # Feature not available - add disabled placeholder
            act_unavailable = QAction("Lists (Not Available)", self)
            act_unavailable.setEnabled(False)
            grp_lists.add_action(act_unavailable, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
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
        sf = self.search_feature
        if sf is not None:
            action_replace = QAction("Replace", self)
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
        grp_tables = tab_insert.add_group("Tables")
        if self.table_feature:
            grp_tables.add_widget(self.table_feature.create_toolbar_button())
        else:
            act_unavailable = QAction("Tables (Not Available)", self)
            act_unavailable.setEnabled(False)
            grp_tables.add_action(act_unavailable)
        
        # Group: Illustrations
        grp_illus = tab_insert.add_group("Illustrations")
        if self.image_insert_feature:
            grp_illus.add_action(self.image_insert_feature.create_toolbar_action(), Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # Shapes
        if self.shape_feature:
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
        
        # Etymology lookup
        if self.etymology_feature:
            grp_lang.add_action(self.etymology_feature.create_action(self), Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        # Group: Proofing
        grp_proof = tab_ref.add_group("Proofing")
        
        # Spell Check (if available)
        if self.spell_feature:
            grp_proof.add_action(self.spell_feature.create_ribbon_action(self), Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            grp_proof.add_action(self.spell_feature.create_toggle_action(self), Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        # =========================================================================
        # CONTEXT CATEGORIES
        # =========================================================================
        
        # === CONTEXT CATEGORY: Table Tools ===
        # Only create if TableFeature is available
        tf = self.table_feature
        if tf is not None:
            self.ctx_table = self.ribbon.add_context_category("Table Tools", Qt.GlobalColor.darkYellow)
            
            # Layout Group - Insert/Delete
            grp_tbl_layout = self.ctx_table.add_group("Layout")
            
            act_ins_row = QAction(qta.icon("fa5s.plus", color="#1e293b"), "Insert Row", self)
            act_ins_row.triggered.connect(lambda: tf._insert_row_below())
            grp_tbl_layout.add_action(act_ins_row, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            
            act_ins_col = QAction(qta.icon("fa5s.plus", color="#1e293b"), "Insert Col", self)
            act_ins_col.triggered.connect(lambda: tf._insert_col_right())
            grp_tbl_layout.add_action(act_ins_col, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            
            grp_tbl_layout.add_separator()
            
            act_del_row = QAction(qta.icon("fa5s.minus", color="#dc2626"), "Delete Row", self)
            act_del_row.triggered.connect(lambda: tf._delete_row())
            grp_tbl_layout.add_action(act_del_row, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            
            act_del_col = QAction(qta.icon("fa5s.minus", color="#dc2626"), "Delete Col", self)
            act_del_col.triggered.connect(lambda: tf._delete_col())
            grp_tbl_layout.add_action(act_del_col, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            
            act_del_table = QAction(qta.icon("fa5s.trash", color="#dc2626"), "Delete Table", self)
            act_del_table.triggered.connect(lambda: tf._delete_table())
            grp_tbl_layout.add_action(act_del_table, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            
            # Merge/Split Group
            grp_tbl_merge = self.ctx_table.add_group("Merge")
            
            act_merge = QAction(qta.icon("fa5s.object-group", color="#1e293b"), "Merge Cells", self)
            act_merge.triggered.connect(lambda: tf._merge_cells())
            grp_tbl_merge.add_action(act_merge, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            
            act_split = QAction(qta.icon("fa5s.object-ungroup", color="#1e293b"), "Split Cells", self)
            act_split.triggered.connect(lambda: tf._split_cells())
            grp_tbl_merge.add_action(act_split, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            
            act_distribute = QAction(qta.icon("fa5s.arrows-alt-h", color="#1e293b"), "Distribute", self)
            act_distribute.triggered.connect(lambda: tf._distribute_columns())
            grp_tbl_merge.add_action(act_distribute, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            
            # Style Group
            grp_tbl_style = self.ctx_table.add_group("Style")
            
            act_cell_bg = QAction(qta.icon("fa5s.fill-drip", color="#1e293b"), "Cell Color", self)
            act_cell_bg.triggered.connect(lambda: tf._set_cell_background())
            grp_tbl_style.add_action(act_cell_bg, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            
            act_cell_border = QAction(qta.icon("fa5s.border-style", color="#1e293b"), "Borders", self)
            act_cell_border.triggered.connect(lambda: tf._edit_cell_borders())
            grp_tbl_style.add_action(act_cell_border, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            
            act_cell_props = QAction(qta.icon("fa5s.sliders-h", color="#1e293b"), "Cell Props", self)
            act_cell_props.triggered.connect(lambda: tf._edit_cell_properties())
            grp_tbl_style.add_action(act_cell_props, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            
            act_table_props = QAction(qta.icon("fa5s.cog", color="#1e293b"), "Table Props", self)
            act_table_props.triggered.connect(lambda: tf._edit_table_properties())
            grp_tbl_style.add_action(act_table_props, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        else:
            # No table feature - ctx_table not created
            self.ctx_table = None

        # === CONTEXT CATEGORY: Image Tools ===
        # Only create if ImageEditFeature is available
        if self.image_edit_feature:
            self.ctx_image = self.ribbon.add_context_category("Image Tools", Qt.GlobalColor.magenta)
        else:
            self.ctx_image = None
        
        if self.ctx_image:
            # Tools Group
            grp_img_tools = self.ctx_image.add_group("Tools")
            
            if self.image_edit_feature:
                # Edit Action (Crop/Filter/Rotate)
                if hasattr(self.image_edit_feature, 'action_edit'):
                    grp_img_tools.add_action(self.image_edit_feature.action_edit, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
                
                # Properties Action
                if hasattr(self.image_edit_feature, 'action_props'):
                    grp_img_tools.add_action(self.image_edit_feature.action_props, Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        # Connect cursor/selection change to context switches
        self.editor.cursorPositionChanged.connect(self._update_context_tabs)
        
    def _update_context_tabs(self) -> None:
        """Show/Hide context tabs based on cursor position.
        
        Gracefully handles missing context categories (when features not injected).
        """
        cursor = self.editor.textCursor()
        
        # Check Table (only if feature available)
        if self.ctx_table:
            if cursor.currentTable():
                self.ribbon.show_context_category(self.ctx_table)
            else:
                self.ribbon.hide_context_category(self.ctx_table)
            
        # Check Image (only if feature available)
        if self.ctx_image:
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

    def _apply_page_setup_to_editor(
        self,
        page_size: QPageSize,
        orientation: QPageLayout.Orientation,
        margins: QMarginsF,
    ) -> None:
        size_mm = page_size.size(QPageSize.Unit.Millimeter)
        width_mm = float(size_mm.width())
        height_mm = float(size_mm.height())
        if orientation == QPageLayout.Orientation.Landscape:
            width_mm, height_mm = height_mm, width_mm
        page_width_in = width_mm / 25.4
        page_height_in = height_mm / 25.4
        margins_in = (
            float(margins.top()) / 25.4,
            float(margins.right()) / 25.4,
            float(margins.bottom()) / 25.4,
            float(margins.left()) / 25.4,
        )
        self.editor.apply_layout(page_width_in, page_height_in, margins_in)

    def _show_page_setup(self) -> None:
        """Show page setup dialog."""
        dialog = PageSetupDialog(self)
        if dialog.exec():
            # Store page settings for later use in printing/export
            self._page_size = dialog.get_page_size()
            self._page_orientation = dialog.get_orientation()
            self._page_margins = dialog.get_margins()
            self._apply_page_setup_to_editor(
                self._page_size,
                self._page_orientation,
                self._page_margins,
            )
            QMessageBox.information(
                self,
                "Page Setup",
                "Page settings applied to the editor and saved for printing/export.",
            )

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
        
    # =========================================================================
    # PUBLIC API: Content Access, Search, Display Control
    # =========================================================================
    # These methods form the stable interface for parent windows to interact
    # with the editor. Internal methods are prefixed with _ by convention.
    # =========================================================================
    
    def set_page_mode(self, mode: PageMode, opts: Optional[PageModeOptions] = None) -> None:
        """
        Set pagination mode with unified control (app-level entry point).
        
        Delegates to SafeTextEdit.set_page_mode() where state is enacted.
        
        Args:
            mode: The PageMode preset to apply
            opts: Optional PageModeOptions for overrides
        """
        self.editor.set_page_mode(mode, opts)

    def set_pagination_debug(self, enabled: bool, verbose: bool = False) -> None:
        """Toggle pagination debug logging."""
        self.editor.set_pagination_debug(enabled, verbose)

    def apply_layout(self, layout: dict) -> None:
        """
        Apply layout metadata captured during import (page size + margins).

        Args:
            layout: Dict with page_width_in, page_height_in, margins_in.
        """
        if not layout:
            self.editor.reset_layout()
            return
        page_width_in = layout.get("page_width_in")
        page_height_in = layout.get("page_height_in")
        margins_in = layout.get("margins_in")
        if not isinstance(page_width_in, (int, float)) or not isinstance(page_height_in, (int, float)):
            self.editor.reset_layout()
            return
        self.editor.apply_layout(float(page_width_in), float(page_height_in), margins_in)

    def reset_layout(self) -> None:
        """Return the editor to its default layout behavior."""
        self.editor.reset_layout()
    
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
        doc = self.editor.document()
        doc_signals_prev = doc.blockSignals(True) if doc is not None else None
        editor_signals_prev = self.editor.blockSignals(True)
        try:
            self._assets_restored = False
            self.editor.setHtml(html)
            # Ensure LTR is maintained after setting content
            self.editor.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        finally:
            if doc is not None:
                doc.blockSignals(doc_signals_prev)
            self.editor.blockSignals(editor_signals_prev)
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
        doc = self.editor.document()
        doc_signals_prev = doc.blockSignals(True) if doc is not None else None
        editor_signals_prev = self.editor.blockSignals(True)
        try:
            self._assets_restored = False
            self.editor.setMarkdown(markdown)
            # Ensure LTR is maintained
            self.editor.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        finally:
            if doc is not None:
                doc.blockSignals(doc_signals_prev)
            self.editor.blockSignals(editor_signals_prev)
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

    # =========================================================================
    # FILE I/O: Open, Save, Import/Export
    # =========================================================================
    # Handles document persistence with encoding detection, DOCX/PDF extraction,
    # and image embedding for round-trip fidelity. Always saves as UTF-8.
    # =========================================================================
    
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
        debug = getattr(self.editor, "_mutation_debug", False)
        verbose = getattr(self.editor, "_mutation_debug_verbose", False)
        if self._assets_restored:
            if debug:
                logger.debug(
                    "mutation: restore-generated skip | revision=%s",
                    doc.revision(),
                )
            return
        if debug:
            logger.debug(
                "mutation: restore-generated start | revision=%s, blocks=%s",
                doc.revision(),
                doc.blockCount(),
            )

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

        if debug:
            logger.debug(
                "mutation: restore-generated tasks | count=%s, revision=%s",
                len(tasks),
                doc.revision(),
            )

        for pos, kind, code in tasks:
            cursor = QTextCursor(doc)
            cursor.setPosition(pos)
            cursor.setPosition(pos + 1, QTextCursor.MoveMode.KeepAnchor)
            try:
                if verbose:
                    logger.debug(
                        "mutation: restore-generated apply | kind=%s, pos=%s, revision=%s",
                        kind,
                        pos,
                        doc.revision(),
                    )
                if kind == 'mermaid' and mer:
                    self.editor.setTextCursor(cursor)
                    mer.insert_mermaid(code)
                elif kind == 'latex' and mth:
                    self.editor.setTextCursor(cursor)
                    mth.insert_math(code)
                if verbose:
                    logger.debug(
                        "mutation: restore-generated applied | kind=%s, pos=%s, revision=%s",
                        kind,
                        pos,
                        doc.revision(),
                    )
            except Exception as exc:
                logger.warning("Failed to restore %s block: %s", kind, exc)
        self._assets_restored = True
        if debug:
            logger.debug(
                "mutation: restore-generated end | revision=%s",
                doc.revision(),
            )

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
