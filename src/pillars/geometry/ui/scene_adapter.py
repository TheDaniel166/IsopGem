"""Adapter to convert legacy drawing dictionaries into scene primitives."""
from __future__ import annotations
import math
from typing import Dict, List, Sequence, Tuple

from .primitives import (
    Bounds,
    BrushStyle,
    CirclePrimitive,
    GeometryScenePayload,
    LabelPrimitive,
    LinePrimitive,
    PenStyle,
    PolygonPrimitive,
    BooleanPrimitive,
)


def build_scene_payload(drawing_instructions: Dict, labels: Sequence[Tuple[str, float, float]]) -> GeometryScenePayload:
    """Translate the legacy viewport dictionaries into structured primitives."""
    if not drawing_instructions or drawing_instructions.get("type") == "empty":
        return GeometryScenePayload()

    primitive_items: List[Primitive] = []

    shape_type = drawing_instructions.get("type")
    primitive_specs = drawing_instructions.get("primitives")

    if primitive_specs:
        primitive_items.extend(_custom_primitives(primitive_specs))
    elif shape_type == "circle":
        primitive_items.extend(_circle_primitives(drawing_instructions))
    elif shape_type == "polygon":
        primitive_items.extend(_polygon_primitives(drawing_instructions))

    label_items = [LabelPrimitive(text=text, position=(x, y)) for text, x, y in labels]
    bounds = _calculate_bounds(primitive_items)

    payload = GeometryScenePayload(
        primitives=primitive_items,
        labels=label_items,
        bounds=bounds,
    )

    if primitive_specs:
        span = bounds.width if bounds else 10
        payload.suggest_grid_span = span * 1.2
    elif shape_type == "circle":
        radius = abs(drawing_instructions.get("radius", 1.0))
        payload.suggest_grid_span = radius * 4
    elif shape_type == "polygon":
        payload.suggest_grid_span = (bounds.width if bounds else 10) * 1.2

    return payload


# ---------------------------------------------------------------------------
# Primitive builders
# ---------------------------------------------------------------------------

def _circle_primitives(payload: Dict) -> List[Primitive]:
    center = (payload.get("center_x", 0.0), payload.get("center_y", 0.0))
    radius = abs(payload.get("radius", 1.0))

    primitives: List[Primitive] = [CirclePrimitive(center=center, radius=radius)]

    if payload.get("show_radius_line"):
        primitives.append(
            LinePrimitive(
                start=center,
                end=(center[0] + radius, center[1]),
                pen=PenStyle(color=(220, 38, 38, 255), width=2.0),
            )
        )

    if payload.get("show_diameter_line"):
        primitives.append(
            LinePrimitive(
                start=(center[0] - radius, center[1]),
                end=(center[0] + radius, center[1]),
                pen=PenStyle(color=(16, 185, 129, 255), width=2.0, dashed=True),
            )
        )

    chord_points = payload.get("chord_points")
    if chord_points and len(chord_points) == 2:
        primitives.append(
            LinePrimitive(
                start=tuple(chord_points[0]),
                end=tuple(chord_points[1]),
                pen=PenStyle(color=(249, 115, 22, 255), width=2.0),
            )
        )

    return primitives


def _polygon_primitives(payload: Dict) -> List[Primitive]:
    base_points: List[Tuple[float, float]] = [(x, y) for x, y in payload.get("points", [])]
    primitives: List[Primitive] = []

    star_mode = payload.get("star") and len(base_points) >= 6
    if star_mode:
        primitives.extend(_star_polygons(base_points))
    else:
        primitives.append(PolygonPrimitive(points=base_points))

    diagonal_groups = payload.get("diagonal_groups")
    if diagonal_groups:
        primitives.extend(_colored_diagonal_groups(diagonal_groups))

    if payload.get("show_diagonals"):
        primitives.extend(_all_diagonals(base_points))

    if payload.get("show_diagonal"):
        primitives.extend(_shortest_diagonals(base_points))

    if payload.get("show_circumcircle"):
        primitives.append(_circumcircle(base_points))

    if payload.get("show_incircle"):
        incircle = _incircle(base_points)
        if incircle:
            primitives.append(incircle)

    axis_lines = payload.get("axis_lines", [])
    if axis_lines:
        axis_pen = PenStyle(color=(14, 165, 233, 255), width=1.5, dashed=True)
        for line in axis_lines:
            if len(line) != 2:
                continue
            primitives.append(
                LinePrimitive(
                    start=tuple(line[0]),
                    end=tuple(line[1]),
                    pen=axis_pen,
                )
            )

    return primitives


def _star_polygons(points: Sequence[Tuple[float, float]]) -> List[Primitive]:
    n = len(points)
    triangles: List[Primitive] = []
    step = 2
    for offset in range(step):
        tri_points = [points[(offset + i * step) % n] for i in range(n // step)]
        triangles.append(PolygonPrimitive(points=tri_points))
    return triangles


def _all_diagonals(points: Sequence[Tuple[float, float]]) -> List[Primitive]:
    diagonals: List[Primitive] = []
    n = len(points)
    pen = PenStyle(color=(156, 163, 175, 255), width=1.0, dashed=True)
    seen_pairs = set()
    for i in range(n):
        for skip in range(2, n - 1):
            j = (i + skip) % n
            if j == i:
                continue
            pair = tuple(sorted((i, j)))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            diagonals.append(LinePrimitive(start=points[i], end=points[j], pen=pen))
    return diagonals


def _shortest_diagonals(points: Sequence[Tuple[float, float]]) -> List[Primitive]:
    if len(points) < 4:
        return []
    diagonals: List[Primitive] = []
    n = len(points)
    pen = PenStyle(color=(220, 38, 38, 255), width=2.0, dashed=True)
    for i in range(n):
        diagonals.append(LinePrimitive(start=points[i], end=points[(i + 2) % n], pen=pen))
    return diagonals


def _circumcircle(points: Sequence[Tuple[float, float]]) -> CirclePrimitive:
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    radius = math.sqrt((points[0][0] - cx) ** 2 + (points[0][1] - cy) ** 2)
    pen = PenStyle(color=(124, 58, 237, 255), width=2.0, dashed=True)
    return CirclePrimitive(center=(cx, cy), radius=radius, pen=pen)


def _incircle(points: Sequence[Tuple[float, float]]):
    if len(points) < 3:
        return None
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    mid_x = (points[0][0] + points[1][0]) / 2
    mid_y = (points[0][1] + points[1][1]) / 2
    radius = math.sqrt((mid_x - cx) ** 2 + (mid_y - cy) ** 2)
    pen = PenStyle(color=(16, 185, 129, 255), width=2.0, dashed=True)
    return CirclePrimitive(center=(cx, cy), radius=radius, pen=pen)


def _calculate_bounds(primitives: Sequence[Primitive]) -> Bounds | None:
    if not primitives:
        return None

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
        elif isinstance(primitive, BooleanPrimitive):
             # Recursively check bounds of shape_a and shape_b
             for sub in (primitive.shape_a, primitive.shape_b):
                 sub_bounds = _calculate_bounds([sub])
                 if sub_bounds:
                     xs.extend([sub_bounds.min_x, sub_bounds.max_x])
                     ys.extend([sub_bounds.min_y, sub_bounds.max_y])

    if not xs or not ys:
        return None

    return Bounds(min(xs), max(xs), min(ys), max(ys))


def _colored_diagonal_groups(groups: Sequence[Dict]) -> List[Primitive]:
    primitives: List[Primitive] = []
    for group in groups:
        raw_color = group.get("color") or (148, 163, 184, 255)
        color = tuple(raw_color) if isinstance(raw_color, (list, tuple)) else (148, 163, 184, 255)
        pen = PenStyle(color=color, width=2.0, dashed=False)
        for segment in group.get("segments", []):
            if isinstance(segment, dict):
                start = tuple(segment.get("start", (0.0, 0.0)))
                end = tuple(segment.get("end", (0.0, 0.0)))
            elif isinstance(segment, (list, tuple)) and len(segment) == 2:
                start = tuple(segment[0])
                end = tuple(segment[1])
            else:
                continue
            primitives.append(LinePrimitive(start=start, end=end, pen=pen))
    return primitives


def _custom_primitives(specs: Sequence[Dict]) -> List[Primitive]:
    primitives: List[Primitive] = []
    for spec in specs:
        if not isinstance(spec, dict):
            continue
        primitive = _parse_single_primitive(spec)
        if primitive:
            primitives.append(primitive)
    return primitives


def _parse_single_primitive(spec: Dict) -> Optional[Primitive]:
    if not isinstance(spec, dict):
        return None
        
    shape = spec.get("shape")
    type_ = spec.get("type", shape) # Handle aliasing/legacy 'shape' vs 'type'
    
    if type_ == "boolean":
         op = spec.get("operation")
         shape_a_spec = spec.get("shape_a")
         shape_b_spec = spec.get("shape_b")
         if not shape_a_spec or not shape_b_spec:
             return None
         shape_a = _parse_single_primitive(shape_a_spec)
         shape_b = _parse_single_primitive(shape_b_spec)
         if shape_a and shape_b:
             pen = _decode_pen(spec.get("pen"))
             brush = _decode_brush(spec.get("brush"))
             return BooleanPrimitive(operation=op, shape_a=shape_a, shape_b=shape_b, pen=pen, brush=brush)
             
    elif type_ == "circle":
        center = tuple(spec.get("center", (0.0, 0.0)))
        radius_val = spec.get("radius", 1.0)
        # Fix logic: handle None radius gracefully if missed elsewhere
        if radius_val is None:
            return None
        radius = abs(float(radius_val))
        pen = _decode_pen(spec.get("pen"))
        brush = _decode_brush(spec.get("brush"))
        return CirclePrimitive(center=center, radius=radius, pen=pen, brush=brush)
        
    elif type_ == "polygon":
        points = [tuple(point) for point in spec.get("points", [])]
        if not points:
            return None
        pen = _decode_pen(spec.get("pen"))
        brush = _decode_brush(spec.get("brush"))
        closed = bool(spec.get("closed", True))
        return PolygonPrimitive(points=points, pen=pen, brush=brush, closed=closed)
        
    elif type_ == "line":
        start = tuple(spec.get("start", (0.0, 0.0)))
        end = tuple(spec.get("end", (0.0, 0.0)))
        pen = _decode_pen(spec.get("pen"))
        return LinePrimitive(start=start, end=end, pen=pen)
        
    elif type_ == "polyline":
        points = [tuple(point) for point in spec.get("points", [])]
        if not points:
            return None
        
        pen = _decode_pen(spec.get("pen"))
        
        # Default to no brush for polyline unless specified
        brush_config = spec.get("brush")
        if brush_config:
            brush = _decode_brush(brush_config)
        else:
            brush = BrushStyle(enabled=False)
            
        closed = bool(spec.get("closed", False))
        return PolygonPrimitive(points=points, pen=pen, brush=brush, closed=closed)
        
    return None


def _decode_pen(config: Dict | None) -> PenStyle:
    if not config:
        return PenStyle()
    color = tuple(config.get("color", PenStyle().color))
    width = float(config.get("width", 2.0))
    dashed = bool(config.get("dashed", False))
    return PenStyle(color=color, width=width, dashed=dashed)


def _decode_brush(config: Dict | None) -> BrushStyle:
    if not config:
        return BrushStyle()
    color = tuple(config.get("color", BrushStyle().color))
    enabled = bool(config.get("enabled", True))
    return BrushStyle(color=color, enabled=enabled)


__all__ = ["build_scene_payload"]
