"""Platonic solid based transition helpers for 3D geometric analysis."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple, cast

from shared.services.geometry.archimedean import CuboctahedronSolidService
from shared.services.geometry.cube import CubeSolidService
from shared.services.geometry.dodecahedron import DodecahedronSolidService
from shared.services.geometry.icosahedron import IcosahedronSolidService
from shared.services.geometry.octahedron import OctahedronSolidService
from shared.services.geometry.tetrahedron import TetrahedronSolidService
from shared.services.geometry.solid_payload import SolidPayload

from .ternary_service import TernaryService
from .ternary_transition_service import TernaryTransitionService

Vec3 = Tuple[float, float, float]


@dataclass(frozen=True)
class SolidVertex3D:
    """Represents a vertex on a Platonic solid."""

    index: int
    label: str
    value: int
    position: Vec3


@dataclass(frozen=True)
class SolidTransition3D:
    """Directed ternary transition between Platonic solid vertices."""

    family_key: str
    family_label: str
    distance: float
    from_index: int
    to_index: int
    from_value: int
    to_value: int
    from_ternary: str
    to_ternary: str
    result_ternary: str
    result_decimal: int


@dataclass(frozen=True)
class SolidFamilyGroup:
    """Collection of transitions that share a geometric distance."""

    key: str
    label: str
    distance: float
    transitions: List[SolidTransition3D]
    summary: Dict[str, object]
    segments: List[Tuple[int, int]]


@dataclass(frozen=True)
class PlatonicSolidGeometry:
    """Resolved geometry payload for a Platonic solid selection."""

    key: str
    name: str
    vertices: List[SolidVertex3D]
    edges: List[Tuple[int, int]]
    faces: List[Tuple[int, ...]]


class PlatonicTransitionService:
    """Generate ternary transitions using Platonic and related uniform solids."""

    _DEFAULT_EDGE = 1.0
    _ROUND_DIGITS = 6
    _SOLIDS: Dict[str, Dict[str, object]] = {
        "tetrahedron": {
            "name": "Tetrahedron",
            "builder": TetrahedronSolidService.build,
        },
        "cube": {
            "name": "Cube",
            "builder": CubeSolidService.build,
        },
        "octahedron": {
            "name": "Octahedron",
            "builder": OctahedronSolidService.build,
        },
        "dodecahedron": {
            "name": "Dodecahedron",
            "builder": DodecahedronSolidService.build,
        },
        "icosahedron": {
            "name": "Icosahedron",
            "builder": IcosahedronSolidService.build,
        },
        "cuboctahedron": {
            "name": "Cuboctahedron (Archimedean)",
            "builder": CuboctahedronSolidService.build,
        },
    }

    @classmethod
    def get_solid_options(cls) -> List[Dict[str, object]]:
        """Return selectable Platonic solid metadata for UI controls."""
        options: List[Dict[str, object]] = []
        for key, descriptor in cls._SOLIDS.items():
            payload = cls._build_payload(cast(Callable[[float], object], descriptor["builder"]))
            vertex_count = len(payload.vertices)
            options.append(
                {
                    "key": key,
                    "name": descriptor["name"],
                    "vertex_count": vertex_count,
                    "face_count": len(payload.faces),
                }
            )
        return options

    @classmethod
    def build_geometry(
        cls,
        solid_key: Optional[str],
        values: Optional[Sequence[int]] = None,
    ) -> PlatonicSolidGeometry:
        """Resolve vertices, edges, and faces for the requested solid."""
        descriptor = cls._SOLIDS.get(solid_key or "")
        if descriptor is None:
            # fallback to the first registered solid
            first_key = next(iter(cls._SOLIDS))
            descriptor = cls._SOLIDS[first_key]
            solid_key = first_key
        assert solid_key is not None
        payload = cls._build_payload(cast(Callable[[float], object], descriptor["builder"]))
        normalized = cls._normalize_values(len(payload.vertices), values)
        vertices = [
            SolidVertex3D(
                index=idx,
                label=f"V{idx + 1}",
                value=normalized[idx],
                position=(float(vx), float(vy), float(vz)),
            )
            for idx, (vx, vy, vz) in enumerate(payload.vertices)
        ]
        edge_source = payload.edges or []
        face_source = payload.faces or []
        edges = [
            (int(start), int(end))
            for start, end in edge_source
        ]
        faces = [
            tuple(int(vertex) for vertex in face)
            for face in face_source
        ]
        return PlatonicSolidGeometry(
            key=solid_key,
            name=str(descriptor["name"]),
            vertices=vertices,
            edges=edges,
            faces=faces,
        )

    @classmethod
    def generate_families(cls, geometry: PlatonicSolidGeometry) -> List[SolidFamilyGroup]:
        """
        Generate families logic.
        
        Args:
            geometry: Description of geometry.
        
        Returns:
            Result of generate_families operation.
        """
        if not geometry.vertices:
            return []
        pair_map, bucket_distances = cls._build_distance_index(geometry.vertices)
        if not bucket_distances:
            return []
        ordered_buckets = sorted(bucket_distances.items(), key=lambda item: item[1])
        families: List[SolidFamilyGroup] = []
        total = len(ordered_buckets)
        for order, (bucket_key, distance) in enumerate(ordered_buckets):
            label = cls._family_label(order, total)
            transitions: List[SolidTransition3D] = []
            for (from_idx, to_idx), bucket in pair_map.items():
                if bucket != bucket_key:
                    continue
                from_vertex = geometry.vertices[from_idx]
                to_vertex = geometry.vertices[to_idx]
                transitions.append(
                    cls._build_transition(
                        from_vertex,
                        to_vertex,
                        family_key=bucket_key,
                        family_label=label,
                        distance=distance,
                    )
                )
            segments = cls._segment_list(pair_map, bucket_key)
            summary = cls._summarize(transitions)
            families.append(
                SolidFamilyGroup(
                    key=bucket_key,
                    label=label,
                    distance=distance,
                    transitions=transitions,
                    summary=summary,
                    segments=segments,
                )
            )
        return families

    @classmethod
    def generate_face_sequences(
        cls,
        geometry: PlatonicSolidGeometry,
    ) -> List[Dict[str, object]]:
        """
        Generate face sequences logic.
        
        Args:
            geometry: Description of geometry.
        
        Returns:
            Result of generate_face_sequences operation.
        """
        if not geometry.faces or not geometry.vertices:
            return []
        lookup = {vertex.index: vertex for vertex in geometry.vertices}
        sequences: List[Dict[str, object]] = []
        for face_index, face in enumerate(geometry.faces):
            cycle = list(dict.fromkeys(int(idx) for idx in face))
            if len(cycle) < 3:
                continue
            transitions: List[SolidTransition3D] = []
            segments: List[Tuple[int, int]] = []
            for pos, start_idx in enumerate(cycle):
                end_idx = cycle[(pos + 1) % len(cycle)]
                start = lookup.get(start_idx)
                end = lookup.get(end_idx)
                if start is None or end is None:
                    continue
                transitions.append(
                    cls._build_transition(
                        start,
                        end,
                        family_key=f"face_{face_index}",
                        family_label=f"Face {face_index + 1}",
                        distance=cls._distance(start.position, end.position),
                    )
                )
                segments.append((start_idx, end_idx))
            if not transitions:
                continue
            sequences.append(
                {
                    "name": f"Face {face_index + 1}",
                    "description": f"{len(cycle)}-cycle perimeter",
                    "transitions": transitions,
                    "segments": segments,
                    "summary": cls._summarize(transitions),
                }
            )
        return sequences

    # -- helpers ---------------------------------------------------------

    @classmethod
    def _build_payload(cls, builder: Callable[[float], object]) -> SolidPayload:
        result = builder(cls._DEFAULT_EDGE)
        payload = getattr(result, "payload", result)
        if not isinstance(payload, SolidPayload):
            raise TypeError("Solid builder must return SolidPayload or an object with a payload attribute")
        return payload

    @staticmethod
    def _normalize_values(count: int, values: Optional[Sequence[int]]) -> List[int]:
        if not values:
            return list(range(1, count + 1))
        normalized = list(values[:count])
        if len(normalized) < count:
            normalized.extend(0 for _ in range(count - len(normalized)))
        return normalized

    @classmethod
    def _build_distance_index(
        cls,
        vertices: Sequence[SolidVertex3D],
    ) -> Tuple[Dict[Tuple[int, int], str], Dict[str, float]]:
        pair_map: Dict[Tuple[int, int], str] = {}
        bucket_distances: Dict[str, float] = {}
        for from_vertex in vertices:
            for to_vertex in vertices:
                if from_vertex.index == to_vertex.index:
                    continue
                distance = cls._distance(from_vertex.position, to_vertex.position)
                bucket_key = cls._bucket_key(distance)
                pair_map[(from_vertex.index, to_vertex.index)] = bucket_key
                bucket_distances.setdefault(bucket_key, distance)
        return pair_map, bucket_distances

    @staticmethod
    def _distance(a: Vec3, b: Vec3) -> float:
        return math.dist(a, b)

    @classmethod
    def _bucket_key(cls, distance: float) -> str:
        return f"{round(distance, cls._ROUND_DIGITS):.{cls._ROUND_DIGITS}f}"

    @staticmethod
    def _family_label(order: int, total: int) -> str:
        if order == 0:
            return "Edge Network"
        if total > 1 and order == total - 1:
            return "Opposition"
        return f"Chord {order}"

    @staticmethod
    def _segment_list(
        pair_map: Dict[Tuple[int, int], str],
        bucket_key: str,
    ) -> List[Tuple[int, int]]:
        seen: Dict[Tuple[int, int], None] = {}
        for (start, end), bucket in pair_map.items():
            if bucket != bucket_key:
                continue
            ordered = (min(start, end), max(start, end))
            seen[ordered] = None
        return list(seen.keys())

    @staticmethod
    def _summarize(transitions: Sequence[SolidTransition3D]) -> Dict[str, object]:
        if not transitions:
            return {
                "count": 0,
                "sum_result": 0,
                "mean_result": 0.0,
                "min_result": 0,
                "max_result": 0,
                "unique_results": 0,
            }
        values = [transition.result_decimal for transition in transitions]
        total = sum(values)
        return {
            "count": len(values),
            "sum_result": total,
            "mean_result": total / len(values),
            "min_result": min(values),
            "max_result": max(values),
            "unique_results": len(set(values)),
        }

    @staticmethod
    def _build_transition(
        start: SolidVertex3D,
        end: SolidVertex3D,
        *,
        family_key: str,
        family_label: str,
        distance: float,
    ) -> SolidTransition3D:
        from_ternary = TernaryService.decimal_to_ternary(start.value)
        to_ternary = TernaryService.decimal_to_ternary(end.value)
        result_ternary = TernaryTransitionService.transition(from_ternary, to_ternary)
        result_decimal = TernaryService.ternary_to_decimal(result_ternary)
        return SolidTransition3D(
            family_key=family_key,
            family_label=family_label,
            distance=distance,
            from_index=start.index,
            to_index=end.index,
            from_value=start.value,
            to_value=end.value,
            from_ternary=from_ternary,
            to_ternary=to_ternary,
            result_ternary=result_ternary,
            result_decimal=result_decimal,
        )


__all__ = [
    "PlatonicTransitionService",
    "PlatonicSolidGeometry",
    "SolidFamilyGroup",
    "SolidTransition3D",
    "SolidVertex3D",
]