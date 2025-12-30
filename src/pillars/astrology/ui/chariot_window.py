"""Chariot Window - The Merkabah Analysis UI.

This window displays the complete Chariot Midpoints analysis,
showing the 21 midpoints organized by their 7 Trios, the calculated
Axles, the Chariot Point, and the Egyptian degree symbols from the
Sacred Landscape.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Dict, List

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QPainter, QPixmap, QPalette, QBrush
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QLabel, QScrollArea,
    QFrame, QTextBrowser, QGroupBox, QPushButton, QMessageBox,
)

from shared.ui.theme import COLORS
from ..models.chariot_models import ChariotMidpoint, AxlePosition, ChariotReport
from ..services.chariot_service import ChariotService
from ..services.maat_symbols_service import MaatSymbol
from ..services.chart_storage_service import ChartStorageService
from .chart_picker_dialog import ChartPickerDialog
from pillars.tq.ui.quadset_analysis_window import SubstrateWidget

# Path to the Merkabah substrate background
SUBSTRATE_PATH = Path(__file__).parent.parent.parent.parent / "assets" / "backgrounds" / "chariot_merkabah.png"


class ChariotWindow(QWidget):
    """The Merkabah Analysis Window.
    
    Displays the complete Chariot system analysis:
    - Left panel: Trio-organized midpoint tree
    - Center panel: Summary and Chariot Point
    - Right panel: Selected item's degree symbol
    """
    
    def __init__(self, parent: Optional[QWidget] = None, window_manager=None):
        """Initialize the Chariot Window."""
        super().__init__(parent)
        self.setWindowTitle("The Celestial Chariot")
        self.setMinimumSize(1200, 800)
        
        self.window_manager = window_manager
        self.chariot_service = ChariotService()
        self.storage_service = ChartStorageService()
        self._current_report: Optional[ChariotReport] = None
        self._current_chart_name: str = ""
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Build the UI layout."""
        # Level 0: The Substrate (Thematic background)
        bg_path = str(SUBSTRATE_PATH) if SUBSTRATE_PATH.exists() else ""
        
        # Create substrate as central container
        central = SubstrateWidget(bg_path) if bg_path else QWidget()
        if not bg_path:
            central.setStyleSheet(f"background: {COLORS['background']};")
        
        # Main window layout contains only the substrate
        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(central)
        
        # Build content on top of substrate
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # Header row with title and load button
        header_row = QHBoxLayout()
        
        # Load Differentials button (disabled until chart loaded)
        self.differentials_btn = QPushButton("Δ Load Differentials")
        self.differentials_btn.setProperty("archetype", "navigator")
        self.differentials_btn.setFixedHeight(40)
        self.differentials_btn.setEnabled(False)
        self.differentials_btn.clicked.connect(self._on_load_differentials)
        header_row.addWidget(self.differentials_btn)
        
        header = QLabel("⚡ The Celestial Chariot ⚡")
        header.setFont(QFont("Georgia", 24, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {COLORS['seeker']}; padding: 8px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_row.addWidget(header, 1)
        
        load_btn = QPushButton("📂 Load Chart")
        load_btn.setProperty("archetype", "seeker")
        load_btn.setFixedHeight(40)
        load_btn.clicked.connect(self._on_load_chart)
        header_row.addWidget(load_btn)
        
        main_layout.addLayout(header_row)
        
        # Chart name label
        self.chart_name_label = QLabel("The Chariot awaits its driver — invoke a chart to begin")
        self.chart_name_label.setFont(QFont("Georgia", 12))
        self.chart_name_label.setStyleSheet(f"color: {COLORS['text_secondary']}; padding-bottom: 12px;")
        self.chart_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.chart_name_label)
        
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background: {COLORS['border']};
                width: 2px;
            }}
        """)
        
        # Left panel: Trio tree
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # Center panel: Summary
        center_panel = self._create_center_panel()
        splitter.addWidget(center_panel)
        
        # Right panel: Degree symbol
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([380, 440, 380])  # Golden Ratio approximation
        main_layout.addWidget(splitter, 1)
    
    def _on_load_chart(self) -> None:
        """Open the chart picker dialog and load the selected chart."""
        dialog = ChartPickerDialog(self.storage_service, self)
        if dialog.exec() and dialog.selected:
            summary = dialog.selected
            # Load full chart data
            loaded = self.storage_service.load_chart(summary.chart_id)
            if loaded:
                self._current_chart_name = summary.name
                self.chart_name_label.setText(f"✨ {summary.name} — {summary.event_timestamp.strftime('%Y-%m-%d %H:%M')}")
                self.chart_name_label.setStyleSheet(f"color: {COLORS['text_primary']}; padding-bottom: 12px;")
                self._load_from_request(loaded.request)
                # Enable differentials button now that we have a chart
                self.differentials_btn.setEnabled(True)
            else:
                QMessageBox.warning(self, "Load Error", f"Could not load chart: {summary.name}")
    
    def _on_load_differentials(self) -> None:
        """Open the Chariot Differentials window with the current report."""
        if not self._current_report:
            QMessageBox.warning(self, "No Chart", "Load a chart first to view differentials.")
            return
        
        from .chariot_differentials_window import ChariotDifferentialsWindow
        
        # Open via window manager if available
        if self.window_manager:
            self.window_manager.open_window(
                window_type="chariot_differentials",
                window_class=ChariotDifferentialsWindow,
                allow_multiple=True,
                report=self._current_report,
                chart_name=self._current_chart_name,
            )
        else:
            # Fallback: open directly (store reference to prevent GC)
            self._differentials_window = ChariotDifferentialsWindow(
                parent=None,
                report=self._current_report,
                chart_name=self._current_chart_name,
            )
            self._differentials_window.show()
    
    def _create_left_panel(self) -> QWidget:
        """Create the left panel with the Trio tree."""
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        
        # Sacred Levitation
        shadow = QGraphicsDropShadowEffect(panel)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 40))
        panel.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("The Seven Trios")
        title.setFont(QFont("Georgia", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['seeker']}; border: none;")
        layout.addWidget(title)
        
        # Tree widget
        self.trio_tree = QTreeWidget()
        self.trio_tree.setHeaderHidden(True)
        self.trio_tree.setStyleSheet(f"""
            QTreeWidget {{
                background: transparent;
                border: none;
                color: {COLORS['text_primary']};
            }}
            QTreeWidget::item {{
                padding: 6px;
                border-radius: 4px;
            }}
            QTreeWidget::item:selected {{
                background: {COLORS['primary_light']};
            }}
            QTreeWidget::item:hover {{
                background: {COLORS['surface_hover']};
            }}
        """)
        self.trio_tree.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.trio_tree)
        
        return panel
    
    def _create_center_panel(self) -> QWidget:
        """Create the center panel with summary information."""
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        
        # Sacred Levitation
        shadow = QGraphicsDropShadowEffect(panel)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 40))
        panel.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(panel)
        
        # Chariot Point section
        chariot_group = QGroupBox("The Chariot Point")
        chariot_group.setFont(QFont("Georgia", 12, QFont.Weight.Bold))
        chariot_group.setStyleSheet(f"""
            QGroupBox {{
                color: {COLORS['seeker']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }}
        """)
        chariot_layout = QVBoxLayout(chariot_group)
        
        self.chariot_point_label = QLabel("Awaiting the Stars...")
        self.chariot_point_label.setFont(QFont("Georgia", 16))
        self.chariot_point_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        self.chariot_point_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chariot_layout.addWidget(self.chariot_point_label)
        
        self.chariot_symbol_preview = QLabel("")
        self.chariot_symbol_preview.setFont(QFont("Georgia", 11))
        self.chariot_symbol_preview.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self.chariot_symbol_preview.setWordWrap(True)
        self.chariot_symbol_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chariot_layout.addWidget(self.chariot_symbol_preview)
        
        layout.addWidget(chariot_group)
        
        # Axles section
        axles_group = QGroupBox("The Seven Axles of Will")
        axles_group.setFont(QFont("Georgia", 12, QFont.Weight.Bold))
        axles_group.setStyleSheet(f"""
            QGroupBox {{
                color: {COLORS['accent']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }}
        """)
        axles_layout = QVBoxLayout(axles_group)
        
        self.axles_list = QLabel("The Axles remain silent...")
        self.axles_list.setFont(QFont("Georgia", 10))
        self.axles_list.setStyleSheet(f"color: {COLORS['text_primary']};")
        self.axles_list.setWordWrap(True)
        axles_layout.addWidget(self.axles_list)
        
        layout.addWidget(axles_group)
        
        # Fateful positions
        fateful_group = QGroupBox("Fateful Positions")
        fateful_group.setFont(QFont("Georgia", 12, QFont.Weight.Bold))
        fateful_group.setStyleSheet(f"""
            QGroupBox {{
                color: {COLORS['error']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }}
        """)
        fateful_layout = QVBoxLayout(fateful_group)
        
        self.fateful_label = QLabel("The Fates have not spoken...")
        self.fateful_label.setFont(QFont("Georgia", 10))
        self.fateful_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self.fateful_label.setWordWrap(True)
        fateful_layout.addWidget(self.fateful_label)
        
        layout.addWidget(fateful_group)
        layout.addStretch()
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Create the right panel for degree symbol display."""
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        
        # Sacred Levitation
        shadow = QGraphicsDropShadowEffect(panel)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 40))
        panel.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(panel)
        
        # Title
        self.symbol_title = QLabel("Choose a Power to Reveal Its Symbol")
        self.symbol_title.setFont(QFont("Georgia", 14, QFont.Weight.Bold))
        self.symbol_title.setStyleSheet(f"color: {COLORS['seeker']}; border: none;")
        layout.addWidget(self.symbol_title)
        
        # Symbol content
        self.symbol_browser = QTextBrowser()
        self.symbol_browser.setStyleSheet(f"""
            QTextBrowser {{
                background: transparent;
                border: none;
                color: {COLORS['text_primary']};
                font-family: Georgia;
                font-size: 12pt;
            }}
        """)
        self.symbol_browser.setOpenExternalLinks(False)
        layout.addWidget(self.symbol_browser)
        
        return panel
    
    def load_from_positions(self, planet_positions: Dict[str, float]) -> None:
        """Load chart data from planet positions.
        
        Args:
            planet_positions: Dict mapping planet name to ecliptic longitude
        """
        self._current_report = self.chariot_service.generate_from_positions(planet_positions)
        self._populate_ui()
    
    def load_from_chart(self, chart) -> None:
        """Load chart data from a ChartResult.
        
        Args:
            chart: ChartResult from astrology calculation
        """
        self._current_report = self.chariot_service.generate_chariot_report(chart)
        self._populate_ui()
    
    def _load_from_request(self, request) -> None:
        """Load chart by recalculating from a ChartRequest.
        
        Args:
            request: ChartRequest to calculate
        """
        from ..services.openastro_service import OpenAstroService
        
        # Recalculate the chart from the request
        service = OpenAstroService()
        result = service.generate_chart(request)
        
        # Now generate the Chariot report
        self._current_report = self.chariot_service.generate_chariot_report(result)
        self._populate_ui()
    
    def _populate_ui(self) -> None:
        """Populate the UI with the current report data."""
        if not self._current_report:
            return
        
        report = self._current_report
        
        # Populate the tree
        self.trio_tree.clear()
        
        # Group midpoints by trio
        trio_groups: Dict[str, List[ChariotMidpoint]] = {}
        for mp in report.midpoints:
            if mp.trio_id:
                if mp.trio_id not in trio_groups:
                    trio_groups[mp.trio_id] = []
                trio_groups[mp.trio_id].append(mp)
        
        # Trio names and icons
        trio_info = {
            "context": ("⚙ Context of the Journey", "Fool + Hanged Man + Aeon"),
            "vitality": ("🔥 Engine of Vitality", "Magus + Fortune + Sun"),
            "navigation": ("🧭 Navigation System", "Priestess + Adjustment + Moon"),
            "form": ("🏛 Relationship with Form", "Empress + Hermit + Devil"),
            "will": ("⚔ Arsenal of Will", "Emperor + Lust + Tower"),
            "transformation": ("🦋 Process of Transformation", "Hierophant + Death + Star"),
            "great_work": ("🌟 The Great Work", "Lovers + Art + Universe"),
        }
        
        for trio_id, midpoints in trio_groups.items():
            info = trio_info.get(trio_id, (trio_id, ""))
            
            # Find the axle for this trio
            axle = next((ax for ax in report.axles if ax.id == trio_id), None)
            axle_text = f" → {axle.sign} {axle.sign_degree:.1f}°" if axle else ""
            
            trio_item = QTreeWidgetItem([f"{info[0]}{axle_text}"])
            trio_item.setFont(0, QFont("Georgia", 11, QFont.Weight.Bold))
            trio_item.setData(0, Qt.ItemDataRole.UserRole, ("trio", trio_id, axle))
            
            for mp in midpoints:
                symbol = report.midpoint_symbols.get(mp.id)
                mp_item = QTreeWidgetItem([f"  {mp.name}: {mp.sign} {mp.sign_degree:.1f}°"])
                mp_item.setFont(0, QFont("Georgia", 10))
                mp_item.setData(0, Qt.ItemDataRole.UserRole, ("midpoint", mp.id, mp))
                trio_item.addChild(mp_item)
            
            self.trio_tree.addTopLevelItem(trio_item)
            trio_item.setExpanded(True)
        
        # Chariot Point
        cp = report.chariot_point
        self.chariot_point_label.setText(f"☆ {cp.sign} {cp.sign_degree:.1f}° ☆")
        self.chariot_symbol_preview.setText(f'"{report.chariot_symbol.text[:150]}..."')
        
        # Axles list
        axle_lines = []
        for ax in report.axles:
            axle_lines.append(f"• {ax.name}: {ax.sign} {ax.sign_degree:.1f}°")
        self.axles_list.setText("\n".join(axle_lines))
        
        # Fateful positions
        if report.fateful_positions:
            fateful_lines = []
            for fp in report.fateful_positions:
                point_name = fp.affected_point.name if hasattr(fp.affected_point, 'name') else "Unknown"
                fateful_lines.append(f"⚡ {point_name} at {fp.name} (orb: {fp.orb:.1f}°)")
            self.fateful_label.setText("\n".join(fateful_lines))
            self.fateful_label.setStyleSheet(f"color: {COLORS['warning']};")
        else:
            self.fateful_label.setText("The Fates have not spoken — no alignments detected")
            self.fateful_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
    
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle tree item click."""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data or not self._current_report:
            return
        
        item_type, item_id, obj = data
        report = self._current_report
        
        if item_type == "midpoint":
            mp: ChariotMidpoint = obj
            symbol = report.midpoint_symbols.get(mp.id)
            
            self.symbol_title.setText(f"{mp.name}")
            
            html = f"""
            <h3 style="color: {COLORS['seeker']};">{mp.name}</h3>
            <p><b>Planets:</b> {mp.planet_a} / {mp.planet_b}</p>
            <p><b>Position:</b> {mp.sign} {mp.sign_degree:.2f}°</p>
            <p><b>Keywords:</b> {', '.join(mp.keywords)}</p>
            <hr>
            <h4 style="color: {COLORS['accent']};">Heaven {symbol.heaven}: {symbol.heaven_name}</h4>
            <p style="font-style: italic; font-size: 14pt; line-height: 1.6;">
                "{symbol.text}"
            </p>
            """
            self.symbol_browser.setHtml(html)
        
        elif item_type == "trio":
            axle: AxlePosition = obj
            if axle:
                symbol = report.axle_symbols.get(axle.id)
                
                self.symbol_title.setText(f"{axle.name}")
                
                mp_names = [mp.name for mp in axle.midpoints]
                html = f"""
                <h3 style="color: {COLORS['seeker']};">{axle.name}</h3>
                <p><b>Components:</b> {' + '.join(mp_names)}</p>
                <p><b>Position:</b> {axle.sign} {axle.sign_degree:.2f}°</p>
                <p>{axle.description}</p>
                <hr>
                <h4 style="color: {COLORS['accent']};">Heaven {symbol.heaven}: {symbol.heaven_name}</h4>
                <p style="font-style: italic; font-size: 14pt; line-height: 1.6;">
                    "{symbol.text}"
                </p>
                """
                self.symbol_browser.setHtml(html)
