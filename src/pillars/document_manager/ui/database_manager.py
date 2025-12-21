"""Database Manager UI for Document Pillar."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTabWidget, QGridLayout, QFrame, QProgressBar,
    QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
import logging
from pillars.document_manager.services.document_service import document_service_context

logger = logging.getLogger(__name__)

class DatabaseManagerWindow(QMainWindow):
    """Admin interface for managing the Document Database."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Database Manager")
        self.resize(700, 500)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self._setup_ui()
        self._refresh_stats()

    def _setup_ui(self):
        layout = QVBoxLayout(self.central_widget)
        
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        self._setup_dashboard_tab()
        self._setup_maintenance_tab()
        
    def _setup_dashboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Stats Grid
        self.stats_labels = {}
        grid = QGridLayout()
        grid.setSpacing(20)
        
        stats_items = [
            ("Documents", "document_count"),
            ("Images", "image_count"),
            ("Image Storage (Bytes)", "image_storage_bytes"),
            ("Image Storage (MB)", "image_storage_mb"),
        ]
        
        for i, (label_text, key) in enumerate(stats_items):
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                }
            """)
            card_layout = QVBoxLayout(card)
            
            lbl_title = QLabel(label_text)
            lbl_title.setStyleSheet("color: #64748b; font-size: 10pt; font-weight: bold;")
            
            lbl_value = QLabel("...")
            lbl_value.setStyleSheet("color: #0f172a; font-size: 24pt; font-weight: bold;")
            lbl_value.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            self.stats_labels[key] = lbl_value
            
            card_layout.addWidget(lbl_title)
            card_layout.addWidget(lbl_value)
            grid.addWidget(card, i // 2, i % 2)
            
        layout.addLayout(grid)
        layout.addStretch()
        
        btn_refresh = QPushButton("Refresh Statistics")
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setMinimumHeight(40)
        btn_refresh.clicked.connect(self._refresh_stats)
        layout.addWidget(btn_refresh)
        
        self.tabs.addTab(tab, "Dashboard")
        
    def _setup_maintenance_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Description
        info_box = QFrame()
        info_box.setStyleSheet("background-color: #eff6ff; border-radius: 6px; padding: 10px;")
        info_layout = QVBoxLayout(info_box)
        info_lbl = QLabel(
            "<b>Orphan Image Cleanup</b><br>"
            "This tool scans all documents to find images stored in the database "
            "that are no longer referenced in any document's content.<br>"
            "This usually happens when images are deleted from the editor."
        )
        info_lbl.setWordWrap(True)
        info_layout.addWidget(info_lbl)
        layout.addWidget(info_box)
        
        # Controls
        controls = QHBoxLayout()
        self.btn_scan = QPushButton("Scan for Orphans")
        self.btn_scan.clicked.connect(self._scan_orphans)
        controls.addWidget(self.btn_scan)
        
        self.btn_clean = QPushButton("Delete Orphan Images")
        self.btn_clean.setStyleSheet("color: #dc2626;")
        self.btn_clean.setEnabled(False)
        self.btn_clean.clicked.connect(self._clean_orphans)
        controls.addWidget(self.btn_clean)
        
        layout.addLayout(controls)
        
        # Results area
        self.results_area = QLabel("Ready to scan.")
        self.results_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_area.setStyleSheet("font-size: 12pt; color: #64748b; margin: 20px;")
        layout.addWidget(self.results_area)
        
        layout.addStretch()
        self.tabs.addTab(tab, "Maintenance")

    def _refresh_stats(self):
        try:
            with document_service_context() as service:
                stats = service.get_database_stats()
                
            for key, label in self.stats_labels.items():
                val = stats.get(key, 0)
                if isinstance(val, (int, float)):
                    label.setText(f"{val:,}")
                else:
                    label.setText(str(val))
        except Exception as e:
            logger.error(f"Failed to refresh stats: {e}")
            QMessageBox.warning(self, "Error", f"Failed to refresh stats: {e}")

    def _scan_orphans(self):
        self.results_area.setText("Scanning database... please wait.")
        # Force repaint
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()
        
        try:
            with document_service_context() as service:
                self.scan_results = service.cleanup_orphans(dry_run=True)
                
            orphans = self.scan_results['orphan_count']
            total = self.scan_results['total_images']
            used = self.scan_results['used_images']
            
            msg = (
                f"<b>Scan Complete</b><br><br>"
                f"Total Images: {total}<br>"
                f"Used Images: {used}<br>"
                f"<b>Orphan Images: {orphans}</b>"
            )
            self.results_area.setText(msg)
            
            if orphans > 0:
                self.btn_clean.setEnabled(True)
                self.btn_clean.setText(f"Delete {orphans} Orphans")
            else:
                self.btn_clean.setEnabled(False)
                self.btn_clean.setText("Delete Orphan Images")
                
        except Exception as e:
            self.results_area.setText(f"Error: {str(e)}")
            logger.error(f"Scan failed: {e}")

    def _clean_orphans(self):
        orphans = self.scan_results.get('orphan_count', 0)
        reply = QMessageBox.question(
            self,
            "Confirm Cleanup",
            f"Are you sure you want to permanently delete {orphans} orphan images?\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                with document_service_context() as service:
                    result = service.cleanup_orphans(dry_run=False)
                
                deleted = result['deleted_count']
                QMessageBox.information(self, "Cleanup Complete", f"Successfully deleted {deleted} images.")
                
                # Refresh UI
                self._scan_orphans()
                self._refresh_stats()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Cleanup failed: {e}")
