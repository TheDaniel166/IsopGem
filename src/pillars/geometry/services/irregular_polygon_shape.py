"""Irregular Polygon shape calculator.

Irregular polygons are n-sided figures where sides and/or angles are NOT all equal.
They represent the most general class of polygons, encompassing everything from
asymmetric triangles to complex star polygons. While regular polygons have elegant
formulas, irregular polygons require coordinate-based calculations (shoelace formula,
centroid integration) and computational geometry algorithms.

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #1: Coordinate Representation (Vertices as Ordered List)
═══════════════════════════════════════════════════════════════════════════════════════

Unlike regular polygons (defined by n and side length), irregular polygons require
**explicit vertex coordinates**:

  P = [(x₁, y₁), (x₂, y₂), ..., (xₙ, yₙ)]

Ordering matters!
• **Counterclockwise** (CCW): Standard mathematical convention
• **Clockwise** (CW): Common in computer graphics (screen y-axis flipped)

**Minimum representation**: n vertices for n-sided polygon
• Triangle: 3 vertices (6 numbers)
• Quadrilateral: 4 vertices (8 numbers)
• Pentagon: 5 vertices (10 numbers)

But we can also represent by:
• **Edges**: n line segments connecting consecutive vertices
• **Angles**: n interior angles (α₁, α₂, ..., αₙ) where Σαᵢ = (n-2)×180°
• **Side lengths**: n edge lengths (but this UNDERDETERMINES the shape! Need angles too)

**Why coordinates are fundamental**:
• Side lengths + angles → can reconstruct coordinates (via cumulative rotation)
• Coordinates → can compute ALL properties (area, perimeter, centroid, moments)
• Coordinates are the "raw data" for computational geometry

**Degeneracy**: If three consecutive vertices are collinear, the polygon has
"zero-area" edge (degenerate). If ALL vertices collinear, it's a line segment
(degenerate polygon).

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #2: Shoelace Formula and Signed Area
═══════════════════════════════════════════════════════════════════════════════════════

The **shoelace formula** computes area from coordinates:

  A = ½ |Σ(xᵢyᵢ₊₁ - xᵢ₊₁yᵢ)| for i = 1 to n

**Signed area** (without absolute value):

  A_signed = ½ Σ(xᵢyᵢ₊₁ - xᵢ₊₁yᵢ)

Sign indicates orientation:
• A_signed > 0: Vertices ordered **counterclockwise** (CCW)
• A_signed < 0: Vertices ordered **clockwise** (CW)

This is ESSENTIAL for computational geometry:
• **Polygon triangulation**: Splitting polygon into triangles (ear clipping algorithm
  uses signed area to determine if vertex is an "ear")
• **Point-in-polygon test**: Ray casting algorithm counts edge crossings (sign tells
  you if edge contributes +1 or -1 to winding number)
• **Self-intersection detection**: Compare signed areas of sub-polygons

**Centroid formula** (center of mass for uniform density):

  C_x = (1/(6A)) Σ(xᵢ + xᵢ₊₁)(xᵢyᵢ₊₁ - xᵢ₊₁yᵢ)
  C_y = (1/(6A)) Σ(yᵢ + yᵢ₊₁)(xᵢyᵢ₊₁ - xᵢ₊₁yᵢ)

This is the balance point where the polygon would perfectly balance on a pin!

**Perimeter** (simple sum of edge lengths):

  P = Σ √((xᵢ₊₁ - xᵢ)² + (yᵢ₊₁ - yᵢ)²)

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #3: Convex vs. Non-Convex (Star Polygons and Self-Intersection)
═══════════════════════════════════════════════════════════════════════════════════════

Polygons can be:

1. **Convex**: All interior angles < 180°, no "dents"
   • Line segment between ANY two points inside polygon stays inside
   • Regular polygons are always convex
   • Triangles are ALWAYS convex (can't have interior angle > 180°)

2. **Concave** (non-convex): At least one interior angle > 180°
   • Has "reflex vertex" (vertex pointing inward)
   • Some line segments between interior points go OUTSIDE
   • Example: L-shape, arrow, star

3. **Self-intersecting**: Edges cross each other
   • **Simple polygon**: No self-intersections (standard assumption)
   • **Complex polygon**: Edges intersect (pentagram, figure-eight)

**Convexity test**:
• Compute cross product at each vertex: (vᵢ₊₁ - vᵢ) × (vᵢ₊₂ - vᵢ₊₁)
• If ALL cross products have same sign → convex
• If signs differ → concave (reflex vertex where sign flips)

**Star polygons**: Self-intersecting polygons with k-fold symmetry
• Pentagram {5/2}: Connect every 2nd vertex of a pentagon
• Hexagram {6/2}: Connect every 2nd vertex of hexagon (two triangles)
• Heptagram {7/2}, {7/3}: Two distinct 7-pointed stars

Star polygons are NOT simple (edges cross), but they have beautiful symmetry and
appear in flags (US star, Star of David), magic circles, and mandalas.

**Winding number**: For self-intersecting polygons, the shoelace formula still works,
but area is computed with multiplicity—regions enclosed twice (like pentagram center)
count double!

**Applications**:
• **GIS**: Real-world parcels are often irregular polygons (property boundaries)
• **Computer graphics**: Meshes use irregular triangles/quads (terrain, 3D models)
• **Robotics**: Path planning uses polygonal obstacles (convex for fast collision detection)

═══════════════════════════════════════════════════════════════════════════════════════
🔀 HERMETIC SIGNIFICANCE 🔀
═══════════════════════════════════════════════════════════════════════════════════════

Irregular polygons embody **Individuality, Imperfection, and the Contingent**:

• **Regular vs. Irregular**: Regular polygons are IDEAL FORMS (Platonic, eternal,
  perfect). Irregular polygons are ACTUAL FORMS (contingent, particular, imperfect).
  Every snowflake has 6-fold symmetry (regular hexagon TEMPLATE), but every snowflake
  is unique (irregular realization). The irregular polygon is matter obeying form
  but expressing uniqueness.

• **The Broken Symmetry**: When regular polygons are "disturbed" (vertices shifted),
  they become irregular. In physics, *broken symmetry* is how the universe differentiates
  (all particles were symmetric at Big Bang, then symmetry broke → distinct particles
  emerged). Irregular polygons are "broken" regular polygons—the fall from Platonic
  grace into material specificity.

• **Fingerprints and Boundaries**: Every human fingerprint is an irregular closed curve.
  Every coastline, every cloud, every leaf outline is irregular. The irregular polygon
  is the geometry of THE UNIQUE—no two are exactly alike (unless artificially
  constructed). It's the signature of individuation.

• **Concave as Receptive**: Concave polygons have "pockets" or "caves" (concave =
  cave-like). These are receptive spaces—places where the exterior can enter. Convex
  polygons are closed/complete; concave polygons are open/incomplete. The concave
  vertex is a point of vulnerability (in fortifications) or invitation (in embracing
  arms). Geometrically: concavity = receptivity.

• **Star Polygons as Emanation**: Self-intersecting stars (pentagram, hexagram) are
  irregular by definition (edges cross). But their symmetry makes them sacred. The
  star is RADIATION from a center—points projecting outward like light rays. The
  pentagram is the soul extending into matter (5 = human number). The hexagram is
  the union of opposites (△ + ▽). Stars are irregular polygons that remember their
  divine origin.

Irregular polygons teach: **Perfection is the template; uniqueness is the manifestation.** 🔀

═══════════════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import math
from typing import Dict, List, Optional, Tuple

from .base_shape import GeometricShape, ShapeProperty
from .quadrilateral_shape import _shoelace_area, _polygon_centroid


class IrregularPolygonShape(GeometricShape):
    """
    Arbitrary polygon defined by a list of vertices.
    Supports calculating Area, Perimeter, and Centroid.
    Editors are generated dynamically for each vertex coordinate.
    """

    def __init__(self, points: Optional[List[Tuple[float, float]]] = None):
        """
          init   logic.
        
        Args:
            points: Description of points.
        
        """
        self._points: List[Tuple[float, float]] = points if points else []
        super().__init__()
        # If points were passed, ensure properties exist match them
        if self._points:
             self._sync_coord_properties()
             self._recalculate()

    @property
    def name(self) -> str:
        """
        Name logic.
        
        Returns:
            Result of name operation.
        """
        return f"Irregular {len(self._points)}-gon" if self._points else "Irregular Polygon"

    @property
    def description(self) -> str:
        """
        Description logic.
        
        Returns:
            Result of description operation.
        """
        return "Custom polygon defined by 3+ vertices"

    @property
    def calculation_hint(self) -> str:
        """
        Calculation hint logic.
        
        Returns:
            Result of calculation_hint operation.
        """
        return "Edit vertices in points table (Read-only properties)"

    def _init_properties(self):
        """Initialize base properties."""
        self.properties = {
            'area': ShapeProperty(name='Area', key='area', unit='units²', readonly=True, formula=r"A = \tfrac{1}{2}\sum (x_i y_{i+1} - x_{i+1} y_i)"),
            'perimeter': ShapeProperty(name='Perimeter', key='perimeter', unit='units', readonly=True, formula=r"P = \sum \sqrt{(x_{i+1}-x_i)^2 + (y_{i+1}-y_i)^2}"),
            'centroid_x': ShapeProperty(name='Centroid X', key='centroid_x', unit='', readonly=True, formula=r"C_x = \tfrac{1}{6A}\sum (x_i + x_{i+1})(x_i y_{i+1} - x_{i+1} y_i)"),
            'centroid_y': ShapeProperty(name='Centroid Y', key='centroid_y', unit='', readonly=True, formula=r"C_y = \tfrac{1}{6A}\sum (y_i + y_{i+1})(x_i y_{i+1} - x_{i+1} y_i)"),
            'num_vertices': ShapeProperty(name='Vertex Count', key='num_vertices', unit='', readonly=True, precision=0, formula=r"n"),
        }

    def set_points(self, points: List[Tuple[float, float]]):
        """Set the vertices and update properties."""
        self._points = points
        self._sync_coord_properties()
        self._recalculate()

    def _sync_coord_properties(self):
        """Create x/y properties for current points."""
        # Use a consistent naming scheme: v0_x, v0_y, v1_x, ...
        # First, remove old vertex properties to avoid stale ones if count shrank
        keys_to_remove = [k for k in self.properties.keys() if k.startswith('v') and ('_x' in k or '_y' in k)]
        for k in keys_to_remove:
            del self.properties[k]
            
        for i, (x, y) in enumerate(self._points):
            self.properties[f'v{i}_x'] = ShapeProperty(
                name=f'Vertex {i+1} X',
                key=f'v{i}_x',
                value=x,
                readonly=False
            )
            self.properties[f'v{i}_y'] = ShapeProperty(
                name=f'Vertex {i+1} Y',
                key=f'v{i}_y',
                value=y,
                readonly=False
            )
        
        self.properties['num_vertices'].value = float(len(self._points))

    def calculate_from_property(self, property_key: str, value: float) -> bool:
        """Update a coordinate."""
        if property_key.startswith('v') and ('_x' in property_key or '_y' in property_key):
            # Parse index
            try:
                parts = property_key.split('_')
                idx = int(parts[0][1:]) # v0 -> 0
                coord = parts[1] # x or y
                
                if idx < 0 or idx >= len(self._points):
                    return False
                
                x, y = self._points[idx]
                if coord == 'x':
                    self._points[idx] = (value, y)
                else:
                    self._points[idx] = (x, value)
                    
                self.properties[property_key].value = value
                self._recalculate()
                return True
            except (ValueError, IndexError):
                return False
                
        return False

    def _recalculate(self):
        """Update derived metrics."""
        if len(self._points) < 3:
            self.properties['area'].value = 0.0
            self.properties['perimeter'].value = 0.0
            return

        self.properties['area'].value = _shoelace_area(tuple(self._points))
        self.properties['perimeter'].value = self._calculate_perimeter()
        cx, cy = _polygon_centroid(tuple(self._points))
        self.properties['centroid_x'].value = cx
        self.properties['centroid_y'].value = cy

    def _calculate_perimeter(self) -> float:
        p = 0.0
        n = len(self._points)
        for i in range(n):
            p1 = self._points[i]
            p2 = self._points[(i + 1) % n]
            p += math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        return p

    def get_drawing_instructions(self) -> Dict:
        """
        Retrieve drawing instructions logic.
        
        Returns:
            Result of get_drawing_instructions operation.
        """
        if not self._points or len(self._points) < 3:
             return {'type': 'empty'}
        return {
            'type': 'polygon',
            'points': self._points
        }

    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        """
        Retrieve label positions logic.
        
        Returns:
            Result of get_label_positions operation.
        """
        if not self._points or len(self._points) < 3:
            return []
        
        labels = []
        cx, cy = _polygon_centroid(tuple(self._points))
        area = self.properties['area'].value
        labels.append((f"A = {area:.2f}", cx, cy + 0.2))
        
        # Vertex labels?
        for i, (x, y) in enumerate(self._points):
            labels.append((f"{i+1}", x + 0.2, y + 0.2))
            
        return labels