"""3D Figurate Numbers: Tetrahedral, Pyramidal, Octahedral, Cubic.

This module provides formulas and point generation for 3D figurate numbers,
along with isometric projection for 2D visualization.
"""
from __future__ import annotations
import math
from typing import List, Tuple


# -----------------------------------------------------------------------------
# Isometric Projection
# -----------------------------------------------------------------------------
def isometric_project(x: float, y: float, z: float) -> Tuple[float, float]:
    """Project 3D coordinates to 2D isometric view.
    
    X axis: right-down at 30°
    Y axis: left-down at 30°
    Z axis: straight up
    """
    # Standard isometric angles
    angle = math.pi / 6  # 30 degrees
    
    # Project to 2D
    screen_x = (x - y) * math.cos(angle)
    screen_y = (x + y) * math.sin(angle) - z
    
    return (screen_x, screen_y)


# -----------------------------------------------------------------------------
# Tetrahedral Numbers
# -----------------------------------------------------------------------------
def tetrahedral_number(n: int) -> int:
    """Calculate the n-th tetrahedral number.
    
    Formula: n(n+1)(n+2)/6
    Sequence: 1, 4, 10, 20, 35, 56, 84, 120, ...
    """
    if n < 1:
        return 0
    return n * (n + 1) * (n + 2) // 6


def tetrahedral_points(n: int, spacing: float = 1.0) -> List[Tuple[float, float, float]]:
    """Generate 3D coordinates for a tetrahedral arrangement.
    
    Builds triangular layers stacked vertically.
    """
    points = []
    
    # Pre-calculate layer offsets to ensure perfect centering
    # For a regular tetrahedron of spheres, the centroid of each layer
    # should align with the Z-axis (x=0, y=0).
    
    for layer in range(n):
        layer_size = layer + 1
        z = layer * spacing * 0.816  # Height of regular tetrahedron
        
        # 1. Generate local layer points
        layer_points = []
        for row in range(layer_size):
            for col in range(row + 1):
                # Triangular grid coordinates
                # x grows with col
                # y grows with row
                # We start with a generic corner alignment
                raw_x = (col - row / 2.0) * spacing
                raw_y = row * spacing * 0.866 # sqrt(3)/2
                layer_points.append((raw_x, raw_y, z))
        
        # 2. Calculate Centroid
        if not layer_points:
            continue
            
        avg_x = sum(p[0] for p in layer_points) / len(layer_points)
        avg_y = sum(p[1] for p in layer_points) / len(layer_points)
        
        # 3. Center the layer
        for lx, ly, lz in layer_points:
            points.append((lx - avg_x, ly - avg_y, lz))
    
    return points


# -----------------------------------------------------------------------------
# Pyramidal Numbers (Square base)
# -----------------------------------------------------------------------------
def square_pyramidal_number(n: int) -> int:
    """Calculate the n-th square pyramidal number.
    
    Formula: n(n+1)(2n+1)/6
    Sequence: 1, 5, 14, 30, 55, 91, 140, ...
    """
    if n < 1:
        return 0
    return n * (n + 1) * (2 * n + 1) // 6


def square_pyramidal_points(n: int, spacing: float = 1.0) -> List[Tuple[float, float, float]]:
    """Generate 3D coordinates for a square pyramidal arrangement.
    
    Builds square layers stacked vertically, each smaller than the one below.
    """
    points = []
    
    # Generate from Top (Apex) to Bottom (Base)
    # So that the first point (Index 1) is at the top.
    
    for i in range(n):
        # i=0 -> Apex (Top layer)
        # i=n-1 -> Base (Bottom layer)
        
        # Logical layer index from top 
        # Size grows as we go down: 1x1, 2x2, ...
        layer_width = i + 1
        
        # Z coordinate goes from High to Low
        z = (n - 1 - i) * spacing
        
        # Center the layer
        offset = (layer_width - 1) / 2.0
        
        for row in range(layer_width):
            for col in range(layer_width):
                x = (col - offset) * spacing
                y = (row - offset) * spacing
                points.append((x, y, z))
    
    return points


# -----------------------------------------------------------------------------
# Octahedral Numbers
# -----------------------------------------------------------------------------
def octahedral_number(n: int) -> int:
    """Calculate the n-th octahedral number.
    
    Formula: n(2n² + 1)/3
    Sequence: 1, 6, 19, 44, 85, 146, ...
    """
    if n < 1:
        return 0
    return n * (2 * n * n + 1) // 3


def octahedral_points(n: int, spacing: float = 1.0) -> List[Tuple[float, float, float]]:
    """Generate 3D coordinates for an octahedral arrangement.
    
    Two square pyramids joined at the base.
    """
    points = []
    
    # An Octahedral number of order n can be visualized as two square pyramids
    # of order n and n-1 joined at their bases.
    # To look like a solid octahedron, we should center the shared base (size n)
    # at z=0, and stack smaller layers above and below.
    
    # 1. Middle Layer (Base) - Size N x N
    # z = 0
    # Construct:
    mid_size = n
    mid_offset = (mid_size - 1) / 2.0
    for row in range(mid_size):
        for col in range(mid_size):
            points.append((
                (col - mid_offset) * spacing,
                (row - mid_offset) * spacing,
                0.0
            ))
            
    # 2. Symmetric Upper and Lower Pyramids
    # Layers decrease size from (N-1) down to 1
    for i in range(1, n):
        layer_size = n - i
        offset = (layer_size - 1) / 2.0
        
        # Upper Layer (+Z)
        z_up = i * spacing * 0.816 # Scale height for better proportions? Or just spacing.
        # Regular octahedron: height of pyramid = base_width / sqrt(2). 
        # spacing * (n)/sqrt(2)? Let's stick to spacing for integer grid first.
        # User accepted spacing for cube, but octahedron might look better scaled.
        # Let's use simple spacing for now to match other figures.
        z_up = i * spacing
        
        # Lower Layer (-Z)
        z_down = -i * spacing
        
        for row in range(layer_size):
            for col in range(layer_size):
                x = (col - offset) * spacing
                y = (row - offset) * spacing
                
                # Add Top Point
                points.append((x, y, z_up))
                
                # Add Bottom Point
                points.append((x, y, z_down))

    return points


# -----------------------------------------------------------------------------
# Cubic Numbers
# -----------------------------------------------------------------------------
def cubic_number(n: int) -> int:
    """Calculate the n-th cubic number.
    
    Formula: n³
    Sequence: 1, 8, 27, 64, 125, ...
    """
    if n < 1:
        return 0
    return n ** 3


def cubic_points(n: int, spacing: float = 1.0) -> List[Tuple[float, float, float]]:
    """Generate 3D coordinates for a cubic arrangement."""
    points = []
    offset = (n - 1) / 2
    
    for z in range(n):
        for y in range(n):
            for x in range(n):
                points.append((
                    (x - offset) * spacing,
                    (y - offset) * spacing,
                    (z - offset) * spacing
                ))
    
    return points


# -----------------------------------------------------------------------------
# Centered Cubic Numbers
# -----------------------------------------------------------------------------
def centered_cubic_number(n: int) -> int:
    """Calculate the n-th centered cubic number.
    
    Formula: (2n-1)³ - (2n-2)³ for shell, or cumulative
    Actually: n³ + (n-1)³ for n >= 1, or 2n³ - 3n² + 3n - 1
    Sequence: 1, 9, 35, 91, 189, ...
    """
    if n < 1:
        return 0
    # Centered cube: points at integer coords where |x|+|y|+|z| follows a pattern
    # Simpler: (2n-1)³ total points in a cube of side 2n-1
    return (2 * n - 1) ** 3


# -----------------------------------------------------------------------------
# Helper: Project all points
# -----------------------------------------------------------------------------
def project_points_isometric(points_3d: List[Tuple[float, float, float]]) -> List[Tuple[float, float]]:
    """Project a list of 3D points to 2D isometric coordinates."""
    return [isometric_project(x, y, z) for x, y, z in points_3d]


# -----------------------------------------------------------------------------
# Layer coloring helper
# -----------------------------------------------------------------------------
def project_dynamic(
    points_3d: List[Tuple[float, float, float]],
    yaw_deg: float,
    pitch_deg: float
) -> List[Tuple[float, float]]:
    """Project points using dynamic Yaw/Pitch angles.
    
    Yaw: Rotation around Z axis (Up).
    Pitch: Rotation around effective X axis.
    """
    yaw = math.radians(yaw_deg)
    pitch = math.radians(pitch_deg)
    
    cy, sy = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    
    projected = []
    for x, y, z in points_3d:
        # 1. Yaw (World Rotation)
        x1 = x * cy - y * sy
        y1 = x * sy + y * cy
        z1 = z
        
        # 2. Pitch (Camera Tilt)
        # Rotate around X axis
        # y becomes depth, z becomes screen Y
        y2 = y1 * cp - z1 * sp
        z2 = y1 * sp + z1 * cp
        
        # 3. Project Orthographically
        # Screen X = x1
        # Screen Y = -z2 (Z is Up in World, Y is Down in Screen)
        projected.append((x1, -z2))
        
    return projected


def get_layer_for_point(point_3d: Tuple[float, float, float], spacing: float = 1.0) -> int:
    """Determine which layer (z-level) a point belongs to."""
    return int(round(point_3d[2] / spacing))


__all__ = [
    "isometric_project",
    "project_points_isometric",
    "project_dynamic",
    "tetrahedral_number",
    "tetrahedral_points",
    "square_pyramidal_number",
    "square_pyramidal_points",
    "octahedral_number",
    "octahedral_points",
    "cubic_number",
    "cubic_points",
    "centered_cubic_number",
    "get_layer_for_point",
]
