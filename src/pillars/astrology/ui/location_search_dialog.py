"""Location Search Dialog - The Cartographer's Sanctum.

A comprehensive location management interface providing:
- City/place search with debounced input
- Favorites management for quick access
- Coordinate-based reverse geocoding
- Default location persistence
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QMessageBox,
    QFormLayout, QGroupBox, QTabWidget, QWidget, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from typing import Optional, List
import json
from pathlib import Path

from shared.ui.theme import COLORS
from ..services import LocationLookupService, LocationLookupError, LocationResult
from ..utils import AstrologyPreferences, DefaultLocation


class LocationSearchDialog(QDialog):
    """The Cartographer's Sanctum - Search, favorite, and manage locations."""
    
    location_selected = pyqtSignal(object)  # Emits LocationResult or DefaultLocation
    
    def __init__(self, preferences: AstrologyPreferences, parent=None):
        """
        Initialize the location search dialog.
        
        Args:
            preferences: AstrologyPreferences instance for managing defaults.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle("Location Search")
        self.setMinimumSize(550, 500)
        self.setModal(True)
        
        self._preferences = preferences
        self._lookup_service = LocationLookupService()
        self._results: List[LocationResult] = []
        self._favorites: List[DefaultLocation] = []
        self._default_location: Optional[DefaultLocation] = None
        self._reverse_location: Optional[LocationResult] = None
        
        # Debounce timer for search
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._perform_search)
        
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title = QLabel("🌍 The Cartographer's Sanctum")
        title.setFont(QFont("", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(title)
        
        # Tab Widget
        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)
        
        # Tab 1: Search
        self._tabs.addTab(self._build_search_tab(), "🔍 Search")
        
        # Tab 2: Favorites
        self._tabs.addTab(self._build_favorites_tab(), "⭐ Favorites")
        
        # Tab 3: Coordinates
        self._tabs.addTab(self._build_coordinates_tab(), "📐 Coordinates")
        
        # Default Location Card
        layout.addWidget(self._build_default_card())
        
        # Apply theme
        self._apply_theme()
    
    def _build_search_tab(self) -> QWidget:
        """Build the search tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        
        # Search Row
        search_row = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Enter city, state, country...")
        self._search_input.textChanged.connect(self._on_search_text_changed)
        self._search_input.returnPressed.connect(self._perform_search)
        search_row.addWidget(self._search_input, stretch=1)
        
        search_btn = QPushButton("Search")
        search_btn.setProperty("archetype", "seeker")
        search_btn.clicked.connect(self._perform_search)
        search_row.addWidget(search_btn)
        
        layout.addLayout(search_row)
        
        # Results List
        self._results_list = QListWidget()
        self._results_list.itemClicked.connect(self._on_result_clicked)
        self._results_list.itemDoubleClicked.connect(self._on_result_double_clicked)
        layout.addWidget(self._results_list)
        
        # Location Details Card
        details_group = QGroupBox("Location Details")
        details_layout = QFormLayout(details_group)
        
        self._detail_name = QLabel("—")
        details_layout.addRow("Name:", self._detail_name)
        
        self._detail_coords = QLabel("—")
        details_layout.addRow("Coordinates:", self._detail_coords)
        
        self._detail_tz = QLabel("—")
        details_layout.addRow("Timezone:", self._detail_tz)
        
        layout.addWidget(details_group)
        
        # Action Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        
        self._add_favorite_btn = QPushButton("⭐ Add to Favorites")
        self._add_favorite_btn.setProperty("archetype", "scribe")
        self._add_favorite_btn.clicked.connect(self._add_to_favorites)
        self._add_favorite_btn.setEnabled(False)
        btn_row.addWidget(self._add_favorite_btn)
        
        self._select_search_btn = QPushButton("Select")
        self._select_search_btn.setProperty("archetype", "magus")
        self._select_search_btn.clicked.connect(self._select_search_result)
        self._select_search_btn.setEnabled(False)
        btn_row.addWidget(self._select_search_btn)
        
        layout.addLayout(btn_row)
        
        return tab
    
    def _build_favorites_tab(self) -> QWidget:
        """Build the favorites tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        
        # Favorites List
        self._favorites_list = QListWidget()
        self._favorites_list.itemClicked.connect(self._on_favorite_clicked)
        self._favorites_list.itemDoubleClicked.connect(self._on_favorite_double_clicked)
        layout.addWidget(self._favorites_list)
        
        # Action Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        
        self._remove_favorite_btn = QPushButton("🗑 Remove")
        self._remove_favorite_btn.setProperty("archetype", "destroyer")
        self._remove_favorite_btn.clicked.connect(self._remove_favorite)
        self._remove_favorite_btn.setEnabled(False)
        btn_row.addWidget(self._remove_favorite_btn)
        
        self._select_favorite_btn = QPushButton("Select")
        self._select_favorite_btn.setProperty("archetype", "magus")
        self._select_favorite_btn.clicked.connect(self._select_favorite)
        self._select_favorite_btn.setEnabled(False)
        btn_row.addWidget(self._select_favorite_btn)
        
        layout.addLayout(btn_row)
        
        return tab
    
    def _build_coordinates_tab(self) -> QWidget:
        """Build the coordinates tab for reverse geocoding."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        
        # Coordinates Input
        coords_group = QGroupBox("Enter Coordinates")
        coords_layout = QFormLayout(coords_group)
        
        self._lat_input = QDoubleSpinBox()
        self._lat_input.setRange(-90.0, 90.0)
        self._lat_input.setDecimals(6)
        self._lat_input.setValue(0.0)
        coords_layout.addRow("Latitude:", self._lat_input)
        
        self._lon_input = QDoubleSpinBox()
        self._lon_input.setRange(-180.0, 180.0)
        self._lon_input.setDecimals(6)
        self._lon_input.setValue(0.0)
        coords_layout.addRow("Longitude:", self._lon_input)
        
        lookup_btn = QPushButton("🔎 Lookup Location")
        lookup_btn.setProperty("archetype", "seeker")
        lookup_btn.clicked.connect(self._reverse_geocode)
        coords_layout.addRow("", lookup_btn)
        
        layout.addWidget(coords_group)
        
        # Reverse Geocode Result
        self._reverse_group = QGroupBox("Location Found")
        reverse_layout = QFormLayout(self._reverse_group)
        
        self._reverse_name = QLabel("—")
        reverse_layout.addRow("Name:", self._reverse_name)
        
        self._reverse_coords = QLabel("—")
        reverse_layout.addRow("Coordinates:", self._reverse_coords)
        
        layout.addWidget(self._reverse_group)
        
        # Action Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        
        self._fav_reverse_btn = QPushButton("⭐ Add to Favorites")
        self._fav_reverse_btn.setProperty("archetype", "scribe")
        self._fav_reverse_btn.clicked.connect(self._add_reverse_to_favorites)
        self._fav_reverse_btn.setEnabled(False)
        btn_row.addWidget(self._fav_reverse_btn)
        
        self._select_reverse_btn = QPushButton("Select")
        self._select_reverse_btn.setProperty("archetype", "magus")
        self._select_reverse_btn.clicked.connect(self._select_reverse)
        self._select_reverse_btn.setEnabled(False)
        btn_row.addWidget(self._select_reverse_btn)
        
        layout.addLayout(btn_row)
        layout.addStretch()
        
        return tab
    
    def _build_default_card(self) -> QGroupBox:
        """Build the default location card."""
        group = QGroupBox("📍 Default Location")
        layout = QVBoxLayout(group)
        
        self._default_label = QLabel("No default location saved")
        self._default_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(self._default_label)
        
        btn_row = QHBoxLayout()
        
        self._use_default_btn = QPushButton("Use Default")
        self._use_default_btn.setProperty("archetype", "navigator")
        self._use_default_btn.clicked.connect(self._use_default)
        self._use_default_btn.setEnabled(False)
        btn_row.addWidget(self._use_default_btn)
        
        self._save_default_btn = QPushButton("Save Current as Default")
        self._save_default_btn.setProperty("archetype", "scribe")
        self._save_default_btn.clicked.connect(self._save_as_default)
        self._save_default_btn.setEnabled(False)
        btn_row.addWidget(self._save_default_btn)
        
        btn_row.addStretch()
        layout.addLayout(btn_row)
        
        return group
    
    def _apply_theme(self):
        """Apply Visual Liturgy theme."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
            }}
            QLabel {{
                color: {COLORS['text_primary']};
            }}
            QLineEdit {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 8px 12px;
            }}
            QDoubleSpinBox {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 8px 12px;
                min-width: 200px;
            }}
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
                width: 20px;
                border: none;
                background: {COLORS['surface']};
            }}
            QListWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
            }}
            QListWidget::item {{
                padding: 8px;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['primary_light']};
                color: {COLORS['primary']};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: {COLORS['surface']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                color: {COLORS['text_primary']};
            }}
            /* Tab widget styling for light theme */
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                background-color: {COLORS['surface']};
            }}
            QTabBar {{
                background: transparent;
            }}
            QTabBar::tab {{
                background: {COLORS['surface']};
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 10px 20px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background: {COLORS['primary_light']};
                color: {COLORS['primary']};
                border-color: {COLORS['primary']};
                font-weight: bold;
            }}
            QTabBar::tab:hover:!selected {{
                background: {COLORS['surface_hover']};
            }}
        """)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Data Loading
    # ─────────────────────────────────────────────────────────────────────────
    
    def _load_data(self):
        """Load default location and favorites."""
        self._default_location = self._preferences.load_default_location()
        if self._default_location:
            self._default_label.setText(
                f"{self._default_location.name} "
                f"({self._default_location.latitude:.2f}°, {self._default_location.longitude:.2f}°)"
            )
            self._use_default_btn.setEnabled(True)
        
        self._load_favorites()
    
    def _load_favorites(self):
        """Load favorites from preferences."""
        self._favorites_list.clear()
        self._favorites = self._preferences.load_favorites() if hasattr(self._preferences, 'load_favorites') else []
        
        if self._favorites:
            for fav in self._favorites:
                item = QListWidgetItem(f"{fav.name} ({fav.latitude:.2f}°, {fav.longitude:.2f}°)")
                item.setData(Qt.ItemDataRole.UserRole, fav)
                self._favorites_list.addItem(item)
        else:
            self._favorites_list.addItem("No favorites saved yet")
    
    # ─────────────────────────────────────────────────────────────────────────
    # Search Tab Logic
    # ─────────────────────────────────────────────────────────────────────────
    
    def _on_search_text_changed(self, text: str):
        """Debounce search input."""
        self._search_timer.stop()
        if text.strip():
            self._search_timer.start(500)  # 500ms debounce
    
    def _perform_search(self):
        """Execute the location search."""
        query = self._search_input.text().strip()
        if not query:
            return
        
        self._results_list.clear()
        self._results = []
        self._clear_details()
        
        try:
            from PyQt6.QtWidgets import QApplication
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            self._results = self._lookup_service.search(query)
        except LocationLookupError as exc:
            self._results_list.addItem(f"⚠️ {exc}")
            return
        except Exception as exc:
            self._results_list.addItem(f"⚠️ Error: {exc}")
            return
        finally:
            from PyQt6.QtWidgets import QApplication
            QApplication.restoreOverrideCursor()
        
        if self._results:
            for result in self._results:
                item = QListWidgetItem(result.label)
                item.setData(Qt.ItemDataRole.UserRole, result)
                self._results_list.addItem(item)
        else:
            self._results_list.addItem("No results found")
    
    def _on_result_clicked(self, item: QListWidgetItem):
        """Show details for clicked result."""
        result = item.data(Qt.ItemDataRole.UserRole)
        if result:
            self._show_details(result)
            self._select_search_btn.setEnabled(True)
            self._add_favorite_btn.setEnabled(True)
            self._save_default_btn.setEnabled(True)
    
    def _on_result_double_clicked(self, item: QListWidgetItem):
        """Select on double-click."""
        result = item.data(Qt.ItemDataRole.UserRole)
        if result:
            self.location_selected.emit(result)
            self.accept()
    
    def _show_details(self, result: LocationResult):
        """Display location details."""
        self._detail_name.setText(result.label)
        self._detail_coords.setText(f"{result.latitude:.4f}°, {result.longitude:.4f}°")
        self._detail_tz.setText(result.timezone_id or "Unknown")
    
    def _clear_details(self):
        """Clear the details display."""
        self._detail_name.setText("—")
        self._detail_coords.setText("—")
        self._detail_tz.setText("—")
        self._select_search_btn.setEnabled(False)
        self._add_favorite_btn.setEnabled(False)
    
    def _select_search_result(self):
        """Emit the selected search result."""
        item = self._results_list.currentItem()
        if item:
            result = item.data(Qt.ItemDataRole.UserRole)
            if result:
                self.location_selected.emit(result)
                self.accept()
    
    def _add_to_favorites(self):
        """Add current search result to favorites."""
        item = self._results_list.currentItem()
        if not item:
            return
        
        result: LocationResult = item.data(Qt.ItemDataRole.UserRole)
        if not result:
            return
        
        fav = DefaultLocation(
            name=result.label,
            latitude=result.latitude,
            longitude=result.longitude,
            elevation=result.elevation or 0,
            timezone_offset=0,
            timezone_id=result.timezone_id,
        )
        
        if hasattr(self._preferences, 'add_favorite'):
            self._preferences.add_favorite(fav)
            self._load_favorites()
            QMessageBox.information(self, "Saved", f"'{fav.name}' added to favorites.")
        else:
            QMessageBox.warning(self, "Not Implemented", "Favorites storage not yet implemented.")
    
    # ─────────────────────────────────────────────────────────────────────────
    # Favorites Tab Logic
    # ─────────────────────────────────────────────────────────────────────────
    
    def _on_favorite_clicked(self, item: QListWidgetItem):
        """Enable actions when favorite is clicked."""
        fav = item.data(Qt.ItemDataRole.UserRole)
        if fav:
            self._select_favorite_btn.setEnabled(True)
            self._remove_favorite_btn.setEnabled(True)
    
    def _on_favorite_double_clicked(self, item: QListWidgetItem):
        """Select favorite on double-click."""
        fav = item.data(Qt.ItemDataRole.UserRole)
        if fav:
            self.location_selected.emit(fav)
            self.accept()
    
    def _select_favorite(self):
        """Emit the selected favorite."""
        item = self._favorites_list.currentItem()
        if item:
            fav = item.data(Qt.ItemDataRole.UserRole)
            if fav:
                self.location_selected.emit(fav)
                self.accept()
    
    def _remove_favorite(self):
        """Remove the selected favorite."""
        item = self._favorites_list.currentItem()
        if not item:
            return
        
        fav = item.data(Qt.ItemDataRole.UserRole)
        if fav and hasattr(self._preferences, 'remove_favorite'):
            self._preferences.remove_favorite(fav)
            self._load_favorites()
            self._remove_favorite_btn.setEnabled(False)
            self._select_favorite_btn.setEnabled(False)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Coordinates Tab Logic
    # ─────────────────────────────────────────────────────────────────────────
    
    def _reverse_geocode(self):
        """Perform reverse geocoding lookup."""
        lat = self._lat_input.value()
        lon = self._lon_input.value()
        
        try:
            from PyQt6.QtWidgets import QApplication
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            results = self._lookup_service.reverse_geocode(lat, lon)
        except Exception as exc:
            self._reverse_name.setText(f"⚠️ {exc}")
            self._reverse_coords.setText("—")
            self._select_reverse_btn.setEnabled(False)
            self._fav_reverse_btn.setEnabled(False)
            return
        finally:
            from PyQt6.QtWidgets import QApplication
            QApplication.restoreOverrideCursor()
        
        if results:
            self._reverse_location = results[0] if isinstance(results, list) else results
            self._reverse_name.setText(self._reverse_location.label)
            self._reverse_coords.setText(f"{self._reverse_location.latitude:.4f}°, {self._reverse_location.longitude:.4f}°")
            self._select_reverse_btn.setEnabled(True)
            self._fav_reverse_btn.setEnabled(True)
        else:
            self._reverse_name.setText("No location found")
            self._reverse_coords.setText("—")
            self._select_reverse_btn.setEnabled(False)
            self._fav_reverse_btn.setEnabled(False)
    
    def _select_reverse(self):
        """Emit the reverse geocoded location."""
        if self._reverse_location:
            self.location_selected.emit(self._reverse_location)
            self.accept()
    
    def _add_reverse_to_favorites(self):
        """Add reverse geocoded location to favorites."""
        if not self._reverse_location:
            return
        
        fav = DefaultLocation(
            name=self._reverse_location.label,
            latitude=self._reverse_location.latitude,
            longitude=self._reverse_location.longitude,
            elevation=self._reverse_location.elevation or 0,
            timezone_offset=0,
            timezone_id=getattr(self._reverse_location, 'timezone_id', None),
        )
        
        if hasattr(self._preferences, 'add_favorite'):
            self._preferences.add_favorite(fav)
            self._load_favorites()
            QMessageBox.information(self, "Saved", f"'{fav.name}' added to favorites.")
    
    # ─────────────────────────────────────────────────────────────────────────
    # Default Location Logic
    # ─────────────────────────────────────────────────────────────────────────
    
    def _use_default(self):
        """Use the saved default location."""
        if self._default_location:
            self.location_selected.emit(self._default_location)
            self.accept()
    
    def _save_as_default(self):
        """Save currently selected location as default."""
        # Try to get from search results first
        item = self._results_list.currentItem()
        if item:
            result = item.data(Qt.ItemDataRole.UserRole)
            if result:
                default = DefaultLocation(
                    name=result.label,
                    latitude=result.latitude,
                    longitude=result.longitude,
                    elevation=result.elevation or 0,
                    timezone_offset=0,
                    timezone_id=result.timezone_id,
                )
                try:
                    self._preferences.save_default_location(default)
                    self._default_location = default
                    self._default_label.setText(
                        f"{default.name} ({default.latitude:.2f}°, {default.longitude:.2f}°)"
                    )
                    self._use_default_btn.setEnabled(True)
                    QMessageBox.information(self, "Saved", f"'{default.name}' is now your default location.")
                except OSError as exc:
                    QMessageBox.critical(self, "Save Failed", str(exc))
                return
        
        QMessageBox.information(self, "No Selection", "Select a location first.")
