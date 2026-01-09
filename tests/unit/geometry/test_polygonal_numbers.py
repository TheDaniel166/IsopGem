import math
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pillars.geometry.services.polygonal_numbers import (
    polygonal_number_value,
    centered_polygonal_value,
    polygonal_number_points,
)


def test_polygonal_number_value_matches_point_count():
    cases = [
        (3, 3, 6),   # triangular
        (4, 3, 9),   # square
        (5, 2, 5),   # pentagonal
        (6, 4, 28),  # hexagonal
    ]
    for sides, index, expected in cases:
        assert polygonal_number_value(sides, index) == expected
        points = polygonal_number_points(sides, index)
        assert len(points) == expected


def test_centered_polygonal_value_matches_point_count():
    cases = [
        (3, 1, 1),   # centered triangular
        (3, 3, 10),  # centered triangular
        (4, 3, 13),  # centered square
        (5, 3, 16),  # centered pentagonal
    ]
    for sides, index, expected in cases:
        assert centered_polygonal_value(sides, index) == expected
        points = polygonal_number_points(sides, index, centered=True)
        assert len(points) == expected


def test_points_are_distributed_on_polygon_rings():
    sides = 6
    index = 4
    spacing = 1.25
    points = polygonal_number_points(sides, index, spacing=spacing)

    # Points should include origin and grow outward from a shared corner
    assert (0.0, 0.0) in {(round(x, 4), round(y, 4)) for x, y in points}

    # Points should not overlap when projected onto perimeter
    rounded = {(round(x, 4), round(y, 4)) for x, y in points}
    assert len(rounded) == len(points)

    # Extents should scale with index and spacing (corner-grown gnomon)
    max_extent = max(max(abs(x), abs(y)) for x, y in points)
    assert max_extent >= spacing * (index - 1)
