"""
Unified Geometry Viewer — ADR-011

A single, Canon-compliant viewer for both 2D shapes and 3D solids.
Provides adaptive rendering, calculation history, and unified Canon integration.

Reference: wiki/01_blueprints/decisions/ADR-011_unified_geometry_viewer.md
"""

from .payloads.geometry_payload import GeometryPayload
from .history.history_entry import HistoryEntry
from .history.history_manager import DeclarationHistory
from .adaptive_viewport import AdaptiveViewport
from .unified_viewer import UnifiedGeometryViewer

__all__ = [
    "GeometryPayload",
    "HistoryEntry",
    "DeclarationHistory",
    "AdaptiveViewport",
    "UnifiedGeometryViewer",
]
