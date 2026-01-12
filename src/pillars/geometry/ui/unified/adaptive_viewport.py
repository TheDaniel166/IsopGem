"""
Adaptive Viewport — ADR-011

A viewport widget that automatically switches between 2D and 3D rendering
based on the dimensional class of the geometry payload.

This is the "eye" of the Unified Geometry Viewer — it sees all forms,
whether flat or volumetric, through the appropriate lens.

Reference: wiki/01_blueprints/decisions/ADR-011_unified_geometry_viewer.md
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from shared.ui.theme import COLORS

if TYPE_CHECKING:
    from .payloads.geometry_payload import GeometryPayload

logger = logging.getLogger(__name__)


class AdaptiveViewport(QFrame):
    """
    Viewport that automatically switches between 2D and 3D rendering.
    
    The viewport contains a QStackedWidget with:
    - Index 0: Placeholder (shown when no payload)
    - Index 1: 2D view (GeometryView + GeometryScene)
    - Index 2: 3D view (Geometry3DView)
    
    When set_payload() is called, the viewport:
    1. Inspects payload.dimensional_class
    2. Activates the appropriate renderer
    3. Passes data to that renderer
    4. Emits payload_changed signal
    
    Signals:
        payload_changed: Emitted when payload is set (GeometryPayload)
        dimension_changed: Emitted when switching 2D↔3D (int: 2 or 3)
        stats_changed: Emitted when geometry stats change (str)
    """
    
    # Signals
    payload_changed = pyqtSignal(object)  # GeometryPayload
    dimension_changed = pyqtSignal(int)  # 2 or 3
    stats_changed = pyqtSignal(str)  # Stats summary string
    
    # Stack indices
    INDEX_PLACEHOLDER = 0
    INDEX_2D = 1
    INDEX_3D = 2
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the adaptive viewport."""
        super().__init__(parent)
        
        self._current_payload: Optional[GeometryPayload] = None
        self._current_dimension: int = 0
        
        # Views (lazily initialized)
        self._view_2d: Optional[QWidget] = None
        self._scene_2d: Optional[object] = None
        self._view_3d: Optional[QWidget] = None
        
        self._setup_ui()
        
        logger.info("AdaptiveViewport initialized")
    
    def _setup_ui(self) -> None:
        """Set up the viewport UI."""
        self.setObjectName("AdaptiveViewport")
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Stacked widget for view switching
        self._stack = QStackedWidget()
        self._stack.setObjectName("ViewportStack")
        
        # Placeholder widget (index 0)
        placeholder = self._create_placeholder()
        self._stack.addWidget(placeholder)
        
        # 2D and 3D views will be added lazily when first needed
        # This avoids importing heavy modules until necessary
        
        layout.addWidget(self._stack)
        
        # Apply minimal styling (let content define appearance)
        self.setStyleSheet(f"""
            QFrame#AdaptiveViewport {{
                background-color: {COLORS['surface']};
                border: none;
            }}
        """)
    
    def _create_placeholder(self) -> QWidget:
        """Create the placeholder widget shown when no payload."""
        placeholder = QFrame()
        placeholder.setObjectName("ViewportPlaceholder")
        
        layout = QVBoxLayout(placeholder)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icon/text placeholder
        label = QLabel("◇")
        label.setObjectName("PlaceholderIcon")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(f"""
            QLabel#PlaceholderIcon {{
                color: {COLORS['text_secondary']};
                font-size: 48px;
            }}
        """)
        
        hint = QLabel("Select a form to visualize")
        hint.setObjectName("PlaceholderHint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet(f"""
            QLabel#PlaceholderHint {{
                color: {COLORS['text_secondary']};
                font-size: 14px;
            }}
        """)
        
        layout.addWidget(label)
        layout.addWidget(hint)
        
        placeholder.setStyleSheet(f"""
            QFrame#ViewportPlaceholder {{
                background-color: {COLORS['surface']};
            }}
        """)
        
        return placeholder
    
    def _ensure_2d_view(self) -> None:
        """Lazily initialize the 2D view."""
        if self._view_2d is not None:
            return
        
        try:
            # Import 2D components
            from ..geometry_scene import GeometryScene
            from ..geometry_view import GeometryView
            
            self._scene_2d = GeometryScene()
            self._view_2d = GeometryView(self._scene_2d)
            
            # Add to stack at index 1
            while self._stack.count() < 2:
                self._stack.addWidget(QWidget())  # Placeholder
            
            self._stack.removeWidget(self._stack.widget(1))
            self._stack.insertWidget(1, self._view_2d)
            
            logger.info("2D view initialized")
            
        except ImportError as e:
            logger.error(f"Failed to initialize 2D view: {e}")
            self._view_2d = QLabel("2D view unavailable")
            self._stack.insertWidget(1, self._view_2d)
    
    def _ensure_3d_view(self) -> None:
        """Lazily initialize the 3D view."""
        if self._view_3d is not None:
            return
        
        try:
            # Import 3D components
            from ..geometry3d.view3d import Geometry3DView
            
            self._view_3d = Geometry3DView()
            
            # Add to stack at index 2
            while self._stack.count() < 3:
                self._stack.addWidget(QWidget())  # Placeholder
            
            self._stack.removeWidget(self._stack.widget(2))
            self._stack.insertWidget(2, self._view_3d)
            
            logger.info("3D view initialized")
            
        except ImportError as e:
            logger.error(f"Failed to initialize 3D view: {e}")
            self._view_3d = QLabel("3D view unavailable")
            self._stack.insertWidget(2, self._view_3d)
    
    # ─────────────────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────────────────
    
    def set_payload(self, payload: GeometryPayload) -> None:
        """
        Set the geometry payload and switch to appropriate renderer.
        
        Args:
            payload: The GeometryPayload to display
        """
        self._current_payload = payload
        
        if payload.is_2d:
            self._show_2d(payload)
        elif payload.is_3d:
            self._show_3d(payload)
        else:
            logger.warning(f"Unknown dimensional class: {payload.dimensional_class}")
            self._show_placeholder()
            return
        
        # Emit signals
        if payload.dimensional_class != self._current_dimension:
            self._current_dimension = payload.dimensional_class
            self.dimension_changed.emit(payload.dimensional_class)
        
        self.payload_changed.emit(payload)
        self.stats_changed.emit(payload.get_stats_summary())
        
        logger.info(f"Payload set: {payload.form_type} ({payload.dimensional_class}D)")
    
    def clear(self) -> None:
        """Clear the viewport and show placeholder."""
        self._current_payload = None
        self._current_dimension = 0
        self._show_placeholder()
        self.stats_changed.emit("")
    
    def get_current_payload(self) -> Optional[GeometryPayload]:
        """Return the current payload."""
        return self._current_payload
    
    def get_current_dimension(self) -> int:
        """Return current dimension (0 if no payload, 2 or 3 otherwise)."""
        return self._current_dimension
    
    def is_2d_active(self) -> bool:
        """Return True if 2D view is currently active."""
        return self._stack.currentIndex() == self.INDEX_2D
    
    def is_3d_active(self) -> bool:
        """Return True if 3D view is currently active."""
        return self._stack.currentIndex() == self.INDEX_3D
    
    # ─────────────────────────────────────────────────────────────────
    # View Switching
    # ─────────────────────────────────────────────────────────────────
    
    def _show_placeholder(self) -> None:
        """Show the placeholder view."""
        self._stack.setCurrentIndex(self.INDEX_PLACEHOLDER)
    
    def _show_2d(self, payload: GeometryPayload) -> None:
        """Show 2D view with the given payload."""
        self._ensure_2d_view()
        
        if payload.scene_payload is not None and self._scene_2d is not None:
            # Set the scene payload
            if hasattr(self._scene_2d, "set_payload"):
                self._scene_2d.set_payload(payload.scene_payload)
            elif hasattr(self._scene_2d, "render_payload"):
                self._scene_2d.render_payload(payload.scene_payload)
            else:
                logger.warning("2D scene has no set_payload or render_payload method")
        
        self._stack.setCurrentIndex(self.INDEX_2D)
    
    def _show_3d(self, payload: GeometryPayload) -> None:
        """Show 3D view with the given payload."""
        self._ensure_3d_view()
        
        if payload.solid_payload is not None and self._view_3d is not None:
            # Set the solid payload
            if hasattr(self._view_3d, "set_payload"):
                self._view_3d.set_payload(payload.solid_payload)
            else:
                logger.warning("3D view has no set_payload method")
        
        self._stack.setCurrentIndex(self.INDEX_3D)
    
    # ─────────────────────────────────────────────────────────────────
    # View Controls (forwarded to active view)
    # ─────────────────────────────────────────────────────────────────
    
    def set_axes_visible(self, visible: bool) -> None:
        """Set axes visibility on the active view."""
        if self.is_2d_active() and self._scene_2d is not None:
            if hasattr(self._scene_2d, "set_axes_visible"):
                self._scene_2d.set_axes_visible(visible)
        elif self.is_3d_active() and self._view_3d is not None:
            if hasattr(self._view_3d, "set_axes_visible"):
                self._view_3d.set_axes_visible(visible)
    
    def set_labels_visible(self, visible: bool) -> None:
        """Set labels visibility on the active view."""
        if self.is_2d_active() and self._scene_2d is not None:
            if hasattr(self._scene_2d, "set_labels_visible"):
                self._scene_2d.set_labels_visible(visible)
        elif self.is_3d_active() and self._view_3d is not None:
            if hasattr(self._view_3d, "set_labels_visible"):
                self._view_3d.set_labels_visible(visible)
    
    def reset_view(self) -> None:
        """Reset the view (zoom, pan, rotation) to default."""
        if self.is_2d_active() and self._view_2d is not None:
            if hasattr(self._view_2d, "fit_in_view"):
                self._view_2d.fit_in_view()
            elif hasattr(self._view_2d, "reset_view"):
                self._view_2d.reset_view()
        elif self.is_3d_active() and self._view_3d is not None:
            if hasattr(self._view_3d, "reset_view"):
                self._view_3d.reset_view()
    
    def take_snapshot(self) -> Optional[object]:  # QPixmap
        """Take a snapshot of the current view."""
        if self.is_2d_active() and self._view_2d is not None:
            return self._view_2d.grab()
        elif self.is_3d_active() and self._view_3d is not None:
            return self._view_3d.grab()
        return None
    
    # ─────────────────────────────────────────────────────────────────
    # 3D-Specific Controls
    # ─────────────────────────────────────────────────────────────────
    
    def set_elevation(self, degrees: float) -> None:
        """Set camera elevation/pitch (3D only)."""
        if self.is_3d_active() and self._view_3d is not None:
            # Geometry3DView uses pitch for elevation
            if hasattr(self._view_3d, "set_camera_angles"):
                # Get current yaw, update pitch
                current_yaw = getattr(self._view_3d._camera, "yaw_deg", 30.0)
                self._view_3d.set_camera_angles(current_yaw, degrees)
    
    def set_azimuth(self, degrees: float) -> None:
        """Set camera azimuth/yaw (3D only)."""
        if self.is_3d_active() and self._view_3d is not None:
            # Geometry3DView uses yaw for azimuth
            if hasattr(self._view_3d, "set_camera_angles"):
                # Get current pitch, update yaw
                current_pitch = getattr(self._view_3d._camera, "pitch_deg", 25.0)
                self._view_3d.set_camera_angles(degrees, current_pitch)
    
    def set_camera_angles(self, yaw: float, pitch: float) -> None:
        """Set both camera angles at once (3D only)."""
        if self.is_3d_active() and self._view_3d is not None:
            if hasattr(self._view_3d, "set_camera_angles"):
                self._view_3d.set_camera_angles(yaw, pitch)
    
    def set_show_faces(self, visible: bool) -> None:
        """Set face visibility (3D only)."""
        if self.is_3d_active() and self._view_3d is not None:
            if hasattr(self._view_3d, "set_faces_visible"):
                self._view_3d.set_faces_visible(visible)

    def set_show_edges(self, visible: bool) -> None:
        """Set edge visibility (3D only)."""
        if self.is_3d_active() and self._view_3d is not None:
            if hasattr(self._view_3d, "set_edges_visible"):
                self._view_3d.set_edges_visible(visible)
    
    def set_show_vertices(self, visible: bool) -> None:
        """Set vertex visibility (2D highlights or 3D vertices)."""
        if self.is_2d_active() and self._view_2d is not None:
            scene = getattr(self._view_2d, "scene", lambda: None)()
            if hasattr(scene, "set_vertex_highlights_visible"):
                scene.set_vertex_highlights_visible(visible)  # type: ignore[arg-type]
        elif self.is_3d_active() and self._view_3d is not None:
            if hasattr(self._view_3d, "set_vertices_visible"):
                self._view_3d.set_vertices_visible(visible)
    
    def set_dual_visible(self, visible: bool) -> None:
        """Set dual solid visibility (3D only)."""
        if self.is_3d_active() and self._view_3d is not None:
            if hasattr(self._view_3d, "set_dual_visible"):
                self._view_3d.set_dual_visible(visible)
    
    def set_sphere_visible(self, sphere_key: str, visible: bool) -> None:
        """Set sphere visibility (3D) or circle overlays (2D)."""
        if self.is_2d_active() and self._view_2d is not None:
            scene = getattr(self._view_2d, "scene", lambda: None)()
            if hasattr(scene, "set_circle_visibility"):
                    role = sphere_key
                    if sphere_key == "circumsphere":
                        role = "circumcircle"
                    elif sphere_key == "incircle":
                        role = "incircle"
                    else:
                        role = sphere_key
                    scene.set_circle_visibility(role, visible)  # type: ignore[arg-type]
        elif self.is_3d_active() and self._view_3d is not None:
            if hasattr(self._view_3d, "set_sphere_visible"):
                self._view_3d.set_sphere_visible(sphere_key, visible)
    
    def set_measure_mode(self, enabled: bool) -> None:
        """Enable/disable measure mode (2D/3D)."""
        if self.is_2d_active() and self._view_2d is not None:
            if hasattr(self._view_2d, "set_measurement_mode"):
                self._view_2d.set_measurement_mode(enabled)
        elif self.is_3d_active() and self._view_3d is not None:
            if hasattr(self._view_3d, "set_measure_mode"):
                self._view_3d.set_measure_mode(enabled)
    
    def zoom_in(self) -> None:
        """Zoom in on the viewport."""
        if self.is_2d_active() and self._view_2d is not None:
            if hasattr(self._view_2d, "zoom_in"):
                self._view_2d.zoom_in()
            elif hasattr(self._view_2d, "scale"):
                self._view_2d.scale(1.2, 1.2)
        elif self.is_3d_active() and self._view_3d is not None:
            if hasattr(self._view_3d, "zoom_in"):
                self._view_3d.zoom_in()
            elif hasattr(self._view_3d, "adjust_zoom"):
                self._view_3d.adjust_zoom(-2.0)  # Negative = closer
    
    def zoom_out(self) -> None:
        """Zoom out on the viewport."""
        if self.is_2d_active() and self._view_2d is not None:
            if hasattr(self._view_2d, "zoom_out"):
                self._view_2d.zoom_out()
            elif hasattr(self._view_2d, "scale"):
                self._view_2d.scale(1/1.2, 1/1.2)
        elif self.is_3d_active() and self._view_3d is not None:
            if hasattr(self._view_3d, "zoom_out"):
                self._view_3d.zoom_out()
            elif hasattr(self._view_3d, "adjust_zoom"):
                self._view_3d.adjust_zoom(2.0)  # Positive = farther
    
    def fit_to_view(self) -> None:
        """Fit the geometry to the viewport."""
        if self.is_2d_active() and self._view_2d is not None:
            if hasattr(self._view_2d, "fit_in_view"):
                self._view_2d.fit_in_view()
        elif self.is_3d_active() and self._view_3d is not None:
            if hasattr(self._view_3d, "fit_to_solid"):
                self._view_3d.fit_to_solid()
    
    # ─────────────────────────────────────────────────────────────────
    # Direct View Access (for advanced use)
    # ─────────────────────────────────────────────────────────────────
    
    def get_2d_view(self) -> Optional[QWidget]:
        """Get the 2D view widget (may be None if not initialized)."""
        return self._view_2d
    
    def get_2d_scene(self) -> Optional[object]:
        """Get the 2D scene (may be None if not initialized)."""
        return self._scene_2d
    
    def get_3d_view(self) -> Optional[QWidget]:
        """Get the 3D view widget (may be None if not initialized)."""
        return self._view_3d
