"""Vault of Hestia sacred geometry service."""
import math
from typing import Dict, List, Tuple

from .base_shape import GeometricShape, ShapeProperty


class VaultOfHestiaShape(GeometricShape):
    """
    The Vault of Hestia: A Square containing an Inscribed Isosceles Triangle,
    containing an Incircle.
    
    Geometric Significance:
    - The semi-perimeter of the triangle is s * Phi.
    - The inradius of the circle is s / (2 * Phi).
    """

    @property
    def name(self) -> str:
        """
        Name logic.
        
        Returns:
            Result of name operation.
        """
        return "Vault of Hestia"

    @property
    def description(self) -> str:
        """
        Description logic.
        
        Returns:
            Result of description operation.
        """
        return "Square holding an Isosceles Triangle and its Incircle, generating the Golden Ratio."

    @property
    def calculation_hint(self) -> str:
        """
        Calculation hint logic.
        
        Returns:
            Result of calculation_hint operation.
        """
        return "Enter the Side Length (s) of the square."

    def _init_properties(self):
        self.properties = {
            "side_length": ShapeProperty(
                name="Side Length (s)",
                key="side_length",
                unit="units",
                default=10.0,
                formula=r"s",
            ),
            "triangle_leg": ShapeProperty(
                name="Triangle Leg",
                key="triangle_leg",
                unit="units",
                readonly=False,
                formula=r"\ell = s\tfrac{\sqrt{5}}{2}",
            ),
            "inradius": ShapeProperty(
                name="Circle Radius (r)",
                key="inradius",
                unit="units",
                readonly=False,
                formula=r"r = \tfrac{s}{2\varphi}",
            ),
            "phi_check": ShapeProperty(
                name="Phi Check (s/2r)",
                key="phi_check",
                unit="",
                readonly=True,
                precision=6,
                formula=r"\tfrac{s}{2r} = \varphi",
            ),
            "triangle_area": ShapeProperty(
                name="Triangle Area",
                key="triangle_area",
                unit="units²",
                readonly=False,
                formula=r"A_{\triangle} = \tfrac{s^2}{2}",
            ),
            "circle_area": ShapeProperty(
                name="Circle Area",
                key="circle_area",
                unit="units²",
                readonly=False,
                formula=r"A_{\circ} = \pi r^2",
            ),
            "hestia_ratio": ShapeProperty(
                name="Hestia Ratio (A_circ/A_sq)",
                key="hestia_ratio",
                unit="",
                readonly=True,
                precision=6,
                formula=r"\tfrac{\pi r^2}{s^2}",
            ),
            "triangle_perimeter": ShapeProperty(
                name="Triangle Perimeter",
                key="triangle_perimeter",
                unit="units",
                readonly=True,
                formula=r"P_{\triangle} = 2\ell + s",
            ),
            "triangle_semi_perimeter": ShapeProperty(
                name="Triangle Semi-Perimeter (s*Phi)",
                key="triangle_semi_perimeter",
                unit="units",
                readonly=True,
                formula=r"s_p = \tfrac{P_{\triangle}}{2} = s\varphi",
            ),
            "circumradius": ShapeProperty(
                name="Triangle Circumradius (R)",
                key="circumradius",
                unit="units",
                readonly=False, # Editable
                formula=r"R = \tfrac{5}{8}s",
            ),
            "square_diagonal": ShapeProperty(
                name="Square Diagonal",
                key="square_diagonal",
                unit="units",
                readonly=False, # Editable
                formula=r"d = s\sqrt{2}",
            ),
            "base_angle": ShapeProperty(
                name="Base Angle",
                key="base_angle",
                unit="deg",
                readonly=True,
                formula=r"\alpha = \arctan 2",
            ),
            "void_area": ShapeProperty(
                name="Void Area (Sq - Circ)",
                key="void_area",
                unit="units²",
                readonly=True,
                formula=r"A_{void} = s^2 - \pi r^2",
            ),
            "circle_diameter": ShapeProperty(
                name="Circle Diameter (d)",
                key="circle_diameter",
                unit="units",
                readonly=False,
                formula=r"d = 2r",
            ),
            "circle_circumference": ShapeProperty(
                name="Circle Circumference",
                key="circle_circumference",
                unit="units",
                readonly=False,
                formula=r"C = 2\pi r",
            ),
            "square_area": ShapeProperty(
                name="Square Area",
                key="square_area",
                unit="units²",
                readonly=False,
                formula=r"A_{sq} = s^2",
            ),
            "area_sq_minus_tri": ShapeProperty(
                name="Area (Square - Triangle)",
                key="area_sq_minus_tri",
                unit="units²",
                readonly=True,
                formula=r"A_{sq-\triangle} = s^2 - \tfrac{s^2}{2}",
            ),
            "area_tri_minus_circ": ShapeProperty(
                name="Area (Triangle - Circle)",
                key="area_tri_minus_circ",
                unit="units²",
                readonly=True,
                formula=r"A_{\triangle-\circ} = \tfrac{s^2}{2} - \pi r^2",
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

        # Constants
        phi = (1 + math.sqrt(5)) / 2

        if property_key == "side_length":
            self.properties["side_length"].value = value
            self._update_metrics()
            return True
        
        elif property_key == "triangle_leg":
            # leg = s * sqrt(5) / 2  =>  s = leg * 2 / sqrt(5)
            s = value * 2 / math.sqrt(5)
            self.properties["side_length"].value = s
            self._update_metrics()
            return True
            
        elif property_key == "inradius":
            # r = s / (2 * phi)  =>  s = r * 2 * phi
            s = value * 2 * phi
            self.properties["side_length"].value = s
            self._update_metrics()
            return True
        
        elif property_key == "triangle_area":
            # Area = s^2 / 2  =>  s = sqrt(2 * Area)
            s = math.sqrt(2 * value)
            self.properties["side_length"].value = s
            self._update_metrics()
            return True
            
        elif property_key == "circle_area":
            # Area = pi * r^2  =>  r = sqrt(Area / pi)
            r = math.sqrt(value / math.pi)
            # s = r * 2 * phi
            s = r * 2 * phi
            self.properties["side_length"].value = s
            self._update_metrics()
            return True

        elif property_key == "circumradius":
            # R = (5/8) * s => s = R * (8/5)
            s = value * 8 / 5
            self.properties["side_length"].value = s
            self._update_metrics()
            return True

        elif property_key == "square_diagonal":
            # d = s * sqrt(2) => s = d / sqrt(2)
            s = value / math.sqrt(2)
            self.properties["side_length"].value = s
            self._update_metrics()
            return True

        elif property_key == "circle_diameter":
            # d = 2r => r = d/2.  s = r * 2 * phi
            r = value / 2
            s = r * 2 * phi
            self.properties["side_length"].value = s
            self._update_metrics()
            return True

        elif property_key == "circle_circumference":
            # C = 2 * pi * r => r = C / (2 * pi)
            r = value / (2 * math.pi)
            s = r * 2 * phi
            self.properties["side_length"].value = s
            self._update_metrics()
            return True

        elif property_key == "square_area":
            # A = s^2 => s = sqrt(A)
            s = math.sqrt(value)
            self.properties["side_length"].value = s
            self._update_metrics()
            return True

        return False

    def _update_metrics(self):
        """
        Compute all geometric metrics for the Vault of Hestia from side length.

        THE VAULT OF HESTIA - CORE FORMULAS & DERIVATIONS:
        ===================================================

        Construction:
        - Square with side s
        - Isosceles triangle inscribed: base = s (bottom of square), apex at top center
        - Circle inscribed within the triangle

        This configuration GENERATES the Golden Ratio φ from pure geometry!


        TRIANGLE LEG LENGTH: ℓ = s√5/2
        ====================================

        The isosceles triangle has:
        - Base = s (full width of square)
        - Height = s (full height of square)
        - Apex at (0, s), base endpoints at (±s/2, 0)

        By Pythagorean theorem on half the triangle:
            ℓ² = (s/2)² + s²
            ℓ² = s²/4 + s²
            ℓ² = s²/4 + 4s²/4
            ℓ² = 5s²/4
            ℓ = s√5/2

        AHA MOMENT #1: √5 appears naturally!
        This is THE square root that generates φ = (1 + √5)/2


        TRIANGLE AREA: A_△ = s²/2
        =========================

        Simple base × height formula:
            A = (1/2) × base × height
            A = (1/2) × s × s
            A = s²/2


        TRIANGLE PERIMETER: P = s√5 + s = s(√5 + 1)
        ============================================

            P = 2ℓ + base
            P = 2(s√5/2) + s
            P = s√5 + s
            P = s(√5 + 1)

        AHA MOMENT #2: The perimeter is s times (√5 + 1)!


        TRIANGLE SEMI-PERIMETER: s_p = s·φ
        ===================================

            s_p = P/2
            s_p = s(√5 + 1)/2

        But wait! φ = (1 + √5)/2, so:

            s_p = s·φ

        AHA MOMENT #3: THE GOLDEN RATIO EMERGES FROM THE GEOMETRY!
        The semi-perimeter is exactly the side length TIMES PHI!
        This is not a coincidence - this is the VAULT OF HESTIA generating φ!


        INCIRCLE RADIUS: r = s/(2φ)
        ============================

        For any triangle:
            r = Area / semi-perimeter

        Therefore:
            r = (s²/2) / (s·φ)
            r = s² / (2s·φ)
            r = s / (2φ)

        AHA MOMENT #4: The inradius relates to the square by the INVERSE of φ!

        We can verify this relationship:
            2r·φ = s
            φ = s/(2r)

        This is the "Phi Check" - if we measure s and r, their ratio MUST be φ!


        CIRCUMRADIUS: R = 5s/8
        =======================

        For isosceles triangle with legs a and base b:
            R = a²/√(4a² - b²)

        With a = s√5/2 and b = s:
            a² = 5s²/4
            4a² = 5s²
            4a² - b² = 5s² - s² = 4s²
            √(4a² - b²) = 2s

        Therefore:
            R = (5s²/4)/(2s)
            R = 5s²/(8s)
            R = 5s/8

        Verification using R = abc/(4A):
            R = (s√5/2)·(s√5/2)·s / (4·s²/2)
            R = (5s³/4) / (2s²)
            R = 5s/8 ✓

        AHA MOMENT #5: The ratio R:r reveals golden structure!
            R/r = (5s/8) / (s/(2φ))
            R/r = (5s/8) × (2φ/s)
            R/r = 10φ/8
            R/r = 5φ/4

        The circumradius to inradius ratio is 5φ/4!
        (For s=10: R/r ≈ 2.024 = 5×1.618.../4)


        BASE ANGLE: α = arctan(2)
        ==========================

        The base angle (at corners of isosceles triangle):
            tan(α) = height / (base/2)
            tan(α) = s / (s/2)
            tan(α) = 2
            α = arctan(2) ≈ 63.435°

        AHA MOMENT #6: This angle encodes the 2:1 ratio of the construction!

        The apex angle β = 180° - 2α ≈ 53.13°
        This is very close to the Great Pyramid angle (≈51.84°)!


        SQUARE DIAGONAL: d = s√2
        =========================

        Standard square diagonal:
            d² = s² + s²
            d = s√2


        HESTIA RATIO: A_○/A_□ = π/(4φ²)
        ================================

        Circle area:
            A_○ = πr²
            A_○ = π(s/(2φ))²
            A_○ = πs²/(4φ²)

        Square area:
            A_□ = s²

        Ratio:
            A_○/A_□ = πs²/(4φ²s²)
            A_○/A_□ = π/(4φ²)

        Since φ² = φ + 1 = (3 + √5)/2:
            4φ² = 2(3 + √5) = 6 + 2√5

        Therefore:
            Hestia Ratio = π/(6 + 2√5) ≈ 0.19208...

        AHA MOMENT #7: The ratio of circle to square area is π divided by
        the golden ratio squared times 4! This is a UNIVERSAL CONSTANT of
        this sacred geometry - independent of size!


        VOID AREA: A_void = s² - πr² = s²(1 - π/(4φ²))
        ===============================================

        This represents the "space" between material (circle) and container (square).
        The void is approximately 80.79% of the square - the MAJORITY of the structure!

        In esoteric terms: Hestia (hearth fire = circle) occupies ~19.2% of the
        sacred enclosure (square), leaving ~80.8% as sacred emptiness.


        HERMETIC SIGNIFICANCE - THE HEARTH OF CREATION:
        ===============================================

        Hestia is the Greek goddess of the hearth, home, and sacred fire.
        She represents the CENTER that holds - the unmoved mover, the axis mundi.

        This geometry reveals:

        1. **Phi Generation**: Unlike other constructions that USE φ, this one
           GENERATES it from first principles (square + inscribed triangle).

        2. **The 2:1 Ratio**: The base angle arctan(2) encodes the fundamental
           duality resolved into unity (triangle apex).

        3. **Sacred Proportions**: The semi-perimeter being s·φ shows that
           the "journey around" the triangle is golden-scaled to the foundation.

        4. **Inversion Symmetry**: r = s/(2φ) means the radius relates to the
           side by inverse-phi, while the perimeter relates by direct-phi.
           This is the hermetic principle: "As above, so below" - inverted yet proportional.

        5. **The Void Predominance**: ~80% void space represents the Taoist principle
           that usefulness comes from emptiness (the space of the hearth, not the stones).

        6. **Five Elements**: √5 in the leg length connects to the five Platonic solids,
           the five elements, the pentagram - the human microcosm.

        7. **Circle-Square Unity**: The impossible "squaring the circle" is here
           achieved SYMBOLICALLY through φ mediation - the circle relates to the
           square through the divine proportion.

        The Vault of Hestia is a **PHI GENERATOR** - a geometric proof that the
        golden ratio exists as a necessary consequence of square-triangle-circle unity.
        """
        s = self.properties["side_length"].value
        if not s:
            return

        # Constants
        phi = (1 + math.sqrt(5)) / 2

        # Triangle (Base=s, Height=s)
        # Leg = sqrt((s/2)^2 + s^2) = s * sqrt(1.25) = s * sqrt(5)/2
        leg = s * math.sqrt(5) / 2

        # Area = 1/2 * b * h = s^2 / 2
        tri_area = (s * s) / 2

        # Semiperimeter = s * phi
        # Inradius = Area / s_p = (s^2/2) / (s*phi) = s / (2*phi)
        r = s / (2 * phi)

        circle_area = math.pi * r * r
        square_area = s * s
        hestia_ratio = circle_area / square_area

        phi_check = s / (2 * r) if r > 0 else 0

        # New Calculations
        # Triangle Perimeter = leg + leg + base = 2*leg + s
        # leg = s * sqrt(5)/2
        tri_perimeter = (2 * leg) + s

        # Semi-Perimeter
        tri_semi_perimeter = tri_perimeter / 2

        # Circumradius (R)
        # For Isosceles Triangle with sides a, a, b (where a=leg, b=s)
        # R = a^2 / sqrt(4a^2 - b^2)
        # a^2 = (s^2 * 5) / 4
        # 4a^2 = 5s^2
        # sqrt(4a^2 - b^2) = sqrt(5s^2 - s^2) = sqrt(4s^2) = 2s
        # R = (5/4 s^2) / 2s = (5/8) * s
        circumradius = (5/8) * s

        # Square Diagonal = s * sqrt(2)
        square_diag = s * math.sqrt(2)

        # Base Angle = arctan(height / (base/2)) = arctan(s / (s/2)) = arctan(2)
        base_angle_rad = math.atan(2)
        base_angle_deg = math.degrees(base_angle_rad)

        # Void Area = Square Area - Circle Area
        void_area = square_area - circle_area

        # New Area Metrics
        # Square Area already calculated as 'square_area'

        # Circle metrics
        circ_diameter = 2 * r
        circ_circumference = 2 * math.pi * r

        # Area Differences
        area_sq_minus_tri = square_area - tri_area
        area_tri_minus_circ = tri_area - circle_area

        self.properties["triangle_leg"].value = leg
        self.properties["inradius"].value = r
        self.properties["triangle_area"].value = tri_area
        self.properties["circle_area"].value = circle_area
        self.properties["hestia_ratio"].value = hestia_ratio
        self.properties["phi_check"].value = phi_check
        
        self.properties["triangle_perimeter"].value = tri_perimeter
        self.properties["triangle_semi_perimeter"].value = tri_semi_perimeter
        self.properties["circumradius"].value = circumradius
        self.properties["square_diagonal"].value = square_diag
        self.properties["base_angle"].value = base_angle_deg
        self.properties["void_area"].value = void_area
        
        self.properties["circle_diameter"].value = circ_diameter
        self.properties["circle_circumference"].value = circ_circumference
        self.properties["square_area"].value = square_area
        self.properties["area_sq_minus_tri"].value = area_sq_minus_tri
        self.properties["area_tri_minus_circ"].value = area_tri_minus_circ

    def get_drawing_instructions(self) -> Dict:
        """
        Retrieve drawing instructions logic.
        
        Returns:
            Result of get_drawing_instructions operation.
        """
        s = self.properties["side_length"].value
        if not s:
            return {"type": "empty"}

        # Coordinate System: Center of Square at (0,0)
        # Square: x = [-s/2, s/2], y = [-s/2, s/2]
        half_s = s / 2
        
        # Square Points
        sq_p1 = (-half_s, -half_s)
        sq_p2 = (half_s, -half_s)
        sq_p3 = (half_s, half_s)
        sq_p4 = (-half_s, half_s)
        square_poly = [sq_p1, sq_p2, sq_p3, sq_p4, sq_p1]
        
        # Triangle Points (Base at bottom, Apex at top)
        # Base: (-s/2, -s/2) to (s/2, -s/2)
        # Apex: (0, s/2)
        tri_p1 = (-half_s, -half_s)
        tri_p2 = (half_s, -half_s)
        tri_p3 = (0, half_s)
        triangle_poly = [tri_p1, tri_p2, tri_p3, tri_p1]
        
        # Circle
        # Radius r
        # Center y = bottom + r = -s/2 + r
        r = self.properties["inradius"].value
        cy = -half_s + r
        
        primitives = [
            # Square (Blue)
            {
                "shape": "polyline",
                "points": square_poly,
                "pen": {"color": (59, 130, 246, 255), "width": 2.0},
            },
            # Triangle (Orange)
            {
                "shape": "polyline",
                "points": triangle_poly,
                "pen": {"color": (249, 115, 22, 255), "width": 2.0},
            },
            # Circle (Teal)
            {
                "shape": "circle",
                "center": (0, cy),
                "radius": r,
                "pen": {"color": (20, 184, 166, 255), "width": 2.0},
            }
        ]
        
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
        s = self.properties["side_length"].value
        if not s:
            return labels
            
        r = self.properties["inradius"].value
        ratio = self.properties["hestia_ratio"].value
        
        # Label s at bottom
        labels.append((f"s = {s:g}", 0, -s/2 * 1.05))
        
        # Label r at center (approx)
        cy = -s/2 + r
        if r:
            labels.append((f"r = {r:.3f}", 0, cy))
            
        # Label Ratio at top
        if ratio:
            labels.append((f"Ratio = {ratio:.5f}", 0, s/2 * 1.05))
            
        return labels