"""
THE STAGE OF THE ADYTON (Scene Graph)

"It is a chamber, a vault, a camera."

This module defines the data structures for the 3D objects in the Sanctuary.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from PyQt6.QtGui import QVector3D, QColor, QMatrix4x4
from pillars.adyton.models.geometry_types import Face3D, Object3D

@dataclass
class AdytonScene:
    """The Container of the Sanctuary."""
    objects: List[Object3D] = field(default_factory=list)
    background_color: QColor = field(default_factory=lambda: QColor(10, 10, 15))

    def add_object(self, obj: Object3D):
        self.objects.append(obj)
        
    def clear(self):
        self.objects.clear()
    
    def get_all_faces(self) -> List[Face3D]:
        """Flattens scene into a list of world-space faces for the renderer."""
        all_faces = []
        for obj in self.objects:
            # Assume update_world_transform is called before render or automatically
            # For simplicity, we can call it here or manage dirty flags
            obj.update_world_transform() 
            all_faces.extend(obj._world_faces)
        return all_faces
