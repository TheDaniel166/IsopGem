"""Terraced step pyramid solid service and calculator."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, cast

from ..shared.solid_payload import Face, SolidLabel, SolidPayload
from .solid_property import SolidProperty


@dataclass(frozen=True)
class StepPyramidMetrics:
    """
    Step Pyramid Metrics class definition.
    
    """
    base_edge: float
    top_edge: float
    height: float
    tiers: int
    step_height: float
    base_area: float
    top_area: float
    lateral_area: float
    surface_area: float
    volume: float
    tier_edges: List[float]


@dataclass(frozen=True)
class StepPyramidSolidResult:
    """
    Step Pyramid Solid Result class definition.
    
    """
    payload: SolidPayload
    metrics: StepPyramidMetrics


def _interpolate_edges(base_edge: float, top_edge: float, tiers: int) -> List[float]:
    if tiers <= 0:
        return [base_edge]
    return [base_edge - (base_edge - top_edge) * (i / tiers) for i in range(tiers + 1)]


def _build_vertices(edge_sizes: List[float], height: float) -> List[tuple[float, float, float]]:
    tiers = len(edge_sizes) - 1
    step_height = height / tiers if tiers else height
    vertices: List[tuple[float, float, float]] = []
    for level, edge in enumerate(edge_sizes):
        half = edge / 2.0
        z = -height / 2.0 + step_height * level
        vertices.extend([
            (-half, -half, z),
            (half, -half, z),
            (half, half, z),
            (-half, half, z),
        ])
    return vertices


def _build_edges(tiers: int) -> List[tuple[int, int]]:
    edges: List[tuple[int, int]] = []
    levels = tiers + 1
    for level in range(levels):
        base = level * 4
        edges.extend([
            (base + 0, base + 1),
            (base + 1, base + 2),
            (base + 2, base + 3),
            (base + 3, base + 0),
        ])
    for level in range(tiers):
        base_lower = level * 4
        base_upper = (level + 1) * 4
        for corner in range(4):
            edges.append((base_lower + corner, base_upper + corner))
    return edges


def _build_faces(tiers: int) -> List[Face]:
    faces: List[Face] = []
    faces.append(cast(Face, (0, 1, 2, 3)))
    levels = tiers + 1
    top_base = (levels - 1) * 4
    faces.append(cast(Face, (top_base + 0, top_base + 1, top_base + 2, top_base + 3)))
    for level in range(tiers):
        base_lower = level * 4
        base_upper = (level + 1) * 4
        faces.append(cast(Face, (base_lower + 0, base_lower + 1, base_upper + 1, base_upper + 0)))
        faces.append(cast(Face, (base_lower + 1, base_lower + 2, base_upper + 2, base_upper + 1)))
        faces.append(cast(Face, (base_lower + 2, base_lower + 3, base_upper + 3, base_upper + 2)))
        faces.append(cast(Face, (base_lower + 3, base_lower + 0, base_upper + 0, base_upper + 3)))
    return faces


def _compute_metrics(base_edge: float, top_edge: float, height: float, tiers: int) -> StepPyramidMetrics:
    if tiers <= 0:
        raise ValueError('Tiers must be at least 1')
    if top_edge <= 0 or base_edge <= 0 or height <= 0:
        raise ValueError('Dimensions must be positive')
    if top_edge >= base_edge:
        raise ValueError('Top edge must be smaller than base edge for a step pyramid')
    step_height = height / tiers
    edges = [base_edge - (base_edge - top_edge) * (i / tiers) for i in range(tiers)]
    tier_edges = edges + [top_edge]
    base_area = base_edge ** 2
    top_area = top_edge ** 2
    lateral_area = 4.0 * step_height * sum(edges)
    volume = step_height * sum(edge ** 2 for edge in edges)
    surface_area = lateral_area + base_area + top_area
    return StepPyramidMetrics(
        base_edge=base_edge,
        top_edge=top_edge,
        height=height,
        tiers=tiers,
        step_height=step_height,
        base_area=base_area,
        top_area=top_area,
        lateral_area=lateral_area,
        surface_area=surface_area,
        volume=volume,
        tier_edges=tier_edges,
    )


def _build_payload(base_edge: float, top_edge: float, height: float, tiers: int) -> SolidPayload:
    edge_sizes = _interpolate_edges(base_edge, top_edge, tiers)
    vertices = _build_vertices(edge_sizes, height)
    edges = _build_edges(tiers)
    faces = _build_faces(tiers)
    metrics = _compute_metrics(base_edge, top_edge, height, tiers)
    labels = [
        SolidLabel(text=f"a₀ = {metrics.base_edge:.2f}", position=(-metrics.base_edge / 2.0, 0.0, -metrics.height / 2.0)),
        SolidLabel(text=f"aₜ = {metrics.top_edge:.2f}", position=(0.0, metrics.top_edge / 2.0, metrics.height / 2.0)),
        SolidLabel(text=f"tiers = {metrics.tiers}", position=(0.0, 0.0, 0.0)),
    ]
    return SolidPayload(
        vertices=vertices,
        edges=edges,
        faces=faces,
        labels=labels,
        metadata={
            'base_edge': metrics.base_edge,
            'top_edge': metrics.top_edge,
            'height': metrics.height,
            'tiers': metrics.tiers,
            'step_height': metrics.step_height,
            'base_area': metrics.base_area,
            'top_area': metrics.top_area,
            'lateral_area': metrics.lateral_area,
            'surface_area': metrics.surface_area,
            'volume': metrics.volume,
            'tier_edges': metrics.tier_edges,
        },
        suggested_scale=max(base_edge, height),
    )


class StepPyramidSolidService:
    """Generates payloads for terraced square pyramids."""

    @staticmethod
    def build(base_edge: float = 200.0, top_edge: float = 60.0, height: float = 120.0, tiers: int = 5) -> StepPyramidSolidResult:
        """
        Build logic.
        
        Args:
            base_edge: Description of base_edge.
            top_edge: Description of top_edge.
            height: Description of height.
            tiers: Description of tiers.
        
        Returns:
            Result of build operation.
        """
        metrics = _compute_metrics(base_edge, top_edge, height, tiers)
        payload = _build_payload(base_edge, top_edge, height, tiers)
        return StepPyramidSolidResult(payload=payload, metrics=metrics)

    @staticmethod
    def payload(base_edge: float = 200.0, top_edge: float = 60.0, height: float = 120.0, tiers: int = 5) -> SolidPayload:
        """
        Payload logic.
        
        Args:
            base_edge: Description of base_edge.
            top_edge: Description of top_edge.
            height: Description of height.
            tiers: Description of tiers.
        
        Returns:
            Result of payload operation.
        """
        return StepPyramidSolidService.build(base_edge, top_edge, height, tiers).payload


class StepPyramidSolidCalculator:
    """Calculator for terraced step pyramids."""

    _PROPERTY_DEFINITIONS = (
        ('base_edge', 'Base Edge', 'units', 3, True),
        ('top_edge', 'Top Edge', 'units', 3, True),
        ('height', 'Height', 'units', 3, True),
        ('tiers', 'Tiers', '', 0, True),
        ('step_height', 'Step Height', 'units', 3, False),
        ('base_area', 'Base Area', 'units²', 3, False),
        ('top_area', 'Top Area', 'units²', 3, False),
        ('lateral_area', 'Lateral Area', 'units²', 3, False),
        ('surface_area', 'Surface Area', 'units²', 3, False),
        ('volume', 'Volume', 'units³', 3, False),
    )

    def __init__(self, base_edge: float = 200.0, top_edge: float = 60.0, height: float = 120.0, tiers: int = 5):
        """
          init   logic.
        
        Args:
            base_edge: Description of base_edge.
            top_edge: Description of top_edge.
            height: Description of height.
            tiers: Description of tiers.
        
        """
        self._properties: Dict[str, SolidProperty] = {
            key: SolidProperty(name=label, key=key, unit=unit, precision=precision, editable=editable)
            for key, label, unit, precision, editable in self._PROPERTY_DEFINITIONS
        }
        self._base_edge = base_edge
        self._top_edge = top_edge
        self._height = height
        self._tiers = max(1, int(round(tiers)))
        self._result: Optional[StepPyramidSolidResult] = None
        self._apply_dimensions(self._base_edge, self._top_edge, self._height, self._tiers)

    def properties(self) -> List[SolidProperty]:
        """
        Properties logic.
        
        Returns:
            Result of properties operation.
        """
        return [self._properties[key] for key, *_ in self._PROPERTY_DEFINITIONS]

    def set_property(self, key: str, value: Optional[float]) -> bool:
        """
        Configure property logic.
        
        Args:
            key: Description of key.
            value: Description of value.
        
        Returns:
            Result of set_property operation.
        """
        if value is None or value <= 0:
            return False
        if key == 'base_edge':
            self._apply_dimensions(value, self._top_edge, self._height, self._tiers)
            return True
        if key == 'top_edge':
            if value >= self._base_edge:
                return False
            self._apply_dimensions(self._base_edge, value, self._height, self._tiers)
            return True
        if key == 'height':
            self._apply_dimensions(self._base_edge, self._top_edge, value, self._tiers)
            return True
        if key == 'tiers':
            tiers = max(1, int(round(value)))
            self._apply_dimensions(self._base_edge, self._top_edge, self._height, tiers)
            return True
        return False

    def clear(self):
        """
        Clear logic.
        
        """
        self._base_edge = 200.0
        self._top_edge = 60.0
        self._height = 120.0
        self._tiers = 5
        for prop in self._properties.values():
            prop.value = None
        self._result = None

    def payload(self) -> Optional[SolidPayload]:
        """
        Payload logic.
        
        Returns:
            Result of payload operation.
        """
        return self._result.payload if self._result else None

    def metadata(self) -> Dict[str, float]:
        """
        Metadata logic.
        
        Returns:
            Result of metadata operation.
        """
        if not self._result:
            return {}
        return dict(self._result.payload.metadata)

    def metrics(self) -> Optional[StepPyramidMetrics]:
        """
        Metrics logic.
        
        Returns:
            Result of metrics operation.
        """
        return self._result.metrics if self._result else None

    def _apply_dimensions(self, base_edge: float, top_edge: float, height: float, tiers: int):
        if base_edge <= 0 or top_edge <= 0 or height <= 0 or tiers <= 0 or top_edge >= base_edge:
            return
        self._base_edge = base_edge
        self._top_edge = top_edge
        self._height = height
        self._tiers = tiers
        result = StepPyramidSolidService.build(base_edge, top_edge, height, tiers)
        self._result = result
        values = {
            'base_edge': result.metrics.base_edge,
            'top_edge': result.metrics.top_edge,
            'height': result.metrics.height,
            'tiers': float(result.metrics.tiers),
            'step_height': result.metrics.step_height,
            'base_area': result.metrics.base_area,
            'top_area': result.metrics.top_area,
            'lateral_area': result.metrics.lateral_area,
            'surface_area': result.metrics.surface_area,
            'volume': result.metrics.volume,
        }
        for key, prop in self._properties.items():
            prop.value = values.get(key)


__all__ = [
    'StepPyramidMetrics',
    'StepPyramidSolidResult',
    'StepPyramidSolidService',
    'StepPyramidSolidCalculator',
]