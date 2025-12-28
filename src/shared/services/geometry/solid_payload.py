"""Shared 3D solid payload structures."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

Vec3 = Tuple[float, float, float]
Vertex = Vec3
Edge = Tuple[int, int]
Face = Sequence[int]


@dataclass
class SolidLabel:
    text: str
    position: Vec3
    align_center: bool = True


@dataclass
class SolidPayload:
    vertices: List[Vec3] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    faces: List[Face] = field(default_factory=list)
    labels: List[SolidLabel] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    face_colors: List[Optional[Tuple[int, int, int, int]]] = field(default_factory=list)
    suggested_scale: Optional[float] = None

    def __init__(
        self,
        *,
        vertices: Optional[List[Vec3]] = None,
        edges: Optional[List[Edge]] = None,
        faces: Optional[List[Face]] = None,
        labels: Optional[List[SolidLabel]] = None,
        metadata: Optional[dict] = None,
        face_colors: Optional[List[Optional[Tuple[int, int, int, int]]]] = None,
        suggested_scale: Optional[float] = None,
        dual: Optional['SolidPayload'] = None,
    ) -> None:
        self.vertices = list(vertices) if vertices is not None else []
        self.edges = list(edges) if edges is not None else []
        self.faces = list(faces) if faces is not None else []
        self.labels = list(labels) if labels is not None else []
        self.metadata = dict(metadata) if metadata is not None else {}
        self.face_colors = list(face_colors) if face_colors is not None else []
        self.suggested_scale = suggested_scale
        self.dual = dual

    def bounds(self) -> Optional[Tuple[Vec3, Vec3]]:
        if not self.vertices:
            return None
        xs = [v[0] for v in self.vertices]
        ys = [v[1] for v in self.vertices]
        zs = [v[2] for v in self.vertices]
        return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))
