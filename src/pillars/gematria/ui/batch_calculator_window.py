"""Great Harvest window for sowing seeds (importing) and reaping calculations."""
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
    QComboBox, QGroupBox, QTextEdit, QMessageBox, QHeaderView, QWidget,
    QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QCloseEvent, QColor, QPalette, QBrush, QImage, QPixmap

from ..services import CalculationService
from ..services.base_calculator import GematriaCalculator


class BatchProcessThread(QThread):
    """Thread for processing batch calculations without blocking UI."""
    
    progress_updated = pyqtSignal(int, int)  # current, total
    calculation_completed = pyqtSignal(str, str)  # text, status
    processing_finished = pyqtSignal(int, int)  # success_count, error_count
    
    def __init__(self, data: List[Dict], calculators: List[GematriaCalculator], service: CalculationService):
        """
        Initialize batch process thread.
        
        Args:
            data: List of dictionaries containing word data
            calculators: List of calculators to use for calculations
            service: Service for storing results
        """
        super().__init__()
        self.data = data
        self.calculators = calculators
        self.service = service
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
                        # Save via Service (handles breakdown and normalization internally)
                        self.service.save_calculation(
                            text=text,
                            value=value,
                            calculator=calculator,
                            breakdown=breakdown,
                            notes=notes,
                            tags=tags
                        )
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


class GreatHarvestWindow(QMainWindow):
    """The Great Harvest: A window for sowing seeds (importing) and reaping (calculating) results."""
    
    def __init__(self, calculators: List[GematriaCalculator], window_manager=None, parent=None):
        """
        Initialize The Great Harvest window.
        
        Args:
            calculators: List of available calculators
            window_manager: Window Manager
            parent: Parent widget
        """
        super().__init__(parent)
        self.window_manager = window_manager
        self.calculators = {calc.name: calc for calc in calculators}
        self.calculation_service = CalculationService()  # Use Service, not Repository
        self.imported_data: List[Dict] = []
        self.process_thread: Optional[BatchProcessThread] = None
        
        self.setWindowTitle("The Great Harvest")
        self.setMinimumSize(1000, 800)
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the Floating Temple user interface."""
        # Level 0: The Background (Thematic Texture)
        self.setAutoFillBackground(True)
        
        # Robust path resolution
        # Try to find the asset relative to the project root or the module
        # Assuming src/ as root for execution context or package structure
        # We will try a few standard locations
        
        possible_paths = [
            Path("src/assets/patterns/batch_bg_pattern.png"), # From project root
            Path("assets/patterns/batch_bg_pattern.png"),     # From src if running inside
            Path(__file__).parent.parent.parent.parent / "assets/patterns/batch_bg_pattern.png" # Relative to this file
        ]
        
        bg_path = None
        for p in possible_paths:
            if p.exists():
                bg_path = p
                break
        
        if bg_path:
            palette = self.palette()
            img = QImage(str(bg_path.absolute()))
            if not img.isNull():
                # Tile the background
                palette.setBrush(QPalette.ColorRole.Window, QBrush(img))
                self.setPalette(palette)
            else:
                 print(f"Error: Failed to load image at {bg_path}")
        else:
            print("Error: Background pattern not found.")
            # Fallback to Cloud color if texture missing
            self.setStyleSheet("QMainWindow { background-color: #f8fafc; }")

        central = QWidget()
        central.setStyleSheet("background: transparent;") # Allow Level 0 to show through
        self.setCentralWidget(central)
        
        # Main Layout
        layout = QVBoxLayout(central)
        layout.setSpacing(24) # 8px Grid: 3 * 8
        layout.setContentsMargins(40, 40, 40, 40) # 8px Grid: 5 * 8
        
        # --- HEADER ---
        header_layout = QVBoxLayout()
        title_label = QLabel("THE GREAT HARVEST")
        title_label.setStyleSheet("""
            font-family: 'Inter', sans-serif;
            font-size: 28pt;
            font-weight: 900;
            color: #0f172a; /* Void */
            letter-spacing: -1px;
            margin-bottom: 8px;
        """)
        header_layout.addWidget(title_label)
        
        desc_label = QLabel(
            "Sow your seeds from the archives (CSV/Excel) and reap the numerical truth.\n"
            "Prepare the soil with 'word', 'tags', and 'notes'."
        )
        desc_label.setStyleSheet("""
            font-family: 'Inter', sans-serif;
            font-size: 11pt;
            color: #64748b; /* Mist */
        """)
        desc_label.setWordWrap(True)
        header_layout.addWidget(desc_label)
        layout.addLayout(header_layout)
        
        # --- LEVEL 1: THE FLOATING PANEL (Container for content) ---
        self.panel = QFrame()
        self.panel.setObjectName("FloatingPanel")
        self.panel.setStyleSheet("""
            QFrame#FloatingPanel {
                background-color: rgba(255, 255, 255, 0.95);
                border: 1px solid #cbd5e1;
                border-radius: 24px;
            }
            QLabel {
                color: #334155; /* Stone */
                font-family: 'Inter', sans-serif;
            }
            QGroupBox {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 24px;
                font-family: 'Inter', sans-serif;
                font-weight: 800;
                font-size: 10pt;
                color: #0f172a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
            }
        """)
        
        # Add Drop Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 40)) # 15% opacity roughly
        self.panel.setGraphicsEffect(shadow)
        
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setSpacing(24)
        panel_layout.setContentsMargins(32, 32, 32, 32)
        
        # --- SECTION 1: SOW SEEDS (Import) ---
        import_group = QGroupBox("1. SOW SEEDS (IMPORT)")
        import_layout = QVBoxLayout(import_group)
        import_layout.setContentsMargins(16, 24, 16, 16)
        
        file_layout = QHBoxLayout()
        self.file_label = QLabel("The soil is empty.")
        self.file_label.setStyleSheet("color: #64748b; font-style: italic;")
        file_layout.addWidget(self.file_label)
        file_layout.addStretch()
        
        self.import_button = QPushButton("Select Granary File")
        self.import_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.import_button.setMinimumHeight(48) # Medium Control
        self.import_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f59e0b, stop:1 #d97706);
                color: white;
                font-weight: 700;
                font-size: 11pt;
                border: 1px solid #b45309;
                border-radius: 12px;
                padding: 0 24px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d97706, stop:1 #f59e0b);
                border-color: #92400e;
            }
            QPushButton:pressed {
                background-color: #b45309;
            }
        """)
        self.import_button.clicked.connect(self._import_file)
        file_layout.addWidget(self.import_button)
        
        import_layout.addLayout(file_layout)
        panel_layout.addWidget(import_group)
        
        # --- SECTION 2: INSPECTION (Preview) ---
        preview_group = QGroupBox("2. INSPECTION OF THE CROP")
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setContentsMargins(16, 24, 16, 16)
        
        config_layout = QHBoxLayout()
        lang_label = QLabel("Select Calculation Method:")
        lang_label.setStyleSheet("font-weight: 700; font-size: 10pt;")
        config_layout.addWidget(lang_label)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Hebrew", "Greek", "English (TQ)"])
        self.language_combo.setMinimumHeight(40)
        self.language_combo.setStyleSheet("""
            QComboBox {
                padding: 4px 16px;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                background: white;
                font-size: 11pt;
                color: #334155;
            }
            QComboBox:hover {
                border-color: #2563eb;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
        """)
        config_layout.addWidget(self.language_combo, 1)
        preview_layout.addLayout(config_layout)
        
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(4)
        self.preview_table.setHorizontalHeaderLabels(["Seed (Word)", "Tags", "Notes", "Status"])
        header = self.preview_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
                gridline-color: #f1f5f9;
                font-family: 'Inter', sans-serif;
            }
            QTableWidget::item {
                padding: 8px;
                color: #334155;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #cbd5e1;
                font-weight: 700;
                color: #64748b;
                text-transform: uppercase;
                font-size: 9pt;
            }
        """)
        preview_layout.addWidget(self.preview_table)
        panel_layout.addWidget(preview_group)
        
        # --- SECTION 3: REAPING (Process) ---
        progress_group = QGroupBox("3. REAP HARVEST")
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setContentsMargins(16, 24, 16, 16)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(16) # Slimmer
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 8px;
                background-color: #f1f5f9;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #1d4ed8);
                border-radius: 8px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Awaiting the command.")
        self.status_label.setStyleSheet("color: #64748b; font-size: 10pt; margin-top: 8px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.status_label)
        
        panel_layout.addWidget(progress_group)
        
        layout.addWidget(self.panel)
        
        # --- ACTIONS FOOTER (Outside Panel, or inside at bottom) ---
        # Sticking to inside panel for visual cohesion
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Abandon Field")
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_button.setMinimumHeight(48)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #64748b;
                font-weight: 600;
                font-size: 11pt;
                border: none;
                padding: 0 16px;
            }
            QPushButton:hover {
                color: #ef4444; /* Expulsion Red on hover */
            }
        """)
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_button)
        
        self.send_button = QPushButton("Send to Tablet")
        self.send_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_button.setMinimumHeight(48)
        # Amethyst Gradient for Emerald Tablet interaction
        self.send_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #64748b, stop:1 #475569);
                color: white;
                font-weight: 800;
                font-size: 11pt;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 0 24px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #475569, stop:1 #64748b);
                border-color: #1e293b;
            }
            QPushButton:disabled {
                background: #e2e8f0;
                border-color: #cbd5e1;
                color: #94a3b8;
            }
        """)
        self.send_button.setEnabled(False)
        self.send_button.clicked.connect(self._send_to_emerald)
        button_layout.addWidget(self.send_button)

        self.process_button = QPushButton("REAP HARVEST")
        self.process_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.process_button.setMinimumHeight(56) # Large Action
        self.process_button.setMinimumWidth(200)
        self.process_button.setEnabled(False)
        # Star Blue Gradient (Revelation)
        self.process_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #7c3aed);
                color: white;
                font-weight: 900;
                font-size: 12pt;
                letter-spacing: 0.5px;
                border: 1px solid #6d28d9;
                border-radius: 16px;
                padding: 0 32px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #8b5cf6);
                margin-top: -1px;
                margin-bottom: 1px;
                border-color: #5b21b6;
            }
            QPushButton:pressed {
                background-color: #5b21b6;
                margin-top: 1px;
                margin-bottom: -1px;
            }
            QPushButton:disabled {
                background: #e2e8f0;
                border-color: #cbd5e1;
                color: #94a3b8;
            }
        """)
        self.process_button.clicked.connect(self._process_batch)
        button_layout.addWidget(self.process_button)
        
        panel_layout.addLayout(button_layout)

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
            "Select Granary File (Spreadsheet)",
            downloads_dir,
            file_filter
        )
        
        if not file_path:
            return
        
        try:
            # Determine file type and read accordingly
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in ['.xlsx', '.xls']:
                if not PANDAS_AVAILABLE or pd is None:
                    QMessageBox.critical(self, "Missing Tool", "Install 'pandas' and 'openpyxl' to harvest Excel files.")
                    return
                df = pd.read_excel(file_path).fillna('')
                self.imported_data = [{str(k).lower(): str(v) for k, v in row.items()} for row in df.to_dict('records')]
            
            elif file_ext == '.ods':
                if not PANDAS_AVAILABLE or pd is None:
                    QMessageBox.critical(self, "Missing Tool", "Install 'pandas' and 'odfpy' to harvest LibreOffice files.")
                    return
                try:
                    df = pd.read_excel(file_path, engine='odf').fillna('')
                    self.imported_data = [{str(k).lower(): str(v) for k, v in row.items()} for row in df.to_dict('records')]
                except ImportError:
                     QMessageBox.critical(self, "Missing Tool", "Install 'odfpy' to harvest LibreOffice files.")
                     return
            
            elif file_ext in ['.csv', '.tsv', '.txt']:
                delimiter = '\t' if file_ext == '.tsv' else ','
                if PANDAS_AVAILABLE and pd is not None:
                    df = pd.read_csv(file_path, delimiter=delimiter).fillna('')
                    self.imported_data = [{str(k).lower(): str(v) for k, v in row.items()} for row in df.to_dict('records')]
                else:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f, delimiter=delimiter)
                        self.imported_data = [{str(k).lower(): str(v) for k, v in row.items()} for row in reader]
            else:
                QMessageBox.warning(self, "Unknown Seed", f"The format '{file_ext}' cannot be sown.")
                return
            
            # Check if data was loaded
            if not self.imported_data:
                QMessageBox.warning(self, "Empty Sack", "No seeds found in this file.")
                return
            
            # Update UI
            self.file_label.setText(f"✓ {Path(file_path).name} ({len(self.imported_data)} seeds loaded)")
            self.file_label.setStyleSheet("color: #059669; font-weight: bold; font-style: normal;")
            self._update_preview()
            self.process_button.setEnabled(True)
            if hasattr(self, "send_button"):
                self.send_button.setEnabled(True)
            self.status_label.setText(f"Ready to harvest {len(self.imported_data)} words.")
                
        except Exception as e:
            QMessageBox.critical(self, "Blighted Crop", f"Failed to sow seeds:\n{str(e)}")
    
    def _update_preview(self):
        """Update preview table with imported data."""
        self.preview_table.setRowCount(len(self.imported_data))
        self.preview_table.setSortingEnabled(False)
        
        for idx, row in enumerate(self.imported_data):
            # 1. Word/Text
            raw_word = row.get('word', row.get('text', ''))
            word_text = "" if raw_word is None else str(raw_word).strip()
            self.preview_table.setItem(idx, 0, QTableWidgetItem(str(word_text)))
            
            # 2. Tags
            raw_tags = row.get('tags', row.get('tag', ''))
            tags_text = str(raw_tags).strip() if raw_tags else ""
            if tags_text.lower() == 'nan': tags_text = ""
            self.preview_table.setItem(idx, 1, QTableWidgetItem(str(tags_text)))
            
            # 3. Notes
            raw_notes = row.get('notes', row.get('note', ''))
            notes_text = str(raw_notes).strip() if raw_notes else ""
            if notes_text.lower() == 'nan': notes_text = ""
            if len(notes_text) > 50: notes_text = notes_text[:47] + "..."
            self.preview_table.setItem(idx, 2, QTableWidgetItem(str(notes_text)))
            
            # 4. Status
            status_item = QTableWidgetItem("Dormant")
            status_item.setForeground(QBrush(QColor("#94a3b8"))) # Slate 400
            self.preview_table.setItem(idx, 3, status_item)

        self.preview_table.setSortingEnabled(True)
    
    def _process_batch(self):
        """Start batch processing."""
        if not self.imported_data:
            return
        
        language = self.language_combo.currentText()
        if language == "Hebrew":
            selected_calcs = [calc for name, calc in self.calculators.items() if "Hebrew" in name]
        elif language == "Greek":
             selected_calcs = [calc for name, calc in self.calculators.items() if "Greek" in name]
        else:  # English (TQ)
             selected_calcs = [calc for name, calc in self.calculators.items() if "English" in name or "TQ" in name]
        
        if not selected_calcs:
            QMessageBox.warning(self, "No Scythes", f"No calculation tools found for {language}.")
            return
        
        self.import_button.setEnabled(False)
        self.process_button.setEnabled(False)
        self.language_combo.setEnabled(False)
        
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(self.imported_data))
        
        self.process_thread = BatchProcessThread(self.imported_data, selected_calcs, self.calculation_service)
        self.process_thread.progress_updated.connect(self._on_progress_updated)
        self.process_thread.calculation_completed.connect(self._on_calculation_completed)
        self.process_thread.processing_finished.connect(self._on_processing_finished)
        self.process_thread.start()
        
        self.status_label.setText(f"Harvesting with {len(selected_calcs)} {language} methods...")
    
    def _on_progress_updated(self, current: int, total: int):
        self.progress_bar.setValue(current)
        self.status_label.setText(f"Harvesting: {current}/{total}")
    
    def _on_calculation_completed(self, text: str, status: str):
        for row_idx in range(self.preview_table.rowCount()):
            item = self.preview_table.item(row_idx, 0)
            if item and item.text() == text:
                status_item = QTableWidgetItem(status)
                if "Error" in status:
                     status_item.setForeground(QBrush(QColor("#ef4444"))) # Crimson
                else:
                     status_item.setForeground(QBrush(QColor("#059669"))) # Emerald
                self.preview_table.setItem(row_idx, 3, status_item)
                break
    
    def _on_processing_finished(self, success_count: int, error_count: int):
        self.import_button.setEnabled(True)
        self.language_combo.setEnabled(True)
        self.status_label.setText(f"Bounty Secure: {success_count} reaped, {error_count} blighted.")
        
        QMessageBox.information(
            self,
            "Harvest Complete",
            f"The season is over.\n\n"
            f"Bounty: {success_count} words saved.\n"
            f"Blight: {error_count} errors.\n\n"
            f"The grain is stored in the silo (Database)."
        )
        self.process_button.setText("✓ Harvest Complete")
        self.process_button.setEnabled(False)
    
    def closeEvent(self, a0: Optional[QCloseEvent]):
        if a0 is None: return
        if self.process_thread and self.process_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Harvest in Progress",
                "The reapers are still in the field. Abandon them?",
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

    def _send_to_emerald(self):
        """Send import preview data to Emerald Tablet."""
        if not self.window_manager or not self.imported_data:
            return

        from shared.signals.navigation_bus import navigation_bus

        # Prepare Data
        columns = ["Word", "Tags", "Notes"]
        rows = []
        for row in self.imported_data:
             word = str(row.get('word', row.get('text', '')))
             tags = str(row.get('tags', row.get('tag', '')))
             notes = str(row.get('notes', row.get('note', '')))
             rows.append([word, tags, notes])
             
        data = {
            "columns": columns,
            "data": rows,
            "styles": {}
        }
        
        # Open Hub
        # Request Window via Signal Bus
        navigation_bus.request_window.emit(
            "emerald_tablet", 
            {"allow_multiple": False, "window_manager": self.window_manager}
        )
        
        # Verify it opened (synchronously in this architecture for now)
        hub = self.window_manager.get_active_windows().get("emerald_tablet")
        
        if hasattr(hub, "receive_import"):
            name = f"Harvest_{datetime.now().strftime('%Y%m%d_%H%M')}"
            hub.receive_import(name, data)
            QMessageBox.information(self, "Sent", f"Sent {len(rows)} rows to the Emerald Tablet.")
