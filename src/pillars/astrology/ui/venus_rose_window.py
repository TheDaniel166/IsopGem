
"""
Cytherean Rose Clock
A generative visualization of the Pentagram of Venus (13:8 Earth-Venus resonance).
"""
from __future__ import annotations

import math
import logging
from typing import List
from datetime import datetime, timedelta, timezone

from pillars.astrology.utils.conversions import to_zodiacal_string
from shared.services.ephemeris_provider import EphemerisProvider
from pillars.astrology.services.venus_position_store import VenusPositionStore

from PyQt6.QtCore import Qt, QTimer, QPointF, QThread, pyqtSignal, QObject
from PyQt6.QtGui import (
    QBrush, 
    QColor, 
    QPainter, 
    QPen, 
    QWheelEvent,
    QRadialGradient,
)
from PyQt6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsTextItem,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMenu,
    QApplication,
)

# Constants
ORBIT_EARTH_R = 300
ORBIT_VENUS_R = 217
PLANET_SIZE = 12
SUN_SIZE = 40
ZODIAC_R = 350 # Radius for zodiac labels

# J2000.0 Epoch: 2000-01-01 12:00 UTC
J2000 = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
# Mean Longitudes at J2000 (Degrees)
L_EARTH_J2000 = 100.46
L_VENUS_J2000 = 181.98

# Orbital Periods (Days)
P_EARTH = 365.256
P_VENUS = 224.701
SYNODIC_PERIOD = 1.0 / (1.0/P_VENUS - 1.0/P_EARTH) # ~583.92 days

# Colors
COLOR_SPACE = QColor("#101015")
COLOR_SUN = QColor("#FFD700")
COLOR_EARTH = QColor("#4169E1")
COLOR_VENUS = QColor("#FFA500")
COLOR_TRACE = QColor(255, 255, 255, 30)
COLOR_ZODIAC = QColor("#555555")
COLOR_GLOW_INF = QColor(255, 200, 255, 200) # Pinkish white
COLOR_GLOW_SUP = QColor(100, 200, 255, 150) # Blueish

logger = logging.getLogger(__name__)

class PlanetItem(QGraphicsEllipseItem):
    """Visual representation of a planet."""
    def __init__(self, color: QColor, size: float, label: str):
        """
          init   logic.
        
        Args:
            color: Description of color.
            size: Description of size.
            label: Description of label.
        
        """
        super().__init__(-size/2, -size/2, size, size)
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.GlobalColor.white))
        self.setToolTip(label)
        self.setZValue(10) # Draw on top

class GlowingParticle(QGraphicsEllipseItem):
    """A glowing highlight for conjunction points."""
    def __init__(self, x, y, is_inferior=True, event_data=None):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        size = 20 if is_inferior else 15
        super().__init__(-size/2, -size/2, size, size)
        self.setPos(x, y)
        self.setZValue(8)
        
        color = COLOR_GLOW_INF if is_inferior else COLOR_GLOW_SUP
        grad = QRadialGradient(0, 0, size/2)
        grad.setColorAt(0.0, color)
        grad.setColorAt(1.0, Qt.GlobalColor.transparent)
        self.setBrush(QBrush(grad))
        self.setPen(QPen(Qt.GlobalColor.transparent))
        
        # Gnostic Inspector: Tooltip
        if event_data:
            dt, evt_type, helio, geo = event_data  # type: ignore[reportUnknownVariableType]
            # Format tooltip with HTML
            # Check context to see which sign to show? Or show both?
            # User has a toggle. But particle persistence means it might have been created
            # when mode was different. Let's just show what we have.
            # actually, passed event_data is (dt, type, helio, geo)
            
            tooltip = (
                f"<div style='background-color: #101015; color: #E0E0E0; padding: 4px;'>"
                f"<b>{evt_type}</b><br/>"
                f"Date: {dt.strftime('%Y-%m-%d')}<br/>"
                f"Helio: {helio}<br/>"
                f"Geo: {geo}"
                f"</div>"
            )
            self.setToolTip(tooltip)
        self.setAcceptHoverEvents(True)

class RoseScene(QGraphicsScene):
    """
    Rose Scene class definition.
    
    Attributes:
        sun: Description of sun.
        earth: Description of earth.
        venus: Description of venus.
        trace_lines: Description of trace_lines.
        highlights: Description of highlights.
        use_real_physics: Description of use_real_physics.
    
    """
    def __init__(self):
        """
          init   logic.
        
        """
        super().__init__()
        self.setBackgroundBrush(QBrush(COLOR_SPACE))
        
        # Sun
        self.sun = QGraphicsEllipseItem(-SUN_SIZE/2, -SUN_SIZE/2, SUN_SIZE, SUN_SIZE)
        self.sun.setBrush(QBrush(COLOR_SUN))
        self.sun.setPen(QPen(Qt.GlobalColor.transparent))
        self.sun.setZValue(5)
        self.addItem(self.sun)
        
        # Zodiac Ring
        self._build_zodiac()
        
        # Planets
        self.earth = PlanetItem(COLOR_EARTH, PLANET_SIZE, "Earth")
        self.venus = PlanetItem(COLOR_VENUS, PLANET_SIZE, "Venus")
        self.addItem(self.earth)
        self.addItem(self.venus)
        
        # Trace Lines Container
        self.trace_lines: List[QGraphicsLineItem] = []
        
        # Highlights
        self.highlights: List[GlowingParticle] = []
        
        # Orbit rings
        self.addEllipse(-ORBIT_EARTH_R, -ORBIT_EARTH_R, ORBIT_EARTH_R*2, ORBIT_EARTH_R*2, QPen(QColor(50, 50, 50)))
        self.addEllipse(-ORBIT_VENUS_R, -ORBIT_VENUS_R, ORBIT_VENUS_R*2, ORBIT_VENUS_R*2, QPen(QColor(50, 50, 50)))
        
        self.use_real_physics = False

        self._venus_store = VenusPositionStore()

    def _build_zodiac(self):
        signs = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqr", "Pis"]
        for i, sign in enumerate(signs):
            angle_deg = (i * 30)
            rad = math.radians(angle_deg)
            line = QGraphicsLineItem(
                (ORBIT_EARTH_R+20)*math.cos(rad), (ORBIT_EARTH_R+20)*math.sin(rad),
                (ORBIT_EARTH_R+40)*math.cos(rad), (ORBIT_EARTH_R+40)*math.sin(rad)
            )
            line.setPen(QPen(COLOR_ZODIAC))
            self.addItem(line)
            
            mid = math.radians(angle_deg + 15)
            text = QGraphicsTextItem(sign)
            text.setDefaultTextColor(COLOR_ZODIAC)
            text.setPos(ZODIAC_R*math.cos(mid)-15, ZODIAC_R*math.sin(mid)-10)
            self.addItem(text)

    def update_positions_by_date(self, dt: datetime, use_real_physics: bool):
        """
        Updates planet positions based on actual datetime using J2000 epoch.
        """
        if use_real_physics:
            # True sky: use heliocentric ephemeris positions (elliptical orbits)
            # Prefer cached DB (30-min cadence); fallback to live ephemeris if DB not built.
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)

            earth_pos = self._venus_store.get_heliocentric_position(dt, "earth")
            venus_pos = self._venus_store.get_heliocentric_position(dt, "venus")

            if earth_pos is None or venus_pos is None:
                provider = EphemerisProvider.get_instance()
                if provider.is_loaded():
                    try:
                        e_lat, e_lon, e_dist = provider.get_heliocentric_ecliptic_latlon_distance('earth', dt)
                        v_lat, v_lon, v_dist = provider.get_heliocentric_ecliptic_latlon_distance('venus', dt)

                        earth_pos = type('Tmp', (), {'lat_deg': e_lat, 'lon_deg': e_lon, 'distance_au': e_dist})
                        venus_pos = type('Tmp', (), {'lat_deg': v_lat, 'lon_deg': v_lon, 'distance_au': v_dist})
                    except Exception as e:
                        logger.warning("Venus Rose ephemeris fallback failed: %s", e)

            if earth_pos is not None and venus_pos is not None:
                # Scale AU to pixels: 1 AU -> ORBIT_EARTH_R
                scale = ORBIT_EARTH_R

                e_lon_r = math.radians(earth_pos.lon_deg)  # type: ignore[reportAttributeAccessIssue, reportUnknownArgumentType, reportUnknownMemberType]
                e_lat_r = math.radians(earth_pos.lat_deg)  # type: ignore[reportAttributeAccessIssue, reportUnknownArgumentType, reportUnknownMemberType]
                e_r = earth_pos.distance_au * scale  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]
                ex = e_r * math.cos(e_lon_r) * math.cos(e_lat_r)
                ey = e_r * math.sin(e_lon_r) * math.cos(e_lat_r)
                self.earth.setPos(ex, ey)

                v_lon_r = math.radians(venus_pos.lon_deg)  # type: ignore[reportAttributeAccessIssue, reportUnknownArgumentType, reportUnknownMemberType]
                v_lat_r = math.radians(venus_pos.lat_deg)  # type: ignore[reportAttributeAccessIssue, reportUnknownArgumentType, reportUnknownMemberType]
                v_r = venus_pos.distance_au * scale  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]
                vx = v_r * math.cos(v_lon_r) * math.cos(v_lat_r)
                vy = v_r * math.sin(v_lon_r) * math.cos(v_lat_r)
                self.venus.setPos(vx, vy)
            else:
                # If cache and ephemeris both unavailable, fall back to the ideal model.
                use_real_physics = False

        if not use_real_physics:
            delta = dt - J2000
            days = delta.total_seconds() / 86400.0

            # Calculate Mean Anomaly/Longitude (Simplified circular model)
            # Earth
            deg_per_day_e = 360.0 / P_EARTH
            mean_long_e = (L_EARTH_J2000 + days * deg_per_day_e) % 360.0
            rad_e = math.radians(mean_long_e)

            # Venus
            # Locked 13:8 resonance
            deg_per_day_v = (13.0 * 360.0) / (8.0 * P_EARTH)
            mean_long_v = (L_VENUS_J2000 + days * deg_per_day_v) % 360.0
            rad_v = math.radians(mean_long_v)

            # Plot positions
            ex = ORBIT_EARTH_R * math.cos(rad_e)
            ey = ORBIT_EARTH_R * math.sin(rad_e)
            self.earth.setPos(ex, ey)

            vx = ORBIT_VENUS_R * math.cos(rad_v)
            vy = ORBIT_VENUS_R * math.sin(rad_v)
            self.venus.setPos(vx, vy)
        
        # Trace
        line = QGraphicsLineItem(ex, ey, vx, vy)  # type: ignore[reportPossiblyUnboundVariable, reportUnknownArgumentType]
        line.setPen(QPen(COLOR_TRACE, 1))
        self.addItem(line)
        self.trace_lines.append(line)
        
        limit = 5000 if use_real_physics else 2500
        while len(self.trace_lines) > limit:
            self.removeItem(self.trace_lines.pop(0))

    def add_highlight(self, event_data):
        # Place highlight at current Venus position
        # event_data is (dt, type, helio, geo)
        evt_type = event_data[1]
        is_inferior = "Inf" in evt_type
        
        h = GlowingParticle(self.venus.x(), self.venus.y(), is_inferior, event_data)
        self.addItem(h)
        self.highlights.append(h)
        if len(self.highlights) > 20: # Keep last 20
            self.removeItem(self.highlights.pop(0))
            
    def clear_trace(self):
        """
        Clear trace logic.
        
        """
        for line in self.trace_lines:
            self.removeItem(line)
        self.trace_lines.clear()
        for h in self.highlights:
            self.removeItem(h)
        self.highlights.clear()


class ConjunctionWorker(QObject):
    """
    Worker for calculating future conjunction events in a background thread.
    prevents UI freeze during heavy Ephemeris calculations.
    """
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def calculate(self, start_date: datetime, is_real_physics: bool):
        try:
            events = self._calculate_future_events(start_date, is_real_physics)
            self.finished.emit(events)
        except Exception as e:
            self.error.emit(str(e))

    def _calculate_future_events(self, start_date, is_real_physics):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        # Approximate next events
        deg_per_day_e = 360.0 / P_EARTH
        
        # Determine Venus speed based on current physics mode
        if is_real_physics:
            deg_per_day_v = 360.0 / P_VENUS
        else:
            deg_per_day_v = (13.0 * 360.0) / (8.0 * P_EARTH)
            
        rel_v = deg_per_day_v - deg_per_day_e # deg/day gain
        
        # Current Longitudes
        delta = start_date - J2000
        days = delta.total_seconds() / 86400.0
        curr_e = (L_EARTH_J2000 + days * deg_per_day_e) % 360
        curr_v = (L_VENUS_J2000 + days * deg_per_day_v) % 360
        
        diff = (curr_v - curr_e) % 360
        # Time to Inferior (0 deg diff) -> Need to gain (360 - diff)
        days_to_inf = (360 - diff) / rel_v
        
        # Time to Superior (180 deg diff) -> Need to gain (180 - diff) % 360
        days_to_sup = ((180 - diff) % 360) / rel_v
        
        synodic_period = 360.0 / rel_v
        
        t_inf = start_date + timedelta(days=days_to_inf)
        t_sup = start_date + timedelta(days=days_to_sup)
        
        raw_events = []
        for i in range(20): # Next 20 events
            # Inferior
            d_inf = t_inf + timedelta(days=i * synodic_period)
            raw_events.append((d_inf, "Petal Point (Inf)"))
            # Superior
            d_sup = t_sup + timedelta(days=i * synodic_period)
            raw_events.append((d_sup, "Outer Point (Sup)"))
            
        raw_events.sort(key=lambda x: x[0])  # type: ignore[reportUnknownLambdaType, reportUnknownMemberType]
        
        final_events = []
        for dt, evt_type in raw_events:
            helio_sign = "--"
            geo_sign = "--"
            
            if is_real_physics:
                # Real Physics: Refine Date to True Conjunction
                is_sup = "Sup" in evt_type
                try:
                    dt = self._refine_conjunction_date(dt, is_superior=is_sup)
                    
                    # Calculate Zodiac Signs HERE in background
                    # Need to convert datetime to UTC for EphemerisProvider
                    t_calc = dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
                    provider = EphemerisProvider.get_instance()
                    
                    # Heliocentric
                    v_lon_h = provider.get_heliocentric_ecliptic_position('venus', t_calc)
                    helio_sign = to_zodiacal_string(v_lon_h)
                    
                    # Geocentric
                    v_lon_g = provider.get_geocentric_ecliptic_position('venus', t_calc)
                    geo_sign = to_zodiacal_string(v_lon_g)
                    
                except Exception as e:
                    logger.warning("Venus Rose refinement error: %s", e)
                    helio_sign = "Error"
                    geo_sign = "Error"
            else:
                # Ideal Math
                deg_per_day_v = (13.0 * 360.0) / (8.0 * P_EARTH)
                d_delta = dt - J2000
                d_days = d_delta.total_seconds() / 86400.0
                mean_long_v = (L_VENUS_J2000 + d_days * deg_per_day_v) % 360.0
                helio_sign = to_zodiacal_string(mean_long_v)
                
                # For Ideal Geocentric:
                # Conjunction means Earth and Venus are aligned.
                # Inferior: Sun -> Venus -> Earth. Geo Longitude = Helio Longitude + 180 ?
                # No, Inferior: Venus is between Earth and Sun.
                # Earth is at L_Earth. Sun is at L_Earth + 180.
                # Venus is at L_Venus = L_Earth.
                # So Geo Longitude (Earth->Venus) is same as Earth->Sun? No.
                # Earth->Sun is L_Sun.
                # Earth->Venus is L_Sun (cuz Venus is in front of Sun).
                # So Geo Long of Venus = Geo Long of Sun.
                
                # Superior: Sun -> Earth -> Venus? No. Earth -> Sun -> Venus.
                # Geo Long of Venus = Geo Long of Sun.
                
                # Wait, simply put: At conjunction, Geo Longitude of Venus ~= Geo Longitude of Sun.
                # Geo Lon Sun = Helio Lon Earth + 180.
                
                # Let's calculate Mean Earth
                deg_per_day_e = 360.0 / P_EARTH
                mean_long_e = (L_EARTH_J2000 + d_days * deg_per_day_e) % 360.0
                geo_sun_lon = (mean_long_e + 180.0) % 360.0
                geo_sign = to_zodiacal_string(geo_sun_lon)

            final_events.append((dt, evt_type, helio_sign, geo_sign))
            
        return final_events

    def _refine_conjunction_date(self, approx_dt: datetime, is_superior: bool = False) -> datetime:
        """
        Refine the date to find the exact moment of Heliocentric Conjunction.
        """
        if approx_dt.tzinfo is None:
            approx_dt = approx_dt.replace(tzinfo=timezone.utc)
            
        provider = EphemerisProvider.get_instance()
        if not provider.is_loaded():
             return approx_dt
        
        def get_diff(t):
            v_lon = provider.get_heliocentric_ecliptic_position('venus', t)
            e_lon = provider.get_heliocentric_ecliptic_position('earth', t)
            
            diff = abs(v_lon - e_lon)
            if diff > 180: diff = 360 - diff
            
            if is_superior:
                # Target is 180 diff
                return abs(diff - 180)
            else:
                # Target is 0 diff
                return diff

        # Coarse Search: +/- 5 days, 4 hour steps
        best_dt = approx_dt
        min_err = 999.0
        
        start_t = approx_dt - timedelta(days=5)
        for i in range(60): # 10 days * 6 steps/day = 60
            t = start_t + timedelta(hours=i*4)
            err = get_diff(t)
            if err < min_err:
                min_err = err
                best_dt = t
                
        # Fine Search: +/- 6 hours, 10 min steps
        start_t = best_dt - timedelta(hours=6)
        for i in range(72): # 12 hours * 6 steps/hour = 72
            t = start_t + timedelta(minutes=i*10)
            err = get_diff(t)
            if err < min_err:
                min_err = err
                best_dt = t
                
        # Ultra-Fine Search: +/- 20 mins, 1 min steps
        start_t = best_dt - timedelta(minutes=20)
        for i in range(40):
            t = start_t + timedelta(minutes=i)
            err = get_diff(t)
            if err < min_err:
                min_err = err
                best_dt = t
                
        return best_dt


class RoseView(QGraphicsView):
    """
    Rose View class definition with Chrono-Scrubbing.
    """
    time_scrubbed = pyqtSignal(float) # days to add/subtract

    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        # We handle dragging manually for scrubbing
        self.setDragMode(QGraphicsView.DragMode.NoDrag) 
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.scale(0.8, 0.8)
        
        self._last_mouse_pos = None
        self._is_scrubbing = False

    def wheelEvent(self, event: QWheelEvent):
        factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_scrubbing = True
            self._last_mouse_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_scrubbing and self._last_mouse_pos:
            delta_x = event.pos().x() - self._last_mouse_pos.x()
            # Sensitivity: 1 pixel = 1 day?
            days_delta = delta_x * 2.0 
            self.time_scrubbed.emit(days_delta)
            
            self._last_mouse_pos = event.pos()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_scrubbing = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)


class VenusRoseWindow(QMainWindow):
    """
    Venus Rose Window class definition.
    
    Attributes:
        current_date: Description of current_date.
        is_real_physics: Description of is_real_physics.
        scene: Description of scene.
        view: Description of view.
        label_date: Description of label_date.
        btn_physics: Description of btn_physics.
        timer: Description of timer.
        table: Description of table.
        events: Description of events.
        step_days: Description of step_days.
        
    Signals:
        request_calculation(datetime, bool): Signal to request background calculation.
    """
    request_calculation = pyqtSignal(datetime, bool)

    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setWindowTitle("The Cytherean Rose")
        self.resize(1200, 900)
        
        # Start at NOW
        self.current_date = datetime.now(timezone.utc)
        self.is_real_physics = False
        self.is_geocentric = True # Default to Geocentric (Standard Astrology)
        
        
        self.scene = RoseScene()
        self.view = RoseView(self.scene)
        self.view.time_scrubbed.connect(self._on_scrub)
        
        # Threading Setup
        self._thread = QThread()
        self._worker = ConjunctionWorker()
        self._worker.moveToThread(self._thread)
        
        # Connections
        self.request_calculation.connect(self._worker.calculate)
        self._worker.finished.connect(self._on_calculation_finished)
        self._worker.error.connect(self._on_calculation_error)
        
        self._thread.start()
        
        # Layouts
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central) # Changed to HBox
        
        # Left: View
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.view)
        
        # Controls (Bottom Left)
        ctrl_layout = QHBoxLayout()
        
        # Add Date Label
        self.label_date = QLabel(f"Date: {self.current_date.strftime('%Y-%m-%d')}")
        self.label_date.setStyleSheet("font-size: 14px; font-weight: bold;")
        ctrl_layout.addWidget(self.label_date) # Add to layout
        
        self.btn_physics = QPushButton("Physics: Ideal")
        self.btn_physics.setCheckable(True)
        self.btn_physics.setProperty("archetype", "seeker")
        self.btn_physics.clicked.connect(self._toggle_physics)
        ctrl_layout.addWidget(self.btn_physics)

        self.btn_coords = QPushButton("View: Geocentric")
        self.btn_coords.setProperty("archetype", "seeker")
        self.btn_coords.clicked.connect(self._toggle_coords)
        ctrl_layout.addWidget(self.btn_coords)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self._animate)
        
        btn_play = QPushButton("Weave")
        btn_play.setProperty("archetype", "magus")
        btn_play.clicked.connect(self._start_animation)
        ctrl_layout.addWidget(btn_play)
        
        btn_turbo = QPushButton("Century Turbo")
        btn_turbo.setProperty("archetype", "magus")
        btn_turbo.clicked.connect(self._start_turbo)
        ctrl_layout.addWidget(btn_turbo)
        
        btn_stop = QPushButton("Pause")
        btn_stop.setProperty("archetype", "navigator")
        btn_stop.clicked.connect(self.timer.stop)
        ctrl_layout.addWidget(btn_stop)
        
        btn_reset = QPushButton("Reset")
        btn_reset.setProperty("archetype", "destroyer")
        btn_reset.clicked.connect(self._reset)
        ctrl_layout.addWidget(btn_reset)
        
        left_layout.addLayout(ctrl_layout)
        main_layout.addLayout(left_layout, stretch=2)
        
        # Right: Data Pane
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Date", "Type", "Helio Sign"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        main_layout.addWidget(self.table, stretch=1)
        
        self.events = []
        self._calculate_future_events()
        
        self.step_days = 2.0 # Days per tick

    def _calculate_future_events(self):
        """Predict next conjunctions (Async)."""
        self.table.setRowCount(0)
        # Show loading state
        self.table.setRowCount(1)
        self.table.setItem(0, 0, QTableWidgetItem("Calculating..."))
        self.table.setItem(0, 1, QTableWidgetItem("Please wait"))
        
        # Emit signal to worker
        self.request_calculation.emit(self.current_date, self.is_real_physics)

    def _on_calculation_error(self, err_msg):
        logger.error("Venus Rose calculation error: %s", err_msg)
        self.table.setRowCount(0)

    def _on_calculation_finished(self, events):
        """Handle results from worker."""
        # Store full events: (dt, type, helio, geo)
        self.events = events
        self._update_table_display()

    def _update_table_display(self):
        """Update table based on current events and view settings."""
        if not self.events:
            self.table.setRowCount(0)
            return

        self.table.setRowCount(len(self.events))
        
        # Update Header
        sign_header = "Geo Sign" if self.is_geocentric else "Helio Sign"
        self.table.setHorizontalHeaderLabels(["Date", "Type", sign_header])
        
        # Populate table
        for i, (dt, evt_type, helio_sign, geo_sign) in enumerate(self.events):  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportUnknownVariableType]
             self.table.setItem(i, 0, QTableWidgetItem(dt.strftime("%Y-%m-%d %H:%M")))
             self.table.setItem(i, 1, QTableWidgetItem(evt_type))
             
             sign_str = geo_sign if self.is_geocentric else helio_sign
             self.table.setItem(i, 2, QTableWidgetItem(sign_str))

    def _show_context_menu(self, pos: QPointF):
        index = self.table.indexAt(pos)
        if not index.isValid():
            return
            
        menu = QMenu(self)
        
        # Action: Copy Line
        action_copy = menu.addAction("Copy Line")
        action_copy.triggered.connect(lambda: self._copy_line(index.row()))
        
        # Action: Cast Chart
        action_cast = menu.addAction("Cast Chart")
        action_cast.triggered.connect(lambda: self._cast_chart(index.row()))
        
        menu.exec(self.table.viewport().mapToGlobal(pos))
        
    def _copy_line(self, row_idx: int):
        cols = self.table.columnCount()
        data = []
        for c in range(cols):
            item = self.table.item(row_idx, c)
            text = item.text() if item else ""
            data.append(text)
        
        line_str = " | ".join(data)
        QApplication.clipboard().setText(line_str)
        
    def _cast_chart(self, row_idx: int):
        # Format: YYYY-MM-DD
        date_item = self.table.item(row_idx, 0)
        if not date_item:
            return
            
        date_str = date_item.text()
        try:
            # Parse date. Defaulting to 12:00 UTC roughly, though we tracked exact times internally
            # Better to retrieve from self.events list if possible
            # self.events stores [(datetime, type), ...]
            
            # Find the event matching this row
            if row_idx < len(self.events):
                evt_dt = self.events[row_idx][0]
                
                # Import here to avoid circular dependency at top level
                from pillars.astrology.ui.natal_chart_window import NatalChartWindow
                
                # We need to instantiate and show the window
                # Assuming simple instantiation works
                self._chart_window = NatalChartWindow()
                
                # Set the date
                # NatalChartWindow -> self.datetime_input (QDateTimeEdit)
                from PyQt6.QtCore import QDateTime, QTimeZone
                qdt = QDateTime(evt_dt)
                if evt_dt.tzinfo:
                    qdt.setTimeZone(QTimeZone.utc())
                
                self._chart_window.datetime_input.setDateTime(qdt)
                self._chart_window.name_input.setText(f"Venus Trans: {date_str}")
                
                self._chart_window.show()
                
        except Exception as e:
            logger.error("Error casting chart from Venus Rose: %s", e)

    def closeEvent(self, event):  # type: ignore[reportIncompatibleMethodOverride, reportMissingParameterType, reportUnknownParameterType]
        """Clean up thread on close."""
        self._thread.quit()
        self._thread.wait()
        super().closeEvent(event)

    def _toggle_physics(self):
        self.is_real_physics = self.btn_physics.isChecked()
        self.btn_physics.setText("Physics: REAL" if self.is_real_physics else "Physics: Ideal")
        self._reset()

    def _toggle_coords(self):
        self.is_geocentric = not self.is_geocentric
        self.btn_coords.setText("View: Geocentric" if self.is_geocentric else "View: Heliocentric")
        self._update_table_display()

    def _start_animation(self):
        self.step_days = 2.0
        self.timer.start(20)

    def _start_turbo(self):
        self.step_days = 20.0 # Fast forward
        self.timer.start(20)

    def _animate(self):
        self.current_date += timedelta(days=self.step_days)
        self.scene.update_positions_by_date(self.current_date, self.is_real_physics)
        self.label_date.setText(f"Date: {self.current_date.strftime('%Y-%m-%d')}")
        
        # Check Events
        # Basic check: if we passed an event date
        if self.events:
            next_evt = self.events[0]
            # If current date is AFTER next event
            # If current date is AFTER next event
            if self.current_date > next_evt[0]:
                evt = self.events.pop(0)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
                self.scene.add_highlight(evt)
                # Scroll table? logic
                
                # For now just pop visual
                self.table.removeRow(0)
    
    def _on_scrub(self, days_delta):
        """Handle manual time scrubbing."""
        self.current_date += timedelta(days=days_delta)
        self.scene.update_positions_by_date(self.current_date, self.is_real_physics)
        self.label_date.setText(f"Date: {self.current_date.strftime('%Y-%m-%d')}")
        
        # We might miss events if we scrub too fast, or need to pop them
        # simple logic: if we scrub forward past an event, trigger it
        # But scrubbing backwards? That's harder with the current event queue.
        # For now, let's just update the visual positions and date.
        # Re-syncing the event queue would require re-calculating or keeping a full history.
        # Given complexity, let's just accept visual update for position.
        pass

    def _reset(self):
        self.timer.stop()
        self.current_date = datetime.now(timezone.utc)
        self.scene.clear_trace()
        self.scene.update_positions_by_date(self.current_date, self.is_real_physics)
        self.label_date.setText(f"Date: {self.current_date.strftime('%Y-%m-%d')}")
        self._calculate_future_events()