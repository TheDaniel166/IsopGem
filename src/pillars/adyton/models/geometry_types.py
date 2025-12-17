"""
CORE GEOMETRY TYPES

Shared data structures for 3D objects to avoid circular imports between UI and Models.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from PyQt6.QtGui import QVector3D, QColor, QMatrix4x4

@dataclass
class Face3D:
    """A single polygon in 3D space."""
    vertices: List[QVector3D]
    color: QColor = field(default_factory=lambda: QColor(200, 200, 200))
    outline_color: QColor = field(default_factory=lambda: QColor(50, 50, 50))
    centroid: QVector3D = field(init=False)

    def __post_init__(self):
        self.recalculate_centroid()

    def recalculate_centroid(self):
        """Calculates geometric center for depth sorting."""
        if not self.vertices:
            self.centroid = QVector3D(0, 0, 0)
            return
        
        sum_vec = QVector3D(0, 0, 0)
        for v in self.vertices:
            sum_vec += v
        self.centroid = sum_vec / len(self.vertices)

@dataclass
class Object3D:
    """A collection of faces (e.g., a Block or Wall)."""
    faces: List[Face3D] = field(default_factory=list)
    position: QVector3D = field(default_factory=lambda: QVector3D(0, 0, 0))
    rotation: QVector3D = field(default_factory=lambda: QVector3D(0, 0, 0)) # Euler angles
    scale: QVector3D = field(default_factory=lambda: QVector3D(1, 1, 1))
    label_positions: Optional[List[QVector3D]] = None
    label_colors: Optional[List[QColor]] = None
    label_planets: Optional[List[str]] = None
    
    # Cache for transformed faces
    _world_faces: List[Face3D] = field(default_factory=list, repr=False)
    _last_position: QVector3D = field(default_factory=lambda: QVector3D(0, 0, 0), repr=False)
    _last_rotation: QVector3D = field(default_factory=lambda: QVector3D(0, 0, 0), repr=False)
    _last_scale: QVector3D = field(default_factory=lambda: QVector3D(1, 1, 1), repr=False)

    def update_world_transform(self):
        """Applies basic TRS matrix to faces, skipping work if nothing moved."""
        if (
            self._world_faces
            and self.position == self._last_position
            and self.rotation == self._last_rotation
            and self.scale == self._last_scale
        ):
            return

        matrix = QMatrix4x4()
        matrix.translate(self.position)
        matrix.rotate(self.rotation.x(), 1, 0, 0)
        matrix.rotate(self.rotation.y(), 0, 1, 0)
        matrix.rotate(self.rotation.z(), 0, 0, 1)
        matrix.scale(self.scale)

        self._world_faces = []
        for face in self.faces:
            transformed_verts = [matrix * v for v in face.vertices]
            new_face = Face3D(vertices=transformed_verts, color=face.color, outline_color=face.outline_color)
            self._world_faces.append(new_face)

        self._last_position = QVector3D(self.position)
        self._last_rotation = QVector3D(self.rotation)
        self._last_scale = QVector3D(self.scale)
