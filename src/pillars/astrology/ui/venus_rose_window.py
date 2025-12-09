
"""
Cytherean Rose Clock
A generative visualization of the Pentagram of Venus (13:8 Earth-Venus resonance).
"""
from __future__ import annotations

import math
from typing import List
from datetime import datetime, timedelta, timezone

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
        super().__init__(-size/2, -size/2, size, size)
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.GlobalColor.white))
        self.setToolTip(label)
        self.setZValue(10) # Draw on top

class GlowingParticle(QGraphicsEllipseItem):
    """A glowing highlight for conjunction points."""
    def __init__(self, x, y, is_inferior=True):
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
    def __init__(self):
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
        h = GlowingParticle(self.venus.x(), self.venus.y(), is_inferior)
        self.addItem(h)
        self.highlights.append(h)
        if len(self.highlights) > 20: # Keep last 20
            self.removeItem(self.highlights.pop(0))
            
    def clear_trace(self):
        for line in self.trace_lines:
            self.removeItem(line)
        self.trace_lines.clear()
        for h in self.highlights:
            self.removeItem(h)
        self.highlights.clear()


class RoseView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.scale(0.8, 0.8)

    def wheelEvent(self, event: QWheelEvent):
        factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        self.scale(factor, factor)


class VenusRoseWindow(QMainWindow):
    def __init__(self, parent=None):
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
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Date", "Type", "Sign"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
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
        deg_per_day_v = 360.0 / P_VENUS
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
        # If diff < 180 (e.g. 10), need 170. 
        # If diff > 180 (e.g. 350), need 190.
        days_to_sup = ((180 - diff) % 360) / rel_v
        
        # Generate list
        # We start with the closest ones and step by Synodic Period
        t_inf = start_date + timedelta(days=days_to_inf)
        t_sup = start_date + timedelta(days=days_to_sup)
        
        raw_events = []
        for i in range(20): # Next 20 events
            # Inferior
            d_inf = t_inf + timedelta(days=i * SYNODIC_PERIOD)
            raw_events.append((d_inf, "Petal Point (Inf)"))
            # Superior
            d_sup = t_sup + timedelta(days=i * SYNODIC_PERIOD)
            raw_events.append((d_sup, "Outer Point (Sup)"))
            
        raw_events.sort(key=lambda x: x[0])
        
        self.events = raw_events
        self.table.setRowCount(len(raw_events))
        for i, (dt, evt_type) in enumerate(raw_events):
            self.table.setItem(i, 0, QTableWidgetItem(dt.strftime("%Y-%m-%d")))
            self.table.setItem(i, 1, QTableWidgetItem(evt_type))
            # Sign approx
            # Improve sign calc later
            self.table.setItem(i, 2, QTableWidgetItem("--"))

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

