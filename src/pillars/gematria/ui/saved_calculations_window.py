"""Saved calculations browser window."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QTextEdit,
    QComboBox, QCheckBox, QSplitter, QWidget, QMessageBox,
    QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import List, Optional

from ..services import CalculationService
from ..models import CalculationRecord
from shared.ui import VirtualKeyboard


class SavedCalculationsWindow(QDialog):
    """Window for browsing and managing saved calculations."""
    
    def __init__(self, parent=None):
        """Initialize the saved calculations browser."""
        super().__init__(parent)
        self.calculation_service = CalculationService()
        self.current_records: List[CalculationRecord] = []
        self.selected_record: Optional[CalculationRecord] = None
        
        # Virtual keyboard
        self.virtual_keyboard: Optional[VirtualKeyboard] = None
        self.keyboard_visible: bool = False
        
        self._setup_ui()
        self._reset_results_view()
    
    def _setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Saved Calculations")
        self.setMinimumSize(1000, 700)
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)
        self.setModal(False)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title_label = QLabel("📚 Saved Calculations")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Search and filter controls
        filter_layout = QHBoxLayout()
        
        # Search box with keyboard toggle
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search text, notes, or source...")
        self.search_input.returnPressed.connect(self._search)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input)
        
        # Keyboard toggle button for search
        self.keyboard_toggle = QPushButton("⌨️")
        self.keyboard_toggle.setToolTip("Open virtual keyboard")
        self.keyboard_toggle.setMaximumWidth(40)
        self.keyboard_toggle.setMinimumHeight(30)
        self.keyboard_toggle.clicked.connect(self._toggle_keyboard)
        search_layout.addWidget(self.keyboard_toggle)
        
        filter_layout.addLayout(search_layout)
        
        # Value search
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Value...")
        self.value_input.setMaximumWidth(100)
        self.value_input.returnPressed.connect(self._search)
        filter_layout.addWidget(QLabel("Value:"))
        filter_layout.addWidget(self.value_input)
        
        # Language filter
        self.language_combo = QComboBox()
        self.language_combo.addItem("All Languages")
        self.language_combo.addItem("Hebrew (Standard)")
        self.language_combo.addItem("Hebrew (Sofit)")
        self.language_combo.addItem("Greek (Isopsephy)")
        self.language_combo.addItem("English (TQ)")
        self.language_combo.currentTextChanged.connect(self._search)
        filter_layout.addWidget(QLabel("Language:"))
        filter_layout.addWidget(self.language_combo)
        
        # Favorites filter
        self.favorites_checkbox = QCheckBox("Favorites Only")
        self.favorites_checkbox.stateChanged.connect(self._search)
        filter_layout.addWidget(self.favorites_checkbox)
        
        # Search button
        search_btn = QPushButton("🔍 Search")
        search_btn.clicked.connect(self._search)
        filter_layout.addWidget(search_btn)
        
        main_layout.addLayout(filter_layout)
        
        # Virtual keyboard (popup window)
        self.virtual_keyboard = VirtualKeyboard(self)
        self.virtual_keyboard.set_target_input(self.search_input)
        
        # Splitter for table and details
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Text", "Value", "Language", "Tags", "Date", "⭐"
        ])
        header = self.results_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            header.setStretchLastSection(False)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.results_table.itemSelectionChanged.connect(self._on_selection_changed)
        self.results_table.setAlternatingRowColors(True)
        
        # Set column widths
        self.results_table.setColumnWidth(0, 200)  # Text
        self.results_table.setColumnWidth(1, 80)   # Value
        self.results_table.setColumnWidth(2, 150)  # Language
        self.results_table.setColumnWidth(3, 150)  # Tags
        self.results_table.setColumnWidth(4, 150)  # Date
        self.results_table.setColumnWidth(5, 40)   # Favorite
        
        splitter.addWidget(self.results_table)
        
        # Details panel
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        details_label = QLabel("Calculation Details")
        details_font = QFont()
        details_font.setPointSize(12)
        details_font.setBold(True)
        details_label.setFont(details_font)
        details_layout.addWidget(details_label)
        
        self.details_display = QTextEdit()
        self.details_display.setReadOnly(True)
        details_layout.addWidget(self.details_display)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.favorite_btn = QPushButton("⭐ Toggle Favorite")
        self.favorite_btn.clicked.connect(self._toggle_favorite)
        self.favorite_btn.setEnabled(False)
        action_layout.addWidget(self.favorite_btn)
        
        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.clicked.connect(self._delete_calculation)
        self.delete_btn.setEnabled(False)
        action_layout.addWidget(self.delete_btn)
        
        action_layout.addStretch()
        
        details_layout.addLayout(action_layout)
        
        splitter.addWidget(details_widget)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_label = QLabel("Ready - enter a search to load calculations")
        self.status_label.setStyleSheet("color: #666;")
        main_layout.addWidget(self.status_label)
    
    def _reset_results_view(self):
        """Show an empty table until the user performs a search."""
        self.current_records = []
        self.selected_record = None
        self.results_table.setRowCount(0)
        self.details_display.clear()
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
            )
            self._update_table()
            self.status_label.setText(f"Found {len(self.current_records)} calculations")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search failed:\n{str(e)}")
    
    def _update_table(self):
        """Update the table with current records."""
        self.results_table.setRowCount(0)
        
        for row, record in enumerate(self.current_records):
            self.results_table.insertRow(row)
            
            # Text
            self.results_table.setItem(row, 0, QTableWidgetItem(record.text))
            
            # Value
            value_item = QTableWidgetItem(str(record.value))
            value_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.results_table.setItem(row, 1, value_item)
            
            # Language
            self.results_table.setItem(row, 2, QTableWidgetItem(record.language))
            
            # Tags
            tags_str = ', '.join(record.tags) if record.tags else ""
            self.results_table.setItem(row, 3, QTableWidgetItem(tags_str))
            
            # Date
            date_str = record.date_modified.strftime("%Y-%m-%d %H:%M")
            self.results_table.setItem(row, 4, QTableWidgetItem(date_str))
            
            # Favorite
            fav_item = QTableWidgetItem("⭐" if record.is_favorite else "")
            fav_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(row, 5, fav_item)
    
    def _on_selection_changed(self):
        """Handle table selection change."""
        selected_rows = self.results_table.selectedItems()
        if not selected_rows:
            self.selected_record = None
            self.details_display.clear()
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
            self.favorite_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
    
    def _display_details(self, record: CalculationRecord):
        """Display details of the selected calculation."""
        breakdown = self.calculation_service.get_breakdown_from_record(record)
        
        details = []
        details.append(f"Text: {record.text}")
        if record.normalized_text and record.normalized_text != record.text:
            details.append(f"Normalized: {record.normalized_text}")
        details.append(f"\nValue: {record.value}")
        details.append(f"Language: {record.language}")
        details.append(f"Method: {record.method}")
        details.append(f"\nCharacter Count: {record.character_count}")
        
        # Breakdown
        if breakdown:
            details.append("\nBreakdown:")
            details.append("-" * 40)
            for char, value in breakdown:
                details.append(f"  {char}  =  {value}")
            details.append("-" * 40)
        
        # Metadata
        details.append(f"\nCreated: {record.date_created.strftime('%Y-%m-%d %H:%M:%S')}")
        details.append(f"Modified: {record.date_modified.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if record.tags:
            details.append(f"\nTags: {', '.join(record.tags)}")
        
        if record.source:
            details.append(f"\nSource: {record.source}")
        
        if record.notes:
            details.append(f"\nNotes:\n{record.notes}")
        
        if record.category:
            details.append(f"\nCategory: {record.category}")
        
        if record.user_rating > 0:
            details.append(f"\nRating: {'⭐' * record.user_rating}")
        
        details.append(f"\nFavorite: {'Yes ⭐' if record.is_favorite else 'No'}")
        details.append(f"\nID: {record.id}")
        
        self.details_display.setPlainText('\n'.join(details))
    
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
                self.details_display.clear()
                self.status_label.setText("Calculation deleted")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete calculation:\n{str(e)}")
    
    def _toggle_keyboard(self):
        """Toggle virtual keyboard visibility."""
        if self.virtual_keyboard:
            if self.virtual_keyboard.isVisible():
                self.virtual_keyboard.hide()
            else:
                self.virtual_keyboard.show()
                self.virtual_keyboard.raise_()
                self.virtual_keyboard.activateWindow()
