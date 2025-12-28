"""Backward compatibility shim for Solid Geometry."""
from shared.services.geometry.solid_geometry import (
    Face, Vertex, Edge, Vec3, compute_surface_area, compute_volume,
    edges_from_faces, plane_distance_from_origin, polygon_area, vec_length,
    vec_add, vec_sub, vec_scale, vec_dot, vec_cross, vec_normalize,
    face_normal, face_centroid, angle_around_axis
)
