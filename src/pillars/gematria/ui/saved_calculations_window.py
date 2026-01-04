"""Saved calculations browser window."""
import json
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QTextEdit,
    QComboBox, QCheckBox, QSplitter, QWidget, QMessageBox,
    QHeaderView, QFrame, QGraphicsDropShadowEffect, QGridLayout,
    QStackedWidget, QScrollArea, QMenu, QDialog, QFormLayout,
    QPlainTextEdit, QInputDialog, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from typing import List, Optional

from ..services import CalculationService
from ..models import CalculationRecord
from shared.ui import VirtualKeyboard, get_shared_virtual_keyboard
from shared.ui.rich_text_editor import RichTextEditor

class NumericTableWidgetItem(QTableWidgetItem):
    """Table item that sorts numerically."""
    def __lt__(self, other):
        try:
            return float(self.text()) < float(other.text())
        except ValueError:
            return super().__lt__(other)


class SavedCalculationsWindow(QMainWindow):
    """Window for browsing and managing saved calculations."""
    
    def __init__(self, window_manager=None, parent=None, initial_value=None, **kwargs):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """Initialize the saved calculations browser."""
        super().__init__(parent)
        self.window_manager = window_manager
        self.calculation_service = CalculationService()
        self.current_records: List[CalculationRecord] = []
        self.selected_record: Optional[CalculationRecord] = None
        
        # Virtual keyboard
        self.virtual_keyboard: Optional[VirtualKeyboard] = None
        self.keyboard_visible: bool = False
        
        self._setup_ui()
        self._reset_results_view()
        
        if initial_value is not None:
            self.value_input.setText(str(initial_value))
            self._search()
    
    def _setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Records of Karnak")
        self.setMinimumSize(1100, 800)
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)

        central = QWidget()
        central.setObjectName("CentralContainer")
        self.setCentralWidget(central)
        
        # Background Pattern
        bg_path = "/home/burkettdaniel927/.gemini/antigravity/brain/2a906893-16d8-4452-966d-10a7777e72da/gematria_bg_pattern_1766530853546.png"
        central.setStyleSheet(f"""
            QWidget#CentralContainer {{
                background-image: url("{bg_path}");
                background-repeat: repeat;
                background-position: center;
                background-color: #f8fafc;
            }}
        """)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # --- LEFT PANEL: NAVIGATION & FILTERS ---
        left_panel = QFrame()
        left_panel.setObjectName("ControlPanel")
        left_panel.setMinimumWidth(400)
        left_panel.setStyleSheet("""
            QFrame#ControlPanel {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 24px;
            }
        """)
        
        # Shadow for Left Panel
        l_shadow = QGraphicsDropShadowEffect()
        l_shadow.setBlurRadius(20)
        l_shadow.setColor(QColor(0, 0, 0, 30))
        l_shadow.setOffset(4, 4)
        left_panel.setGraphicsEffect(l_shadow)
        
        l_layout = QVBoxLayout(left_panel)
        l_layout.setContentsMargins(25, 30, 25, 30)
        l_layout.setSpacing(15)
        
        # Header
        header_layout = QVBoxLayout()
        title_label = QLabel("RECORDS OF KARNAK")
        title_label.setStyleSheet("""
            color: #0f172a; font-size: 22pt; font-weight: 900; letter-spacing: -0.5px;
        """)
        subtitle_label = QLabel("AN ARCHIVE OF NUMERIC TRUTH")
        subtitle_label.setStyleSheet("""
            color: #64748b; font-size: 7pt; font-weight: 800; letter-spacing: 0.3em;
        """)
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        l_layout.addLayout(header_layout)
        
        l_layout.addSpacing(10)
        
        # Search Components
        search_section = QVBoxLayout()
        search_section.setSpacing(8)
        
        s_label = QLabel("FIND RECORD")
        s_label.setStyleSheet("font-size: 8pt; font-weight: 800; color: #94a3b8; letter-spacing: 0.1em;")
        search_section.addWidget(s_label)
        
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search phrases or notes...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                font-size: 11pt; padding: 10px; border: 2px solid #e2e8f0; border-radius: 10px; background: #f8fafc;
            }
            QLineEdit:focus { border-color: #3b82f6; background: white; }
        """)
        self.search_input.returnPressed.connect(self._search)
        search_row.addWidget(self.search_input)
        
        self.keyboard_toggle = QPushButton("⌨️")
        self.keyboard_toggle.setFixedSize(40, 40)
        self.keyboard_toggle.setStyleSheet("""
            QPushButton { font-size: 14pt; background: white; border: 2px solid #3b82f6; border-radius: 10px; color: #3b82f6; }
            QPushButton:hover { background: #3b82f6; color: white; }
        """)
        self.keyboard_toggle.clicked.connect(self._toggle_keyboard)
        search_row.addWidget(self.keyboard_toggle)
        
        # Search Mode Selector
        self.search_mode_combo = QComboBox()
        self.search_mode_combo.addItems(["General", "Exact", "Regex", "Wildcard"])
        self.search_mode_combo.setToolTip("Select Search Mode")
        self.search_mode_combo.setStyleSheet("""
            QComboBox { font-size: 10pt; padding: 5px; border: 2px solid #e2e8f0; border-radius: 10px; background: white; min-width: 80px; }
            QComboBox::drop-down { border: none; }
        """)
        self.search_mode_combo.setCurrentText("Exact")
        search_row.addWidget(self.search_mode_combo)
        
        search_section.addLayout(search_row)
        
        # Grid for smaller filters
        filter_grid = QGridLayout()
        filter_grid.setSpacing(10)
        
        v_label = QLabel("VALUE")
        v_label.setStyleSheet("font-size: 8pt; font-weight: 800; color: #94a3b8;")
        filter_grid.addWidget(v_label, 0, 0)
        
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("####")
        self.value_input.setStyleSheet("font-size: 10pt; padding: 8px; border: 2px solid #e2e8f0; border-radius: 8px;")
        filter_grid.addWidget(self.value_input, 1, 0)
        self.value_input.returnPressed.connect(self._search)
        
        lang_label = QLabel("LANGUAGE")
        lang_label.setStyleSheet("font-size: 8pt; font-weight: 800; color: #94a3b8;")
        filter_grid.addWidget(lang_label, 0, 1)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["All Languages", "Hebrew", "Greek", "English"])
        self.language_combo.setStyleSheet("""
            QComboBox { font-size: 10pt; padding: 8px; border: 2px solid #e2e8f0; border-radius: 8px; background: white; }
        """)
        self.language_combo.currentTextChanged.connect(self._search)
        filter_grid.addWidget(self.language_combo, 1, 1)
        
        l_layout.addLayout(search_section)
        l_layout.addLayout(filter_grid)
        
        self.favorites_checkbox = QCheckBox("⭐ EXHIBIT FAVORITES ONLY")
        self.favorites_checkbox.setStyleSheet("color: #475569; font-size: 9pt; font-weight: 700;")
        self.favorites_checkbox.stateChanged.connect(self._search)
        l_layout.addWidget(self.favorites_checkbox)
        
        search_btn = QPushButton("CONSULT THE ARCHIVE")
        search_btn.clicked.connect(self._search)
        search_btn.setMinimumHeight(50)
        search_btn.setStyleSheet("""
            QPushButton { background: #1e293b; color: white; font-weight: 800; font-size: 11pt; border-radius: 12px; }
            QPushButton:hover { background: #334155; }
        """)
        l_layout.addWidget(search_btn)
        
        l_layout.addSpacing(10)
        
        # Table Section
        table_label = QLabel("CHRONICLE ENTRIES")
        table_label.setStyleSheet("font-size: 8pt; font-weight: 800; color: #94a3b8; letter-spacing: 0.1em;")
        l_layout.addWidget(table_label)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Text", "Value", "⭐"])
        self.results_table.horizontalHeader().setStretchLastSection(False)
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.results_table.setColumnWidth(2, 40)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.itemSelectionChanged.connect(self._on_selection_changed)
        self.results_table.setSortingEnabled(True)  # Enable Sorting
        
        # Context Menu
        self.results_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self._show_context_menu)
        self.results_table.setStyleSheet("""
            QTableWidget { background: white; border: 1px solid #e2e8f0; border-radius: 12px; gridline-color: #f1f5f9; }
            QTableWidget::item { padding: 8px; color: #334155; border-bottom: 1px solid #f1f5f9; }
            QHeaderView::section { background: #f8fafc; font-weight: 700; border: none; padding: 8px; color: #64748b; }
        """)
        l_layout.addWidget(self.results_table, 1)  # Give table weight
        
        # --- RIGHT PANEL: DETAILED INSCRIPTION ---
        right_panel = QFrame()
        right_panel.setObjectName("DetailsPanel")
        right_panel.setStyleSheet("""
            QFrame#DetailsPanel {
                background-color: rgba(255, 255, 255, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 24px;
            }
        """)
        
        r_layout = QVBoxLayout(right_panel)
        r_layout.setContentsMargins(0, 0, 0, 0)
        r_layout.setSpacing(0)
        
        self.details_stack = QStackedWidget()
        r_layout.addWidget(self.details_stack)
        
        # --- MODE 0: SUMMARY PAGE ---
        summary_page = QWidget()
        s_layout = QVBoxLayout(summary_page)
        s_layout.setContentsMargins(35, 40, 35, 40)
        s_layout.setSpacing(20)
        
        summary_title = QLabel("REVELATION SUMMARY")
        summary_title.setStyleSheet("font-size: 10pt; font-weight: 800; color: #0f172a; letter-spacing: 0.15em;")
        s_layout.addWidget(summary_title)
        
        # Summary Content Area
        self.summary_display = QTextEdit()
        self.summary_display.setReadOnly(True)
        self.summary_display.setStyleSheet("""
            QTextEdit { 
                background: rgba(255, 255, 255, 0.4); 
                border: none; 
                font-family: 'Inter', 'Segoe UI', serif; 
                font-size: 12pt; 
                color: #1e293b;
                line-height: 1.6;
            }
        """)
        s_layout.addWidget(self.summary_display)
        
        # Summary Actions
        s_actions = QHBoxLayout()
        s_actions.setSpacing(15)
        
        self.edit_notes_btn = QPushButton("NOTE REVISION")
        self.edit_notes_btn.setMinimumHeight(50)
        self.edit_notes_btn.setEnabled(False)
        self.edit_notes_btn.setStyleSheet("""
            QPushButton:enabled { background: #3b82f6; color: white; font-weight: 800; border-radius: 12px; }
            QPushButton:enabled:hover { background: #2563eb; }
            QPushButton:disabled { background: #f1f5f9; color: #cbd5e1; border: 1px solid #e2e8f0; }
        """)
        self.edit_notes_btn.clicked.connect(self._enter_revision_mode)
        s_actions.addWidget(self.edit_notes_btn, 2)
        
        self.favorite_btn = QPushButton("⭐")
        self.favorite_btn.setMinimumHeight(50)
        self.favorite_btn.setEnabled(False)
        self.favorite_btn.setStyleSheet("""
            QPushButton:enabled { background: #f59e0b; color: white; font-weight: 700; border-radius: 12px; }
            QPushButton:enabled:hover { background: #d97706; }
            QPushButton:disabled { background: #f1f5f9; color: #cbd5e1; border: 1px solid #e2e8f0; }
        """)
        self.favorite_btn.clicked.connect(self._toggle_favorite)
        s_actions.addWidget(self.favorite_btn, 1)
        
        self.delete_btn = QPushButton("EXPUNGE")
        self.delete_btn.setMinimumHeight(50)
        self.delete_btn.setEnabled(False)
        self.delete_btn.setStyleSheet("""
            QPushButton:enabled { background: #ef4444; color: white; font-weight: 700; border-radius: 12px; }
            QPushButton:enabled:hover { background: #dc2626; }
            QPushButton:disabled { background: #f1f5f9; color: #cbd5e1; border: 1px solid #e2e8f0; }
        """)
        self.delete_btn.clicked.connect(self._delete_calculation)
        s_actions.addWidget(self.delete_btn, 1)
        
        s_layout.addLayout(s_actions)
        self.details_stack.addWidget(summary_page)
        
        # --- MODE 1: REVISION PAGE (THE FORGE) ---
        revision_page = QWidget()
        rev_layout = QVBoxLayout(revision_page)
        rev_layout.setContentsMargins(35, 40, 35, 40)
        rev_layout.setSpacing(20)
        
        rev_title = QLabel("THE FORGE: NOTE REVISION")
        rev_title.setStyleSheet("font-size: 10pt; font-weight: 800; color: #3b82f6; letter-spacing: 0.15em;")
        rev_layout.addWidget(rev_title)
        
        self.notes_editor = RichTextEditor(show_ui=True)
        rev_layout.addWidget(self.notes_editor)
        
        rev_actions = QHBoxLayout()
        rev_actions.setSpacing(15)
        
        self.commit_btn = QPushButton("COMMIT REVISION")
        self.commit_btn.setMinimumHeight(50)
        self.commit_btn.setStyleSheet("""
            QPushButton { background: #10b981; color: white; font-weight: 800; border-radius: 12px; }
            QPushButton:hover { background: #059669; }
        """)
        self.commit_btn.clicked.connect(self._commit_revision)
        rev_actions.addWidget(self.commit_btn, 1)
        
        self.cancel_btn = QPushButton("CANCEL")
        self.cancel_btn.setMinimumHeight(50)
        self.cancel_btn.setStyleSheet("""
            QPushButton { background: #64748b; color: white; font-weight: 800; border-radius: 12px; }
            QPushButton:hover { background: #475569; }
        """)
        self.cancel_btn.clicked.connect(self._cancel_revision)
        rev_actions.addWidget(self.cancel_btn, 1)
        
        rev_layout.addLayout(rev_actions)
        self.details_stack.addWidget(revision_page)
        
        # Add to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([500, 500])

        # Status
        self.status_label = QLabel("The archive is silent. Consult the records...")
        self.status_label.setStyleSheet("color: #94a3b8; font-size: 9pt; font-style: italic;")
        l_layout.addWidget(self.status_label)
        
        # Keyboard init
        self.virtual_keyboard = get_shared_virtual_keyboard(self)
        self.virtual_keyboard.set_target_input(self.search_input)
    
    def _reset_results_view(self):
        """Show an empty table until the user performs a search."""
        self.current_records = []
        self.selected_record = None
        self.results_table.setRowCount(0)
        self.notes_editor.clear()
        self.summary_display.clear()
        self.details_stack.setCurrentIndex(0)
        self.edit_notes_btn.setEnabled(False)
        self.favorite_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.status_label.setText("Ready - enter a search to load calculations")
    
    def _search(self):
        """Search calculations based on current filters."""
        search_text = self.search_input.text().strip()
        language = self.language_combo.currentText()
        if language == "All Languages":
            language = None
        favorites_only = self.favorites_checkbox.isChecked()
        
        # Parse value input
        value_text = self.value_input.text().strip()
        value = None
        if value_text:
            try:
                value = int(value_text)
            except ValueError:
                QMessageBox.warning(self, "Invalid Value", f"'{value_text}' is not a valid number")
                return

        if not any([search_text, language, value is not None, favorites_only]):
            self._reset_results_view()
            self.status_label.setText("Add text, value, language, or favorites filter before searching.")
            return
        
        try:
            self.current_records = self.calculation_service.search_calculations(
                query=search_text if search_text else None,
                language=language,
                value=value,
                favorites_only=favorites_only,
                limit=500,
                page=1,
                summary_only=True,
                search_mode=self.search_mode_combo.currentText()
            )
            self._update_table()
            self.status_label.setText(f"Found {len(self.current_records)} calculations")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search failed:\n{str(e)}")
    
    def _update_table(self):
        """Update the table with current records."""
        self.results_table.setSortingEnabled(False)  # Disable sorting during update
        self.results_table.setRowCount(0)
        
        for row, record in enumerate(self.current_records):
            self.results_table.insertRow(row)
            
            # Text
            self.results_table.setItem(row, 0, QTableWidgetItem(record.text))
            
            # Value
            value_item = NumericTableWidgetItem(str(record.value))
            value_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.results_table.setItem(row, 1, value_item)
            
            # Favorite
            fav_item = QTableWidgetItem("⭐" if record.is_favorite else "")
            fav_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(row, 2, fav_item)
            
        self.results_table.setSortingEnabled(True)  # Re-enable sorting
    
    def _on_selection_changed(self):
        """Handle table selection change."""
        selected_rows = self.results_table.selectedItems()
        if not selected_rows:
            self.selected_record = None
            self.notes_editor.clear()
            self.favorite_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            return
        
        # Get the row index
        row = self.results_table.currentRow()
        if 0 <= row < len(self.current_records):
            record = self.current_records[row]

            # Fetch full record details on demand
            if record and record.id:
                try:
                    full_record = self.calculation_service.get_calculation(record.id)
                except Exception:
                    full_record = None
                if full_record:
                    record = full_record
                    self.current_records[row] = full_record

            self.selected_record = record
            self._display_details(self.selected_record)
            self.edit_notes_btn.setEnabled(True)
            self.favorite_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
    
    def _display_details(self, record: CalculationRecord):
        """Populate the summary view and prepare the editor."""
        self.details_stack.setCurrentIndex(0)  # Always start with summary
        
        # Format Summary
        summary = []
        summary.append(f"<h1 style='color:#0f172a; margin-bottom:0;'>{record.text}</h1>")
        summary.append(f"<p style='color:#3b82f6; font-size:18pt; font-weight:bold; margin-top:0;'>Total Value: {record.value}</p>")
        summary.append("<hr style='border:1px solid #e2e8f0;'>")
        # Parse Language Broad Category (e.g. "English (TQ)" -> "English")
        lang_display = record.language.split('(')[0].strip()
        summary.append(f"<p><b>Method:</b> {record.method}</p>")
        summary.append(f"<p><b>Language:</b> {lang_display}</p>")
        summary.append(f"<p><b>Date:</b> {record.date_modified.strftime('%Y-%m-%d %H:%M')}</p>")
        summary.append("<br>")
        summary.append("<p><b>NOTES:</b></p>")
        if record.notes:
            summary.append(f"<div style='color:#334155;'>{record.notes}</div>")
        else:
            summary.append("<p style='color:#94a3b8; font-style:italic;'>No notes recorded for this revelation.</p>")
            
        self.summary_display.setHtml("".join(summary))
        
        # Prepare editor (but don't show yet)
        if record.notes:
            self.notes_editor.set_html(record.notes)
        else:
            self.notes_editor.set_text("")
        self.notes_editor.editor.setPlaceholderText(f"Revise the notes for '{record.text}'...")

    def _enter_revision_mode(self):
        """Switch to the RTF editor mode."""
        if self.selected_record:
            self.details_stack.setCurrentIndex(1)

    def _cancel_revision(self):
        """Return to summary mode without saving."""
        self.details_stack.setCurrentIndex(0)

    def _commit_revision(self):
        """Save updated notes and return to summary."""
        if not self.selected_record:
            return
            
        try:
            rtf_content = self.notes_editor.get_html()
            updated = self.calculation_service.update_calculation(
                self.selected_record.id,
                notes=rtf_content
            )
            if updated:
                self.selected_record = updated
                self._display_details(updated) # This will return to summary mode
                
                # Update local list
                for i, rec in enumerate(self.current_records):
                    if rec.id == updated.id:
                        self.current_records[i] = updated
                        break
                
                self.status_label.setText("Notes preserved in the Chronicle.")
        except Exception as e:
            QMessageBox.critical(self, "Forge Failure", f"Could not commit revision:\n{str(e)}")
            
    def _show_context_menu(self, pos):
        """Show context menu for calculation entries."""
        if not self.results_table.itemAt(pos):
            return
            
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 5px; }
            QMenu::item { padding: 8px 25px; border-radius: 4px; color: #334155; }
            QMenu::item:selected { background: #f1f5f9; color: #0f172a; }
        """)
        
        # Standard Actions
        copy_text_action = menu.addAction("📋 Copy Text")
        copy_text_action.triggered.connect(lambda: QApplication.clipboard().setText(self.selected_record.text))  # type: ignore[reportOptionalMemberAccess]
        
        copy_value_action = menu.addAction("🔢 Copy Value")
        copy_value_action.triggered.connect(lambda: QApplication.clipboard().setText(str(self.selected_record.value)))  # type: ignore[reportOptionalMemberAccess]
        
        menu.addSeparator()
        
        examine_action = menu.addAction("🔍 EXAMINE DETAILED INSCRIPTION")
        examine_action.triggered.connect(self._examine_detailed_inscription)
        
        menu.addSeparator()
        
        edit_tags_action = menu.addAction("🏷️ EDIT TAGS")
        edit_tags_action.triggered.connect(self._edit_tags)
        
        change_category_action = menu.addAction("📂 CHANGE CATEGORY")
        change_category_action.triggered.connect(self._change_category)
        
        edit_source_action = menu.addAction("📜 EDIT SOURCE")
        edit_source_action.triggered.connect(self._edit_source)
        
        menu.exec(self.results_table.mapToGlobal(pos))

    def _examine_detailed_inscription(self):
        """Show a dialog with ALL fields of the selected record."""
        if not self.selected_record:
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Detailed Inscription: {self.selected_record.text}")
        dialog.setMinimumSize(600, 700)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        header = QLabel("CHRONICLE: FULL INSCRIPTION")
        header.setStyleSheet("font-size: 11pt; font-weight: 800; color: #1e293b; letter-spacing: 0.1em;")
        layout.addWidget(header)
        
        form_container = QWidget()
        form_layout = QFormLayout(form_container)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        def add_field(label, value):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
            """
            Add field logic.
            
            Args:
                label: Description of label.
                value: Description of value.
            
            """
            val_label = QLineEdit(str(value))
            val_label.setReadOnly(True)
            val_label.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 4px; padding: 5px; background: #f8fafc;")
            form_layout.addRow(f"<b>{label}:</b>", val_label)
            
        record = self.selected_record
        add_field("ID", record.id)
        add_field("Text", record.text)
        add_field("Value", record.value)
        add_field("Language", record.language)
        add_field("Method", record.method)
        add_field("Normalized", record.normalized_text)
        add_field("Created", record.date_created.strftime("%Y-%m-%d %H:%M:%S"))
        add_field("Modified", record.date_modified.strftime("%Y-%m-%d %H:%M:%S"))
        add_field("Source", record.source)
        add_field("Category", record.category)
        add_field("Rating", f"{record.user_rating} ⭐")
        add_field("Favorite", "Yes" if record.is_favorite else "No")
        add_field("Tags", ", ".join(record.tags))
        # Length Logic: Fallback to text length if 0
        char_count = record.character_count
        if char_count == 0 and record.text:
             char_count = len(record.normalized_text) if record.normalized_text else len(record.text)
             
        add_field("Length", char_count)
        
        # Breakdown and Related IDs get text areas if long
        # Parse breakdown to show actual characters (unescaped)
        formatted_breakdown = record.breakdown
        try:
            if record.breakdown:
                data = json.loads(record.breakdown)
                # Format as: "Char (Value) + Char (Value)..."
                parts = [f"{item[0]} ({item[1]})" for item in data]
                formatted_breakdown = " + ".join(parts)
        except Exception:
            pass # Keep original if parse fails
            
        breakdown_text = QPlainTextEdit(formatted_breakdown)
        breakdown_text.setReadOnly(True)
        breakdown_text.setMinimumHeight(150)  # Expanded for better visibility
        breakdown_text.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 4px; background: #f8fafc;")
        form_layout.addRow("<b>Breakdown:</b>", breakdown_text)
        
        breakdown_text.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 4px; background: #f8fafc;")
        form_layout.addRow("<b>Breakdown:</b>", breakdown_text)
        
        # Dynamic Relations: Fetch Siblings (Same Word, Different System)
        siblings = self.calculation_service.get_siblings_by_text(record.text, exclude_id=record.id)
        if siblings:
            related_str = "\n".join([f"{s.method}: {s.value}" for s in siblings])
        else:
            related_str = "No siblings found in the archive."

        related_text = QPlainTextEdit(related_str)
        related_text.setReadOnly(True)
        related_text.setMinimumHeight(80)
        related_text.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 4px; background: #f8fafc;")
        form_layout.addRow("<b>Siblings:</b>", related_text)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(form_container)
        scroll.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 8px;")
        layout.addWidget(scroll)
        
        close_btn = QPushButton("CLOSE INSCRIPTION")
        close_btn.setMinimumHeight(45)
        close_btn.setStyleSheet("""
            QPushButton { background: #1e293b; color: white; font-weight: 700; border-radius: 10px; }
            QPushButton:hover { background: #334155; }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()

    def _edit_tags(self):
        """Open dialog to edit tags for the selected record."""
        if not self.selected_record:
            return
            
        current_tags = ", ".join(self.selected_record.tags)
        new_tags_str, ok = QInputDialog.getText(
            self, 
            "Edit Tags", 
            "Enter tags (comma separated):", 
            QLineEdit.EchoMode.Normal, 
            current_tags
        )
        
        if ok and new_tags_str != current_tags:
            tags = [t.strip() for t in new_tags_str.split(',') if t.strip()]
            updated = self.calculation_service.update_calculation(
                self.selected_record.id,
                tags=tags
            )
            if updated:
                self._update_local_record(updated)
                QMessageBox.information(self, "Tags Updated", "The tags have been refined.")

    def _change_category(self):
        """Open dialog to change category."""
        if not self.selected_record:
            return
            
        current_cat = self.selected_record.category
        new_cat, ok = QInputDialog.getText(
            self, 
            "Change Category", 
            "Enter new category:", 
            QLineEdit.EchoMode.Normal, 
            current_cat
        )
        
        if ok and new_cat != current_cat:
            updated = self.calculation_service.update_calculation(
                self.selected_record.id,
                category=new_cat.strip()
            )
            if updated:
                self._update_local_record(updated)
                QMessageBox.information(self, "Category Changed", "The category has been realigned.")

    def _edit_source(self):
        """Open dialog to edit source."""
        if not self.selected_record:
            return
            
        current_src = self.selected_record.source
        new_src, ok = QInputDialog.getText(
            self, 
            "Edit Source", 
            "Enter source reference (e.g. Book, Chapter, Verse):", 
            QLineEdit.EchoMode.Normal, 
            current_src
        )
        
        if ok and new_src != current_src:
            updated = self.calculation_service.update_calculation(
                self.selected_record.id,
                source=new_src.strip()
            )
            if updated:
                self._update_local_record(updated)
                QMessageBox.information(self, "Source Updated", "The origin has been clarified.")

    def _update_local_record(self, updated_record):
        """Helper to update a record in the local list and refresh view."""
        self.selected_record = updated_record
        
        # Update list
        for i, rec in enumerate(self.current_records):
            if rec.id == updated_record.id:
                self.current_records[i] = updated_record
                break
        
        # Refresh details if currently showing Summary
        if self.details_stack.currentIndex() == 0:
            self._display_details(updated_record)
            
        # Refresh table (to update any changes visible there, though tags/cat aren't shown in main table)
        self._update_table()
    
    def _toggle_favorite(self):
        """Toggle favorite status of selected calculation."""
        if not self.selected_record or not self.selected_record.id:
            return
        
        try:
            updated = self.calculation_service.toggle_favorite(self.selected_record.id)
            if updated:
                self.selected_record = updated
                self._search()  # Refresh the table
                self._display_details(updated)
                self.status_label.setText("Favorite status updated")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update favorite:\n{str(e)}")
    
    def _delete_calculation(self):
        """Delete the selected calculation."""
        if not self.selected_record or not self.selected_record.id:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete this calculation?\n\n{self.selected_record.text} = {self.selected_record.value}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.calculation_service.delete_calculation(self.selected_record.id)
                self.selected_record = None
                self._search()  # Refresh the table
                self.notes_editor.clear()
                self.status_label.setText("Calculation deleted")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete calculation:\n{str(e)}")
    
    def _toggle_keyboard(self):
        """Toggle virtual keyboard visibility."""
        if self.virtual_keyboard:
            if self.virtual_keyboard.isVisible():
                self.virtual_keyboard.hide()
            else:
                self.virtual_keyboard.set_target_input(self.search_input)
                self.virtual_keyboard.show()
                self.virtual_keyboard.raise_()
                self.virtual_keyboard.activateWindow()