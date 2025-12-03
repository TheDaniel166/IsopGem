"""Services for geometric-based vertex transitions."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from .ternary_service import TernaryService
from .ternary_transition_service import TernaryTransitionService


@dataclass(frozen=True)
class Vertex:
    """Represents a vertex on a regular polygon."""

    index: int
    label: str
    value: int
    x: float
    y: float


@dataclass(frozen=True)
class Transition:
    """Represents a directed connection between two vertices."""

    skip: int
    from_index: int
    to_index: int
    from_value: int
    to_value: int
    from_ternary: str
    to_ternary: str
    result_ternary: str
    result_decimal: int


class GeometricTransitionService:
    """Generate transitions on regular polygons (3 to 27 sides)."""

    MIN_SIDES = 3
    MAX_SIDES = 27
    MAX_SKIP_GROUPS = 13  # skip 1 + 12 diagonal families
    SPECIAL_PATTERNS: Dict[int, List[Dict[str, object]]] = {
        7: [
            {
                "name": "Lovely Star",
                "description": "Unicursal heptagram formed by vertices 1-4-2-6-3-7-5-1",
                "edges": [
                    (0, 3),  # 1 -> 4
                    (3, 1),  # 4 -> 2
                    (1, 5),  # 2 -> 6
                    (5, 2),  # 6 -> 3
                    (2, 6),  # 3 -> 7
                    (6, 4),  # 7 -> 5
                    (4, 0),  # 5 -> 1
                ],
            },
            {
                "name": "Mountain Star",
                "description": "Alternate heptagram 1-4-6-2-7-3-5-1",
                "edges": [
                    (0, 3),  # 1 -> 4
                    (3, 5),  # 4 -> 6
                    (5, 1),  # 6 -> 2
                    (1, 6),  # 2 -> 7
                    (6, 2),  # 7 -> 3
                    (2, 4),  # 3 -> 5
                    (4, 0),  # 5 -> 1
                ],
            },
            {
                "name": "Atomic Star",
                "description": "Heptagram path 1-3-5-2-7-4-6-1",
                "edges": [
                    (0, 2),  # 1 -> 3
                    (2, 4),  # 3 -> 5
                    (4, 1),  # 5 -> 2
                    (1, 6),  # 2 -> 7
                    (6, 3),  # 7 -> 4
                    (3, 5),  # 4 -> 6
                    (5, 0),  # 6 -> 1
                ],
            },
        ]
    }

    @classmethod
    def get_polygon_options(cls) -> List[Dict[str, object]]:
        """Return supported polygon side counts for UI selectors."""
        return [
            {"sides": sides, "name": cls._polygon_name(sides)}
            for sides in range(cls.MIN_SIDES, cls.MAX_SIDES + 1)
        ]

    @classmethod
    def build_vertices(
        cls,
        sides: int,
        values: Optional[Sequence[int]] = None,
    ) -> List[Vertex]:
        """Construct ordered vertices with coordinates."""
        cls._validate_sides(sides)

        resolved_values = cls._normalize_values(sides, values)
        angle_step = (2 * math.pi) / sides
        radius = 1.0

        vertices: List[Vertex] = []
        for idx in range(sides):
            angle = math.pi / 2 - idx * angle_step  # start at top, go clockwise
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            label = str(idx + 1)
            vertices.append(
                Vertex(
                    index=idx,
                    label=label,
                    value=resolved_values[idx],
                    x=round(x, 6),
                    y=round(y, 6),
                )
            )
        return vertices

    @classmethod
    def generate_skip_groups(
        cls,
        vertices: Sequence[Vertex],
        max_skip: Optional[int] = None,
    ) -> List[Dict[str, object]]:
        """Return transition groups keyed by skip value."""
        sides = len(vertices)
        if sides < cls.MIN_SIDES:
            raise ValueError("At least three vertices required")

        max_skip_allowed = min(sides // 2, cls.MAX_SKIP_GROUPS)
        if max_skip is not None:
            if max_skip < 1:
                raise ValueError("max_skip must be positive when provided")
            max_skip_allowed = min(max_skip_allowed, max_skip)

        groups: List[Dict[str, object]] = []
        for skip in range(1, max_skip_allowed + 1):
            transitions = cls._build_transitions(vertices, skip)
            groups.append(
                {
                    "skip": skip,
                    "label": cls._group_label(skip),
                    "transitions": transitions,
                    "summary": cls._summarize(transitions),
                }
            )
        return groups

    @classmethod
    def generate_special_sequences(
        cls,
        vertices: Sequence[Vertex],
    ) -> List[Dict[str, object]]:
        """Return predefined transition sets for particular polygons."""
        sides = len(vertices)
        patterns = cls.SPECIAL_PATTERNS.get(sides, [])
        if not patterns:
            return []

        sequences: List[Dict[str, object]] = []
        for pattern in patterns:
            edges: List[Tuple[int, int]] = pattern.get("edges", [])  # type: ignore[arg-type]
            transitions = [
                cls._build_custom_transition(vertices, start, end)
                for start, end in edges
            ]
            sequences.append(
                {
                    "name": pattern.get("name", "Special Pattern"),
                    "description": pattern.get("description", ""),
                    "transitions": transitions,
                    "summary": cls._summarize(transitions),
                }
            )
        return sequences

    # -- internal helpers -------------------------------------------------

    @classmethod
    def _build_transitions(
        cls,
        vertices: Sequence[Vertex],
        skip: int,
    ) -> List[Transition]:
        sides = len(vertices)
        transitions: List[Transition] = []

        for idx, vertex in enumerate(vertices):
            target_idx = (idx + skip) % sides
            target = vertices[target_idx]

            from_ter = TernaryService.decimal_to_ternary(vertex.value)
            to_ter = TernaryService.decimal_to_ternary(target.value)
            result_ter = TernaryTransitionService.transition(from_ter, to_ter)
            result_dec = TernaryService.ternary_to_decimal(result_ter)
            transitions.append(
                Transition(
                    skip=skip,
                    from_index=vertex.index,
                    to_index=target.index,
                    from_value=vertex.value,
                    to_value=target.value,
                    from_ternary=from_ter,
                    to_ternary=to_ter,
                    result_ternary=result_ter,
                    result_decimal=result_dec,
                )
            )
        return transitions

    @classmethod
    def _build_custom_transition(
        cls,
        vertices: Sequence[Vertex],
        from_index: int,
        to_index: int,
    ) -> Transition:
        sides = len(vertices)
        if sides == 0:
            raise ValueError("No vertices provided")

        start = vertices[from_index % sides]
        end = vertices[to_index % sides]

        from_ter = TernaryService.decimal_to_ternary(start.value)
        to_ter = TernaryService.decimal_to_ternary(end.value)
        result_ter = TernaryTransitionService.transition(from_ter, to_ter)
        result_dec = TernaryService.ternary_to_decimal(result_ter)
        skip_value = (end.index - start.index) % sides

        return Transition(
            skip=skip_value,
            from_index=start.index,
            to_index=end.index,
            from_value=start.value,
            to_value=end.value,
            from_ternary=from_ter,
            to_ternary=to_ter,
            result_ternary=result_ter,
            result_decimal=result_dec,
        )

    @classmethod
    def _summarize(cls, transitions: Sequence[Transition]) -> Dict[str, object]:
        if not transitions:
            return {
                "count": 0,
                "sum_result": 0,
                "mean_result": 0,
                "min_result": 0,
                "max_result": 0,
                "unique_results": 0,
            }

        result_values = [t.result_decimal for t in transitions]
        count = len(result_values)
        return {
            "count": count,
            "sum_result": sum(result_values),
            "mean_result": sum(result_values) / count,
            "min_result": min(result_values),
            "max_result": max(result_values),
            "unique_results": len(set(result_values)),
        }

    @staticmethod
    def _group_label(skip: int) -> str:
        if skip == 1:
            return "Perimeter"
        return f"Diagonal (Skip {skip})"

    @classmethod
    def _normalize_values(
        cls,
        sides: int,
        values: Optional[Sequence[int]],
    ) -> List[int]:
        if values is None or len(values) == 0:
            return list(range(1, sides + 1))

        normalized = list(values[:sides])
        if len(normalized) < sides:
            normalized.extend(0 for _ in range(sides - len(normalized)))
        return normalized

    @classmethod
    def _validate_sides(cls, sides: int):
        if sides < cls.MIN_SIDES or sides > cls.MAX_SIDES:
            raise ValueError(
                f"Sides must be between {cls.MIN_SIDES} and {cls.MAX_SIDES}"
            )

    @staticmethod
    def _polygon_name(sides: int) -> str:
        if sides == 3:
            return "Triangle"
        if sides == 4:
            return "Square"
        if sides == 5:
            return "Pentagon"
        if sides == 6:
            return "Hexagon"
        if sides == 7:
            return "Heptagon"
        if sides == 8:
            return "Octagon"
        if sides == 9:
            return "Nonagon"
        if sides == 10:
            return "Decagon"
        if sides == 11:
            return "Hendecagon"
        if sides == 12:
            return "Dodecagon"
        return f"{sides}-gon"
