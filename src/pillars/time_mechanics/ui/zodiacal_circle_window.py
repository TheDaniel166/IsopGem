"""
Zodiacal Circle Window - Main window for Trigrammic Time Keeping.

Displays the interactive Zodiacal Circle with an info panel showing
selected Conrune pair details.
"""
from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QSizePolicy, QCheckBox
)

from .zodiacal_circle_widget import ZodiacalCircleWidget
from ..models.thelemic_calendar_models import ConrunePair, ZODIAC_SIGNS


class ZodiacalCircleWindow(QWidget):
    """
    Main window for the Trigrammic Time Keeper featuring the Zodiacal Circle.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
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
        """Create the info panel showing selected Conrune pair details."""
        panel = QFrame()
        panel.setObjectName("info_panel")
        panel.setMinimumWidth(280)
        panel.setMaximumWidth(350)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("✦ Selected Day ✦")
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
        
        # Instruction label (shown when nothing selected)
        self.instruction_label = QLabel(
            "Click on any degree in the circle\nto reveal its Conrune pair."
        )
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction_label.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(self.instruction_label)
        
        # Info fields (hidden until selection)
        self.info_container = QWidget()
        info_layout = QVBoxLayout(self.info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(16)
        
        # Gregorian Date
        self.date_label = self._create_info_row("Date", "")
        info_layout.addWidget(self.date_label)
        
        # Zodiacal Position
        self.zodiacal_label = self._create_info_row("Zodiacal", "")
        info_layout.addWidget(self.zodiacal_label)
        
        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background-color: #2a2a4e;")
        sep2.setFixedHeight(1)
        info_layout.addWidget(sep2)
        
        # Conrune Pair section
        pair_title = QLabel("Conrune Pair")
        pair_title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        pair_title.setStyleSheet("color: #D4AF37;")
        info_layout.addWidget(pair_title)
        
        # Ditrune (Day)
        self.ditrune_label = self._create_info_row("Ditrune (Day)", "")
        info_layout.addWidget(self.ditrune_label)
        
        # Contrune (Night)
        self.contrune_label = self._create_info_row("Contrune (Night)", "")
        info_layout.addWidget(self.contrune_label)
        
        # Difference
        self.difference_label = self._create_info_row("Difference (Tension)", "")
        info_layout.addWidget(self.difference_label)
        
        # Prime Ditrune indicator
        self.prime_label = QLabel("")
        self.prime_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prime_label.setStyleSheet(
            "color: #ff2a6d; font-weight: bold; font-size: 12pt;"
        )
        info_layout.addWidget(self.prime_label)
        
        info_layout.addStretch()
        
        self.info_container.hide()
        layout.addWidget(self.info_container)
        
        # --- Aspects Panel (Divisors of 360) ---
        aspects_title = QLabel("✧ Aspects (Divisors of 360°) ✧")
        aspects_title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        aspects_title.setStyleSheet("color: #D4AF37;")
        aspects_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(aspects_title)
        
        # Scrollable checkbox area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(200)
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
        
        checkbox_container = QWidget()
        checkbox_layout = QVBoxLayout(checkbox_container)
        checkbox_layout.setContentsMargins(4, 4, 4, 4)
        checkbox_layout.setSpacing(4)
        
        self._divisor_checkboxes = {}
        
        scroll.setWidget(checkbox_container)
        layout.addWidget(scroll)
        
        # Populate checkboxes (done after widget exists)
        self._checkbox_container = checkbox_container
        
        return panel
    
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
        
        # Check if we have a selection and active divisors
        if not hasattr(self.circle_widget, '_selected_degree') or not self.circle_widget._selected_degree:
            return
        if not hasattr(self.circle_widget, '_active_divisors') or not self.circle_widget._active_divisors:
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
        
        self._related_layout.addStretch()
