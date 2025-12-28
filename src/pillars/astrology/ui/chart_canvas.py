"""Custom in-app chart renderer (no browser dependency)."""
from typing import List, Optional
import math

from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import (
    QFont,
    QPainter,
    QColor,
    QPen,
    QBrush,
    QRadialGradient,
    QLinearGradient,
    QMouseEvent,
)
from PyQt6.QtWidgets import QWidget

from ..models.chart_models import PlanetPosition, HousePosition

class ChartCanvas(QWidget):
    """Custom in-app chart renderer (no browser dependency) with 'Celestia' design."""

    def __init__(self, parent: Optional[QWidget] = None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.planets: List[PlanetPosition] = []
        self.houses: List[HousePosition] = []
        self.setMinimumHeight(400)
        self.setStyleSheet("background-color: #0f0f13;")
        self.setMouseTracking(True)  # Enable hover detection

        # Interaction State
        self._hovered_planet: Optional[PlanetPosition] = None
        self._planet_hitboxes: List[tuple[QRectF, PlanetPosition]] = []
        
        self._hovered_house: Optional[HousePosition] = None
        self._house_hitboxes: List[tuple[QRectF, HousePosition]] = []

        # Celestia Palette
        self.c_background_start = QColor("#1a1a2e")
        self.c_background_end = QColor("#0f0f13")
        self.c_gold = QColor("#D4AF37")
        self.c_silver = QColor("#E0E0E0")
        self.c_house_line = QColor(255, 255, 255, 30)
        self.c_zodiac_ring_bg = QColor(255, 255, 255, 10) 
        self.c_planet_glow = QColor(255, 255, 255, 40)

        # Aspect Colors
        self.c_aspect_trine = QColor("#4deeea") # Neon Blue
        self.c_aspect_square = QColor("#f000ff") # Neon Magenta/Red
        self.c_aspect_opp = QColor("#ff2a6d") # Red
        self.c_aspect_sextile = QColor("#74ee15") # Lime
        self.c_aspect_conj = QColor("#ffee00") # Yellow
        
        # Minor Aspect Colors
        self.c_aspect_semisextile = QColor("#88aa88")  # Muted green
        self.c_aspect_semisquare = QColor("#cc88cc")   # Muted purple
        self.c_aspect_quintile = QColor("#88cccc")     # Teal
        self.c_aspect_sesquiquadrate = QColor("#cc8888")  # Muted red
        self.c_aspect_quincunx = QColor("#cccc88")     # Muted yellow

        # Aspect display options
        self._include_minor_aspects = False
        self._orb_factor = 1.0

        # Planet Colors (Nature-based)
        self.planet_colors = {
            "Sun": QColor("#FFD700"),       # Gold
            "Moon": QColor("#E0E0E0"),      # Silver/White
            "Mercury": QColor("#B0C4DE"),   # Light Steel Blue
            "Venus": QColor("#F4C2C2"),     # Tea Rose
            "Mars": QColor("#FF6B6B"),      # Soft Red
            "Jupiter": QColor("#FFA07A"),   # Light Salmon
            "Saturn": QColor("#F4A460"),    # Sandy Brown
            "Uranus": QColor("#87CEEB"),    # Sky Blue
            "Neptune": QColor("#9370DB"),   # Medium Purple
            "Pluto": QColor("#708090"),     # Slate Gray
            "North Node": QColor("#A9A9A9"),
            "South Node": QColor("#A9A9A9"),
            "Chiron": QColor("#20B2AA"),    # Light Sea Green
            "ASC": QColor("#D4AF37"),       # Gold
            "MC": QColor("#D4AF37"),        # Gold
        }

    def set_data(self, planets: List[PlanetPosition], houses: List[HousePosition]) -> None:
        # Whitelist of major bodies to display
        """
        Configure data logic.
        
        Args:
            planets: Description of planets.
            houses: Description of houses.
        
        Returns:
            Result of set_data operation.
        """
        shown_bodies = {
            "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter",
            "Saturn", "Uranus", "Neptune", "Pluto", 
            "North Node", "South Node", "Mean Node", "True Node",
            "Chiron"
        }
        
        candidates = []
        if planets:
            for p in planets:
                if any(b.lower() == p.name.strip().lower() for b in shown_bodies):
                    candidates.append(p)

        # Refine: Prioritize True Node over Mean Node
        has_true = any(p.name.strip().lower() == "true node" for p in candidates)
        filtered_planets = []
        for p in candidates:
            name_lower = p.name.strip().lower()
            if has_true and name_lower == "mean node":
                continue
            filtered_planets.append(p)
        
        self.planets = filtered_planets
        self.houses = houses or []
        self.update()

    def set_aspect_options(self, include_minor: bool, orb_factor: float) -> None:
        """Set aspect display options."""
        self._include_minor_aspects = include_minor
        self._orb_factor = orb_factor
        self.update()

    def mouseMoveEvent(self, a0: Optional[QMouseEvent]) -> None:
        """
        Mousemoveevent logic.
        
        Args:
            a0: Description of a0.
        
        Returns:
            Result of mouseMoveEvent operation.
        """
        pos = a0.position() if a0 else QPointF()
        
        # Check Planets
        hovered_planet = None
        for rect, planet in self._planet_hitboxes:
            if rect.contains(pos):
                hovered_planet = planet
                break
        
        # Check Houses (only if not over a planet)
        hovered_house = None
        if not hovered_planet:
            for rect, house in self._house_hitboxes:
                if rect.contains(pos):
                    hovered_house = house
                    break

        # Update State
        if hovered_planet != self._hovered_planet or hovered_house != self._hovered_house:
            self._hovered_planet = hovered_planet
            self._hovered_house = hovered_house
            
            # Tooltip
            if self._hovered_planet:
                self.setToolTip(f"{self._hovered_planet.name}: {self._format_degree(self._hovered_planet.degree)}")
                self.setCursor(Qt.CursorShape.PointingHandCursor)
            elif self._hovered_house:
                self.setToolTip(f"House {self._hovered_house.number}: {self._format_degree(self._hovered_house.degree)}")
                self.setCursor(Qt.CursorShape.PointingHandCursor)
            else:
                self.setToolTip("")
                self.setCursor(Qt.CursorShape.ArrowCursor)
                
            self.update()

    def _format_degree(self, deg: float) -> str:
        d = int(deg)
        m = int((deg - d) * 60)
        # Simple sign calc
        signs = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
        sign_idx = int(d / 30) % 12
        sign_deg = d % 30
        return f"{sign_deg}° {signs[sign_idx]} {m}'"

    def paintEvent(self, event) -> None:  # type: ignore[override]
        """
        Paintevent logic.
        
        Args:
            event: Description of event.
        
        Returns:
            Result of paintEvent operation.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        cx, cy = w / 2.0, h / 2.0
        
        # Dimensions
        radius = min(w, h) * 0.45
        inner_radius = radius * 0.75
        house_radius = inner_radius * 0.95
        
        # Reset Hitboxes
        self._planet_hitboxes = []
        self._house_hitboxes = []

        # 1. Background (The Void)
        self._draw_background(painter, cx, cy, w, h)

        # Rotation: Align House I to left (9 o'clock)
        base_cusp = self.houses[0].degree if self.houses else 0.0

        def angle_for(deg: float) -> float:
            """
            Angle for logic.
            
            Args:
                deg: Description of deg.
            
            Returns:
                Result of angle_for operation.
            """
            return math.radians((base_cusp - deg) + 180.0)

        # 2. Houses (The Earthly Plane)
        self._draw_houses(painter, cx, cy, angle_for, radius, inner_radius)
        
        # 3. Aspects (The Web of Fate) - Draw BEHIND planets
        if self._hovered_planet:
            self._draw_aspects(painter, cx, cy, angle_for, inner_radius)

        # 4. Zodiac Ring (The Firmament)
        self._draw_zodiac_ring(painter, cx, cy, angle_for, radius, inner_radius)

        # 5. Planets (The Wandering Stars)
        self._draw_planets(painter, cx, cy, angle_for, inner_radius)
        
        # Center decoration
        self._draw_center_decoration(painter, cx, cy, inner_radius * 0.6)

        painter.end()

    def _draw_background(self, p: QPainter, cx: float, cy: float, w: float, h: float) -> None:
        gradient = QRadialGradient(cx, cy, max(w, h) * 0.8)
        gradient.setColorAt(0.0, self.c_background_start)
        gradient.setColorAt(1.0, self.c_background_end)
        p.fillRect(0, 0, int(w), int(h), QBrush(gradient))

    def _draw_zodiac_ring(self, p: QPainter, cx: float, cy: float, angle_func, r_outer: float, r_inner: float) -> None:
        # Outer stroke
        pen = QPen(self.c_gold)
        pen.setWidthF(1.5)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QPointF(cx, cy), r_outer, r_outer)
        
        # Inner stroke
        pen.setColor(self.c_silver)
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.drawEllipse(QPointF(cx, cy), r_inner, r_inner)

        # Signs
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer",
            "Leo", "Virgo", "Libra", "Scorpio",
            "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        
        font = QFont("Serif", 10) # Elegant font
        font.setBold(True)
        p.setFont(font)
        
        for idx, name in enumerate(signs):
            # Draw dividers
            deg_start = idx * 30.0
            angle_start = angle_func(deg_start)
            
            x1 = cx + math.cos(angle_start) * r_inner
            y1 = cy + math.sin(angle_start) * r_inner
            x2 = cx + math.cos(angle_start) * r_outer
            y2 = cy + math.sin(angle_start) * r_outer
            
            p.setPen(QPen(QColor(255,255,255, 50), 1))
            p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            
            # Label center
            mid_deg = deg_start + 15.0
            mid_angle = angle_func(mid_deg)
            text_r = (r_outer + r_inner) / 2.0
            tx = cx + math.cos(mid_angle) * text_r
            ty = cy + math.sin(mid_angle) * text_r
            
            p.setPen(self.c_gold)
            # Center text calculation
            rect_w, rect_h = 40, 20
            t_rect = QRectF(tx - rect_w/2, ty - rect_h/2, rect_w, rect_h)
            p.drawText(t_rect, Qt.AlignmentFlag.AlignCenter, self._sign_glyph(name))

    def _draw_houses(self, p: QPainter, cx: float, cy: float, angle_func, r_outer: float, r_inner: float) -> None:
        if not self.houses:
            return
            
        pen_cusp = QPen(self.c_silver)
        pen_line = QPen(self.c_house_line)
        pen_line.setStyle(Qt.PenStyle.DashLine)
        
        houses_sorted = sorted(self.houses, key=lambda h: h.number)
        
        # House numbers font
        font = QFont("Sans", 7)
        font.setBold(True)
        p.setFont(font)
        
        for idx, house in enumerate(houses_sorted):
            angle = angle_func(house.degree)
            
            # Hitbox for Cusp (Outer ring segment)
            # Simplification: Small rect around the cusp marker on the outer ring
            hx = cx + math.cos(angle) * r_inner
            hy = cy + math.sin(angle) * r_inner
            
            hit_size = 15.0
            self._house_hitboxes.append((
                QRectF(hx - hit_size/2, hy - hit_size/2, hit_size, hit_size),
                house
            ))

            # Highlight if hovered
            is_hovered = (self._hovered_house == house)
            
            # Cusp marker on inner ring
            if is_hovered:
                p.setPen(QPen(self.c_gold, 2.0))
                p.drawEllipse(QPointF(hx, hy), 6.0, 6.0)
            else:
                p.setPen(pen_cusp)
                p.drawEllipse(QPointF(hx, hy), 4.0, 4.0)
            
            # Line towards center (fade out)
            p.setPen(pen_line)
            lx = cx + math.cos(angle) * (r_inner * 0.2)
            ly = cy + math.sin(angle) * (r_inner * 0.2)
            p.drawLine(QPointF(lx, ly), QPointF(hx, hy))
            
            # Number
            next_house = houses_sorted[(idx + 1) % len(houses_sorted)] if houses_sorted else house
            h1 = house.degree
            h2 = next_house.degree
            if h2 < h1: h2 += 360
            mid_deg = (h1 + h2) / 2.0
            mid_angle = angle_func(mid_deg % 360)
            
            num_r = r_inner * 0.90
            nx = cx + math.cos(mid_angle) * num_r
            ny = cy + math.sin(mid_angle) * num_r
            
            p.setPen(QColor(255, 255, 255, 100))
            p.drawText(QPointF(nx - 4, ny + 4), str(house.number))

    def _draw_planets(self, p: QPainter, cx: float, cy: float, angle_func, r_inner: float) -> None:
        base_r = r_inner * 0.75
        
        font = QFont("Sans", 10, QFont.Weight.Bold)
        p.setFont(font)
        
        for idx, pos in enumerate(self.planets):
            angle = angle_func(pos.degree)
            
            # Stagger tiers to prevent overlap
            tier = idx % 3
            marker_r = base_r - (tier * 15.0)
            
            px = cx + math.cos(angle) * marker_r
            py = cy + math.sin(angle) * marker_r
            
            # Hitbox
            hit_size = 20.0
            self._planet_hitboxes.append((
                QRectF(px - hit_size/2, py - hit_size/2, hit_size, hit_size),
                pos
            ))
            
            color = self._get_planet_color(pos.name)
            is_hovered = (self._hovered_planet == pos)
            
            # Glow behind
            glow_alpha = 100 if is_hovered else 60
            glow_size = 12.0 if is_hovered else 8.0
            
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(color.red(), color.green(), color.blue(), glow_alpha))
            p.drawEllipse(QPointF(px, py), glow_size, glow_size)
            
            # Core orb
            p.setBrush(color)
            p.drawEllipse(QPointF(px, py), 3.0, 3.0)
            
            # Glyph label
            p.setPen(color)
            if is_hovered:
                # Highlight text
                font_hover = QFont(font)
                font_hover.setBold(True)
                font_hover.setPointSize(12)
                p.setFont(font_hover)
                p.drawText(QPointF(px + 8, py + 6), self._planet_glyph(pos.name))
                p.setFont(font) # Restore
            else:
                p.drawText(QPointF(px + 6, py + 5), self._planet_glyph(pos.name))

    def _draw_aspects(self, p: QPainter, cx: float, cy: float, angle_func, r_inner: float) -> None:
        """Draw aspect lines from the hovered planet to others."""
        if not self._hovered_planet:
            return

        h_deg = self._hovered_planet.degree
        base_r = r_inner * 0.75
        
        # Major Aspects (angle, default_orb, color)
        aspects = [
            (0, 8, self.c_aspect_conj),    # Conjunction
            (60, 4, self.c_aspect_sextile), # Sextile
            (90, 6, self.c_aspect_square),  # Square
            (120, 8, self.c_aspect_trine),  # Trine
            (180, 8, self.c_aspect_opp),    # Opposition
        ]
        
        # Add minor aspects if enabled
        if self._include_minor_aspects:
            aspects.extend([
                (30, 2, self.c_aspect_semisextile),   # Semi-sextile
                (45, 2, self.c_aspect_semisquare),   # Semi-square
                (72, 2, self.c_aspect_quintile),     # Quintile
                (135, 2, self.c_aspect_sesquiquadrate), # Sesquiquadrate
                (150, 3, self.c_aspect_quincunx),    # Quincunx
            ])

        # Calculate position of hovered planet
        # Note: We duplicate the radius calculation logic here... 
        # Ideally we'd store positions in a pass before drawing, but for now we re-calc.
        h_idx = self.planets.index(self._hovered_planet)
        h_tier = h_idx % 3
        h_r = base_r - (h_tier * 15.0)
        h_angle = angle_func(h_deg)
        hx = cx + math.cos(h_angle) * h_r
        hy = cy + math.sin(h_angle) * h_r

        for idx, pos in enumerate(self.planets):
            if pos == self._hovered_planet:
                continue
                
            # Calc difference
            diff = abs(pos.degree - h_deg)
            if diff > 180: diff = 360 - diff
            
            # Check for aspect
            matched_color = None
            for angle, orb, color in aspects:
                if abs(diff - angle) <= orb * self._orb_factor:
                    matched_color = color
                    break
            
            if matched_color:
                # Calc target position
                t_tier = idx % 3
                t_r = base_r - (t_tier * 15.0)
                t_angle = angle_func(pos.degree)
                tx = cx + math.cos(t_angle) * t_r
                ty = cy + math.sin(t_angle) * t_r
                
                # Draw Line
                pen = QPen(matched_color)
                pen.setWidthF(1.5)
                # Opaque line
                p.setPen(pen)
                p.drawLine(QPointF(hx, hy), QPointF(tx, ty))

    def _draw_center_decoration(self, p: QPainter, cx: float, cy: float, r: float) -> None:
        # Subtle aspect web placeholder or just a decorative center
        pen = QPen(QColor(255, 255, 255, 10))
        pen.setWidth(1)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QPointF(cx, cy), r, r)
        p.drawEllipse(QPointF(cx, cy), r*0.5, r*0.5)

    def _get_planet_color(self, name: str) -> QColor:
        for key, color in self.planet_colors.items():
            if key.lower() in name.lower():
                return color
        return self.c_silver

    @staticmethod
    def _planet_glyph(name: str) -> str:
        key = name.strip().lower()
        glyphs = {
            "sun": "☉", "moon": "☽", "mercury": "☿", "venus": "♀",
            "mars": "♂", "jupiter": "♃", "saturn": "♄", "uranus": "♅",
            "neptune": "♆", "pluto": "♇", "north node": "☊", "south node": "☋",
            "mean node": "☊", "true node": "☊",
            "chiron": "⚷", "asc": "ASC", "mc": "MC",
        }
        return glyphs.get(key, name[:2].upper() if name else "")

    @staticmethod
    def _sign_glyph(name: str) -> str:
        glyphs = {
            "Aries": "♈", "Taurus": "♉", "Gemini": "♊", "Cancer": "♋",
            "Leo": "♌", "Virgo": "♍", "Libra": "♎", "Scorpio": "♏",
            "Sagittarius": "♐", "Capricorn": "♑", "Aquarius": "♒", "Pisces": "♓"
        }
        return glyphs.get(name, name[:3])