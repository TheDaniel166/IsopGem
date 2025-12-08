"""Geometry pillar hub - launcher interface for geometry tools."""
from __future__ import annotations

from typing import Callable, List, Optional, Dict, Any, cast

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSpinBox, QScrollArea, QLayout, QInputDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from shared.ui import WindowManager
from .advanced_scientific_calculator_window import AdvancedScientificCalculatorWindow
from .geometry_calculator_window import GeometryCalculatorWindow
from .polygonal_number_window import PolygonalNumberWindow
from .experimental_star_window import ExperimentalStarWindow
from .figurate_3d_window import Figurate3DWindow
from ..services import (
    AnnulusShape,
    CircleShape,
    CrescentShape,
    EllipseShape,
    RoseCurveShape,
    SquareShape,
    RectangleShape,
    ParallelogramShape,
    RhombusShape,
    TrapezoidShape,
    IsoscelesTrapezoidShape,
    KiteShape,
    DeltoidShape,
    EquilateralTriangleShape,
    RightTriangleShape,
    IsoscelesTriangleShape,
    ScaleneTriangleShape,
    AcuteTriangleShape,
    ObtuseTriangleShape,
    HeronianTriangleShape,
    IsoscelesRightTriangleShape,
    ThirtySixtyNinetyTriangleShape,
    GoldenTriangleShape,
    TriangleSolverShape,
    CyclicQuadrilateralShape,
    TangentialQuadrilateralShape,
    BicentricQuadrilateralShape,
    QuadrilateralSolverShape,
    RegularPolygonShape,
    VesicaPiscisShape,
    TetrahedronSolidService,
    TetrahedronSolidCalculator,
    CubeSolidService,
    CubeSolidCalculator,
    OctahedronSolidService,
    OctahedronSolidCalculator,
    DodecahedronSolidService,
    DodecahedronSolidCalculator,
    IcosahedronSolidService,
    IcosahedronSolidCalculator,
    TesseractSolidService,
    TesseractSolidCalculator,
    SquarePyramidSolidService,
    SquarePyramidSolidCalculator,
    SquarePyramidFrustumSolidService,
    SquarePyramidFrustumSolidCalculator,
    PentagonalPyramidFrustumSolidService,
    PentagonalPyramidFrustumSolidCalculator,
    HexagonalPyramidFrustumSolidService,
    HexagonalPyramidFrustumSolidCalculator,
    RectangularPyramidSolidService,
    RectangularPyramidSolidCalculator,
    TriangularPyramidSolidService,
    TriangularPyramidSolidCalculator,
    PentagonalPyramidSolidService,
    PentagonalPyramidSolidCalculator,
    HexagonalPyramidSolidService,
    HexagonalPyramidSolidCalculator,
    HeptagonalPyramidSolidService,
    HeptagonalPyramidSolidCalculator,
    GoldenPyramidSolidService,
    GoldenPyramidSolidCalculator,
    StepPyramidSolidService,
    StepPyramidSolidCalculator,
    RectangularPrismSolidService,
    RectangularPrismSolidCalculator,
    TriangularPrismSolidService,
    TriangularPrismSolidCalculator,
    PentagonalPrismSolidService,
    PentagonalPrismSolidCalculator,
    HexagonalPrismSolidService,
    HexagonalPrismSolidCalculator,
    OctagonalPrismSolidService,
    OctagonalPrismSolidCalculator,
    HeptagonalPrismSolidService,
    HeptagonalPrismSolidCalculator,
    ObliquePrismSolidService,
    ObliquePrismSolidCalculator,
    PrismaticFrustumSolidService,
    PrismaticFrustumSolidCalculator,
    TriangularAntiprismSolidService,
    TriangularAntiprismSolidCalculator,
    SquareAntiprismSolidService,
    SquareAntiprismSolidCalculator,
    PentagonalAntiprismSolidService,
    PentagonalAntiprismSolidCalculator,
    HexagonalAntiprismSolidService,
    HexagonalAntiprismSolidCalculator,
    OctagonalAntiprismSolidService,
    OctagonalAntiprismSolidCalculator,
    HeptagonalAntiprismSolidService,
    HeptagonalAntiprismSolidCalculator,
    CuboctahedronSolidService,
    CuboctahedronSolidCalculator,
    TruncatedTetrahedronSolidService,
    TruncatedTetrahedronSolidCalculator,
    TruncatedCubeSolidService,
    TruncatedCubeSolidCalculator,
    TruncatedOctahedronSolidService,
    TruncatedOctahedronSolidCalculator,
    RhombicuboctahedronSolidService,
    RhombicuboctahedronSolidCalculator,
    RhombicosidodecahedronSolidService,
    RhombicosidodecahedronSolidCalculator,
    TruncatedCuboctahedronSolidService,
    TruncatedCuboctahedronSolidCalculator,
    IcosidodecahedronSolidService,
    IcosidodecahedronSolidCalculator,
    TruncatedDodecahedronSolidService,
    TruncatedDodecahedronSolidCalculator,
    TruncatedIcosahedronSolidService,
    TruncatedIcosahedronSolidCalculator,
    TruncatedIcosidodecahedronSolidService,
    TruncatedIcosidodecahedronSolidCalculator,
    SnubCubeSolidService,
    SnubCubeSolidCalculator,
    SnubDodecahedronSolidService,
    SnubDodecahedronSolidCalculator,
)
from .geometry3d.window3d import Geometry3DWindow


def _category(name: str, icon: str, tagline: str, shapes: List[dict], menu: Optional[List[Any]] = None) -> dict:
    return {
        'name': name,
        'icon': icon,
        'tagline': tagline,
        'shapes': shapes,
        'menu': menu,
    }


CATEGORY_DEFINITIONS: List[dict] = [
    _category(
        name="Circles",
        icon="◯",
        tagline="Curves, arcs, and ellipses",
        shapes=[
            {
                'name': 'Circle',
                'summary': 'Radius, diameter, circumference, area',
                'factory': CircleShape,
            },
            {
                'name': 'Oval (Ellipse)',
                'summary': 'Semi-major/minor axes, eccentricity, Ramanujan perimeter',
                'factory': EllipseShape,
            },
            {
                'name': 'Annulus',
                'summary': 'Ring width, concentric circumferences, area delta',
                'factory': AnnulusShape,
            },
            {
                'name': 'Crescent',
                'summary': 'Lune carved by offset inner circle with overlap metrics',
                'factory': CrescentShape,
            },
            {
                'name': 'Vesica Piscis',
                'summary': 'Sacred lens of two equal circles with arc + area data',
                'factory': VesicaPiscisShape,
            },
            {
                'name': 'Rose (Rhodonea Curve)',
                'summary': 'Amplitude and harmonic-driven petal curves',
                'factory': RoseCurveShape,
            },
        ],
    ),
    _category(
        name="Triangles",
        icon="△",
        tagline="Classical sacred triples",
        shapes=[
            {
                'name': 'Equilateral Triangle',
                'summary': 'Side, height, area, radii',
                'factory': EquilateralTriangleShape,
            },
            {
                'name': 'Right Triangle',
                'summary': 'Base, height, hypotenuse, area',
                'factory': RightTriangleShape,
            },
            {
                'name': 'Isosceles Triangle',
                'summary': 'Equal legs from base + height inputs with area/perimeter',
                'factory': IsoscelesTriangleShape,
            },
            {
                'name': 'Scalene Triangle',
                'summary': 'Three unequal sides with SSS validation, altitudes, radii',
                'factory': ScaleneTriangleShape,
            },
            {
                'name': 'Acute Triangle',
                'summary': 'All interior angles < 90° with altitude breakdowns',
                'factory': AcuteTriangleShape,
            },
            {
                'name': 'Obtuse Triangle',
                'summary': 'Detects >90° angle scenarios with exterior altitude tracing',
                'factory': ObtuseTriangleShape,
            },
            {
                'name': 'Isosceles Right Triangle (45-45-90)',
                'summary': '45-45-90 triangle with √2 leg relationships & radii',
                'factory': IsoscelesRightTriangleShape,
            },
            {
                'name': '30-60-90 Triangle',
                'summary': 'Half-equilateral proportions with √3 ratios and heights',
                'factory': ThirtySixtyNinetyTriangleShape,
            },
            {
                'name': 'Golden Triangle',
                'summary': 'Isosceles phi-based triangle with derived short side + area',
                'factory': GoldenTriangleShape,
            },
            {
                'name': 'Heronian Triangle',
                'summary': 'Integer side + area validation using Heron’s formula',
                'factory': HeronianTriangleShape,
            },
            {
                'name': 'Triangle Solver (any sides/angles)',
                'summary': 'General SAS/ASA/SSA/SSS solver with visualization',
                'factory': TriangleSolverShape,
            },
        ],
    ),
    _category(
        name="Quadrilaterals",
        icon="▭",
        tagline="Squares, rectangles, and beyond",
        shapes=[
            {
                'name': 'Square',
                'summary': 'Side, perimeter, area, diagonal',
                'factory': SquareShape,
            },
            {
                'name': 'Rectangle',
                'summary': 'Length, width, perimeter, diagonal',
                'factory': RectangleShape,
            },
            {
                'name': 'Parallelogram',
                'summary': 'Opposite sides parallel with angle, height, and diagonal data',
                'factory': ParallelogramShape,
            },
            {
                'name': 'Rhombus',
                'summary': 'Equal sides with diagonal, area, and height solvers',
                'factory': RhombusShape,
            },
            {
                'name': 'Trapezoid',
                'summary': 'General trapezoid with base, leg, and altitude validation',
                'factory': TrapezoidShape,
            },
            {
                'name': 'Isosceles Trapezoid',
                'summary': 'Symmetric trapezoid with equal legs and diagonal readouts',
                'factory': IsoscelesTrapezoidShape,
            },
            {
                'name': 'Kite',
                'summary': 'Adjacent equal sides with diagonal + area from side-angle inputs',
                'factory': KiteShape,
            },
            {
                'name': 'Deltoid / Dart',
                'summary': 'Concave kite (dart) variant using reflex angles',
                'factory': DeltoidShape,
            },
            {
                'name': 'Cyclic Quadrilateral',
                'summary': 'All vertices on a circle with Brahmagupta area and R',
                'factory': CyclicQuadrilateralShape,
            },
            {
                'name': 'Tangential Quadrilateral',
                'summary': 'Incircle touches every side with Pitot + inradius checks',
                'factory': TangentialQuadrilateralShape,
            },
            {
                'name': 'Bicentric Quadrilateral',
                'summary': 'Simultaneously cyclic and tangential (incircle + circumcircle)',
                'factory': BicentricQuadrilateralShape,
            },
            {
                'name': 'General Quadrilateral Solver',
                'summary': 'Mix sides with diagonal lengths + included diagonal angle',
                'factory': QuadrilateralSolverShape,
            },
        ],
    ),
    _category(
        name="Polygons",
        icon="⬢",
        tagline="Regular and star polygons",
        shapes=[
            {
                'name': 'Regular Pentagon (5-gon)',
                'summary': 'Equal sides and angles – sacred pentagonal ratios',
                'polygon_sides': 5,
            },
            {
                'name': 'Regular Hexagon (6-gon)',
                'summary': 'Hexagonal lattices, honeycomb symmetries',
                'polygon_sides': 6,
            },
            {
                'name': 'Regular Heptagon (7-gon)',
                'summary': 'Septenary geometry studies',
                'polygon_sides': 7,
            },
            {
                'name': 'Regular Octagon (8-gon)',
                'summary': 'Stop-sign symmetry, eastern mandalas',
                'polygon_sides': 8,
            },
            {
                'name': 'Regular Nonagon (9-gon)',
                'summary': 'Ninefold geometry explorations',
                'polygon_sides': 9,
            },
            {
                'name': 'Regular Decagon (10-gon)',
                'summary': 'Golden ratio relationships in tenfold form',
                'polygon_sides': 10,
            },
            {
                'name': 'Regular Hendecagon (11-gon)',
                'summary': 'Rarer elevenfold rotational symmetry',
                'polygon_sides': 11,
            },
            {
                'name': 'Regular Dodecagon (12-gon)',
                'summary': 'Twelvefold cycles and sacred geometry',
                'polygon_sides': 12,
            },
            {
                'name': 'Any Regular n-gon',
                'summary': 'Choose any number of sides ≥ 3',
                'type': 'regular_polygon_custom',
            },
        ],
    ),
    _category(
        name="Pyramids",
        icon="⌂",
        tagline="Tapered solids rising from sacred bases",
        shapes=[
            {
                'name': 'Square Pyramid',
                'summary': 'Base edge, slant height, apothem, volume',
                'type': 'solid_viewer',
                'solid_id': 'square_pyramid',
            },
            {
                'name': 'Rectangular Pyramid',
                'summary': 'Independent base edges with dual slant heights and volume',
                'type': 'solid_viewer',
                'solid_id': 'rectangular_pyramid',
            },
            {
                'name': 'Equilateral Triangular Pyramid (Tetrahedral)',
                'summary': 'Equilateral base with adjustable apex height, slant, and volume',
                'type': 'solid_viewer',
                'solid_id': 'triangular_pyramid',
            },
            {
                'name': 'Regular Pentagonal Pyramid',
                'summary': 'Fivefold symmetry with apothem, slant, and lateral metrics',
                'type': 'solid_viewer',
                'solid_id': 'pentagonal_pyramid',
            },
            {
                'name': 'Regular Hexagonal Pyramid',
                'summary': 'Honeycomb-style base with live perimeter and volume solving',
                'type': 'solid_viewer',
                'solid_id': 'hexagonal_pyramid',
            },
            {
                'name': 'Regular Heptagonal Pyramid',
                'summary': 'Sevenfold base showcasing rare apothem and slant couplings',
                'type': 'solid_viewer',
                'solid_id': 'heptagonal_pyramid',
            },
            {
                'name': 'Oblique Pyramid',
                'summary': 'Coming soon: apex offset with lateral face resolution',
                'status': 'Coming Soon',
                'factory': None,
            },
            {
                'name': 'Square Pyramid Frustum',
                'summary': 'Dual-base truncated square pyramid with coupled slant metrics',
                'type': 'solid_viewer',
                'solid_id': 'square_pyramid_frustum',
            },
            {
                'name': 'Pentagonal Pyramid Frustum',
                'summary': 'Fivefold truncated pyramid with dual perimeter + slant metrics',
                'type': 'solid_viewer',
                'solid_id': 'pentagonal_pyramid_frustum',
            },
            {
                'name': 'Hexagonal Pyramid Frustum',
                'summary': 'Honeycomb-based truncated pyramid with apothem-driven slant control',
                'type': 'solid_viewer',
                'solid_id': 'hexagonal_pyramid_frustum',
            },
            {
                'name': 'Golden Pyramid',
                'summary': 'Great Pyramid inspired φ-ratio pyramid with derived slant + height',
                'type': 'solid_viewer',
                'solid_id': 'golden_pyramid',
            },
            {
                'name': 'Step Pyramid',
                'summary': 'Tiered mastaba stack with adjustable steps and cumulative metrics',
                'type': 'solid_viewer',
                'solid_id': 'step_pyramid',
            },
            {
                'name': 'General n-gonal Pyramid Solver',
                'summary': 'Coming soon: arbitrary base polygon with apex control',
                'status': 'Coming Soon',
                'factory': None,
            },
        ],
        menu=[
            {
                'label': 'Right Regular Pyramids',
                'items': [
                    'Square Pyramid',
                    'Rectangular Pyramid',
                    'Equilateral Triangular Pyramid (Tetrahedral)',
                    'Regular Pentagonal Pyramid',
                    'Regular Hexagonal Pyramid',
                    'Regular Heptagonal Pyramid',
                ],
            },
            {
                'label': 'Oblique & Frustums',
                'items': [
                    'Oblique Pyramid',
                    'Square Pyramid Frustum',
                    'Pentagonal Pyramid Frustum',
                    'Hexagonal Pyramid Frustum',
                ],
            },
            {
                'label': 'Sacred & General Tools',
                'items': [
                    'Golden Pyramid',
                    'Step Pyramid',
                    'General n-gonal Pyramid Solver',
                ],
            },
        ],
    ),
    _category(
        name="Prisms",
        icon="▱",
        tagline="Uniform cross-section solids",
        shapes=[
            {
                'name': 'Triangular Prism',
                'summary': 'Equilateral base prism with apothem, lateral area, and volume solving.',
                'type': 'solid_viewer',
                'solid_id': 'triangular_prism',
            },
            {
                'name': 'Rectangular Prism',
                'summary': 'Independent length × width × height box with diagonal readouts.',
                'type': 'solid_viewer',
                'solid_id': 'rectangular_prism',
            },
            {
                'name': 'Pentagonal Prism',
                'summary': 'Fivefold regular prism showing perimeter, apothem, and volume coupling.',
                'type': 'solid_viewer',
                'solid_id': 'pentagonal_prism',
            },
            {
                'name': 'Hexagonal Prism',
                'summary': 'Honeycomb regular prism with live lateral/surface area metrics.',
                'type': 'solid_viewer',
                'solid_id': 'hexagonal_prism',
            },
            {
                'name': 'Heptagonal Prism',
                'summary': 'Sevenfold base prism showcasing rare perimeter/apothem couplings.',
                'type': 'solid_viewer',
                'solid_id': 'heptagonal_prism',
            },
            {
                'name': 'Octagonal Prism',
                'summary': 'Stop-sign base prism featuring radius, apothem, and face analytics.',
                'type': 'solid_viewer',
                'solid_id': 'octagonal_prism',
            },
            {
                'name': 'Oblique Prism',
                'summary': 'Skewed regular prism with editable lateral offset.',
                'type': 'solid_viewer',
                'solid_id': 'oblique_prism',
            },
            {
                'name': 'Prismatic Frustum',
                'summary': 'Regular prism truncated between dual polygon bases.',
                'type': 'solid_viewer',
                'solid_id': 'prismatic_frustum',
            },
            {
                'name': 'Gyroelongated Square Prism',
                'summary': 'Coming soon: Johnson solid combo of prisms and antiprisms',
                'status': 'Coming Soon',
                'factory': None,
            },
            {
                'name': 'General n-gonal Prism Solver',
                'summary': 'Coming soon: configurable base polygon with extrusion height',
                'status': 'Coming Soon',
                'factory': None,
            },
            {
                'name': 'Prism Net Explorer',
                'summary': 'Coming soon: unfoldable nets and face adjacency maps',
                'status': 'Coming Soon',
                'factory': None,
            },
        ],
        menu=[
            {
                'label': 'Right Prisms',
                'items': [
                    'Triangular Prism',
                    'Rectangular Prism',
                    'Pentagonal Prism',
                    'Hexagonal Prism',
                    'Heptagonal Prism',
                    'Octagonal Prism',
                ],
            },
            {
                'label': 'Oblique & Truncated Forms',
                'items': [
                    'Oblique Prism',
                    'Prismatic Frustum',
                    'Gyroelongated Square Prism',
                ],
            },
            {
                'label': 'Explorers & Solvers',
                'items': [
                    'General n-gonal Prism Solver',
                    'Prism Net Explorer',
                ],
            },
        ],
    ),
    _category(
        name="Antiprisms",
        icon="⧖",
        tagline="Twisted twin-base solids",
        shapes=[
            {
                'name': 'Triangular Antiprism',
                'summary': 'Dual rotated triangles joined by equilateral lateral faces.',
                'type': 'solid_viewer',
                'solid_id': 'triangular_antiprism',
            },
            {
                'name': 'Square Antiprism',
                'summary': 'Square bases rotated 45° with eight congruent triangles.',
                'type': 'solid_viewer',
                'solid_id': 'square_antiprism',
            },
            {
                'name': 'Pentagonal Antiprism',
                'summary': 'Decagonal waist linking rotated pentagons with ten faces.',
                'type': 'solid_viewer',
                'solid_id': 'pentagonal_antiprism',
            },
            {
                'name': 'Hexagonal Antiprism',
                'summary': 'Staggered honeycomb pair producing twelve lateral triangles.',
                'type': 'solid_viewer',
                'solid_id': 'hexagonal_antiprism',
            },
            {
                'name': 'Heptagonal Antiprism',
                'summary': 'Sevenfold antiprism with fourteen lateral equilateral faces.',
                'type': 'solid_viewer',
                'solid_id': 'heptagonal_antiprism',
            },
            {
                'name': 'Octagonal Antiprism',
                'summary': 'Sixteen-triangle belt between rotated octagons.',
                'type': 'solid_viewer',
                'solid_id': 'octagonal_antiprism',
            },
            {
                'name': 'Snub Antiprism',
                'summary': 'Coming soon: chiral extension with alternating twists',
                'status': 'Coming Soon',
                'factory': None,
            },
            {
                'name': 'Twisted Icosahedral Antiprism',
                'summary': 'Coming soon: high-order antiprism approaching icosahedron',
                'status': 'Coming Soon',
                'factory': None,
            },
            {
                'name': 'General n-gonal Antiprism Solver',
                'summary': 'Coming soon: configure any base polygon and twist angle',
                'status': 'Coming Soon',
                'factory': None,
            },
            {
                'name': 'Antiprism Net Explorer',
                'summary': 'Coming soon: unfolding studies for twisted solids',
                'status': 'Coming Soon',
                'factory': None,
            },
        ],
        menu=[
            {
                'label': 'Standard Antiprisms',
                'items': [
                    'Triangular Antiprism',
                    'Square Antiprism',
                    'Pentagonal Antiprism',
                    'Hexagonal Antiprism',
                    'Heptagonal Antiprism',
                    'Octagonal Antiprism',
                ],
            },
            {
                'label': 'Advanced & Chiral',
                'items': [
                    'Snub Antiprism',
                    'Twisted Icosahedral Antiprism',
                ],
            },
            {
                'label': 'Tools & Explorers',
                'items': [
                    'General n-gonal Antiprism Solver',
                    'Antiprism Net Explorer',
                ],
            },
        ],
    ),
    _category(
        name="Platonic Solids",
        icon="◆",
        tagline="Perfect 3D symmetry",
        shapes=[
            {
                'name': 'Tetrahedron',
                'summary': 'Edge, height, area, volume',
                'type': 'solid_viewer',
                'solid_id': 'tetrahedron',
            },
            {
                'name': 'Cube',
                'summary': 'Edge, diagonals, volume',
                'type': 'solid_viewer',
                'solid_id': 'cube',
            },
            {
                'name': 'Octahedron',
                'summary': 'Dual of cube with triangular faces',
                'type': 'solid_viewer',
                'solid_id': 'octahedron',
            },
            {
                'name': 'Dodecahedron',
                'summary': 'Sacred pentagonal faces',
                'type': 'solid_viewer',
                'solid_id': 'dodecahedron',
            },
            {
                'name': 'Icosahedron',
                'summary': 'Twenty equilateral faces and golden ratios',
                'type': 'solid_viewer',
                'solid_id': 'icosahedron',
            },
        ],
    ),
    _category(
        name="Archimedean Solids",
        icon="◇",
        tagline="Truncated and blended forms",
        shapes=[
            {
                'name': 'Truncated Tetrahedron',
                'summary': 'Regular tetra unfolded into 4 triangles + 4 hexagons.',
                'type': 'solid_viewer',
                'solid_id': 'truncated_tetrahedron',
            },
            {
                'name': 'Cuboctahedron',
                'summary': 'Eight triangles and six squares sharing uniform edges.',
                'type': 'solid_viewer',
                'solid_id': 'cuboctahedron',
            },
            {
                'name': 'Truncated Cube',
                'summary': 'Octagon-square composition generated by trimming cube corners.',
                'type': 'solid_viewer',
                'solid_id': 'truncated_cube',
            },
            {
                'name': 'Truncated Octahedron',
                'summary': 'Space-filling solid blending hexagons with squares.',
                'type': 'solid_viewer',
                'solid_id': 'truncated_octahedron',
            },
            {
                'name': 'Rhombicuboctahedron',
                'summary': 'Uniform mix of 18 squares and 8 triangles with full symmetry.',
                'type': 'solid_viewer',
                'solid_id': 'rhombicuboctahedron',
            },
            {
                'name': 'Truncated Cuboctahedron',
                'summary': 'Great rhombicuboctahedron weaving hexagons, squares, and octagons.',
                'type': 'solid_viewer',
                'solid_id': 'truncated_cuboctahedron',
            },
            {
                'name': 'Snub Cube',
                'summary': 'Chiral solid pairing squares with equilateral triangles.',
                'type': 'solid_viewer',
                'solid_id': 'snub_cube',
            },
            {
                'name': 'Icosidodecahedron',
                'summary': 'Alternating pentagon-triangle faces bridging icosahedron and dodecahedron.',
                'type': 'solid_viewer',
                'solid_id': 'icosidodecahedron',
            },
            {
                'name': 'Truncated Dodecahedron',
                'summary': 'Decagon-triangle mixture carved from a dodecahedron.',
                'type': 'solid_viewer',
                'solid_id': 'truncated_dodecahedron',
            },
            {
                'name': 'Truncated Icosahedron',
                'summary': 'Classic soccer-ball blend of pentagons and hexagons.',
                'type': 'solid_viewer',
                'solid_id': 'truncated_icosahedron',
            },
            {
                'name': 'Rhombicosidodecahedron',
                'summary': 'Uniform solid with 20 triangles, 30 squares, and 12 pentagons.',
                'type': 'solid_viewer',
                'solid_id': 'rhombicosidodecahedron',
            },
            {
                'name': 'Truncated Icosidodecahedron',
                'summary': 'Great rhombicosidodecahedron combining pentagons, decagons, and squares.',
                'type': 'solid_viewer',
                'solid_id': 'truncated_icosidodecahedron',
            },
            {
                'name': 'Snub Dodecahedron',
                'summary': 'Chiral pentagon-triangle solid completing the Archimedean family.',
                'type': 'solid_viewer',
                'solid_id': 'snub_dodecahedron',
            },
        ],
    ),
    _category(
        name="Other Solids",
        icon="⚪",
        tagline="Cylinders, cones, and torus forms",
        shapes=[
            {
                'name': 'Sphere',
                'summary': 'Coming soon: radius, area, volume',
                'status': 'Coming Soon',
                'factory': None,
            },
            {
                'name': 'Cylinder',
                'summary': 'Coming soon: radius, height, lateral area',
                'status': 'Coming Soon',
                'factory': None,
            },
            {
                'name': 'Cone',
                'summary': 'Coming soon: slant height, volume',
                'status': 'Coming Soon',
                'factory': None,
            },
        ],
    ),
    _category(
        name="Hypercube",
        icon="⧈",
        tagline="Dimensional expansions and projections",
        shapes=[
            {
                'name': 'Tesseract',
                'summary': 'Dual-cube Schlegel projection with 24 square faces.',
                'type': 'solid_viewer',
                'solid_id': 'tesseract',
            },
        ],
    ),
]

SOLID_VIEWER_CONFIG: Dict[str, dict] = {
    'tetrahedron': {
        'title': 'Tetrahedron',
        'summary': 'Edge-equal platonic solid with 4 faces, 6 edges, and 4 vertices.',
        'builder': TetrahedronSolidService.build,
        'calculator': TetrahedronSolidCalculator,
    },
    'cube': {
        'title': 'Cube',
        'summary': 'Six perfect squares with equal edges, diagonals, and orthogonal faces.',
        'builder': CubeSolidService.build,
        'calculator': CubeSolidCalculator,
    },
    'octahedron': {
        'title': 'Octahedron',
        'summary': 'Dual of the cube featuring eight equilateral triangles and axial symmetry.',
        'builder': OctahedronSolidService.build,
        'calculator': OctahedronSolidCalculator,
    },
    'dodecahedron': {
        'title': 'Dodecahedron',
        'summary': 'Twelve sacred pentagons with golden-ratio symmetry and rich radii.',
        'builder': DodecahedronSolidService.build,
        'calculator': DodecahedronSolidCalculator,
    },
    'icosahedron': {
        'title': 'Icosahedron',
        'summary': 'Twenty equilateral faces yielding maximal symmetry among platonic solids.',
        'builder': IcosahedronSolidService.build,
        'calculator': IcosahedronSolidCalculator,
    },
    'tesseract': {
        'title': 'Tesseract (Hypercube)',
        'summary': 'Schlegel projection of a four-dimensional cube with paired shells.',
        'builder': TesseractSolidService.build,
        'calculator': TesseractSolidCalculator,
    },
    'square_pyramid': {
        'title': 'Square Pyramid',
        'summary': 'Right square pyramid with interactive base + height driven metric coupling.',
        'builder': SquarePyramidSolidService.build,
        'calculator': SquarePyramidSolidCalculator,
    },
    'rectangular_pyramid': {
        'title': 'Rectangular Pyramid',
        'summary': 'Unequal base edges with dual slant heights and apex-controlled volume.',
        'builder': RectangularPyramidSolidService.build,
        'calculator': RectangularPyramidSolidCalculator,
    },
    'triangular_pyramid': {
        'title': 'Equilateral Triangular Pyramid',
        'summary': 'Regular triangle base with editable height, apothem, and slant relations.',
        'builder': TriangularPyramidSolidService.build,
        'calculator': TriangularPyramidSolidCalculator,
    },
    'pentagonal_pyramid': {
        'title': 'Regular Pentagonal Pyramid',
        'summary': 'Fivefold base pyramid highlighting apothem, lateral, and perimeter data.',
        'builder': PentagonalPyramidSolidService.build,
        'calculator': PentagonalPyramidSolidCalculator,
    },
    'hexagonal_pyramid': {
        'title': 'Regular Hexagonal Pyramid',
        'summary': 'Sixfold honeycomb base with full metric solving and 3D payload.',
        'builder': HexagonalPyramidSolidService.build,
        'calculator': HexagonalPyramidSolidCalculator,
    },
    'heptagonal_pyramid': {
        'title': 'Regular Heptagonal Pyramid',
        'summary': 'Sevenfold symmetry drive with detailed apothem, slant, and volume outputs.',
        'builder': HeptagonalPyramidSolidService.build,
        'calculator': HeptagonalPyramidSolidCalculator,
    },
    'square_pyramid_frustum': {
        'title': 'Square Pyramid Frustum',
        'summary': 'Truncated square pyramid with editable dual bases and slant-coupled metrics.',
        'builder': SquarePyramidFrustumSolidService.build,
        'calculator': SquarePyramidFrustumSolidCalculator,
    },
    'pentagonal_pyramid_frustum': {
        'title': 'Pentagonal Pyramid Frustum',
        'summary': 'Fivefold truncated pyramid with apothem-aware slant + volume solving.',
        'builder': PentagonalPyramidFrustumSolidService.build,
        'calculator': PentagonalPyramidFrustumSolidCalculator,
    },
    'hexagonal_pyramid_frustum': {
        'title': 'Hexagonal Pyramid Frustum',
        'summary': 'Sixfold honeycomb frustum with dual perimeters and metric coupling.',
        'builder': HexagonalPyramidFrustumSolidService.build,
        'calculator': HexagonalPyramidFrustumSolidCalculator,
    },
    'golden_pyramid': {
        'title': 'Golden Pyramid',
        'summary': 'Great Pyramid style square pyramid enforcing φ-based slant/height links.',
        'builder': GoldenPyramidSolidService.build,
        'calculator': GoldenPyramidSolidCalculator,
    },
    'step_pyramid': {
        'title': 'Step Pyramid',
        'summary': 'Adjustable terraced mastaba stack with tier-aware metrics.',
        'builder': StepPyramidSolidService.build,
        'calculator': StepPyramidSolidCalculator,
    },
    'rectangular_prism': {
        'title': 'Rectangular Prism',
        'summary': 'Axis-aligned box with independent length, width, height, and diagonal metrics.',
        'builder': RectangularPrismSolidService.build,
        'calculator': RectangularPrismSolidCalculator,
    },
    'triangular_prism': {
        'title': 'Triangular Prism',
        'summary': 'Equilateral base right prism featuring apothem, lateral area, and volume coupling.',
        'builder': TriangularPrismSolidService.build,
        'calculator': TriangularPrismSolidCalculator,
    },
    'pentagonal_prism': {
        'title': 'Pentagonal Prism',
        'summary': 'Fivefold regular prism with perimeter/apothem metrics and expansive surface data.',
        'builder': PentagonalPrismSolidService.build,
        'calculator': PentagonalPrismSolidCalculator,
    },
    'hexagonal_prism': {
        'title': 'Hexagonal Prism',
        'summary': 'Honeycomb-style regular prism highlighting lateral area and volume relationships.',
        'builder': HexagonalPrismSolidService.build,
        'calculator': HexagonalPrismSolidCalculator,
    },
    'heptagonal_prism': {
        'title': 'Heptagonal Prism',
        'summary': 'Sevenfold regular prism emphasizing perimeter/apothem coupling and volume.',
        'builder': HeptagonalPrismSolidService.build,
        'calculator': HeptagonalPrismSolidCalculator,
    },
    'octagonal_prism': {
        'title': 'Octagonal Prism',
        'summary': 'Stop-sign base prism with extended perimeter, apothem, and surface analytics.',
        'builder': OctagonalPrismSolidService.build,
        'calculator': OctagonalPrismSolidCalculator,
    },
    'oblique_prism': {
        'title': 'Oblique Prism',
        'summary': 'Regular prism sheared by a horizontal offset with edge and skew metrics.',
        'builder': ObliquePrismSolidService.build,
        'calculator': ObliquePrismSolidCalculator,
    },
    'prismatic_frustum': {
        'title': 'Prismatic Frustum',
        'summary': 'Truncated regular prism bridging distinct polygon edges with linear taper.',
        'builder': PrismaticFrustumSolidService.build,
        'calculator': PrismaticFrustumSolidCalculator,
    },
    'triangular_antiprism': {
        'title': 'Triangular Antiprism',
        'summary': 'Dual equilateral triangles rotated 60° and joined by six faces.',
        'builder': TriangularAntiprismSolidService.build,
        'calculator': TriangularAntiprismSolidCalculator,
    },
    'square_antiprism': {
        'title': 'Square Antiprism',
        'summary': 'Forty-five degree rotated squares creating an eight-triangle belt.',
        'builder': SquareAntiprismSolidService.build,
        'calculator': SquareAntiprismSolidCalculator,
    },
    'pentagonal_antiprism': {
        'title': 'Pentagonal Antiprism',
        'summary': 'Rotated pentagons producing a decagonal midsection with ten faces.',
        'builder': PentagonalAntiprismSolidService.build,
        'calculator': PentagonalAntiprismSolidCalculator,
    },
    'hexagonal_antiprism': {
        'title': 'Hexagonal Antiprism',
        'summary': 'Honeycomb antiprism featuring twelve lateral equilateral triangles.',
        'builder': HexagonalAntiprismSolidService.build,
        'calculator': HexagonalAntiprismSolidCalculator,
    },
    'octagonal_antiprism': {
        'title': 'Octagonal Antiprism',
        'summary': 'Stop-sign antiprism with sixteen congruent triangle faces.',
        'builder': OctagonalAntiprismSolidService.build,
        'calculator': OctagonalAntiprismSolidCalculator,
    },
    'heptagonal_antiprism': {
        'title': 'Heptagonal Antiprism',
        'summary': 'Sevenfold antiprism forming fourteen lateral equilateral triangles.',
        'builder': HeptagonalAntiprismSolidService.build,
        'calculator': HeptagonalAntiprismSolidCalculator,
    },
    'truncated_tetrahedron': {
        'title': 'Truncated Tetrahedron',
        'summary': 'Four hexagons and four triangles derived from a sliced tetrahedron.',
        'builder': TruncatedTetrahedronSolidService.build,
        'calculator': TruncatedTetrahedronSolidCalculator,
    },
    'cuboctahedron': {
        'title': 'Cuboctahedron',
        'summary': 'Uniform solid blending cube and octahedron symmetries.',
        'builder': CuboctahedronSolidService.build,
        'calculator': CuboctahedronSolidCalculator,
    },
    'truncated_cube': {
        'title': 'Truncated Cube',
        'summary': 'Eight triangles and six octagons from shaving cube corners.',
        'builder': TruncatedCubeSolidService.build,
        'calculator': TruncatedCubeSolidCalculator,
    },
    'truncated_octahedron': {
        'title': 'Truncated Octahedron',
        'summary': 'Space-filling Archimedean solid mixing squares and hexagons.',
        'builder': TruncatedOctahedronSolidService.build,
        'calculator': TruncatedOctahedronSolidCalculator,
    },
    'rhombicuboctahedron': {
        'title': 'Rhombicuboctahedron',
        'summary': 'Eighteen squares and eight triangles arranged with uniform edges.',
        'builder': RhombicuboctahedronSolidService.build,
        'calculator': RhombicuboctahedronSolidCalculator,
    },
    'truncated_cuboctahedron': {
        'title': 'Truncated Cuboctahedron',
        'summary': 'Great rhombicuboctahedron weaving hexagons, squares, and octagons.',
        'builder': TruncatedCuboctahedronSolidService.build,
        'calculator': TruncatedCuboctahedronSolidCalculator,
    },
    'snub_cube': {
        'title': 'Snub Cube',
        'summary': 'Chiral Archimedean solid pairing squares with equilateral triangles.',
        'builder': SnubCubeSolidService.build,
        'calculator': SnubCubeSolidCalculator,
    },
    'icosidodecahedron': {
        'title': 'Icosidodecahedron',
        'summary': 'Alternating pentagon-triangle faces bridging platonic duals.',
        'builder': IcosidodecahedronSolidService.build,
        'calculator': IcosidodecahedronSolidCalculator,
    },
    'truncated_dodecahedron': {
        'title': 'Truncated Dodecahedron',
        'summary': 'Decagon-triangle mixture carved from a dodecahedron.',
        'builder': TruncatedDodecahedronSolidService.build,
        'calculator': TruncatedDodecahedronSolidCalculator,
    },
    'truncated_icosahedron': {
        'title': 'Truncated Icosahedron',
        'summary': 'Soccer-ball blend of twelve pentagons and twenty hexagons.',
        'builder': TruncatedIcosahedronSolidService.build,
        'calculator': TruncatedIcosahedronSolidCalculator,
    },
    'rhombicosidodecahedron': {
        'title': 'Rhombicosidodecahedron',
        'summary': 'Uniform solid with triangles, squares, and pentagons in harmony.',
        'builder': RhombicosidodecahedronSolidService.build,
        'calculator': RhombicosidodecahedronSolidCalculator,
    },
    'truncated_icosidodecahedron': {
        'title': 'Truncated Icosidodecahedron',
        'summary': 'Great rhombicosidodecahedron with pentagons, decagons, and squares.',
        'builder': TruncatedIcosidodecahedronSolidService.build,
        'calculator': TruncatedIcosidodecahedronSolidCalculator,
    },
    'snub_dodecahedron': {
        'title': 'Snub Dodecahedron',
        'summary': 'Chiral pentagon-triangle solid completing the Archimedean family.',
        'builder': SnubDodecahedronSolidService.build,
        'calculator': SnubDodecahedronSolidCalculator,
    },
}


class GeometryHub(QWidget):
    """Hub widget for Geometry pillar - displays available tools."""
    
    def __init__(self, window_manager: WindowManager):
        """
        Initialize the Geometry hub.
        
        Args:
            window_manager: Shared window manager instance
        """
        super().__init__()
        self.window_manager = window_manager
        self.categories = CATEGORY_DEFINITIONS
        self.category_buttons: List[QPushButton] = []
        self.selected_category_index = 0
        self.content_layout: Optional[QVBoxLayout] = None
        self.menu_layout: Optional[QVBoxLayout] = None
        self._setup_ui()
        self._render_category(0)
    
    def _setup_ui(self):
        """Set up the hub interface."""
        self.setStyleSheet("background-color: #f8fafc;")

        root_layout = QVBoxLayout(self)
        root_layout.setSpacing(24)
        root_layout.setContentsMargins(32, 32, 32, 32)

        hero = self._build_hero_banner()
        root_layout.addWidget(hero)

        body_layout = QHBoxLayout()
        body_layout.setSpacing(18)
        root_layout.addLayout(body_layout)

        nav_frame = self._build_category_nav()
        body_layout.addWidget(nav_frame, 0)

        content_frame = self._build_content_area()
        body_layout.addWidget(content_frame, 1)

        footer = QLabel("Ready • Bidirectional calculations • Interactive viewport ✦ Future 3D support")
        footer.setStyleSheet("color: #475569; font-size: 10pt; font-style: italic; background: transparent;")
        root_layout.addWidget(footer)

    def _build_hero_banner(self) -> QWidget:
        banner = QFrame()
        banner.setStyleSheet(
            """
            QFrame {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                  stop:0 #1d4ed8, stop:1 #9333ea);
                border-radius: 20px;
                padding: 24px;
            }
            """
        )
        layout = QVBoxLayout(banner)
        layout.setSpacing(6)

        title_row = QHBoxLayout()
        title_row.setSpacing(10)

        title = QLabel("Geometry Library")
        title.setStyleSheet("color: white; font-size: 26pt; font-weight: 700; letter-spacing: -0.5px;")
        title_row.addWidget(title)
        title_row.addStretch()

        hero_btn = QPushButton("Advanced Scientific Calculator")
        hero_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        hero_btn.setStyleSheet(
            """
            QPushButton {background-color: #0ea5e9; color: white; border: none;
                        padding: 10px 14px; border-radius: 10px; font-weight: 700;}
            QPushButton:hover {background-color: #0284c7;}
            QPushButton:pressed {background-color: #0369a1;}
            """
        )
        hero_btn.setToolTip("Open the advanced scientific calculator")
        hero_btn.clicked.connect(self._open_advanced_scientific_calculator)
        title_row.addWidget(hero_btn)



        # Polygonal Numbers Button
        poly_btn = QPushButton("Polygonal Numbers")
        poly_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        poly_btn.setStyleSheet(
            """
            QPushButton {background-color: #f59e0b; color: white; border: none;
                        padding: 10px 14px; border-radius: 10px; font-weight: 700;}
            QPushButton:hover {background-color: #d97706;}
            QPushButton:pressed {background-color: #b45309;}
            """
        )
        poly_btn.setToolTip("Visualize polygonal and centered polygonal numbers")
        poly_btn.clicked.connect(self._open_polygonal_number_visualizer)
        title_row.addWidget(poly_btn)

        # Experimental Star Numbers Button
        exp_btn = QPushButton("Experimental Stars")
        exp_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exp_btn.setStyleSheet(
            """
            QPushButton {background-color: #9333ea; color: white; border: none;
                        padding: 10px 14px; border-radius: 10px; font-weight: 700;}
            QPushButton:hover {background-color: #7e22ce;}
            QPushButton:pressed {background-color: #6b21a8;}
            """
        )
        exp_btn.setToolTip("Explore generalized star numbers (P-grams)")
        exp_btn.clicked.connect(self._open_experimental_star_visualizer)
        title_row.addWidget(exp_btn)

        # 3D Figurate Numbers Button
        figurate_3d_btn = QPushButton("3D Figurate")
        figurate_3d_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        figurate_3d_btn.setStyleSheet(
            """
            QPushButton {background-color: #06b6d4; color: white; border: none;
                        padding: 10px 14px; border-radius: 10px; font-weight: 700;}
            QPushButton:hover {background-color: #0891b2;}
            QPushButton:pressed {background-color: #0e7490;}
            """
        )
        figurate_3d_btn.setToolTip("Visualize 3D figurate numbers (tetrahedral, pyramidal, cubic)")
        figurate_3d_btn.clicked.connect(self._open_figurate_3d_visualizer)
        title_row.addWidget(figurate_3d_btn)

        layout.addLayout(title_row)

        subtitle = QLabel("Explore sacred shapes, from perfect circles to multidimensional solids")
        subtitle.setStyleSheet("color: rgba(255,255,255,0.85); font-size: 12pt;")
        layout.addWidget(subtitle)

        return banner

    def _build_category_nav(self) -> QWidget:
        frame = QFrame()
        frame.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 18px;
            }
            """
        )

        layout = QHBoxLayout(frame)
        layout.setSpacing(12)
        layout.setContentsMargins(18, 18, 18, 18)

        categories_panel = QFrame()
        categories_panel.setFixedWidth(200)
        categories_panel.setStyleSheet("background: transparent;")
        categories_layout = QVBoxLayout(categories_panel)
        categories_layout.setSpacing(10)
        categories_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("Categories")
        label.setStyleSheet("color: #0f172a; font-weight: 700; font-size: 12pt;")
        categories_layout.addWidget(label)

        for idx, category in enumerate(self.categories):
            button = QPushButton(f"{category['icon']}  {category['name']}")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setCheckable(True)
            button.clicked.connect(lambda _, i=idx: self._render_category(i))
            button.setStyleSheet(self._category_button_style(False))
            categories_layout.addWidget(button)
            self.category_buttons.append(button)

        categories_layout.addStretch()

        menu_panel = QFrame()
        menu_panel.setMinimumWidth(220)
        menu_panel.setStyleSheet("background-color: #f8fafc; border-radius: 14px;")
        menu_panel_layout = QVBoxLayout(menu_panel)
        menu_panel_layout.setSpacing(8)
        menu_panel_layout.setContentsMargins(14, 14, 14, 14)

        menu_label = QLabel("Shapes in family")
        menu_label.setStyleSheet("color: #475569; font-weight: 600; font-size: 10pt;")
        menu_panel_layout.addWidget(menu_label)

        menu_scroll = QScrollArea()
        menu_scroll.setWidgetResizable(True)
        menu_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        menu_widget = QWidget()
        self.menu_layout = QVBoxLayout(menu_widget)
        self.menu_layout.setContentsMargins(0, 0, 0, 0)
        self.menu_layout.setSpacing(8)
        menu_scroll.setWidget(menu_widget)
        menu_panel_layout.addWidget(menu_scroll)

        layout.addWidget(categories_panel)
        layout.addWidget(menu_panel, 1)
        return frame

    def _build_content_area(self) -> QWidget:
        frame = QFrame()
        frame.setStyleSheet("background-color: transparent;")
        outer_layout = QVBoxLayout(frame)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        content_widget = QWidget()
        scroll.setWidget(content_widget)

        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(16)

        outer_layout.addWidget(scroll)
        return frame

    def _category_button_style(self, active: bool) -> str:
        if active:
            return (
                "QPushButton {background-color: #1d4ed8; color: white; border: none;"
                "padding: 10px 14px; border-radius: 10px; font-weight: 600;}"
            )
        return (
            "QPushButton {background-color: #f1f5f9; color: #0f172a; border: none;"
            "padding: 10px 14px; border-radius: 10px; text-align: left; font-weight: 600;}"
            "QPushButton:hover {background-color: #e2e8f0;}"
        )

    def _render_category(self, index: int):
        if not (0 <= index < len(self.categories)):
            return
        self.selected_category_index = index
        for i, button in enumerate(self.category_buttons):
            button.setChecked(i == index)
            button.setStyleSheet(self._category_button_style(i == index))
        self._populate_category_content(self.categories[index])
        self._populate_menu(self.categories[index])

    def _populate_category_content(self, category: dict):
        if not self.content_layout:
            return
        self._clear_layout(self.content_layout)

        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        title = QLabel(f"{category['icon']}  {category['name']}")
        title.setStyleSheet("color: #0f172a; font-size: 22pt; font-weight: 700;")
        header_layout.addWidget(title)

        tagline = QLabel(category['tagline'])
        tagline.setStyleSheet("color: #475569; font-size: 11pt;")
        header_layout.addWidget(tagline)
        header_layout.addStretch()

        sci_calc_btn = QPushButton("Advanced Scientific Calculator")
        sci_calc_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        sci_calc_btn.setStyleSheet(self._primary_button_style())
        sci_calc_btn.setToolTip("Open a full scientific calculator in its own window")
        sci_calc_btn.clicked.connect(self._open_advanced_scientific_calculator)
        header_layout.addWidget(sci_calc_btn)

        self.content_layout.addWidget(header)

        for shape_def in category['shapes']:
            card = self._create_shape_card(shape_def)
            self.content_layout.addWidget(card)

        self.content_layout.addStretch()

    def _populate_menu(self, category: dict):
        if not hasattr(self, 'menu_layout') or self.menu_layout is None:
            return
        self._clear_layout(self.menu_layout)

        menu_tree = category.get('menu')
        if menu_tree:
            shape_lookup = {shape['name']: shape for shape in category['shapes']}
            self._add_menu_entries(menu_tree, shape_lookup, indent=0)
        else:
            for shape_def in category['shapes']:
                entry = self._create_menu_entry(shape_def)
                self.menu_layout.addWidget(entry)

        self.menu_layout.addStretch()

    def _add_menu_entries(self, entries: List[Any], shape_lookup: Dict[str, dict], indent: int):
        layout = self.menu_layout
        if layout is None:
            return
        for item in entries:
            if isinstance(item, str):
                shape_def = shape_lookup.get(item)
                if shape_def:
                    entry = self._create_menu_entry(shape_def, indent)
                    layout.addWidget(entry)
                continue

            if isinstance(item, dict):
                if 'shape' in item:
                    shape_def = shape_lookup.get(item['shape'])
                    if shape_def:
                        entry = self._create_menu_entry(shape_def, indent + item.get('indent_adjust', 0))
                        layout.addWidget(entry)
                    continue

                label = item.get('label')
                child_items = item.get('items')
                if label:
                    label_container = QWidget()
                    label_layout = QHBoxLayout(label_container)
                    label_layout.setContentsMargins(indent, 6, 0, 2)
                    label_layout.setSpacing(0)
                    label_widget = QLabel(label)
                    label_widget.setStyleSheet("color: #64748b; font-weight: 600; font-size: 9pt;")
                    label_layout.addWidget(label_widget)
                    layout.addWidget(label_container)
                if child_items:
                    self._add_menu_entries(child_items, shape_lookup, indent + 16)

    def _create_menu_entry(self, shape_definition: dict, indent: int = 0) -> QWidget:
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(indent, 0, 0, 0)
        container_layout.setSpacing(0)

        button = QPushButton(shape_definition['name'])
        button.setToolTip(shape_definition.get('summary', ''))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(
            "QPushButton {background-color: #f8fafc; border: 1px solid #e2e8f0;"
            "border-radius: 10px; padding: 8px 12px; text-align: left; color: #0f172a;}"
            "QPushButton:hover {background-color: #eef2ff; border-color: #c7d2fe;}"
        )
        container_layout.addWidget(button)

        factory: Optional[Callable] = shape_definition.get('factory')
        shape_type = shape_definition.get('type')
        status = shape_definition.get('status')
        polygon_sides = shape_definition.get('polygon_sides')

        if status and not factory and not polygon_sides and shape_type not in {'regular_polygon', 'regular_polygon_custom'}:
            button.setEnabled(False)
            button.setCursor(Qt.CursorShape.ArrowCursor)
            button.setStyleSheet(
                "QPushButton {background-color: #f1f5f9; border: 1px dashed #e2e8f0;"
                "border-radius: 10px; padding: 8px 12px; text-align: left; color: #94a3b8;}"
            )
        else:
            if polygon_sides:
                button.clicked.connect(lambda _, n=polygon_sides: self._open_polygon_calculator(n))
            elif shape_type == 'regular_polygon':
                button.clicked.connect(lambda _, default_sides=shape_definition.get('default_sides', 6): self._open_polygon_calculator(default_sides))
            elif shape_type == 'regular_polygon_custom':
                button.clicked.connect(self._prompt_custom_polygon)
            elif shape_type == 'polygonal_numbers':
                button.clicked.connect(self._open_polygonal_number_visualizer)
            elif shape_type == 'star_numbers':
                button.clicked.connect(self._open_star_number_visualizer)
            elif shape_type == 'solid_viewer':
                solid_id = shape_definition.get('solid_id')
                if solid_id in SOLID_VIEWER_CONFIG:
                    button.clicked.connect(lambda _, sid=solid_id: self._open_solid_viewer(sid))
                else:
                    button.setEnabled(False)
                    button.setCursor(Qt.CursorShape.ArrowCursor)
            elif factory:
                button.clicked.connect(lambda _, ctor=factory: self._open_shape_calculator(ctor()))
            else:
                button.setEnabled(False)
                button.setCursor(Qt.CursorShape.ArrowCursor)
                button.setStyleSheet(
                    "QPushButton {background-color: #f1f5f9; border: 1px dashed #e2e8f0;"
                    "border-radius: 10px; padding: 8px 12px; text-align: left; color: #94a3b8;}"
                )

        return container

    def _create_shape_card(self, shape_definition: dict) -> QWidget:
        frame = QFrame()
        frame.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 18px;
                padding: 20px;
            }
            QFrame:hover {
                border-color: #cbd5e1;
                box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
            }
            """
        )

        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        title_row = QHBoxLayout()
        name_label = QLabel(shape_definition['name'])
        name_label.setStyleSheet("color: #0f172a; font-size: 14pt; font-weight: 700;")
        title_row.addWidget(name_label)

        status = shape_definition.get('status')
        if status:
            badge = QLabel(status)
            badge.setStyleSheet(
                "color: #7c3aed; background-color: rgba(124,58,237,0.12);"
                "padding: 4px 10px; border-radius: 999px; font-size: 9pt;"
            )
            title_row.addWidget(badge)
        title_row.addStretch()
        layout.addLayout(title_row)

        summary = QLabel(shape_definition.get('summary', ''))
        summary.setWordWrap(True)
        summary.setStyleSheet("color: #475569; font-size: 10.5pt;")
        layout.addWidget(summary)

        polygon_sides = shape_definition.get('polygon_sides')
        shape_type = shape_definition.get('type')

        if shape_type == 'regular_polygon':
            layout.addSpacing(6)
            ctrl_row = QHBoxLayout()
            ctrl_row.setSpacing(10)

            spin_label = QLabel("Sides:")
            spin_label.setStyleSheet("color: #475569; font-weight: 600;")
            ctrl_row.addWidget(spin_label)

            polygon_spin = QSpinBox()
            polygon_spin.setMinimum(3)
            polygon_spin.setMaximum(40)
            polygon_spin.setValue(6)
            polygon_spin.setStyleSheet(
                "QSpinBox {padding: 6px 10px; font-size: 11pt; border: 1px solid #cbd5e1; border-radius: 8px;}"
                "QSpinBox:focus {border-color: #3b82f6;}"
            )
            ctrl_row.addWidget(polygon_spin)
            ctrl_row.addStretch()

            open_btn = QPushButton("Open Regular Polygon Calculator")
            open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            open_btn.setStyleSheet(self._primary_button_style())
            open_btn.clicked.connect(lambda _, spin=polygon_spin: self._open_polygon_calculator(spin.value()))
            layout.addLayout(ctrl_row)
            layout.addWidget(open_btn)
            return frame
        if polygon_sides:
            open_btn = QPushButton(f"Open {polygon_sides}-gon Calculator")
            open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            open_btn.setStyleSheet(self._primary_button_style())
            open_btn.clicked.connect(lambda _, n=polygon_sides: self._open_polygon_calculator(n))
            layout.addWidget(open_btn)
            return frame

        if shape_type == 'regular_polygon_custom':
            layout.addSpacing(6)
            open_btn = QPushButton("Choose n and Open Calculator")
            open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            open_btn.setStyleSheet(self._primary_button_style())
            open_btn.clicked.connect(self._prompt_custom_polygon)
            layout.addWidget(open_btn)
            return frame
        if shape_type == 'polygonal_numbers':
            layout.addSpacing(6)
            open_btn = QPushButton("Open Polygonal Visualizer")
            open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            open_btn.setStyleSheet(self._primary_button_style())
            open_btn.clicked.connect(self._open_polygonal_number_visualizer)
            layout.addWidget(open_btn)
            return frame

        if shape_type == 'star_numbers':
            layout.addSpacing(6)
            open_btn = QPushButton("Open Star Visualizer")
            open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            open_btn.setStyleSheet(self._primary_button_style())
            open_btn.clicked.connect(self._open_star_number_visualizer)
            layout.addWidget(open_btn)
            return frame

        if shape_definition.get('type') == 'solid_viewer':
            solid_id = shape_definition.get('solid_id')
            open_btn = QPushButton("Open 3D Viewer")
            open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            open_btn.setStyleSheet(self._primary_button_style())
            if solid_id in SOLID_VIEWER_CONFIG:
                open_btn.clicked.connect(lambda _, sid=solid_id: self._open_solid_viewer(sid))
            else:
                open_btn.setEnabled(False)
                open_btn.setCursor(Qt.CursorShape.ArrowCursor)
            layout.addWidget(open_btn)
            return frame

        factory: Optional[Callable] = shape_definition.get('factory')
        if factory:
            open_btn = QPushButton("Open Calculator")
            open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            open_btn.setStyleSheet(self._primary_button_style())
            open_btn.clicked.connect(lambda _, ctor=factory: self._open_shape_calculator(ctor()))
            layout.addWidget(open_btn)
        else:
            hint = QLabel("Stay tuned – this shape is currently in design.")
            hint.setStyleSheet("color: #94a3b8; font-size: 9.5pt; font-style: italic;")
            layout.addWidget(hint)

        return frame

    def _primary_button_style(self) -> str:
        return (
            "QPushButton {background-color: #1d4ed8; color: white; border: none;"
            "padding: 10px 16px; border-radius: 10px; font-weight: 600;}"
            "QPushButton:hover {background-color: #2563eb;}"
            "QPushButton:pressed {background-color: #1e3a8a;}"
        )

    def _prompt_custom_polygon(self):
        sides, ok = QInputDialog.getInt(
            self,
            "Regular n-gon",
            "Number of sides (n ≥ 3):",
            value=6,
            min=3,
            max=200,
        )
        if ok:
            self._open_polygon_calculator(sides)

    def _open_solid_viewer(self, solid_id: Optional[str]):
        if not solid_id:
            return
        config = SOLID_VIEWER_CONFIG.get(solid_id)
        if not config:
            return
        builder = config.get('builder')
        calculator_cls = config.get('calculator')
        calculator = calculator_cls() if calculator_cls else None
        payload = None
        if calculator is None and builder:
            result = builder()
            payload = getattr(result, 'payload', result)

        window = cast(
            Geometry3DWindow,
            self.window_manager.open_window(
                window_type=f"geometry_{solid_id}_viewer",
                window_class=Geometry3DWindow,
                allow_multiple=True,
                window_manager=self.window_manager,
            ),
        )
        window.setWindowTitle(f"{config.get('title', solid_id.title())} • 3D Viewer")
        window.set_solid_context(title=config.get('title'), summary=config.get('summary'))
        if calculator is not None:
            window.set_calculator(calculator)
        else:
            window.set_payload(payload)

    @staticmethod
    def _clear_layout(layout: QLayout):
        while layout.count():
            item = layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout is not None:
                    GeometryHub._clear_layout(child_layout)

    
    def _open_shape_calculator(self, shape):
        """Open geometry calculator for a shape."""
        self.window_manager.open_window(
            window_type=f"geometry_{shape.name.lower().replace(' ', '_')}",
            window_class=GeometryCalculatorWindow,
            allow_multiple=True,
            shape=shape,
            window_manager=self.window_manager,
        )

    def _open_advanced_scientific_calculator(self):
        """Open the standalone scientific calculator."""
        self.window_manager.open_window(
            window_type="geometry_advanced_scientific_calculator",
            window_class=AdvancedScientificCalculatorWindow,
            allow_multiple=True,
            window_manager=self.window_manager,
        )

    def _open_polygonal_number_visualizer(self):
        """Open polygonal/centered polygonal number visualizer."""
        window = self.window_manager.open_window(
            window_type="geometry_polygonal_numbers",
            window_class=PolygonalNumberWindow,
            allow_multiple=True,
            window_manager=self.window_manager,
        )
        # Default is polygonal, which is index 0.


    
    def _open_polygon_calculator(self, sides: int):
        """Open geometry calculator for regular polygon."""
        shape = RegularPolygonShape(num_sides=sides)
        self._open_shape_calculator(shape)

    def _open_experimental_star_visualizer(self):
        """Open generalized experimental star visualizer."""
        self.window_manager.open_window(
            window_type="geometry_experimental_star",
            window_class=ExperimentalStarWindow,
            allow_multiple=True,
            window_manager=self.window_manager,
        )

    def _open_figurate_3d_visualizer(self):
        """Open 3D figurate numbers visualizer."""
        self.window_manager.open_window(
            window_type="geometry_figurate_3d",
            window_class=Figurate3DWindow,
            allow_multiple=True,
            window_manager=self.window_manager,
        )
