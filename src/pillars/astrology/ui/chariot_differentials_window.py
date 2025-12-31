"""Chariot Differentials Window - Maps 21 midpoints to Conrune pairs.

This window bridges the Astrology and Time Mechanics pillars by:
1. Taking the 21 Chariot midpoints from a loaded chart
2. Mapping each midpoint's zodiacal degree to its corresponding Conrune pair
"""
from __future__ import annotations

from typing import Dict, List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction, QPixmap, QPainter, QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QMenu,
    QTabWidget, QListWidget, QListWidgetItem, QSplitter,
    QTreeWidget, QTreeWidgetItem
)

from shared.ui.theme import COLORS
from shared.services.time.thelemic_calendar_service import ThelemicCalendarService
from shared.services.astro_glyph_service import astro_glyphs
from ..models.chariot_models import ChariotReport, ChariotMidpoint
from .chariot_canvas import ChariotCanvas


class SubstrateWidget(QWidget):
    """Widget that paints a background image scaled to fill the entire widget."""
    
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self._pixmap = QPixmap(image_path)
        self._bg_color = QColor(COLORS['background'])
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # Fill with background color first
        painter.fillRect(self.rect(), self._bg_color)
        
        # Scale pixmap to fill widget (aspect fill)
        if not self._pixmap.isNull():
            scaled = self._pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            # Center the scaled pixmap
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)


# Tarot symbols for midpoints
MIDPOINT_SYMBOLS = {
    "The Magician": "☉",
    "The High Priestess": "☾",
    "The Empress": "♀",
    "The Emperor": "♈",
    "The Hierophant": "♉",
    "The Lovers": "♊",
    "Strength": "♌",
    "The Hermit": "♍",
    "Wheel of Fortune": "♃",
    "Justice": "♎",
    "The Hanged Man": "☿",
    "Death": "♏",
    "Temperance": "♐",
    "The Devil": "♑",
    "The Tower": "♂",
    "The Star": "♒",
    "The Moon": "♓",
    "The Sun": "☉",
    "Judgment": "♇",
    "The World": "♄",
    "The Fool": "⚡",
}


class ChariotDifferentialsWindow(QWidget):
    """Window for mapping Chariot midpoints to Conrune pairs and visualizing Axles."""
    
    def __init__(
        self, 
        parent: Optional[QWidget] = None, 
        window_manager=None,
        report: Optional[ChariotReport] = None,
        chart_name: str = ""
    ):
        super().__init__(parent)
        self.setWindowTitle("Chariot Differentials")
        self.resize(1100, 750)
        
        self.window_manager = window_manager
        self._calendar_service = ThelemicCalendarService()
        self._report = report
        self._chart_name = chart_name
        
        # Store computed values for context menu
        self._midpoint_differences: List[int] = []
        self._midpoint_ditrunes: List[int] = []
        self._midpoint_contrunes: List[int] = []
        self._total_difference = 0
        self._total_ditrune = 0
        self._total_contrune = 0
        
        # Store 7 Axle subtotals for cross-pillar transfer
        # Maps axle_id (1-7) -> {"difference": int, "ditrune": int, "contrune": int}
        self._axle_subtotals: Dict[int, Dict[str, int]] = {}
        
        # UI Components
        self.tabs: QTabWidget
        self.results_table: QTableWidget
        self.axle_list: QListWidget # Legacy, replaced by tree but kept typings for safety if needed
        self.axle_tree: QTreeWidget
        self.canvas: ChariotCanvas
        self.status_label: QLabel
        self.chart_label: QLabel
        
        self._build_ui()
        
        if report:
            self._populate_data()
    
    def _build_ui(self) -> None:
        """Build the window UI using Substrate layout."""
        # Main layout wrapper
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        
        # Level 0: The Substrate
        import os
        # Trying to locate the asset based on current location
        # src/pillars/astrology/ui/ -> .../src/assets
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        bg_path = os.path.join(base_path, "assets", "backgrounds", "chariot_merkabah.png")
        
        substrate = SubstrateWidget(bg_path)
        root_layout.addWidget(substrate)
        
        # Content Layout inside Substrate
        main_layout = QVBoxLayout(substrate)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        
        # Header Area
        header = QFrame()
        # header.setStyleSheet(f"background-color: {COLORS['surface']}; border-bottom: 1px solid {COLORS['border']};")
        # Removing opaque background for header to show substrate texture
        header.setStyleSheet("background: transparent;")
        
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        title_box = QHBoxLayout()
        title = QLabel("Δ Chariot Differentials")
        title.setFont(QFont("Georgia", 24, QFont.Weight.Bold))
        # Use a Gold/Seeker color to pop against dark substrate
        title.setStyleSheet(f"color: {COLORS['seeker']}; letter-spacing: 1px;") 
        title_box.addWidget(title)
        title_box.addStretch()
        
        self.chart_label = QLabel(f"Chart: {self._chart_name}" if self._chart_name else "No chart loaded")
        self.chart_label.setFont(QFont("Georgia", 11))
        self.chart_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        title_box.addWidget(self.chart_label)
        
        header_layout.addLayout(title_box)
        main_layout.addWidget(header)
        
        # Content Area (Tabs)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                background: {COLORS['surface']}; /* Slightly opaque surface */
                border-radius: 8px;
            }}
            QTabWidget::tab-bar {{
                alignment: left;
            }}
            QTabBar::tab {{
                background: transparent;
                color: {COLORS['text_secondary']};
                padding: 10px 24px;
                border: none;
                border-bottom: 2px solid transparent;
                margin-right: 4px;
                font-size: 11pt;
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                color: {COLORS['primary']};
                border-bottom: 2px solid {COLORS['primary']};
            }}
            QTabBar::tab:hover:!selected {{
                color: {COLORS['text_primary']};
            }}
        """)
        
        # Tab 1: Data Grid
        self._setup_grid_tab()
        
        # Tab 2: Visualization
        self._setup_viz_tab()
        
        main_layout.addWidget(self.tabs)
        
        # Footer
        footer = QFrame()
        footer.setStyleSheet("background: transparent;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(10, 4, 10, 4)
        
        self.status_label = QLabel("Awaiting Chariot data...")
        self.status_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-style: italic;")
        footer_layout.addWidget(self.status_label)
        
        main_layout.addWidget(footer)
        
    def _setup_grid_tab(self) -> None:
        """Setup the Data Grid tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Midpoint", "Degree", "Difference", "Ditrune", "Contrune", "Calendar Date"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['surface']}; 
                alternate-background-color: {COLORS['surface_hover']};
                gridline-color: {COLORS['border']};
                border: none;
                border-radius: 0px; 
            }}
            QHeaderView::section {{
                background-color: {COLORS['background_alt']};
                color: {COLORS['text_primary']};
                padding: 12px;
                border: none;
                border-bottom: 2px solid {COLORS['border']};
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            QTableWidget::item {{
                padding: 8px;
                color: {COLORS['text_primary']};
                border-bottom: 1px solid {COLORS['border']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['primary_light']};
                color: {COLORS['primary']};
            }}
        """)
        
        # Enable context menu
        self.results_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self._show_context_menu)
        
        layout.addWidget(self.results_table)
        self.tabs.addTab(tab, "Data Grid")
        
    def _setup_viz_tab(self) -> None:
        """Setup the Visualization tab."""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {COLORS['border']};
                width: 2px;
            }}
        """)
        
        # Left Pane: Axle Tree
        tree_frame = QFrame()
        tree_frame.setMinimumWidth(280)
        tree_frame.setMaximumWidth(400)
        # Transparent frame
        tree_frame.setStyleSheet("background: transparent;")
        
        tree_layout = QVBoxLayout(tree_frame)
        tree_layout.setContentsMargins(0, 0, 16, 0)
        
        list_label = QLabel("Axles & Geometry")
        list_label.setFont(QFont("Georgia", 11, QFont.Weight.Bold))
        list_label.setStyleSheet(f"color: {COLORS['text_secondary']}; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px;")
        tree_layout.addWidget(list_label)
        
        self.axle_tree = QTreeWidget()
        self.axle_tree.setHeaderHidden(True)
        # Using specific styling for tree
        self.axle_tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                color: {COLORS['text_primary']};
                font-size: 11pt;
            }}
            QTreeWidget::item {{
                padding: 6px;
                border-bottom: 1px solid transparent;
            }}
            QTreeWidget::item:hover {{
                background-color: {COLORS['surface_hover']};
            }}
            QTreeWidget::item:selected {{
                background-color: {COLORS['primary_light']};
                color: {COLORS['primary']};
                font-weight: bold;
                border-radius: 4px;
            }}
            /* Reset branch icons to default to fix missing SVG error */
            QTreeWidget::branch {{
                background: transparent;
            }}
        """)
        self.axle_tree.itemClicked.connect(self._on_tree_item_clicked)
        tree_layout.addWidget(self.axle_tree)
        
        splitter.addWidget(tree_frame)
        
        # Right Pane: Canvas
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        
        self.canvas = ChariotCanvas(report=self._report)
        self.canvas.setStyleSheet(f"""
            QWidget {{
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                background-color: {COLORS['void']}; 
            }}
        """)
        canvas_layout.addWidget(self.canvas)
        
        splitter.addWidget(canvas_container)
        
        # Set initial sizes (30% list, 70% canvas)
        splitter.setSizes([320, 780])
        
        layout.addWidget(splitter)
        self.tabs.addTab(tab, "Visualization")
    
    def _populate_data(self) -> None:
        """Populate grid and visualization data."""
        if not self._report:
            return
            
        self._populate_grid()
        self._populate_viz()
        self.status_label.setText(f"Calculated {len(self._report.midpoints)} midpoints + Chariot Point")
        
    def _populate_viz(self) -> None:
        """Populate visualization tab data."""
        from PyQt6.QtWidgets import QTreeWidgetItem
        
        self.axle_tree.clear()
        self.canvas.set_chariot_data(self._report) # type: ignore
        
        # Add Axles to tree
        for axle in self._report.axles:
            # Root Item for Axle
            axle_item = QTreeWidgetItem(self.axle_tree)
            axle_item.setText(0, f"⚙ {axle.name}")
            axle_item.setData(0, Qt.ItemDataRole.UserRole, {
                "type": "axle", 
                "id": axle.id
            })
            axle_item.setFont(0, QFont("Georgia", 11, QFont.Weight.Bold))
            axle_item.setExpanded(False) # Collapsed by default
            
            # Child Items for Midpoints (Tarot Cards)
            for midpoint in axle.midpoints:
                symbol = MIDPOINT_SYMBOLS.get(midpoint.name, "✦")
                pt_item = QTreeWidgetItem(axle_item)
                pt_item.setText(0, f"  {symbol} {midpoint.name}")
                pt_item.setFont(0, QFont("Georgia", 10))
                pt_item.setData(0, Qt.ItemDataRole.UserRole, {
                    "type": "point",
                    "axle_id": axle.id,
                    "name": midpoint.name
                })
            
            # Child Item for Axle Point (Center)
            center_item = QTreeWidgetItem(axle_item)
            center_item.setText(0, "  ⌖ Axle Point")
            center_item.setForeground(0, Qt.GlobalColor.gray)
            center_item.setFont(0, QFont("Georgia", 10, QFont.Weight.Bold))
            center_item.setData(0, Qt.ItemDataRole.UserRole, {
                "type": "point", # Treat as a point for highlighting logic
                "axle_id": axle.id,
                "name": "Axle Point" # Special name handled in Canvas
            })
            
        # Add Chariot Point just for info (since it's always visible)
        chariot_item = QTreeWidgetItem(self.axle_tree)
        chariot_item.setText(0, "⚡ Chariot Point")
        chariot_item.setFlags(Qt.ItemFlag.NoItemFlags) # Non-selectable
        chariot_item.setForeground(0, Qt.GlobalColor.darkRed)
        chariot_item.setFont(0, QFont("Georgia", 11, QFont.Weight.Bold))
    
    def _on_tree_item_clicked(self, item, column: int) -> None:
        """Handle tree item selection."""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
            
        item_type = data.get("type")
        
        if item_type == "axle":
            # Highlight entire Axle hierarchy
            axle_id = data.get("id")
            self.canvas.set_highlighted_axle(axle_id)
            
        elif item_type == "point":
            # Highlight Axle AND specific Point
            axle_id = data.get("axle_id")
            point_name = data.get("name")
            
            # Ensure parent Axle is the active highlighted axle
            self.canvas.set_highlighted_axle(axle_id)
            # Then set the specific point highlight
            self.canvas.set_highlighted_point(point_name)

    def _populate_grid(self) -> None:
        """Populate the results table with midpoint data organized by Axle."""
        if not self._report:
            return
        
        self.results_table.setRowCount(0)
        
        # Reset totals
        self._midpoint_differences = []
        self._midpoint_ditrunes = []
        self._midpoint_contrunes = []
        self._axle_subtotals = {}  # Clear for fresh calculation
        
        chariot_diff = 0
        chariot_ditrune = 0
        chariot_contrune = 0
        
        # Process each Axle and its midpoints
        for axle in self._report.axles:
            # Add Axle header row
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            axle_header = QTableWidgetItem(f"⚙ {axle.name}")
            axle_header.setFont(QFont("Georgia", 11, QFont.Weight.Bold))
            axle_header.setBackground(Qt.GlobalColor.lightGray)
            self.results_table.setItem(row, 0, axle_header)
            
            # Empty cells for header
            for col in range(1, 6):
                empty = QTableWidgetItem("")
                empty.setBackground(Qt.GlobalColor.lightGray)
                self.results_table.setItem(row, col, empty)
            
            # Track axle subtotals
            axle_diffs = []
            axle_ditrunes = []
            axle_contrunes = []
            
            # Add each midpoint under this axle
            for midpoint in axle.midpoints:
                degree = midpoint.longitude
                
                # Map degree to Conrune pair
                diff = self._calendar_service.zodiac_degree_to_difference(degree)
                pair = self._calendar_service.get_pair_by_difference(diff) if diff else None
                
                # Add row
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                
                # Midpoint with symbol
                symbol = MIDPOINT_SYMBOLS.get(midpoint.name, "✦")
                midpoint_item = QTableWidgetItem(f"    {symbol} {midpoint.name}")
                midpoint_item.setFont(QFont("Georgia", 10))
                self.results_table.setItem(row, 0, midpoint_item)
                
                # Degree (zodiacal format with glyphs)
                degree_item = QTableWidgetItem(astro_glyphs.to_zodiacal_string(degree))
                degree_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                degree_item.setFont(QFont(astro_glyphs.get_font_family(), 12))
                self.results_table.setItem(row, 1, degree_item)
                
                if pair:
                    # Track values
                    self._midpoint_differences.append(pair.difference)
                    self._midpoint_ditrunes.append(pair.ditrune)
                    self._midpoint_contrunes.append(pair.contrune)
                    axle_diffs.append(pair.difference)
                    axle_ditrunes.append(pair.ditrune)
                    axle_contrunes.append(pair.contrune)
                    
                    # Difference
                    diff_item = QTableWidgetItem(str(pair.difference))
                    diff_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.results_table.setItem(row, 2, diff_item)
                    
                    # Ditrune
                    ditrune_item = QTableWidgetItem(str(pair.ditrune))
                    ditrune_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.results_table.setItem(row, 3, ditrune_item)
                    
                    # Contrune
                    contrune_item = QTableWidgetItem(str(pair.contrune))
                    contrune_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.results_table.setItem(row, 4, contrune_item)
                    
                    # Calendar date
                    self.results_table.setItem(row, 5, QTableWidgetItem(pair.gregorian_date))
                else:
                    for col in range(2, 6):
                        self.results_table.setItem(row, col, QTableWidgetItem("—"))
            
            # Add Axle subtotal row
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            subtotal_label = QTableWidgetItem(f"  Σ {axle.name} Subtotal")
            subtotal_label.setFont(QFont("Georgia", 10, QFont.Weight.Bold))
            subtotal_label.setForeground(Qt.GlobalColor.darkBlue)
            self.results_table.setItem(row, 0, subtotal_label)
            self.results_table.setItem(row, 1, QTableWidgetItem(""))
            
            for col, total in [(2, sum(axle_diffs)), (3, sum(axle_ditrunes)), (4, sum(axle_contrunes))]:
                item = QTableWidgetItem(str(total))
                item.setFont(QFont("Georgia", 10, QFont.Weight.Bold))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(Qt.GlobalColor.darkBlue)
                self.results_table.setItem(row, col, item)
            
            self.results_table.setItem(row, 5, QTableWidgetItem(""))
            
            # Store axle subtotals for cross-pillar transfer
            self._axle_subtotals[axle.id] = {
                "difference": sum(axle_diffs),
                "ditrune": sum(axle_ditrunes),
                "contrune": sum(axle_contrunes)
            }
        
        # Calculate 21 Midpoints total
        total_21_diff = sum(self._midpoint_differences)
        total_21_ditrune = sum(self._midpoint_ditrunes)
        total_21_contrune = sum(self._midpoint_contrunes)
        
        # Add 21 Midpoints total row
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        total_21_item = QTableWidgetItem("Σ TOTAL (21 Midpoints)")
        total_21_item.setFont(QFont("Georgia", 11, QFont.Weight.Bold))
        total_21_item.setForeground(Qt.GlobalColor.darkMagenta)
        self.results_table.setItem(row, 0, total_21_item)
        self.results_table.setItem(row, 1, QTableWidgetItem(""))
        
        for col, total in [(2, total_21_diff), (3, total_21_ditrune), (4, total_21_contrune)]:
            item = QTableWidgetItem(str(total))
            item.setFont(QFont("Georgia", 11, QFont.Weight.Bold))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(Qt.GlobalColor.darkMagenta)
            self.results_table.setItem(row, col, item)
        
        self.results_table.setItem(row, 5, QTableWidgetItem(""))
        
        # Add Chariot Point row
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        chariot = self._report.chariot_point
        chariot_degree = chariot.longitude
        
        chariot_diff_val = self._calendar_service.zodiac_degree_to_difference(chariot_degree)
        chariot_pair = self._calendar_service.get_pair_by_difference(chariot_diff_val) if chariot_diff_val else None
        
        chariot_item = QTableWidgetItem("⚡ THE CHARIOT POINT")
        chariot_item.setFont(QFont("Georgia", 11, QFont.Weight.Bold))
        chariot_item.setForeground(Qt.GlobalColor.darkRed)
        self.results_table.setItem(row, 0, chariot_item)
        
        chariot_deg_item = QTableWidgetItem(astro_glyphs.to_zodiacal_string(chariot_degree))
        chariot_deg_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        chariot_deg_item.setFont(QFont(astro_glyphs.get_font_family(), 12))
        self.results_table.setItem(row, 1, chariot_deg_item)
        
        if chariot_pair:
            chariot_diff = chariot_pair.difference
            chariot_ditrune = chariot_pair.ditrune
            chariot_contrune = chariot_pair.contrune
            
            for col, val in [(2, chariot_diff), (3, chariot_ditrune), (4, chariot_contrune)]:
                item = QTableWidgetItem(str(val))
                item.setFont(QFont("Georgia", 10, QFont.Weight.Bold))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(Qt.GlobalColor.darkRed)
                self.results_table.setItem(row, col, item)
            
            date_item = QTableWidgetItem(chariot_pair.gregorian_date)
            date_item.setFont(QFont("Georgia", 10, QFont.Weight.Bold))
            self.results_table.setItem(row, 5, date_item)
        else:
            for col in range(2, 6):
                self.results_table.setItem(row, col, QTableWidgetItem("—"))
        
        # Add 22 Total (with Chariot) row
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        total_22_diff = total_21_diff + chariot_diff
        total_22_ditrune = total_21_ditrune + chariot_ditrune
        total_22_contrune = total_21_contrune + chariot_contrune
        
        total_22_item = QTableWidgetItem("Σ GRAND TOTAL (21 + Chariot)")
        total_22_item.setFont(QFont("Georgia", 11, QFont.Weight.Bold))
        total_22_item.setForeground(Qt.GlobalColor.darkGreen)
        self.results_table.setItem(row, 0, total_22_item)
        self.results_table.setItem(row, 1, QTableWidgetItem(""))
        
        for col, total in [(2, total_22_diff), (3, total_22_ditrune), (4, total_22_contrune)]:
            item = QTableWidgetItem(str(total))
            item.setFont(QFont("Georgia", 11, QFont.Weight.Bold))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(Qt.GlobalColor.darkGreen)
            self.results_table.setItem(row, col, item)
        
        self.results_table.setItem(row, 5, QTableWidgetItem(""))
        
        # Store for context menu
        self._total_difference = total_21_diff
        self._total_ditrune = total_21_ditrune
        self._total_contrune = total_21_contrune
    
    def _show_context_menu(self, position) -> None:
        """Show context menu on table right-click."""
        if not self._midpoint_differences:
            return
        
        # Get the clicked cell
        item = self.results_table.itemAt(position)
        if not item:
            return
        
        row = item.row()
        col = item.column()
        
        # Only columns 2 (Difference), 3 (Ditrune), 4 (Contrune) have numeric values
        if col not in (2, 3, 4):
            # If clicked on another column, default to Difference column
            col = 2
        
        cell_item = self.results_table.item(row, col)
        if not cell_item:
            return
        
        cell_text = cell_item.text()
        
        # Skip empty or non-numeric cells
        try:
            value = int(cell_text)
        except (ValueError, TypeError):
            return
        
        # Get the row name for display
        row_name_item = self.results_table.item(row, 0)
        row_name = row_name_item.text() if row_name_item else f"Row {row}"
        col_names = {2: "Difference", 3: "Ditrune", 4: "Contrune"}
        col_name = col_names.get(col, "Value")
        
        menu = QMenu(self)
        
        # Send to Quadset Analysis
        quadset_action = QAction(f"Send {col_name} ({value}) to Quadset Analysis", menu)
        quadset_action.triggered.connect(lambda: self._send_value_to_quadset(value))
        menu.addAction(quadset_action)
        
        # Look up in Database
        lookup_action = QAction(f"Look up {col_name} ({value}) in Database", menu)
        lookup_action.triggered.connect(lambda: self._lookup_value_in_database(value))
        menu.addAction(lookup_action)
        
        # Check if this is a total or subtotal row — offer "Send 7 Axles to Geometry"
        if self._axle_subtotals and len(self._axle_subtotals) == 7:
            # Add separator and Geometry options
            menu.addSeparator()
            
            diff_action = QAction("⚡ Send 7 Axle Differences to Geometry", menu)
            diff_action.triggered.connect(lambda: self._send_axles_to_geometry("difference"))
            menu.addAction(diff_action)
            
            ditrune_action = QAction("⚡ Send 7 Axle Ditrunes to Geometry", menu)
            ditrune_action.triggered.connect(lambda: self._send_axles_to_geometry("ditrune"))
            menu.addAction(ditrune_action)
            
            contrune_action = QAction("⚡ Send 7 Axle Contrunes to Geometry", menu)
            contrune_action.triggered.connect(lambda: self._send_axles_to_geometry("contrune"))
            menu.addAction(contrune_action)
        
        menu.exec(self.results_table.viewport().mapToGlobal(position))
    
    def _send_value_to_quadset(self, value: int) -> None:
        """Send a value to Quadset Analysis."""
        from shared.signals.navigation_bus import navigation_bus
        
        navigation_bus.request_window.emit(
            "quadset_analysis",
            {"initial_value": value}
        )
    
    def _lookup_value_in_database(self, value: int) -> None:
        """Look up a value in the Saved Calculations database."""
        from shared.signals.navigation_bus import navigation_bus
        
        navigation_bus.request_window.emit(
            "saved_calculations",
            {"initial_value": value}
        )
    
    def _send_axles_to_geometry(self, column: str) -> None:
        """Send 7 Axle subtotals to Geometric Transitions as heptagon vertices.
        
        Args:
            column: Which column to send ('difference', 'ditrune', or 'contrune')
        """
        if not self._axle_subtotals or len(self._axle_subtotals) != 7:
            return
        
        from shared.signals.navigation_bus import navigation_bus
        
        # Extract values in axle order (sorted by axle_id 1-7)
        values = [
            self._axle_subtotals[axle_id][column]
            for axle_id in sorted(self._axle_subtotals.keys())
        ]
        
        navigation_bus.request_window.emit(
            "geometric_transitions",
            {"initial_values": values}
        )
