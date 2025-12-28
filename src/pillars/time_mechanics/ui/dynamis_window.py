"""
Dynamis Window - The Circulation of Energies.
Visual Tzolkin cycle animator with trigram rendering, dipole field, and orb tracking.
"""
import math
from datetime import timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene, 
    QGraphicsItem, QSlider, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QColor, QPen, QBrush, QPainter, QPainterPath, QFont, QRadialGradient, QLinearGradient

from ..services.tzolkin_service import TzolkinService
from ..models.tzolkin_models import TzolkinDate

class TrigramItem(QGraphicsItem):
    """
    Renders a single 3-line Trigram.
    Style: 'SOLID' (Anchor) or 'FLUID' (Flux).
    """
    def __init__(self, trigram_str="000", size=60, color=QColor("#333"), style='SOLID'):
        super().__init__()
        self.trigram = trigram_str
        self.size = size
        self.color = color
        self.style = style # 'SOLID', 'FLUID', 'FIRE', 'MIST'
        
    def boundingRect(self) -> QRectF:
        return QRectF(-self.size/2, -self.size/2, self.size, self.size)
        
    def paint(self, painter: QPainter, option, widget):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        pen = QPen(self.color, 4 if self.style in ['SOLID', 'CRYSTAL'] else 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        
        if self.style in ['FLUID', 'MIST', 'FIRE']:
            pen.setStyle(Qt.PenStyle.DashLine if self.style == 'FLUID' else Qt.PenStyle.DotLine)
            
        painter.setPen(pen)
        
        # Draw 3 lines
        spacing = self.size / 3
        y_start = -self.size / 3
        
        for i, char in enumerate(self.trigram):
            y = y_start + (i * spacing)
            self._draw_line(painter, char, y)

    def _draw_line(self, painter, type_char, y):
        w = self.size 
        x_left = -w / 2
        x_right = w / 2
        
        if type_char == '1': # Yang (Solid)
            painter.drawLine(QPointF(x_left, y), QPointF(x_right, y))
            
        elif type_char == '2': # Yin (Broken)
            gap = w / 5
            mid_l = -gap/2
            mid_r = gap/2
            painter.drawLine(QPointF(x_left, y), QPointF(mid_l, y))
            painter.drawLine(QPointF(mid_r, y), QPointF(x_right, y))
            
        else: # Void (Ghost)
            p = painter.pen()
            p.setColor(self.color.lighter(160))
            p.setWidth(1)
            painter.setPen(p)
            painter.drawLine(QPointF(x_left, y), QPointF(x_right, y))
            # Restore
            p.setColor(self.color)
            if self.style in ['SOLID', 'CRYSTAL']: p.setWidth(4)
            else: p.setWidth(2)
            painter.setPen(p)

    def update_trigram(self, new_val, new_style):
        self.trigram = new_val
        self.style = new_style
        self.update()

class PillarGauge(QGraphicsItem):
    """
    The Central Gauge visualizing the Column Logic.
    Shows the Upper and Lower Trigrams with distinct styles based on Column Type.
    """
    def __init__(self):
        super().__init__()
        self.size = 200
        self.col_type = "ODD" # ODD, EVEN, MYSTIC
        self.upper_t = "000"
        self.lower_t = "000"
        
    def boundingRect(self):
        return QRectF(-self.size/2, -self.size/2, self.size, self.size)
        
    def update_state(self, upper, lower, tone):
        self.upper_t = upper
        self.lower_t = lower
        
        if tone == 7:
            self.col_type = "MYSTIC"
        elif tone % 2 != 0:
            self.col_type = "ODD"
        else:
            self.col_type = "EVEN"
        self.update()
        
    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background Circle
        r = self.size / 2
        if self.col_type == "MYSTIC":
            color = QColor("#f0abfc") # Purple-ish
        elif self.col_type == "ODD":
            color = QColor("#bae6fd") # Sky Blue (but Earth is Anchor) - Wait, ODD = Earth Anchor.
            # Visual cue: Earth (Bot) is Solid.
        else:
            color = QColor("#fda4af") # Reddish (Even = Sky Anchor)
            
        grad = QRadialGradient(0, 0, r)
        grad.setColorAt(0, color.lighter(120))
        grad.setColorAt(1, QColor("#0f172a")) # Fade to bg
        painter.setBrush(grad)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(0,0), r, r)
        
        # Determine Styles
        # ODD Col (1,3..): Earth Fixed (Solid), Sky Fluid (Mist)
        # EVEN Col (2,4..): Sky Fixed (Solid), Earth Fluid (Fire)
        # MYSTIC (7): Mirror (Both Fluid/Crystal?)
        
        u_style = 'SOLID'
        l_style = 'SOLID'
        u_color = QColor("white")
        l_color = QColor("white")
        
        if self.col_type == "ODD":
            l_style = 'SOLID' # Anchor
            l_color = QColor("#f59e0b") # Amber Earth
            u_style = 'MIST'  # Flux
            u_color = QColor("#7dd3fc") # Sky
            
        elif self.col_type == "EVEN":
            u_style = 'CRYSTAL' # Anchor
            u_color = QColor("#38bdf8") # Blue Crystal
            l_style = 'FIRE'    # Flux
            l_color = QColor("#f43f5e") # Red Fire
            
        elif self.col_type == "MYSTIC":
            u_style = 'CRYSTAL'
            l_style = 'CRYSTAL'
            u_color = QColor("#d8b4fe")
            l_color = QColor("#d8b4fe")
            
        # Draw Trigrams Manually here or use helper?
        # Let's instantiate temporary helpers or draw simple lines?
        # Better to have Child Items? 
        # Painting directly allows us to control the "Gauge" feel within one item easily.
        
        # Draw Top Trigram
        self._draw_trigram_at(painter, self.upper_t, 0, -r/2, u_style, u_color)
        
        # Draw Bottom Trigram
        self._draw_trigram_at(painter, self.lower_t, 0, r/2, l_style, l_color)
        
        # Draw Divider
        painter.setPen(QPen(QColor(255,255,255,50), 1))
        painter.drawLine(QPointF(-r/2, 0), QPointF(r/2, 0))
        
        # Text Label for Type
        font = QFont("Arial", 10)
        painter.setFont(font)
        painter.setPen(QColor(255,255,255,100))
        painter.drawText(QRectF(-r, -15, r*2, 30), Qt.AlignmentFlag.AlignCenter, self.col_type)

    def _draw_trigram_at(self, painter, trigram, cx, cy, style, color):
        # Mini version of TrigramItem logic
        size = 50
        spacing = size / 3
        y_start = cy - size/3
        
        pen = QPen(color, 3)
        if style in ['MIST', 'FIRE']:
            pen.setStyle(Qt.PenStyle.DotLine)
        elif style == 'CRYSTAL':
            pen.setWidth(4)
        
        painter.setPen(pen)
        
        for i, char in enumerate(trigram):
            y = y_start + (i * spacing)
            w = size 
            x_left = cx - w / 2
            x_right = cx + w / 2
            
            if char == '1': # Solid
                painter.drawLine(QPointF(x_left, y), QPointF(x_right, y))
            elif char == '2': # Broken
                mid_l = cx - w/10
                mid_r = cx + w/10
                painter.drawLine(QPointF(x_left, y), QPointF(mid_l, y))
                painter.drawLine(QPointF(mid_r, y), QPointF(x_right, y))
            else: # Void
                pass

class OrbItem(QGraphicsItem):
    def __init__(self, color, radius=10):
        super().__init__()
        self.color = QColor(color)
        self.radius = radius
        
    def boundingRect(self):
        return QRectF(-self.radius*2, -self.radius*2, self.radius*4, self.radius*4)
                      
    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = QColor(self.color)
        # Glow
        grad = QRadialGradient(0, 0, self.radius*2)
        grad.setColorAt(0, c)
        c_trans = QColor(c)
        c_trans.setAlpha(0)
        grad.setColorAt(1, c_trans)
        painter.setBrush(grad)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(0,0), self.radius*2, self.radius*2)
        # Core
        painter.setBrush(c)
        painter.drawEllipse(QPointF(0,0), self.radius/2, self.radius/2)

class DynamisScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(-400, -400, 800, 800)
        self.setBackgroundBrush(QColor("#0f172a"))
        
        self.track_radius = 280
        
        # Items
        self.pillar_gauge = PillarGauge()
        self.addItem(self.pillar_gauge)
        
        self.self_orb = OrbItem("#0ea5e9", 15)
        self.conrune_orb = OrbItem("#f43f5e", 15)
        
        self.addItem(self.self_orb)
        self.addItem(self.conrune_orb)
        
    def drawBackground(self, painter, rect):
        # Draw Dipole Field (Top Blue, Bottom Red)
        # Represents +168 Charge (Top) vs -168 Charge (Bottom)
        # We want a subtle gradient.
        
        scene_rect = self.sceneRect()
        
        # Gradient from Top (-400) to Bottom (+400)
        grad = QLinearGradient(0, -400, 0, 400)
        # Top: Positive/Blue-ish
        grad.setColorAt(0.0, QColor("#0f172a")) # Slate 900 (Dark)
        grad.setColorAt(0.2, QColor("#1e293b")) # Slate 800
        grad.setColorAt(0.5, QColor("#0f172a")) # Dark Equator
        grad.setColorAt(0.8, QColor("#2a1215")) # Reddish Dark
        grad.setColorAt(1.0, QColor("#0f172a"))
        
        # Let's try simpler: Split background
        # Actually, let's just fill the rect with this gradient
        painter.fillRect(rect, QBrush(grad))
        
        # Add distinct Hemispheric tint?
        # Top half
        top_rect = QRectF(scene_rect.left(), scene_rect.top(), scene_rect.width(), scene_rect.height()/2)
        grad_top = QLinearGradient(0, -400, 0, 0)
        c_top = QColor("#0ea5e9") # Sky Blue
        c_top.setAlpha(10)
        grad_top.setColorAt(0, c_top)
        grad_top.setColorAt(1, Qt.GlobalColor.transparent)
        painter.fillRect(top_rect, grad_top)
        
        # Bottom half
        bot_rect = QRectF(scene_rect.left(), 0, scene_rect.width(), scene_rect.height()/2)
        grad_bot = QLinearGradient(0, 400, 0, 0)
        c_bot = QColor("#f43f5e") # Rose Red
        c_bot.setAlpha(10)
        grad_bot.setColorAt(0, c_bot)
        grad_bot.setColorAt(1, Qt.GlobalColor.transparent)
        painter.fillRect(bot_rect, grad_bot)
        
    def drawForeground(self, painter, rect):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw Ouroboros Track
        pen = QPen(QColor("#334155"), 2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(0,0), self.track_radius, self.track_radius)
        
        # Draw Nexus Axis (130-131)
        # Assuming 1 is top (-90 deg). 130 is Bottom (+90 deg).
        painter.setPen(QPen(QColor("#475569"), 1, Qt.PenStyle.DashLine))
        painter.drawLine(QPointF(0, -self.track_radius), QPointF(0, self.track_radius))
        
        # Draw Cord
        p1 = self.self_orb.pos()
        p2 = self.conrune_orb.pos()
        painter.setPen(QPen(QColor("#f59e0b"), 2))
        painter.drawLine(p1, p2)

class TzolkinDynamisWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tzolkin Dynamis: The Constitution of Time")
        self.resize(1000, 900)
        
        self.service = TzolkinService()
        self.current_kin = 1
        
        self.layout = QVBoxLayout(self)
        
        # Header
        info_layout = QHBoxLayout()
        self.lbl_day = QLabel("Kin 1")
        self.lbl_day.setStyleSheet("font-size: 16pt; font-weight: bold; color: #e2e8f0;")
        info_layout.addWidget(self.lbl_day)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(1, 260)
        self.slider.setValue(1)
        self.slider.valueChanged.connect(self.on_slider_change)
        info_layout.addWidget(self.slider)
        
        self.btn_play = QPushButton("▶ Cycle")
        self.btn_play.clicked.connect(self.toggle_animation)
        info_layout.addWidget(self.btn_play)
        
        self.layout.addLayout(info_layout)
        
        # View
        self.scene = DynamisScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setStyleSheet("border: 0px;")
        self.layout.addWidget(self.view)
        
        # Side Trigrams (Static Reference)
        self.self_trigram = TrigramItem("000000", size=80, color=QColor("#0ea5e9"))
        self.self_trigram.setPos(-350, -300)
        self.scene.addItem(self.self_trigram)
        
        self.conrune_trigram = TrigramItem("000000", size=80, color=QColor("#f43f5e"))
        self.conrune_trigram.setPos(350, -300)
        self.scene.addItem(self.conrune_trigram)

        # Labels
        t1 = self.scene.addText("Self")
        t1.setDefaultTextColor(QColor("#94a3b8"))
        t1.setPos(-370, -240)
        t2 = self.scene.addText("Conrune")
        t2.setDefaultTextColor(QColor("#94a3b8"))
        t2.setPos(330, -240)

        self.timer = QTimer()
        self.timer.timeout.connect(self.advance_frame)
        self.is_playing = False
        
        self.update_positions()

    def on_slider_change(self, val):
        self.current_kin = val
        self.update_positions()
        
    def toggle_animation(self):
        if self.is_playing:
            self.timer.stop()
            self.btn_play.setText("▶ Cycle")
        else:
            self.timer.start(100)
            self.btn_play.setText("⏸ Pause")
        self.is_playing = not self.is_playing

    def advance_frame(self):
        k = self.current_kin + 1
        if k > 260: k = 1
        self.slider.setValue(k)

    def update_positions(self):
        kin = self.current_kin
        
        # Calculate Angle (Kin 1 @ -90 deg)
        angle_deg = -90 + (kin - 1) * (360/260)
        angle_rad = math.radians(angle_deg)
        r = self.scene.track_radius
        
        # Self Pos
        self.scene.self_orb.setPos(r * math.cos(angle_rad), r * math.sin(angle_rad))
        
        # Conrune Pos (261 - Kin)
        c_kin = 261 - kin
        if c_kin == 261: c_kin = 1
        c_angle_deg = -90 + (c_kin - 1) * (360/260)
        c_angle_rad = math.radians(c_angle_deg)
        self.scene.conrune_orb.setPos(r * math.cos(c_angle_rad), r * math.sin(c_angle_rad))
        
        # Data
        d = self.service.EPOCH + timedelta(days=kin-1)
        tz_date = self.service.from_gregorian(d)
        dit = tz_date.ditrune_ternary
        con_dit = self.service.get_conrune(dit)
        
        # Update Trigrams
        self.self_trigram.update_trigram(dit, 'SOLID')
        self.conrune_trigram.update_trigram(con_dit, 'SOLID')
        
        # Update Pillar Gauge (Center)
        # Needs Upper/Lower split and Tone
        upper, lower = self.service.get_trigrams(dit)
        self.scene.pillar_gauge.update_state(upper, lower, tz_date.tone)
        
        self.lbl_day.setText(f"Kin {kin} • {dit} • Tone {tz_date.tone}")
        self.scene.update()
