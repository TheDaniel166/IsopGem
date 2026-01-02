"""
Neo-Aubrey Window - The Eclipse Clock Simulator.
Interactive Stonehenge-inspired dual-ring visualizer for eclipse prediction using DE441 ephemeris.
"""
from ..services.location_lookup import LocationLookupService, LocationLookupError, LocationResult
from ..utils.conversions import to_zodiacal_string

import math
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from PyQt6.QtWidgets import (
    QGraphicsScene, QGraphicsEllipseItem, QGraphicsItem, QGraphicsLineItem, 
    QGraphicsTextItem, QGraphicsView, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QPushButton, QSlider, QLineEdit, QFormLayout, 
    QInputDialog, QMessageBox, QApplication, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import (
    QBrush, QColor, QFont, QPainter, QPainterPath, QPen, QWheelEvent, QPolygonF
)

# Constants
SAROS_HOLES = 223
AUBREY_HOLES = 56
SYNODIC_MONTH = 29.53059  # Days
SAROS_RADIUS = 400
AUBREY_RADIUS = 250
STONE_RADIUS = 8

# Markers colors
COLOR_STONE = QColor("#555555")
COLOR_STONE_HIGHLIGHT = QColor("#AAAAAA")
COLOR_SUN = QColor("#FFD700")  # Gold
COLOR_MOON = QColor("#C0C0C0") # Silver
COLOR_NODE = QColor("#FF69B4") # Pink
COLOR_SAROS_HAND = QColor("#00FFFF") # Cyan

J2000 = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

class StoneItem(QGraphicsEllipseItem):
    """Visual representation of a hole/stone."""
    def __init__(self, x: float, y: float, r: float, index: int, label: str = ""):
        """
          init   logic.
        
        Args:
            x: Description of x.
            y: Description of y.
            r: Description of r.
            index: Description of index.
            label: Description of label.
        
        """
        super().__init__(x - r, y - r, r * 2, r * 2)
        self.setBrush(QBrush(COLOR_STONE))
        self.setPen(QPen(Qt.GlobalColor.black))
        self.index = index
        self.setToolTip(f"{label} #{index + 1}")

class MarkerItem(QGraphicsEllipseItem):
    """Movable marker (Sun, Moon, etc)."""
    def __init__(self, color: QColor, label: str):
        """
          init   logic.
        
        Args:
            color: Description of color.
            label: Description of label.
        
        """
        super().__init__(-10, -10, 20, 20) # 20px size
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.GlobalColor.white, 2))
        self.setZValue(10) # Draw on top
        self.setToolTip(label)
        self._label_item = QGraphicsTextItem(label, self)
        self._label_item.setPos(10, 10)
        self._label_item.setDefaultTextColor(Qt.GlobalColor.white)

class EclipseClockScene(QGraphicsScene):
    """
    Eclipse Clock Scene class definition.
    
    Attributes:
        saros_stones: Description of saros_stones.
        aubrey_stones: Description of aubrey_stones.
        sun_marker: Description of sun_marker.
        moon_marker: Description of moon_marker.
        node_marker: Description of node_marker.
        south_node_marker: Description of south_node_marker.
        saros_hand: Description of saros_hand.
    
    """
    def __init__(self):
        """
          init   logic.
        
        """
        super().__init__()
        self.setBackgroundBrush(QBrush(QColor("#1e1e1e")))
        self.saros_stones: List[StoneItem] = []
        self.aubrey_stones: List[StoneItem] = []
        
        self.sun_marker = MarkerItem(COLOR_SUN, "Sun")
        self.moon_marker = MarkerItem(COLOR_MOON, "Moon")
        self.node_marker = MarkerItem(COLOR_NODE, "Node (North)")
        self.south_node_marker = MarkerItem(COLOR_NODE, "Node (South)")
        # Make South Node slightly different (hollow?)
        self.south_node_marker.setBrush(QBrush(Qt.GlobalColor.transparent))
        
        self.saros_hand = MarkerItem(COLOR_SAROS_HAND, "Saros")
        
        self._build_rings()
        
        self.addItem(self.sun_marker)
        self.addItem(self.moon_marker)
        self.addItem(self.node_marker)
        self.addItem(self.south_node_marker)
        self.addItem(self.saros_hand)
        
        # Center marker
        center = self.addEllipse(-5, -5, 10, 10, QPen(Qt.GlobalColor.gray), QBrush(Qt.GlobalColor.gray))
        center.setZValue(-1)

    def _build_rings(self):
        # Build Saros Ring (Outer)
        for i in range(SAROS_HOLES):
            angle_deg = (i / SAROS_HOLES) * 360.0 - 90 # Start at top (-90)
            rad = math.radians(angle_deg)
            x = SAROS_RADIUS * math.cos(rad)
            y = SAROS_RADIUS * math.sin(rad)
            stone = StoneItem(x, y, STONE_RADIUS, i, "Saros")
            self.addItem(stone)
            self.saros_stones.append(stone)
            
            # Major ticks every ~1 year (approx 12-13 moons)
            if i % 12 == 0:
                tick = QGraphicsLineItem(x * 0.9, y * 0.9, x * 1.1, y * 1.1)
                tick.setPen(QPen(QColor("#444"), 1))
                self.addItem(tick)

        # Build Aubrey Ring (Inner)
        for i in range(AUBREY_HOLES):
            angle_deg = (i / AUBREY_HOLES) * 360.0 - 90
            rad = math.radians(angle_deg)
            x = AUBREY_RADIUS * math.cos(rad)
            y = AUBREY_RADIUS * math.sin(rad)
            stone = StoneItem(x, y, STONE_RADIUS, i, "Aubrey")
            # Highlight cardinal points
            if i % 14 == 0:
                stone.setBrush(QBrush(QColor("#777777")))
            self.addItem(stone)
            self.aubrey_stones.append(stone)

    def set_markers(self, sun_lon: float, moon_lon: float, node_lon: float, saros_idx: float):
        """
        Update marker positions based on Zodiac Longitude (0-360).
        Zodiac Longitude is mapped to the 56-hole Aubrey Circle.
        """
        # Map 0-360 -> 0-56
        sun_pos = (sun_lon / 360.0) * AUBREY_HOLES
        moon_pos = (moon_lon / 360.0) * AUBREY_HOLES
        node_pos = (node_lon / 360.0) * AUBREY_HOLES
        south_node_pos = ((node_lon + 180) % 360 / 360.0) * AUBREY_HOLES

        self._place_marker_on_ring(self.sun_marker, sun_pos, AUBREY_HOLES, AUBREY_RADIUS)
        self._place_marker_on_ring(self.moon_marker, moon_pos, AUBREY_HOLES, AUBREY_RADIUS)
        self._place_marker_on_ring(self.node_marker, node_pos, AUBREY_HOLES, AUBREY_RADIUS)
        self._place_marker_on_ring(self.south_node_marker, south_node_pos, AUBREY_HOLES, AUBREY_RADIUS)
        
        # Saros is separate cycle
        self._place_marker_on_ring(self.saros_hand, saros_idx, SAROS_HOLES, SAROS_RADIUS)
        
        # Return positions for collision detection
        return sun_pos, moon_pos, node_pos, south_node_pos

    def _place_marker_on_ring(self, marker: QGraphicsItem, index: float, total: int, radius: float):
        angle_deg = (index / total) * 360.0 - 90
        rad = math.radians(angle_deg)
        x = radius * math.cos(rad)
        y = radius * math.sin(rad)
        marker.setPos(x, y)


class ZoomableGraphicsView(QGraphicsView):
    """
    Zoomable Graphics View class definition.
    
    """
    def __init__(self, scene):
        """
          init   logic.
        
        Args:
            scene: Description of scene.
        
        """
        super().__init__(scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.scale(0.8, 0.8) # Initial zoom out
        self.setStyleSheet("border: none;")

    def wheelEvent(self, event: QWheelEvent):
        """
        Wheelevent logic.
        
        Args:
            event: Description of event.
        
        """
        zoom_in = event.angleDelta().y() > 0
        factor = 1.1 if zoom_in else 0.9
        self.scale(factor, factor)


from PyQt6.QtWidgets import (
    QGraphicsScene, QGraphicsEllipseItem, QGraphicsItem, QGraphicsLineItem, 
    QGraphicsTextItem, QGraphicsView, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QPushButton, QSlider, QLineEdit, QFormLayout
)

# ... (Previous imports and classes unchanged) ...

class NeoAubreyWindow(QMainWindow):
    """
    Neo Aubrey Window class definition.
    
    Attributes:
        ephemeris: Description of ephemeris.
        location_lookup: Description of location_lookup.
        current_time: Description of current_time.
        is_playing: Description of is_playing.
        days_per_tick: Description of days_per_tick.
        timer: Description of timer.
    
    """
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setWindowTitle("Neo-Aubrey Eclipse Clock (DE441 Engine)")
        self.resize(1200, 850)
        
        # Services
        from shared.services.ephemeris_provider import EphemerisProvider
        self.ephemeris = EphemerisProvider.get_instance()
        self.location_lookup = LocationLookupService()
        self.current_time = datetime.now(timezone.utc)
        
        # State
        self.is_playing = False
        self.days_per_tick = 1
        
        self._setup_ui()
        
        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._animate)
        
        # Initial Draw inside delayed timer to let engine load
        QTimer.singleShot(500, self._update_clock)

    def _setup_ui(self):
        # Main Layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # Left: Visualizer
        self.scene = EclipseClockScene()
        self.view = ZoomableGraphicsView(self.scene)
        layout.addWidget(self.view, stretch=3)
        
        # Right: Control & Log Panel
        panel = QWidget()
        panel.setFixedWidth(300)
        panel.setStyleSheet("background-color: #2b2b2b; color: #eee; border-left: 1px solid #444;")
        panel_layout = QVBoxLayout(panel)
        
        # Title
        lbl_title = QLabel("CHRONICLE")
        lbl_title.setStyleSheet("font-weight: bold; font-size: 14pt; color: #FFD700; margin-bottom: 10px;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(lbl_title)
        
        # Date Display
        self.date_label = QLabel()
        self.date_label.setStyleSheet("font-size: 12pt; font-family: monospace; color: #fff;")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(self.date_label)
        
        # Location Controls
        loc_group = QWidget()
        loc_layout = QFormLayout(loc_group)
        
        # Search Button
        search_btn = QPushButton("Search Location...")
        search_btn.clicked.connect(self._search_location)
        loc_layout.addRow(search_btn)
        
        self.lat_input = QLineEdit("51.48")
        self.lat_input.setPlaceholderText("Latitude")
        self.lat_input.setStyleSheet("background-color: #444; color: #fff; padding: 5px;")
        
        self.lon_input = QLineEdit("0.0")
        self.lon_input.setPlaceholderText("Longitude")
        self.lon_input.setStyleSheet("background-color: #444; color: #fff; padding: 5px;")
        
        loc_layout.addRow("Lat:", self.lat_input)
        loc_layout.addRow("Lon:", self.lon_input)
        panel_layout.addWidget(loc_group)
        
        # Status
        self.status_label = QLabel("Status: Normal")
        self.status_label.setStyleSheet("font-size: 10pt; color: #aaa; margin-bottom: 15px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        panel_layout.addWidget(self.status_label)
        
        # Controls Group
        grid = QVBoxLayout()
        btn_now = QPushButton("Reset to Now")
        btn_now.clicked.connect(self._reset_now)
        grid.addWidget(btn_now)
        
        btn_play = QPushButton("Play (1 day/tick)")
        btn_play.clicked.connect(lambda: self._start_animation(1))
        grid.addWidget(btn_play)
        
        btn_scan = QPushButton("Scan for Eclipses (Fast)")
        btn_scan.clicked.connect(lambda: self._start_animation(5))
        grid.addWidget(btn_scan)
        
        btn_stop = QPushButton("Stop")
        btn_stop.clicked.connect(self._stop_animation)
        grid.addWidget(btn_stop)
        
        # Step Controls
        step_grid = QHBoxLayout()
        btn_step_day = QPushButton("+1 Day")
        btn_step_day.clicked.connect(lambda: self._step_time(1))
        
        btn_step_month = QPushButton("+Month")
        btn_step_month.setToolTip("Add Synodic Month (29.53 days)")
        btn_step_month.clicked.connect(lambda: self._step_time(SYNODIC_MONTH))
        
        btn_step_year = QPushButton("+Year")
        btn_step_year.clicked.connect(lambda: self._step_time(365.25))
        
        btn_step_saros = QPushButton("+Saros")
        btn_step_saros.setToolTip("Add Saros Cycle (18y 11d)")
        btn_step_saros.clicked.connect(lambda: self._step_time(6585.32))

        step_grid.addWidget(btn_step_day)
        step_grid.addWidget(btn_step_month)
        step_grid.addWidget(btn_step_year)
        step_grid.addWidget(btn_step_saros)
        panel_layout.addLayout(step_grid)
        
        panel_layout.addLayout(grid)
        
        # Log
        panel_layout.addWidget(QLabel("Eclipse Log (Click to Jump):"))
        self.log_list = QListWidget()
        self.log_list.setStyleSheet("background-color: #1a1a1a; border: none; font-family: monospace;")
        self.log_list.itemClicked.connect(self._on_log_item_clicked)
        panel_layout.addWidget(self.log_list)
        
        layout.addWidget(panel)

    def _search_location(self):
        """Standard Location Lookup Pattern."""
        query, accepted = QInputDialog.getText(self, "Search Location", "City Name:")
        if not accepted or not query.strip():
            return

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            results = self.location_lookup.search(query)
        except Exception as e:
            QMessageBox.warning(self, "Lookup Failed", str(e))
            return
        finally:
            QApplication.restoreOverrideCursor()

        # Selection Logic
        selection = None
        if len(results) == 1:
            selection = results[0]
        else:
            options = [f"{r.label} ({r.latitude:.2f}, {r.longitude:.2f})" for r in results]
            choice, ok = QInputDialog.getItem(self, "Select Location", "Choose correct city:", options, 0, False)
            if ok and choice:
                selection = results[options.index(choice)]
        
        if selection:
            self.lat_input.setText(str(selection.latitude))
            self.lon_input.setText(str(selection.longitude))
            self.status_label.setText(f"Location set to: {selection.name}")
            self._update_clock()

    def _reset_now(self):
        self._stop_animation()
        self.current_time = datetime.now(timezone.utc)
        self._update_clock()

    def _step_time(self, days: float):
        self._stop_animation()
        self.current_time += timedelta(days=days)
        self._update_clock()

    def _start_animation(self, days_per_tick: int):
        self.days_per_tick = days_per_tick
        self.is_playing = True
        self.timer.start(50) # 20 FPS

    def _stop_animation(self):
        self.is_playing = False
        self.timer.stop()

    def _animate(self):
        self.current_time += timedelta(days=self.days_per_tick)
        self._update_clock()

    def _update_clock(self):
        # 1. Update UI Date
        self.date_label.setText(self.current_time.strftime('%Y-%m-%d'))
        
        # 2. Get Astronomical Data
        try:
            # Check engine load
            if not self.ephemeris.is_loaded():
                self.status_label.setText("Status: Loading Ephemeris (DE441)... Please Wait.")
                # self._update_clock() # Dont recurse rapidly
                QTimer.singleShot(1000, self._update_clock)
                return

            # Note: We simulate Geocentric View (Stonehenge is on Earth)
            # EphemerisProvider expects UTC datetime
            dt = self.current_time
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)

            sun_lon = self.ephemeris.get_geocentric_ecliptic_position("sun", dt)
            moon_lon = self.ephemeris.get_geocentric_ecliptic_position("moon", dt)
            node_lon = self.ephemeris.get_osculating_north_node(dt)
            
            # Saros calculation (approximate day count from J2000 epoch)
            delta = dt - J2000
            days = delta.total_seconds() / 86400.0
            saros_idx = (days / SYNODIC_MONTH) % SAROS_HOLES
            
            # Update Scene
            s_pos, m_pos, n_pos, sn_pos = self.scene.set_markers(sun_lon, moon_lon, node_lon, saros_idx)
            
            # 4. Eclipse Detection
            self._check_eclipse(sun_lon, moon_lon, node_lon, saros_idx)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.status_label.setText(f"Error: {e.__class__.__name__}: {str(e)}")

    def _check_eclipse(self, sun: float, moon: float, node: float, saros_idx: float):
        """
        Detect eclipses based on longitudinal proximity.
        """
        # Normalize Distances
        dist_sun_node = min(abs(sun - node), 360 - abs(sun - node))
        south_node = (node + 180) % 360
        dist_sun_snode = min(abs(sun - south_node), 360 - abs(sun - south_node))
        
        dist_sun_node_min = min(dist_sun_node, dist_sun_snode)
        
        # Check Season
        is_season = dist_sun_node_min < 18
        
        # Check Syzygy (Alignment of Sun-Moon)
        dist_sun_moon = min(abs(sun - moon), 360 - abs(sun - moon))
        is_new_moon = dist_sun_moon < 15 
        is_full_moon = abs(dist_sun_moon - 180) < 15
        
        status_text = "Status: Normal"
        style = "color: #aaa;"
        
        if is_season:
            status_text = "Status: ECLIPSE SEASON (Sun near Node)"
            style = "color: #FFD700; font-weight: bold;"
            
            # Precise check for Event Log
            log_msg = ""
            event_type = ""
            
            # Solar Eclipse Check: New Moon + Near Node
            if is_new_moon and dist_sun_moon < 2: 
                status_text = "*** SOLAR ECLIPSE DETECTED ***"
                style = "color: #FF4500; font-weight: 900; font-size: 12pt;"
                event_type = "SOLAR ECLIPSE"
            
            # Lunar Eclipse Check: Full Moon + Near Node
            elif is_full_moon and abs(dist_sun_moon - 180) < 2:
                status_text = "*** LUNAR ECLIPSE DETECTED ***"
                style = "color: #00FFFF; font-weight: 900; font-size: 12pt;"
                event_type = "LUNAR ECLIPSE"
                
            if event_type:
                # Helper to get Aubrey Stone Index (1-56)
                def get_stone_idx(lon):
                    # Map 0-360 -> 0-56, then +1 for 1-based index
                    """
                    Retrieve stone idx logic.
                    
                    Args:
                        lon: Description of lon.
                    
                    Returns:
                        Result of get_stone_idx operation.
                    """
                    return int((lon / 360.0) * AUBREY_HOLES) + 1
                
                sun_stone = get_stone_idx(sun)
                moon_stone = get_stone_idx(moon)
                node_stone = get_stone_idx(node)
                saros_stone = int(saros_idx) + 1
                
                # Determine which node is involved
                node_name = "N.Node" if dist_sun_node < dist_sun_snode else "S.Node"
                node_val = node if node_name == "N.Node" else south_node
                node_stone_val = get_stone_idx(node_val)
                
                # Construct Detailed Log
                # Check duplicate by date
                date_str = self.current_time.strftime('%Y-%m-%d')
                
                # Simple duplicate check - if last item has same date
                if self.log_list.count() > 0:
                    last_item = self.log_list.item(0)
                    if date_str in last_item.text():
                        return

                log_msg = (
                    f"[{date_str}] {event_type}\n"
                    f"  Sun:    Stone #{sun_stone} ({to_zodiacal_string(sun)})\n"
                    f"  Moon:   Stone #{moon_stone} ({to_zodiacal_string(moon)})\n"
                    f"  {node_name}: Stone #{node_stone_val} ({to_zodiacal_string(node_val)})\n"
                    f"  Saros:  Stone #{saros_stone}\n"
                    f"{'-'*30}"
                )
                
                item = QListWidgetItem(log_msg)
                # Store datetime in UserRole for jump-to
                from PyQt6.QtCore import Qt
                item.setData(Qt.ItemDataRole.UserRole, self.current_time)
                self.log_list.insertItem(0, item)
        
        self.status_label.setText(status_text)
        self.status_label.setStyleSheet(style)

    def _on_log_item_clicked(self, item: QListWidgetItem):
        """Restore state to the clicked eclipse event."""
        timestamp = item.data(Qt.ItemDataRole.UserRole)
        if timestamp:
            self._stop_animation()
            self.current_time = timestamp
            self._update_clock()
            self.status_label.setText(f"Jumped to {timestamp.strftime('%Y-%m-%d')}")