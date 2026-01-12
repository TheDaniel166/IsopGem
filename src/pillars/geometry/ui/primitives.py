"""Data primitives for the geometry visualization scene."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Sequence, Tuple, Union, Optional

Color = Tuple[int, int, int, int]


def _color(r: int, g: int, b: int, a: int = 255) -> Color:
    """Helper to keep default colors short."""
    return (r, g, b, a)


@dataclass
class PenStyle:
    """Stroke styling for a primitive."""
    color: Color = _color(37, 99, 235)
    width: float = 2.0
    dashed: bool = False


@dataclass
class BrushStyle:
    """Fill styling for a primitive."""
    color: Color = _color(219, 234, 254, 120)
    enabled: bool = True


@dataclass
class Bounds:
    """Axis-aligned bounding box for the current scene payload."""
    min_x: float
    max_x: float
    min_y: float
    max_y: float

    @property
    def width(self) -> float:
        """
        Width logic.
        
        Returns:
            Result of width operation.
        """
        return max(self.max_x - self.min_x, 1e-6)

    @property
    def height(self) -> float:
        """
        Height logic.
        
        Returns:
            Result of height operation.
        """
        return max(self.max_y - self.min_y, 1e-6)

    def padded(self, padding: float) -> "Bounds":
        """
        Padded logic.
        
        Args:
            padding: Description of padding.
        
        Returns:
            Result of padded operation.
        """
        return Bounds(
            min_x=self.min_x - padding,
            max_x=self.max_x + padding,
            min_y=self.min_y - padding,
            max_y=self.max_y + padding,
        )


@dataclass
class CirclePrimitive:
    """
    Circle Primitive class definition.
    
    """
    center: Tuple[float, float]
    radius: float
    pen: PenStyle = field(default_factory=PenStyle)
    brush: BrushStyle = field(default_factory=BrushStyle)
    metadata: Optional[dict] = field(default=None)


@dataclass
class PolygonPrimitive:
    """
    Polygon Primitive class definition.
    
    """
    points: Sequence[Tuple[float, float]]
    pen: PenStyle = field(default_factory=PenStyle)
    brush: BrushStyle = field(default_factory=BrushStyle)
    closed: bool = True


@dataclass
class LinePrimitive:
    """
    Line Primitive class definition.
    
    """
    start: Tuple[float, float]
    end: Tuple[float, float]
    pen: PenStyle = field(default_factory=PenStyle)
    metadata: Optional[dict] = field(default=None)


@dataclass
class LabelPrimitive:
    """
    Label Primitive class definition.
    
    """
    text: str
    position: Tuple[float, float]
    align_center: bool = True
    metadata: Optional[dict] = field(default=None)


@dataclass
class BooleanPrimitive:
    """A shape resulting from a boolean operation between two primitives."""
    operation: str # "difference", "union", "intersection"
    shape_a: Primitive
    shape_b: Primitive
    pen: PenStyle = field(default_factory=PenStyle)
    brush: BrushStyle = field(default_factory=BrushStyle)


Primitive = Union[CirclePrimitive, PolygonPrimitive, LinePrimitive, BooleanPrimitive]


@dataclass
class GeometryScenePayload:
    """All information necessary for the scene to render a shape."""
    primitives: List[Primitive] = field(default_factory=list)
    labels: List[LabelPrimitive] = field(default_factory=list)
    bounds: Optional[Bounds] = None
    suggest_grid_span: Optional[float] = None


__all__ = [
    "Color",
    "PenStyle",
    "BrushStyle",
    "Bounds",
    "CirclePrimitive",
    "PolygonPrimitive",
    "LinePrimitive",
    "LabelPrimitive",
    "Primitive",
    "GeometryScenePayload",
]