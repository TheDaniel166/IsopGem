
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsObject, QGraphicsPathItem
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QPainter, QBrush, QPen, QColor, QRadialGradient, QFont, QPainterPath, QPainterPathStroker

class MindscapeNodeItem(QGraphicsObject):
    """
    The Visual Representation of a Thought.
    Uses QGraphicsObject to allow for Property Animations (pos, opacity, scale).
    """
    clicked = pyqtSignal(int)  # Emits node_id on click
    position_changed = pyqtSignal()  # Emits when pos changes (for edges)

    def __init__(self, node_id, title, node_type="concept", icon=None, theme=None):
        super().__init__()
        self.node_id = node_id
        self.title_text = title
        self.node_type = node_type
        self.icon = icon
        self.theme = theme # GraphTheme instance
        
        self.width = 160
        self.height = 80
        # Resolve initial color from theme if available, else hardcoded fallback
        self._default_color = self._resolve_theme_color(node_type)
        self._style = {} # Custom Appearance
        self._selected = False
        
        # Accept hover events for glow effect
        self.setAcceptHoverEvents(True)
        # CRITICAL: This flag is required for ItemPositionChange/HasChanged to fire!
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self._hovered = False

    def _resolve_theme_color(self, ntype):
        if not self.theme:
            return QColor("#64748b")
        key_map = {
            "concept": "node_concept",
            "system": "node_system",
            "jump": "node_jump",
            "document": "node_document"
        }
        return self.theme.get_color(key_map.get(ntype, "node_default"))

    def set_style(self, style: dict):
        """Apply custom styling from 'appearance' JSON."""
        self._style = style
        self.update()

    def set_title(self, title: str):
        """Update displayed title."""
        self.title_text = title
        self.update()

    def boundingRect(self):
        # Add padding for glow/shadow to prevent trails
        return QRectF(-self.width/2 - 20, -self.height/2 - 20, self.width + 40, self.height + 40)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.position_changed.emit()
        return super().itemChange(change, value)

    def paint(self, painter, option, widget):
        # Style Overrides OR Theme Defaults
        style_shape = self._style.get("shape", "capsule")
        color = QColor(self._style.get("color_override")) if self._style.get("color_override") else self._default_color
        
        # Border Params
        border_width = int(self._style.get("borderWidth", 0))
        border_color_hex = self._style.get("borderColor")
        border_style = self._style.get("borderStyle", "none")
        
        # Adjusted rect for painting the actual body (excluding padding)
        rect = QRectF(-self.width/2, -self.height/2, self.width, self.height)
        
        # Get Shape Path
        path = self._get_shape_path(rect, style_shape)
        
        # 1. Glow Effect (Selection/Hover) overrides everything to show interaction state
        if self._hovered or self._selected:
            glow_path = self._get_shape_path(rect.adjusted(-5, -5, 5, 5), style_shape)
            glow_col = self.theme.get_color("glow_selected") if self._selected else self.theme.get_color("glow_hover")
            glow_col.setAlpha(40)
            painter.fillPath(glow_path, glow_col)

        # 2. Main Body (Dark Glass Gradient)
        grad = QRadialGradient(0, 0, self.width)
        # Using theme colors mixed with base color
        start_col = self.theme.get_color("node_gradient_start") if self.theme else QColor(40,40,50)
        end_col = self.theme.get_color("node_gradient_end") if self.theme else QColor(10,10,20)
        
        # Tint with node color
        start_col = QColor(start_col) # Copy
        start_col.setRed(int((start_col.red() + color.red())/2))
        start_col.setGreen(int((start_col.green() + color.green())/2))
        start_col.setBlue(int((start_col.blue() + color.blue())/2))
        start_col.setAlpha(230)
        
        end_col = QColor(end_col)
        end_col.setRed(int((end_col.red() + color.red()/4))) 
        end_col.setGreen(int((end_col.green() + color.green()/4)))
        end_col.setBlue(int((end_col.blue() + color.blue()/4)))
        end_col.setAlpha(255)

        grad.setColorAt(0, start_col)
        grad.setColorAt(1, end_col)
        
        painter.setBrush(QBrush(grad))
        
        # 3. Stroke (Border)
        pen = QPen(Qt.PenStyle.NoPen)
        
        # Custom Border Logic
        if border_style != "none" and border_width > 0:
            b_color = QColor(border_color_hex) if border_color_hex else Qt.GlobalColor.white
            pen = QPen(b_color, border_width)
            
            if border_style == "dashed":
                 pen.setStyle(Qt.PenStyle.DashLine)
            elif border_style == "dotted":
                 pen.setStyle(Qt.PenStyle.DotLine)
            else:
                 pen.setStyle(Qt.PenStyle.SolidLine)
        elif self._selected:
             # Default Selection Stroke if no custom border
             pen = QPen(self.theme.get_color("glow_selected") if self.theme else Qt.GlobalColor.white, 2)
             
        painter.setPen(pen)
        painter.drawPath(path)
        
        # 4. Text
        text_color_override = self._style.get("textColor")
        text_color = QColor(text_color_override) if text_color_override else self.theme.get_color("text_main")
        
        painter.setPen(text_color)
        
        # Font Customization
        font_family = self._style.get("fontFamily")
        font_size = self._style.get("fontSize")
        
        base_font = self.theme.get_font("bold" if self._selected else "body")
        if font_family:
            base_font.setFamily(font_family)
        if font_size:
            base_font.setPointSize(int(font_size))
            
        painter.setFont(base_font)
        
        text_rect = self._get_text_rect(rect, style_shape)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, self.title_text)

    def shape(self):
        """
        Return the precise shape path for collision detection.
        This fixes the issue where the large bounding rect (for text) blocks clicks on edges.
        """
        # Recalculate rect as in paint()
        rect = QRectF(-self.width/2, -self.height/2, self.width, self.height)
        style_shape = self._style.get("shape", "capsule")
        return self._get_shape_path(rect, style_shape)

    def _get_shape_path(self, rect: QRectF, shape: str) -> QPainterPath:
        path = QPainterPath()
        
        if shape == "circle":
            # For "Orb", let's use a circle constrained by height to avoid stretching
            # Or just an ellipse if that's preferred? Let's use Ellipse for container.
            path.addEllipse(rect)
        elif shape == "diamond":
            path.moveTo(rect.center().x(), rect.top())
            path.lineTo(rect.right(), rect.center().y())
            path.lineTo(rect.center().x(), rect.bottom())
            path.lineTo(rect.left(), rect.center().y())
            path.closeSubpath()
        elif shape == "hexagon":
            # Flat-topped hexagon
            w = rect.width()
            h = rect.height()
            x = rect.x()
            y = rect.y()
            offset = w * 0.15 # 15% offset for corners
            
            path.moveTo(x + offset, y)
            path.lineTo(x + w - offset, y)
            path.lineTo(x + w, y + h/2)
            path.lineTo(x + w - offset, y + h)
            path.lineTo(x + offset, y + h)
            path.lineTo(x, y + h/2)
            path.closeSubpath()
        elif shape == "triangle_up":
            path.moveTo(rect.center().x(), rect.top())
            path.lineTo(rect.right(), rect.bottom())
            path.lineTo(rect.left(), rect.bottom())
            path.closeSubpath()
        elif shape == "triangle_down":
            path.moveTo(rect.left(), rect.top())
            path.lineTo(rect.right(), rect.top())
            path.lineTo(rect.center().x(), rect.bottom())
            path.closeSubpath()
        elif shape == "cartouche":
            # Rounded top, flat bottom bar? Or just standard hierarchy cartouche (Rounded Rect)
            # "Oval with a flat bar at the bottom"
            # Draw standard capsule/oval but add a line/rect at bottom? 
            # Let's interpret as: Top 80% is oval, bottom 20% is a flat base
            path.addRoundedRect(rect, 15, 15) # Fallback to rounded rect structure for now
            # To do distinct bottom bar, we'd need complex path. 
            # Let's try: Rounded Rect but with a line drawn differently?
            # Simplify to RoundedRect for "Entity" look, maybe sharper corners?
            # Let's stick to Rounded Rect with corner radius 10 (default is 10)
            # Actually default capsule implies FULL radius (semicircle ends).
            # So 'capsule' below changes to correct capsule logic.
            # 'cartouche' will be the rounded rect we had before.
            path.addRoundedRect(rect, 10, 10)
        elif shape == "document":
            # "File" Look: Rectangle with small folded corner (top-right)
            # But simple version: Sharp Rectangle with small rounding
            path.addRoundedRect(rect, 3, 3)
        else: # capsule (Default)
            # Semicircle ends
            radius = rect.height() / 2
            path.addRoundedRect(rect, radius, radius)
            
        return path

    def _get_text_rect(self, rect: QRectF, shape: str) -> QRectF:
        """Returns a smaller rect for text to ensure it fits inside the shape."""
        if shape == "diamond":
            # Diamond has very little space in corners. Use central 60%
            w = rect.width() * 0.6
            h = rect.height() * 0.6
            return QRectF(rect.center().x() - w/2, rect.center().y() - h/2, w, h)
        elif shape == "triangle_up":
            # Shift text down
            w = rect.width() * 0.6
            h = rect.height() * 0.5
            return QRectF(rect.center().x() - w/2, rect.center().y(), w, h)
        elif shape == "triangle_down":
            # Shift text up
            w = rect.width() * 0.6
            h = rect.height() * 0.5
            return QRectF(rect.center().x() - w/2, rect.top() + h*0.2, w, h)
        elif shape == "hexagon":
            return rect.adjusted(10, 5, -10, -5)
        elif shape == "circle":
             # Ellipse: keep away from edges
             w = rect.width() * 0.75
             h = rect.height() * 0.75
             return QRectF(rect.center().x() - w/2, rect.center().y() - h/2, w, h)
             
        return rect.adjusted(5, 0, -5, 0) # Default padding

    def mousePressEvent(self, event):
        self.clicked.emit(self.node_id)
        super().mousePressEvent(event)

    def hoverEnterEvent(self, event):
        self._hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self._hovered = False
        self.update()
        super().hoverLeaveEvent(event)

    def _get_type_color(self, ntype):
        # Fallback for when theme is not present (although it should be)
        return QColor("#64748b")


class MindscapeEdgeItem(QGraphicsPathItem):
    """
    A connection between two thoughts.
    Updates automatically when source or target moves.
    """
    def __init__(self, edge_id: int, source_item: MindscapeNodeItem, target_item: MindscapeNodeItem, relation_type="parent", theme=None):
        super().__init__()
        self.edge_id = edge_id # For inspection
        self.source = source_item
        self.target = target_item
        self.relation_type = relation_type
        self.theme = theme
        self._style = {}
        
        # Initial Paint
        self.update_path()
        self._apply_style()
            
        self.setZValue(-1) # Behind nodes
        
    def set_style(self, style: dict):
        self._style = style
        self._apply_style()
        self.update()
        
    def _apply_style(self):
        # Styling Logic
        color_hex = self._style.get("color")
        width = int(self._style.get("width", 2))
        
        # Line Style (Solid, Dashed, Dotted)
        style_str = self._style.get("style", "solid").lower()
        is_dashed = style_str == "dashed" or self.relation_type == "jump"
        
        if color_hex:
            color = QColor(color_hex)
        else:
            # Theme Colors
            if self.relation_type == "jump":
                 color = self.theme.get_color("edge_jump") if self.theme else QColor(130, 130, 210, 180)
            else:
                 color = self.theme.get_color("edge_parent") if self.theme else QColor(100, 160, 210, 200)
                 
        pen = QPen(color, width)
        
        if style_str == "dashed":
            pen.setStyle(Qt.PenStyle.DashLine)
        elif style_str == "dotted":
            pen.setStyle(Qt.PenStyle.DotLine)
        elif is_dashed: # Fallback to jump default
            pen.setStyle(Qt.PenStyle.DashLine)
        else:
            pen.setStyle(Qt.PenStyle.SolidLine)
            
        self.setPen(pen)

    def shape(self):
        """Override collision shape for easier clicking."""
        path = QPainterPath()
        if self.path().isEmpty():
            return path
            
        # Create a wider stroker for hit detection
        stroker = QPainterPathStroker()
        stroker.setWidth(10) # 10px hit area
        return stroker.createStroke(self.path())

    def update_path(self):
        if not self.source.scene() or not self.target.scene():
            return
            
        # Ray-Cast Anchoring: "Sliding" ports that always face the target
        # Use scenePos to be safe
        source_pos = self.source.scenePos()
        target_pos = self.target.scenePos()

        # Calculate in SCENE coordinates
        start_scene = self.get_ray_cast_point(self.source, target_pos)
        end_scene = self.get_ray_cast_point(self.target, source_pos)
        
        # Convert to LOCAL coordinates for drawing (Crucial Fix)
        # If EdgeItem is at (0,0), this is identity, but guarantees correctness if it moves.
        self.start_point = self.mapFromScene(start_scene)
        self.end_point = self.mapFromScene(end_scene)
        
        start = self.start_point
        end = self.end_point
        
        path = QPainterPath()
        path.moveTo(start)
        
        dx = end.x() - start.x()
        dy = end.y() - start.y()

        # Geometric S-Curve
        if abs(dy) > abs(dx) and self.relation_type != "jump":
            ctrl1 = QPointF(start.x(), start.y() + dy * 0.5)
            ctrl2 = QPointF(end.x(), end.y() - dy * 0.5)
        else:
            ctrl1 = QPointF(start.x() + dx * 0.5, start.y())
            ctrl2 = QPointF(end.x() - dx * 0.5, end.y())
            
        path.cubicTo(ctrl1, ctrl2, end)
        self.setPath(path)

    def get_ray_cast_point(self, node_item, target_pos):
        """
        Calculates the intersection of the line (NodeCenter -> Target) with the Node's Bounding Box.
        Allows the connection to 'slide' along the edge smoothly.
        """
        center = node_item.scenePos()
        # Use actual visual size (200x100) or whatever is defined
        w = node_item.width / 2.0
        h = node_item.height / 2.0
        
        dx = target_pos.x() - center.x()
        dy = target_pos.y() - center.y()
        
        if dx == 0 and dy == 0:
            return center

        scale_x = abs(w / dx) if dx != 0 else 99999
        scale_y = abs(h / dy) if dy != 0 else 99999
        
        scale = min(scale_x, scale_y)
        
        return QPointF(center.x() + dx * scale, center.y() + dy * scale)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        super().paint(painter, option, widget)
