"""
Zodiacal Circle Window - Main window for Trigrammic Time Keeping.

Displays the interactive Zodiacal Circle with an info panel showing
selected Conrune pair details.
"""
from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QSizePolicy, QCheckBox, QPushButton, QMessageBox,
    QDateEdit, QSpinBox, QComboBox, QGroupBox, QTabWidget
)

from shared.ui.window_manager import WindowManager

from .zodiacal_circle_widget import ZodiacalCircleWidget
from ..models.thelemic_calendar_models import ConrunePair, ZODIAC_SIGNS


class ZodiacalCircleWindow(QWidget):
    """
    Main window for the Trigrammic Time Keeper featuring the Zodiacal Circle.
    """
    
    def __init__(self, parent: Optional[QWidget] = None, window_manager: Optional[WindowManager] = None):
        super().__init__(parent)
        self.window_manager = window_manager
        self.setWindowTitle("Zodiacal Circle - Trigrammic Time Keeper")
        self.resize(1200, 750)
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """Build the UI layout."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # Left side: Zodiacal Circle
        self.circle_widget = ZodiacalCircleWidget()
        self.circle_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        main_layout.addWidget(self.circle_widget, stretch=3)
        
        # Middle: Info Panel
        info_panel = self._create_info_panel()
        main_layout.addWidget(info_panel, stretch=1)
        
        # Right: Related Points Panel
        related_panel = self._create_related_panel()
        main_layout.addWidget(related_panel, stretch=1)
        
        # Apply dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #0f0f13;
                color: #e0e0e0;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QFrame#info_panel {
                background-color: #1a1a2e;
                border: 1px solid #2a2a4e;
                border-radius: 8px;
            }
            QLabel {
                background: transparent;
            }
        """)
    
    def _create_info_panel(self) -> QFrame:
        """Create the info panel with tabbed interface."""
        panel = QFrame()
        panel.setObjectName("info_panel")
        panel.setMinimumWidth(280)
        panel.setMaximumWidth(350)
        
        main_layout = QVBoxLayout(panel)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # Create Tab Widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #2a2a4e;
                background: #1a1a2e;
                border-radius: 4px;
            }
            QTabBar::tab {
                background: #0f0f13;
                color: #888;
                padding: 8px 12px;
                border: 1px solid #2a2a4e;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #1a1a2e;
                color: #D4AF37;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                color: #e0e0e0;
            }
        """)
        
        # === TAB 1: INFO ===
        info_tab = self._create_info_tab()
        self.tab_widget.addTab(info_tab, "📊 Info")
        
        # === TAB 2: SEARCH ===
        search_tab = self._create_search_tab()
        self.tab_widget.addTab(search_tab, "🔍 Search")
        
        # === TAB 3: OPTIONS ===
        options_tab = self._create_options_tab()
        self.tab_widget.addTab(options_tab, "⚙️ Options")
        
        main_layout.addWidget(self.tab_widget)
        
        return panel
    
    def _create_info_tab(self) -> QWidget:
        """Create the Info tab content."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("✦ Selected Day ✦")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #D4AF37;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Instruction label
        self.instruction_label = QLabel("Click on any degree in the circle\nto reveal its Conrune pair.")
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction_label.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(self.instruction_label)
        
        # Info fields (hidden until selection)
        self.info_container = QWidget()
        info_layout = QVBoxLayout(self.info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(12)
        
        self.date_label = self._create_info_row("Date", "")
        info_layout.addWidget(self.date_label)
        
        self.zodiacal_label = self._create_info_row("Zodiacal", "")
        info_layout.addWidget(self.zodiacal_label)
        
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #2a2a4e;")
        sep.setFixedHeight(1)
        info_layout.addWidget(sep)
        
        pair_title = QLabel("Conrune Pair")
        pair_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        pair_title.setStyleSheet("color: #74ee15;")
        info_layout.addWidget(pair_title)
        
        self.ditrune_label = self._create_info_row("Ditrune (Day)", "")
        info_layout.addWidget(self.ditrune_label)
        
        self.contrune_label = self._create_info_row("Contrune (Night)", "")
        info_layout.addWidget(self.contrune_label)
        
        self.difference_label = self._create_info_row("Difference (Tension)", "")
        info_layout.addWidget(self.difference_label)
        
        self.prime_label = QLabel("")
        self.prime_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prime_label.setStyleSheet("color: #ff2a6d; font-weight: bold; font-size: 12pt;")
        info_layout.addWidget(self.prime_label)
        
        info_layout.addStretch()
        self.info_container.hide()
        layout.addWidget(self.info_container)
        
        layout.addStretch()
        return tab
    
    def _create_search_tab(self) -> QWidget:
        """Create the Search tab content."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)
        
        date_title = QLabel("📅 Jump to Date")
        date_title.setStyleSheet("color: #D4AF37; font-weight: bold; font-size: 11pt;")
        layout.addWidget(date_title)
        
        date_row = QHBoxLayout()
        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.setDisplayFormat("d-MMM")
        self.date_picker.setStyleSheet("QDateEdit { background-color: #1a1a2e; color: #e0e0e0; border: 1px solid #3a3a5e; border-radius: 4px; padding: 6px 10px; }")
        date_row.addWidget(self.date_picker, 1)
        
        go_date_btn = QPushButton("Go")
        go_date_btn.setStyleSheet("QPushButton { background-color: #D4AF37; color: #0f0f13; padding: 6px 16px; border-radius: 4px; font-weight: bold; } QPushButton:hover { background-color: #e8c34a; }")
        go_date_btn.clicked.connect(self._on_date_go)
        date_row.addWidget(go_date_btn)
        layout.addLayout(date_row)
        
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #2a2a4e;")
        sep.setFixedHeight(1)
        layout.addWidget(sep)
        
        search_title = QLabel("🔍 Search by Value")
        search_title.setStyleSheet("color: #4deeea; font-weight: bold; font-size: 11pt;")
        layout.addWidget(search_title)
        
        self.search_type = QComboBox()
        self.search_type.addItems(["Ditrune", "Contrune", "Difference"])
        self.search_type.setStyleSheet("QComboBox { background-color: #1a1a2e; color: #e0e0e0; border: 1px solid #3a3a5e; border-radius: 4px; padding: 6px 10px; }")
        layout.addWidget(self.search_type)
        
        value_row = QHBoxLayout()
        self.search_value = QSpinBox()
        self.search_value.setRange(1, 1000)
        self.search_value.setValue(1)
        self.search_value.setStyleSheet("QSpinBox { background-color: #1a1a2e; color: #e0e0e0; border: 1px solid #3a3a5e; border-radius: 4px; padding: 6px 10px; }")
        value_row.addWidget(self.search_value, 1)
        
        search_btn = QPushButton("Find")
        search_btn.setStyleSheet("QPushButton { background-color: #4deeea; color: #0f0f13; padding: 6px 16px; border-radius: 4px; font-weight: bold; } QPushButton:hover { background-color: #6ef4f0; }")
        search_btn.clicked.connect(self._on_search_value)
        value_row.addWidget(search_btn)
        layout.addLayout(value_row)
        
        self.search_result_label = QLabel("")
        self.search_result_label.setStyleSheet("color: #888; font-size: 9pt;")
        self.search_result_label.setWordWrap(True)
        layout.addWidget(self.search_result_label)
        
        layout.addStretch()
        return tab
    
    def _create_options_tab(self) -> QWidget:
        """Create the Options tab content."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        export_title = QLabel("📤 Export Data")
        export_title.setStyleSheet("color: #D4AF37; font-weight: bold; font-size: 11pt;")
        layout.addWidget(export_title)
        
        export_row = QHBoxLayout()
        self.export_tablet_btn = QPushButton("📊 Tablet")
        self.export_tablet_btn.setStyleSheet("QPushButton { background-color: #2a4a3a; color: #74ee15; padding: 6px 12px; border-radius: 4px; font-weight: bold; } QPushButton:hover { background-color: #3a5a4a; }")
        self.export_tablet_btn.clicked.connect(self._send_to_emerald_tablet)
        export_row.addWidget(self.export_tablet_btn)
        
        self.export_rtf_btn = QPushButton("📝 RTF")
        self.export_rtf_btn.setStyleSheet("QPushButton { background-color: #2a3a4a; color: #4deeea; padding: 6px 12px; border-radius: 4px; font-weight: bold; } QPushButton:hover { background-color: #3a4a5a; }")
        self.export_rtf_btn.clicked.connect(self._send_to_rtf_editor)
        export_row.addWidget(self.export_rtf_btn)
        layout.addLayout(export_row)
        
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #2a2a4e;")
        sep.setFixedHeight(1)
        layout.addWidget(sep)
        
        display_title = QLabel("🎨 Display Options")
        display_title.setStyleSheet("color: #D4AF37; font-weight: bold; font-size: 11pt;")
        layout.addWidget(display_title)
        
        self.reversal_checkbox = QCheckBox("🔄 Reversal Pair")
        self.reversal_checkbox.setStyleSheet("QCheckBox { color: #FF69B4; font-size: 10pt; padding: 4px; }")
        self.reversal_checkbox.stateChanged.connect(self._on_reversal_changed)
        layout.addWidget(self.reversal_checkbox)
        
        self.perspective_checkbox = QCheckBox("🎯 Center Perspective")
        self.perspective_checkbox.setStyleSheet("QCheckBox { color: #D4AF37; font-size: 10pt; padding: 4px; }")
        self.perspective_checkbox.stateChanged.connect(self._on_perspective_changed)
        layout.addWidget(self.perspective_checkbox)
        
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background-color: #2a2a4e;")
        sep2.setFixedHeight(1)
        layout.addWidget(sep2)
        
        aspects_title = QLabel("✧ Aspects (360° Divisors)")
        aspects_title.setStyleSheet("color: #D4AF37; font-weight: bold; font-size: 11pt;")
        layout.addWidget(aspects_title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        checkbox_container = QWidget()
        checkbox_layout = QVBoxLayout(checkbox_container)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        checkbox_layout.setSpacing(4)
        
        scroll.setWidget(checkbox_container)
        layout.addWidget(scroll, 1)
        
        self._divisor_checkboxes = {}
        self._checkbox_container = checkbox_container
        
        return tab
    
    def _create_info_row(self, label: str, value: str) -> QWidget:
        """Create a row with label and value."""
        row = QWidget()
        layout = QVBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #888; font-size: 10pt;")
        layout.addWidget(lbl)
        
        val = QLabel(value)
        val.setObjectName("value")
        val.setStyleSheet("color: #fff; font-size: 14pt; font-weight: bold;")
        layout.addWidget(val)
        
        return row
    
    def _connect_signals(self) -> None:
        """Connect widget signals."""
        self.circle_widget.degree_clicked.connect(self._on_degree_clicked)
        
        # Populate aspect checkboxes now that circle_widget exists
        self._populate_aspect_checkboxes(self._checkbox_container)
    
    def _on_degree_clicked(self, pair: Optional[ConrunePair]) -> None:
        """Handle degree selection."""
        if pair is None:
            return
        
        # Hide instruction, show info
        self.instruction_label.hide()
        self.info_container.show()
        
        # Update date
        self._set_value(self.date_label, pair.gregorian_date)
        
        # Update zodiacal
        if pair.is_prime_ditrune:
            zodiacal_text = "⚡ Prime Ditrune Gate"
        else:
            sign_letter = pair.sign_letter
            sign_name = ZODIAC_SIGNS.get(sign_letter, ("", 0))[0] if sign_letter else ""
            day = pair.sign_day if pair.sign_day is not None else 0
            zodiacal_text = f"{day}° {sign_name}" if sign_name else pair.zodiacal
        self._set_value(self.zodiacal_label, zodiacal_text)
        
        # Update Conrune pair values
        self._set_value(self.ditrune_label, str(pair.ditrune))
        self._set_value(self.contrune_label, str(pair.contrune))
        self._set_value(self.difference_label, str(pair.difference))
        
        # Prime Ditrune indicator
        if pair.is_prime_ditrune:
            self.prime_label.setText("✦ Calendar Unifier ✦\n360 ↔ 364 ↔ 365")
            self.prime_label.show()
        else:
            self.prime_label.hide()
        
        # Update related points panel
        self._update_related_points()
    
    def _set_value(self, row: QWidget, value: str) -> None:
        """Set the value label in an info row."""
        val_label = row.findChild(QLabel, "value")
        if val_label:
            val_label.setText(value)
    
    def _populate_aspect_checkboxes(self, container_widget: QWidget) -> None:
        """Populate the aspects panel with checkboxes for all divisors."""
        layout = container_widget.layout()
        divisors = self.circle_widget.get_divisors()
        
        # Sort by angle (largest first = most common aspects first)
        sorted_divisors = sorted(divisors.items(), key=lambda x: x[1][2], reverse=True)
        
        for divisor, (color_hex, name, angle) in sorted_divisors:
            checkbox = QCheckBox(f"{name} ({angle}°)")
            checkbox.setStyleSheet(f"""
                QCheckBox {{
                    color: {color_hex};
                    font-size: 10pt;
                    padding: 2px;
                }}
                QCheckBox::indicator {{
                    width: 14px;
                    height: 14px;
                }}
                QCheckBox::indicator:checked {{
                    background-color: {color_hex};
                    border: 1px solid {color_hex};
                    border-radius: 2px;
                }}
                QCheckBox::indicator:unchecked {{
                    background-color: transparent;
                    border: 1px solid #555;
                    border-radius: 2px;
                }}
            """)
            checkbox.stateChanged.connect(self._on_aspect_changed)
            layout.addWidget(checkbox)
            self._divisor_checkboxes[divisor] = checkbox
    
    def _on_aspect_changed(self) -> None:
        """Handle aspect checkbox changes."""
        active = []
        for divisor, checkbox in self._divisor_checkboxes.items():
            if checkbox.isChecked():
                active.append(divisor)
        
        self.circle_widget.set_active_divisors(active)
        self._update_related_points()
    
    def _on_reversal_changed(self) -> None:
        """Handle reversal checkbox change."""
        self.circle_widget.set_show_reversal(self.reversal_checkbox.isChecked())
        self._update_related_points()
    
    def _on_perspective_changed(self) -> None:
        """Handle center perspective checkbox change."""
        self.circle_widget.set_center_perspective(self.perspective_checkbox.isChecked())
    
    def _create_related_panel(self) -> QFrame:
        """Create the panel showing Conrune pairs at related points."""
        panel = QFrame()
        panel.setObjectName("info_panel")  # Reuse same styling
        panel.setMinimumWidth(280)
        panel.setMaximumWidth(400)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Title
        title = QLabel("✧ Related Points ✧")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #D4AF37;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #2a2a4e;")
        sep.setFixedHeight(1)
        layout.addWidget(sep)
        
        # Instruction label
        self.related_instruction = QLabel(
            "Select a degree and check\nan aspect to see related points."
        )
        self.related_instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.related_instruction.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(self.related_instruction)
        
        # Scrollable area for related points
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #1a1a2e;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: #3a3a5e;
                border-radius: 4px;
            }
        """)
        
        self._related_container = QWidget()
        self._related_layout = QVBoxLayout(self._related_container)
        self._related_layout.setContentsMargins(0, 0, 0, 0)
        self._related_layout.setSpacing(8)
        
        scroll.setWidget(self._related_container)
        layout.addWidget(scroll)
        
        return panel
    
    def _update_related_points(self) -> None:
        """Update the related points display based on selection and active divisors."""
        # Clear existing items
        while self._related_layout.count():
            child = self._related_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Check if we have a selection and something to show
        if not hasattr(self.circle_widget, '_selected_degree') or not self.circle_widget._selected_degree:
            return
        
        has_divisors = hasattr(self.circle_widget, '_active_divisors') and self.circle_widget._active_divisors
        has_reversal = self.reversal_checkbox.isChecked()
        
        if not has_divisors and not has_reversal:
            return
        
        self.related_instruction.hide()
        
        selected_diff = self.circle_widget._selected_degree
        selected_deg = self.circle_widget._difference_to_degree(selected_diff)
        if selected_deg is None:
            return
        
        # Get divisor data
        divisors = self.circle_widget.get_divisors()
        
        for divisor in sorted(self.circle_widget._active_divisors, key=lambda d: divisors[d][2], reverse=True):
            if divisor not in divisors:
                continue
            
            color_hex, name, angle = divisors[divisor]
            
            # Section header
            header = QLabel(f"▸ {name} ({angle}°)")
            header.setStyleSheet(f"color: {color_hex}; font-weight: bold; font-size: 10pt;")
            self._related_layout.addWidget(header)
            
            # Find related points
            for i in range(1, divisor):
                related_deg = (selected_deg + i * angle) % 360
                
                # Find the Conrune pair at this degree
                related_diff = self.circle_widget._degree_to_difference(int(related_deg))
                if related_diff is None:
                    continue
                
                pair = self.circle_widget._service.get_pair_by_difference(related_diff)
                if pair is None:
                    continue
                
                # Create row for this related point
                row = QWidget()
                row_layout = QHBoxLayout(row)
                row_layout.setContentsMargins(8, 2, 2, 2)
                row_layout.setSpacing(4)
                
                # Zodiacal degree indicator (e.g., "8° Cap" instead of "278°")
                if pair.is_prime_ditrune:
                    zodiac_str = "Gate"
                else:
                    sign_letter = pair.sign_letter
                    sign_abbrs = {'A': 'Ari', 'B': 'Tau', 'C': 'Gem', 'D': 'Can', 'E': 'Leo', 'F': 'Vir',
                                  'G': 'Lib', 'H': 'Sco', 'I': 'Sag', 'J': 'Cap', 'K': 'Aqu', 'L': 'Pis'}
                    sign_abbr = sign_abbrs.get(sign_letter, '?') if sign_letter else '?'
                    day = pair.sign_day if pair.sign_day is not None else 0
                    zodiac_str = f"{day}° {sign_abbr}"
                
                deg_label = QLabel(zodiac_str)
                deg_label.setFixedWidth(60)
                deg_label.setStyleSheet("color: #888; font-size: 9pt;")
                row_layout.addWidget(deg_label)
                
                # Conrune pair
                pair_label = QLabel(f"{pair.ditrune} ↔ {pair.contrune}")
                pair_label.setStyleSheet(f"color: {color_hex}; font-size: 10pt;")
                row_layout.addWidget(pair_label)
                
                # Date
                date_label = QLabel(pair.gregorian_date)
                date_label.setStyleSheet("color: #666; font-size: 9pt;")
                row_layout.addWidget(date_label)
                
                row_layout.addStretch()
                self._related_layout.addWidget(row)
        
        # Show reversal pair if enabled
        if self.reversal_checkbox.isChecked():
            selected_pair = self.circle_widget._service.get_pair_by_difference(selected_diff)
            if selected_pair:
                reversal_pair = self.circle_widget._service.get_reversal_pair(selected_pair)
                if reversal_pair:
                    # Reversal header
                    rev_header = QLabel("▸ Reversal (Y-Mirror)")
                    rev_header.setStyleSheet("color: #FF69B4; font-weight: bold; font-size: 10pt;")
                    self._related_layout.addWidget(rev_header)
                    
                    # Reversal row
                    row = QWidget()
                    row_layout = QHBoxLayout(row)
                    row_layout.setContentsMargins(8, 2, 2, 2)
                    row_layout.setSpacing(4)
                    
                    # Zodiacal position
                    if reversal_pair.is_prime_ditrune:
                        zodiac_str = "Gate"
                    else:
                        sign_letter = reversal_pair.sign_letter
                        sign_abbrs = {'A': 'Ari', 'B': 'Tau', 'C': 'Gem', 'D': 'Can', 'E': 'Leo', 'F': 'Vir',
                                      'G': 'Lib', 'H': 'Sco', 'I': 'Sag', 'J': 'Cap', 'K': 'Aqu', 'L': 'Pis'}
                        sign_abbr = sign_abbrs.get(sign_letter, '?') if sign_letter else '?'
                        day = reversal_pair.sign_day if reversal_pair.sign_day is not None else 0
                        zodiac_str = f"{day}° {sign_abbr}"
                    
                    deg_label = QLabel(zodiac_str)
                    deg_label.setFixedWidth(60)
                    deg_label.setStyleSheet("color: #888; font-size: 9pt;")
                    row_layout.addWidget(deg_label)
                    
                    pair_label = QLabel(f"{reversal_pair.ditrune} ↔ {reversal_pair.contrune}")
                    pair_label.setStyleSheet("color: #FF69B4; font-size: 10pt;")
                    row_layout.addWidget(pair_label)
                    
                    date_label = QLabel(reversal_pair.gregorian_date)
                    date_label.setStyleSheet("color: #666; font-size: 9pt;")
                    row_layout.addWidget(date_label)
                    
                    row_layout.addStretch()
                    self._related_layout.addWidget(row)
        
        self._related_layout.addStretch()
    
    def _collect_export_data(self) -> dict:
        """Collect current selection and related points data for export."""
        if not hasattr(self.circle_widget, '_selected_degree') or not self.circle_widget._selected_degree:
            return {}
        
        selected_diff = self.circle_widget._selected_degree
        selected_pair = self.circle_widget._service.get_pair_by_difference(selected_diff)
        if not selected_pair:
            return {}
        
        rows = []
        
        # Add selected point
        rows.append([
            "Selected", 
            str(selected_pair.ditrune), 
            str(selected_pair.contrune),
            str(selected_pair.difference),
            selected_pair.zodiacal,
            selected_pair.gregorian_date
        ])
        
        # Add related points from divisors
        if hasattr(self.circle_widget, '_active_divisors'):
            selected_deg = self.circle_widget._difference_to_degree(selected_diff)
            divisors = self.circle_widget.get_divisors()
            
            for divisor in self.circle_widget._active_divisors:
                if divisor not in divisors:
                    continue
                _, name, angle = divisors[divisor]
                
                for i in range(1, divisor):
                    related_deg = (selected_deg + i * angle) % 360
                    related_diff = self.circle_widget._service.zodiac_degree_to_difference(related_deg)
                    if related_diff:
                        pair = self.circle_widget._service.get_pair_by_difference(related_diff)
                        if pair:
                            rows.append([
                                f"{name} ({angle}°)",
                                str(pair.ditrune),
                                str(pair.contrune),
                                str(pair.difference),
                                pair.zodiacal,
                                pair.gregorian_date
                            ])
        
        # Add reversal if enabled
        if hasattr(self, 'reversal_checkbox') and self.reversal_checkbox.isChecked():
            reversal = self.circle_widget._service.get_reversal_pair(selected_pair)
            if reversal:
                rows.append([
                    "Reversal (Y-Mirror)",
                    str(reversal.ditrune),
                    str(reversal.contrune),
                    str(reversal.difference),
                    reversal.zodiacal,
                    reversal.gregorian_date
                ])
        
        return {
            "columns": ["Relationship", "Ditrune", "Contrune", "Difference", "Zodiacal", "Date"],
            "data": rows,
            "styles": {}
        }
    
    def _send_to_emerald_tablet(self) -> None:
        """Send data to Emerald Tablet spreadsheet via cross-pillar communication."""
        if not self.window_manager:
            QMessageBox.warning(self, "Integration Error", "Window Manager not available.")
            return
        
        data = self._collect_export_data()
        if not data or not data.get("data"):
            QMessageBox.information(self, "No Data", "Please select a degree first.")
            return
        
        # Import here to avoid circular imports
        from pillars.correspondences.ui.correspondence_hub import CorrespondenceHub
        
        hub = self.window_manager.open_window(
            "emerald_tablet",
            CorrespondenceHub,
            allow_multiple=False,
            window_manager=self.window_manager
        )
        
        if hasattr(hub, "receive_import"):
            hub.receive_import("Zodiacal Circle Export", data)
            QMessageBox.information(self, "Sent", "Data sent to Emerald Tablet.")
    
    def _send_to_rtf_editor(self) -> None:
        """Send data to RTF Editor via cross-pillar communication."""
        if not self.window_manager:
            QMessageBox.warning(self, "Integration Error", "Window Manager not available.")
            return
        
        if not hasattr(self.circle_widget, '_selected_degree') or not self.circle_widget._selected_degree:
            QMessageBox.information(self, "No Data", "Please select a degree first.")
            return
        
        data = self._collect_export_data()
        
        # Format as RTF-friendly text (Markdown table)
        lines = ["# Zodiacal Circle Analysis\n"]
        
        if data and data.get("data"):
            lines.append("| Relationship | Ditrune | Contrune | Difference | Zodiacal | Date |")
            lines.append("|---|---|---|---|---|---|")
            for row in data["data"]:
                lines.append(f"| {' | '.join(row)} |")
        
        text_content = "\n".join(lines)
        
        # Open Document Editor directly
        from pillars.document_manager.ui.document_editor_window import DocumentEditorWindow
        
        window = self.window_manager.open_window(
            "document_editor",
            DocumentEditorWindow
        )
        
        if window and hasattr(window, "set_html"):
            # Convert markdown to simple HTML
            html_content = f"<h1>Zodiacal Circle Analysis</h1><pre>{text_content}</pre>"
            window.set_html(html_content)
            QMessageBox.information(self, "Sent", "Data sent to Document Editor.")
        elif window:
            QMessageBox.information(self, "Note", "Document Editor opened. Paste data manually.")
        else:
            QMessageBox.warning(self, "Error", "Could not open Document Editor.")
    
    def _on_date_go(self) -> None:
        """Jump to a specific date on the circle."""
        date = self.date_picker.date()
        # Format to match CSV format: "21-Mar", "1-Apr"
        date_str = date.toString("d-MMM")
        
        pair = self.circle_widget._service.get_pair_by_date(date_str)
        if pair:
            # Select this degree on the circle
            self.circle_widget._selected_degree = pair.difference
            self.circle_widget.update()
            self.circle_widget.degree_clicked.emit(pair)
            QMessageBox.information(self, "Found", 
                f"Date {date_str}\n"
                f"Difference: {pair.difference}\n"
                f"Ditrune: {pair.ditrune} ↔ Contrune: {pair.contrune}"
            )
        else:
            QMessageBox.warning(self, "Not Found", f"No Conrune pair found for date: {date_str}")
    
    def _on_search_value(self) -> None:
        """Search for pairs matching the specified value."""
        search_type = self.search_type.currentText()
        value = self.search_value.value()
        
        # Find matching pairs
        matches = self.circle_widget._service.search_by_value(search_type.lower(), value)
        
        if matches:
            # Select the first match
            first = matches[0]
            self.circle_widget._selected_degree = first.difference
            self.circle_widget.update()
            self.circle_widget.degree_clicked.emit(first)
            
            # Show results summary
            if len(matches) == 1:
                self.search_result_label.setText(
                    f"Found: {first.gregorian_date} ({first.zodiacal})"
                )
            else:
                dates = ", ".join(m.gregorian_date for m in matches[:5])
                more = f" (+{len(matches)-5} more)" if len(matches) > 5 else ""
                self.search_result_label.setText(f"Found {len(matches)}: {dates}{more}")
        else:
            self.search_result_label.setText(f"No matches for {search_type}={value}")



