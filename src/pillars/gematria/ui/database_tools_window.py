"""Database management tools window for cleaning and maintaining calculation database."""
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QProgressDialog,
    QGroupBox, QTextEdit, QHeaderView, QCheckBox, QWidget, QLineEdit, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from typing import List, Dict, Set
from collections import defaultdict
from pathlib import Path

from ..services import CalculationService
from ..models import CalculationRecord
from shared.ui.theme import COLORS, set_archetype, get_title_style, get_subtitle_style


class DatabaseToolsWindow(QMainWindow):
    """Window for database maintenance and cleanup operations."""
    
    def __init__(self, window_manager=None, parent=None):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """Initialize the database tools window."""
        super().__init__(parent)
        self.window_manager = window_manager
        self.calculation_service = CalculationService()
        self.duplicate_groups: List[List[CalculationRecord]] = []
        self.selected_for_deletion: Set[str] = set()
        
        self.setWindowTitle("The Archive Custodian")
        self.setMinimumSize(1200, 800)
        self.resize(1300, 900)
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)

        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Level 0: The Ghost Layer (Nano Banana substrate)
        possible_paths = [
            Path("src/assets/patterns/database_bg_pattern.png"),
            Path("src/assets/patterns/tq_bg_pattern.png"),
            Path("assets/patterns/tq_bg_pattern.png"),
        ]
        
        bg_path = None
        for p in possible_paths:
            if p.exists():
                bg_path = p
                break
        
        central = QWidget()
        central.setObjectName("CentralContainer")
        self.setCentralWidget(central)
        
        if bg_path:
            abs_path = bg_path.absolute().as_posix()
            central.setStyleSheet(f"""
                QWidget#CentralContainer {{
                    border-image: url("{abs_path}") 0 0 0 0 stretch stretch;
                    border: none;
                    background-color: {COLORS['light']};
                }}
            """)
        else:
            central.setStyleSheet(f"QWidget#CentralContainer {{ background-color: {COLORS['light']}; }}")
        
        # Create scroll area for content
        scroll = QScrollArea(central)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        # Content widget inside scroll area
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Attach scroll area to central widget
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.addWidget(scroll)
        scroll.setWidget(content_widget)
        
        # Level 1: Title (The Sigil)
        title_label = QLabel("📚 THE ARCHIVE CUSTODIAN")
        title_label.setStyleSheet(get_title_style())
        layout.addWidget(title_label)
        
        # Subtitle (The Whisper)
        desc_label = QLabel("Maintain the integrity of the Sacred Records")
        desc_label.setStyleSheet(get_subtitle_style())
        layout.addWidget(desc_label)
        
        # Level 1: Statistics Tablet
        stats_group = QGroupBox("Archive Metrics")
        stats_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 800;
                font-size: 14pt;
                color: {COLORS['void']};
                border: 2px solid {COLORS['ash']};
                border-radius: 12px;
                margin-top: 16px;
                padding-top: 16px;
                background-color: {COLORS['marble']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
            }}
        """)
        stats_layout = QVBoxLayout(stats_group)
        stats_layout.setSpacing(12)
        stats_layout.setContentsMargins(16, 20, 16, 16)
        
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        self.stats_display.setMaximumHeight(120)
        self.stats_display.setStyleSheet(f"""
            QTextEdit {{
                font-family: 'Courier New', monospace;
                font-size: 10pt;
                color: {COLORS['stone']};
                background-color: {COLORS['light']};
                border: 1px solid {COLORS['ash']};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        stats_layout.addWidget(self.stats_display)
        
        refresh_stats_btn = QPushButton("🔄 Refresh Metrics")
        refresh_stats_btn.clicked.connect(self._load_statistics)
        refresh_stats_btn.setMinimumHeight(40)
        set_archetype(refresh_stats_btn, "navigator")
        stats_layout.addWidget(refresh_stats_btn)
        
        layout.addWidget(stats_group)
        layout.addSpacing(20)  # Breathing room between tablets
        
        # Level 1: Purification Tools Tablet
        tools_group = QGroupBox("Purification Rituals")
        tools_group.setStyleSheet(stats_group.styleSheet())
        tools_layout = QVBoxLayout(tools_group)
        tools_layout.setSpacing(16)
        tools_layout.setContentsMargins(16, 20, 16, 16)
        
        # Find Duplicates (Seeker archetype)
        dup_layout = QHBoxLayout()
        dup_label = QLabel("Reveal duplicate inscriptions (identical text, tongue, and cipher):")
        dup_label.setWordWrap(False)
        dup_label.setStyleSheet(f"color: {COLORS['stone']}; font-size: 11pt;")
        dup_layout.addWidget(dup_label, 1)  # stretch factor
        dup_layout.addSpacing(12)
        
        find_dup_btn = QPushButton("🔍 Reveal Duplicates")
        find_dup_btn.clicked.connect(self._find_duplicates)
        find_dup_btn.setMinimumHeight(40)
        find_dup_btn.setMinimumWidth(160)
        set_archetype(find_dup_btn, "seeker")
        dup_layout.addWidget(find_dup_btn)
        tools_layout.addLayout(dup_layout)
        
        # Remove Empty/Invalid Records (Destroyer archetype)
        empty_layout = QHBoxLayout()
        empty_label = QLabel("Banish void inscriptions or corrupted records:")
        empty_label.setWordWrap(False)
        empty_label.setStyleSheet(f"color: {COLORS['stone']}; font-size: 11pt;")
        empty_layout.addWidget(empty_label, 1)
        empty_layout.addSpacing(12)
        
        clean_empty_btn = QPushButton("🧹 Purge the Void")
        clean_empty_btn.clicked.connect(self._clean_empty_records)
        clean_empty_btn.setMinimumHeight(40)
        clean_empty_btn.setMinimumWidth(160)
        set_archetype(clean_empty_btn, "destroyer")
        empty_layout.addWidget(clean_empty_btn)
        tools_layout.addLayout(empty_layout)
        
        # Sanitize Text (Magus archetype - transmutation)
        sanitize_layout = QHBoxLayout()
        sanitize_label = QLabel("Transmute chaos into order (normalize spacing and encoding):")
        sanitize_label.setWordWrap(False)
        sanitize_label.setStyleSheet(f"color: {COLORS['stone']}; font-size: 11pt;")
        sanitize_layout.addWidget(sanitize_label, 1)
        sanitize_layout.addSpacing(12)
        
        sanitize_btn = QPushButton("✨ Transmute All")
        sanitize_btn.clicked.connect(self._sanitize_text)
        sanitize_btn.setMinimumHeight(40)
        sanitize_btn.setMinimumWidth(160)
        set_archetype(sanitize_btn, "magus")
        sanitize_layout.addWidget(sanitize_btn)
        tools_layout.addLayout(sanitize_layout)
        
        # Rebuild Index (Scribe archetype)
        rebuild_layout = QHBoxLayout()
        rebuild_label = QLabel("Restore the great index (mend broken pathways):")
        rebuild_label.setWordWrap(False)
        rebuild_label.setStyleSheet(f"color: {COLORS['stone']}; font-size: 11pt;")
        rebuild_layout.addWidget(rebuild_label, 1)
        rebuild_layout.addSpacing(12)
        
        rebuild_btn = QPushButton("🔧 Restore Index")
        rebuild_btn.clicked.connect(self._rebuild_index)
        rebuild_btn.setMinimumHeight(40)
        rebuild_btn.setMinimumWidth(160)
        set_archetype(rebuild_btn, "scribe")
        rebuild_layout.addWidget(rebuild_btn)
        tools_layout.addLayout(rebuild_layout)
        
        # Delete All Entries (Destroyer archetype - ULTIMATE)
        delete_all_layout = QHBoxLayout()
        delete_all_label = QLabel("⚠️ OBLITERATE ALL RECORDS (The Final Purge - Cannot be undone!):")
        delete_all_label.setWordWrap(False)
        delete_all_label.setStyleSheet(f"color: {COLORS['destroyer']}; font-weight: 800; font-size: 11pt;")
        delete_all_layout.addWidget(delete_all_label, 1)
        delete_all_layout.addSpacing(12)
        
        delete_all_btn = QPushButton("💣 THE FINAL PURGE")
        delete_all_btn.clicked.connect(self._delete_all_entries)
        delete_all_btn.setMinimumHeight(40)
        delete_all_btn.setMinimumWidth(160)
        set_archetype(delete_all_btn, "destroyer")
        delete_all_layout.addWidget(delete_all_btn)
        tools_layout.addLayout(delete_all_layout)
        
        layout.addWidget(tools_group)
        layout.addSpacing(20)  # Breathing room between tablets
        
        # Level 1: Duplicates Revelation Tablet
        dup_group = QGroupBox("Echoes in the Archive (Mark for Purging)")
        dup_group.setStyleSheet(stats_group.styleSheet())
        dup_table_layout = QVBoxLayout(dup_group)
        dup_table_layout.setSpacing(12)
        dup_table_layout.setContentsMargins(16, 20, 16, 16)
        
        self.duplicates_table = QTableWidget()
        self.duplicates_table.setColumnCount(7)
        self.duplicates_table.setHorizontalHeaderLabels([
            "Mark", "Inscription", "Value", "Tongue", "Cipher", "Carved", "Sigil"
        ])
        header = self.duplicates_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.duplicates_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.duplicates_table.setAlternatingRowColors(True)
        self.duplicates_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['light']};
                alternate-background-color: {COLORS['marble']};
                border: 1px solid {COLORS['ash']};
                border-radius: 8px;
                color: {COLORS['stone']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['marble']};
                color: {COLORS['void']};
                font-weight: 800;
                padding: 8px;
                border: none;
                border-right: 1px solid {COLORS['ash']};
                border-bottom: 2px solid {COLORS['ash']};
            }}
        """)
        
        dup_table_layout.addWidget(self.duplicates_table)
        
        # Delete selected button
        delete_btn_layout = QHBoxLayout()
        self.select_all_dup_btn = QPushButton("✓ Mark All Echoes (Preserve Newest)")
        self.select_all_dup_btn.clicked.connect(self._select_all_duplicates)
        self.select_all_dup_btn.setEnabled(False)
        self.select_all_dup_btn.setMinimumHeight(40)
        set_archetype(self.select_all_dup_btn, "navigator")
        delete_btn_layout.addWidget(self.select_all_dup_btn)
        
        delete_btn_layout.addStretch()
        
        self.delete_selected_btn = QPushButton("🗑️ Purge Marked Records")
        self.delete_selected_btn.clicked.connect(self._delete_selected)
        self.delete_selected_btn.setEnabled(False)
        self.delete_selected_btn.setMinimumHeight(40)
        set_archetype(self.delete_selected_btn, "destroyer")
        delete_btn_layout.addWidget(self.delete_selected_btn)
        
        dup_table_layout.addLayout(delete_btn_layout)
        
        layout.addWidget(dup_group)
        
        # Status oracle
        self.status_label = QLabel("Awaiting your decree, Custodian.")
        self.status_label.setStyleSheet(f"color: {COLORS['mist']}; font-size: 10pt; font-weight: 700;")
        layout.addWidget(self.status_label)
        
        # Show placeholder, load stats after window appears
        self.stats_display.setPlainText("Communing with the Archive...")
        # Defer statistics loading to not block UI
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self._load_statistics)
    
    def _load_statistics(self):
        """Load and display database statistics."""
        try:
            # Use efficient count query instead of loading all records
            all_records = self.calculation_service.get_all_calculations(limit=10000)  # Sample for stats
            
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
            for lang, count in sorted(language_counts.items(), key=lambda x: -x[1]):  # type: ignore[reportUnknownArgumentType, reportUnknownLambdaType, reportUnknownVariableType]
                stats.append(f"  {lang}: {count:,}")
            
            self.stats_display.setPlainText("\n".join(stats))
            self.status_label.setText(f"The Archive reveals {total_count:,} inscriptions (sample of records)")
            
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
