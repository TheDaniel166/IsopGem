"""Backward compatibility shim for Platonic Constants."""
from shared.services.geometry.platonic_constants import (
    PlatonicSolid, TOPOLOGY, DIHEDRAL_ANGLES_DEG, SOLID_ANGLES_SR,  # type: ignore[reportUnusedImport]
    face_inradius, face_circumradius, sphere_surface_area, sphere_volume,  # type: ignore[reportUnusedImport]
    sphericity, isoperimetric_quotient, surface_to_volume_ratio  # type: ignore[reportUnusedImport]
)
