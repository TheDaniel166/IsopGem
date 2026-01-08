"""Dodecahedron solid math utilities and calculator.

Enhanced with comprehensive bidirectional properties including:
- Topology (faces, edges, vertices)
- Dihedrals and solid angles
- Face geometry (inradius, circumradius)
- Sphere metrics (inscribed/circumscribed surface area and volume)
- Quality metrics (sphericity, isoperimetric quotient)
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional

from .solid_payload import SolidLabel, SolidPayload
from .solid_geometry import (
    Face,
    Vec3,
    angle_around_axis,
    compute_surface_area,
    compute_volume,
    edges_from_faces,
    face_centroid,
    face_normal,
    plane_distance_from_origin,
    polygon_area,
    vec_length,
    vec_normalize,
)
from .solid_property import SolidProperty
from .platonic_constants import (
    PlatonicSolid,
    TOPOLOGY,
    DIHEDRAL_ANGLES_DEG,
    SOLID_ANGLES_SR,
    MOMENT_INERTIA_SOLID_K,
    MOMENT_INERTIA_SHELL_K,
    ANGULAR_DEFECT_VERTEX_DEG,
    TOTAL_ANGULAR_DEFECT_DEG,
    PACKING_DENSITY,
    SYMMETRY_GROUP_ORDER,
    ROTATIONAL_SYMMETRY_ORDER,
    SYMMETRY_GROUP_NAME,
    DUAL_SOLID_NAME,
    GOLDEN_RATIO_FACTOR,
    face_inradius,
    face_circumradius,
    sphere_surface_area,
    sphere_volume,
    sphericity,
    isoperimetric_quotient,
    surface_to_volume_ratio,
)


_phi = (1.0 + math.sqrt(5.0)) / 2.0

_ICOSAHEDRON_VERTICES: List[Vec3] = [
    (-1.0, _phi, 0.0),
    (1.0, _phi, 0.0),
    (-1.0, -_phi, 0.0),
    (1.0, -_phi, 0.0),
    (0.0, -1.0, _phi),
    (0.0, 1.0, _phi),
    (0.0, -1.0, -_phi),
    (0.0, 1.0, -_phi),
    (_phi, 0.0, -1.0),
    (_phi, 0.0, 1.0),
    (-_phi, 0.0, -1.0),
    (-_phi, 0.0, 1.0),
]

_ICOSAHEDRON_FACES: List[Face] = [
    (0, 11, 5),
    (0, 5, 1),
    (0, 1, 7),
    (0, 7, 10),
    (0, 10, 11),
    (1, 5, 9),
    (5, 11, 4),
    (11, 10, 2),
    (10, 7, 6),
    (7, 1, 8),
    (3, 9, 4),
    (3, 4, 2),
    (3, 2, 6),
    (3, 6, 8),
    (3, 8, 9),
    (4, 9, 5),
    (2, 4, 11),
    (6, 2, 10),
    (8, 6, 7),
    (9, 8, 1),
]


def _build_dual_vertices() -> List[Vec3]:
    vertices: List[Vec3] = []
    for face in _ICOSAHEDRON_FACES:
        normal = face_normal(_ICOSAHEDRON_VERTICES, face)
        centroid = face_centroid(_ICOSAHEDRON_VERTICES, face)
        if math.isclose(vec_length(normal), 0.0):
            vertices.append((0.0, 0.0, 0.0))
            continue
        if sum(n * c for n, c in zip(normal, centroid)) < 0:
            normal = (-normal[0], -normal[1], -normal[2])
        vertices.append(vec_normalize(normal))
    return vertices


def _build_dual_faces(dual_vertices: List[Vec3]) -> List[Face]:
    vertex_to_faces: Dict[int, List[int]] = {i: [] for i in range(len(_ICOSAHEDRON_VERTICES))}
    for idx, face in enumerate(_ICOSAHEDRON_FACES):
        for vertex_index in face:
            vertex_to_faces[vertex_index].append(idx)

    faces: List[Face] = []
    for vertex_idx, face_indices in vertex_to_faces.items():
        axis = _ICOSAHEDRON_VERTICES[vertex_idx]
        ordered = []
        for face_index in face_indices:
            point = dual_vertices[face_index]
            angle = angle_around_axis(point, axis, (0.0, 0.0, 1.0))
            ordered.append((angle, face_index))
        ordered.sort()
        faces.append(tuple(face_index for _, face_index in ordered))
    return faces


_DUAL_VERTICES = _build_dual_vertices()
_DUAL_FACES = _build_dual_faces(_DUAL_VERTICES)
_EDGES = edges_from_faces(_DUAL_FACES)
_BASE_EDGE_LENGTH = math.dist(_DUAL_VERTICES[_EDGES[0][0]], _DUAL_VERTICES[_EDGES[0][1]])
_BASE_FACE_AREA = polygon_area(_DUAL_VERTICES, _DUAL_FACES[0])
_BASE_SURFACE_AREA = compute_surface_area(_DUAL_VERTICES, _DUAL_FACES)
_BASE_VOLUME = compute_volume(_DUAL_VERTICES, _DUAL_FACES)
_BASE_INRADIUS = plane_distance_from_origin(_DUAL_VERTICES, _DUAL_FACES[0])
_mid_edge = (
    (_DUAL_VERTICES[_EDGES[0][0]][0] + _DUAL_VERTICES[_EDGES[0][1]][0]) / 2.0,
    (_DUAL_VERTICES[_EDGES[0][0]][1] + _DUAL_VERTICES[_EDGES[0][1]][1]) / 2.0,
    (_DUAL_VERTICES[_EDGES[0][0]][2] + _DUAL_VERTICES[_EDGES[0][1]][2]) / 2.0,
)
_BASE_MIDRADIUS = vec_length(_mid_edge)
_BASE_CIRCUMRADIUS = vec_length(_DUAL_VERTICES[0])
_BASE_INCIRC_CIRC = 2.0 * math.pi * _BASE_INRADIUS
_BASE_MID_CIRC = 2.0 * math.pi * _BASE_MIDRADIUS
_BASE_CIRCUM_CIRC = 2.0 * math.pi * _BASE_CIRCUMRADIUS

# Topology constants
_TOPOLOGY = TOPOLOGY[PlatonicSolid.DODECAHEDRON]
_DIHEDRAL_DEG = DIHEDRAL_ANGLES_DEG[PlatonicSolid.DODECAHEDRON]
_SOLID_ANGLE_SR = SOLID_ANGLES_SR[PlatonicSolid.DODECAHEDRON]

# Face geometry at base edge
_BASE_FACE_INRADIUS = face_inradius(_BASE_EDGE_LENGTH, _TOPOLOGY.p)
_BASE_FACE_CIRCUMRADIUS = face_circumradius(_BASE_EDGE_LENGTH, _TOPOLOGY.p)

# Sphere metrics at base edge
_BASE_INSPHERE_SA = sphere_surface_area(_BASE_INRADIUS)
_BASE_MIDSPHERE_SA = sphere_surface_area(_BASE_MIDRADIUS)
_BASE_CIRCUMSPHERE_SA = sphere_surface_area(_BASE_CIRCUMRADIUS)
_BASE_INSPHERE_VOL = sphere_volume(_BASE_INRADIUS)
_BASE_MIDSPHERE_VOL = sphere_volume(_BASE_MIDRADIUS)
_BASE_CIRCUMSPHERE_VOL = sphere_volume(_BASE_CIRCUMRADIUS)

# Advanced physics: Moment of Inertia base values
_MOI_K_SOLID = MOMENT_INERTIA_SOLID_K[PlatonicSolid.DODECAHEDRON]
_MOI_K_SHELL = MOMENT_INERTIA_SHELL_K[PlatonicSolid.DODECAHEDRON]
_BASE_MOI_SOLID = _MOI_K_SOLID * _BASE_VOLUME * _BASE_EDGE_LENGTH * _BASE_EDGE_LENGTH
_BASE_MOI_SHELL = _MOI_K_SHELL * _BASE_SURFACE_AREA * _BASE_EDGE_LENGTH * _BASE_EDGE_LENGTH

# Advanced constants (read-only)
_ANGULAR_DEFECT_DEG = ANGULAR_DEFECT_VERTEX_DEG[PlatonicSolid.DODECAHEDRON]
_PACKING_DENSITY = PACKING_DENSITY[PlatonicSolid.DODECAHEDRON]
_SYMMETRY_ORDER = SYMMETRY_GROUP_ORDER[PlatonicSolid.DODECAHEDRON]
_ROTATION_ORDER = ROTATIONAL_SYMMETRY_ORDER[PlatonicSolid.DODECAHEDRON]
_SYMMETRY_NAME = SYMMETRY_GROUP_NAME[PlatonicSolid.DODECAHEDRON]
_DUAL_NAME = DUAL_SOLID_NAME[PlatonicSolid.DODECAHEDRON]
_GOLDEN_FACTOR = GOLDEN_RATIO_FACTOR[PlatonicSolid.DODECAHEDRON]


@dataclass(frozen=True)
class DodecahedronMetrics:
    """Comprehensive metrics for a regular dodecahedron."""
    # Core dimensions
    edge_length: float
    face_area: float
    surface_area: float
    volume: float
    
    # Sphere radii
    inradius: float
    midradius: float
    circumradius: float
    
    # Sphere circumferences
    incircle_circumference: float
    midsphere_circumference: float
    circumcircle_circumference: float
    
    # Topology (constants)
    faces: int = _TOPOLOGY.faces
    edges: int = _TOPOLOGY.edges
    vertices: int = _TOPOLOGY.vertices
    face_sides: int = _TOPOLOGY.p
    vertex_valence: int = _TOPOLOGY.q
    
    # Angles (constants)
    dihedral_angle_deg: float = _DIHEDRAL_DEG
    solid_angle_sr: float = _SOLID_ANGLE_SR
    
    # Face geometry
    face_inradius: float = 0.0
    face_circumradius: float = 0.0
    
    # Inscribed sphere
    insphere_surface_area: float = 0.0
    insphere_volume: float = 0.0
    
    # Midsphere
    midsphere_surface_area: float = 0.0
    midsphere_volume: float = 0.0
    
    # Circumscribed sphere
    circumsphere_surface_area: float = 0.0
    circumsphere_volume: float = 0.0
    
    # Quality metrics
    sphericity: float = 0.0
    isoperimetric_quotient: float = 0.0
    surface_to_volume_ratio: float = 0.0
    
    # =========================================================================
    # ADVANCED PROPERTIES
    # =========================================================================
    
    # Physics: Moment of Inertia (assumes unit density)
    moment_inertia_solid: float = 0.0
    moment_inertia_shell: float = 0.0
    
    # Topology: Angular Defect
    angular_defect_vertex_deg: float = _ANGULAR_DEFECT_DEG
    total_angular_defect_deg: float = TOTAL_ANGULAR_DEFECT_DEG
    euler_characteristic: int = 2
    
    # Packing
    packing_density: float = _PACKING_DENSITY
    
    # Symmetry
    symmetry_group_order: int = _SYMMETRY_ORDER
    rotational_symmetry_order: int = _ROTATION_ORDER
    symmetry_group_name: str = _SYMMETRY_NAME
    
    # Dual
    dual_solid_name: str = _DUAL_NAME
    
    # Golden ratio
    golden_ratio_factor: float = _GOLDEN_FACTOR


@dataclass(frozen=True)
class DodecahedronSolidResult:
    """
    Dodecahedron Solid Result class definition.
    
    """
    payload: SolidPayload
    metrics: DodecahedronMetrics


def _scaled_value(base_value: float, edge_length: float, power: float) -> float:
    scale = edge_length / _BASE_EDGE_LENGTH
    return base_value * (scale ** power)


def _scale_vertices(edge_length: float) -> List[Vec3]:
    scale = edge_length / _BASE_EDGE_LENGTH
    return [(vx * scale, vy * scale, vz * scale) for vx, vy, vz in _DUAL_VERTICES]


def _compute_metrics(edge_length: float) -> DodecahedronMetrics:
    # Core dimensions
    face_area_val = _scaled_value(_BASE_FACE_AREA, edge_length, 2.0)
    surface_area_val = _scaled_value(_BASE_SURFACE_AREA, edge_length, 2.0)
    volume_val = _scaled_value(_BASE_VOLUME, edge_length, 3.0)
    
    # Sphere radii
    inradius_val = _scaled_value(_BASE_INRADIUS, edge_length, 1.0)
    midradius_val = _scaled_value(_BASE_MIDRADIUS, edge_length, 1.0)
    circumradius_val = _scaled_value(_BASE_CIRCUMRADIUS, edge_length, 1.0)
    
    # Face geometry
    face_inradius_val = face_inradius(edge_length, _TOPOLOGY.p)
    face_circumradius_val = face_circumradius(edge_length, _TOPOLOGY.p)
    
    # Sphere metrics
    insphere_sa = sphere_surface_area(inradius_val)
    midsphere_sa = sphere_surface_area(midradius_val)
    circumsphere_sa = sphere_surface_area(circumradius_val)
    insphere_vol = sphere_volume(inradius_val)
    midsphere_vol = sphere_volume(midradius_val)
    circumsphere_vol = sphere_volume(circumradius_val)
    
    # Quality metrics
    sph = sphericity(volume_val, surface_area_val)
    iq = isoperimetric_quotient(volume_val, surface_area_val)
    sv_ratio = surface_to_volume_ratio(surface_area_val, volume_val)
    
    # Advanced physics: Moment of Inertia (unit density)
    moi_solid = _scaled_value(_BASE_MOI_SOLID, edge_length, 5.0)
    moi_shell = _scaled_value(_BASE_MOI_SHELL, edge_length, 4.0)
    
    return DodecahedronMetrics(
        edge_length=edge_length,
        face_area=face_area_val,
        surface_area=surface_area_val,
        volume=volume_val,
        inradius=inradius_val,
        midradius=midradius_val,
        circumradius=circumradius_val,
        incircle_circumference=_scaled_value(_BASE_INCIRC_CIRC, edge_length, 1.0),
        midsphere_circumference=_scaled_value(_BASE_MID_CIRC, edge_length, 1.0),
        circumcircle_circumference=_scaled_value(_BASE_CIRCUM_CIRC, edge_length, 1.0),
        face_inradius=face_inradius_val,
        face_circumradius=face_circumradius_val,
        insphere_surface_area=insphere_sa,
        insphere_volume=insphere_vol,
        midsphere_surface_area=midsphere_sa,
        midsphere_volume=midsphere_vol,
        circumsphere_surface_area=circumsphere_sa,
        circumsphere_volume=circumsphere_vol,
        sphericity=sph,
        isoperimetric_quotient=iq,
        surface_to_volume_ratio=sv_ratio,
        # Advanced
        moment_inertia_solid=moi_solid,
        moment_inertia_shell=moi_shell,
    )


class DodecahedronSolidService:
    """Generates payloads for regular dodecahedra."""

    @staticmethod
    def build(edge_length: float = 1.0) -> DodecahedronSolidResult:
        """
        Build logic.
        
        Args:
            edge_length: Description of edge_length.
        
        Returns:
            Result of build operation.
        """
        if edge_length <= 0:
            raise ValueError("Edge length must be positive")
        metrics = _compute_metrics(edge_length)
        from .geometry_visuals import compute_dual_payload
        
        payload = SolidPayload(
            vertices=_scale_vertices(edge_length),
            edges=list(_EDGES),
            faces=[tuple(face) for face in _DUAL_FACES],
            labels=[
                SolidLabel(text=f"a = {edge_length:.3f}", position=(0.0, 0.0, 0.0)),
                SolidLabel(text=f"V = {metrics.volume:.3f}", position=(0.0, -edge_length * 0.3, 0.0)),
            ],
            metadata={
                # Core
                'edge_length': metrics.edge_length,
                'face_area': metrics.face_area,
                'surface_area': metrics.surface_area,
                'volume': metrics.volume,
                # Sphere radii
                'inradius': metrics.inradius,
                'midradius': metrics.midradius,
                'circumradius': metrics.circumradius,
                'incircle_circumference': metrics.incircle_circumference,
                'midsphere_circumference': metrics.midsphere_circumference,
                'circumcircle_circumference': metrics.circumcircle_circumference,
                # Topology
                'faces': metrics.faces,
                'edges': metrics.edges,
                'vertices': metrics.vertices,
                'face_sides': metrics.face_sides,
                'vertex_valence': metrics.vertex_valence,
                # Angles
                'dihedral_angle_deg': metrics.dihedral_angle_deg,
                'solid_angle_sr': metrics.solid_angle_sr,
                # Face geometry
                'face_inradius': metrics.face_inradius,
                'face_circumradius': metrics.face_circumradius,
                # Sphere metrics
                'insphere_surface_area': metrics.insphere_surface_area,
                'insphere_volume': metrics.insphere_volume,
                'midsphere_surface_area': metrics.midsphere_surface_area,
                'midsphere_volume': metrics.midsphere_volume,
                'circumsphere_surface_area': metrics.circumsphere_surface_area,
                'circumsphere_volume': metrics.circumsphere_volume,
                # Quality
                'sphericity': metrics.sphericity,
                'isoperimetric_quotient': metrics.isoperimetric_quotient,
                'surface_to_volume_ratio': metrics.surface_to_volume_ratio,
            },
            suggested_scale=edge_length,
        )
        payload.dual = compute_dual_payload(payload)
        return DodecahedronSolidResult(payload=payload, metrics=metrics)

    @staticmethod
    def payload(edge_length: float = 1.0) -> SolidPayload:
        """
        Payload logic.
        
        Args:
            edge_length: Description of edge_length.
        
        Returns:
            Result of payload operation.
        """
        return DodecahedronSolidService.build(edge_length).payload


class DodecahedronSolidCalculator:
    """Bidirectional calculator for regular dodecahedra with comprehensive properties."""

    _FORMULAS = {
        'face_area': r"A_f = \frac{1}{4}\sqrt{25+10\sqrt{5}}\,a^2",
        'surface_area': r"A = 3\sqrt{25+10\sqrt{5}}\,a^2",
        'volume': r"V = \frac{15+7\sqrt{5}}{4}a^3",
        'inradius': r"r = \frac{a}{20}\sqrt{250+110\sqrt{5}}",
        'circumradius': r"R = \frac{a}{4}\sqrt{3}\,(1+\sqrt{5})",
    }

    _EDITABLE_PROPERTIES = (
        ('edge_length', 'Edge Length', 'units', 4, 1.0, _BASE_EDGE_LENGTH),
        ('face_area', 'Face Area', 'units²', 4, 2.0, _BASE_FACE_AREA),
        ('surface_area', 'Surface Area', 'units²', 4, 2.0, _BASE_SURFACE_AREA),
        ('volume', 'Volume', 'units³', 4, 3.0, _BASE_VOLUME),
        ('inradius', 'Inradius', 'units', 4, 1.0, _BASE_INRADIUS),
        ('midradius', 'Midsphere Radius', 'units', 4, 1.0, _BASE_MIDRADIUS),
        ('circumradius', 'Circumradius', 'units', 4, 1.0, _BASE_CIRCUMRADIUS),
        ('incircle_circumference', 'Insphere Circumference', 'units', 4, 1.0, _BASE_INCIRC_CIRC),
        ('midsphere_circumference', 'Midsphere Circumference', 'units', 4, 1.0, _BASE_MID_CIRC),
        ('circumcircle_circumference', 'Circumsphere Circumference', 'units', 4, 1.0, _BASE_CIRCUM_CIRC),
        ('face_inradius', 'Face Inradius', 'units', 4, 1.0, _BASE_FACE_INRADIUS),
        ('face_circumradius', 'Face Circumradius', 'units', 4, 1.0, _BASE_FACE_CIRCUMRADIUS),
        ('insphere_surface_area', 'Insphere Surface Area', 'units²', 4, 2.0, _BASE_INSPHERE_SA),
        ('insphere_volume', 'Insphere Volume', 'units³', 4, 3.0, _BASE_INSPHERE_VOL),
        ('midsphere_surface_area', 'Midsphere Surface Area', 'units²', 4, 2.0, _BASE_MIDSPHERE_SA),
        ('midsphere_volume', 'Midsphere Volume', 'units³', 4, 3.0, _BASE_MIDSPHERE_VOL),
        ('circumsphere_surface_area', 'Circumsphere Surface Area', 'units²', 4, 2.0, _BASE_CIRCUMSPHERE_SA),
        ('circumsphere_volume', 'Circumsphere Volume', 'units³', 4, 3.0, _BASE_CIRCUMSPHERE_VOL),
        # Advanced (bidirectional)
        ('moment_inertia_solid', 'Moment of Inertia (Solid)', 'units⁵', 6, 5.0, _BASE_MOI_SOLID),
        ('moment_inertia_shell', 'Moment of Inertia (Shell)', 'units⁴', 6, 4.0, _BASE_MOI_SHELL),
    )

    _READONLY_PROPERTIES = (
        ('faces', 'Faces', '', 0),
        ('edges', 'Edges', '', 0),
        ('vertices', 'Vertices', '', 0),
        ('face_sides', 'Face Sides', '', 0),
        ('vertex_valence', 'Vertex Valence', '', 0),
        ('dihedral_angle_deg', 'Dihedral Angle', '°', 2),
        ('solid_angle_sr', 'Solid Angle', 'sr', 4),
        ('sphericity', 'Sphericity', '', 4),
        ('isoperimetric_quotient', 'Isoperimetric Quotient', '', 4),
        ('surface_to_volume_ratio', 'Surface/Volume Ratio', '1/units', 4),
        # Advanced (read-only)
        ('angular_defect_vertex_deg', 'Angular Defect (Vertex)', '°', 2),
        ('total_angular_defect_deg', 'Total Angular Defect', '°', 0),
        ('euler_characteristic', 'Euler Characteristic', '', 0),
        ('packing_density', 'Packing Density', '', 4),
        ('symmetry_group_order', 'Symmetry Group Order', '', 0),
        ('rotational_symmetry_order', 'Rotational Symmetry Order', '', 0),
        ('symmetry_group_name', 'Symmetry Group', '', 0),
        ('dual_solid_name', 'Dual Solid', '', 0),
        ('golden_ratio_factor', 'Golden Ratio Factor', '', 4),
    )

    def __init__(self, edge_length: float = 1.0):
        """
          init   logic.
        
        Args:
            edge_length: Description of edge_length.
        
        """
        self._properties: Dict[str, SolidProperty] = {}
        self._edge_solvers: Dict[str, callable] = {}
        
        for key, label, unit, precision, power, base_value in self._EDITABLE_PROPERTIES:
            self._properties[key] = SolidProperty(
                name=label,
                key=key,
                unit=unit,
                precision=precision,
                editable=True,
                formula=self._FORMULAS.get(key),
            )
            self._edge_solvers[key] = self._build_solver(base_value, power)
        
        for key, label, unit, precision in self._READONLY_PROPERTIES:
            self._properties[key] = SolidProperty(
                name=label,
                key=key,
                unit=unit,
                precision=precision,
                editable=False,
                formula=self._FORMULAS.get(key),
            )
        
        self._result: Optional[DodecahedronSolidResult] = None
        if edge_length > 0:
            self._apply_edge(edge_length)

    @staticmethod
    def _build_solver(base_value: float, power: float):
        def solver(value: Optional[float]) -> Optional[float]:
            """
            Solver logic.
            
            Args:
                value: Description of value.
            
            Returns:
                Result of solver operation.
            """
            if value is None or value <= 0 or base_value <= 0:
                return None
            scale = (value / base_value) ** (1.0 / power)
            return scale * _BASE_EDGE_LENGTH
        return solver

    def properties(self) -> List[SolidProperty]:
        """
        Properties logic.
        
        Returns:
            Result of properties operation.
        """
        order = [key for key, *_ in self._EDITABLE_PROPERTIES] + \
                [key for key, *_ in self._READONLY_PROPERTIES]
        return [self._properties[key] for key in order if key in self._properties]

    def set_property(self, key: str, value: Optional[float]) -> bool:
        """
        Configure property logic.
        
        Args:
            key: Description of key.
            value: Description of value.
        
        Returns:
            Result of set_property operation.
        """
        if key not in self._edge_solvers or value is None or value <= 0:
            return False
        solver = self._edge_solvers[key]
        edge_length = solver(value)
        if edge_length is None or not math.isfinite(edge_length) or edge_length <= 0:
            return False
        self._apply_edge(edge_length)
        return True

    def clear(self):
        """
        Clear logic.
        
        """
        for prop in self._properties.values():
            prop.value = None
        self._result = None

    def payload(self) -> Optional[SolidPayload]:
        """
        Payload logic.
        
        Returns:
            Result of payload operation.
        """
        return self._result.payload if self._result else None

    def metadata(self) -> Dict[str, float]:
        """
        Metadata logic.
        
        Returns:
            Result of metadata operation.
        """
        if not self._result:
            return {}
        return dict(self._result.payload.metadata)

    def metrics(self) -> Optional[DodecahedronMetrics]:
        """
        Metrics logic.
        
        Returns:
            Result of metrics operation.
        """
        return self._result.metrics if self._result else None

    def _apply_edge(self, edge_length: float):
        result = DodecahedronSolidService.build(edge_length)
        self._result = result
        m = result.metrics
        
        values = {
            'edge_length': m.edge_length,
            'face_area': m.face_area,
            'surface_area': m.surface_area,
            'volume': m.volume,
            'inradius': m.inradius,
            'midradius': m.midradius,
            'circumradius': m.circumradius,
            'incircle_circumference': m.incircle_circumference,
            'midsphere_circumference': m.midsphere_circumference,
            'circumcircle_circumference': m.circumcircle_circumference,
            'face_inradius': m.face_inradius,
            'face_circumradius': m.face_circumradius,
            'insphere_surface_area': m.insphere_surface_area,
            'insphere_volume': m.insphere_volume,
            'midsphere_surface_area': m.midsphere_surface_area,
            'midsphere_volume': m.midsphere_volume,
            'circumsphere_surface_area': m.circumsphere_surface_area,
            'circumsphere_volume': m.circumsphere_volume,
            'faces': m.faces,
            'edges': m.edges,
            'vertices': m.vertices,
            'face_sides': m.face_sides,
            'vertex_valence': m.vertex_valence,
            'dihedral_angle_deg': m.dihedral_angle_deg,
            'solid_angle_sr': m.solid_angle_sr,
            'sphericity': m.sphericity,
            'isoperimetric_quotient': m.isoperimetric_quotient,
            'surface_to_volume_ratio': m.surface_to_volume_ratio,
        }
        for key, prop in self._properties.items():
            prop.value = values.get(key)


__all__ = [
    'DodecahedronMetrics',
    'DodecahedronSolidResult',
    'DodecahedronSolidService',
    'DodecahedronSolidCalculator',
]