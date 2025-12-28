"""Shared geometry services and solids."""
from .solid_payload import SolidPayload, SolidLabel
from .cube import CubeSolidService, CubeSolidCalculator
from .tetrahedron import TetrahedronSolidService, TetrahedronSolidCalculator
from .octahedron import OctahedronSolidService, OctahedronSolidCalculator
from .dodecahedron import DodecahedronSolidService, DodecahedronSolidCalculator
from .icosahedron import IcosahedronSolidService, IcosahedronSolidCalculator
from .archimedean import (
    CuboctahedronSolidService, CuboctahedronSolidCalculator,
    # ... and others, but let's just export the base or common ones for now
)

__all__ = [
    'SolidPayload', 'SolidLabel',
    'CubeSolidService', 'CubeSolidCalculator',
    'TetrahedronSolidService', 'TetrahedronSolidCalculator',
    'OctahedronSolidService', 'OctahedronSolidCalculator',
    'DodecahedronSolidService', 'DodecahedronSolidCalculator',
    'IcosahedronSolidService', 'IcosahedronSolidCalculator',
]
