"""
Neo-Aubrey Eclipse Clock
A dual-ring visualization tracking Saros (223) and Aubrey (56) cycles.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import (
    QBrush, 
    QColor, 
    QFont, 
    QPainter, 
    QPainterPath, 
    QPen, 
    QWheelEvent,
    QPolygonF
)
from PyQt6.QtWidgets import (
    QGraphicsItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
    QGraphicsEllipseItem,
    QGraphicsTextItem,
    QGraphicsLineItem
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
        super().__init__(x - r, y - r, r * 2, r * 2)
        self.setBrush(QBrush(COLOR_STONE))
        self.setPen(QPen(Qt.GlobalColor.black))
        self.index = index
        self.setToolTip(f"{label} #{index + 1}")

class MarkerItem(QGraphicsEllipseItem):
    """Movable marker (Sun, Moon, etc)."""
    def __init__(self, color: QColor, label: str):
        super().__init__(-10, -10, 20, 20) # 20px size
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.GlobalColor.white, 2))
        self.setZValue(10) # Draw on top
        self.setToolTip(label)
        self._label_item = QGraphicsTextItem(label, self)
        self._label_item.setPos(10, 10)
        self._label_item.setDefaultTextColor(Qt.GlobalColor.white)

class EclipseClockScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setBackgroundBrush(QBrush(QColor("#1e1e1e")))
        self.saros_stones: List[StoneItem] = []
        self.aubrey_stones: List[StoneItem] = []
        
        self.sun_marker = MarkerItem(COLOR_SUN, "Sun")
        self.moon_marker = MarkerItem(COLOR_MOON, "Moon")
        self.node_marker = MarkerItem(COLOR_NODE, "Node")
        self.saros_hand = MarkerItem(COLOR_SAROS_HAND, "Saros")
        
        self._build_rings()
        
        self.addItem(self.sun_marker)
        self.addItem(self.moon_marker)
        self.addItem(self.node_marker)
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

    def update_positions(self, dt: datetime):
        delta = dt - J2000
        days = delta.total_seconds() / 86400.0
        
        # J2000 Offsets (Mean Longitude at 2000-01-01 12:00 UTC)
        # Sun: 280.46 deg -> Hole 43.62
        # Moon: 218.31 deg -> Hole 33.96
        # Node: 125.04 deg -> Hole 19.45
        sun_offset = 43.62
        moon_offset = 33.96
        node_offset = 19.45

        # 1. Saros Logic (Outer Ring)
        # Moves 1 hole per Synodic Month
        saros_idx = (days / SYNODIC_MONTH) % SAROS_HOLES
        self._place_marker_on_ring(self.saros_hand, saros_idx, SAROS_HOLES, SAROS_RADIUS)
        
        # 2. Aubrey Logic (Inner Ring) - Scaled to standard J2000 positions
        # Sun: 2 holes every 13 days -> ~364 day cycle. 
        # Rate: 56 holes / 365.2422 days = 0.1533 holes/day
        sun_pos = (sun_offset + days * (56.0 / 365.2422)) % AUBREY_HOLES
        self._place_marker_on_ring(self.sun_marker, sun_pos, AUBREY_HOLES, AUBREY_RADIUS)
        
        # Moon: 2 holes per day -> ~28 day cycle
        # Rate: 56 holes / 27.322 days (Sidereal) = 2.05 holes/day
        moon_pos = (moon_offset + days * (56.0 / 27.322)) % AUBREY_HOLES
        self._place_marker_on_ring(self.moon_marker, moon_pos, AUBREY_HOLES, AUBREY_RADIUS)
        
        # Node: 3 holes per year -> ~18.66 years
        # Rate: -3 holes / 365.2422 days (Retrograde)
        # Node moves backwards (Retrograde)
        node_pos = (node_offset - days * (56.0 / (18.61 * 365.2422))) % AUBREY_HOLES
        self._place_marker_on_ring(self.node_marker, node_pos, AUBREY_HOLES, AUBREY_RADIUS)

    def _place_marker_on_ring(self, marker: QGraphicsItem, index: float, total: int, radius: float):
        angle_deg = (index / total) * 360.0 - 90
        rad = math.radians(angle_deg)
        x = radius * math.cos(rad)
        y = radius * math.sin(rad)
        marker.setPos(x, y)


class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.scale(0.8, 0.8) # Initial zoom out

    def wheelEvent(self, event: QWheelEvent):
        zoom_in = event.angleDelta().y() > 0
        factor = 1.1 if zoom_in else 0.9
        self.scale(factor, factor)


class NeoAubreyWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Neo-Aubrey Eclipse Clock")
        self.resize(1000, 800)
        
        self.current_time = datetime.now(timezone.utc)
        self.scene = EclipseClockScene()
        self.view = ZoomableGraphicsView(self.scene)
        
        # UI
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.addWidget(self.view)
        
        # Controls
        ctrl_layout = QHBoxLayout()
        
        self.date_label = QLabel()
        self._update_label()
        ctrl_layout.addWidget(self.date_label)
        
        btn_now = QPushButton("Now")
        btn_now.clicked.connect(self._reset_now)
        ctrl_layout.addWidget(btn_now)
        
        # Multi-speed Timeline
        self.timer = QTimer()
        self.timer.timeout.connect(self._animate)
        
        btn_play = QPushButton("Play (1 day/tick)")
        btn_play.clicked.connect(lambda: self._start_animation(1))
        ctrl_layout.addWidget(btn_play)
        
        btn_ff = QPushButton("Fast Fwd (1 month/tick)")
        btn_ff.clicked.connect(lambda: self._start_animation(30))
        ctrl_layout.addWidget(btn_ff)
        
        btn_stop = QPushButton("Stop")
        btn_stop.clicked.connect(self.timer.stop)
        ctrl_layout.addWidget(btn_stop)
        
        layout.addLayout(ctrl_layout)
        
        # Initial Draw
        self.scene.update_positions(self.current_time)

    def _reset_now(self):
        self.current_time = datetime.now(timezone.utc)
        self.scene.update_positions(self.current_time)
        self._update_label()

    def _start_animation(self, days_per_tick: int):
        self.days_per_tick = days_per_tick
        self.timer.start(50) # 20 FPS

    def _animate(self):
        self.current_time += timedelta(days=self.days_per_tick)
        self.scene.update_positions(self.current_time)
        self._update_label()

    def _update_label(self):
        self.date_label.setText(f"Date: {self.current_time.strftime('%Y-%m-%d')}")
