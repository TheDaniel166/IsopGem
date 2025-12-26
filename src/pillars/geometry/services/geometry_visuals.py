"""Geometry visualization services.

Provides utilities for generating auxiliary visualization geometry,
such as dual solids, stellation diagrams, and inscribed figures.
"""
from typing import Dict, List, Tuple, Optional, Set

from ..shared.solid_payload import SolidPayload, SolidLabel

Vec3 = Tuple[float, float, float]


def _centroid(vertices: List[Vec3], indices: List[int]) -> Vec3:
    """Calculate centroid of a set of vertices."""
    if not indices:
        return (0.0, 0.0, 0.0)
    x = sum(vertices[i][0] for i in indices)
    y = sum(vertices[i][1] for i in indices)
    z = sum(vertices[i][2] for i in indices)
    count = len(indices)
    return (x / count, y / count, z / count)


def compute_dual_payload(primal: SolidPayload, scale_factor: float = 1.0) -> SolidPayload:
    """Generate the dual solid for a given primal polyhedron.
    
    The dual's vertices are the centroids of the primal's faces.
    The dual's edges connect centroids of adjacent primal faces.
    The dual's faces correspond to the primal's vertices.
    
    Args:
        primal: The source SolidPayload.
        scale_factor: Optional scaling for the dual (usually 1.0 is canonical).
            For reciprocal duals, size relationship is fixed defined by reciprocation radius,
            but here we just use the centroids directly.
    """
    if not primal.faces or not primal.vertices:
        return SolidPayload()

    # 1. Compute Dual Vertices (Centroids of Primal Faces)
    dual_vertices: List[Vec3] = []
    for face in primal.faces:
        center = _centroid(primal.vertices, list(face))
        if scale_factor != 1.0:
            center = (center[0] * scale_factor, center[1] * scale_factor, center[2] * scale_factor)
        dual_vertices.append(center)
    
    # 2. Map Edges to Faces (Adjacency)
    # Key: (min_v, max_v) -> List[face_index]
    edge_to_faces: Dict[Tuple[int, int], List[int]] = {}
    
    for face_idx, face in enumerate(primal.faces):
        # Iterate edges of the face
        for i in range(len(face)):
            u, v = face[i], face[(i + 1) % len(face)]
            edge_key = tuple(sorted((u, v)))
            if edge_key not in edge_to_faces:
                edge_to_faces[edge_key] = []
            edge_to_faces[edge_key].append(face_idx)
            
    # 3. Compute Dual Edges
    dual_edges: List[Tuple[int, int]] = []
    for faces in edge_to_faces.values():
        if len(faces) == 2:
            # Connect the two face centroids
            dual_edges.append((faces[0], faces[1]))
            
    # 4. Compute Dual Faces (One per Primal Vertex)
    # We need to find the cycle of faces around each vertex.
    # Build Vertex -> List[FaceIndex] map first
    vertex_to_faces: Dict[int, Set[int]] = {}
    for face_idx, face in enumerate(primal.faces):
        for v_idx in face:
            if v_idx not in vertex_to_faces:
                vertex_to_faces[v_idx] = set()
            vertex_to_faces[v_idx].add(face_idx)
            
    dual_faces: List[Tuple[int, ...]] = []
    
    # For each primal vertex, reconstruct the loop of faces
    # This requires traversing the edge adjacency.
    # Or, for each face in set, find neighbor in set that shares an edge connected to v.
    
    sorted_primal_vertices = sorted(vertex_to_faces.keys())
    
    for v_idx in sorted_primal_vertices:
        associated_faces = list(vertex_to_faces[v_idx])
        if len(associated_faces) < 3:
            continue
            
        # Sort these faces to form a cycle.
        # Start with first face. Find neighbor that shares an edge incidents to v.
        # Face f1 shares edge (v, u) with f2.
        
        # Helper: Two faces adjacent? and share vertex v?
        # They share an edge containing v.
        
        # Let's organize edges around v.
        # Find all edges connected to v.
        # Each edge connects to 2 faces.
        # Graph nodes = Faces. Graph edges = adjacency (sharing primal edge satisfying rule).
        
        # Build mini-graph for this vertex
        local_adjacency: Dict[int, List[int]] = {f: [] for f in associated_faces}
        
        # Identify edges incident to v
        # edges incident to v are (v, x).
        # find faces sharing this edge.
        for u in range(len(primal.vertices)): 
            # This is O(V^2), inefficient. Better to use edge_to_faces.
            # edge_key = sorted(v, u).
            pass
            
        # Better: Iterate all edges incident to v.
        # We don't have vertex->edge map handy. 
        # But we have edge_to_faces map.
        # Filter edge_to_faces for keys containing v_idx.
        
        for (a, b), faces_sharing in edge_to_faces.items():
            if v_idx in (a, b):
                if len(faces_sharing) == 2:
                    f1, f2 = faces_sharing
                    if f1 in local_adjacency and f2 in local_adjacency:
                        local_adjacency[f1].append(f2)
                        local_adjacency[f2].append(f1)
        
        # Now traverse the cycle
        if not local_adjacency: 
            continue
            
        start_face = associated_faces[0]
        cycle = [start_face]
        current = start_face
        visited = {start_face}
        
        # Walk
        for _ in range(len(associated_faces) - 1):
            neighbors = local_adjacency[current]
            # Pick unvisited
            next_face = None
            for n in neighbors:
                if n not in visited:
                    next_face = n
                    break
            
            if next_face is not None:
                visited.add(next_face)
                cycle.append(next_face)
                current = next_face
            else:
                # Cycle broken or closed prematurely?
                break
                
        dual_faces.append(tuple(cycle))

    return SolidPayload(
        vertices=dual_vertices,
        edges=dual_edges,
        faces=dual_faces,
        face_colors=None, # Duals usually default color
        suggested_scale=primal.suggested_scale
    )
