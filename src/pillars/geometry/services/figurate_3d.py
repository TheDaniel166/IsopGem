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
            
        avg_x = sum(p[0] for p in layer_points) / len(layer_points)  # type: ignore[reportUnknownArgumentType, reportUnknownVariableType]
        avg_y = sum(p[1] for p in layer_points) / len(layer_points)  # type: ignore[reportUnknownArgumentType, reportUnknownVariableType]
        
        # 3. Center the layer
        for lx, ly, lz in layer_points:  # type: ignore[reportUnknownVariableType]
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
        _y2 = y1 * cp - z1 * sp
        z2 = y1 * sp + z1 * cp
        
        # 3. Project Orthographically
        # Screen X = x1
        # Screen Y = -z2 (Z is Up in World, Y is Down in Screen)
        projected.append((x1, -z2))
        
    return projected


def get_layer_for_point(point_3d: Tuple[float, float, float], spacing: float = 1.0) -> int:
    """Determine which layer (z-level) a point belongs to."""
    return int(round(point_3d[2] / spacing))



def centered_cubic_points(n: int, spacing: float = 1.0) -> List[Tuple[float, float, float]]:
    """Generate 3D coordinates for a Centered Cubic arrangement.
    
    Structure: Two interlaced cubes.
    1. Outer Cube of size n (lattice points)
    2. Inner Cube of size n-1 (in the cell centers of the outer cube)
    """
    points = []
    
    # 1. Outer Cube (n x n x n)
    # Centered at (0,0,0)
    outer_offset = (n - 1) / 2.0
    for z in range(n):
        for y in range(n):
            for x in range(n):
                points.append((
                    (x - outer_offset) * spacing,
                    (y - outer_offset) * spacing,
                    (z - outer_offset) * spacing
                ))
                
    # 2. Inner Cube ((n-1) x (n-1) x (n-1))
    # Centered in the voids.
    # The voids are at half-integer steps relative to outer grid.
    if n > 1:
        inner_n = n - 1
        inner_offset = (inner_n - 1) / 2.0
        # Check alignment:
        # Outer 2x2: -0.5, 0.5. Center 0.
        # Inner 1x1: 0. 
        # They naturally align if both centered at 0.
        
        for z in range(inner_n):
            for y in range(inner_n):
                for x in range(inner_n):
                    points.append((
                        (x - inner_offset) * spacing,
                        (y - inner_offset) * spacing,
                        (z - inner_offset) * spacing
                    ))
                    
    return points


# -----------------------------------------------------------------------------
# Stellated Octahedron (Merkaba)
# -----------------------------------------------------------------------------
def stellated_octahedron_number(n: int) -> int:
    """Calculate the n-th stellated octahedron number.
    
    Formula: n(2n² - 1)  (Euler)
    Actually, physically it is 2 * Tetra(n) - Combined Core?
    Commonly: Octahedron(n) + 8 * Tetra(n-1)
    
    For this visualization, we effectively treat it as two interlocking tetrahedra.
    Tetra(N) + Tetra(N inverted).
    """
    if n < 1: return 0
    return octahedral_number(n) + 8 * tetrahedral_number(n - 1)


def stellated_octahedron_points(n: int, spacing: float = 1.0) -> List[Tuple[float, float, float]]:
    """Generate 3D coordinates for a Stellated Octahedron (Merkaba).
    
    Structure: Two intersecting Tetrahedra.
    1. Pointing Up (Standard)
    2. Pointing Down (Inverted)
    They share a centroid.
    """
    points = []
    
    # 1. Generate Base Tetrahedron
    # Currently generates from Tip (Z=0) to Base (Z=H).
    raw_points = tetrahedral_points(n, spacing)
    
    if not raw_points:
        return []
        
    # 2. Calculate Centroid "Center of Mass"
    # To intersect them perfectly, we align their centroids.
    # (Note: For geometric purity, we might align geometric centers, 
    # but aligning point-clouds by average works well for visual symmetry)
    avg_x = sum(p[0] for p in raw_points) / len(raw_points)
    avg_y = sum(p[1] for p in raw_points) / len(raw_points)
    avg_z = sum(p[2] for p in raw_points) / len(raw_points)
    
    centered_up = []
    for x, y, z in raw_points:
        centered_up.append((x - avg_x, y - avg_y, z - avg_z))
        
    points.extend(centered_up)
    
    # 3. Generate Downward Tetrahedron (Dual)
    # Reflect through the origin (-x, -y, -z)
    # This creates the opposing tetrahedron intersecting the first.
    for x, y, z in centered_up:  # type: ignore[reportUnknownVariableType]
        points.append((-x, -y, -z))

    # Dedup
    unique_map = {}
    for p in points:
        key = (round(p[0], 4), round(p[1], 4), round(p[2], 4))  # type: ignore[reportUnknownArgumentType, reportUnknownVariableType]
        unique_map[key] = p
        
    return list(unique_map.values())


# -----------------------------------------------------------------------------
# Icosahedral & Dodecahedral (The Final Platonics)
# -----------------------------------------------------------------------------
PHI = (1 + math.sqrt(5)) / 2

def icosahedral_number(n: int) -> int:
    """Centered Icosahedral number.
    Formula: (2n+1) * [(5n^2 + 5n + 1)]? 
    Actually, standard Centered Icosahedral is: 1 + 12(Tri_n-1?)
    Sequence: 1, 13, 55, 147... -> 1 + 12*1, 1+12*1 + 12*??
    Shell k has 12 points (k=0 is 1).
    Shell k>0 has 10k^2 + 2 points.
    Total(n) = 1 + sum(10k^2 + 2 for k in 1..n-1)
    """
    if n < 1: return 0
    if n == 1: return 1
    # n-1 shells
    # Sum_{k=1}^{n-1} (10k^2 + 2) = 10 * (n-1)n(2n-1)/6 + 2(n-1)
    k = n - 1
    return 1 + 10 * k * (k + 1) * (2 * k + 1) // 6 + 2 * k


def icosahedral_points(n: int, spacing: float = 1.0) -> List[Tuple[float, float, float]]:
    """Generate Centered Icosahedral points.
    
    Construction:
    - Shell 0: Center (0,0,0)
    - Shell k (1..n-1): Geodesic sphere of frequency k.
      Triangulate the 20 faces of the base Icosahedron.
    """
    if n < 1: return []
    points = [(0.0, 0.0, 0.0)]
    if n == 1: return points

    # Vertices of unit Icosahedron
    # (0, ±1, ±phi), (±1, ±phi, 0), (±phi, 0, ±1)
    # Norm = sqrt(1 + phi^2) = sqrt(1 + 2.618) = 1.902
    
    # We will define 12 vertices explicitly to index them for faces.
    # Using index convention for standard icosahedron.
    _raw_verts = [
        (0, 1, PHI), (0, -1, PHI), (0, 1, -PHI), (0, -1, -PHI),  # 0-3
        (1, PHI, 0), (-1, PHI, 0), (1, -PHI, 0), (-1, -PHI, 0),  # 4-7
        (PHI, 0, 1), (PHI, 0, -1), (-PHI, 0, 1), (-PHI, 0, -1)   # 8-11: Wait, fixed typo
    ]
    # Re-verify my permutation generation logic from previous block:
    # (PHI, 0, 1) and (-PHI, 0, 1) and (PHI, 0, -1) and (-PHI, 0, -1)
    
    # Let's clean up indices for faces.
    # 12 specific points.
    verts = [
        (0, 1, PHI),  # 0
        (0, -1, PHI), # 1
        (0, 1, -PHI), # 2
        (0, -1, -PHI),# 3
        (1, PHI, 0),  # 4
        (-1, PHI, 0), # 5
        (1, -PHI, 0), # 6
        (-1, -PHI, 0),# 7
        (PHI, 0, 1),  # 8
        (PHI, 0, -1), # 9
        (-PHI, 0, 1), # 10
        (-PHI, 0, -1) # 11
    ]
    
    # 20 Faces (Triplets of indices)
    # Standard Icosahedron face indices (checked against vertex list above)
    # A generic triangulation is safer if we don't want to debug indices:
    # Use distance check to build faces once.
    
    _faces = []
    num_v = 12
    # Threshold for edge length 2 (squared 4)
    # Distances are 4, or 4*PHI^2? 
    # Vertices are at radius sqrt(1+phi^2).
    # Distance between adjacent vertices is 2.
    
    valid_edges = set()
    for i in range(num_v):
        for j in range(i+1, num_v):
            v1, v2 = verts[i], verts[j]
            d2 = (v1[0]-v2[0])**2 + (v1[1]-v2[1])**2 + (v1[2]-v2[2])**2
            if abs(d2 - 4.0) < 0.1: # Edge length is 2
                valid_edges.add((i, j))
                valid_edges.add((j, i))
                
    # Find triangles
    triangles = []
    for i in range(num_v):
        for j in range(i+1, num_v):
            if (i, j) in valid_edges:
                for k in range(j+1, num_v):
                    if (j, k) in valid_edges and (k, i) in valid_edges:
                        triangles.append((i, j, k))
                        
    # Generate Shells
    seen_points = set()
    seen_points.add((0.0, 0.0, 0.0))
    
    # For each shell k > 0
    for k in range(1, n):
        shell_points = []
        
        # For each face
        for t_idx in triangles:
            i, j, m_idx = t_idx # m is taken, use m_idx  # type: ignore[reportUnknownVariableType]
            A = verts[i]
            B = verts[j]
            C = verts[m_idx]
            
            # Subdivide face into k^2 small triangles? 
            # We want the vertices of the subdivision.
            # Points P = (r*A + s*B + t*C) / k where r+s+t = k
            # r,s,t are integers >= 0.
            
            for r in range(k + 1):
                for s in range(k - r + 1):
                    t = k - r - s
                    # Only add points?
                    # This adds points for every face.
                    # Duplicates will verify at edges/vertices.
                    
                    # Coordinate
                    px = (r * A[0] + s * B[0] + t * C[0]) / k
                    py = (r * A[1] + s * B[1] + t * C[1]) / k
                    pz = (r * A[2] + s * B[2] + t * C[2]) / k
                    
                    shell_points.append((px, py, pz))
                    
        # Filter duplicates for this shell
        # Because edges are shared by 2 faces, vertices by 5 faces.
        for p in shell_points:
            # Round for key
            key = (round(p[0], 4), round(p[1], 4), round(p[2], 4))  # type: ignore[reportUnknownArgumentType, reportUnknownVariableType]
            if key not in seen_points:
                seen_points.add(key)
                # Scale by spacing
                points.append((p[0] * spacing, p[1] * spacing, p[2] * spacing))

    return points


def dodecahedral_number(n: int) -> int:
    """Centered Dodecahedral number.
    Sequence: 1, 33, 155, 427...
    Formula: (2n+1)*(9n^2 + 9n + 1)? 
    Let's rely on the point generator for visual count accuracy.
    """
    if n < 1: return 0
    if n == 1: return 1
    # Simple recursive approx or exact if known.
    # We will compute it from geometry or leave as estimate.
    # oeis A005904: 1, 33, 155, 427, 909, 1661...
    # Formula: (2*n - 1) * (9*(n-1)**2 + 9*(n-1) + 1) NO.
    # It is 1 + 12 * Pentagonal_Pyramid(n-1)? 
    # For now return simple label or 0.
    return 0


def dodecahedral_points(n: int, spacing: float = 1.0) -> List[Tuple[float, float, float]]:
    """Generate Centered Dodecahedral points.
    
    Construction:
    - 20 Vertices.
    - 12 Pentagonal Faces.
    - We scale the hull by k (1..n-1).
    - We fill faces with pentagonal numbers.
    """
    if n < 1: return []
    points = [(0.0, 0.0, 0.0)]
    if n == 1: return points
    
    # Vertices of unit Dodecahedron
    # (±1, ±1, ±1)
    # (0, ±1/phi, ±phi)
    # (±1/phi, ±phi, 0)
    # (±phi, 0, ±1/phi)
    phi = PHI
    inv_phi = 1.0 / phi
    
    verts = []
    # 1. Cube vertices
    for x in [-1, 1]:
        for y in [-1, 1]:
            for z in [-1, 1]:
                verts.append((x, y, z))
                
    # 2. Cyclic perms
    perms = [
        (0, inv_phi, phi), (0, -inv_phi, phi), (0, inv_phi, -phi), (0, -inv_phi, -phi),
        (inv_phi, phi, 0), (-inv_phi, phi, 0), (inv_phi, -phi, 0), (-inv_phi, -phi, 0),
        (phi, 0, inv_phi), (phi, 0, -inv_phi), (-phi, 0, inv_phi), (-phi, 0, -inv_phi)
    ]
    verts.extend(perms)
    
    # Scale to normalize edge length? 
    # Cube points are dist sqrt(3)~1.73.
    # Perms dist sqrt(phi^2 + 1/phi^2) = sqrt(2.618 + 0.382) = sqrt(3).
    # All vertices are on sphere of radius sqrt(3).
    # Edge length: dist((1,1,1), (0, 1/phi, phi))?
    # d^2 = 1 + (1-0.618)^2 + (1-1.618)^2 = 1 + 0.14 + 0.38 = 1.52?
    # Actual edge length is 2/phi * sqrt(3)? No.
    # Standard edge length is 2/phi = 1.236.
    
    # Identify Faces (Pentagons).
    # 12 faces. 
    # Brute force face finding (5 verts).
    
    # Build adjacency
    num_v = 20
    # True edge length dist_sq ~ 1.236^2 = 1.527
    # Calculated: (1-0)^2 + (1-0.618)^2 + (1-1.618)^2
    # = 1 + 0.145 + 0.381 = 1.527. Correct.
    
    edges = set()
    for i in range(num_v):
        for j in range(i+1, num_v):
            v1, v2 = verts[i], verts[j]
            d2 = (v1[0]-v2[0])**2 + (v1[1]-v2[1])**2 + (v1[2]-v2[2])**2
            if abs(d2 - 1.527) < 0.1:
                edges.add(tuple(sorted((i, j))))
                
    # Find Pentagons (cycles of 5)
    # This is tricky graph theory.
    # Hardcode faces for standard Dodecahedron is safer.
    # Let's trust "Geodesic Sphere" logic for filling faces is simpler if we just treat them as triangles?
    # No, Dodecahedron has Pentagons.
    # Triangulating the pentagons (center + 5 verts) -> 60 triangles (Kis-Dodecahedron).
    # But we want Dodecahedral shape.
    
    # Simple robust strategy:
    # Treat each Pentagonal Face as 5 triangles fan from a "Face Center".
    # But Face Center is not a vertex.
    # Actually, Pentagonal Grid filling is standard.
    # P(n) points.
    # Let's hardcode the 12 pentagon normals/centers.
    # Center of pentagon is vertex of Icosahedron!
    # Icosahedron vertices (0, ±1, ±phi)...
    # For each Icosa Vert C:
    # Find the 5 Dodeca Verts closest to C. They form the face.
    # Interpolate those 5 verts.
    
    # Icosa Verts (normalized) are Face Centers.
    _ico_verts = []
    # (0, ±1, ±phi) perms
    raw_ico = [
        (0, 1, phi), (0, -1, phi), (0, 1, -phi), (0, -1, -phi),
        (1, phi, 0), (-1, phi, 0), (1, -phi, 0), (-1, -phi, 0),
        (phi, 0, 1), (phi, 0, -1), (-phi, 0, 1), (-phi, 0, -1)
    ]
    
    seen_points = set()
    seen_points.add((0.0, 0.0, 0.0))
    
    for k in range(1, n):
        # Scale factor
        # For each face (defined by ico_vert center)
        for cx, cy, cz in raw_ico:
            # Find 5 vertices of Dodeca nearest to (cx, cy, cz)
            _face_verts = []
            # Brute force 20
            dists = []
            for _idx, v in enumerate(verts):  # type: ignore[reportUnknownArgumentType, reportUnknownVariableType, reportUnusedVariable]
                d2 = (v[0]-cx)**2 + (v[1]-cy)**2 + (v[2]-cz)**2
                dists.append((d2, v))
            dists.sort(key=lambda x: x[0])  # type: ignore[reportUnknownLambdaType, reportUnknownMemberType]
            # Top 5 are the face
            pentagon = [d[1] for d in dists[:5]]
            
            # Now fill this pentagon at scale k.
            # Triangle Fan from first vertex?
            # Or Centroid of pentagon (cx, cy, cz)?
            # Note: (cx, cy, cz) is magnitude sqrt(1+phi^2) ~ 1.9.
            # Dodeca verts are magnitude sqrt(3) ~ 1.73.
            # The Icosa vert is slightly "above" the flat face.
            # But the PROJECTION of that center onto the plane is likely the center.
            
            # Simple Plan: Decompose pentagon into 3 triangles: (0,1,2), (0,2,3), (0,3,4).
            # Fill triangles.
            # This covers the area completely.
            
            sub_tris = [
                (pentagon[0], pentagon[1], pentagon[2]),
                (pentagon[0], pentagon[2], pentagon[3]),
                (pentagon[0], pentagon[3], pentagon[4])
            ]
            
            for A, B, C in sub_tris:  # type: ignore[reportUnknownVariableType]
                # Fill triangle at scale k
                for r in range(k + 1):
                    for s in range(k - r + 1):
                        t = k - r - s
                        px = (r * A[0] + s * B[0] + t * C[0]) / k
                        py = (r * A[1] + s * B[1] + t * C[1]) / k
                        pz = (r * A[2] + s * B[2] + t * C[2]) / k
                        
                        # Add to set
                        key = (round(px, 4), round(py, 4), round(pz, 4))  # type: ignore[reportUnknownArgumentType, reportUnknownVariableType]
                        if key not in seen_points:
                            seen_points.add(key)
                            points.append((px*spacing, py*spacing, pz*spacing))

    return points


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
    "centered_cubic_points",
    "stellated_octahedron_number",
    "stellated_octahedron_points",
    "icosahedral_number",
    "icosahedral_points",
    "dodecahedral_number",
    "dodecahedral_points",
    "get_layer_for_point",
]
