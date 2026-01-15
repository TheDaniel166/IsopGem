"""Shared geometry services and solids."""
from .solid_payload import SolidPayload, SolidLabel
from .cube import CubeSolidService
from .tetrahedron import TetrahedronSolidService
from .octahedron import OctahedronSolidService
from .dodecahedron import DodecahedronSolidService
from .icosahedron import IcosahedronSolidService
from .archimedean import (
    CuboctahedronSolidService, CuboctahedronSolidCalculator,
    # ... and others, but let's just export the base or common ones for now
)

__all__ = [
    'SolidPayload', 'SolidLabel',
    'CubeSolidService',
    'TetrahedronSolidService',
    'OctahedronSolidService',
    'DodecahedronSolidService',
    'IcosahedronSolidService',
]
