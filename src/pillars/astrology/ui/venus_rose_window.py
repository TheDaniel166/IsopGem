
"""
Cytherean Rose Clock
A generative visualization of the Pentagram of Venus (13:8 Earth-Venus resonance).
"""
from __future__ import annotations

import math
from typing import List
from datetime import datetime, timedelta, timezone

from pillars.astrology.utils.conversions import to_zodiacal_string
from pillars.astrology.repositories.ephemeris_provider import EphemerisProvider, EphemerisNotLoadedError

from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import (
    QBrush, 
    QColor, 
    QPainter, 
    QPen, 
    QWheelEvent,
    QRadialGradient,
)
from PyQt6.QtWidgets import (
    QGraphicsItem,
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
    QSlider,
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
    def __init__(self, x, y, is_inferior=True):
        """
          init   logic.
        
        Args:
            x: Description of x.
            y: Description of y.
            is_inferior: Description of is_inferior.
        
        """
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
        delta = dt - J2000
        days = delta.total_seconds() / 86400.0
        
        # Calculate Mean Anomaly/Longitude (Simplified circular model)
        # Earth
        deg_per_day_e = 360.0 / P_EARTH
        mean_long_e = (L_EARTH_J2000 + days * deg_per_day_e) % 360.0
        rad_e = math.radians(mean_long_e)
        
        # Venus
        if use_real_physics:
            deg_per_day_v = 360.0 / P_VENUS
        else:
            # Locked 13:8 resonance
            # Venus completes 13 orbits in 8 * P_EARTH days
            # Rate = (13 * 360) / (8.0 * P_EARTH)
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
        line = QGraphicsLineItem(ex, ey, vx, vy)
        line.setPen(QPen(COLOR_TRACE, 1))
        self.addItem(line)
        self.trace_lines.append(line)
        
        limit = 5000 if use_real_physics else 2500
        while len(self.trace_lines) > limit:
            self.removeItem(self.trace_lines.pop(0))

    def add_highlight(self, is_inferior):
        # Place highlight at current Venus position
        """
        Add highlight logic.
        
        Args:
            is_inferior: Description of is_inferior.
        
        """
        h = GlowingParticle(self.venus.x(), self.venus.y(), is_inferior)
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


class RoseView(QGraphicsView):
    """
    Rose View class definition.
    
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
        self.scale(0.8, 0.8)

    def wheelEvent(self, event: QWheelEvent):
        """
        Wheelevent logic.
        
        Args:
            event: Description of event.
        
        """
        factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        self.scale(factor, factor)


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
    
    """
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
        
        self.scene = RoseScene()
        self.view = RoseView(self.scene)
        
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
        self.btn_physics.clicked.connect(self._toggle_physics)
        ctrl_layout.addWidget(self.btn_physics)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self._animate)
        
        btn_play = QPushButton("Weave")
        btn_play.clicked.connect(self._start_animation)
        ctrl_layout.addWidget(btn_play)
        
        btn_turbo = QPushButton("Century Turbo")
        btn_turbo.clicked.connect(self._start_turbo)
        ctrl_layout.addWidget(btn_turbo)
        
        btn_stop = QPushButton("Pause")
        btn_stop.clicked.connect(self.timer.stop)
        ctrl_layout.addWidget(btn_stop)
        
        btn_reset = QPushButton("Reset")
        btn_reset.clicked.connect(self._reset)
        ctrl_layout.addWidget(btn_reset)
        
        left_layout.addLayout(ctrl_layout)
        main_layout.addLayout(left_layout, stretch=2)
        
        # Right: Data Pane
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Date", "Type", "Helio Sign", "Lat", "Speed", "Elong.", "Motion"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        main_layout.addWidget(self.table, stretch=1)
        
        self.events = []
        self._calculate_future_events()
        
        self.step_days = 2.0 # Days per tick

    def _calculate_future_events(self):
        """Predict next conjunctions."""
        self.events = []
        self.table.setRowCount(0)
        
        # Approximate next events
        start_date = self.current_date
        deg_per_day_e = 360.0 / P_EARTH
        
        # Determine Venus speed based on current physics mode
        if self.is_real_physics:
            deg_per_day_v = 360.0 / P_VENUS
        else:
            deg_per_day_v = (13.0 * 360.0) / (8.0 * P_EARTH)
            
        rel_v = deg_per_day_v - deg_per_day_e # deg/day gain
        
        # Current Longitudes
        # Note: We calculate current positions based on the SAME speed to ensure consistency
        delta = start_date - J2000
        days = delta.total_seconds() / 86400.0
        curr_e = (L_EARTH_J2000 + days * deg_per_day_e) % 360
        curr_v = (L_VENUS_J2000 + days * deg_per_day_v) % 360
        
        diff = (curr_v - curr_e) % 360
        # Time to Inferior (0 deg diff) -> Need to gain (360 - diff)
        days_to_inf = (360 - diff) / rel_v
        
        # Time to Superior (180 deg diff) -> Need to gain (180 - diff) % 360
        # If diff < 180 (e.g. 10), need 170. 
        # If diff > 180 (e.g. 350), need 190.
        days_to_sup = ((180 - diff) % 360) / rel_v
        
        # Generate list
        # We start with the closest ones and step by Synodic Period
        # Calculate Synodic Period dynamically based on rates
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
            
        raw_events.sort(key=lambda x: x[0])
        
        self.events = raw_events
        self.table.setRowCount(len(raw_events))
        for i, (dt, evt_type) in enumerate(raw_events):
            
            # Real Physics: Refine Date to True Conjunction
            if self.is_real_physics:
                # Determine if superior or inferior based on type string or loop index logic
                # 'Petal Point (Inf)' vs 'Outer Point (Sup)'
                is_sup = "Sup" in evt_type
                try:
                    dt = self._refine_conjunction_date(dt, is_superior=is_sup)
                    self.events[i] = (dt, evt_type) 
                except EphemerisNotLoadedError:
                    # Retry in 1 second
                    QTimer.singleShot(1000, self._calculate_future_events)
                    # Mark all as loading and break
                    for r in range(self.table.rowCount()):
                        self.table.setItem(r, 2, QTableWidgetItem("Loading..."))
                    return
                except Exception as e:
                    print(f"Date refinement failed: {e}")

            self.table.setItem(i, 0, QTableWidgetItem(dt.strftime("%Y-%m-%d %H:%M")))
            self.table.setItem(i, 1, QTableWidgetItem(evt_type))
            
            # Calculate Venus Sign at this event
            sign_str = "--"
            lat_str = "--"
            speed_str = "--"
            elong_str = "--"
            motion_str = "--"

            if self.is_real_physics:
                try:
                    provider = EphemerisProvider.get_instance()
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    
                    # HELIOCENTRIC + Extended
                    data = provider.get_extended_data('venus', dt)
                    
                    sign_str = to_zodiacal_string(data['helio_lon'])
                    lat_str = f"{data['helio_lat']:.2f}°"
                    speed_str = f"{data['helio_speed']:.3f}°/d"
                    elong_str = f"{data['elongation']:.1f}°"
                    motion_str = "Rx" if data['is_retrograde'] else "D"
                    
                except EphemerisNotLoadedError:
                     sign_str = "Loading..."
                     # Logic above (in Refine) handles the retry loop, 
                     # but if refinement is skipped (Ideal mode?) we might need it here?
                     # Actually Physics toggle handles mode. 
                     # Refine block returns early if loading.
                     # So logic here is only reached if Refine block succeeded OR skipped.
                     # Wait, Refine block is inside `if self.is_real_physics`.
                     # So if Refine block returns, we exit function.
                     pass 
                except Exception as e:
                    print(f"Error calculating skyfield position: {e}")
                    sign_str = "Error"
            else:
                # Ideal Math (Heliocentric - Simple Circular)
                # This is just the raw angle of Venus around the Sun
                d_delta = dt - J2000
                d_days = d_delta.total_seconds() / 86400.0
                
                mean_long_v = (L_VENUS_J2000 + d_days * deg_per_day_v) % 360.0
                sign_str = to_zodiacal_string(mean_long_v)
                
                # Ideal Speed is constant 360/224.7 = ~1.602
                speed_str = f"{deg_per_day_v:.3f}°/d"
                # Ideal Lat is 0
                lat_str = "0.00°"
                # Ideal Elongation requires Earth calculation... maybe skip for Ideal?
                # Or implement simple ideal math. 
                # Let's leave Elongation blank for Ideal to emphasize it's a simplification.
                motion_str = "D" # Mean motion is always direct
            
            self.table.setItem(i, 2, QTableWidgetItem(sign_str))
            self.table.setItem(i, 3, QTableWidgetItem(lat_str))
            self.table.setItem(i, 4, QTableWidgetItem(speed_str))
            self.table.setItem(i, 5, QTableWidgetItem(elong_str))
            self.table.setItem(i, 6, QTableWidgetItem(motion_str))

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
                evt_dt, _ = self.events[row_idx]
                
                # Import here to avoid circular dependency at top level
                from pillars.astrology.ui.natal_chart_window import NatalChartWindow
                
                # We need to instantiate and show the window
                # Assuming simple instantiation works
                self._chart_window = NatalChartWindow()
                
                # Set the date
                # NatalChartWindow -> self.datetime_input (QDateTimeEdit)
                from PyQt6.QtCore import QDateTime, Qt, QTimeZone
                qdt = QDateTime(evt_dt)
                if evt_dt.tzinfo:
                    qdt.setTimeZone(QTimeZone.utc())
                
                self._chart_window.datetime_input.setDateTime(qdt)
                self._chart_window.name_input.setText(f"Venus Trans: {date_str}")
                
                self._chart_window.show()
                
        except Exception as e:
            print(f"Error casting chart: {e}")

    def _refine_conjunction_date(self, approx_dt: datetime, is_superior: bool = False) -> datetime:
        """
        Refine the date to find the exact moment of Heliocentric Conjunction.
        Objective: Minimize abs(Ven_Lon - Earth_Lon) for Inferior, 
                   or abs(abs(Ven_Lon - Earth_Lon) - 180) for Superior.
        Range: +/- 5 days from approx_dt.
        """
        if approx_dt.tzinfo is None:
            approx_dt = approx_dt.replace(tzinfo=timezone.utc)
            
        provider = EphemerisProvider.get_instance()
        
        def get_diff(t):
            """
            Retrieve diff logic.
            
            Args:
                t: Description of t.
            
            Returns:
                Result of get_diff operation.
            """
            d = provider.get_extended_data('venus', t)
            # We need Earth's longitude too. 
            # Ideally extended_data would return it, but we can fetch separately for now
            # or optimize provider. simpler to fetch separately or just assume alignment logic
            # Let's trust provider's get_heliocentric_ecliptic_position for earth?
            # actually provider only takes body_name.
            # Let's peek provider again? 
            # Actually get_heliocentric_ecliptic_position works for 'earth' too if we pass it?
            # Wait, EphemerisProvider code:
            # sun.at(t).observe(planets[body_name])
            # So yes, we can pass 'earth'.
            
            v_lon = d['helio_lon']
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

    def _toggle_physics(self):
        self.is_real_physics = self.btn_physics.isChecked()
        self.btn_physics.setText("Physics: REAL" if self.is_real_physics else "Physics: Ideal")
        self._reset()

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
            if self.current_date > next_evt[0]:
                evt = self.events.pop(0)
                is_inf = "Inf" in evt[1]
                self.scene.add_highlight(is_inf)
                # Scroll table? logic
                
                # For now just pop visual
                self.table.removeRow(0)

    def _reset(self):
        self.timer.stop()
        self.current_date = datetime.now(timezone.utc)
        self.scene.clear_trace()
        self.scene.update_positions_by_date(self.current_date, self.is_real_physics)
        self.label_date.setText(f"Date: {self.current_date.strftime('%Y-%m-%d')}")
        self._calculate_future_events()