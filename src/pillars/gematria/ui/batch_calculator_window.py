"""Batch calculator window for importing and processing spreadsheet data."""
import csv
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
import json

try:
    import pandas as pd  # type: ignore
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None  # type: ignore

from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QFileDialog, QProgressBar,
    QComboBox, QGroupBox, QTextEdit, QMessageBox, QHeaderView, QWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QCloseEvent

from ..models import CalculationRecord
from ..repositories import CalculationRepository
from ..services.base_calculator import GematriaCalculator


class BatchProcessThread(QThread):
    """Thread for processing batch calculations without blocking UI."""
    
    progress_updated = pyqtSignal(int, int)  # current, total
    calculation_completed = pyqtSignal(str, str)  # text, status
    processing_finished = pyqtSignal(int, int)  # success_count, error_count
    
    def __init__(self, data: List[Dict], calculators: List[GematriaCalculator], repository: CalculationRepository):
        """
        Initialize batch process thread.
        
        Args:
            data: List of dictionaries containing word data
            calculators: List of calculators to use for calculations
            repository: Repository for storing results
        """
        super().__init__()
        self.data = data
        self.calculators = calculators
        self.repository = repository
        self._is_running = True
    
    def run(self):
        """Process all calculations."""
        success_count = 0
        error_count = 0
        total = len(self.data)
        
        for idx, row in enumerate(self.data):
            if not self._is_running:
                break
            
            try:
                # Extract word/text (required field) - convert to string and handle NaN
                text = str(row.get('word', row.get('text', ''))).strip()
                if not text or text.lower() == 'nan':
                    error_count += 1
                    self.calculation_completed.emit("", "Error: No text")
                    self.progress_updated.emit(idx + 1, total)
                    continue
                
                # Extract optional fields (case-insensitive) - handle NaN values
                notes = str(row.get('notes', row.get('note', ''))).strip()
                if notes.lower() == 'nan':
                    notes = ''
                    
                tags_str = str(row.get('tags', row.get('tag', ''))).strip()
                if tags_str.lower() == 'nan':
                    tags_str = ''
                
                # Parse tags (can be comma-separated)
                tags = []
                if tags_str:
                    tags = [t.strip() for t in tags_str.split(',') if t.strip()]
                
                # Calculate with ALL calculators
                word_success = True
                for calculator in self.calculators:
                    try:
                        # Calculate value
                        value = calculator.calculate(text)
                        breakdown = calculator.get_breakdown(text)
                        normalized = calculator.normalize_text(text)
                        
                        # Create calculation record
                        record = CalculationRecord(
                            text=text,
                            value=value,
                            language=calculator.name,
                            method=calculator.name,
                            notes=notes,
                            tags=tags,
                            breakdown=json.dumps(breakdown),
                            character_count=len(breakdown),
                            normalized_text=normalized,
                            date_created=datetime.now(),
                            date_modified=datetime.now()
                        )
                        
                        # Save to repository
                        self.repository.save(record)
                    except Exception as calc_error:
                        word_success = False
                        continue
                
                if word_success:
                    success_count += 1
                    self.calculation_completed.emit(text, f"✓ {len(self.calculators)} methods")
                else:
                    error_count += 1
                    self.calculation_completed.emit(text, "Partial success")
                
            except Exception as e:
                error_count += 1
                self.calculation_completed.emit(
                    row.get('word', row.get('text', 'Unknown')),
                    f"Error: {str(e)}"
                )
            
            self.progress_updated.emit(idx + 1, total)
        
        self.processing_finished.emit(success_count, error_count)
    
    def stop(self):
        """Stop processing."""
        self._is_running = False


class BatchCalculatorWindow(QMainWindow):
    """Window for batch importing and calculating words from spreadsheets."""
    
    def __init__(self, calculators: List[GematriaCalculator], parent=None):
        """
        Initialize the batch calculator window.
        
        Args:
            calculators: List of available calculators
            parent: Parent widget
        """
        super().__init__(parent)
        self.calculators = {calc.name: calc for calc in calculators}
        self.repository = CalculationRepository()
        self.imported_data: List[Dict] = []
        self.process_thread: Optional[BatchProcessThread] = None
        
        self.setWindowTitle("Batch Calculator")
        self.setMinimumSize(900, 700)
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("📊 Batch Calculator")
        title_label.setStyleSheet("""
            font-size: 24pt;
            font-weight: bold;
            color: #1e293b;
            margin-bottom: 8px;
        """)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            "Import spreadsheets (CSV, TSV, Excel, LibreOffice) to calculate and save multiple words at once.\n"
            "Required column: 'word' or 'text' | Optional: 'tags'/'tag', 'notes'/'note'"
        )
        desc_label.setStyleSheet("color: #64748b; font-size: 10pt; margin-bottom: 12px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Import section
        import_group = QGroupBox("1. Import Spreadsheet")
        import_group.setStyleSheet("""
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
        import_layout = QVBoxLayout(import_group)
        
        # File selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: #64748b; font-weight: normal;")
        file_layout.addWidget(self.file_label)
        file_layout.addStretch()
        
        self.import_button = QPushButton("📁 Select File")
        self.import_button.setMinimumHeight(36)
        self.import_button.setStyleSheet(self._get_button_style())
        self.import_button.clicked.connect(self._import_file)
        file_layout.addWidget(self.import_button)
        
        import_layout.addLayout(file_layout)
        layout.addWidget(import_group)
        
        # Preview section
        preview_group = QGroupBox("2. Preview & Configure")
        preview_group.setStyleSheet(import_group.styleSheet())
        preview_layout = QVBoxLayout(preview_group)
        
        # Language selection
        calc_layout = QHBoxLayout()
        calc_label = QLabel("Language:")
        calc_label.setStyleSheet("font-weight: normal;")
        calc_layout.addWidget(calc_label)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Hebrew", "Greek", "English (TQ)"])
        self.language_combo.setMinimumHeight(32)
        self.language_combo.setStyleSheet("""
            QComboBox {
                padding: 4px 8px;
                border: 2px solid #cbd5e1;
                border-radius: 6px;
                background: white;
                font-size: 10pt;
            }
            QComboBox:hover {
                border-color: #2563eb;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
        """)
        calc_layout.addWidget(self.language_combo, 1)
        preview_layout.addLayout(calc_layout)
        
        # Data preview table
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(4)
        self.preview_table.setHorizontalHeaderLabels(["Word", "Tags", "Notes", "Status"])
        header = self.preview_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #cbd5e1;
                border-radius: 6px;
                background-color: white;
                gridline-color: #e2e8f0;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #f1f5f9;
                padding: 6px;
                border: none;
                border-bottom: 2px solid #cbd5e1;
                font-weight: bold;
            }
        """)
        preview_layout.addWidget(self.preview_table)
        
        layout.addWidget(preview_group)
        
        # Progress section
        progress_group = QGroupBox("3. Process")
        progress_group.setStyleSheet(import_group.styleSheet())
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(28)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #cbd5e1;
                border-radius: 6px;
                text-align: center;
                background-color: #f1f5f9;
            }
            QProgressBar::chunk {
                background-color: #2563eb;
                border-radius: 4px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready to import")
        self.status_label.setStyleSheet("color: #64748b; font-weight: normal; margin-top: 4px;")
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.process_button = QPushButton("▶️ Process All")
        self.process_button.setMinimumHeight(40)
        self.process_button.setMinimumWidth(140)
        self.process_button.setEnabled(False)
        self.process_button.setStyleSheet(self._get_button_style("#16a34a", "#15803d", "#166534"))
        self.process_button.clicked.connect(self._process_batch)
        button_layout.addWidget(self.process_button)
        
        self.cancel_button = QPushButton("Close")
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.setMinimumWidth(100)
        self.cancel_button.setStyleSheet(self._get_button_style("#64748b", "#475569", "#334155"))
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _get_button_style(self, bg="#2563eb", hover="#1d4ed8", pressed="#1e40af"):
        """Get button stylesheet with custom colors."""
        return f"""
            QPushButton {{
                background-color: {bg};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 11pt;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            QPushButton:pressed {{
                background-color: {pressed};
            }}
            QPushButton:disabled {{
                background-color: #e5e7eb;
                color: #9ca3af;
            }}
        """
    
    def _import_file(self):
        """Import spreadsheet file."""
        # Build file filter based on available libraries
        file_filter = "CSV/TSV Files (*.csv *.tsv *.txt)"
        if PANDAS_AVAILABLE:
            file_filter = "All Spreadsheets (*.csv *.tsv *.xlsx *.xls *.ods);;Excel Files (*.xlsx *.xls);;LibreOffice Files (*.ods);;CSV/TSV Files (*.csv *.tsv *.txt);;All Files (*.*)"
        else:
            file_filter += ";;All Files (*.*)"
        
        # Start in Downloads directory
        downloads_dir = str(Path.home() / "Downloads")
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Spreadsheet File",
            downloads_dir,
            file_filter
        )
        
        if not file_path:
            return
        
        try:
            # Determine file type and read accordingly
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in ['.xlsx', '.xls']:
                # Excel files - require pandas
                if not PANDAS_AVAILABLE or pd is None:
                    QMessageBox.critical(
                        self,
                        "Missing Dependency",
                        "Excel file support requires pandas and openpyxl.\n\n"
                        "Install with: pip install pandas openpyxl"
                    )
                    return
                
                # Read Excel file
                df = pd.read_excel(file_path)
                # Replace NaN with empty strings and convert all to strings
                df = df.fillna('')
                self.imported_data = [
                    {str(k).lower(): str(v) for k, v in row.items()}
                    for row in df.to_dict('records')
                ]
            
            elif file_ext == '.ods':
                # LibreOffice files - require pandas and odfpy
                if not PANDAS_AVAILABLE or pd is None:
                    QMessageBox.critical(
                        self,
                        "Missing Dependency",
                        "LibreOffice file support requires pandas and odfpy.\n\n"
                        "Install with: pip install pandas odfpy"
                    )
                    return
                
                try:
                    # Read ODS file
                    df = pd.read_excel(file_path, engine='odf')
                    # Replace NaN with empty strings and convert all to strings
                    df = df.fillna('')
                    self.imported_data = [
                        {str(k).lower(): str(v) for k, v in row.items()}
                        for row in df.to_dict('records')
                    ]
                except ImportError:
                    QMessageBox.critical(
                        self,
                        "Missing Dependency",
                        "LibreOffice file support requires odfpy.\n\n"
                        "Install with: pip install odfpy"
                    )
                    return
            
            elif file_ext in ['.csv', '.tsv', '.txt']:
                # CSV/TSV files - use pandas if available, otherwise csv module
                if PANDAS_AVAILABLE and pd is not None:
                    # Use pandas for better handling
                    delimiter = '\t' if file_ext == '.tsv' else ','
                    df = pd.read_csv(file_path, delimiter=delimiter)
                    # Replace NaN with empty strings and convert all to strings
                    df = df.fillna('')
                    self.imported_data = [
                        {str(k).lower(): str(v) for k, v in row.items()}
                        for row in df.to_dict('records')
                    ]
                else:
                    # Fallback to csv module
                    delimiter = '\t' if file_ext == '.tsv' else ','
                    with open(file_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f, delimiter=delimiter)
                        self.imported_data = [
                            {str(key).lower(): str(value) for key, value in row.items()}
                            for row in reader
                        ]
            else:
                QMessageBox.warning(
                    self,
                    "Unsupported Format",
                    f"File format '{file_ext}' is not supported.\n\n"
                    f"Supported formats: .csv, .tsv, .xlsx, .xls, .ods"
                )
                return
            
            # Check if data was loaded
            if not self.imported_data:
                QMessageBox.warning(self, "Import Error", "No data found in file.")
                return
            
            # Update UI
            self.file_label.setText(f"✓ {Path(file_path).name} ({len(self.imported_data)} rows)")
            self.file_label.setStyleSheet("color: #16a34a; font-weight: bold;")
            self._update_preview()
            self.process_button.setEnabled(True)
            self.status_label.setText(f"Ready to process {len(self.imported_data)} words")
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Error",
                f"Failed to import file:\n{str(e)}"
            )
    
    def _update_preview(self):
        """Update preview table with imported data, strictly enforcing string types."""
        self.preview_table.setRowCount(len(self.imported_data))
        self.preview_table.setSortingEnabled(False)
        
        for idx, row in enumerate(self.imported_data):
            # 1. Word/Text Column - force string conversion
            raw_word = row.get('word', row.get('text', ''))
            word_text = "" if raw_word is None else str(raw_word).strip()
            self.preview_table.setItem(idx, 0, QTableWidgetItem(str(word_text)))
            
            # 2. Tags Column - force string conversion
            raw_tags = row.get('tags', row.get('tag', ''))
            tags_text = str(raw_tags).strip() if raw_tags else ""
            if tags_text.lower() == 'nan':
                tags_text = ""
            self.preview_table.setItem(idx, 1, QTableWidgetItem(str(tags_text)))
            
            # 3. Notes Column - force string conversion
            raw_notes = row.get('notes', row.get('note', ''))
            notes_text = str(raw_notes).strip() if raw_notes else ""
            if notes_text.lower() == 'nan':
                notes_text = ""
            # Truncate long notes
            if len(notes_text) > 50:
                notes_text = notes_text[:47] + "..."
            self.preview_table.setItem(idx, 2, QTableWidgetItem(str(notes_text)))
            
            # 4. Status Column
            status_item = QTableWidgetItem("Pending")
            status_item.setForeground(Qt.GlobalColor.gray)
            self.preview_table.setItem(idx, 3, status_item)

        self.preview_table.setSortingEnabled(True)
    
    def _process_batch(self):
        """Start batch processing."""
        if not self.imported_data:
            return
        
        # Get selected language and filter calculators
        language = self.language_combo.currentText()
        
        # Filter calculators by language
        if language == "Hebrew":
            selected_calcs = [calc for name, calc in self.calculators.items() if "Hebrew" in name]
        elif language == "Greek":
            selected_calcs = [calc for name, calc in self.calculators.items() if "Greek" in name]
        else:  # English (TQ)
            selected_calcs = [calc for name, calc in self.calculators.items() if "English" in name or "TQ" in name]
        
        if not selected_calcs:
            QMessageBox.warning(self, "Error", f"No calculators found for {language}.")
            return
        
        # Disable controls
        self.import_button.setEnabled(False)
        self.process_button.setEnabled(False)
        self.language_combo.setEnabled(False)
        
        # Reset progress
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(self.imported_data))
        
        # Create and start processing thread
        self.process_thread = BatchProcessThread(self.imported_data, selected_calcs, self.repository)
        self.process_thread.progress_updated.connect(self._on_progress_updated)
        self.process_thread.calculation_completed.connect(self._on_calculation_completed)
        self.process_thread.processing_finished.connect(self._on_processing_finished)
        self.process_thread.start()
        
        self.status_label.setText(f"Processing with {len(selected_calcs)} {language} methods...")
    
    def _on_progress_updated(self, current: int, total: int):
        """Handle progress update."""
        self.progress_bar.setValue(current)
        self.status_label.setText(f"Processing: {current}/{total}")
    
    def _on_calculation_completed(self, text: str, status: str):
        """Handle individual calculation completion."""
        # Find row and update status
        for row_idx in range(self.preview_table.rowCount()):
            item = self.preview_table.item(row_idx, 0)
            if item and item.text() == text:
                status_item = QTableWidgetItem(status)
                if "Error" in status:
                    status_item.setForeground(Qt.GlobalColor.red)
                else:
                    status_item.setForeground(Qt.GlobalColor.darkGreen)
                self.preview_table.setItem(row_idx, 3, status_item)
                break
    
    def _on_processing_finished(self, success_count: int, error_count: int):
        """Handle processing completion."""
        # Re-enable controls
        self.import_button.setEnabled(True)
        self.language_combo.setEnabled(True)
        
        # Update status
        self.status_label.setText(
            f"Complete: {success_count} saved, {error_count} errors"
        )
        
        # Show completion message
        QMessageBox.information(
            self,
            "Batch Processing Complete",
            f"Successfully processed {success_count} words.\n"
            f"{error_count} errors encountered.\n\n"
            f"All calculations have been saved to the database."
        )
        
        # Change button to allow new import
        self.process_button.setText("✓ Process Complete")
        self.process_button.setEnabled(False)
    
    def closeEvent(self, a0: Optional[QCloseEvent]):
        """Handle window close."""
        if a0 is None:
            return
        # Stop processing thread if running
        if self.process_thread and self.process_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Processing in Progress",
                "Batch processing is still running. Are you sure you want to close?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.process_thread.stop()
                self.process_thread.wait()
                a0.accept()
            else:
                a0.ignore()
        else:
            a0.accept()
