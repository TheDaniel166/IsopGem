"""
THE EYE OF THE ADYTON (Camera System)

"One is the index that charted the course."

This module handles the 6-DOF navigation within the Sanctuary.
Since we are using Software Rasterization, the Camera is responsible for
generating the View and Projection matrices.
"""
from dataclasses import dataclass, field
import math
from PyQt6.QtGui import QMatrix4x4, QVector3D

@dataclass
class AdytonCamera:
    """
    The Virtual Eye.
    Handles position (Eye), target (LookAt), and Up vector.
    """
    # Position (Spherical Coordinates for Orbit)
    radius: float = 800.0  # Initial distance from center
    theta: float = 45.0    # Pitch (degrees from vertical)
    phi: float = 45.0      # Yaw (degrees around vertical)
    
    # Target (Where we look)
    target: QVector3D = field(default_factory=lambda: QVector3D(0, 0, 0))
    
    # Field of View
    fov: float = 60.0

    def view_matrix(self) -> QMatrix4x4:
        """Calculates the View Matrix (World -> Camera)."""
        eye = self.position()
        matrix = QMatrix4x4()
        matrix.lookAt(eye, self.target, QVector3D(0, 1, 0))
        return matrix

    def position(self) -> QVector3D:
        """Converts spherical coordinates to Cartesian."""
        rad_theta = math.radians(self.theta)
        rad_phi = math.radians(self.phi)
        
        # Standard Spherical to Cartesian (Y-up)
        # x = r * sin(theta) * sin(phi)
        # y = r * cos(theta)
        # z = r * sin(theta) * cos(phi)
        
        y = self.radius * math.cos(rad_theta)
        x = self.radius * math.sin(rad_theta) * math.sin(rad_phi)
        z = self.radius * math.sin(rad_theta) * math.cos(rad_phi)
        
        return QVector3D(x, y, z)

    def orbit(self, d_phi: float, d_theta: float):
        """Orbits the camera around the target."""
        self.phi += d_phi
        self.theta = max(1.0, min(179.0, self.theta + d_theta))

    def zoom(self, delta: float):
        """Moves camera closer/further."""
        self.radius = max(50.0, self.radius - delta)

    def pan(self, dx: float, dy: float):
        """Pans the camera target (Moves the world)."""
        # Right Vector (Cross product of Forward and Up)
        eye = self.position()
        forward = (self.target - eye).normalized()
        up = QVector3D(0, 1, 0)
        right = QVector3D.crossProduct(forward, up).normalized()
        
        # Re-calc Up (True camera up)
        cam_up = QVector3D.crossProduct(right, forward).normalized()
        
        self.target += (right * dx) + (cam_up * dy)
