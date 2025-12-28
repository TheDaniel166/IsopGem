"""Shape items for the Rich Text Editor overlay."""
from PyQt6.QtWidgets import (
    QGraphicsItem, QGraphicsRectItem, QGraphicsEllipseItem,
    QGraphicsLineItem, QGraphicsPolygonItem, QGraphicsPathItem,
    QStyleOptionGraphicsItem, QWidget, QGraphicsSceneMouseEvent
)
from PyQt6.QtCore import Qt, QRectF, QPointF, QLineF
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QPolygonF, QPainterPath,
    QCursor
)
from enum import Enum
from typing import Optional
import math


class HandlePosition(Enum):
    """Positions for resize handles."""
    TOP_LEFT = 0
    TOP = 1
    TOP_RIGHT = 2
    RIGHT = 3
    BOTTOM_RIGHT = 4
    BOTTOM = 5
    BOTTOM_LEFT = 6
    LEFT = 7


class ResizeHandle(QGraphicsRectItem):
    """A resize handle for shape items."""
    
    HANDLE_SIZE = 8
    
    def __init__(self, position: HandlePosition, parent: QGraphicsItem):
        """
          init   logic.
        
        Args:
            position: Description of position.
            parent: Description of parent.
        
        """
        super().__init__(-self.HANDLE_SIZE/2, -self.HANDLE_SIZE/2, 
                         self.HANDLE_SIZE, self.HANDLE_SIZE, parent)
        self.position = position
        self.setBrush(QBrush(QColor("#2563eb")))
        self.setPen(QPen(QColor("#ffffff"), 1))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setAcceptHoverEvents(True)
        self._set_cursor()
    
    def _set_cursor(self):
        """Set appropriate cursor for this handle position."""
        cursors = {
            HandlePosition.TOP_LEFT: Qt.CursorShape.SizeFDiagCursor,
            HandlePosition.TOP_RIGHT: Qt.CursorShape.SizeBDiagCursor,
            HandlePosition.BOTTOM_LEFT: Qt.CursorShape.SizeBDiagCursor,
            HandlePosition.BOTTOM_RIGHT: Qt.CursorShape.SizeFDiagCursor,
            HandlePosition.TOP: Qt.CursorShape.SizeVerCursor,
            HandlePosition.BOTTOM: Qt.CursorShape.SizeVerCursor,
            HandlePosition.LEFT: Qt.CursorShape.SizeHorCursor,
            HandlePosition.RIGHT: Qt.CursorShape.SizeHorCursor,
        }
        self.setCursor(cursors.get(self.position, Qt.CursorShape.ArrowCursor))


class BaseShapeItem(QGraphicsItem):
    """Base class for all shape items with resize handles."""
    
    MIN_SIZE = 20
    
    def __init__(self, x: float, y: float, width: float, height: float):
        """
          init   logic.
        
        Args:
            x: Description of x.
            y: Description of y.
            width: Description of width.
            height: Description of height.
        
        """
        super().__init__()
        self._rect = QRectF(0, 0, width, height)
        self.setPos(x, y)
        
        # Properties
        self._fill_color = QColor("#dbeafe")
        self._stroke_color = QColor("#2563eb")
        self._stroke_width = 2
        
        # Interaction flags
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        
        # Resize handles
        self._handles: list[ResizeHandle] = []
        self._active_handle: Optional[ResizeHandle] = None
        self._resize_start_rect: Optional[QRectF] = None
        self._resize_start_pos: Optional[QPointF] = None
        self._resize_start_item_pos: Optional[QPointF] = None  # Store item position at resize start
        self._create_handles()
        self._update_handles()
    
    def _create_handles(self):
        """Create resize handles for all positions."""
        for pos in HandlePosition:
            handle = ResizeHandle(pos, self)
            handle.setVisible(False)
            self._handles.append(handle)
    
    def _update_handles(self):
        """Update handle positions based on current rect."""
        positions = {
            HandlePosition.TOP_LEFT: QPointF(0, 0),
            HandlePosition.TOP: QPointF(self._rect.width() / 2, 0),
            HandlePosition.TOP_RIGHT: QPointF(self._rect.width(), 0),
            HandlePosition.RIGHT: QPointF(self._rect.width(), self._rect.height() / 2),
            HandlePosition.BOTTOM_RIGHT: QPointF(self._rect.width(), self._rect.height()),
            HandlePosition.BOTTOM: QPointF(self._rect.width() / 2, self._rect.height()),
            HandlePosition.BOTTOM_LEFT: QPointF(0, self._rect.height()),
            HandlePosition.LEFT: QPointF(0, self._rect.height() / 2),
        }
        for handle in self._handles:
            handle.setPos(positions[handle.position])
    
    def boundingRect(self) -> QRectF:
        """Return the bounding rectangle."""
        pad = self._stroke_width / 2
        return self._rect.adjusted(-pad, -pad, pad, pad)
    
    def itemChange(self, change, value):
        """Handle item changes."""
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            for handle in self._handles:
                handle.setVisible(bool(value))
        return super().itemChange(change, value)
    
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        """Handle mouse press for resize."""
        # Check if clicking on a handle
        for handle in self._handles:
            if handle.contains(handle.mapFromScene(event.scenePos())):
                self._active_handle = handle
                self._resize_start_rect = QRectF(self._rect)
                self._resize_start_pos = event.scenePos()
                self._resize_start_item_pos = self.pos()  # Store item position
                event.accept()
                return
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        """Handle mouse move for resize."""
        if self._active_handle and self._resize_start_rect and self._resize_start_pos and self._resize_start_item_pos:
            delta = event.scenePos() - self._resize_start_pos
            new_rect = QRectF(self._resize_start_rect)
            
            # Apply resize based on handle position
            h = self._active_handle.position
            if h in (HandlePosition.TOP_LEFT, HandlePosition.LEFT, HandlePosition.BOTTOM_LEFT):
                new_rect.setLeft(new_rect.left() + delta.x())
            if h in (HandlePosition.TOP_RIGHT, HandlePosition.RIGHT, HandlePosition.BOTTOM_RIGHT):
                new_rect.setRight(new_rect.right() + delta.x())
            if h in (HandlePosition.TOP_LEFT, HandlePosition.TOP, HandlePosition.TOP_RIGHT):
                new_rect.setTop(new_rect.top() + delta.y())
            if h in (HandlePosition.BOTTOM_LEFT, HandlePosition.BOTTOM, HandlePosition.BOTTOM_RIGHT):
                new_rect.setBottom(new_rect.bottom() + delta.y())
            
            # Normalize and apply minimum size
            new_rect = new_rect.normalized()
            if new_rect.width() < self.MIN_SIZE:
                new_rect.setWidth(self.MIN_SIZE)
            if new_rect.height() < self.MIN_SIZE:
                new_rect.setHeight(self.MIN_SIZE)
            
            # Update geometry using starting position as reference
            self.prepareGeometryChange()
            self._rect = QRectF(0, 0, new_rect.width(), new_rect.height())
            self.setPos(self._resize_start_item_pos.x() + new_rect.x(), 
                       self._resize_start_item_pos.y() + new_rect.y())
            self._update_handles()
            event.accept()
            return
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        """Handle mouse release."""
        self._active_handle = None
        self._resize_start_rect = None
        self._resize_start_pos = None
        self._resize_start_item_pos = None
        super().mouseReleaseEvent(event)
    
    def contextMenuEvent(self, event):
        """Show right-click context menu."""
        from PyQt6.QtWidgets import QMenu, QColorDialog, QInputDialog, QWidgetAction, QSlider, QLabel, QHBoxLayout, QWidget
        from PyQt6.QtCore import Qt
        
        menu = QMenu()
        
        # Fill Color submenu
        fill_menu = menu.addMenu("Fill Color")
        fill_colors = [
            ("Blue", "#dbeafe"),
            ("Green", "#dcfce7"),
            ("Yellow", "#fef3c7"),
            ("Red", "#fecaca"),
            ("Purple", "#f3e8ff"),
            ("Gray", "#f3f4f6"),
            ("White", "#ffffff"),
            ("Transparent", "transparent"),
        ]
        for name, color in fill_colors:
            action = fill_menu.addAction(name)
            if color == "transparent":
                action.triggered.connect(lambda checked, c=QColor(0, 0, 0, 0): self._set_fill_color(c))
            else:
                action.triggered.connect(lambda checked, c=QColor(color): self._set_fill_color(c))
        fill_menu.addSeparator()
        custom_fill = fill_menu.addAction("Custom...")
        custom_fill.triggered.connect(self._choose_fill_color)
        
        # Stroke Color submenu
        stroke_menu = menu.addMenu("Stroke Color")
        stroke_colors = [
            ("Blue", "#2563eb"),
            ("Green", "#16a34a"),
            ("Yellow", "#ca8a04"),
            ("Red", "#dc2626"),
            ("Purple", "#9333ea"),
            ("Black", "#000000"),
            ("Gray", "#6b7280"),
        ]
        for name, color in stroke_colors:
            action = stroke_menu.addAction(name)
            action.triggered.connect(lambda checked, c=QColor(color): self._set_stroke_color(c))
        stroke_menu.addSeparator()
        custom_stroke = stroke_menu.addAction("Custom...")
        custom_stroke.triggered.connect(self._choose_stroke_color)
        
        # Stroke Width submenu
        width_menu = menu.addMenu("Stroke Width")
        for w in [1, 2, 3, 4, 5, 6, 8, 10]:
            action = width_menu.addAction(f"{w}px")
            action.setCheckable(True)
            action.setChecked(self._stroke_width == w)
            action.triggered.connect(lambda checked, width=w: self._set_stroke_width(width))
        
        menu.addSeparator()
        
        # Z-Order
        bring_front = menu.addAction("Bring to Front")
        bring_front.triggered.connect(self._bring_to_front)
        
        send_back = menu.addAction("Send to Back")
        send_back.triggered.connect(self._send_to_back)
        
        menu.addSeparator()
        
        # Duplicate
        duplicate_action = menu.addAction("Duplicate")
        duplicate_action.triggered.connect(self._duplicate)
        
        # Delete
        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(self._delete)
        
        menu.exec(event.screenPos())
    
    def _set_fill_color(self, color: QColor):
        self._fill_color = color
        self.update()
    
    def _set_stroke_color(self, color: QColor):
        self._stroke_color = color
        self.update()
    
    def _set_stroke_width(self, width: int):
        self._stroke_width = width
        self.update()
    
    def _choose_fill_color(self):
        from PyQt6.QtWidgets import QColorDialog
        color = QColorDialog.getColor(
            self._fill_color, None, "Choose Fill Color",
            QColorDialog.ColorDialogOption.ShowAlphaChannel
        )
        if color.isValid():
            self._fill_color = color
            self.update()
    
    def _choose_stroke_color(self):
        from PyQt6.QtWidgets import QColorDialog
        color = QColorDialog.getColor(self._stroke_color, None, "Choose Stroke Color")
        if color.isValid():
            self._stroke_color = color
            self.update()
    
    def _bring_to_front(self):
        """Bring shape to front (highest z-order)."""
        if self.scene():
            max_z = max((item.zValue() for item in self.scene().items()), default=0)
            self.setZValue(max_z + 1)
    
    def _send_to_back(self):
        """Send shape to back (lowest z-order)."""
        if self.scene():
            min_z = min((item.zValue() for item in self.scene().items()), default=0)
            self.setZValue(min_z - 1)
    
    def _duplicate(self):
        """Create a copy of this shape."""
        if self.scene():
            data = self.to_dict()
            # Offset the copy
            data["x"] = data["x"] + 20
            data["y"] = data["y"] + 20
            from .shape_item import create_shape_from_dict
            new_shape = create_shape_from_dict(data)
            if new_shape:
                self.scene().addItem(new_shape)
                # Select the new shape
                self.setSelected(False)
                new_shape.setSelected(True)
    
    def _delete(self):
        """Remove this shape from the scene."""
        if self.scene():
            self.scene().removeItem(self)
    
    # --- Properties ---
    
    @property
    def fill_color(self) -> QColor:
        """
        Fill color logic.
        
        Returns:
            Result of fill_color operation.
        """
        return self._fill_color
    
    @fill_color.setter
    def fill_color(self, color: QColor):
        """
        Fill color logic.
        
        Args:
            color: Description of color.
        
        """
        self._fill_color = color
        self.update()
    
    @property
    def stroke_color(self) -> QColor:
        """
        Stroke color logic.
        
        Returns:
            Result of stroke_color operation.
        """
        return self._stroke_color
    
    @stroke_color.setter
    def stroke_color(self, color: QColor):
        """
        Stroke color logic.
        
        Args:
            color: Description of color.
        
        """
        self._stroke_color = color
        self.update()
    
    @property
    def stroke_width(self) -> float:
        """
        Stroke width logic.
        
        Returns:
            Result of stroke_width operation.
        """
        return self._stroke_width
    
    @stroke_width.setter
    def stroke_width(self, width: float):
        """
        Stroke width logic.
        
        Args:
            width: Description of width.
        
        """
        self._stroke_width = width
        self.update()
    
    def to_dict(self) -> dict:
        """Serialize shape to dictionary."""
        return {
            "type": self.__class__.__name__,
            "x": self.pos().x(),
            "y": self.pos().y(),
            "width": self._rect.width(),
            "height": self._rect.height(),
            "fill_color": self._fill_color.name(QColor.NameFormat.HexArgb),
            "stroke_color": self._stroke_color.name(QColor.NameFormat.HexArgb),
            "stroke_width": self._stroke_width,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BaseShapeItem":
        """Create shape from dictionary."""
        shape = cls(data["x"], data["y"], data["width"], data["height"])
        shape.fill_color = QColor(data.get("fill_color", "#dbeafe"))
        shape.stroke_color = QColor(data.get("stroke_color", "#2563eb"))
        shape.stroke_width = data.get("stroke_width", 2)
        return shape


class RectShapeItem(BaseShapeItem):
    """Rectangle shape."""
    
    def __init__(self, x: float, y: float, width: float = 100, height: float = 60):
        """
          init   logic.
        
        Args:
            x: Description of x.
            y: Description of y.
            width: Description of width.
            height: Description of height.
        
        """
        super().__init__(x, y, width, height)
        self._corner_radius = 0
    
    @property
    def corner_radius(self) -> float:
        """
        Corner radius logic.
        
        Returns:
            Result of corner_radius operation.
        """
        return self._corner_radius
    
    @corner_radius.setter
    def corner_radius(self, radius: float):
        """
        Corner radius logic.
        
        Args:
            radius: Description of radius.
        
        """
        self._corner_radius = max(0, radius)
        self.update()
    
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        """
        Paint logic.
        
        Args:
            painter: Description of painter.
            option: Description of option.
            widget: Description of widget.
        
        """
        painter.setPen(QPen(self._stroke_color, self._stroke_width))
        painter.setBrush(QBrush(self._fill_color))
        if self._corner_radius > 0:
            painter.drawRoundedRect(self._rect, self._corner_radius, self._corner_radius)
        else:
            painter.drawRect(self._rect)


class EllipseShapeItem(BaseShapeItem):
    """Ellipse/Circle shape."""
    
    def __init__(self, x: float, y: float, width: float = 80, height: float = 60):
        """
          init   logic.
        
        Args:
            x: Description of x.
            y: Description of y.
            width: Description of width.
            height: Description of height.
        
        """
        super().__init__(x, y, width, height)
    
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        """
        Paint logic.
        
        Args:
            painter: Description of painter.
            option: Description of option.
            widget: Description of widget.
        
        """
        painter.setPen(QPen(self._stroke_color, self._stroke_width))
        painter.setBrush(QBrush(self._fill_color))
        painter.drawEllipse(self._rect)


class TriangleShapeItem(BaseShapeItem):
    """Triangle shape."""
    
    def __init__(self, x: float, y: float, width: float = 80, height: float = 70):
        """
          init   logic.
        
        Args:
            x: Description of x.
            y: Description of y.
            width: Description of width.
            height: Description of height.
        
        """
        super().__init__(x, y, width, height)
    
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        """
        Paint logic.
        
        Args:
            painter: Description of painter.
            option: Description of option.
            widget: Description of widget.
        
        """
        painter.setPen(QPen(self._stroke_color, self._stroke_width))
        painter.setBrush(QBrush(self._fill_color))
        
        polygon = QPolygonF([
            QPointF(self._rect.width() / 2, 0),  # Top center
            QPointF(self._rect.width(), self._rect.height()),  # Bottom right
            QPointF(0, self._rect.height()),  # Bottom left
        ])
        painter.drawPolygon(polygon)


# Line ending style constants
LINE_END_NONE = "none"
LINE_END_ARROW = "arrow"
LINE_END_OPEN_ARROW = "open_arrow"
LINE_END_CIRCLE = "circle"
LINE_END_DIAMOND = "diamond"
LINE_END_SQUARE = "square"
LINE_END_BAR = "bar"

LINE_END_STYLES = [
    LINE_END_NONE, LINE_END_ARROW, LINE_END_OPEN_ARROW,
    LINE_END_CIRCLE, LINE_END_DIAMOND, LINE_END_SQUARE, LINE_END_BAR
]


class LineShapeItem(BaseShapeItem):
    """Line/Connector shape with configurable ending styles at either end."""
    
    END_SIZE = 10  # Size of end decorations
    
    # Middle handle positions used for rotation
    ROTATION_HANDLES = {HandlePosition.TOP, HandlePosition.BOTTOM, HandlePosition.LEFT, HandlePosition.RIGHT}
    
    def __init__(self, x: float, y: float, width: float = 100, height: float = 20):
        """
          init   logic.
        
        Args:
            x: Description of x.
            y: Description of y.
            width: Description of width.
            height: Description of height.
        
        """
        super().__init__(x, y, width, max(20, height))
        self._fill_color = QColor(0, 0, 0, 0)  # Transparent fill for lines
        self._start_style = LINE_END_NONE
        self._end_style = LINE_END_NONE
        self._angle = 0.0  # Rotation angle in degrees
        
        # Set transform origin to center for rotation
        self.setTransformOriginPoint(self._rect.center())
        
        # Update handle visual for rotation handles
        self._update_handle_cursors()
    
    def _update_handle_cursors(self):
        """Set rotation cursor for middle handles."""
        for handle in self._handles:
            if handle.position in self.ROTATION_HANDLES:
                handle.setCursor(Qt.CursorShape.CrossCursor)
    
    @property
    def angle(self) -> float:
        """
        Angle logic.
        
        Returns:
            Result of angle operation.
        """
        return self._angle
    
    @angle.setter
    def angle(self, value: float):
        """
        Angle logic.
        
        Args:
            value: Description of value.
        
        """
        self._angle = value % 360
        self.setRotation(self._angle)
    
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        """Handle mouse press - check for rotation vs resize."""
        for handle in self._handles:
            if handle.contains(handle.mapFromScene(event.scenePos())):
                if handle.position in self.ROTATION_HANDLES:
                    # Middle handle = rotation
                    self._active_handle = handle
                    self._resize_start_pos = event.scenePos()
                    self._resize_start_rect = None  # Mark as rotation mode
                    # Store starting angle for relative calculation
                    center = self.mapToScene(self._rect.center())
                    dx = self._resize_start_pos.x() - center.x()
                    dy = self._resize_start_pos.y() - center.y()
                    self._rotation_start_angle = math.degrees(math.atan2(dy, dx))
                    self._rotation_start_value = self._angle
                    event.accept()
                    return
                else:
                    # Corner handle = resize (length)
                    self._active_handle = handle
                    self._resize_start_rect = QRectF(self._rect)
                    self._resize_start_pos = event.scenePos()
                    self._resize_start_item_pos = self.pos()
                    event.accept()
                    return
        super(BaseShapeItem, self).mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        """Handle mouse move for rotation or resize."""
        if self._active_handle and self._resize_start_pos:
            if self._resize_start_rect is None:
                # Rotation mode (middle handles)
                center = self.mapToScene(self._rect.center())
                mouse_pos = event.scenePos()
                
                # Calculate current angle from center to mouse
                dx = mouse_pos.x() - center.x()
                dy = mouse_pos.y() - center.y()
                current_angle = math.degrees(math.atan2(dy, dx))
                
                # Apply delta to starting rotation value
                angle_delta = current_angle - self._rotation_start_angle
                new_angle = self._rotation_start_value + angle_delta
                
                self._angle = new_angle % 360
                self.setRotation(self._angle)
                event.accept()
                return
            else:
                # Resize mode (corner handles) - only adjust width (length)
                delta = event.scenePos() - self._resize_start_pos
                
                if self._active_handle.position in (HandlePosition.LEFT, HandlePosition.TOP_LEFT, HandlePosition.BOTTOM_LEFT):
                    # Left side - adjust width from left
                    new_width = max(self.MIN_SIZE, self._resize_start_rect.width() - delta.x())
                    self.prepareGeometryChange()
                    self._rect.setWidth(new_width)
                    self._update_handles()
                else:
                    # Right side - adjust width from right
                    new_width = max(self.MIN_SIZE, self._resize_start_rect.width() + delta.x())
                    self.prepareGeometryChange()
                    self._rect.setWidth(new_width)
                    self._update_handles()
                
                self.setTransformOriginPoint(self._rect.center())
                event.accept()
                return
        
        super(BaseShapeItem, self).mouseMoveEvent(event)
    
    def boundingRect(self) -> QRectF:
        """Override to include end decorations in bounding rect."""
        # Add padding for end decorations and stroke
        padding = self.END_SIZE + self._stroke_width
        return self._rect.adjusted(-padding, -padding, padding, padding)
    
    @property
    def start_style(self) -> str:
        """
        Start style logic.
        
        Returns:
            Result of start_style operation.
        """
        return self._start_style
    
    @start_style.setter
    def start_style(self, value: str):
        """
        Start style logic.
        
        Args:
            value: Description of value.
        
        """
        if value in LINE_END_STYLES:
            self._start_style = value
            self.update()
    
    @property
    def end_style(self) -> str:
        """
        End style logic.
        
        Returns:
            Result of end_style operation.
        """
        return self._end_style
    
    @end_style.setter
    def end_style(self, value: str):
        """
        End style logic.
        
        Args:
            value: Description of value.
        
        """
        if value in LINE_END_STYLES:
            self._end_style = value
            self.update()
    
    # Backward compatibility
    @property
    def start_arrow(self) -> bool:
        """
        Start arrow logic.
        
        Returns:
            Result of start_arrow operation.
        """
        return self._start_style == LINE_END_ARROW
    
    @start_arrow.setter
    def start_arrow(self, value: bool):
        """
        Start arrow logic.
        
        Args:
            value: Description of value.
        
        """
        self._start_style = LINE_END_ARROW if value else LINE_END_NONE
        self.update()
    
    @property
    def end_arrow(self) -> bool:
        """
        End arrow logic.
        
        Returns:
            Result of end_arrow operation.
        """
        return self._end_style == LINE_END_ARROW
    
    @end_arrow.setter
    def end_arrow(self, value: bool):
        """
        End arrow logic.
        
        Args:
            value: Description of value.
        
        """
        self._end_style = LINE_END_ARROW if value else LINE_END_NONE
        self.update()
    
    def _get_end_offset(self, style: str) -> float:
        """Get how much to offset the line end for this style."""
        if style == LINE_END_NONE:
            return 0
        elif style in (LINE_END_ARROW, LINE_END_OPEN_ARROW):
            return self.END_SIZE
        elif style in (LINE_END_CIRCLE, LINE_END_DIAMOND, LINE_END_SQUARE):
            return self.END_SIZE / 2
        elif style == LINE_END_BAR:
            return 0
        return 0
    
    def _draw_end_style(self, painter: QPainter, x: float, y_mid: float, 
                        style: str, pointing_right: bool):
        """Draw the specified end style at the given position."""
        if style == LINE_END_NONE:
            return
        
        size = self.END_SIZE
        
        if style == LINE_END_ARROW:
            # Filled triangle - x is the edge, arrow points towards edge
            painter.setBrush(QBrush(self._stroke_color))
            path = QPainterPath()
            if pointing_right:
                # Tip at x (right edge), base at x - size
                path.moveTo(x, y_mid)  # Tip
                path.lineTo(x - size, y_mid - size / 2)  # Base top
                path.lineTo(x - size, y_mid + size / 2)  # Base bottom
            else:
                # Tip at x (left edge), base at x + size
                path.moveTo(x, y_mid)  # Tip
                path.lineTo(x + size, y_mid - size / 2)  # Base top
                path.lineTo(x + size, y_mid + size / 2)  # Base bottom
            path.closeSubpath()
            painter.drawPath(path)
            
        elif style == LINE_END_OPEN_ARROW:
            # Open triangle (outline only) - tip at edge
            painter.setBrush(Qt.BrushStyle.NoBrush)
            if pointing_right:
                # Tip at x, base at x - size
                painter.drawLine(QLineF(x - size, y_mid - size / 2, x, y_mid))
                painter.drawLine(QLineF(x, y_mid, x - size, y_mid + size / 2))
            else:
                # Tip at x, base at x + size
                painter.drawLine(QLineF(x + size, y_mid - size / 2, x, y_mid))
                painter.drawLine(QLineF(x, y_mid, x + size, y_mid + size / 2))
                
        elif style == LINE_END_CIRCLE:
            # Filled circle - center at half size from edge
            painter.setBrush(QBrush(self._stroke_color))
            radius = size / 2
            cx = x - radius if pointing_right else x + radius
            painter.drawEllipse(QPointF(cx, y_mid), radius, radius)
            
        elif style == LINE_END_DIAMOND:
            # Filled diamond - edge point at x
            painter.setBrush(QBrush(self._stroke_color))
            path = QPainterPath()
            half = size / 2
            if pointing_right:
                # Diamond tip at x, center at x - half
                path.moveTo(x, y_mid)  # Right tip (at edge)
                path.lineTo(x - half, y_mid - half)
                path.lineTo(x - size, y_mid)  # Left tip
                path.lineTo(x - half, y_mid + half)
            else:
                # Diamond tip at x, center at x + half
                path.moveTo(x, y_mid)  # Left tip (at edge)
                path.lineTo(x + half, y_mid - half)
                path.lineTo(x + size, y_mid)  # Right tip
                path.lineTo(x + half, y_mid + half)
            path.closeSubpath()
            painter.drawPath(path)
            
        elif style == LINE_END_SQUARE:
            # Filled square - edge at x
            painter.setBrush(QBrush(self._stroke_color))
            half = size / 2
            if pointing_right:
                painter.drawRect(QRectF(x - size, y_mid - half, size, size))
            else:
                painter.drawRect(QRectF(x, y_mid - half, size, size))
                
        elif style == LINE_END_BAR:
            # Perpendicular bar at edge
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawLine(QLineF(x, y_mid - size / 2, x, y_mid + size / 2))
    
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        """
        Paint logic.
        
        Args:
            painter: Description of painter.
            option: Description of option.
            widget: Description of widget.
        
        """
        pen = QPen(self._stroke_color, self._stroke_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        
        y_mid = self._rect.height() / 2
        line_start = self._get_end_offset(self._start_style)
        line_end = self._rect.width() - self._get_end_offset(self._end_style)
        
        # Draw line
        painter.drawLine(QLineF(line_start, y_mid, line_end, y_mid))
        
        # Draw end decorations
        self._draw_end_style(painter, 0, y_mid, self._start_style, pointing_right=False)
        self._draw_end_style(painter, self._rect.width(), y_mid, self._end_style, pointing_right=True)
    
    def to_dict(self) -> dict:
        """
        Convert to dict logic.
        
        Returns:
            Result of to_dict operation.
        """
        data = super().to_dict()
        data["start_style"] = self._start_style
        data["end_style"] = self._end_style
        data["angle"] = self._angle
        # Backward compat
        data["start_arrow"] = self._start_style == LINE_END_ARROW
        data["end_arrow"] = self._end_style == LINE_END_ARROW
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "LineShapeItem":
        """
        From dict logic.
        
        Args:
            data: Description of data.
        
        Returns:
            Result of from_dict operation.
        """
        shape = cls(data["x"], data["y"], data["width"], data["height"])
        shape.fill_color = QColor(data.get("fill_color", "#00000000"))
        shape.stroke_color = QColor(data.get("stroke_color", "#2563eb"))
        shape.stroke_width = data.get("stroke_width", 2)
        # New style format
        shape._start_style = data.get("start_style", LINE_END_NONE)
        shape._end_style = data.get("end_style", LINE_END_NONE)
        # Angle
        shape._angle = data.get("angle", 0.0)
        shape.setRotation(shape._angle)
        # Backward compat
        if "start_arrow" in data and data["start_arrow"] and shape._start_style == LINE_END_NONE:
            shape._start_style = LINE_END_ARROW
        if "end_arrow" in data and data["end_arrow"] and shape._end_style == LINE_END_NONE:
            shape._end_style = LINE_END_ARROW
        return shape
    
    def contextMenuEvent(self, event):
        """Extended context menu with end style options."""
        from PyQt6.QtWidgets import QMenu, QColorDialog
        
        menu = QMenu()
        
        # Style names for display
        style_names = {
            LINE_END_NONE: "None",
            LINE_END_ARROW: "Arrow ▶",
            LINE_END_OPEN_ARROW: "Open Arrow ⊳",
            LINE_END_CIRCLE: "Circle ●",
            LINE_END_DIAMOND: "Diamond ◆",
            LINE_END_SQUARE: "Square ■",
            LINE_END_BAR: "Bar |",
        }
        
        # Start End Style
        start_menu = menu.addMenu(f"Start End: {style_names[self._start_style]}")
        for style in LINE_END_STYLES:
            action = start_menu.addAction(style_names[style])
            action.setCheckable(True)
            action.setChecked(self._start_style == style)
            action.triggered.connect(lambda checked, s=style: self._set_start_style(s))
        
        # End Style
        end_menu = menu.addMenu(f"End: {style_names[self._end_style]}")
        for style in LINE_END_STYLES:
            action = end_menu.addAction(style_names[style])
            action.setCheckable(True)
            action.setChecked(self._end_style == style)
            action.triggered.connect(lambda checked, s=style: self._set_end_style(s))
        
        menu.addSeparator()
        
        # Quick presets
        presets_menu = menu.addMenu("Quick Presets")
        presets_menu.addAction("Line (no ends)").triggered.connect(
            lambda: self._set_styles(LINE_END_NONE, LINE_END_NONE))
        presets_menu.addAction("Arrow →").triggered.connect(
            lambda: self._set_styles(LINE_END_NONE, LINE_END_ARROW))
        presets_menu.addAction("← Arrow").triggered.connect(
            lambda: self._set_styles(LINE_END_ARROW, LINE_END_NONE))
        presets_menu.addAction("↔ Double Arrow").triggered.connect(
            lambda: self._set_styles(LINE_END_ARROW, LINE_END_ARROW))
        presets_menu.addAction("●—● Circle Both").triggered.connect(
            lambda: self._set_styles(LINE_END_CIRCLE, LINE_END_CIRCLE))
        presets_menu.addAction("|—| Bar Both").triggered.connect(
            lambda: self._set_styles(LINE_END_BAR, LINE_END_BAR))
        
        menu.addSeparator()
        
        # Stroke color
        stroke_menu = menu.addMenu("Stroke Color")
        stroke_colors = [
            ("Blue", "#2563eb"), ("Green", "#16a34a"), ("Yellow", "#ca8a04"),
            ("Red", "#dc2626"), ("Purple", "#9333ea"), ("Black", "#000000"), ("Gray", "#6b7280"),
        ]
        for name, color in stroke_colors:
            action = stroke_menu.addAction(name)
            action.triggered.connect(lambda checked, c=QColor(color): self._set_stroke_color(c))
        stroke_menu.addSeparator()
        stroke_menu.addAction("Custom...").triggered.connect(self._choose_stroke_color)
        
        # Stroke width
        width_menu = menu.addMenu("Stroke Width")
        for w in [1, 2, 3, 4, 5, 6, 8, 10]:
            action = width_menu.addAction(f"{w}px")
            action.setCheckable(True)
            action.setChecked(self._stroke_width == w)
            action.triggered.connect(lambda checked, width=w: self._set_stroke_width(width))
        
        menu.addSeparator()
        menu.addAction("Bring to Front").triggered.connect(self._bring_to_front)
        menu.addAction("Send to Back").triggered.connect(self._send_to_back)
        menu.addSeparator()
        menu.addAction("Duplicate").triggered.connect(self._duplicate)
        menu.addAction("Delete").triggered.connect(self._delete)
        
        menu.exec(event.screenPos())
    
    def _set_start_style(self, style: str):
        self._start_style = style
        self.update()
    
    def _set_end_style(self, style: str):
        self._end_style = style
        self.update()
    
    def _set_styles(self, start: str, end: str):
        self._start_style = start
        self._end_style = end
        self.update()


class ArrowShapeItem(LineShapeItem):
    """Arrow shape - a line with end arrow enabled by default."""
    
    def __init__(self, x: float, y: float, width: float = 100, height: float = 20):
        """
          init   logic.
        
        Args:
            x: Description of x.
            y: Description of y.
            width: Description of width.
            height: Description of height.
        
        """
        super().__init__(x, y, width, height)
        self._end_style = LINE_END_ARROW  # Arrow at end by default


class PolygonShapeItem(BaseShapeItem):
    """Configurable polygon shape - supports n-gons and n-grams (star polygons).
    
    An n-gon is a regular polygon with n sides.
    An n-gram is a star polygon created by connecting every k-th vertex.
    
    Examples:
    - Pentagon (5-gon): sides=5, skip=1
    - Pentagram (5-gram): sides=5, skip=2
    - Hexagram (Star of David): sides=6, skip=2
    - Heptagram: sides=7, skip=2 or skip=3
    """
    
    def __init__(self, x: float, y: float, width: float = 100, height: float = 100,
                 sides: int = 5, skip: int = 1):
        """
          init   logic.
        
        Args:
            x: Description of x.
            y: Description of y.
            width: Description of width.
            height: Description of height.
            sides: Description of sides.
            skip: Description of skip.
        
        """
        self._sides = max(3, sides)
        self._skip = max(1, min(skip, (sides - 1) // 2))  # Skip must be < n/2
        super().__init__(x, y, width, height)
    
    @property
    def sides(self) -> int:
        """
        Sides logic.
        
        Returns:
            Result of sides operation.
        """
        return self._sides
    
    @sides.setter
    def sides(self, value: int):
        """
        Sides logic.
        
        Args:
            value: Description of value.
        
        """
        self._sides = max(3, value)
        self._skip = min(self._skip, (self._sides - 1) // 2) or 1
        self.update()
    
    @property
    def skip(self) -> int:
        """
        Skip logic.
        
        Returns:
            Result of skip operation.
        """
        return self._skip
    
    @skip.setter
    def skip(self, value: int):
        """
        Skip logic.
        
        Args:
            value: Description of value.
        
        """
        self._skip = max(1, min(value, (self._sides - 1) // 2))
        self.update()
    
    @property
    def is_star(self) -> bool:
        """True if this is a star polygon (skip > 1)."""
        return self._skip > 1
    
    def _get_polygon_name(self) -> str:
        """Get the name of this polygon."""
        names = {
            3: "Triangle", 4: "Square", 5: "Pentagon", 6: "Hexagon",
            7: "Heptagon", 8: "Octagon", 9: "Nonagon", 10: "Decagon",
            11: "Hendecagon", 12: "Dodecagon"
        }
        base_name = names.get(self._sides, f"{self._sides}-gon")
        if self._skip > 1:
            return f"{base_name} ({self._sides}/{self._skip})"
        return base_name
    
    def _calculate_vertices(self) -> list[QPointF]:
        """Calculate vertex positions for the polygon."""
        cx = self._rect.width() / 2
        cy = self._rect.height() / 2
        radius = min(cx, cy) - 2  # Small margin for stroke
        
        vertices = []
        for i in range(self._sides):
            # Start from top (negative y-axis)
            angle = -math.pi / 2 + (2 * math.pi * i / self._sides)
            vx = cx + radius * math.cos(angle)
            vy = cy + radius * math.sin(angle)
            vertices.append(QPointF(vx, vy))
        return vertices
    
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        """
        Paint logic.
        
        Args:
            painter: Description of painter.
            option: Description of option.
            widget: Description of widget.
        
        """
        painter.setPen(QPen(self._stroke_color, self._stroke_width))
        painter.setBrush(QBrush(self._fill_color))
        
        vertices = self._calculate_vertices()
        
        if self._skip == 1:
            # Regular polygon - connect adjacent vertices
            polygon = QPolygonF(vertices)
            painter.drawPolygon(polygon)
        else:
            # Star polygon - connect every k-th vertex
            path = QPainterPath()
            n = len(vertices)
            visited = [False] * n
            start = 0
            
            while not all(visited):
                if not visited[start]:
                    path.moveTo(vertices[start])
                    current = start
                    while True:
                        visited[current] = True
                        next_idx = (current + self._skip) % n
                        path.lineTo(vertices[next_idx])
                        current = next_idx
                        if current == start:
                            break
                # Find next unvisited
                for i in range(n):
                    if not visited[i]:
                        start = i
                        break
            
            path.closeSubpath()
            painter.drawPath(path)
    
    def to_dict(self) -> dict:
        """Serialize shape to dictionary."""
        data = super().to_dict()
        data["sides"] = self._sides
        data["skip"] = self._skip
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "PolygonShapeItem":
        """Create shape from dictionary."""
        shape = cls(
            data["x"], data["y"], 
            data["width"], data["height"],
            data.get("sides", 5), data.get("skip", 1)
        )
        shape.fill_color = QColor(data.get("fill_color", "#dbeafe"))
        shape.stroke_color = QColor(data.get("stroke_color", "#2563eb"))
        shape.stroke_width = data.get("stroke_width", 2)
        return shape
    
    def contextMenuEvent(self, event):
        """Extended context menu with polygon-specific options."""
        from PyQt6.QtWidgets import QMenu, QColorDialog, QInputDialog
        
        menu = QMenu()
        
        # Polygon configuration
        config_menu = menu.addMenu("Polygon Settings")
        
        # Sides submenu
        sides_menu = config_menu.addMenu(f"Sides ({self._sides})")
        for n in range(3, 13):
            action = sides_menu.addAction(f"{n}")
            action.setCheckable(True)
            action.setChecked(self._sides == n)
            action.triggered.connect(lambda checked, s=n: self._set_sides(s))
        sides_menu.addSeparator()
        custom_sides = sides_menu.addAction("Custom...")
        custom_sides.triggered.connect(self._choose_sides)
        
        # Skip submenu (for star polygons)
        max_skip = (self._sides - 1) // 2
        if max_skip > 1:
            skip_menu = config_menu.addMenu(f"Star Skip ({self._skip})")
            skip_menu.addAction("1 (Regular)").triggered.connect(lambda: self._set_skip(1))
            for k in range(2, max_skip + 1):
                action = skip_menu.addAction(f"{k} ({self._sides}/{k})")
                action.setCheckable(True)
                action.setChecked(self._skip == k)
                action.triggered.connect(lambda checked, s=k: self._set_skip(s))
        
        menu.addSeparator()
        
        # Call parent context menu items
        fill_menu = menu.addMenu("Fill Color")
        fill_colors = [
            ("Blue", "#dbeafe"), ("Green", "#dcfce7"), ("Yellow", "#fef3c7"),
            ("Red", "#fecaca"), ("Purple", "#f3e8ff"), ("Gray", "#f3f4f6"),
            ("White", "#ffffff"), ("Transparent", "transparent"),
        ]
        for name, color in fill_colors:
            action = fill_menu.addAction(name)
            if color == "transparent":
                action.triggered.connect(lambda checked, c=QColor(0, 0, 0, 0): self._set_fill_color(c))
            else:
                action.triggered.connect(lambda checked, c=QColor(color): self._set_fill_color(c))
        fill_menu.addSeparator()
        fill_menu.addAction("Custom...").triggered.connect(self._choose_fill_color)
        
        stroke_menu = menu.addMenu("Stroke Color")
        stroke_colors = [
            ("Blue", "#2563eb"), ("Green", "#16a34a"), ("Yellow", "#ca8a04"),
            ("Red", "#dc2626"), ("Purple", "#9333ea"), ("Black", "#000000"), ("Gray", "#6b7280"),
        ]
        for name, color in stroke_colors:
            action = stroke_menu.addAction(name)
            action.triggered.connect(lambda checked, c=QColor(color): self._set_stroke_color(c))
        stroke_menu.addSeparator()
        stroke_menu.addAction("Custom...").triggered.connect(self._choose_stroke_color)
        
        width_menu = menu.addMenu("Stroke Width")
        for w in [1, 2, 3, 4, 5, 6, 8, 10]:
            action = width_menu.addAction(f"{w}px")
            action.setCheckable(True)
            action.setChecked(self._stroke_width == w)
            action.triggered.connect(lambda checked, width=w: self._set_stroke_width(width))
        
        menu.addSeparator()
        menu.addAction("Bring to Front").triggered.connect(self._bring_to_front)
        menu.addAction("Send to Back").triggered.connect(self._send_to_back)
        menu.addSeparator()
        menu.addAction("Duplicate").triggered.connect(self._duplicate)
        menu.addAction("Delete").triggered.connect(self._delete)
        
        menu.exec(event.screenPos())
    
    def _set_sides(self, n: int):
        self._sides = max(3, n)
        self._skip = min(self._skip, (self._sides - 1) // 2) or 1
        self.update()
    
    def _set_skip(self, k: int):
        self._skip = max(1, min(k, (self._sides - 1) // 2))
        self.update()
    
    def _choose_sides(self):
        from PyQt6.QtWidgets import QInputDialog
        n, ok = QInputDialog.getInt(None, "Number of Sides", "Enter number of sides:", 
                                     self._sides, 3, 100, 1)
        if ok:
            self._set_sides(n)


# Registry for shape types
SHAPE_TYPES = {
    "RectShapeItem": RectShapeItem,
    "EllipseShapeItem": EllipseShapeItem,
    "TriangleShapeItem": TriangleShapeItem,
    "LineShapeItem": LineShapeItem,
    "ArrowShapeItem": ArrowShapeItem,
    "PolygonShapeItem": PolygonShapeItem,
}


def create_shape_from_dict(data: dict) -> Optional[BaseShapeItem]:
    """Factory function to create shape from dictionary."""
    shape_type = data.get("type")
    if shape_type in SHAPE_TYPES:
        return SHAPE_TYPES[shape_type].from_dict(data)
    return None
