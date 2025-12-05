"""Database management tools window for cleaning and maintaining calculation database."""
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QProgressDialog,
    QGroupBox, QTextEdit, QHeaderView, QCheckBox, QWidget, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from typing import List, Dict, Set
from collections import defaultdict

from ..services import CalculationService
from ..models import CalculationRecord


class DatabaseToolsWindow(QMainWindow):
    """Window for database maintenance and cleanup operations."""
    
    def __init__(self, parent=None):
        """Initialize the database tools window."""
        super().__init__(parent)
        self.calculation_service = CalculationService()
        self.duplicate_groups: List[List[CalculationRecord]] = []
        self.selected_for_deletion: Set[str] = set()
        
        self.setWindowTitle("Database Management Tools")
        self.setMinimumSize(1000, 700)
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)

        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("🛠️ Database Management Tools")
        title_label.setStyleSheet("""
            font-size: 22pt;
            font-weight: bold;
            color: #1e293b;
            margin-bottom: 8px;
        """)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Clean, optimize, and maintain your calculation database")
        desc_label.setStyleSheet("color: #64748b; font-size: 10pt; margin-bottom: 12px;")
        layout.addWidget(desc_label)
        
        # Statistics Section
        stats_group = QGroupBox("Database Statistics")
        stats_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                border: 2px solid #cbd5e1;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """)
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        self.stats_display.setMaximumHeight(120)
        self.stats_display.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 10pt;
                background-color: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        stats_layout.addWidget(self.stats_display)
        
        refresh_stats_btn = QPushButton("🔄 Refresh Statistics")
        refresh_stats_btn.clicked.connect(self._load_statistics)
        refresh_stats_btn.setMinimumHeight(36)
        stats_layout.addWidget(refresh_stats_btn)
        
        layout.addWidget(stats_group)
        
        # Cleanup Tools Section
        tools_group = QGroupBox("Cleanup Tools")
        tools_group.setStyleSheet(stats_group.styleSheet())
        tools_layout = QVBoxLayout(tools_group)
        
        # Find Duplicates
        dup_layout = QHBoxLayout()
        dup_label = QLabel("Find duplicate calculations (same text + language + method):")
        dup_label.setWordWrap(True)
        dup_layout.addWidget(dup_label)
        dup_layout.addStretch()
        
        find_dup_btn = QPushButton("🔍 Find Duplicates")
        find_dup_btn.clicked.connect(self._find_duplicates)
        find_dup_btn.setMinimumHeight(36)
        find_dup_btn.setMinimumWidth(150)
        dup_layout.addWidget(find_dup_btn)
        tools_layout.addLayout(dup_layout)
        
        # Remove Empty/Invalid Records
        empty_layout = QHBoxLayout()
        empty_label = QLabel("Remove records with empty text or invalid data:")
        empty_layout.addWidget(empty_label)
        empty_layout.addStretch()
        
        clean_empty_btn = QPushButton("🧹 Clean Empty Records")
        clean_empty_btn.clicked.connect(self._clean_empty_records)
        clean_empty_btn.setMinimumHeight(36)
        clean_empty_btn.setMinimumWidth(150)
        empty_layout.addWidget(clean_empty_btn)
        tools_layout.addLayout(empty_layout)
        
        # Sanitize Text
        sanitize_layout = QHBoxLayout()
        sanitize_label = QLabel("Normalize whitespace and remove control characters:")
        sanitize_layout.addWidget(sanitize_label)
        sanitize_layout.addStretch()
        
        sanitize_btn = QPushButton("✨ Sanitize All Text")
        sanitize_btn.clicked.connect(self._sanitize_text)
        sanitize_btn.setMinimumHeight(36)
        sanitize_btn.setMinimumWidth(150)
        sanitize_layout.addWidget(sanitize_btn)
        tools_layout.addLayout(sanitize_layout)
        
        # Rebuild Index
        rebuild_layout = QHBoxLayout()
        rebuild_label = QLabel("Rebuild search index (fixes search issues):")
        rebuild_layout.addWidget(rebuild_label)
        rebuild_layout.addStretch()
        
        rebuild_btn = QPushButton("🔧 Rebuild Index")
        rebuild_btn.clicked.connect(self._rebuild_index)
        rebuild_btn.setMinimumHeight(36)
        rebuild_btn.setMinimumWidth(150)
        rebuild_layout.addWidget(rebuild_btn)
        tools_layout.addLayout(rebuild_layout)
        
        # Delete All Entries (Dangerous!)
        delete_all_layout = QHBoxLayout()
        delete_all_label = QLabel("⚠️ Delete ALL calculations (CANNOT BE UNDONE!):")
        delete_all_label.setStyleSheet("color: #dc2626; font-weight: bold;")
        delete_all_layout.addWidget(delete_all_label)
        delete_all_layout.addStretch()
        
        delete_all_btn = QPushButton("💣 Delete All Entries")
        delete_all_btn.clicked.connect(self._delete_all_entries)
        delete_all_btn.setMinimumHeight(36)
        delete_all_btn.setMinimumWidth(150)
        delete_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #7f1d1d;
                color: white;
                font-weight: bold;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #991b1b;
            }
            QPushButton:pressed {
                background-color: #dc2626;
            }
        """)
        delete_all_layout.addWidget(delete_all_btn)
        tools_layout.addLayout(delete_all_layout)
        
        layout.addWidget(tools_group)
        
        # Duplicates Table Section
        dup_group = QGroupBox("Duplicate Records (Select to Delete)")
        dup_group.setStyleSheet(stats_group.styleSheet())
        dup_table_layout = QVBoxLayout(dup_group)
        
        self.duplicates_table = QTableWidget()
        self.duplicates_table.setColumnCount(7)
        self.duplicates_table.setHorizontalHeaderLabels([
            "Select", "Text", "Value", "Language", "Method", "Date", "ID"
        ])
        header = self.duplicates_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.duplicates_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.duplicates_table.setAlternatingRowColors(True)
        self.duplicates_table.setColumnWidth(0, 60)
        self.duplicates_table.setColumnWidth(1, 200)
        self.duplicates_table.setColumnWidth(2, 80)
        self.duplicates_table.setColumnWidth(3, 150)
        self.duplicates_table.setColumnWidth(4, 150)
        self.duplicates_table.setColumnWidth(5, 150)
        
        dup_table_layout.addWidget(self.duplicates_table)
        
        # Delete selected button
        delete_btn_layout = QHBoxLayout()
        self.select_all_dup_btn = QPushButton("Select All Duplicates (Keep Newest)")
        self.select_all_dup_btn.clicked.connect(self._select_all_duplicates)
        self.select_all_dup_btn.setEnabled(False)
        delete_btn_layout.addWidget(self.select_all_dup_btn)
        
        delete_btn_layout.addStretch()
        
        self.delete_selected_btn = QPushButton("🗑️ Delete Selected Records")
        self.delete_selected_btn.clicked.connect(self._delete_selected)
        self.delete_selected_btn.setEnabled(False)
        self.delete_selected_btn.setStyleSheet("""
            QPushButton:enabled {
                background-color: #dc2626;
                color: white;
                font-weight: 600;
                min-height: 36px;
            }
            QPushButton:enabled:hover {
                background-color: #b91c1c;
            }
        """)
        delete_btn_layout.addWidget(self.delete_selected_btn)
        
        dup_table_layout.addLayout(delete_btn_layout)
        
        layout.addWidget(dup_group)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #64748b; font-weight: normal;")
        layout.addWidget(self.status_label)
        
        # Load initial statistics
        self._load_statistics()
    
    def _load_statistics(self):
        """Load and display database statistics."""
        try:
            all_records = self.calculation_service.get_all_calculations(limit=100000)
            
            total_count = len(all_records)
            
            # Count by language
            language_counts = defaultdict(int)
            method_counts = defaultdict(int)
            favorites_count = 0
            tagged_count = 0
            with_notes_count = 0
            
            for record in all_records:
                language_counts[record.language] += 1
                method_counts[record.method] += 1
                if record.is_favorite:
                    favorites_count += 1
                if record.tags:
                    tagged_count += 1
                if record.notes:
                    with_notes_count += 1
            
            # Format statistics
            stats = []
            stats.append(f"Total Calculations: {total_count:,}")
            stats.append(f"Favorites: {favorites_count:,}")
            stats.append(f"With Tags: {tagged_count:,}")
            stats.append(f"With Notes: {with_notes_count:,}")
            stats.append("")
            stats.append("By Language:")
            for lang, count in sorted(language_counts.items(), key=lambda x: -x[1]):
                stats.append(f"  {lang}: {count:,}")
            
            self.stats_display.setPlainText("\n".join(stats))
            self.status_label.setText(f"Statistics loaded - {total_count:,} total records")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load statistics:\n{str(e)}")
    
    def _find_duplicates(self):
        """Find duplicate records based on text + language + method."""
        try:
            all_records = self.calculation_service.get_all_calculations(limit=100000)
            
            # Group by (text, language, method)
            groups: Dict[tuple, List[CalculationRecord]] = defaultdict(list)
            for record in all_records:
                key = (record.text.strip().lower(), record.language, record.method)
                groups[key].append(record)
            
            # Filter to only groups with duplicates
            self.duplicate_groups = [
                sorted(records, key=lambda r: r.date_created, reverse=True)
                for records in groups.values()
                if len(records) > 1
            ]
            
            if not self.duplicate_groups:
                QMessageBox.information(
                    self,
                    "No Duplicates Found",
                    "No duplicate calculations were found in the database."
                )
                self.status_label.setText("No duplicates found")
                return
            
            # Display in table
            self._display_duplicates()
            
            total_dups = sum(len(group) for group in self.duplicate_groups)
            self.status_label.setText(
                f"Found {len(self.duplicate_groups)} duplicate groups ({total_dups} total records)"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to find duplicates:\n{str(e)}")
    
    def _display_duplicates(self):
        """Display duplicate records in the table."""
        self.duplicates_table.setRowCount(0)
        self.selected_for_deletion.clear()
        
        row = 0
        for group in self.duplicate_groups:
            # Add separator row
            if row > 0:
                self.duplicates_table.insertRow(row)
                for col in range(7):
                    separator_item = QTableWidgetItem("")
                    separator_item.setBackground(Qt.GlobalColor.lightGray)
                    self.duplicates_table.setItem(row, col, separator_item)
                row += 1
            
            # Add each record in the group
            for idx, record in enumerate(group):
                self.duplicates_table.insertRow(row)
                
                # Checkbox
                checkbox = QCheckBox()
                checkbox.setProperty("record_id", record.id)
                checkbox.stateChanged.connect(self._on_checkbox_changed)
                # Auto-select older duplicates (keep newest, which is index 0)
                if idx > 0:
                    checkbox.setChecked(False)
                checkbox_widget = QWidget()
                checkbox_layout = QHBoxLayout(checkbox_widget)
                checkbox_layout.addWidget(checkbox)
                checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                self.duplicates_table.setCellWidget(row, 0, checkbox_widget)
                
                # Text
                text_item = QTableWidgetItem(record.text)
                if idx == 0:  # Newest record
                    text_item.setBackground(QColor(144, 238, 144))  # Light green
                    text_item.setToolTip("Newest record (recommended to keep)")
                self.duplicates_table.setItem(row, 1, text_item)
                
                # Value
                self.duplicates_table.setItem(row, 2, QTableWidgetItem(str(record.value)))
                
                # Language
                self.duplicates_table.setItem(row, 3, QTableWidgetItem(record.language))
                
                # Method
                self.duplicates_table.setItem(row, 4, QTableWidgetItem(record.method))
                
                # Date
                date_str = record.date_created.strftime("%Y-%m-%d %H:%M:%S")
                self.duplicates_table.setItem(row, 5, QTableWidgetItem(date_str))
                
                # ID (truncated)
                id_short = record.id[:8] + "..." if record.id and len(record.id) > 8 else record.id
                self.duplicates_table.setItem(row, 6, QTableWidgetItem(id_short or ""))
                
                row += 1
        
        self.select_all_dup_btn.setEnabled(True)
        self.delete_selected_btn.setEnabled(True)
    
    def _on_checkbox_changed(self, state):
        """Handle checkbox state change."""
        checkbox = self.sender()
        if not isinstance(checkbox, QCheckBox):
            return
        record_id = checkbox.property("record_id")
        
        if state == Qt.CheckState.Checked.value:
            self.selected_for_deletion.add(record_id)
        else:
            self.selected_for_deletion.discard(record_id)
        
        # Update delete button
        count = len(self.selected_for_deletion)
        if count > 0:
            self.delete_selected_btn.setText(f"🗑️ Delete {count} Selected Records")
        else:
            self.delete_selected_btn.setText("🗑️ Delete Selected Records")
    
    def _select_all_duplicates(self):
        """Select all older duplicates (keep newest in each group)."""
        self.selected_for_deletion.clear()
        
        for row in range(self.duplicates_table.rowCount()):
            widget = self.duplicates_table.cellWidget(row, 0)
            if widget:
                checkbox = widget.findChild(QCheckBox)
                if checkbox:
                    # Check if this is NOT the newest (green) record
                    text_item = self.duplicates_table.item(row, 1)
                    if text_item and text_item.background().color() != QColor(144, 238, 144):
                        checkbox.setChecked(True)
                    else:
                        checkbox.setChecked(False)
    
    def _delete_selected(self):
        """Delete selected duplicate records."""
        if not self.selected_for_deletion:
            QMessageBox.warning(self, "No Selection", "No records selected for deletion.")
            return
        
        count = len(self.selected_for_deletion)
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {count} records?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                deleted = 0
                for record_id in self.selected_for_deletion:
                    if self.calculation_service.delete_calculation(record_id):
                        deleted += 1
                
                self.selected_for_deletion.clear()
                self.duplicates_table.setRowCount(0)
                self.select_all_dup_btn.setEnabled(False)
                self.delete_selected_btn.setEnabled(False)
                
                QMessageBox.information(
                    self,
                    "Deletion Complete",
                    f"Successfully deleted {deleted} records."
                )
                
                self._load_statistics()
                self.status_label.setText(f"Deleted {deleted} records")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete records:\n{str(e)}")
    
    def _clean_empty_records(self):
        """Remove records with empty or invalid text."""
        try:
            all_records = self.calculation_service.get_all_calculations(limit=100000)
            
            empty_records = [
                r for r in all_records
                if not r.text or not r.text.strip() or r.text.strip().lower() in ['nan', 'none', 'null']
            ]
            
            if not empty_records:
                QMessageBox.information(
                    self,
                    "No Empty Records",
                    "No empty or invalid records were found."
                )
                return
            
            reply = QMessageBox.question(
                self,
                "Confirm Cleanup",
                f"Found {len(empty_records)} empty/invalid records.\n\nDelete them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                deleted = 0
                for record in empty_records:
                    if record.id and self.calculation_service.delete_calculation(record.id):
                        deleted += 1
                
                QMessageBox.information(
                    self,
                    "Cleanup Complete",
                    f"Deleted {deleted} empty/invalid records."
                )
                self._load_statistics()
                self.status_label.setText(f"Cleaned {deleted} empty records")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clean empty records:\n{str(e)}")
    
    def _sanitize_text(self):
        """Sanitize all text fields - normalize whitespace and remove control characters."""
        try:
            all_records = self.calculation_service.get_all_calculations(limit=100000)
            
            updated = 0
            for record in all_records:
                modified = False
                
                # Sanitize text
                if record.text:
                    sanitized = ' '.join(record.text.split())
                    if sanitized != record.text:
                        record.text = sanitized
                        modified = True
                
                # Sanitize normalized_text
                if record.normalized_text:
                    sanitized = ' '.join(record.normalized_text.split())
                    if sanitized != record.normalized_text:
                        record.normalized_text = sanitized
                        modified = True
                
                # Sanitize notes
                if record.notes:
                    sanitized = ' '.join(record.notes.split())
                    if sanitized != record.notes:
                        record.notes = sanitized
                        modified = True
                
                if modified:
                    self.calculation_service.repository.save(record)
                    updated += 1
            
            QMessageBox.information(
                self,
                "Sanitization Complete",
                f"Updated {updated} records with sanitized text."
            )
            self._load_statistics()
            self.status_label.setText(f"Sanitized {updated} records")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to sanitize text:\n{str(e)}")
    
    def _rebuild_index(self):
        """Rebuild the Whoosh search index."""
        reply = QMessageBox.question(
            self,
            "Rebuild Search Index",
            "This will rebuild the entire search index.\n\n"
            "This may take a few moments but can fix search issues.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Get all records
                all_records = self.calculation_service.get_all_calculations(limit=100000)
                
                # Re-save each record (this updates the index)
                progress = QProgressDialog("Rebuilding search index...", "Cancel", 0, len(all_records), self)
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                
                for idx, record in enumerate(all_records):
                    if progress.wasCanceled():
                        break
                    
                    self.calculation_service.repository.save(record)
                    progress.setValue(idx + 1)
                
                progress.close()
                
                QMessageBox.information(
                    self,
                    "Rebuild Complete",
                    f"Successfully rebuilt search index for {len(all_records)} records."
                )
                self.status_label.setText("Search index rebuilt")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to rebuild index:\n{str(e)}")
    
    def _delete_all_entries(self):
        """Delete ALL calculations from the database (dangerous operation)."""
        # First confirmation
        reply1 = QMessageBox.warning(
            self,
            "⚠️ WARNING: Delete All Entries",
            "This will DELETE ALL calculations from the database!\n\n"
            "This action CANNOT be undone.\n\n"
            "Are you ABSOLUTELY sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply1 != QMessageBox.StandardButton.Yes:
            return
        
        # Second confirmation (type to confirm)
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(
            self,
            "Final Confirmation Required",
            "Type 'DELETE ALL' to confirm (case-sensitive):",
            QLineEdit.EchoMode.Normal,
            ""
        )
        
        if not ok or text != "DELETE ALL":
            QMessageBox.information(
                self,
                "Cancelled",
                "Operation cancelled - database unchanged."
            )
            return
        
        try:
            # Get ALL records without limit
            all_records = self.calculation_service.get_all_calculations(limit=100000)
            total = len(all_records)
            
            if total == 0:
                QMessageBox.information(self, "No Data", "Database is already empty.")
                return
            
            # Show progress dialog
            progress = QProgressDialog(
                "Deleting all calculations...", 
                "Cancel", 
                0, 
                total, 
                self
            )
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)
            
            deleted = 0
            failed = []
            for idx, record in enumerate(all_records):
                if progress.wasCanceled():
                    break
                
                if record.id:
                    if self.calculation_service.delete_calculation(record.id):
                        deleted += 1
                    else:
                        failed.append(record.id)
                
                progress.setValue(idx + 1)
            
            progress.close()
            
            # Clear the duplicates table and refresh stats
            self.duplicates_table.setRowCount(0)
            self.selected_for_deletion.clear()
            self.select_all_dup_btn.setEnabled(False)
            self.delete_selected_btn.setEnabled(False)
            self._load_statistics()
            
            if deleted == total:
                QMessageBox.information(
                    self,
                    "Database Cleared",
                    f"Successfully deleted all {deleted} calculations.\n\n"
                    "The database is now empty."
                )
                self.status_label.setText(f"All {deleted} calculations deleted")
            else:
                msg = f"Deleted {deleted} out of {total} calculations.\n\n"
                if failed:
                    msg += f"{len(failed)} records could not be deleted.\n\n"
                    msg += "Try running 'Rebuild Index' and then delete again."
                QMessageBox.warning(
                    self,
                    "Partial Deletion",
                    msg
                )
                self.status_label.setText(f"Deleted {deleted}/{total} calculations")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete all entries:\n{str(e)}")
