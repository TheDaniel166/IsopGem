"""
Controls Pane - The Visualizer Panel.
Right panel with display toggles, measurement tools, history, and export options.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QCheckBox, QLabel, QPushButton, QFrame, QListWidget, QListWidgetItem, QHBoxLayout, QApplication, QComboBox, QColorDialog, QMenu, QInputDialog
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from ....services.persistence_service import PersistenceService
from ..view_model import GeometryViewModel
from ...liturgy_styles import LiturgyPanels, LiturgyTabs, LiturgyToolbar, LiturgyColors, LiturgyButtons

class ControlsPane(QWidget):
    """
    Right panel: Display options, camera controls, and export tools.
    """
    
    def __init__(self, view_model: GeometryViewModel, parent=None):
        super().__init__(parent)
        self.view_model = view_model
        
        self._setup_ui()
        self._connect_signals()

    # Signals for parent window to handle
    snapshot_requested = pyqtSignal()
    copy_measurements_requested = pyqtSignal()
    interactive_measure_toggled = pyqtSignal(bool)
    theme_changed = pyqtSignal(str)
    measurement_line_color_changed = pyqtSignal(QColor)
    measurement_text_color_changed = pyqtSignal(QColor)


    def _setup_ui(self):
        self.setStyleSheet(LiturgyPanels.controls_pane())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header (Visualizer)
        header = QLabel("Visualizer")
        header.setStyleSheet(f"font-size: 16pt; font-weight: 600; color: {LiturgyColors.VOID}; padding: 16px;")
        layout.addWidget(header)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(LiturgyTabs.standard())
        
        self.tabs.addTab(self._build_display_tab(), "Display")
        self.tabs.addTab(self._build_history_tab(), "History")
        self.tabs.addTab(self._build_output_tab(), "Output")
        
        layout.addWidget(self.tabs)
        
        # Hide Button (to collapse this pane)
        self.hide_btn = QPushButton("Hide Controls")
        self.hide_btn.setStyleSheet(LiturgyToolbar.toggle_button())
        self.hide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.hide_btn)
        
    def _connect_signals(self):
        self.view_model.history_updated.connect(self._refresh_history)

    def _build_history_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        
        self.history_list = QListWidget()
        self.history_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self._show_history_context_menu)

        self.history_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {LiturgyColors.STONE};
                border: 1px solid {LiturgyColors.ASH};
                border-radius: 8px;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {LiturgyColors.ASH};
            }}
            QListWidget::item:selected {{
                background-color: {LiturgyColors.LIGHT};
                color: {LiturgyColors.VOID};
            }}
        """)
        self.history_list.itemDoubleClicked.connect(self._restore_history_item)
        
        layout.addWidget(self.history_list)
        
        # Initial Load
        self._refresh_history()
        
        return tab

    def _refresh_history(self):
        self.history_list.clear()
        recent = PersistenceService.get_recent_calculations()
        current_shape = self.view_model.shape_name
        
        for entry in recent:
            if entry.get("shape_name") == current_shape:
                timestamp = entry.get("timestamp", "").split("T")[1][:8] # HH:MM:SS
                summary = entry.get("summary", "No details")
                note = entry.get("note", "")
                
                display_text = f"[{timestamp}] {summary}"
                if note:
                    display_text += f"\nNote: {note}"
                    
                item = QListWidgetItem(display_text)
                # Store full entry in user role (so we have timestamp for note updates)
                item.setData(Qt.ItemDataRole.UserRole, entry) 
                self.history_list.addItem(item)
                
    def _show_history_context_menu(self, pos):
        item = self.history_list.itemAt(pos)
        if not item:
            return
            
        menu = QMenu(self)
        entry = item.data(Qt.ItemDataRole.UserRole)
        current_note = entry.get("note", "")
        
        # Dynamic label based on whether note exists
        note_label = "Edit Note" if current_note else "Add Note"
        edit_note_action = menu.addAction(note_label)
        
        menu.addSeparator()
        delete_action = menu.addAction("Delete")
        
        action = menu.exec(self.history_list.mapToGlobal(pos))
        
        if action == edit_note_action:
            text, ok = QInputDialog.getText(self, note_label, "Note:", text=current_note)
            if ok:
                PersistenceService.update_note(entry["timestamp"], text)
                self._refresh_history()
                
        elif action == delete_action:
            PersistenceService.delete_calculation(entry["timestamp"])
            self._refresh_history()

    def _restore_history_item(self, item: QListWidgetItem):
        entry = item.data(Qt.ItemDataRole.UserRole)
        data = entry.get("data")
        if data:
            self.view_model.load_state(data)


    def _build_display_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Toggles
        # Toggles
        self.show_labels = self._create_checkbox("Show Labels", True)
        self.show_axes = self._create_checkbox("Show Axes", True)
        
        layout.addWidget(self.show_labels)
        layout.addWidget(self.show_axes)

        # Theme Selector
        layout.addSpacing(8)
        theme_label = QLabel("Theme")
        theme_label.setStyleSheet(f"font-weight: 600; color: {LiturgyColors.VOID};")
        layout.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Daylight", "Midnight", "Slate", "Pearl"])
        self.theme_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 6px;
                border: 1px solid {LiturgyColors.ASH};
                border-radius: 4px;
                background-color: {LiturgyColors.LIGHT};
                color: {LiturgyColors.VOID};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
        """)
        self.theme_combo.currentTextChanged.connect(self.theme_changed.emit)
        layout.addWidget(self.theme_combo)
        
        # Interactive Measurement Section
        layout.addSpacing(16)
        measure_label = QLabel("Measurement Tool")
        measure_label.setStyleSheet(f"font-weight: 600; color: {LiturgyColors.VOID};")
        layout.addWidget(measure_label)
        
        self.measure_toggle = QPushButton("Enable Interactive Measure")
        self.measure_toggle.setCheckable(True)
        self.measure_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.measure_toggle.setStyleSheet(LiturgyToolbar.toggle_button())
        self.measure_toggle.toggled.connect(self.interactive_measure_toggled.emit)
        layout.addWidget(self.measure_toggle)
        
        # Color Controls
        layout.addSpacing(8)
        
        # Line Colors Swatch
        line_swatch_label = QLabel("Line Color")
        line_swatch_label.setStyleSheet(f"color: {LiturgyColors.VOID}; font-size: 9pt;")
        layout.addWidget(line_swatch_label)
        
        line_row = QHBoxLayout()
        line_row.setSpacing(4)
        line_colors = [
            QColor(234, 88, 12),  # Orange (Default)
            QColor(220, 38, 38),  # Red
            QColor(234, 179, 8),  # Yellow
            QColor(22, 163, 74),  # Green
            QColor(6, 182, 212),  # Cyan
            QColor(30, 41, 59),   # Black (Slate)
        ]
        for col in line_colors:
            btn = self._create_swatch_btn(col)
            btn.clicked.connect(lambda checked, c=col: self.measurement_line_color_changed.emit(c))
            line_row.addWidget(btn)
        line_row.addStretch()
        layout.addLayout(line_row)
        
        # Text Colors Swatch
        layout.addSpacing(4)
        text_swatch_label = QLabel("Text Color")
        text_swatch_label.setStyleSheet(f"color: {LiturgyColors.VOID}; font-size: 9pt;")
        layout.addWidget(text_swatch_label)
        
        text_row = QHBoxLayout()
        text_row.setSpacing(4)
        text_colors = [
            QColor(0, 0, 0),      # Black (Default)
            QColor(255, 255, 255),# White
            QColor(234, 88, 12),  # Orange
            QColor(220, 38, 38),  # Red
            QColor(22, 163, 74),  # Green
            QColor(37, 99, 235),  # Blue
        ]
        for col in text_colors:
            btn = self._create_swatch_btn(col)
            btn.clicked.connect(lambda checked, c=col: self.measurement_text_color_changed.emit(c))
            text_row.addWidget(btn)
        text_row.addStretch()
        layout.addLayout(text_row)
        
        # Live Stats Container
        self.stats_container = QFrame()
        self.stats_container.setStyleSheet(f"""
            QFrame {{
                background-color: {LiturgyColors.STONE};
                border-radius: 8px;
                padding: 8px;
            }}
            QLabel {{
                color: {LiturgyColors.VOID_SLATE};
                font-size: 9pt;
            }}
        """)
        self.stats_container.hide() # Hidden until tools active
        stats_layout = QVBoxLayout(self.stats_container)
        stats_layout.setSpacing(4)
        
        self.dist_label = QLabel("Distance: --")
        self.area_label = QLabel("Area: --")
        stats_layout.addWidget(self.dist_label)
        stats_layout.addWidget(self.area_label)
        
        layout.addWidget(self.stats_container)
        
        layout.addStretch()
        return tab
    
    def update_measurement_labels(self, stats: dict):
        """Update the stats labels from scene measurement data."""
        if not self.measure_toggle.isChecked():
            self.stats_container.hide()
            return
            
        self.stats_container.show()
        
        dist = stats.get("perimeter", 0.0)
        area = stats.get("area", 0.0)
        closed = stats.get("closed", False)
        
        self.dist_label.setText(f"Distance: {dist:.2f}")
        if closed:
            self.area_label.setText(f"Area: {area:.2f}")
            self.area_label.show()
        else:
            self.area_label.hide()


    def _build_output_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        info = QLabel("Export Tools")
        info.setStyleSheet(f"font-weight: 600; color: {LiturgyColors.VOID};")
        layout.addWidget(info)
        
        # Snapshot
        snapshot_btn = QPushButton("📸 Copy Snapshot")
        snapshot_btn.setToolTip("Copy current view to clipboard")
        snapshot_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        snapshot_btn.setStyleSheet(LiturgyButtons.scribe())
        snapshot_btn.clicked.connect(self.snapshot_requested.emit)
        layout.addWidget(snapshot_btn)
        
        # Copy Stats
        copy_stats_btn = QPushButton("📋 Copy Measurements")
        copy_stats_btn.setToolTip("Copy calculated properties to clipboard")
        copy_stats_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_stats_btn.setStyleSheet(LiturgyButtons.scribe())
        copy_stats_btn.clicked.connect(self.copy_measurements_requested.emit)
        layout.addWidget(copy_stats_btn)
        
        layout.addStretch()
        return tab

    def _create_checkbox(self, text: str, checked: bool) -> QCheckBox:
        cb = QCheckBox(text)
        cb.setChecked(checked)
        cb.setCursor(Qt.CursorShape.PointingHandCursor)
        # Using simple style for now, could move to LiturgyInputs
        cb.setStyleSheet(f"""
            QCheckBox {{
                font-size: 10pt;
                color: {LiturgyColors.VOID_SLATE};
                spacing: 8px;
            }}
        """)
        return cb

    def _create_swatch_btn(self, color: QColor) -> QPushButton:
        btn = QPushButton()
        btn.setFixedSize(24, 24)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # Using a simple block color, slightly rounded
        color_hex = color.name()
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_hex};
                border: 1px solid {LiturgyColors.ASH};
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border: 1px solid {LiturgyColors.VOID};
            }}
        """)
        return btn
