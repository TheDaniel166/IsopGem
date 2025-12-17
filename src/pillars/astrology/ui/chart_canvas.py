"""Custom in-app chart renderer (no browser dependency)."""
from typing import List, Optional
import math

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QFont, QPainter, QColor
from PyQt6.QtWidgets import QWidget

from ..models.chart_models import PlanetPosition, HousePosition

class ChartCanvas(QWidget):
    """Custom in-app chart renderer (no browser dependency)."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.planets: List[PlanetPosition] = []
        self.houses: List[HousePosition] = []
        self.setMinimumHeight(320)

    def set_data(self, planets: List[PlanetPosition], houses: List[HousePosition]) -> None:
        self.planets = planets or []
        self.houses = houses or []
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        cx, cy = w / 2.0, h / 2.0
        radius = min(w, h) * 0.44
        inner = radius * 0.70
        house_r = inner * 0.95

        # Rotation: align House I to the left (9 o'clock). If no houses, fall back to 0° Aries at top.
        base_cusp = self.houses[0].degree if self.houses else 0.0

        def angle_for(deg: float) -> float:
            # Rotate so House I is at the left (180° screen) and keep house order counterclockwise from the Ascendant
            return math.radians((base_cusp - deg) + 180.0)

        # Background
        painter.fillRect(self.rect(), QColor(245, 247, 250))

        # Outer ring (zodiac)
        pen = painter.pen()
        pen.setWidthF(1.4)
        pen.setColor(QColor(60, 60, 95))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(cx, cy), radius, radius)

        # Inner ring (houses)
        pen.setColor(QColor(130, 140, 180))
        painter.setPen(pen)
        painter.drawEllipse(QPointF(cx, cy), house_r, house_r)

        # Zodiac ticks/labels
        signs = [
            "Aries",
            "Taurus",
            "Gemini",
            "Cancer",
            "Leo",
            "Virgo",
            "Libra",
            "Scorpio",
            "Sagittarius",
            "Capricorn",
            "Aquarius",
            "Pisces",
        ]
        label_font = QFont()
        label_font.setPointSize(8)
        label_font.setBold(True)
        painter.setFont(label_font)
        for idx, name in enumerate(signs):
            deg = idx * 30.0
            angle = angle_for(deg)
            tx = cx + math.cos(angle) * (radius + 12)
            ty = cy + math.sin(angle) * (radius + 12)
            painter.drawText(QPointF(tx - 14, ty + 4), name[:3])
            # Ticks
            tick_r1 = radius
            tick_r2 = radius * 0.94
            x1 = cx + math.cos(angle) * tick_r1
            y1 = cy + math.sin(angle) * tick_r1
            x2 = cx + math.cos(angle) * tick_r2
            y2 = cy + math.sin(angle) * tick_r2
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # Houses (division lines + labels)
        pen.setColor(QColor(70, 110, 200))
        pen.setWidthF(1.15)
        painter.setPen(pen)
        painter.setFont(QFont("Sans", 8, QFont.Weight.Bold))

        houses_sorted = sorted(self.houses, key=lambda h: h.number)
        for idx, house in enumerate(houses_sorted):
            angle = angle_for(house.degree)
            x_outer = cx + math.cos(angle) * house_r
            y_outer = cy + math.sin(angle) * house_r
            x_inner = cx + math.cos(angle) * (house_r * 0.58)
            y_inner = cy + math.sin(angle) * (house_r * 0.58)
            painter.drawLine(QPointF(x_inner, y_inner), QPointF(x_outer, y_outer))

            # Label at midpoint to next cusp
            next_house = houses_sorted[(idx + 1) % len(houses_sorted)] if houses_sorted else house
            mid_deg = (house.degree + next_house.degree) / 2.0
            # unwrap if crossing 360
            if next_house.degree < house.degree:
                mid_deg = (house.degree + (next_house.degree + 360.0)) / 2.0
            mid_angle = angle_for(mid_deg % 360.0)
            lx = cx + math.cos(mid_angle) * (house_r * 0.40)
            ly = cy + math.sin(mid_angle) * (house_r * 0.40)
            painter.drawText(QPointF(lx - 6, ly + 4), str(house.number))

        # Planets (glyphs + markers)
        planet_font = QFont()
        planet_font.setPointSize(11)
        planet_font.setBold(True)
        painter.setFont(planet_font)
        pen.setColor(QColor(30, 30, 30))
        painter.setPen(pen)
        base_r = inner * 0.86
        glyph_offset = 12.0
        for idx, pos in enumerate(self.planets):
            angle = angle_for(pos.degree)
            # Stagger radius slightly to reduce overlap
            marker_r = base_r + ((idx % 3) - 1) * 8.0
            px = cx + math.cos(angle) * marker_r
            py = cy + math.sin(angle) * marker_r
            painter.setBrush(QColor(245, 247, 250))
            painter.drawEllipse(QPointF(px, py), 4.0, 4.0)
            gx = px + math.cos(angle) * glyph_offset
            gy = py + math.sin(angle) * glyph_offset
            painter.drawText(QPointF(gx - 6, gy + 5), self._planet_glyph(pos.name))

        painter.end()

    @staticmethod
    def _planet_glyph(name: str) -> str:
        key = name.strip().lower()
        glyphs = {
            "sun": "☉",
            "moon": "☽",
            "mercury": "☿",
            "venus": "♀",
            "mars": "♂",
            "jupiter": "♃",
            "saturn": "♄",
            "uranus": "♅",
            "neptune": "♆",
            "pluto": "♇",
            "north node": "☊",
            "south node": "☋",
            "mean node": "☊",
            "true node": "☊",
            "chiron": "⚷",
            "asc": "ASC",
            "mc": "MC",
        }
        return glyphs.get(key, name[:2].upper() if name else "")
