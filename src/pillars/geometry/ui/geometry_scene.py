"""Central QGraphicsScene implementation for the geometry pillar."""
from __future__ import annotations
import math
from typing import List, Optional, Tuple

from PyQt6.QtWidgets import QGraphicsScene, QGraphicsItem, QGraphicsSimpleTextItem, QGraphicsSceneMouseEvent, QGraphicsEllipseItem
from PyQt6.QtGui import QPen, QBrush, QColor, QPolygonF, QPainter, QTransform, QRadialGradient, QPainterPath
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal

from .primitives import (
    Bounds,
    CirclePrimitive,
    GeometryScenePayload,
    LabelPrimitive,
    LinePrimitive,
    PenStyle,
    PolygonPrimitive,
    Primitive,
    BooleanPrimitive
)




def _segment_intersection(p1: QPointF, p2: QPointF, p3: QPointF, p4: QPointF) -> Optional[QPointF]:
    """Calculate intersection of two line segments p1-p2 and p3-p4."""
    d = (p2.x() - p1.x()) * (p4.y() - p3.y()) - (p2.y() - p1.y()) * (p4.x() - p3.x())
    if d == 0:
        return None
    
    u = ((p3.x() - p1.x()) * (p4.y() - p3.y()) - (p3.y() - p1.y()) * (p4.x() - p3.x())) / d
    v = ((p3.x() - p1.x()) * (p2.y() - p1.y()) - (p3.y() - p1.y()) * (p2.x() - p1.x())) / d
    
    if 0 <= u <= 1 and 0 <= v <= 1:
        x = p1.x() + u * (p2.x() - p1.x())
        y = p1.y() + u * (p2.y() - p1.y())
        return QPointF(x, y)
    return None

def _polygon_centroid(points: List[Tuple[float, float]]) -> QPointF:
    """Calculate centroid of a polygon."""
    if not points:
        return QPointF(0, 0)
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    return QPointF(cx, cy)


def _shoelace_area(points: List[QPointF]) -> float:
    """Calculate polygon area using Shoelace formula."""
    n = len(points)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += points[i].x() * points[j].y()
        area -= points[j].x() * points[i].y()
    return abs(area) / 2.0


class GeometryScene(QGraphicsScene):
    """Shared graphics scene that can render any supported geometry shape."""
    
    measurementChanged = pyqtSignal(dict)
    measurementChanged = pyqtSignal(dict)
    dot_clicked = pyqtSignal(int, Qt.KeyboardModifier, Qt.MouseButton) # index, modifiers, button

    def __init__(self, parent=None):
        super().__init__(parent)
        self._payload: Optional[GeometryScenePayload] = None
        self._label_items: List[QGraphicsSimpleTextItem] = []
        self._axes_items: List[QGraphicsItem] = []
        self._vertex_highlight_items: List[QGraphicsItem] = []
        self._label_primitives: List[LabelPrimitive] = []
        self._temp_items: List[QGraphicsItem] = []

        # Measurement Customization State
        self._meas_font_size: float = 9.0
        self._meas_line_color: QColor = QColor(234, 88, 12) # Orange
        self._meas_text_color: QColor = QColor(0, 0, 0) # Black default
        self._meas_use_line_color_for_text: bool = False
        self._meas_show_area: bool = True
        
        self._last_meas_points: List[QPointF] = []
        self._last_meas_closed: bool = False

        self.axes_visible: bool = True
        self.labels_visible: bool = True

        # Format: (Background RGB, Text RGB, Axis RGB)
        self._themes = {
            "Daylight": ((248, 250, 252), (30, 41, 59), (148, 163, 184)),
            "Midnight": ((15, 23, 42), (226, 232, 240), (71, 85, 105)),
            "Slate": ((30, 41, 59), (241, 245, 249), (100, 116, 139)),
            "Pearl": ((255, 255, 255), (15, 23, 42), (148, 163, 184)),
        }
        self._theme_name = "Daylight"
        self._text_pen = QPen(QColor(30, 41, 59))
        self._axis_pen = QPen(QColor(148, 163, 184), 0)
        
        self.setBackgroundBrush(QColor(*self._themes[self._theme_name][0]))
        self.setSceneRect(-5, -5, 10, 10)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def set_payload(self, payload: Optional[GeometryScenePayload]):
        """Replace the scene content with the provided payload."""
        self._payload = payload
        self._rebuild_scene()

    def clear_payload(self):
        self._payload = None
        self._rebuild_scene()



    def set_axes_visible(self, visible: bool):
        if self.axes_visible != visible:
            self.axes_visible = visible
            self._refresh_axes()

    def set_labels_visible(self, visible: bool):
        if self.labels_visible != visible:
            self.labels_visible = visible
            self._refresh_labels()

    def set_vertex_highlights_visible(self, visible: bool):
        """Toggle visibility of vertex highlight dots."""
        if not self._vertex_highlight_items:
            self._create_vertex_highlights()
            
        for item in self._vertex_highlight_items:
            item.setVisible(visible)

    def apply_theme(self, theme: str):
        theme_data = self._themes.get(theme, self._themes["Daylight"])
        self._theme_name = theme if theme in self._themes else "Daylight"
        
        bg_rgb, text_rgb, axis_rgb = theme_data
        
        # Update Background
        self.setBackgroundBrush(QColor(*bg_rgb))
        
        # Update Pens
        self._text_pen = QPen(QColor(*text_rgb))
        self._axis_pen = QPen(QColor(*axis_rgb), 0)
        
        # Refresh Items
        self._refresh_labels()
        self._refresh_axes()
        
        self.update()

    def get_current_bounds(self) -> Optional[Bounds]:
        if not self._payload:
            return None
        if self._payload.bounds:
            return self._payload.bounds
        if self._payload.primitives:
            return self._derive_bounds(self._payload.primitives)
        return None

    def get_vertices(self) -> List[QPointF]:
        """Get all significant vertices from the current payload."""
        if not self._payload or not self._payload.primitives:
            return []
        
        points: List[QPointF] = []
        segments: List[Tuple[QPointF, QPointF]] = []

        # 1. Collect explicit vertices and segments
        for primitive in self._payload.primitives:
            if isinstance(primitive, PolygonPrimitive):
                poly_points = [QPointF(x, y) for x, y in primitive.points]
                points.extend(poly_points)
                # Add centroid
                points.append(_polygon_centroid(primitive.points))
                # Add segments
                for i in range(len(poly_points)):
                    segments.append((poly_points[i], poly_points[(i + 1) % len(poly_points)]))
                    
            elif isinstance(primitive, LinePrimitive):
                p1 = QPointF(*primitive.start)
                p2 = QPointF(*primitive.end)
                points.append(p1)
                points.append(p2)
                segments.append((p1, p2))
                
            elif isinstance(primitive, CirclePrimitive):
                cx, cy = primitive.center
                r = primitive.radius
                points.append(QPointF(cx, cy))
                points.append(QPointF(cx + r, cy))
                points.append(QPointF(cx - r, cy))
                points.append(QPointF(cx, cy + r))
                points.append(QPointF(cx, cy - r))

        # 2. Find intersections
        for i in range(len(segments)):
            for j in range(i + 1, len(segments)):
                s1 = segments[i]
                s2 = segments[j]
                intersection = _segment_intersection(s1[0], s1[1], s2[0], s2[1])
                if intersection:
                    points.append(intersection)
        
        # 3. Dedup (simple distance check or quantization)
        # Using quantization for robustness
        unique_points: List[QPointF] = []
        seen = set()
        
        for p in points:
            # Round to 3 decimal places for key
            key = (round(p.x(), 3), round(p.y(), 3))
            if key not in seen:
                seen.add(key)
                unique_points.append(p)
                
        return unique_points 

    def add_temporary_line(self, start: QPointF, end: QPointF, label: Optional[str] = None):
        """Legacy helper, redirected to new system or kept for simple 2-point compatibility."""
        # We can implement this via update_measurement_preview or keep as is.
        # Keeping as is for backward compat if needed, but we will likely transition to update_measurement_preview.
        self._temp_items.clear()
        self._add_temp_segment(start, end, label)

    def update_measurement_preview(self, points: List[QPointF], closed: bool = False):
        """Update the scene with the current multi-point measurement state."""
        self._last_meas_points = list(points)
        self._last_meas_closed = closed
        self.clear_temporary_items()
        
        if not points:
            return

        # 1. Draw Segments
        n = len(points)
        limit = n if closed else n - 1
        
        for i in range(limit):
            p1 = points[i]
            p2 = points[(i + 1) % n]
            dist = math.sqrt((p2.x() - p1.x())**2 + (p2.y() - p1.y())**2)
            self._add_temp_segment(p1, p2, f"{dist:.2f}")

        # 2. Draw Polygon Fill & Area if closed or enough points
        if n >= 3 and self._meas_show_area:
            # Draw semi-transparent fill
            poly = QPolygonF(points)
            brush = QBrush(QColor(self._meas_line_color.red(), self._meas_line_color.green(), self._meas_line_color.blue(), 40)) 
            pen = QPen(Qt.PenStyle.NoPen)
            
            poly_item = self.addPolygon(poly, pen, brush)
            poly_item.setZValue(9)
            self._temp_items.append(poly_item)
            
            # Calculate and show area ONLY if closed
            if closed:
                area = _shoelace_area(points)
                centroid = _polygon_centroid([(p.x(), p.y()) for p in points])
                
                # Create Area Label
                text = f"Area: {area:.2f}"
                text_item = QGraphicsSimpleTextItem(text)
                
                text_col = self._meas_line_color if self._meas_use_line_color_for_text else self._meas_text_color
                text_item.setBrush(QBrush(text_col)) 
                
                # Background for label
                font = text_item.font()
                font.setPointSizeF(self._meas_font_size + 1.0) # Slightly larger than segments
                font.setBold(True)
                text_item.setFont(font)
                
                rect = text_item.boundingRect()
                
                # Positioning
                text_item.setPos(centroid.x() - rect.width()/2, centroid.y() - rect.height()/2)
                text_item.setZValue(13)
                
                self.addItem(text_item)
                self._temp_items.append(text_item)

        # 3. Emit Stats
        perimeter = 0.0
        for i in range(len(points)):
            if i == len(points) - 1 and not closed:
                continue
            p1 = points[i]
            p2 = points[(i + 1) % len(points)]
            perimeter += math.sqrt((p2.x() - p1.x())**2 + (p2.y() - p1.y())**2)
            
        area = 0.0
        if n >= 3:
             area = _shoelace_area(points)
             
        self.measurementChanged.emit({
            "points": points,
            "perimeter": perimeter,
            "area": area,
            "closed": closed,
            "count": n
        })

    def _add_temp_segment(self, start: QPointF, end: QPointF, label: Optional[str]):
        """Helper to draw a single temp segment."""
        pen = QPen(self._meas_line_color, 2)
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setCosmetic(True)
        
        line_item = self.addLine(start.x(), start.y(), end.x(), end.y(), pen)
        line_item.setZValue(10)
        self._temp_items.append(line_item)
        
        if label:
            text_item = QGraphicsSimpleTextItem(label)
            text_col = self._meas_line_color if self._meas_use_line_color_for_text else self._meas_text_color
            text_item.setBrush(QBrush(text_col))
            text_item.setZValue(11)
            text_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
            font = text_item.font()
            font.setPointSizeF(self._meas_font_size)
            font.setBold(True)
            text_item.setFont(font)
            
            mid_x = (start.x() + end.x()) / 2
            mid_y = (start.y() + end.y()) / 2
            rect = text_item.boundingRect()
            text_item.setPos(mid_x - rect.width() / 2, mid_y - rect.height() / 2)
            
            self.addItem(text_item)
            self._temp_items.append(text_item) 

    def set_measurement_font_size(self, size: float):
        self._meas_font_size = size
        self.update_measurement_preview(self._last_meas_points, self._last_meas_closed)

    def set_measurement_line_color(self, color: QColor):
        self._meas_line_color = color
        self.update_measurement_preview(self._last_meas_points, self._last_meas_closed)
        
    def set_measurement_text_color(self, color: QColor):
        self._meas_text_color = color
        self.update_measurement_preview(self._last_meas_points, self._last_meas_closed)
        
    def set_measurement_show_area(self, enabled: bool):
        self._meas_show_area = enabled
        self.update_measurement_preview(self._last_meas_points, self._last_meas_closed)


    def clear_temporary_items(self):
        """Remove all temporary items from the scene."""
        for item in self._temp_items:
            scene = item.scene()
            if scene == self:
                self.removeItem(item)
        self._temp_items.clear()

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        # Process our custom click logic BEFORE calling super(), otherwise 
        # items with ItemIsSelectable will accept Left Clicks and prevent our logic.
        pos = event.scenePos()
        print(f"[DEBUG] Scene: Click at {pos}")
        
        # We must pass the view transform to itemAt for ItemIgnoresTransformations to work correctly!
        view_transform = QTransform()
        if self.views():
            view_transform = self.views()[0].transform()
            
        item = self.itemAt(pos, view_transform)
        if item:
            # Check for dot index in data(0)
            dot_index = item.data(0)
            print(f"[DEBUG] Scene: Item found. Data(0)={dot_index}, Type={type(item)}")
            if dot_index is not None:
                modifiers = event.modifiers()
                button = event.button()
                print(f"[DEBUG] Scene: Emitting dot_clicked(index={dot_index}, modifiers={modifiers}, button={button})")
                self.dot_clicked.emit(dot_index, modifiers, button)
        else:
            print("[DEBUG] Scene: No item found at click position.")
        
        # Call super() after our logic so default Qt behavior still works (e.g., item selection)
        super().mousePressEvent(event)

    def add_connection_line(self, start_pos: Tuple[float, float], end_pos: Tuple[float, float], pen: QPen):
        """Add a persistent connection line to the scene."""
        print(f"[DEBUG] Scene: Adding connection line from {start_pos} to {end_pos}")
        line_item = self.addLine(start_pos[0], start_pos[1], end_pos[0], end_pos[1], pen)
        line_item.setZValue(0.5) # Below dots (dots are at Z=2)
        # Dots are Z? CirclePrimitive doesn't set Z? Default is 0. labels are Z=2.
        # We should set dots to Z=1.
        
    def set_dot_z_index(self, z: float):
        # Helper to set z value for all dots?
        # Better: Set Z in _create_circle_items.
        pass

    def highlight_dots(self, indices: List[int], color: QColor):
        """Highlight specific dots by index."""
        # This requires iterating items and checking data(0).
        # Performance might be okay for < 1000 dots.
        brush = QBrush(color)
        pen = QPen(color.darker(150), 0) # Cosmetic pen (1px) to avoid scaling artifacts
        
        for item in self.items():
            idx = item.data(0)
            if idx in indices:
                if hasattr(item, 'setBrush'):
                    item.setBrush(brush)
                    item.setPen(pen)

    def set_dot_color(self, color: QColor):
        """Set the fill color for all dot items (EllipseItems)."""
        brush = QBrush(color)
        pen = QPen(color.darker(120), 0)
        for item in self.items():
            if isinstance(item, QGraphicsEllipseItem):
                item.setBrush(brush)
                item.setPen(pen)

    def set_text_color(self, color: QColor):
        """Set the color for all text labels."""
        for item in self.items():
            if isinstance(item, QGraphicsSimpleTextItem):
                item.setBrush(color)

    def get_dots_in_rect(self, rect: QRectF) -> List[int]:
        """Return list of dot indices whose centers fall within the given rectangle."""
        indices = []
        for item in self.items():
            if isinstance(item, QGraphicsEllipseItem):
                idx = item.data(0)
                if idx is not None:
                    # Check if the CENTER of the dot is within the rect, not just bounding box overlap
                    center = item.sceneBoundingRect().center()
                    if rect.contains(center):
                        indices.append(idx)
        return indices

    # ------------------------------------------------------------------
    # Rendering hooks
    # ------------------------------------------------------------------
    def drawBackground(self, painter: Optional[QPainter], rect: QRectF):  # pragma: no cover - Qt hook
        if painter is None:
            return

        super().drawBackground(painter, rect)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _rebuild_scene(self):
        self.blockSignals(True)
        self.clear()
        self.blockSignals(False)
        self._label_items.clear()
        self._label_items.clear()
        self._axes_items.clear()
        self._vertex_highlight_items.clear()
        self._temp_items.clear()  # Also clear temp items on rebuild
        self._label_primitives = []

        if not self._payload or not self._payload.primitives:
            self.setSceneRect(-5, -5, 10, 10)
            return

        bounds = self._payload.bounds or self._derive_bounds(self._payload.primitives)
        padded_bounds = bounds.padded(max(bounds.width, bounds.height) * 0.1)
        self.setSceneRect(
            padded_bounds.min_x,
            padded_bounds.min_y,
            padded_bounds.width,
            padded_bounds.height,
        )



        for primitive in self._payload.primitives:
            self._add_primitive(primitive)

        self._label_primitives = list(self._payload.labels)
        if self.labels_visible:
            self._label_items = self._create_label_items(self._label_primitives)

        if self.axes_visible:
            self._axes_items = self._create_axes(bounds)



    def _derive_bounds(self, primitives: List[Primitive]) -> Bounds:
        xs: List[float] = []
        ys: List[float] = []

        for primitive in primitives:
            if isinstance(primitive, CirclePrimitive):
                cx, cy = primitive.center
                r = abs(primitive.radius)
                xs.extend([cx - r, cx + r])
                ys.extend([cy - r, cy + r])
            elif isinstance(primitive, PolygonPrimitive):
                for px, py in primitive.points:
                    xs.append(px)
                    ys.append(py)
            elif isinstance(primitive, LinePrimitive):
                xs.extend([primitive.start[0], primitive.end[0]])
                ys.extend([primitive.start[1], primitive.end[1]])

        if not xs or not ys:
            return Bounds(-1, 1, -1, 1)

        return Bounds(min(xs), max(xs), min(ys), max(ys))

    def _add_primitive(self, primitive: Primitive):
        if isinstance(primitive, CirclePrimitive):
            self._add_circle(primitive)
        elif isinstance(primitive, PolygonPrimitive):
            self._add_polygon(primitive)
        elif isinstance(primitive, LinePrimitive):
            self._add_line(primitive)
        elif isinstance(primitive, BooleanPrimitive):
            self._add_boolean_primitive(primitive)

    def _add_boolean_primitive(self, primitive: BooleanPrimitive):
        path_a = self._primitive_to_path(primitive.shape_a)
        path_b = self._primitive_to_path(primitive.shape_b)
        
        if path_a.isEmpty() or path_b.isEmpty():
            return
            
        result_path = QPainterPath()
        if primitive.operation == "difference":
            result_path = path_a.subtracted(path_b)
        elif primitive.operation == "union":
            result_path = path_a.united(path_b)
        elif primitive.operation == "intersection":
            result_path = path_a.intersected(path_b)
            
        path_item = self.addPath(
            result_path,
            self._qt_pen(primitive.pen),
            self._qt_brush(primitive.brush)
        )
        path_item.setZValue(1)

    def _primitive_to_path(self, primitive: Primitive) -> QPainterPath:
        path = QPainterPath()
        if isinstance(primitive, CirclePrimitive):
            cx, cy = primitive.center
            r = primitive.radius
            # QPainterPath.addEllipse takes rect or center+radii
            path.addEllipse(QPointF(cx, cy), r, r)
        elif isinstance(primitive, PolygonPrimitive):
            points = [QPointF(x, y) for x, y in primitive.points]
            path.addPolygon(QPolygonF(points))
        return path

    def _add_circle(self, primitive: CirclePrimitive):
        cx, cy = primitive.center
        radius = primitive.radius
        diameter = radius * 2
        
        # Determined brush style
        brush = self._qt_brush(primitive.brush)
        if primitive.metadata and primitive.metadata.get('style') == 'sphere' and primitive.brush.enabled:
            # Create a radial gradient for 3D sphere effect
            base_color = QColor(*primitive.brush.color)
            gradient = QRadialGradient(cx - radius * 0.3, cy - radius * 0.3, radius * 1.5)
            gradient.setColorAt(0.0, QColor(255, 255, 255, 180))  # Specular highlight
            gradient.setColorAt(0.3, base_color)
            gradient.setColorAt(1.0, base_color.darker(150))      # Shadow
            brush = QBrush(gradient)

        ellipse = self.addEllipse(
            cx - radius,
            cy - radius,
            diameter,
            diameter,
            self._qt_pen(primitive.pen),
            brush,
        )
        if ellipse is not None:
            ellipse.setZValue(2.0) # Dots above lines (Z=1.5)
            if primitive.metadata and 'index' in primitive.metadata:
                ellipse.setData(0, primitive.metadata['index'])
            ellipse.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

    def _add_polygon(self, primitive: PolygonPrimitive):
        points = [QPointF(x, y) for x, y in primitive.points]
        polygon = QPolygonF(points)
        item = self.addPolygon(polygon, self._qt_pen(primitive.pen), self._qt_brush(primitive.brush))
        if item is not None:
            item.setZValue(0)

    def _add_line(self, primitive: LinePrimitive):
        line = self.addLine(
            primitive.start[0],
            primitive.start[1],
            primitive.end[0],
            primitive.end[1],
            self._qt_pen(primitive.pen),
        )
        if line is not None:
            line.setZValue(1)

    def _create_label_items(self, labels: List[LabelPrimitive]) -> List[QGraphicsSimpleTextItem]:
        from collections import defaultdict
        
        label_items: List[QGraphicsSimpleTextItem] = []
        groups = defaultdict(list)
        
        # 1. Create items and group by quantized position
        for label in labels:
            item = QGraphicsSimpleTextItem(label.text)
            item.setBrush(self._text_pen.color())
            item.setZValue(2)
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
            font = item.font()
            font.setPointSizeF(8.0)
            item.setFont(font)
            
            if label.metadata and 'index' in label.metadata:
                item.setData(0, label.metadata['index'])
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
            
            # Key: quantized position for grouping
            key = (round(label.position[0], 3), round(label.position[1], 3))
            groups[key].append((item, label))

        # 2. Process groups and stack if needed
        for pos_key, group in groups.items():
            total_height = sum(item.boundingRect().height() for item, _ in group)
            # Center the entire stack
            current_y_offset = -total_height / 2 if len(group) > 1 else 0
            
            for item, label in group:
                item.setPos(label.position[0], label.position[1])
                rect = item.boundingRect()
                w = rect.width()
                h = rect.height()
                
                off_x = -w / 2 if label.align_center else 0
                
                if len(group) > 1:
                    # Stack mode: Vertical list, centered on point
                    off_y = current_y_offset
                    # Check if font size changed, item bounds might change.
                    # BoundingRect is in local coords (pixels).
                    current_y_offset += h
                else:
                    # Single mode: Respect align_center
                    off_y = -h / 2 if label.align_center else 0
                
                item.setTransform(QTransform().translate(off_x, off_y))
                self.addItem(item)
                label_items.append(item)
                
        return label_items

    def update_label_layout(self, view_transform: QTransform):
        """
        Dynamically adjust label positions to avoid overlaps in screen space (pixels).
        Usage: Called by the view on zoom/resize.
        """
        if not self._label_items:
            return

        # 1. Calculate screen positions and bounding boxes
        # ItemIgnoresTransformations: position is scene, but size is pixels.
        # But wait, QGraphicsScene.views()[0].mapFromScene? No, we have the transform.
        # Project anchor point:
        
        # Sort by Y then X to process top-down
        # We need a list of (item, screen_pos_y, screen_pos_x, height)
        
        projections = []
        for item in self._label_items:
            scene_pos = item.pos() # Anchor
            screen_pos = view_transform.map(scene_pos)
            rect = item.boundingRect() # in pixels
            projections.append({
                'item': item,
                'screen_x': screen_pos.x(),
                'screen_y': screen_pos.y(),
                'width': rect.width(),
                'height': rect.height(),
                # Store original translation if needed? No, we reset transform.
                'align_center': True # Assuming all for now or check item transform?
            })

        # Sort by screen Y
        projections.sort(key=lambda p: (p['screen_y'], p['screen_x']))
        
        # Group by screen proximity


        # Let's use a simpler group-by-screen-proximity approach
        groups = []
        threshold_x = 20.0 # pixels
        threshold_y = 20.0 # pixels
        
        # Determine strict groups
        sorted_p = sorted(projections, key=lambda i: (i['screen_y'], i['screen_x']))
        
        active_groups = [] # List of [ {'sy':..., 'sx':...} ]
        
        for p in sorted_p:
            placed = False
            for group in active_groups:
                leader = group[0]
                if abs(p['screen_x'] - leader['screen_x']) < threshold_x and \
                   abs(p['screen_y'] - leader['screen_y']) < threshold_y:
                    group.append(p)
                    placed = True
                    break
            if not placed:
                active_groups.append([p])

                
        # Now layout groups
        for group in active_groups:
            if not group: continue
            
            total_h = sum(g['height'] for g in group)
            start_y_offset = -total_h / 2
            
            current_off = start_y_offset
            for p in group:
                item = p['item']
                h = p['height']
                w = p['width']
                
                # Apply offset to the base anchor
                # We need to set the item's transform.
                # Base anchor is still at scene_pos.
                # Item draws at screen_pos.
                
                # Item transform is applied in item local space (pixels)
                # Standard centering: translate(-w/2, -h/2)
                # Stacked centering: translate(-w/2, current_off)
                
                # We assume align_center=True for all labels for now
                item.setTransform(QTransform().translate(-w/2, current_off))
                current_off += h


    def _create_axes(self, bounds: Bounds) -> List[QGraphicsItem]:
        span = max(bounds.width, bounds.height) * 0.7
        pen = self._axis_pen
        axes: List[QGraphicsItem] = []
        horizontal = self.addLine(-span, 0, span, 0, pen)
        vertical = self.addLine(0, -span, 0, span, pen)
        for item in (horizontal, vertical):
            if item is not None:
                item.setZValue(-1)
                axes.append(item)
        return axes

    def _refresh_labels(self):
        if self.labels_visible:
            if not self._label_items and self._label_primitives:
                self._label_items = self._create_label_items(self._label_primitives)
            for item in self._label_items:
                item.setVisible(True)
        else:
            for item in self._label_items:
                item.setVisible(False)

    def _refresh_axes(self):
        if self.axes_visible:
            if not self._axes_items and self._payload and (self._payload.bounds or self._payload.primitives):
                bounds = self._payload.bounds or self._derive_bounds(self._payload.primitives)
                self._axes_items = self._create_axes(bounds)
            for item in self._axes_items:
                item.setVisible(True)
        else:
            for item in self._axes_items:
                item.setVisible(False)

    def _create_vertex_highlights(self):
        """Create highlight dots for all vertices."""
        self._vertex_highlight_items.clear()
        vertices = self.get_vertices()
        
        pen = QPen(Qt.GlobalColor.black, 0)
        brush = QBrush(Qt.GlobalColor.black)
        
        for v in vertices:
            # Create a small circle item that ignores transformations (constant screen size)
            # However, QGraphicsEllipseItem doesn't support ItemIgnoresTransformations nicely with centering.
            # We'll use a small fixed radius in scene coordinates, or just standard item.
            # Better: Use a small rect centered on point.
            
            # Let's try constant size using a custom drawing or just small scene-units.
            # Issue with small scene units: Zooming in makes them huge.
            # We will use ItemIgnoresTransformations on a small rect.
            
            dot_size = 6.0
            rect = QRectF(-dot_size/2, -dot_size/2, dot_size, dot_size)
            item = self.addEllipse(rect, pen, brush)
            item.setPos(v)
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
            item.setZValue(20) # On top of everything
            item.setVisible(False) # Hidden by default
            self._vertex_highlight_items.append(item)

    @staticmethod
    def _qt_pen(style: PenStyle) -> QPen:
        color = QColor(*style.color)
        pen = QPen(color, style.width)
        if style.dashed:
            pen.setStyle(Qt.PenStyle.DashLine)
        pen.setCosmetic(True)
        return pen

    @staticmethod
    def _qt_brush(style) -> QBrush:
        if not style.enabled:
            return QBrush(Qt.BrushStyle.NoBrush)
        return QBrush(QColor(*style.color))


__all__ = ["GeometryScene"]
