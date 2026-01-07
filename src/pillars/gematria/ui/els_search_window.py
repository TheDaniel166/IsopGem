"""TQ Text Sequencer Window - Three-pane interface for ELS searching.

Left: Controls (text source, grid config, search params)
Center: Zoomable letter grid
Right: Clickable search results
"""
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QLineEdit, QSpinBox, QPushButton, QComboBox, QRadioButton,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit,
    QFileDialog, QMessageBox, QButtonGroup, QFrame, QTabWidget,
    QCheckBox
)
from PyQt6.QtCore import Qt
from typing import List, Optional
import logging

from .els_grid_view import ELSGridView
from ..services.els_service import ELSSearchService, ELSResult
from ..services import TQGematriaCalculator
from ..services.document_gateway import get_all_documents_metadata, get_document
from shared.ui import theme

logger = logging.getLogger(__name__)



class ELSSearchWindow(QMainWindow):
    """
    TQ Text Sequencer Window with 3-pane layout.
    
    - Left pane: Text source, grid configuration, search controls
    - Center pane: Zoomable/pannable letter grid (ELSGridView)
    - Right pane: Clickable search results
    """
    
    def __init__(self, window_manager=None, parent=None):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """
          init   logic.
        
        Args:
            window_manager: Description of window_manager.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.window_manager = window_manager
        self._service = ELSSearchService()
        
        self._stripped_text = ""
        self._position_map = []
        self._current_results: List[ELSResult] = []
        
        self.setWindowTitle("🔮 The Resonant Chain")
        self.setMinimumSize(1200, 700)
        self.resize(1400, 800)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Build the 3-pane interface."""
        central = QWidget()
        central.setObjectName("CentralContainer")
        self.setCentralWidget(central)
        
        # Level 0: Background
        import os
        bg_path = os.path.abspath("src/assets/patterns/tq_bg_pattern.png")
        central.setStyleSheet(f"""
            QWidget#CentralContainer {{
                border-image: url("{bg_path}") 0 0 0 0 stretch stretch;
                background-color: {theme.COLORS['cloud']};
            }}
        """)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Main horizontal splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # === LEFT PANE: Controls ===
        left_pane = self._create_left_pane()
        splitter.addWidget(left_pane)
        
        # === CENTER PANE: Grid View with Floating Zoom ===
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        
        # Grid view
        self._grid_view = ELSGridView()
        center_layout.addWidget(self._grid_view)
        
        # Floating zoom controls (overlay in top-right)
        zoom_toolbar = QFrame(center_container)
        zoom_toolbar.setObjectName("FloatingZoom")
        zoom_layout = QHBoxLayout(zoom_toolbar)
        zoom_layout.setContentsMargins(8, 8, 8, 8)
        zoom_layout.setSpacing(4)
        
        # Glassmorphism styling per Visual Liturgy
        zoom_toolbar.setStyleSheet(f"""
            QFrame#FloatingZoom {{
                background-color: rgba(30, 30, 40, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
            }}
        """)
        
        # Apply shadow effect
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        from PyQt6.QtGui import QColor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 120))
        zoom_toolbar.setGraphicsEffect(shadow)
        
        # === ZOOM BUTTONS ===
        # DEVIATION FROM VISUAL LITURGY (by decree of The Magus, 2026-01-07):
        # - Inline styles instead of archetypes (for precise centering control)
        # - Amber gradient (seeker palette) for visibility on dark glassmorphic background
        # - Navigator archetype (dark slate) is invisible on dark surfaces
        # Rationale: Centering precision and dark-surface visibility prioritized over semantic purity
        
        btn_zoom_out = QPushButton("−")
        btn_zoom_out.setFixedSize(36, 36)
        btn_zoom_out.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_zoom_out.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f59e0b, stop:1 #d97706);
                border: 2px solid #b45309;
                color: white;
                font-weight: 700;
                font-size: 18pt;
                border-radius: 8px;
                padding: 0px;
                text-align: center;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fbbf24, stop:1 #f59e0b); }
            QPushButton:pressed { background: #b45309; }
        """)
        btn_zoom_out.clicked.connect(lambda: self._grid_view.zoom_out())
        zoom_layout.addWidget(btn_zoom_out)
        
        btn_zoom_in = QPushButton("+")
        btn_zoom_in.setFixedSize(36, 36)
        btn_zoom_in.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_zoom_in.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f59e0b, stop:1 #d97706);
                border: 2px solid #b45309;
                color: white;
                font-weight: 700;
                font-size: 18pt;
                border-radius: 8px;
                padding: 0px;
                text-align: center;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fbbf24, stop:1 #f59e0b); }
            QPushButton:pressed { background: #b45309; }
        """)
        btn_zoom_in.clicked.connect(lambda: self._grid_view.zoom_in())
        zoom_layout.addWidget(btn_zoom_in)
        
        btn_zoom_reset = QPushButton("⟲")
        btn_zoom_reset.setFixedSize(36, 36)
        btn_zoom_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_zoom_reset.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f59e0b, stop:1 #d97706);
                border: 2px solid #b45309;
                color: white;
                font-weight: 700;
                font-size: 16pt;
                border-radius: 8px;
                padding: 0px;
                text-align: center;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fbbf24, stop:1 #f59e0b); }
            QPushButton:pressed { background: #b45309; }
        """)
        btn_zoom_reset.clicked.connect(lambda: self._grid_view.zoom_reset())
        zoom_layout.addWidget(btn_zoom_reset)
        
        # Position floating toolbar in top-right
        zoom_toolbar.setGeometry(10, 10, 130, 52)
        zoom_toolbar.raise_()  # Ensure it's on top
        
        splitter.addWidget(center_container)
        
        # === RIGHT PANE: Results ===
        right_pane = self._create_right_pane()
        splitter.addWidget(right_pane)
        
        # Set splitter proportions
        splitter.setSizes([380, 700, 380])
        splitter.setStretchFactor(0, 0)  # Left fixed
        splitter.setStretchFactor(1, 1)  # Center stretches
        splitter.setStretchFactor(2, 0)  # Right fixed
        
        main_layout.addWidget(splitter, 1)
        
        # Status bar
        self.statusBar().showMessage("The grid awaits your text...")
        self.statusBar().setStyleSheet(theme.get_status_muted_style())
    
    def _create_left_pane(self) -> QWidget:
        """Create left control pane with unified workflow (no tabs)."""
        from PyQt6.QtWidgets import QScrollArea
        
        # Scroll container
        scroll = QScrollArea()
        scroll.setMaximumWidth(380)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        # Content widget
        pane = QWidget()
        pane.setObjectName("LeftPane")
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(24)  # Visual Liturgy: spacing-lg (24px)
        
        # Style as floating card (scoped to allow descendant archetype selectors)
        pane.setStyleSheet(f"QWidget#LeftPane {{ {theme.get_tablet_style()} }}")
        theme.apply_tablet_shadow(pane)
        
        # === SECTION 1: Text Source ===
        source_group = QGroupBox("📄 Text Source")
        source_group.setStyleSheet(theme.get_exegesis_group_style())
        source_layout = QVBoxLayout(source_group)
        source_layout.setSpacing(8)  # Visual Liturgy: spacing-sm (8px)
        
        source_layout.setSpacing(8)  # Visual Liturgy: spacing-sm (8px)
        
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        
        self._btn_load = QPushButton("📁 File")
        self._btn_load.setMinimumHeight(40)
        self._btn_load.setCursor(Qt.CursorShape.PointingHandCursor)
        theme.set_archetype(self._btn_load, "seeker")
        self._btn_load.clicked.connect(self._on_load_document)
        btn_row.addWidget(self._btn_load)
        
        self._btn_paste = QPushButton("📋 Paste")
        self._btn_paste.setMinimumHeight(40)
        self._btn_paste.setCursor(Qt.CursorShape.PointingHandCursor)
        theme.set_archetype(self._btn_paste, "seeker")
        self._btn_paste.clicked.connect(self._on_paste_text)
        btn_row.addWidget(self._btn_paste)
        source_layout.addLayout(btn_row)
        
        self._btn_database = QPushButton("📚 Load from Database")
        self._btn_database.setMinimumHeight(40)
        self._btn_database.setCursor(Qt.CursorShape.PointingHandCursor)
        theme.set_archetype(self._btn_database, "seeker")
        self._btn_database.clicked.connect(self._on_load_from_database)
        source_layout.addWidget(self._btn_database)
        
        self._letter_count_label = QLabel("Letters: 0")
        self._letter_count_label.setStyleSheet(
            f"font-weight: 700; font-size: 11pt; color: {theme.COLORS['magus']}; padding: 4px;"
        )
        source_layout.addWidget(self._letter_count_label)
        
        layout.addWidget(source_group)
        
        # === SECTION 2: Grid Configuration ===
        grid_group = QGroupBox("📐 Grid Configuration")
        grid_group.setStyleSheet(theme.get_exegesis_group_style())
        grid_layout = QVBoxLayout(grid_group)
        grid_layout.setSpacing(8)
        grid_layout.setSpacing(8)
        
        grid_layout.addWidget(QLabel("Factor:"))
        self._factors_combo = QComboBox()
        self._factors_combo.setStyleSheet(
            f"""QComboBox {{ background-color: {theme.COLORS['light']}; border: 1px solid {theme.COLORS['border']}; border-radius: 8px; padding: 8px 12px; color: {theme.COLORS['text_primary']}; }}
                QComboBox:focus {{ border: 2px solid {theme.COLORS['focus']}; padding: 7px 11px; }}"""
        )
        self._factors_combo.currentIndexChanged.connect(self._on_factor_selected)
        grid_layout.addWidget(self._factors_combo)
        
        custom_row = QHBoxLayout()
        custom_row.setSpacing(8)
        custom_row.addWidget(QLabel("Custom:"))
        self._cols_spin = QSpinBox()
        self._cols_spin.setRange(1, 10000)
        self._cols_spin.setValue(50)
        self._cols_spin.setStyleSheet(
            f"""QSpinBox {{ background-color: {theme.COLORS['light']}; border: 1px solid {theme.COLORS['border']}; border-radius: 8px; padding: 6px 10px; color: {theme.COLORS['text_primary']}; }}
                QSpinBox:focus {{ border: 2px solid {theme.COLORS['focus']}; padding: 5px 9px; }}"""
        )
        custom_row.addWidget(self._cols_spin)
        custom_row.addWidget(QLabel("cols"))
        custom_row.addStretch()
        grid_layout.addLayout(custom_row)
        
        self._btn_apply_grid = QPushButton("Apply Grid")
        self._btn_apply_grid.setMinimumHeight(40)
        self._btn_apply_grid.setCursor(Qt.CursorShape.PointingHandCursor)
        theme.set_archetype(self._btn_apply_grid, "magus")
        self._btn_apply_grid.clicked.connect(self._on_apply_grid)
        grid_layout.addWidget(self._btn_apply_grid)
        
        layout.addWidget(grid_group)
        
        # === SECTION 3: Search Configuration ===
        search_group = QGroupBox("🔍 Search Configuration")
        search_group.setStyleSheet(theme.get_exegesis_group_style())
        search_layout = QVBoxLayout(search_group)
        search_layout.setSpacing(8)
        
        search_layout.addWidget(QLabel("Search Term:"))
        self._term_input = QLineEdit()
        self._term_input.setMinimumHeight(40)
        self._term_input.setPlaceholderText("Seek the hidden letters...")
        self._term_input.setStyleSheet(
            f"""
                QLineEdit {{
                    background-color: {theme.COLORS['light']};
                    border: 1px solid {theme.COLORS['border']};
                    border-radius: 8px;
                    padding: 8px 12px;
                    color: {theme.COLORS['text_primary']};
                }}
                QLineEdit:focus {{
                    border: 2px solid {theme.COLORS['focus']};
                    padding: 7px 11px;
                }}
            """
        )
        search_layout.addWidget(self._term_input)
        
        # Skip mode
        self._skip_group = QButtonGroup()
        
        skip_layout = QHBoxLayout()
        self._exact_radio = QRadioButton("Exact Skip:")
        self._exact_radio.setChecked(True)
        self._skip_group.addButton(self._exact_radio)
        skip_layout.addWidget(self._exact_radio)
        
        self._exact_skip_spin = QSpinBox()
        self._exact_skip_spin.setRange(1, 10000)
        self._exact_skip_spin.setValue(50)
        self._exact_skip_spin.setStyleSheet(
            f"""QSpinBox {{ background-color: {theme.COLORS['light']}; border: 1px solid {theme.COLORS['border']}; border-radius: 8px; padding: 4px 8px; color: {theme.COLORS['text_primary']}; }}
                QSpinBox:focus {{ border: 2px solid {theme.COLORS['focus']}; padding: 3px 7px; }}"""
        )
        skip_layout.addWidget(self._exact_skip_spin)
        search_layout.addLayout(skip_layout)
        
        range_layout = QHBoxLayout()
        self._range_radio = QRadioButton("Range:")
        self._skip_group.addButton(self._range_radio)
        range_layout.addWidget(self._range_radio)
        
        self._min_skip_spin = QSpinBox()
        self._min_skip_spin.setRange(1, 1000)
        self._min_skip_spin.setValue(1)
        self._min_skip_spin.setFixedWidth(60)
        self._min_skip_spin.setStyleSheet(
            f"""QSpinBox {{ background-color: {theme.COLORS['light']}; border: 1px solid {theme.COLORS['border']}; border-radius: 8px; padding: 4px 8px; color: {theme.COLORS['text_primary']}; }}
                QSpinBox:focus {{ border: 2px solid {theme.COLORS['focus']}; padding: 3px 7px; }}"""
        )
        range_layout.addWidget(self._min_skip_spin)
        
        range_layout.addWidget(QLabel("to"))
        
        self._max_skip_spin = QSpinBox()
        self._max_skip_spin.setRange(1, 10000)
        self._max_skip_spin.setValue(100)
        self._max_skip_spin.setFixedWidth(70)
        self._max_skip_spin.setStyleSheet(
            f"""QSpinBox {{ background-color: {theme.COLORS['light']}; border: 1px solid {theme.COLORS['border']}; border-radius: 8px; padding: 4px 8px; color: {theme.COLORS['text_primary']}; }}
                QSpinBox:focus {{ border: 2px solid {theme.COLORS['focus']}; padding: 3px 7px; }}"""
        )
        range_layout.addWidget(self._max_skip_spin)
        search_layout.addLayout(range_layout)
        
        # Sequence mode
        seq_layout = QHBoxLayout()
        self._seq_radio = QRadioButton("Sequence:")
        self._skip_group.addButton(self._seq_radio)
        seq_layout.addWidget(self._seq_radio)
        
        self._seq_combo = QComboBox()
        self._seq_combo.addItems(["Triangular", "Square", "Fibonacci"])
        self._seq_combo.setStyleSheet(
            f"""QComboBox {{ background-color: {theme.COLORS['light']}; border: 1px solid {theme.COLORS['border']}; border-radius: 8px; padding: 6px 10px; color: {theme.COLORS['text_primary']}; }}
                QComboBox:focus {{ border: 2px solid {theme.COLORS['focus']}; padding: 5px 9px; }}"""
        )
        seq_layout.addWidget(self._seq_combo)
        search_layout.addLayout(seq_layout)
        
        # Chain mode
        chain_layout = QHBoxLayout()
        self._chain_radio = QRadioButton("🔗 Chain")
        self._skip_group.addButton(self._chain_radio)
        chain_layout.addWidget(self._chain_radio)
        
        self._chain_reverse_check = QCheckBox("Reverse")
        self._chain_reverse_check.setToolTip("Search backwards for each letter")
        chain_layout.addWidget(self._chain_reverse_check)
        chain_layout.addStretch()
        search_layout.addLayout(chain_layout)
        
        # Direction
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Direction:"))
        self._dir_combo = QComboBox()
        self._dir_combo.addItems(["Both", "Forward", "Reverse"])
        self._dir_combo.setStyleSheet(
            f"""QComboBox {{ background-color: {theme.COLORS['light']}; border: 1px solid {theme.COLORS['border']}; border-radius: 8px; padding: 6px 10px; color: {theme.COLORS['text_primary']}; }}
                QComboBox:focus {{ border: 2px solid {theme.COLORS['focus']}; padding: 5px 9px; }}"""
        )
        dir_layout.addWidget(self._dir_combo)
        search_layout.addLayout(dir_layout)
        
        self._btn_search = QPushButton("🔍 Search")
        self._btn_search.setMinimumHeight(40)
        self._btn_search.setCursor(Qt.CursorShape.PointingHandCursor)
        theme.set_archetype(self._btn_search, "magus")
        self._btn_search.clicked.connect(self._on_search)
        search_layout.addWidget(self._btn_search)
        
        layout.addWidget(search_group)
        layout.addStretch()
        
        scroll.setWidget(pane)
        return scroll
    
    def _create_right_pane(self) -> QWidget:
        """Create right results pane - focused on results table."""
        pane = QWidget()
        pane.setObjectName("RightPane")
        pane.setMaximumWidth(380)
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)
        
        # Style as floating card (scoped to allow descendant archetype selectors)
        pane.setStyleSheet(f"QWidget#RightPane {{ {theme.get_tablet_style()} }}")
        theme.apply_tablet_shadow(pane)
        
        # Header with count
        header_layout = QHBoxLayout()
        header_label = QLabel("📊 Search Results")
        header_label.setStyleSheet(f"font-size: 14pt; font-weight: 700; color: {theme.COLORS['text_primary']};")
        header_layout.addWidget(header_label)
        
        header_layout.addStretch()
        
        self._hits_label = QLabel("0 hits")
        self._hits_label.setStyleSheet(
            f"font-weight: 600; font-size: 11pt; color: {theme.COLORS['magus']};"
        )
        header_layout.addWidget(self._hits_label)
        layout.addLayout(header_layout)
        
        # Gematria filter row
        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)
        filter_row.addWidget(QLabel("Filter by Gematria:"))
        self._gematria_filter = QLineEdit()
        self._gematria_filter.setPlaceholderText("e.g. 93")
        self._gematria_filter.setFixedWidth(80)
        self._gematria_filter.setStyleSheet(
            f"""
                QLineEdit {{
                    background-color: {theme.COLORS['light']};
                    border: 1px solid {theme.COLORS['border']};
                    border-radius: 8px;
                    padding: 6px 10px;
                    color: {theme.COLORS['text_primary']};
                }}
                QLineEdit:focus {{
                    border: 2px solid {theme.COLORS['focus']};
                    padding: 5px 9px;
                }}
            """
        )
        self._gematria_filter.textChanged.connect(self._apply_gematria_filter)
        filter_row.addWidget(self._gematria_filter)
        filter_row.addStretch()
        layout.addLayout(filter_row)
        
        # Results table (larger - takes most space)
        self._results_table = QTableWidget()
        self._results_table.setColumnCount(4)
        self._results_table.setHorizontalHeaderLabels(["Term", "Skip", "Pos", "Dir"])
        self._results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._results_table.setStyleSheet(
            f"""
                QTableWidget {{
                    background-color: {theme.COLORS['light']};
                    border: 1px solid {theme.COLORS['border']};
                    border-radius: 8px;
                    gridline-color: {theme.COLORS['border']};
                }}
                QHeaderView::section {{
                    background-color: {theme.COLORS['surface']};
                    color: {theme.COLORS['text_primary']};
                    font-weight: 600;
                    padding: 8px;
                    border: none;
                    border-bottom: 2px solid {theme.COLORS['border']};
                }}
                QTableWidget::item:selected {{
                    background-color: {theme.COLORS['magus']};
                    color: {theme.COLORS['light']};
                }}
            """
        )
        self._results_table.cellClicked.connect(self._on_result_clicked)
        layout.addWidget(self._results_table, 1)  # Stretch factor 1 - takes available space
        
        # Gematria breakdown (compact, collapsible)
        breakdown_group = QGroupBox("🔢 Selected Result")
        breakdown_group.setCheckable(True)
        breakdown_group.setChecked(True)
        breakdown_group.setStyleSheet(theme.get_exegesis_group_style())
        breakdown_layout = QVBoxLayout(breakdown_group)
        breakdown_layout.setContentsMargins(8, 12, 8, 8)
        
        self._breakdown_text = QTextEdit()
        self._breakdown_text.setReadOnly(True)
        self._breakdown_text.setMaximumHeight(180)
        self._breakdown_text.setStyleSheet(
            f"""
                QTextEdit {{
                    background-color: {theme.COLORS['light']};
                    border: 1px solid {theme.COLORS['border']};
                    border-radius: 8px;
                    font-family: 'JetBrains Mono', 'Courier New', monospace;
                    font-size: 10px;
                    color: {theme.COLORS['text_primary']};
                    padding: 8px;
                }}
            """
        )
        breakdown_layout.addWidget(self._breakdown_text)
        layout.addWidget(breakdown_group)
        
        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        
        self._btn_export = QPushButton("Export")
        self._btn_export.setMinimumHeight(40)
        self._btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        theme.set_archetype(self._btn_export, "scribe")
        self._btn_export.clicked.connect(self._on_export)
        btn_row.addWidget(self._btn_export)
        
        self._btn_clear = QPushButton("Clear")
        self._btn_clear.setMinimumHeight(40)
        self._btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        theme.set_archetype(self._btn_clear, "destroyer")
        self._btn_clear.clicked.connect(self._on_clear)
        btn_row.addWidget(self._btn_clear)
        
        layout.addLayout(btn_row)
        
        return pane
    
    # === Event Handlers ===
    
    def _on_load_document(self):
        """Load text from a file."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Text File", "",
            "Text Files (*.txt);;All Files (*)"
        )
        if path:
            text = None
            # Try multiple encodings
            encodings = ['utf-8', 'utf-16', 'cp1252', 'latin-1', 'iso-8859-1']
            for encoding in encodings:
                try:
                    with open(path, 'r', encoding=encoding) as f:
                        text = f.read()
                    logger.info(f"Loaded file with {encoding} encoding")
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            
            if text is not None:
                self._load_text(text, source=path)
            else:
                QMessageBox.warning(self, "Error", "Failed to decode file with any supported encoding")
    
    def _on_paste_text(self):
        """Show dialog to paste raw text."""
        from PyQt6.QtWidgets import QDialog, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Paste Text")
        dialog.setMinimumSize(500, 400)
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("Paste your text here...")
        layout.addWidget(text_edit)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        ok_btn = buttons.button(QDialogButtonBox.StandardButton.Ok)
        cancel_btn = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        if ok_btn:
            theme.set_archetype(ok_btn, "magus")
        if cancel_btn:
            theme.set_archetype(cancel_btn, "ghost")
        layout.addWidget(buttons)
        
        if dialog.exec():
            text = text_edit.toPlainText()
            if text.strip():
                self._load_text(text, source="Pasted Text")
    
    def _on_load_from_database(self):
        """Load text from Document Manager database."""
        from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QListWidget, QListWidgetItem
        
        # Fetch documents from database
        try:
            docs = get_all_documents_metadata()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load documents: {e}")
            return
        
        if not docs:
            QMessageBox.information(self, "No Documents", "No documents found in database")
            return
        
        # Create selector dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Document")
        dialog.setMinimumSize(500, 400)
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel(f"📚 {len(docs)} documents available:"))
        
        # Document list
        doc_list = QListWidget()
        doc_list.setStyleSheet(
            f"""
                QListWidget::item {{ padding: 8px; }}
                QListWidget::item:selected {{ background-color: {theme.COLORS['magus']}; color: {theme.COLORS['light']}; }}
            """
        )
        
        # Sort by title
        sorted_docs = sorted(docs, key=lambda d: d.title or "Untitled")
        for doc in sorted_docs:
            item = QListWidgetItem(f"{doc.title or 'Untitled'}")
            item.setData(Qt.ItemDataRole.UserRole, doc.id)
            doc_list.addItem(item)
        
        layout.addWidget(doc_list)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        ok_btn = buttons.button(QDialogButtonBox.StandardButton.Ok)
        cancel_btn = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        if ok_btn:
            theme.set_archetype(ok_btn, "magus")
        if cancel_btn:
            theme.set_archetype(cancel_btn, "ghost")
        layout.addWidget(buttons)
        
        if dialog.exec() and doc_list.currentItem():
            doc_id = doc_list.currentItem().data(Qt.ItemDataRole.UserRole)
            try:
                document = get_document(doc_id)
                if document and document.raw_content:
                    self._load_text(document.raw_content, source=document.title or "Database Document")
                elif document and document.content:
                    # Strip HTML if raw_content not available
                    import re
                    text = re.sub(r'<[^>]+>', '', document.content)  # type: ignore[reportArgumentType, reportCallIssue, reportUnknownVariableType]
                    self._load_text(text, source=document.title or "Database Document")
                else:
                    QMessageBox.warning(self, "Error", "Document has no text content")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load document: {e}")
    
    def _load_text(self, text: str, source: str = ""):
        """Process and display text."""
        self._stripped_text, self._position_map = self._service.prepare_text(text)
        
        letter_count = len(self._stripped_text)
        self._letter_count_label.setText(f"Letters: {letter_count:,}")
        
        # Populate grid factors
        self._factors_combo.clear()
        factors = self._service.get_grid_factors(letter_count)
        for cols, rows in factors:
            self._factors_combo.addItem(f"{cols} × {rows}", cols)
        
        # Set initial grid
        if factors:
            initial_cols = factors[0][0]
            self._cols_spin.setValue(initial_cols)
            self._grid_view.set_grid(self._stripped_text, initial_cols)
        
            self._grid_view.set_grid(self._stripped_text, initial_cols)
        
        self.statusBar().showMessage(f"Loaded: {source} ({letter_count:,} letters)")
        logger.info(f"Loaded text: {letter_count} letters from {source}")
    
    def _on_factor_selected(self, index: int):
        """Apply selected factor as grid columns."""
        if index >= 0:
            cols = self._factors_combo.currentData()
            if cols:
                self._cols_spin.setValue(cols)
    
    def _on_apply_grid(self):
        """Apply custom grid configuration."""
        cols = self._cols_spin.value()
        if self._stripped_text:
            self._grid_view.clear_highlights()
        if self._stripped_text:
            self._grid_view.clear_highlights()
            self._grid_view.set_grid(self._stripped_text, cols)
            self.statusBar().showMessage(f"Grid: {cols} columns")
    
    def _on_search(self):
        """Execute ELS or sequence search."""
        term = self._term_input.text().strip()
        if not term:
            QMessageBox.warning(self, "Error", "Please enter a search term")
            return
        
        if not self._stripped_text:
            QMessageBox.warning(self, "Error", "Please load text first")
            return
        
        # Get search parameters
        direction = self._dir_combo.currentText().lower()
        
        if self._exact_radio.isChecked():
            skip = self._exact_skip_spin.value()
            summary = self._service.search_els(
                self._stripped_text, term, skip=skip, direction=direction
            )
        elif self._range_radio.isChecked():
            min_skip = self._min_skip_spin.value()
            max_skip = self._max_skip_spin.value()
            summary = self._service.search_els(
                self._stripped_text, term,
                min_skip=min_skip, max_skip=max_skip,
                direction=direction
            )
        elif self._seq_radio.isChecked():
            seq_type = self._seq_combo.currentText().lower()
            summary = self._service.search_sequence(
                self._stripped_text, term,
                sequence_type=seq_type, direction=direction
            )
        elif self._chain_radio.isChecked():
            # Chain search - opens separate results window
            reverse = self._chain_reverse_check.isChecked()
            chain_summary = self._service.search_chain(self._stripped_text, term, reverse=reverse)
            
            direction_str = "reverse" if reverse else "forward"
            self.statusBar().showMessage(f"Found {len(chain_summary.results)} chain paths ({direction_str}) for '{term}'")
            
            if chain_summary.results:
                from .chain_results_window import ChainResultsWindow
                # Pass window manager for export functionality
                self._chain_results_window = ChainResultsWindow(chain_summary, window_manager=self.window_manager)
                self._chain_results_window.result_selected.connect(self._on_chain_result_selected)
                self._chain_results_window.show()
            return  # Don't continue to normal results display
        
        self._all_results = summary.results
        self._current_results = summary.results
        self._current_results = summary.results
        self._gematria_filter.clear()  # Clear filter on new search
        self._display_results()
        
        self.statusBar().showMessage(f"Found {len(self._current_results)} matches for '{term}'")
    
    def _apply_gematria_filter(self):
        """Filter displayed results by gematria value."""
        if not hasattr(self, '_all_results'):
            return
        
        filter_text = self._gematria_filter.text().strip()
        
        if not filter_text:
            # Show all results
            self._current_results = self._all_results
        else:
            try:
                target_gematria = int(filter_text)
                # Calculate gematria for each result and filter
                calc = TQGematriaCalculator()
                filtered = []
                for result in self._all_results:
                    # Calculate total gematria for this result's intervening letters
                    result_gematria = 0
                    if self._stripped_text:
                        segments = self._service.extract_intervening_letters(
                            self._stripped_text.upper(),
                            result.letter_positions,
                            result.term
                        )
                        for seg in segments:
                            if seg.letters:
                                result_gematria += calc.calculate(seg.letters)
                    
                    term_gematria = calc.calculate(result.term)
                    total = term_gematria + result_gematria
                    
                    if total == target_gematria:
                        filtered.append(result)
                
                self._current_results = filtered
            except ValueError:
                # Invalid input, show all
                self._current_results = self._all_results
        
        self._display_results()
    
    def _display_results(self):
        """Populate results table."""
        self._results_table.setRowCount(len(self._current_results))
        
        for i, result in enumerate(self._current_results):
            self._results_table.setItem(i, 0, QTableWidgetItem(result.term))
            self._results_table.setItem(i, 1, QTableWidgetItem(str(result.skip)))
            self._results_table.setItem(i, 2, QTableWidgetItem(str(result.start_pos)))
            self._results_table.setItem(i, 3, QTableWidgetItem(result.direction[:3]))
        
        all_count = len(self._all_results) if hasattr(self, '_all_results') else len(self._current_results)
        if len(self._current_results) < all_count:
            self._hits_label.setText(f"{len(self._current_results)} / {all_count} hits")
        else:
            self._hits_label.setText(f"{len(self._current_results)} hits")
        
        # Highlight all results on grid
        self._grid_view.clear_highlights()
        for i, result in enumerate(self._current_results):
            self._grid_view.highlight_sequence(result.letter_positions, i)
    
    def _on_result_clicked(self, row: int, col: int):
        """Center grid on clicked result and show gematria breakdown."""
        if 0 <= row < len(self._current_results):
            result = self._current_results[row]
            if result.letter_positions:
                self._grid_view.center_on_position(result.letter_positions[0])
                self._show_gematria_breakdown(result)
    
    def _on_chain_result_selected(self, positions: list):
        """Handle chain result selection - highlight path on grid."""
        self._grid_view.clear_highlights()
        self._grid_view.highlight_sequence(positions, 0)
        if positions:
            self._grid_view.center_on_position(positions[0])
    
    def _on_export(self):
        """Export results to Document Editor."""
        if not self._current_results:
            QMessageBox.information(self, "No Results", "No results to export")
            return
        
        # Build formatted HTML report
        calc = TQGematriaCalculator()
        lines = []
        
        # Header
        term = self._current_results[0].term if self._current_results else "ELS"
        term_gematria = calc.calculate(term)
        lines.append(f"<h1>🔮 ELS Search Report: {term}</h1>")
        lines.append(f"<p><strong>Term Gematria:</strong> {term_gematria}</p>")
        lines.append(f"<p><strong>Total Matches:</strong> {len(self._current_results)}</p>")
        lines.append("<hr>")
        
        # Each result with gematria breakdown
        for i, result in enumerate(self._current_results, 1):
            lines.append(f"<h2>Match {i}: Skip {result.skip}, Position {result.start_pos} ({result.direction})</h2>")
            
            # Extract segments and calculate gematria
            if self._stripped_text:
                segments = self._service.extract_intervening_letters(
                    self._stripped_text.upper(),
                    result.letter_positions,
                    result.term
                )
                
                term_value = calc.calculate(result.term)
                skip_total = 0
                
                lines.append("<table border='1' cellpadding='5'>")
                lines.append("<tr><th>Segment</th><th>Letters</th><th>Gematria</th></tr>")
                lines.append(f"<tr><td><strong>Term: {result.term}</strong></td><td>—</td><td><strong>{term_value}</strong></td></tr>")
                
                for seg in segments:
                    seg_value = calc.calculate(seg.letters) if seg.letters else 0
                    skip_total += seg_value
                    display_letters = seg.letters[:30] + "..." if len(seg.letters) > 30 else seg.letters
                    lines.append(f"<tr><td>{seg.from_letter} → {seg.to_letter}</td><td>{display_letters}</td><td>{seg_value}</td></tr>")
                
                lines.append(f"<tr><td><strong>Skip Total</strong></td><td>—</td><td><strong>{skip_total}</strong></td></tr>")
                lines.append(f"<tr><td><strong>TOTAL</strong></td><td>—</td><td><strong>{term_value + skip_total}</strong></td></tr>")
                lines.append("</table>")
                lines.append("<br>")
        
        html_content = "\n".join(lines)
        
        # Open in Document Editor
        if self.window_manager:
            from shared.signals.navigation_bus import navigation_bus
            
            navigation_bus.request_window.emit(
                "document_editor",
                {"allow_multiple": True, "window_manager": self.window_manager}
            )
            
            # Find the window instance
            count = self.window_manager._window_counters.get("document_editor", 0)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
            win_id = f"document_editor_{count}"
            editor_window = self.window_manager.get_window(win_id)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
            
            if editor_window and hasattr(editor_window, 'editor'):
                editor_window.setWindowTitle(f"ELS Report - {term}")
                editor_window.editor.set_html(html_content)
                editor_window.is_modified = True  # Mark as needing save
                editor_window.show()
            
            self.statusBar().showMessage("Exported to Document Editor")
        else:
            QMessageBox.warning(self, "Error", "Window manager not available")
    
    def _on_clear(self):
        """Clear search results."""
        self._current_results.clear()
        self._results_table.setRowCount(0)
        self._hits_label.setText("0 hits")
        self._grid_view.clear_highlights()
        self._breakdown_text.clear()
    
    def _show_gematria_breakdown(self, result: ELSResult):
        """Display gematria breakdown for selected result."""
        if not self._stripped_text or not result.letter_positions:
            return
        
        calc = TQGematriaCalculator()
        lines = []
        
        # Calculate term gematria
        term_value = calc.calculate(result.term)
        lines.append(f"Search Term: {result.term}")
        lines.append(f"Term Gematria: {term_value}")
        lines.append("-" * 30)
        
        # Extract and calculate intervening segments
        segments = self._service.extract_intervening_letters(
            self._stripped_text.upper(),
            result.letter_positions,
            result.term
        )
        
        skip_total = 0
        for seg in segments:
            seg_value = calc.calculate(seg.letters) if seg.letters else 0
            skip_total += seg_value
            
            # Truncate long letter sequences for display
            display_letters = seg.letters[:20] + "..." if len(seg.letters) > 20 else seg.letters
            lines.append(f"{seg.from_letter} → {seg.to_letter}: {display_letters}")
            lines.append(f"  Value: {seg_value}")
        
        lines.append("-" * 30)
        lines.append(f"Skip Letters Total: {skip_total}")
        lines.append(f"Term + Skip: {term_value + skip_total}")
        
        self._breakdown_text.setText("\n".join(lines))
