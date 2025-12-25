from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QSpinBox, QPushButton, QListWidget, QListWidgetItem, 
    QGroupBox, QMenu, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction

class SearchPanel(QWidget):
    """
    Widget for searching text by gematria value and displaying results.
    """
    search_requested = pyqtSignal(int, int, bool)  # value, max_words, is_global
    result_selected = pyqtSignal(int, int, int)   # start, end, doc_index (optional)
    save_matches_requested = pyqtSignal()
    export_requested = pyqtSignal()
    smart_filter_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_matches = []
        self.current_tab_index = -1
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        group = QGroupBox("Search by Value")
        # Styling extracted from original
        group.setStyleSheet("""
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
        group_layout = QVBoxLayout(group)
        
        # Inputs
        input_layout = QHBoxLayout()
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Enter value...")
        self.value_input.returnPressed.connect(self._on_search)
        
        self.max_words = QSpinBox()
        self.max_words.setRange(1, 9999)
        self.max_words.setValue(8)
        self.max_words.setToolTip("Max words in a phrase (1-9999)")
        
        search_btn = QPushButton("🔍 Find")
        search_btn.clicked.connect(self._on_search)
        search_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f59e0b, stop:1 #d97706);
                color: white;
                border: 1px solid #b45309;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 600;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d97706, stop:1 #f59e0b);
            }
        """)
        
        input_layout.addWidget(QLabel("Value:"))
        input_layout.addWidget(self.value_input)
        input_layout.addWidget(QLabel("Value:"))
        input_layout.addWidget(self.value_input)
        input_layout.addWidget(search_btn)
        
        # Global Search Checkbox
        self.global_chk = QCheckBox("All Docs")
        self.global_chk.setToolTip("Search in all open documents")
        input_layout.addWidget(self.global_chk)
        
        group_layout.addLayout(input_layout)
        
        # Info label
        self.info_label = QLabel("Enter a value to search.")
        self.info_label.setStyleSheet("color: #64748b; font-size: 9pt;")
        group_layout.addWidget(self.info_label)
        
        # Results List
        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self._on_item_clicked)
        group_layout.addWidget(self.results_list)
        
        # Actions
        actions_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_requested.emit)
        clear_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ef4444, stop:1 #b91c1c);
                color: white;
                border: 1px solid #b91c1c;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 600;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #b91c1c, stop:1 #ef4444); }
        """)
        
        save_btn = QPushButton("💾 Save Matches")
        save_btn.clicked.connect(self.save_matches_requested.emit)
        save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #059669);
                color: white;
                border: 1px solid #047857;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 600;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10b981); }
        """)
        
        export_btn = QPushButton("📤 Export")
        export_btn.clicked.connect(self._on_export)
        export_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #64748b, stop:1 #475569);
                color: white;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 600;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #475569, stop:1 #64748b); }
        """)
        
        smart_btn = QPushButton("✨ Smart Filter")
        smart_btn.clicked.connect(self._on_smart_filter)
        smart_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #7c3aed);
                color: white;
                border: 1px solid #6d28d9;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 600;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #8b5cf6); }
        """)
        
        actions_layout.addWidget(clear_btn)
        actions_layout.addWidget(save_btn)
        actions_layout.addWidget(export_btn)
        actions_layout.addWidget(smart_btn)
        group_layout.addLayout(actions_layout)
        
        layout.addWidget(group)
        
    def _on_search(self):
        val_str = self.value_input.text().strip()
        if not val_str or not val_str.isdigit():
            return
        # Hardcoded to 9999 as requested by user
        self.search_requested.emit(int(val_str), 9999, self.global_chk.isChecked())
        
    def _on_export(self):
        self.export_requested.emit()
        
    def _on_smart_filter(self):
        self.smart_filter_requested.emit()

    def set_active_tab(self, index: int):
        self.current_tab_index = index
        self._refresh_results()

    def set_results(self, matches):
        """
        Set matches and refresh display.
        Args:
            matches: List of tuples (text, start, end, doc_title, tab_index)
        """
        self.all_matches = matches
        self._refresh_results()
        
    def _refresh_results(self):
        self.results_list.clear()
        
        # Filter by active tab
        if self.current_tab_index == -1:
            filtered = [] # No tab active? or show all? 
            # If no tab active, maybe show nothing.
        else:
            filtered = [m for m in self.all_matches if m[4] == self.current_tab_index]
        
        total_count = len(self.all_matches)
        local_count = len(filtered)
        target_val = self.value_input.text()
        
        if not self.all_matches:
            self.info_label.setText("No matches found.")
        else:
            self.info_label.setText(f"Found {total_count} total ({local_count} in current tab)")
        
        if not filtered and total_count > 0:
            # Maybe show a helper item?
            pass
            
        for item_data in filtered:
            # item_data: (text, start, end, doc_title, tab_index)
            text, start, end, doc_title, tab_index = item_data
            
            label = f"{text} = {target_val}"
            # Doc title is redundant if we only show current tab, but kept for clarity if needed?
            # User said "only the active tab", so doc_title is implicitly the active doc.
            # We can remove it to clean up UI.
            # label += f" [{doc_title}]" 
                
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, (start, end, tab_index))
            self.results_list.addItem(item)
            
    def clear_results(self):
        self.all_matches = []
        self.results_list.clear()
        self.info_label.setText("")
        
    send_to_tablet_requested = pyqtSignal(list)

    def _on_item_clicked(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            start, end, tab_index = data
            self.result_selected.emit(start, end, tab_index)

    def contextMenuEvent(self, event):
        """Context menu for results."""
        if not self.results_list.itemAt(event.pos()):
            return
            
        menu = QMenu(self)
        send_action = QAction("Send Results to Emerald Tablet", self)
        send_action.triggered.connect(self._on_send_results)
        menu.addAction(send_action)
        menu.exec(event.globalPos())
        
    def _on_send_results(self):
        """Emit signal to send current filtered results to Tablet."""
        # Filter matches by current tab if needed, similar to display
        if self.current_tab_index == -1:
             # If no tab active, maybe send nothing or all? Logic in refresh uses all if -1?
             # refresh_results logic: if -1, filtered = [].
             # Let's use visible items from list widget to be true to WYSIWYG
             pass
        
        # Actually easier to just send self.all_matches filtered by current_tab_index
        filtered = []
        if self.current_tab_index != -1:
            filtered = [m for m in self.all_matches if m[4] == self.current_tab_index]
            
        if filtered:
            self.send_to_tablet_requested.emit(filtered)
            


