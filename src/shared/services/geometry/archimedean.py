"""Archimedean solid services and calculators."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple, Type, cast

from .solid_payload import SolidLabel, SolidPayload, Vec3, Edge, Face
from .solid_property import SolidProperty
from .solid_geometry import (
    vec_sub,
    vec_cross,
    vec_length,
    vec_dot,
    vec_normalize,
    compute_surface_area,
    compute_volume,
    edges_from_faces,
)
from .archimedean_data import ARCHIMEDEAN_DATA


@dataclass(frozen=True)
class ArchimedeanSolidMetrics:
    """
    Archimedean Solid Metrics class definition.

    """
    # Core dimensions
    edge_length: float
    surface_area: float
    volume: float
    face_count: int
    edge_count: int
    vertex_count: int
    face_sides: Dict[int, int]
    face_metrics: Dict[int, Dict[str, float]] # {sides: {'area_single': x, 'area_total': y}}

    # Sphere radii
    inradius: float
    midradius: float
    circumradius: float

    # Sphere properties
    insphere_surface_area: float
    insphere_volume: float
    midsphere_surface_area: float
    midsphere_volume: float
    circumsphere_surface_area: float
    circumsphere_volume: float

    # Sphere circumferences
    insphere_circumference: float
    midsphere_circumference: float
    circumsphere_circumference: float

    # Geometric ratios
    sphericity: float
    isoperimetric_quotient: float
    surface_to_volume_ratio: float

    # Topology
    euler_characteristic: int

    # Symmetry (stored as strings/ints for display)
    symmetry_group: str
    symmetry_order: int
    rotational_order: int

    # Dual solid
    dual_name: str


@dataclass(frozen=True)
class ArchimedeanSolidResult:
    """
    Archimedean Solid Result class definition.
    
    """
    payload: SolidPayload
    metrics: ArchimedeanSolidMetrics


@dataclass(frozen=True)
class ArchimedeanSolidDefinition:
    """
    Archimedean Solid Definition class definition.
    
    """
    key: str
    name: str
    canonical_vertices: List[Vec3]
    faces: List[Face]
    edges: List[Edge]
    base_edge_length: float
    base_surface_area: float
    base_volume: float
    face_sides: Dict[int, int]


_DEF_CACHE: Dict[str, ArchimedeanSolidDefinition] = {}

def _order_face_vertices(indices: List[int], vertices: List[Vec3]) -> Face:
    if len(indices) <= 2:
        return tuple(indices)
    centroid: Vec3 = cast(
        Vec3,
        tuple(sum(vertices[idx][k] for idx in indices) / len(indices) for k in range(3)),
    )
    normal = (0.0, 0.0, 1.0)
    for i in range(len(indices)):
        v1 = vec_sub(vertices[indices[i]], centroid)
        v2 = vec_sub(vertices[indices[(i + 1) % len(indices)]], centroid)
        cross = vec_cross(v1, v2)
        if vec_length(cross) > 1e-6:
            normal = vec_normalize(cross)
            break
    basis = None
    for idx in indices:
        vec = vec_sub(vertices[idx], centroid)
        if vec_length(vec) > 1e-6:
            basis = vec_normalize(vec)
            break
    if basis is None:
        return tuple(indices)
    perp = vec_cross(normal, basis)
    if vec_length(perp) < 1e-6:
        perp = (0.0, 1.0, 0.0)
    else:
        perp = vec_normalize(perp)
    ordered = []
    for idx in indices:
        rel = vec_sub(vertices[idx], centroid)
        x = vec_dot(rel, basis)
        y = vec_dot(rel, perp)
        angle = math.atan2(y, x)
        ordered.append((angle, idx))
    ordered.sort()
    return tuple(idx for _, idx in ordered)


def _definition_from_data(key: str) -> ArchimedeanSolidDefinition:
    data = ARCHIMEDEAN_DATA.get(key)
    if not data:
        raise KeyError(key)
    vertices: List[Vec3] = [cast(Vec3, tuple(v)) for v in data['vertices']]
    faces: List[Face] = [cast(Face, tuple(face)) for face in data['faces']]
    return _finalize_definition(key, data['name'], vertices, faces)


def _finalize_definition(key: str, name: str, vertices: List[Vec3], faces: List[Face]) -> ArchimedeanSolidDefinition:
    ordered_faces: List[Face] = [cast(Face, tuple(face)) for face in faces]
    edges = edges_from_faces(ordered_faces)
    if not edges:
        raise ValueError(f"No edges computed for Archimedean solid '{key}'")
    edge_vec = vec_sub(vertices[edges[0][0]], vertices[edges[0][1]])
    base_edge_length = vec_length(edge_vec)
    base_surface_area = compute_surface_area(vertices, ordered_faces)
    base_volume = compute_volume(vertices, ordered_faces)
    face_sides: Dict[int, int] = {}
    for face in ordered_faces:
        face_sides[len(face)] = face_sides.get(len(face), 0) + 1
    definition = ArchimedeanSolidDefinition(
        key=key,
        name=name,
        canonical_vertices=vertices,
        faces=ordered_faces,
        edges=edges,
        base_edge_length=base_edge_length,
        base_surface_area=base_surface_area,
        base_volume=base_volume,
        face_sides=face_sides,
    )
    _DEF_CACHE[key] = definition
    return definition


def _get_definition(key: str) -> ArchimedeanSolidDefinition:
    if key in _DEF_CACHE:
        return _DEF_CACHE[key]
    return _definition_from_data(key)


# Symmetry and dual data for Archimedean solids
_ARCHIMEDEAN_PROPERTIES = {
    'cuboctahedron': {
        'symmetry_group': 'Oh',
        'symmetry_order': 48,
        'rotational_order': 24,
        'dual_name': 'Rhombic Dodecahedron'
    },
    'truncated_tetrahedron': {
        'symmetry_group': 'Td',
        'symmetry_order': 24,
        'rotational_order': 12,
        'dual_name': 'Triakis Tetrahedron'
    },
    'truncated_cube': {
        'symmetry_group': 'Oh',
        'symmetry_order': 48,
        'rotational_order': 24,
        'dual_name': 'Triakis Octahedron'
    },
    'truncated_octahedron': {
        'symmetry_group': 'Oh',
        'symmetry_order': 48,
        'rotational_order': 24,
        'dual_name': 'Tetrakis Hexahedron'
    },
    'rhombicuboctahedron': {
        'symmetry_group': 'Oh',
        'symmetry_order': 48,
        'rotational_order': 24,
        'dual_name': 'Deltoidal Icositetrahedron'
    },
    'truncated_cuboctahedron': {
        'symmetry_group': 'Oh',
        'symmetry_order': 48,
        'rotational_order': 24,
        'dual_name': 'Disdyakis Dodecahedron'
    },
    'snub_cube': {
        'symmetry_group': 'O',
        'symmetry_order': 24,
        'rotational_order': 24,
        'dual_name': 'Pentagonal Icositetrahedron'
    },
    'icosidodecahedron': {
        'symmetry_group': 'Ih',
        'symmetry_order': 120,
        'rotational_order': 60,
        'dual_name': 'Rhombic Triacontahedron'
    },
    'truncated_dodecahedron': {
        'symmetry_group': 'Ih',
        'symmetry_order': 120,
        'rotational_order': 60,
        'dual_name': 'Triakis Icosahedron'
    },
    'truncated_icosahedron': {
        'symmetry_group': 'Ih',
        'symmetry_order': 120,
        'rotational_order': 60,
        'dual_name': 'Pentakis Dodecahedron'
    },
    'rhombicosidodecahedron': {
        'symmetry_group': 'Ih',
        'symmetry_order': 120,
        'rotational_order': 60,
        'dual_name': 'Deltoidal Hexecontahedron'
    },
    'truncated_icosidodecahedron': {
        'symmetry_group': 'Ih',
        'symmetry_order': 120,
        'rotational_order': 60,
        'dual_name': 'Disdyakis Triacontahedron'
    },
    'snub_dodecahedron': {
        'symmetry_group': 'I',
        'symmetry_order': 60,
        'rotational_order': 60,
        'dual_name': 'Pentagonal Hexecontahedron'
    },
}


def _compute_sphere_radii(vertices: List[Vec3], faces: List[Face], volume: float, surface_area: float) -> tuple[float, float, float]:
    """
    Compute inradius, midradius, and circumradius for an Archimedean solid.

    Inradius: Distance from center to nearest face center
    Midradius: Distance from center to nearest edge midpoint
    Circumradius: Distance from center to vertices (all equidistant for uniform solids)
    """
    if not vertices or not faces:
        return (0.0, 0.0, 0.0)

    # Circumradius: distance from origin to any vertex (they're all equidistant)
    circumradius = math.sqrt(sum(c**2 for c in vertices[0]))

    # Inradius: use r = 3V/A (works for all convex polyhedra)
    inradius = (3.0 * volume / surface_area) if surface_area > 0 else 0.0

    # Midradius: find closest edge midpoint to origin
    min_edge_dist = float('inf')
    seen_edges: set[tuple[int, int]] = set()

    for face in faces:
        for i in range(len(face)):
            v1_idx, v2_idx = face[i], face[(i + 1) % len(face)]
            edge = tuple(sorted([v1_idx, v2_idx]))
            if edge in seen_edges:
                continue
            seen_edges.add(edge)

            v1, v2 = vertices[v1_idx], vertices[v2_idx]
            midpoint = tuple((v1[k] + v2[k]) / 2.0 for k in range(3))
            dist = math.sqrt(sum(c**2 for c in midpoint))
            min_edge_dist = min(min_edge_dist, dist)

    midradius = min_edge_dist if min_edge_dist != float('inf') else 0.0

    return (inradius, midradius, circumradius)


class ArchimedeanSolidServiceBase:
    """Base service for Archimedean solids with uniform edge length."""

    DEFINITION_KEY: str = ''

    @classmethod
    def build(cls, edge_length: float = 2.0) -> ArchimedeanSolidResult:
        """
        Build logic.
        
        Args:
            edge_length: Description of edge_length.
        
        Returns:
            Result of build operation.
        """
        if edge_length <= 0:
            raise ValueError('Edge length must be positive')
        definition = _get_definition(cls.DEFINITION_KEY)
        scale = edge_length / definition.base_edge_length
        vertices: List[Vec3] = [
            cast(Vec3, tuple(coord * scale for coord in v))
            for v in definition.canonical_vertices
        ]
        faces = definition.faces
        edges = definition.edges
        surface_area = compute_surface_area(vertices, faces)
        volume = compute_volume(vertices, faces)
        bbox_max_z = max(v[2] for v in vertices)
        payload = SolidPayload(
            vertices=vertices,
            edges=edges,
            faces=faces,
            labels=[
                SolidLabel(text=f"e = {edge_length:.3f}", position=(0.0, 0.0, bbox_max_z + edge_length * 0.25)),
            ],
            metadata={
                'edge_length': edge_length,
                'surface_area': surface_area,
                'volume': volume,
                'face_count': len(faces),
                'edge_count': len(edges),
                'vertex_count': len(vertices),
                'face_sides': definition.face_sides,
            },
            suggested_scale=edge_length,
        )
        # Calculate granular face metrics
        face_metrics: Dict[int, Dict[str, float]] = {}
        # We need regular polygon area formula: Area = (n * s^2) / (4 * tan(pi/n))
        for n_gon, count in definition.face_sides.items():
            if n_gon < 3: continue
            area_single = (n_gon * edge_length**2) / (4 * math.tan(math.pi / n_gon))
            area_total = area_single * count
            face_metrics[n_gon] = {
                'area_single': area_single,
                'area_total': area_total
            }

        # Compute sphere radii
        inradius, midradius, circumradius = _compute_sphere_radii(vertices, faces, volume, surface_area)

        # Sphere surface areas and volumes
        insphere_sa = 4.0 * math.pi * inradius ** 2
        insphere_vol = (4.0 / 3.0) * math.pi * inradius ** 3
        midsphere_sa = 4.0 * math.pi * midradius ** 2
        midsphere_vol = (4.0 / 3.0) * math.pi * midradius ** 3
        circumsphere_sa = 4.0 * math.pi * circumradius ** 2
        circumsphere_vol = (4.0 / 3.0) * math.pi * circumradius ** 3

        # Sphere circumferences
        insphere_circ = 2.0 * math.pi * inradius
        midsphere_circ = 2.0 * math.pi * midradius
        circumsphere_circ = 2.0 * math.pi * circumradius

        # Geometric ratios
        sphericity = (math.pi ** (1.0 / 3.0)) * ((6.0 * volume) ** (2.0 / 3.0)) / surface_area if surface_area > 0 else 0.0
        isoperimetric = (36.0 * math.pi * volume ** 2) / (surface_area ** 3) if surface_area > 0 else 0.0
        sv_ratio = surface_area / volume if volume > 0 else 0.0

        # Topology (Euler characteristic = V - E + F)
        euler_char = len(vertices) - len(edges) + len(faces)

        # Get symmetry and dual info
        default_props = {
            'symmetry_group': 'Unknown',
            'symmetry_order': 0,
            'rotational_order': 0,
            'dual_name': 'Unknown'
        }
        props = _ARCHIMEDEAN_PROPERTIES.get(cls.DEFINITION_KEY, default_props)

        metrics = ArchimedeanSolidMetrics(
            edge_length=edge_length,
            surface_area=surface_area,
            volume=volume,
            face_count=len(faces),
            edge_count=len(edges),
            vertex_count=len(vertices),
            face_sides=definition.face_sides,
            face_metrics=face_metrics,
            inradius=inradius,
            midradius=midradius,
            circumradius=circumradius,
            insphere_surface_area=insphere_sa,
            insphere_volume=insphere_vol,
            midsphere_surface_area=midsphere_sa,
            midsphere_volume=midsphere_vol,
            circumsphere_surface_area=circumsphere_sa,
            circumsphere_volume=circumsphere_vol,
            insphere_circumference=insphere_circ,
            midsphere_circumference=midsphere_circ,
            circumsphere_circumference=circumsphere_circ,
            sphericity=sphericity,
            isoperimetric_quotient=isoperimetric,
            surface_to_volume_ratio=sv_ratio,
            euler_characteristic=euler_char,
            symmetry_group=str(props['symmetry_group']),
            symmetry_order=int(props['symmetry_order']),
            rotational_order=int(props['rotational_order']),
            dual_name=str(props['dual_name']),
        )
        return ArchimedeanSolidResult(payload=payload, metrics=metrics)

    @classmethod
    def payload(cls, edge_length: float = 2.0) -> SolidPayload:
        """
        Payload logic.
        
        Args:
            edge_length: Description of edge_length.
        
        Returns:
            Result of payload operation.
        """
        return cls.build(edge_length=edge_length).payload


class ArchimedeanSolidCalculatorBase:
    """Base calculator for Archimedean solids supporting uniform scaling."""

    SERVICE: Type[ArchimedeanSolidServiceBase] = ArchimedeanSolidServiceBase

    _EDITABLE_PROPERTIES = (
        ('edge_length', 'Edge Length', 'units', 4, True),
        ('surface_area', 'Surface Area', 'units²', 4, False),
        ('volume', 'Volume', 'units³', 4, True),
        ('inradius', 'Inradius', 'units', 4, True),
        ('midradius', 'Midradius', 'units', 4, True),
        ('circumradius', 'Circumradius', 'units', 4, True),
        ('insphere_surface_area', 'Insphere Surface Area', 'units²', 4, True),
        ('insphere_volume', 'Insphere Volume', 'units³', 4, True),
        ('midsphere_surface_area', 'Midsphere Surface Area', 'units²', 4, True),
        ('midsphere_volume', 'Midsphere Volume', 'units³', 4, True),
        ('circumsphere_surface_area', 'Circumsphere Surface Area', 'units²', 4, True),
        ('circumsphere_volume', 'Circumsphere Volume', 'units³', 4, True),
        ('insphere_circumference', 'Insphere Circumference', 'units', 4, True),
        ('midsphere_circumference', 'Midsphere Circumference', 'units', 4, True),
        ('circumsphere_circumference', 'Circumsphere Circumference', 'units', 4, True),
    )

    _READONLY_PROPERTIES = (
        ('face_count', 'Faces', '', 0),
        ('edge_count', 'Edges', '', 0),
        ('vertex_count', 'Vertices', '', 0),
        ('sphericity', 'Sphericity', '', 4),
        ('isoperimetric_quotient', 'Isoperimetric Quotient', '', 4),
        ('surface_to_volume_ratio', 'Surface/Volume Ratio', '1/units', 4),
        ('euler_characteristic', 'Euler Characteristic', '', 0),
        ('symmetry_group', 'Symmetry Group', '', 0),
        ('symmetry_order', 'Symmetry Order', '', 0),
        ('rotational_order', 'Rotational Order', '', 0),
        ('dual_name', 'Dual Solid', '', 0),
    )

    def __init__(self, edge_length: float = 2.0):
        """
          init   logic.
        
        Args:
            edge_length: Description of edge_length.
        
        """
        self._definition = _get_definition(self.SERVICE.DEFINITION_KEY)
        self._formulas = self._build_formulas()

        self._properties: Dict[str, SolidProperty] = {}

        # Add editable properties
        for key, label, unit, precision, editable in self._EDITABLE_PROPERTIES:
            self._properties[key] = SolidProperty(
                name=label,
                key=key,
                unit=unit,
                precision=precision,
                editable=editable,
                formula=self._formulas.get(key),
            )

        # Add readonly properties
        for key, label, unit, precision in self._READONLY_PROPERTIES:
            self._properties[key] = SolidProperty(
                name=label,
                key=key,
                unit=unit,
                precision=precision,
                editable=False,
                formula=self._formulas.get(key),
            )

        # Add dynamic properties for face metrics based on definition
        for n_gon, count in self._definition.face_sides.items():
            if n_gon == 3: name = "Triangle"
            elif n_gon == 4: name = "Square"
            elif n_gon == 5: name = "Pentagon"
            elif n_gon == 6: name = "Hexagon"
            elif n_gon == 8: name = "Octagon"
            elif n_gon == 10: name = "Decagon"
            else: name = f"{n_gon}-gon"
            
            # Individual Area
            key_single = f"area_{n_gon}_single"
            self._properties[key_single] = SolidProperty(
                name=f"{name} Area (x1)",
                key=key_single,
                unit='units²',
                precision=4,
                editable=True,
                formula=self._formulas.get(key_single),
            )
            
            # Total Area
            key_total = f"area_{n_gon}_total"
            self._properties[key_total] = SolidProperty(
                name=f"Total {name}s Area (x{count})",
                key=key_total,
                unit='units²',
                precision=4,
                editable=True,
                formula=self._formulas.get(key_total),
            )

        self._edge_length = edge_length if edge_length > 0 else 2.0
        self._result: ArchimedeanSolidResult | None = None
        self._apply_edge_length(self._edge_length)

    def properties(self) -> List[SolidProperty]:
        """
        Properties logic.

        Returns:
            Result of properties operation.
        """
        # Collect static property keys
        editable_keys = [k for k, *_ in self._EDITABLE_PROPERTIES]
        readonly_keys = [k for k, *_ in self._READONLY_PROPERTIES]
        static_keys = set(editable_keys + readonly_keys)

        # Dynamic face area properties
        dynamic_props = [p for k, p in self._properties.items() if k not in static_keys]
        dynamic_props.sort(key=lambda p: p.key)

        # Return: editable first, then readonly, then dynamic
        result = [self._properties[k] for k in editable_keys if k in self._properties]
        result += [self._properties[k] for k in readonly_keys if k in self._properties]
        result += dynamic_props

        return result

    def set_property(self, key: str, value: float | None) -> bool:
        """
        Configure property logic.
        
        Args:
            key: Description of key.
            value: Description of value.
        
        Returns:
            Result of set_property operation.
        """
        if value is None or value <= 0:
            return False
            
        definition = self._definition
        
        if key == 'edge_length':
            self._apply_edge_length(value)
            return True
        if key == 'volume' and definition.base_volume > 0:
            scale = (value / definition.base_volume) ** (1.0 / 3.0)
            edge_length = definition.base_edge_length * scale
            self._apply_edge_length(edge_length)
            return True
        if key == 'surface_area' and definition.base_surface_area > 0:
            scale = math.sqrt(value / definition.base_surface_area)
            edge_length = definition.base_edge_length * scale
            self._apply_edge_length(edge_length)
            return True
            
        # Handle Dynamic Face Area Properties
        if key.startswith('area_'):
            # Parse n_gon from key "area_{n}_single" or "area_{n}_total"
            parts = key.split('_')
            if len(parts) >= 3 and parts[1].isdigit():
                n_gon = int(parts[1])
                mode = parts[2] # 'single' or 'total'
                
                # Formula: Area = (n * s^2) / (4 * tan(pi/n))
                # s^2 = (Area * 4 * tan(pi/n)) / n
                # s = sqrt(...)
                
                target_area_single = value
                if mode == 'total':
                    # Convert total to single
                    count = definition.face_sides.get(n_gon, 1)
                    target_area_single = value / count
                
                # Solve for edge length
                tan_factor = math.tan(math.pi / n_gon)
                s_sq = (target_area_single * 4 * tan_factor) / n_gon
                if s_sq > 0:
                    new_edge_length = math.sqrt(s_sq)
                    self._apply_edge_length(new_edge_length)
                    return True
                    
        return False

    def clear(self):
        """
        Clear logic.
        
        """
        self._edge_length = 2.0
        for prop in self._properties.values():
            prop.value = None
        self._result = None

    def payload(self) -> SolidPayload | None:
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

    def metrics(self) -> ArchimedeanSolidMetrics | None:
        """
        Metrics logic.
        
        Returns:
            Result of metrics operation.
        """
        return self._result.metrics if self._result else None

    def _apply_edge_length(self, edge_length: float):
        if edge_length <= 0:
            return
        self._edge_length = edge_length
        result = self.SERVICE.build(edge_length=edge_length)
        self._result = result

        m = result.metrics

        # Update all numeric properties from metrics
        values = {
            'edge_length': m.edge_length,
            'surface_area': m.surface_area,
            'volume': m.volume,
            'face_count': float(m.face_count),
            'edge_count': float(m.edge_count),
            'vertex_count': float(m.vertex_count),
            'inradius': m.inradius,
            'midradius': m.midradius,
            'circumradius': m.circumradius,
            'insphere_surface_area': m.insphere_surface_area,
            'insphere_volume': m.insphere_volume,
            'midsphere_surface_area': m.midsphere_surface_area,
            'midsphere_volume': m.midsphere_volume,
            'circumsphere_surface_area': m.circumsphere_surface_area,
            'circumsphere_volume': m.circumsphere_volume,
            'insphere_circumference': m.insphere_circumference,
            'midsphere_circumference': m.midsphere_circumference,
            'circumsphere_circumference': m.circumsphere_circumference,
            'sphericity': m.sphericity,
            'isoperimetric_quotient': m.isoperimetric_quotient,
            'surface_to_volume_ratio': m.surface_to_volume_ratio,
            'euler_characteristic': float(m.euler_characteristic),
            'symmetry_order': float(m.symmetry_order),
            'rotational_order': float(m.rotational_order),
        }
        for k, v in values.items():
            if k in self._properties:
                self._properties[k].value = v

        # String properties stored in name field for display (since value is numeric only)
        if 'symmetry_group' in self._properties:
            self._properties['symmetry_group'].name = f"Symmetry Group ({m.symmetry_group})"
        if 'dual_name' in self._properties:
            self._properties['dual_name'].name = f"Dual: {m.dual_name}"

        # Update dynamic face properties
        if m.face_metrics:
            for n_gon, data in m.face_metrics.items():
                key_single = f"area_{n_gon}_single"
                key_total = f"area_{n_gon}_total"
                if key_single in self._properties:
                    self._properties[key_single].value = data['area_single']
                if key_total in self._properties:
                    self._properties[key_total].value = data['area_total']

    def _build_formulas(self) -> Dict[str, str]:
        base_edge = self._definition.base_edge_length
        base_surface_area = self._definition.base_surface_area
        base_volume = self._definition.base_volume

        formulas: Dict[str, str] = {
            'edge_length': r"e = s",
            'surface_area': rf"A = {base_surface_area:.4f}\left(\frac{{e}}{{{base_edge:.4f}}}\right)^2",
            'volume': rf"V = {base_volume:.4f}\left(\frac{{e}}{{{base_edge:.4f}}}\right)^3",
        }

        for n_gon, count in self._definition.face_sides.items():
            area_expr = rf"\frac{{{n_gon} e^2}}{{4 \tan\left(\frac{{\pi}}{{{n_gon}}}\right)}}"
            formulas[f"area_{n_gon}_single"] = rf"A_{{{n_gon}}} = {area_expr}"
            formulas[f"area_{n_gon}_total"] = rf"A_{{{n_gon},\mathrm{{total}}}} = {count}\times {area_expr}"

        return formulas


class CuboctahedronSolidService(ArchimedeanSolidServiceBase):
    """Cuboctahedron (uniform rectified cube/octahedron).

        CONSTRUCTION INSIGHT:
        =====================
        The cuboctahedron is the “meeting-place” of the cube and octahedron.
        One way to see it: take a cube and slice (rectify) each vertex exactly to
        the midpoint of every incident edge. The original square faces become
        smaller squares, and each original vertex becomes a triangular face.

        Faces (by type):
        - 8 × triangles
        - 6 × squares

        AHA MOMENT:
        ===========
        This is the first Archimedean solid where the uniformity is *not* “one face
        type everywhere” but “one edge length everywhere”. The magic is that
        triangles and squares can interlock around a vertex with identical edge
        lengths, yielding a perfectly uniform vertex figure.

        TOPOLOGY (V/E/F + EULER):
        =========================
        From the mesh data used by this repo:
        - V = 12
        - E = 24
        - F = 14
        - Euler characteristic: χ = V − E + F = 12 − 24 + 14 = 2

        SPHERE RADII (r, ρ, R):
        =======================
        We track three “canonical” radii for uniform solids:
        - Circumradius R: center → vertex (circumsphere).
        - Inradius r: center → face planes (insphere).
            Justification: for any convex polyhedron with an inscribed sphere tangent
            to all faces, V = (1/3)·r·A, so r = 3V/A.
            Even when “insphere tangency” is subtle in theory, r = 3V/A is still the
            natural radius implied by decomposing volume into pyramids on each face.
        - Midradius ρ: center → midpoint of an edge (midsphere).
            In this implementation, ρ is computed as the minimum distance from the
            origin to any edge midpoint.

        SYMMETRY:
        =========
        Symmetry group: Oh (full octahedral), order 48; rotational subgroup order 24.
        Implication: the solid has the same axis structure as a cube/octahedron:
        - 3 fourfold axes through opposite square faces
        - 4 threefold axes through opposite triangular-face triples (cube vertices)
        - 6 twofold axes through opposite edges

        DUAL RELATIONSHIP:
        ===================
        Dual solid: Rhombic Dodecahedron.
        Duality reminder: face-centers of the cuboctahedron become vertices of its
        Catalan dual; dual faces correspond to cuboctahedron vertices.

        IMPLEMENTATION NOTES (THIS REPO):
        =================================
        - Geometry source: `ARCHIMEDEAN_DATA['cuboctahedron']` (canonical vertices + faces).
        - `build(edge_length)` scales canonical coordinates so all edges match the
            requested length.
        - Surface area and volume are computed from the mesh via
            `compute_surface_area()` and `compute_volume()`.
        - Radii are derived by `_compute_sphere_radii()` (R from vertex norm,
            r from 3V/A, ρ from closest edge midpoint).
        - Ratios (sphericity, isoperimetric quotient, surface/volume) are computed
            from the resulting A and V.
        - Per-face-type areas shown in UI use the regular n-gon formula
            $A_n = \\frac{n e^2}{4\\tan(\\pi/n)}$ and are aggregated by face counts.
        """
    DEFINITION_KEY = 'cuboctahedron'


class CuboctahedronSolidCalculator(ArchimedeanSolidCalculatorBase):
    """
    Cuboctahedron Solid Calculator class definition.
    
    """
    SERVICE = CuboctahedronSolidService


class TruncatedTetrahedronSolidService(ArchimedeanSolidServiceBase):
    """Truncated tetrahedron (uniform truncation of a tetrahedron).

    CONSTRUCTION INSIGHT:
    =====================
    Start with a regular tetrahedron and “shave off” (truncate) each vertex by
    a plane cut. When the cut depth is chosen so that every resulting edge is
    the same length, the four original triangular faces become *hexagons*, and
    each original vertex becomes a new triangular face.

    Faces (by type):
    - 4 × triangles (from truncated vertices)
    - 4 × hexagons (from the original tetrahedron faces)

    AHA MOMENT:
    ===========
    Truncation converts a single face type into two — yet preserves uniform edge
    length. The “uniformity” condition forces the truncation depth, and the
    hexagons that appear are the original triangles with their corners clipped.

    TOPOLOGY (V/E/F + EULER):
    =========================
    From the mesh data used by this repo:
    - V = 12
    - E = 18
    - F = 8
    - Euler characteristic: χ = 12 − 18 + 8 = 2

    SPHERE RADII (r, ρ, R):
    =======================
    - Circumradius R: computed as the distance from the origin to any vertex.
    - Inradius r: computed by $r = 3V/A$ (volume-to-area identity).
    - Midradius ρ: computed as the minimum distance from the origin to any
      unique edge midpoint.

    SYMMETRY:
    =========
    Symmetry group: Td, order 24; rotational order 12.
    Implication: tetrahedral axis structure (3-fold rotations through opposite
    “vertex directions” and 2-fold rotations through opposite edge midpoints).

    DUAL RELATIONSHIP:
    ===================
    Dual solid: Triakis Tetrahedron (a Catalan solid).
    The dual encodes the face-normal directions and equal edge constraints in a
    “kite-like” faceting.

    IMPLEMENTATION NOTES (THIS REPO):
    =================================
    Uses `ARCHIMEDEAN_DATA['truncated_tetrahedron']`, scales to target edge
    length, then computes mesh area/volume → radii → sphere metrics → ratios.
    Face-type area breakdown uses the regular n-gon area formula, aggregated by
    the face counts (triangles and hexagons).
    """
    DEFINITION_KEY = 'truncated_tetrahedron'


class TruncatedTetrahedronSolidCalculator(ArchimedeanSolidCalculatorBase):
    """
    Truncated Tetrahedron Solid Calculator class definition.
    
    """
    SERVICE = TruncatedTetrahedronSolidService


class TruncatedCubeSolidService(ArchimedeanSolidServiceBase):
    """Truncated cube (uniform truncation of a cube).

    CONSTRUCTION INSIGHT:
    =====================
    Truncate each vertex of a cube with a plane cut. With the uniform truncation
    depth, the original 6 square faces become *octagons*, and each original cube
    vertex becomes a triangular face.

    Faces (by type):
    - 8 × triangles
    - 6 × octagons

    AHA MOMENT:
    ===========
    The cube’s 3 edges meeting at each vertex are symmetric. A single truncation
    depth clips all corners equally, and the requirement “all edges equal”
    forces the octagons and triangles to share the same edge length.

    TOPOLOGY (V/E/F + EULER):
    =========================
    From the mesh data used by this repo:
    - V = 24
    - E = 36
    - F = 14
    - Euler characteristic: χ = 24 − 36 + 14 = 2

    SPHERE RADII (r, ρ, R):
    =======================
    - R (circumradius): vertex norm (origin-centered canonical mesh).
    - r (inradius): $r = 3V/A$ from computed mesh volume and area.
    - ρ (midradius): distance to the nearest edge midpoint (min over edges).

    SYMMETRY:
    =========
    Symmetry group: Oh, order 48; rotational order 24.
    Implication: full cube/octahedral symmetry; octagonal faces align with the
    cube’s original face planes, and rotational axes correspond to cube axes.

    DUAL RELATIONSHIP:
    ===================
    Dual solid: Triakis Octahedron.
    The dual replaces each face type with a corresponding vertex orbit, encoding
    the truncation in a “pyramided” octahedral form.

    IMPLEMENTATION NOTES (THIS REPO):
    =================================
    Mesh area/volume are computed directly from triangulated faces; radii are
    derived afterward (R from vertex norm, r from 3V/A, ρ from edge midpoints).
    Face-type areas displayed in UI use the regular 3-gon and 8-gon formulas.
    """
    DEFINITION_KEY = 'truncated_cube'


class TruncatedCubeSolidCalculator(ArchimedeanSolidCalculatorBase):
    """
    Truncated Cube Solid Calculator class definition.
    
    """
    SERVICE = TruncatedCubeSolidService


class TruncatedOctahedronSolidService(ArchimedeanSolidServiceBase):
    """Truncated octahedron (uniform truncation of an octahedron; space-filling).

    CONSTRUCTION INSIGHT:
    =====================
    Truncate each vertex of a regular octahedron. At the uniform truncation
    depth, the original 8 triangular faces become *hexagons*, and each original
    vertex becomes a square face.

    Faces (by type):
    - 6 × squares
    - 8 × hexagons

    AHA MOMENT:
    ===========
    This is the only Archimedean solid that tiles 3D space by translation.
    The “square + hexagon” face set is not decorative — it is exactly what lets
    copies pack without gaps.

    TOPOLOGY (V/E/F + EULER):
    =========================
    From the mesh data used by this repo:
    - V = 24
    - E = 36
    - F = 14
    - Euler characteristic: χ = 24 − 36 + 14 = 2

    SPHERE RADII (r, ρ, R):
    =======================
    - R: distance from center to a vertex (vertex norm).
    - r: computed via $r = 3V/A$ from mesh volume and surface area.
    - ρ: minimum distance to any edge midpoint.

    SYMMETRY:
    =========
    Symmetry group: Oh, order 48; rotational order 24.
    Implication: full octahedral symmetry; square faces are aligned with former
    vertex directions, hexagons with former face directions.

    DUAL RELATIONSHIP:
    ===================
    Dual solid: Tetrakis Hexahedron.

    IMPLEMENTATION NOTES (THIS REPO):
    =================================
    We compute A and V from the scaled mesh, then derive radii and secondary
    sphere metrics (surface areas/volumes/circumferences) from those radii.
    Face areas shown are computed as regular 4-gon and 6-gon areas from edge
    length and multiplied by face counts.
    """
    DEFINITION_KEY = 'truncated_octahedron'


class TruncatedOctahedronSolidCalculator(ArchimedeanSolidCalculatorBase):
    """
    Truncated Octahedron Solid Calculator class definition.
    
    """
    SERVICE = TruncatedOctahedronSolidService


class RhombicuboctahedronSolidService(ArchimedeanSolidServiceBase):
    """Rhombicuboctahedron (uniform expansion between cube and octahedron).

    CONSTRUCTION INSIGHT:
    =====================
    The rhombicuboctahedron can be viewed as a cube/octahedron “expanded” so
    that both the cube’s vertices and the octahedron’s vertices are opened into
    triangular faces, while the cube’s square faces split into a belt of squares.
    It is a classic example of a uniform solid with *many* squares plus triangles.

    Faces (by type):
    - 8 × triangles
    - 18 × squares

    AHA MOMENT:
    ===========
    Uniformity is maintained by a single edge length even though squares appear
    in two different “roles” (some adjacent to triangles, some forming rings).
    The vertex figure is constant across all 24 vertices.

    TOPOLOGY (V/E/F + EULER):
    =========================
    From the mesh data used by this repo:
    - V = 24
    - E = 48
    - F = 26
    - Euler characteristic: χ = 24 − 48 + 26 = 2

    SPHERE RADII (r, ρ, R):
    =======================
    - R: computed from vertex norm (canonical mesh is centered at the origin).
    - r: computed by $r = 3V/A$ using mesh volume and surface area.
    - ρ: computed from the closest edge midpoint to the origin.

    SYMMETRY:
    =========
    Symmetry group: Oh, order 48; rotational order 24.
    Implication: same axis hierarchy as the cube; face orbits fall into the
    cube’s symmetry directions, and the metric functions are invariant under all
    these rotations/reflections.

    DUAL RELATIONSHIP:
    ===================
    Dual solid: Deltoidal Icositetrahedron.

    IMPLEMENTATION NOTES (THIS REPO):
    =================================
    The service is data-driven: vertices/faces come from `ARCHIMEDEAN_DATA` and
    are uniformly scaled. All reported counts (V/E/F), Euler characteristic, and
    face-type breakdowns are computed from that mesh.
    """
    DEFINITION_KEY = 'rhombicuboctahedron'


class RhombicuboctahedronSolidCalculator(ArchimedeanSolidCalculatorBase):
    """
    Rhombicuboctahedron Solid Calculator class definition.
    
    """
    SERVICE = RhombicuboctahedronSolidService


class RhombicosidodecahedronSolidService(ArchimedeanSolidServiceBase):
    """Rhombicosidodecahedron (uniform expansion in the icosahedral family).

    CONSTRUCTION INSIGHT:
    =====================
    This solid sits “between” the dodecahedron and icosahedron families.
    Intuitively: start from the icosidodecahedron (which already mixes triangles
    and pentagons) and expand/adjust so that squares appear along the edges while
    preserving equal edge length and a uniform vertex figure.

    Faces (by type):
    - 20 × triangles
    - 30 × squares
    - 12 × pentagons

    AHA MOMENT:
    ===========
    The icosahedral symmetry (5-fold axes) can host a *three-face-type* uniform
    tiling around each vertex. The squares are not “added on” — they arise from
    the consistent way triangles and pentagons can be separated while keeping a
    single edge length.

    TOPOLOGY (V/E/F + EULER):
    =========================
    From the mesh data used by this repo:
    - V = 60
    - E = 120
    - F = 62
    - Euler characteristic: χ = 60 − 120 + 62 = 2

    SPHERE RADII (r, ρ, R):
    =======================
    - R: center → vertex (vertex norm).
    - r: derived from $r = 3V/A$.
    - ρ: nearest edge midpoint distance.
    These three radii summarize “how spherical” the solid is at the level of
    faces (r), edges (ρ), and vertices (R).

    SYMMETRY:
    =========
    Symmetry group: Ih (full icosahedral), order 120; rotational order 60.
    Implication: 5-fold, 3-fold, and 2-fold rotational axes exist in the same
    pattern as the dodecahedron/icosahedron, and all measured metrics are
    invariant under those symmetries.

    DUAL RELATIONSHIP:
    ===================
    Dual solid: Deltoidal Hexecontahedron.
    As a Catalan dual, it trades the rhombicosidodecahedron’s uniform vertex
    figure for face-transitivity.

    IMPLEMENTATION NOTES (THIS REPO):
    =================================
    This service uses mesh-derived A and V rather than closed forms. The radii
    are computed from those measures and the canonical origin-centered geometry.
    Face-type areas in UI are computed from regular n-gon formulas and the face
    counts (20/30/12).
    """
    DEFINITION_KEY = 'rhombicosidodecahedron'


class RhombicosidodecahedronSolidCalculator(ArchimedeanSolidCalculatorBase):
    """
    Rhombicosidodecahedron Solid Calculator class definition.
    
    """
    SERVICE = RhombicosidodecahedronSolidService


class TruncatedCuboctahedronSolidService(ArchimedeanSolidServiceBase):
    """Truncated cuboctahedron (a.k.a. great rhombicuboctahedron).

    CONSTRUCTION INSIGHT:
    =====================
    This solid can be seen as “truncate the cuboctahedron” in the uniform way.
    The truncation turns original vertices into new faces, and the original
    triangles and squares are expanded into larger polygons.

    Faces (by type):
    - 12 × squares
    - 8 × hexagons
    - 6 × octagons

    AHA MOMENT:
    ===========
    Truncation does not merely “add faces”; it reorganizes adjacency so that
    three different polygon types share a single edge length. The squares become
    a mediating face type between hexagons and octagons.

    TOPOLOGY (V/E/F + EULER):
    =========================
    From the mesh data used by this repo:
    - V = 48
    - E = 72
    - F = 26
    - Euler characteristic: χ = 48 − 72 + 26 = 2

    SPHERE RADII (r, ρ, R):
    =======================
    - R: computed from the vertex norm of the scaled mesh.
    - r: computed via $r = 3V/A$ (mesh volume and area).
    - Midradius ρ: computed from the minimum distance to any edge midpoint.

    SYMMETRY:
    =========
    Symmetry group: Oh, order 48; rotational order 24.
    Implication: full cube/octahedral symmetry; face orbits (4/6/8-gons) align
    with the cube’s axial directions.

    DUAL RELATIONSHIP:
    ===================
    Dual solid: Disdyakis Dodecahedron.

    IMPLEMENTATION NOTES (THIS REPO):
    =================================
    The service is purely data-driven: canonical vertices/faces are scaled,
    mesh A and V are computed, then radii and derived sphere metrics/ratios are
    computed. Face-type area summaries use regular n-gon formulas for 4, 6, 8.
    """
    DEFINITION_KEY = 'truncated_cuboctahedron'


class TruncatedCuboctahedronSolidCalculator(ArchimedeanSolidCalculatorBase):
    """
    Truncated Cuboctahedron Solid Calculator class definition.
    
    """
    SERVICE = TruncatedCuboctahedronSolidService


class IcosidodecahedronSolidService(ArchimedeanSolidServiceBase):
    """Icosidodecahedron (uniform rectified dodecahedron/icosahedron).

    CONSTRUCTION INSIGHT:
    =====================
    The icosidodecahedron is the icosahedral-family analogue of the
    cuboctahedron. Rectify a dodecahedron (or equivalently an icosahedron):
    slice each vertex down to the midpoints of incident edges. The original
    faces become one polygon type, and each original vertex becomes the other.

    Faces (by type):
    - 20 × triangles
    - 12 × pentagons

    AHA MOMENT:
    ===========
    This is the “bridge” solid where the dodecahedron and icosahedron share the
    same edge graph after rectification. Triangles and pentagons alternate with
    a uniform vertex figure, reflecting the underlying 5-fold symmetry.

    TOPOLOGY (V/E/F + EULER):
    =========================
    From the mesh data used by this repo:
    - V = 30
    - E = 60
    - F = 32
    - Euler characteristic: χ = 30 − 60 + 32 = 2

    SPHERE RADII (r, ρ, R):
    =======================
    - R: computed from vertex norm.
    - r: computed by $r = 3V/A$.
    - ρ: computed as nearest edge midpoint distance.
    These three radii are especially meaningful here: faces are “dual-family”
    (triangles + pentagons), edges mediate, vertices sit on the circumsphere.

    SYMMETRY:
    =========
    Symmetry group: Ih, order 120; rotational order 60.
    Implication: full icosahedral symmetry (including reflections). Expect
    5-fold axes through opposite pentagon face centers and 3-fold axes through
    opposite triangle face centers.

    DUAL RELATIONSHIP:
    ===================
    Dual solid: Rhombic Triacontahedron.

    IMPLEMENTATION NOTES (THIS REPO):
    =================================
    All numeric metrics are derived from the canonical mesh after scaling:
    - A and V from `compute_surface_area` / `compute_volume`
    - radii from `_compute_sphere_radii`
    - ratios from A and V
    Face-type areas are computed analytically as regular 3-gons and 5-gons.
    """
    DEFINITION_KEY = 'icosidodecahedron'


class IcosidodecahedronSolidCalculator(ArchimedeanSolidCalculatorBase):
    """
    Icosidodecahedron Solid Calculator class definition.
    
    """
    SERVICE = IcosidodecahedronSolidService


class TruncatedDodecahedronSolidService(ArchimedeanSolidServiceBase):
    """Truncated dodecahedron (uniform truncation of a dodecahedron).

    CONSTRUCTION INSIGHT:
    =====================
    Truncate each vertex of a regular dodecahedron. With the uniform truncation
    depth, each original pentagonal face becomes a *decagon*, and each original
    vertex becomes a triangular face.

    Faces (by type):
    - 20 × triangles
    - 12 × decagons

    AHA MOMENT:
    ===========
    A pentagon has the golden ratio woven into its diagonals; truncating the
    dodecahedron exposes that 5-fold structure at two scales: the decagon
    “remembers” the pentagon’s symmetry while triangles mark the original
    vertex directions.

    TOPOLOGY (V/E/F + EULER):
    =========================
    From the mesh data used by this repo:
    - V = 60
    - E = 90
    - F = 32
    - Euler characteristic: χ = 60 − 90 + 32 = 2

    SPHERE RADII (r, ρ, R):
    =======================
    - R: vertex norm.
    - r: $r = 3V/A$ from mesh measures.
    - ρ: closest edge midpoint distance.

    SYMMETRY:
    =========
    Symmetry group: Ih, order 120; rotational order 60.
    Implication: full icosahedral symmetry; decagon face normals lie on the same
    orbit structure as the original dodecahedron’s face normals.

    DUAL RELATIONSHIP:
    ===================
    Dual solid: Triakis Icosahedron.

    IMPLEMENTATION NOTES (THIS REPO):
    =================================
    Uses the canonical mesh from `ARCHIMEDEAN_DATA`, scaled to target edge. A
    and V come from mesh computation; radii/ratios follow. UI face areas come
    from the regular 3-gon and 10-gon formulas aggregated by face counts.
    """
    DEFINITION_KEY = 'truncated_dodecahedron'


class TruncatedDodecahedronSolidCalculator(ArchimedeanSolidCalculatorBase):
    """
    Truncated Dodecahedron Solid Calculator class definition.
    
    """
    SERVICE = TruncatedDodecahedronSolidService


class TruncatedIcosahedronSolidService(ArchimedeanSolidServiceBase):
    """Truncated icosahedron (uniform truncation of an icosahedron; “soccer ball”).

    CONSTRUCTION INSIGHT:
    =====================
    Truncate each vertex of a regular icosahedron. With the uniform truncation
    depth, each original triangular face becomes a *hexagon*, and each original
    vertex becomes a pentagonal face.

    Faces (by type):
    - 12 × pentagons
    - 20 × hexagons

    AHA MOMENT:
    ===========
    The famous “pentagon + hexagon” pattern is not arbitrary: 12 pentagons are
    forced by Euler topology for convex polyhedra with mostly hexagons.
    Uniform truncation of the icosahedron produces exactly that balance while
    keeping all edges equal.

    TOPOLOGY (V/E/F + EULER):
    =========================
    From the mesh data used by this repo:
    - V = 60
    - E = 90
    - F = 32
    - Euler characteristic: χ = 60 − 90 + 32 = 2

    SPHERE RADII (r, ρ, R):
    =======================
    - R: computed from vertex norm (circumsphere).
    - r: computed by $r = 3V/A$ (insphere radius implied by pyramid decomposition).
    - ρ: computed as the minimum edge-midpoint distance (midsphere radius).

    SYMMETRY:
    =========
    Symmetry group: Ih, order 120; rotational order 60.
    Implication: full icosahedral symmetry; there are 6 fivefold axes through
    opposite pentagon centers and 10 threefold axes through hexagon triples.

    DUAL RELATIONSHIP:
    ===================
    Dual solid: Pentakis Dodecahedron.

    IMPLEMENTATION NOTES (THIS REPO):
    =================================
    This service intentionally avoids claiming closed forms. Instead:
    - scale canonical mesh → compute A and V
    - derive (r, ρ, R) via `_compute_sphere_radii`
    - compute sphere surface areas/volumes, circumferences, and ratios
    - compute face-type areas as regular 5-gons and 6-gons from edge length
    """
    DEFINITION_KEY = 'truncated_icosahedron'


class TruncatedIcosahedronSolidCalculator(ArchimedeanSolidCalculatorBase):
    """
    Truncated Icosahedron Solid Calculator class definition.
    
    """
    SERVICE = TruncatedIcosahedronSolidService


class TruncatedIcosidodecahedronSolidService(ArchimedeanSolidServiceBase):
    """Truncated icosidodecahedron (a.k.a. great rhombicosidodecahedron).

    CONSTRUCTION INSIGHT:
    =====================
    Truncate the icosidodecahedron uniformly. The truncation introduces a third
    face type: squares appear as the “edge mediators” while the original
    triangle/pentagon structure expands into larger polygons.

    Faces (by type):
    - 30 × squares
    - 20 × hexagons
    - 12 × decagons

    AHA MOMENT:
    ===========
    In the icosahedral symmetry family, truncation can yield three polygon types
    in a perfectly uniform way. Squares act like “buffers” between the 6-gons and
    10-gons, letting a single edge length serve radically different curvatures.

    TOPOLOGY (V/E/F + EULER):
    =========================
    From the mesh data used by this repo:
    - V = 120
    - E = 180
    - F = 62
    - Euler characteristic: χ = 120 − 180 + 62 = 2

    SPHERE RADII (r, ρ, R):
    =======================
    - R: computed from vertex norm.
    - r: computed via $r = 3V/A$.
    - ρ: computed from the nearest edge midpoint.

    SYMMETRY:
    =========
    Symmetry group: Ih, order 120; rotational order 60.
    Implication: full icosahedral symmetry; face types partition into symmetry
    orbits consistent with 5-fold/3-fold/2-fold axes.

    DUAL RELATIONSHIP:
    ===================
    Dual solid: Disdyakis Triacontahedron.

    IMPLEMENTATION NOTES (THIS REPO):
    =================================
    Computation is mesh-first:
    - A and V from the scaled triangulated surface
    - radii from `_compute_sphere_radii`
    - ratios and sphere properties derived afterward
    UI face areas are analytic regular n-gon areas for n ∈ {4, 6, 10}.
    """
    DEFINITION_KEY = 'truncated_icosidodecahedron'


class TruncatedIcosidodecahedronSolidCalculator(ArchimedeanSolidCalculatorBase):
    """
    Truncated Icosidodecahedron Solid Calculator class definition.
    
    """
    SERVICE = TruncatedIcosidodecahedronSolidService


class SnubCubeSolidService(ArchimedeanSolidServiceBase):
    """Snub cube (chiral uniform solid in the octahedral family).

    CONSTRUCTION INSIGHT:
    =====================
    The snub cube is produced by a “twist and triangulate” operation on the cube
    family: squares remain, but most of the surface becomes triangles arranged
    in a way that breaks mirror symmetry.

    Faces (by type):
    - 32 × triangles
    - 6 × squares

    AHA MOMENT:
    ===========
    Chiral uniformity: the snub cube comes in left-handed and right-handed
    variants (mirror images). Yet both variants have the same metric invariants
    (A, V, radii, ratios) and the same edge length.

    TOPOLOGY (V/E/F + EULER):
    =========================
    From the mesh data used by this repo:
    - V = 24
    - E = 60
    - F = 38
    - Euler characteristic: χ = 24 − 60 + 38 = 2

    SPHERE RADII (r, ρ, R):
    =======================
    - R: computed from vertex norm.
    - r: computed by $r = 3V/A$.
    - ρ: computed as the nearest edge midpoint distance.
    Note: for snub solids, “insphere” tangency can be more subtle to reason about
    analytically; this service uses the robust volume/area-derived r.

    SYMMETRY:
    =========
    Symmetry group: O (rotational octahedral), order 24; rotational order 24.
    Implication: rotations preserve the solid, but reflections do not (chiral).
    In other words, the full Oh symmetry is reduced to its orientation-preserving
    subgroup.

    DUAL RELATIONSHIP:
    ===================
    Dual solid: Pentagonal Icositetrahedron.

    IMPLEMENTATION NOTES (THIS REPO):
    =================================
    Uses canonical mesh data for one handedness. Metric computation is purely
    geometric (mesh A/V → radii → ratios), so left/right variants would produce
    identical scalar metrics.
    """
    DEFINITION_KEY = 'snub_cube'


class SnubCubeSolidCalculator(ArchimedeanSolidCalculatorBase):
    """
    Snub Cube Solid Calculator class definition.
    
    """
    SERVICE = SnubCubeSolidService


class SnubDodecahedronSolidService(ArchimedeanSolidServiceBase):
    """Snub dodecahedron (chiral uniform solid in the icosahedral family).

    CONSTRUCTION INSIGHT:
    =====================
    The snub dodecahedron is the icosahedral-family counterpart to the snub cube:
    a “snubbing” operation introduces a pervasive triangulation while preserving
    a set of pentagonal faces. The result is chiral (two mirror forms).

    Faces (by type):
    - 80 × triangles
    - 12 × pentagons

    AHA MOMENT:
    ===========
    The icosahedral symmetry’s 5-fold structure is strong enough to support a
    uniform triangulated field *and* keep pentagons as stable anchors — but the
    price is chirality. Reflection symmetry is lost; rotational symmetry remains.

    TOPOLOGY (V/E/F + EULER):
    =========================
    From the mesh data used by this repo:
    - V = 60
    - E = 150
    - F = 92
    - Euler characteristic: χ = 60 − 150 + 92 = 2

    SPHERE RADII (r, ρ, R):
    =======================
    - R: computed from vertex norm.
    - r: computed via $r = 3V/A$.
    - ρ: computed via nearest edge midpoint distance.
    These three radii again separate face/edge/vertex “sphericity layers.”

    SYMMETRY:
    =========
    Symmetry group: I (rotational icosahedral), order 60; rotational order 60.
    Implication: rotations preserve the solid, but reflections do not (chiral).
    The full Ih symmetry is reduced to its orientation-preserving subgroup.

    DUAL RELATIONSHIP:
    ===================
    Dual solid: Pentagonal Hexecontahedron.

    IMPLEMENTATION NOTES (THIS REPO):
    =================================
    The service computes all metrics from the scaled canonical mesh:
    - mesh surface area/volume → radii (r, ρ, R) → derived sphere metrics + ratios
    Since the output metrics are scalar and rotation-invariant, they match for
    both handedness variants.
    """
    DEFINITION_KEY = 'snub_dodecahedron'


class SnubDodecahedronSolidCalculator(ArchimedeanSolidCalculatorBase):
    """
    Snub Dodecahedron Solid Calculator class definition.
    
    """
    SERVICE = SnubDodecahedronSolidService


__all__ = [
    'ArchimedeanSolidMetrics',
    'ArchimedeanSolidResult',
    'ArchimedeanSolidServiceBase',
    'ArchimedeanSolidCalculatorBase',
    'CuboctahedronSolidService',
    'CuboctahedronSolidCalculator',
    'TruncatedTetrahedronSolidService',
    'TruncatedTetrahedronSolidCalculator',
    'TruncatedCubeSolidService',
    'TruncatedCubeSolidCalculator',
    'TruncatedOctahedronSolidService',
    'TruncatedOctahedronSolidCalculator',
    'RhombicuboctahedronSolidService',
    'RhombicuboctahedronSolidCalculator',
    'RhombicosidodecahedronSolidService',
    'RhombicosidodecahedronSolidCalculator',
    'TruncatedCuboctahedronSolidService',
    'TruncatedCuboctahedronSolidCalculator',
    'IcosidodecahedronSolidService',
    'IcosidodecahedronSolidCalculator',
    'TruncatedDodecahedronSolidService',
    'TruncatedDodecahedronSolidCalculator',
    'TruncatedIcosahedronSolidService',
    'TruncatedIcosahedronSolidCalculator',
    'TruncatedIcosidodecahedronSolidService',
    'TruncatedIcosidodecahedronSolidCalculator',
    'SnubCubeSolidService',
    'SnubCubeSolidCalculator',
    'SnubDodecahedronSolidService',
    'SnubDodecahedronSolidCalculator',
]