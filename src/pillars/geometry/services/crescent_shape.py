"""Crescent (lune) shape calculator.

A crescent (or lune) is the region between two intersecting circular arcs. It is formed
by subtracting one circular disk from another, where the circles partially overlap. The
crescent appears in lunar phases, Islamic symbolism, and geometric constructions related
to the ancient problem of "squaring the circle" (Hippocrates' lunes).

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #1: Lune as Intersection Geometry (Circle Minus Circle)
═══════════════════════════════════════════════════════════════════════════════════════

A crescent is defined by TWO circles:
• **Outer circle**: radius R, center O₁
• **Inner circle**: radius r, center O₂
• **Offset**: distance d between centers

The crescent area is:

  A_crescent = A_outer - A_intersection

where A_intersection is the **lens-shaped overlap** (vesica piscis if R = r).

**Lens intersection area** (general formula):

For two circles with radii R and r separated by distance d, the intersection area is:

  A_∩ = R²·arccos((d²+R²-r²)/(2dR)) + r²·arccos((d²+r²-R²)/(2dr)) 
        - (1/2)√[(2dR)² - (d²+R²-r²)²]

This derives from summing two circular segments (one from each circle).

**Special cases**:
• d = 0 (concentric): A_∩ = πr² (smaller circle fully inside) → A_crescent = π(R²-r²) (annulus!)
• d = R + r (externally tangent): A_∩ = 0 → A_crescent = πR² (full circle, no subtraction)
• R = r, d = R (vesica piscis): A_∩ = 2R²(2π/3 - √3/2) → symmetric lens

**Triangle inequality constraint**:
For the circles to intersect: |R - r| < d < R + r
• If d ≥ R + r: circles don't overlap (no crescent, two separate disks)
• If d ≤ |R - r|: one circle fully inside other (annulus or nothing)

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #2: Lunar Phases (Illuminated Crescent)
═══════════════════════════════════════════════════════════════════════════════════════

The crescent shape is most famously observed in **lunar phases**:

**New Moon → Waxing Crescent → First Quarter → Waxing Gibbous → Full Moon**
(then reverse: Waning Gibbous → Third Quarter → Waning Crescent → New Moon)

The crescent phase occurs when the Moon is 0-90° from the Sun (as viewed from Earth):
• **Waxing crescent**: 0-45° (thin sliver growing)
• **Waning crescent**: 315-360° (thin sliver shrinking)

**Geometric model** (simplified):
• Sun illuminates hemisphere facing it (outer circle: full disk)
• We see hemisphere facing Earth (inner circle: terminator curve)
• The visible illuminated part is the CRESCENT (or gibbous when > 50%)

More accurately, the terminator (shadow boundary) is an ELLIPSE (not a circle) because
we view the spherical Moon from an angle. But for thin crescents, the approximation
as two circular arcs is good enough.

**Historical significance**:
• Ancient calendars (lunar calendars) tracked months by crescent sightings
• Islamic calendar begins each month with first visible crescent (hilal)
• The crescent moon (with star) is the symbol of Islam (adopted from Byzantine symbolism)

**Earthshine**: During crescent phase, the dark side of the Moon is faintly visible due
to reflected light from Earth ("the old moon in the new moon's arms"). This is sunlight
reflecting off Earth, then bouncing to the Moon's dark side, then back to us!

**Crescents elsewhere**:
• Venus phases (observed by Galileo, proving heliocentric model!)
• Horns of crescent-shaped nebulae (e.g., Crescent Nebula NGC 6888)

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #3: Hippocrates' Lunes (Squaring the Crescent)
═══════════════════════════════════════════════════════════════════════════════════════

**Hippocrates of Chios** (~440 BCE) discovered that certain lune shapes have areas equal
to the areas of triangles or other rectilinear figures. This was a major breakthrough
toward "squaring the circle."

**Hippocrates' Lune Theorem**:

Consider a right triangle ABC with right angle at C. Draw semicircles on all three sides:
• Semicircle on hypotenuse AB (radius R)
• Semicircles on legs AC and BC (radii r and s)

The two LUNES formed outside the legs (crescents bounded by the large semicircle and
the small semicircles) have combined area EXACTLY EQUAL to the area of the triangle!

Proof sketch:
• By Pythagorean theorem: AB² = AC² + BC²
• Areas of semicircles: (π/2)R² = (π/2)(r² + s²) [using R² = r² + s²]
• Lune areas = (semicircles on legs) - (segments of large semicircle)
• After algebra: A_lunes = A_triangle (exactly!)

**Significance**: This showed that SOME curvilinear figures can be "squared" (expressed
as equivalent rectilinear areas). Hippocrates hoped to extend this to the full circle,
but that proved impossible (π is transcendental, proven 1882).

**Other squarable lunes**: Five types of lunes are known to be squarable (expressible
as rational multiples of rational areas). No others exist!

**Modern understanding**: Lunes are squarable because they're formed by RATIONAL
relationships between circular arcs. The circle itself is not squarable because its
area involves the transcendental constant π.

═══════════════════════════════════════════════════════════════════════════════════════
🌙 HERMETIC SIGNIFICANCE 🌙
═══════════════════════════════════════════════════════════════════════════════════════

The crescent embodies **Phases, Transformation, and the Feminine Principle**:

• **Lunar Symbolism**: The crescent is the MOON in transition—neither new (dark) nor
  full (complete), but WAXING (growing) or WANING (diminishing). It represents the
  cycles of life, death, and rebirth. The Moon (feminine, reflective, changeable) vs.
  Sun (masculine, radiant, constant).

• **The Horns**: The two points of the crescent are "horns"—associated with:
  - The bull (Taurus, fertility, strength)
  - The cow (Hathor in Egyptian myth, nourisher)
  - The horned goddess (Diana/Artemis, moon goddess)
  The horns point UPWARD (waxing) or DOWNWARD (waning), indicating direction of change.

• **Islamic Symbolism**: The crescent (hilal) marks the beginning of the lunar month
  (especially Ramadan). It represents RENEWAL, the fresh start, the first light after
  darkness. Often paired with a star (Venus or a five-pointed star), symbolizing
  divine guidance in the darkness.

• **Triple Goddess**: Maiden (waxing crescent) → Mother (full moon) → Crone (waning
  crescent). The crescent is youth (maiden) and wisdom (crone), bookending the fullness
  of maturity.

• **Incomplete Circle**: The crescent is a PARTIAL circle—potential not yet realized
  (waxing) or fading away (waning). It's the geometry of *becoming* and *un-becoming*,
  not static being. The crescent teaches that perfection (full circle) is momentary—
  most of existence is in the liminal phases.

• **Cup and Horn**: Upward crescent (☽) = cup (receptive, gathering, holding) like
  the Holy Grail. Downward crescent (☾) = pouring out, releasing, emptying. The
  geometry of *receiving* vs. *giving*.

The crescent teaches: **Fullness is fleeting; the true work is in the waxing and waning.** 🌙

═══════════════════════════════════════════════════════════════════════════════════════
"""
import math
from typing import Dict, List, Tuple

from .base_shape import GeometricShape, ShapeProperty


class CrescentShape(GeometricShape):
    """Represents the lune carved from an outer circle by an offset smaller circle."""

    @property
    def name(self) -> str:
        """
        Name logic.
        
        Returns:
            Result of name operation.
        """
        return "Crescent"

    @property
    def description(self) -> str:
        """
        Description logic.
        
        Returns:
            Result of description operation.
        """
        return "Lune/Crescent formed by two intersecting circles"

    @property
    def calculation_hint(self) -> str:
        """
        Calculation hint logic.
        
        Returns:
            Result of calculation_hint operation.
        """
        return "Enter 2 Radii + Shift Distance"

    def _init_properties(self):
        self.properties = {
            "outer_radius": ShapeProperty(
                name="Outer Radius (R)",
                key="outer_radius",
                unit="units",
                formula=r"R",
            ),
            "inner_radius": ShapeProperty(
                name="Inner Radius (r)",
                key="inner_radius",
                unit="units",
                formula=r"r",
            ),
            "offset": ShapeProperty(
                name="Center Offset (d)",
                key="offset",
                unit="units",
                formula=r"d",
            ),
            "outer_diameter": ShapeProperty(
                name="Outer Diameter",
                key="outer_diameter",
                unit="units",
                formula=r"D_R = 2R",
            ),
            "inner_diameter": ShapeProperty(
                name="Inner Diameter",
                key="inner_diameter",
                unit="units",
                formula=r"D_r = 2r",
            ),
            "intersection_area": ShapeProperty(
                name="Overlap Area",
                key="intersection_area",
                unit="units²",
                readonly=True,
                formula=r"A_{\cap} = R^2\cos^{-1}\!\frac{d^2+R^2-r^2}{2dR} + r^2\cos^{-1}\!\frac{d^2+r^2-R^2}{2dr} - \tfrac{1}{2}\sqrt{(-d+R+r)(d+R-r)(d-R+r)(d+R+r)}",
            ),
            "crescent_area": ShapeProperty(
                name="Crescent Area",
                key="crescent_area",
                unit="units²",
                readonly=True,
                formula=r"A_{cres} = \pi R^2 - A_{\cap}",
            ),
            "perimeter": ShapeProperty(
                name="Crescent Perimeter",
                key="perimeter",
                unit="units",
                readonly=True,
                formula=r"P = (2\pi-\alpha)R + \beta r,\ \alpha=2\cos^{-1}\!\tfrac{d^2+R^2-r^2}{2dR},\ \beta=2\cos^{-1}\!\tfrac{d^2+r^2-R^2}{2dr}",
            ),
        }

    def calculate_from_property(self, property_key: str, value: float) -> bool:
        """
        Compute from property logic.
        
        Args:
            property_key: Description of property_key.
            value: Description of value.
        
        Returns:
            Result of calculate_from_property operation.
        """
        if value <= 0:
            return False

        if property_key == "outer_radius":
            inner = self.properties["inner_radius"].value
            if inner is not None and value <= inner:
                return False
            self.properties["outer_radius"].value = value
            self._update_metrics()
            return True

        if property_key == "inner_radius":
            outer = self.properties["outer_radius"].value
            if outer is not None and value >= outer:
                return False
            self.properties["inner_radius"].value = value
            self._update_metrics()
            return True

        if property_key == "offset":
            outer = self.properties["outer_radius"].value
            inner = self.properties["inner_radius"].value
            if outer is None or inner is None:
                return False
            if not self._is_valid_offset(outer, inner, value):
                return False
            self.properties["offset"].value = value
            self._update_metrics()
            return True

        if property_key == "outer_diameter":
            return self.calculate_from_property("outer_radius", value / 2)

        if property_key == "inner_diameter":
            return self.calculate_from_property("inner_radius", value / 2)

        return False

    def _update_metrics(self):
        """
        Compute crescent (lune) properties.

        CRESCENT (LUNE) DERIVATIONS:
        =============================

        Definition:
        -----------
        A crescent (or lune) is the **region between two intersecting circular arcs**,
        typically formed when a smaller circle overlaps a larger circle.

        Parameters:
        - **Outer radius**: R (larger circle)
        - **Inner radius**: r (smaller circle)
        - **Offset (center distance)**: d

        Geometry Constraints:
        - R > r (outer is larger)
        - d ≥ 0 (centers can coincide or be separated)

        CASES:
        ======

        Case 1: **Disjoint** (d ≥ R + r)
        - Circles do not overlap
        - Overlap area = 0
        - Crescent area = πR² (full outer circle)
        - Perimeter = 2πR

        Case 2: **One Inside Other** (d ≤ R - r)
        - Inner circle completely inside outer circle
        - Overlap area = πr² (full inner circle)
        - Crescent area = π(R² - r²) (annulus)
        - Perimeter = 2πR + 2πr (both boundaries)

        Case 3: **Intersection** (R - r < d < R + r)
        - True crescent/lune shape
        - Overlap area = A_∩ (lens between circles)
        - Crescent area = πR² - A_∩
        - Perimeter = (2π - α)R + βr

        OVERLAP AREA (LENS):
        ====================

        For two intersecting circles with radii R, r and center distance d:

        Using the **Cosine Rule** in the triangle formed by the two centers
        and an intersection point:

        **Half-angles at each center**:
        - α = 2·arccos((d² + R² - r²)/(2dR))  [angle at outer center]
        - β = 2·arccos((d² + r² - R²)/(2dr))  [angle at inner center]

        **Circular Segment Areas**:
        - Segment from outer circle: A₁ = (R²/2)(α - sin α)
        - Segment from inner circle: A₂ = (r²/2)(β - sin β)

        **Total Overlap**:
        A_∩ = A₁ + A₂ = (R²/2)(α - sin α) + (r²/2)(β - sin β)

        Alternative (Heron-like formula):
        A_∩ can also be expressed using:
        A_∩ = R²·arccos((d²+R²-r²)/(2dR)) + r²·arccos((d²+r²-R²)/(2dr))
             - (1/2)√[(-d+R+r)(d+R-r)(d-R+r)(d+R+r)]

        This form uses Heron's formula for the **kite-shaped quadrilateral**
        formed by the two centers and the two intersection points.

        CRESCENT AREA:
        ==============

        A_crescent = πR² - A_∩

        For symmetric case (d = 0, concentric):
        A_crescent = π(R² - r²) = πw(2r + w) where w = R - r

        PERIMETER:
        ==========

        The crescent boundary consists of:
        - **Outer arc**: Major arc on outer circle = (2π - α)R
        - **Inner arc**: Minor arc on inner circle = βr

        P_crescent = (2π - α)R + βr

        Where α, β are the full angles (in radians) as derived above.

        HERMETIC NOTE - THE LUNAR CRESCENT:
        ====================================
        The crescent is the **SYMBOL OF THE MOON**, **CYCLICAL TIME**, and
        **DIVINE FEMININE POWER**. It represents **GROWTH**, **WAXING AND WANING**,
        and the **RHYTHM OF NATURE**.

        In Symbolism:
        - **Waxing Moon**: Growth, increase, fertility, new beginnings
        - **Waning Moon**: Decrease, reflection, rest, releasing
        - **Horns of the Crescent**: Receptivity, capturing light/energy
        - **Islamic Crescent**: Star and crescent, faith, celestial guidance

        In Sacred Traditions:
        - **Lunar Goddesses**: Diana, Artemis, Selene, Hecate
        - **Virgin Mary**: Often depicted on a crescent moon
        - **Osiris**: Associated with lunar cycles, death and rebirth
        - **Isis**: Horns of the cow goddess form crescent

        Mathematical Properties:
        ------------------------
        1. **Lune of Hippocrates**: Special lunes can have area equal to a triangle
           (Famous ancient squaring problem)
        2. **Area-angle relation**: Crescent area depends on α, β derived from
           cosine law
        3. **Symmetry**: Crescent is symmetric about the line joining centers

        In Nature & Culture:
        • **Moon Phases**: Waxing/waning crescent, gibbous phases
        • **Dune Crescents**: Barchan dunes in desert landscapes
        • **Fingernails**: Lunula (white crescent at nail base)
        • **Scythes & Sickles**: Tools for harvest, reaping time
        • **Horns**: Bull, ram, crescent as strength and power

        In Astronomy:
        - **Phases of Venus**: Galileo observed crescent Venus (heliocentric proof)
        - **Eclipses**: Partial solar eclipses show crescent sun
        - **Thin Crescent**: New moon visible just after sunset
        """
        outer = self.properties["outer_radius"].value
        inner = self.properties["inner_radius"].value
        offset = self.properties["offset"].value

        self.properties["outer_diameter"].value = outer * 2 if outer else None
        self.properties["inner_diameter"].value = inner * 2 if inner else None

        if not self._has_valid_geometry(outer, inner, offset):
            self.properties["intersection_area"].value = None
            self.properties["crescent_area"].value = None
            self.properties["perimeter"].value = None
            return

        assert outer is not None and inner is not None and offset is not None
        overlap = self._circle_overlap_area(outer, inner, offset)
        crescent_area = math.pi * outer * outer - overlap
        perimeter = self._crescent_perimeter(outer, inner, offset)

        self.properties["intersection_area"].value = overlap
        self.properties["crescent_area"].value = crescent_area
        self.properties["perimeter"].value = perimeter

    @staticmethod
    def _has_valid_geometry(outer, inner, offset) -> bool:  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        if outer is None or inner is None or offset is None:
            return False
        if outer <= inner:
            return False
        return CrescentShape._is_valid_offset(outer, inner, offset)  # type: ignore[reportUnknownArgumentType]

    @staticmethod
    def _is_valid_offset(outer: float, inner: float, offset: float) -> bool:
        # Allow any non-negative offset provided circles are valid
        return offset >= 0

    @staticmethod
    def _circle_overlap_area(r1: float, r2: float, d: float) -> float:
        # Case 1: Disjoint (d >= r1 + r2) -> No overlap
        if d >= r1 + r2:
            return 0.0
        
        # Case 2: One inside other (d <= |r1 - r2|) -> Overlap is area of smaller circle
        # Note: We enforce r1 > r2 in _has_valid_geometry, so r2 is smaller.
        if d <= abs(r1 - r2):
            return math.pi * min(r1, r2) ** 2

        # Case 3: Intersection
        alpha = math.acos((d * d + r1 * r1 - r2 * r2) / (2 * d * r1)) * 2
        beta = math.acos((d * d + r2 * r2 - r1 * r1) / (2 * d * r2)) * 2
        area1 = 0.5 * r1 * r1 * (alpha - math.sin(alpha))
        area2 = 0.5 * r2 * r2 * (beta - math.sin(beta))
        return area1 + area2

    @staticmethod
    def _crescent_perimeter(r1: float, r2: float, d: float) -> float:
        # Case 1: Disjoint (d >= r1 + r2) -> Inner circle is completely outside Outer
        # Result is just the Outer circle (minus nothing).
        if d >= r1 + r2:
            return 2 * math.pi * r1
            
        # Case 2: One inside other (d <= |r1 - r2|) -> Hole inside Outer
        # Result is Outer + Inner perimeters (Annulus-like)
        if d <= abs(r1 - r2):
            return 2 * math.pi * r1 + 2 * math.pi * r2
            
        # Case 3: Intersection
        # Arc of Outer (major) + Arc of Inner (minor)
        alpha = math.acos((d * d + r1 * r1 - r2 * r2) / (2 * d * r1)) * 2
        beta = math.acos((d * d + r2 * r2 - r1 * r1) / (2 * d * r2)) * 2
        outer_arc = (2 * math.pi - alpha) * r1
        inner_arc = beta * r2
        return outer_arc + inner_arc

    def get_drawing_instructions(self) -> Dict:
        """
        Retrieve drawing instructions logic.
        
        Returns:
            Result of get_drawing_instructions operation.
        """
        outer = self.properties["outer_radius"].value
        inner = self.properties["inner_radius"].value
        offset = self.properties["offset"].value
        if outer is None:
            return {"type": "empty"}

        if inner is None or offset is None:
             # Just draw outer circle
            return {
                "type": "composite",
                "primitives": [
                    {
                        "shape": "circle",
                        "center": (0.0, 0.0),
                        "radius": outer,
                        "pen": {"color": (59, 130, 246, 255), "width": 2.4},
                        "brush": {"color": (147, 197, 253, 90)},
                    }
                ]
            }

        # Define Outer Circle
        outer_circle = {
            "shape": "circle",
            "center": (0.0, 0.0),
            "radius": outer,
            "pen": {"color": (59, 130, 246, 255), "width": 0.0}, # Pen handled by boolean container
            "brush": {"color": (0, 0, 0, 255), "enabled": True}, # Fill required for path op
        }
        
        # Define Inner Circle (The Cutter)
        inner_circle = {
            "shape": "circle",
            "center": (offset, 0.0),
            "radius": inner,
            "pen": {"color": (0, 0, 0, 255), "width": 0.0},
            "brush": {"color": (0, 0, 0, 255), "enabled": True},
        }

        # The result (Crescent)
        crescent = {
            "type": "boolean",
            "operation": "difference",
            "shape_a": outer_circle,
            "shape_b": inner_circle,
            "pen": {"color": (59, 130, 246, 255), "width": 2.4}, # Blue Border
            "brush": {"color": (59, 130, 246, 120), "enabled": True}, # Blue Fill
        }

        primitives = [crescent]
        
        # Optional: Dashed outline of the cutter for reference?
        # User requested "The Crescent", implies just the result mostly.
        # But seeing the invisible inner circle boundary is helpful.
        primitives.append({
             "shape": "circle",
             "center": (offset, 0.0),
             "radius": inner,
             "pen": {"color": (15, 23, 42, 100), "width": 1.0, "dashed": True},
             "brush": {"enabled": False}
        })

        return {
            "type": "composite",
            "primitives": primitives,
        }

    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        """
        Retrieve label positions logic.
        
        Returns:
            Result of get_label_positions operation.
        """
        labels: List[Tuple[str, float, float]] = []
        outer = self.properties["outer_radius"].value
        inner = self.properties["inner_radius"].value
        offset = self.properties["offset"].value
        if outer is None:
            return labels

        labels.append((self._fmt("R", outer), outer * 0.65, 0.1))
        if inner is not None:
            labels.append((self._fmt("r", inner), (offset or 0) + inner * 0.4, 0.1))
        if offset is not None:
            labels.append((self._fmt("d", offset), offset / 2, -0.25))

        crescent_area = self.properties["crescent_area"].value
        if crescent_area is not None:
            labels.append((self._fmt("A", crescent_area), -outer * 0.3, 0.2))

        return labels

    @staticmethod
    def _fmt(symbol: str, value: float) -> str:
        return f"{symbol} = {value:.4f}".rstrip("0").rstrip(".")