"""
Unified Geometry Payload — ADR-011

A dimension-agnostic payload structure that can hold either 2D drawing
instructions or 3D solid data, along with Canon provenance information.

This replaces the need for separate payload types in different viewers.

Reference: wiki/01_blueprints/decisions/ADR-011_unified_geometry_viewer.md
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from shared.services.geometry.solid_payload import SolidPayload
    from ..primitives import GeometryScenePayload

logger = logging.getLogger(__name__)


@dataclass
class GeometryPayload:
    """
    Unified output from Canon realization (2D or 3D).
    
    This payload serves as the single data structure that flows from
    Canon realization to the AdaptiveViewport. The viewport inspects
    `dimensional_class` to determine which renderer to activate.
    
    Attributes:
        dimensional_class: 2 for shapes (2D), 3 for solids (3D)
        scene_payload: 2D drawing primitives (populated if dim=2)
        solid_payload: 3D mesh data (populated if dim=3)
        metadata: Form-specific metadata (name, properties, etc.)
        provenance: Canon provenance (signature, timestamp, verdict summary)
    
    Invariants:
        - Exactly one of scene_payload or solid_payload should be populated
        - dimensional_class must match the populated payload type
    """
    
    dimensional_class: int
    
    # 2D data (populated if dimensional_class == 2)
    scene_payload: Optional[Any] = None  # GeometryScenePayload
    
    # 3D data (populated if dimensional_class == 3)
    solid_payload: Optional[Any] = None  # SolidPayload
    
    # Always present
    metadata: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)
    
    # Cached signature
    _signature: Optional[str] = field(default=None, repr=False, compare=False)
    
    @property
    def is_2d(self) -> bool:
        """Return True if this is a 2D geometry payload."""
        return self.dimensional_class == 2
    
    @property
    def is_3d(self) -> bool:
        """Return True if this is a 3D geometry payload."""
        return self.dimensional_class == 3
    
    @property
    def form_type(self) -> str:
        """Return the Canon form type (e.g., 'Circle', 'VaultOfHestia')."""
        return self.metadata.get("form_type", "Unknown")
    
    @property
    def title(self) -> str:
        """Return the display title."""
        return self.metadata.get("title", self.form_type)
    
    @property
    def declaration_signature(self) -> Optional[str]:
        """Return the Canon declaration signature if available."""
        return self.provenance.get("signature")
    
    @property
    def validation_status(self) -> str:
        """Return validation status: 'passed', 'warnings', 'failed', or 'unknown'."""
        return self.provenance.get("status", "unknown")
    
    @property
    def created_at(self) -> Optional[datetime]:
        """Return creation timestamp if available."""
        ts = self.provenance.get("timestamp")
        if isinstance(ts, datetime):
            return ts
        if isinstance(ts, str):
            try:
                return datetime.fromisoformat(ts)
            except ValueError:
                return None
        return None
    
    def get_signature(self) -> str:
        """
        Compute a stable signature for this payload.
        
        Used for history deduplication and comparison.
        """
        if self._signature is not None:
            return self._signature
        
        # Build signature from key identifying data
        sig_data = {
            "dim": self.dimensional_class,
            "form_type": self.form_type,
            "params": self.metadata.get("params", {}),
        }
        
        sig_str = json.dumps(sig_data, sort_keys=True, default=str)
        sig_hash = hashlib.sha256(sig_str.encode()).hexdigest()[:16]
        
        # Cache it (mutable field despite frozen appearance)
        object.__setattr__(self, "_signature", sig_hash)
        return sig_hash
    
    def get_vertex_count(self) -> int:
        """Return the number of vertices in this geometry."""
        if self.is_3d and self.solid_payload is not None:
            return len(getattr(self.solid_payload, "vertices", []))
        if self.is_2d and self.scene_payload is not None:
            # Count vertices from polygon primitives
            count = 0
            primitives = getattr(self.scene_payload, "primitives", [])
            for prim in primitives:
                if hasattr(prim, "points"):
                    count += len(prim.points)
            return count
        return 0
    
    def get_edge_count(self) -> int:
        """Return the number of edges in this geometry."""
        if self.is_3d and self.solid_payload is not None:
            return len(getattr(self.solid_payload, "edges", []))
        return 0
    
    def get_face_count(self) -> int:
        """Return the number of faces in this geometry."""
        if self.is_3d and self.solid_payload is not None:
            return len(getattr(self.solid_payload, "faces", []))
        return 0
    
    def get_stats_summary(self) -> str:
        """Return a short stats summary string."""
        if self.is_3d:
            v = self.get_vertex_count()
            e = self.get_edge_count()
            f = self.get_face_count()
            return f"{v}v · {e}e · {f}f"
        elif self.is_2d:
            v = self.get_vertex_count()
            return f"{v} vertices"
        return ""
    
    @classmethod
    def from_solid_payload(
        cls,
        solid: Any,  # SolidPayload
        *,
        form_type: str = "Unknown",
        title: Optional[str] = None,
        params: Optional[dict] = None,
        signature: Optional[str] = None,
        validation_status: str = "unknown",
    ) -> "GeometryPayload":
        """
        Create a GeometryPayload from a SolidPayload.
        
        Factory method for 3D geometry.
        """
        metadata = {
            "form_type": form_type,
            "title": title or form_type,
            "params": params or {},
        }
        
        # Copy metadata from solid if available
        if hasattr(solid, "metadata") and solid.metadata:
            metadata.update(solid.metadata)
            if "form_type" not in metadata or metadata["form_type"] == "Unknown":
                metadata["form_type"] = solid.metadata.get("name", form_type)
        
        provenance = {
            "signature": signature,
            "status": validation_status,
            "timestamp": datetime.now().isoformat(),
        }
        
        return cls(
            dimensional_class=3,
            solid_payload=solid,
            metadata=metadata,
            provenance=provenance,
        )
    
    @classmethod
    def from_scene_payload(
        cls,
        scene: Any,  # GeometryScenePayload
        *,
        form_type: str = "Unknown",
        title: Optional[str] = None,
        params: Optional[dict] = None,
        signature: Optional[str] = None,
        validation_status: str = "unknown",
    ) -> "GeometryPayload":
        """
        Create a GeometryPayload from a GeometryScenePayload.
        
        Factory method for 2D geometry.
        """
        metadata = {
            "form_type": form_type,
            "title": title or form_type,
            "params": params or {},
        }
        
        provenance = {
            "signature": signature,
            "status": validation_status,
            "timestamp": datetime.now().isoformat(),
        }
        
        return cls(
            dimensional_class=2,
            scene_payload=scene,
            metadata=metadata,
            provenance=provenance,
        )
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert to a JSON-serializable dictionary.
        
        Note: Payload data (scene/solid) is summarized, not fully serialized.
        """
        return {
            "dimensional_class": self.dimensional_class,
            "form_type": self.form_type,
            "title": self.title,
            "metadata": self.metadata,
            "provenance": self.provenance,
            "stats": {
                "vertices": self.get_vertex_count(),
                "edges": self.get_edge_count() if self.is_3d else None,
                "faces": self.get_face_count() if self.is_3d else None,
            },
            "signature": self.get_signature(),
        }
