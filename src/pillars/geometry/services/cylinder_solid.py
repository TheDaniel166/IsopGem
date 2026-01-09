"""Cylinder 3D Solid Service."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, cast

from ..shared.solid_payload import Face, SolidLabel, SolidPayload
from .solid_geometry import Vec3, edges_from_faces
from .solid_property import SolidProperty


@dataclass(frozen=True)
class CylinderMetrics:
    """
    Cylinder Metrics class definition.
    
    """
    radius: float
    height: float
    circumference: float # [NEW]
    base_area: float
    lateral_area: float
    surface_area: float
    volume: float


@dataclass(frozen=True)
class CylinderResult:
    """
    Cylinder Result class definition.
    
    """
    payload: SolidPayload
    metrics: CylinderMetrics


class CylinderSolidService:
    """Generates the geometry for a Cylinder."""

    @staticmethod
    def build(radius: float = 1.0, height: float = 2.0, segments: int = 32) -> CylinderResult:
        """
        Build logic.
        
        Args:
            radius: Description of radius.
            height: Description of height.
            segments: Description of segments.
        
        Returns:
            Result of build operation.
        """
        if radius <= 0 or height <= 0:
            raise ValueError("Radius and Height must be positive")

        metrics = CylinderSolidService.compute_metrics(radius, height)
        
        vertices: List[Vec3] = []
        faces: List[Tuple[int, ...]] = []
        
        # Center of bottom cap
        vertices.append((0.0, 0.0, 0.0)) # Index 0
        # Bottom ring
        for i in range(segments):
            angle = i * 2 * math.pi / segments
            vertices.append((radius * math.cos(angle), radius * math.sin(angle), 0.0))
            
        # Center of top cap
        vertices.append((0.0, 0.0, height)) # Index segments + 1
        # Top ring
        for i in range(segments):
            angle = i * 2 * math.pi / segments
            vertices.append((radius * math.cos(angle), radius * math.sin(angle), height))
            
        # Bottom Cap Faces
        for i in range(segments):
            faces.append((0, (i % segments) + 1, ((i + 1) % segments) + 1))
            
        # Top Cap Faces
        top_offset = segments + 1
        for i in range(segments):
            faces.append((top_offset, top_offset + ((i + 1) % segments) + 1, top_offset + (i % segments) + 1))
            
        # Side Faces (Quads)
        for i in range(segments):
            v1 = i + 1
            v2 = ((i + 1) % segments) + 1
            v3 = v2 + top_offset
            v4 = v1 + top_offset
            faces.append((v1, v2, v3, v4))
            
        edges = edges_from_faces(faces)
        
        payload = SolidPayload(
            vertices=vertices,
            edges=edges,
            faces=cast(List[Face], faces),
            labels=[
                SolidLabel(text=f"r={radius:.2f}, h={height:.2f}", position=(0, 0, height * 1.05))
            ],
            metadata={
                'radius': radius,
                'height': height,
                'surface_area': metrics.surface_area,
                'volume': metrics.volume
            },
            suggested_scale=max(radius * 2, height),
        )
        return CylinderResult(payload=payload, metrics=metrics)

    @staticmethod
    def compute_metrics(r: float, h: float) -> CylinderMetrics:
        """
        Compute all geometric metrics for a right circular cylinder.

        DEFINITION:
        ===========
        A cylinder is a prism with circular bases—a solid formed by extruding
        a circle along a perpendicular axis.

        Parameters:
        - r: Base radius
        - h: Height (distance between parallel circular bases)

        CORE FORMULAS & DERIVATIONS:
        ==============================

        Volume: V = πr²h
        ----------------
        Volume = base area × height

        Base is a circle: A_base = πr²
        V = A_base × h = πr²h ✓

        Alternative derivation (cylindrical shells):
        Integrate concentric cylindrical shells from ρ=0 to ρ=r:
        dV = 2πρh dρ
        V = ∫₀ʳ 2πρh dρ = 2πh [ρ²/2]₀ʳ = πr²h ✓

        Lateral Surface Area: A_L = 2πrh
        ----------------------------------
        The lateral (curved) surface \"unrolls\" into a RECTANGLE!

        When you cut the cylinder along a generator (vertical line) and unroll:
        - Width = circumference of base = 2πr\n        - Height = h
        - Area = width × height = 2πrh ✓

        Total Surface Area: A = 2πr² + 2πrh = 2πr(r + h)
        --------------------------------------------------
        Sum of two circular bases + lateral surface:
        A = 2 × πr² + 2πrh = 2πr(r + h) ✓

        AHA MOMENT #1: THE CIRCULAR PRISM\n        ==================================\n        The cylinder is a PRISM with a circular base!\n\n        All prism formulas apply:\n        - Volume = base area × height\n        - Lateral area = perimeter × height\n        - For cylinder: base = circle, perimeter = 2πr\n\n        The cylinder is the LIMIT of regular n-gonal prisms as n → ∞:\n        - Triangle prism (n=3)\n        - Square prism = cube (n=4)\n        - Hexagon prism (n=6)\n        - ...\n        - Circle \"prism\" = cylinder (n→∞)\n\n        As polygon sides increase, the prism approaches cylindrical form.\n        The cylinder is the CONTINUOUS LIMIT of discrete polygonal prisms.\n\n        This is why:\n        - π appears (limiting perimeter of n-gon inscribed in circle)\n        - Formulas are \"smooth\" (no vertices, edges—just curves)\n        - Cylinder has rotational symmetry (infinite-fold)\n\n        The cylinder is the PERFECT PRISM—the prism of infinite symmetry.\n\n        AHA MOMENT #2: ARCHIMEDES' CYLINDER-SPHERE-CONE RELATIONSHIP\n        ==============================================================\n        Archimedes discovered the beautiful 3:2:1 volume ratio!\n\n        Consider:\n        - Cylinder: radius r, height 2r\n        - Sphere: radius r (inscribed, touching top/bottom/sides)\n        - Cone: radius r, height 2r (same dimensions as cylinder)\n\n        Volumes:\n        - V_cylinder = πr² × 2r = 2πr³\n        - V_sphere = (4/3)πr³\n        - V_cone = (1/3)πr² × 2r = (2/3)πr³\n\n        Ratio:\n        V_cylinder : V_sphere : V_cone = 2πr³ : (4/3)πr³ : (2/3)πr³\n                                        = 6 : 4 : 2\n                                        = 3 : 2 : 1 ✓\n\n        Archimedes considered this his GREATEST discovery! He requested\n        a cylinder with inscribed sphere be carved on his tombstone.\n\n        The 3:2:1 ratio reveals:\n        - Cylinder = full prism volume (baseline)\n        - Sphere = 2/3 of cylinder (nature's optimal packing)\n        - Cone = 1/3 of cylinder (pyramid taper factor)\n\n        This ratio appears in:\n        - Classical architecture (column proportions)\n        - Engineering (pressure vessels)\n        - Nature (seed pods, flower buds)\n\n        HERMETIC NOTE - THE PILLAR OF STABILITY:\n        =========================================\n        The cylinder represents STABILITY, AXIS, and STRUCTURED FLOW:\n\n        - **Vertical Axis**: The world axis (axis mundi)\n        - **Circular Base**: Eternal return, cyclical time\n        - **Constant Radius**: Unchanging essence through time/space\n        - **No Apex**: No hierarchy, all heights equivalent\n\n        Symbolism:\n        - **Architectural**: Columns supporting temples (Doric, Ionic, Corinthian)\n        - **Cosmic**: The pillar of heaven, the world tree trunk\n        - **Alchemical**: The vessel (retort, alembic) containing transformation\n        - **Spiritual**: The spine (sushumna nadi), central channel of energy\n\n        The cylinder is the geometry of UNDIMINISHED TRANSMISSION:\n        - Light passing through cylindrical fiber → no divergence\n        - Water flowing through pipe → constant cross-section\n        - Energy rising through spine → chakras aligned on axis\n\n        Unlike the cone (diverging) or sphere (converging), the cylinder\n        maintains CONSTANT FORM through its length. It is the shape of\n        PRESERVATION and CHANNELING.\n\n        Physical Manifestations:\n        - **Structural**: Columns, pillars, piles (bearing vertical loads)\n        - **Fluid**: Pipes, tubes, vessels (containing and directing flow)\n        - **Biological**: Tree trunks, bones, blood vessels\n        - **Mechanical**: Shafts, axles, pistons (rotational/linear motion)\n\n        The cylinder is the SPINE OF GEOMETRY—the upright axis upon which\n        all else rotates and flows.\n\n        KEY RATIOS AND PROPERTIES:\n        ==========================\n        - Surface-to-volume ratio: A/V = 2(r+h)/(r²h)\n        - Minimized when h = 2r (golden proportion for cylinders)\n        - Optimal can: h = 2r (minimum material for given volume)\n        - Moment of inertia (solid): I = (1/2)Mr² (about central axis)\n        - Circumradius: R = √(r² + h²/4) (sphere through base edge and midheight)
        """
        base_area = math.pi * (r ** 2)
        lateral_area = 2 * math.pi * r * h
        circumference = 2 * math.pi * r
        return CylinderMetrics(
            radius=r,
            height=h,
            circumference=circumference,
            base_area=base_area,
            lateral_area=lateral_area,
            surface_area=2 * base_area + lateral_area,
            volume=base_area * h
        )


class CylinderSolidCalculator:
    """Bidirectional calculator for the 3D Cylinder."""

    def __init__(self, radius: float = 1.0, height: float = 2.0):
        """
          init   logic.
        
        Args:
            radius: Description of radius.
            height: Description of height.
        
        """
        self._properties = {
            'radius': SolidProperty('Radius (r)', 'radius', 'units', radius),
            'height': SolidProperty('Height (h)', 'height', 'units', height),
            'circumference': SolidProperty('Circumference (C)', 'circumference', 'units', 0.0, editable=True),
            'base_area': SolidProperty('Base Area (B)', 'base_area', 'units²', 0.0, editable=True),
            'lateral_area': SolidProperty('Lateral Area (L)', 'lateral_area', 'units²', 0.0, editable=True),
            'surface_area': SolidProperty('Surface Area (A)', 'surface_area', 'units²', 0.0, editable=True),
            'volume': SolidProperty('Volume (V)', 'volume', 'units³', 0.0, editable=True),
        }
        self._result: Optional[CylinderResult] = None
        self._recalculate()

    def properties(self) -> List[SolidProperty]:
        """
        Properties logic.
        
        Returns:
            Result of properties operation.
        """
        return list(self._properties.values())

    def set_property(self, key: str, value: Optional[float]) -> bool:
        """
        Configure property logic.
        
        Args:
            key: Description of key.
            value: Description of value.
        
        Returns:
            Result of set_property operation.
        """
        if value is not None and value <= 0:
            return False
            
        prop = self._properties.get(key)
        if not prop:
            return False
            
        r = self._properties['radius'].value
        h = self._properties['height'].value
        
        if key == 'radius':
            r = value
        elif key == 'height':
            h = value
        elif key == 'circumference':
            if value is None:
                return False
            r = value / (2 * math.pi)
        elif key == 'base_area':
            r = math.sqrt(value / math.pi)
        elif key == 'lateral_area':
            if value is None:
                return False
            # L = 2*pi*r*h. Solve for h (keep r) or r (keep h)?
            # Prioritize solving for height if r is set.
            if r and r > 0:
                h = value / (2 * math.pi * r)
            elif h and h > 0:
                r = value / (2 * math.pi * h)
        elif key == 'surface_area':
            if value is None:
                return False
            # A = 2*pi*r*(r+h). 
            # Solve for r (quadratic) or h (linear).
            # If h is known/fixed, solve for r?
            # Let's solve for r if h is 0 or we just want to scale r.
            # But usually changing Surface Area implies scaling the whole object or changing one dim.
            
            # Try solving for h if r is valid
            if r and r > 0:
                # A = 2*pi*r^2 + 2*pi*r*h
                # 2*pi*r*h = A - 2*pi*r^2
                # h = (A - 2*pi*r^2) / (2*pi*r)
                numerator = value - 2 * math.pi * r**2
                if numerator > 0:
                    h = numerator / (2 * math.pi * r)
                else:
                    return False
            else:
                # Solve for r (assuming h is fixed? or h scales?)
                # 2*pi*r^2 + 2*pi*h*r - A = 0
                # Quadratic: a=2pi, b=2pi*h, c=-A
                if h is None or h <= 0:
                    return False
                a = 2 * math.pi
                b = 2 * math.pi * h
                c = -value
                
                delta = b**2 - 4*a*c
                if delta >= 0:
                    r = (-b + math.sqrt(delta)) / (2 * a)
                else:
                    return False

        elif key == 'volume':
            # Solve for height keeping radius constant
            if r and r > 0:
                h = value / (math.pi * r**2)
            elif h and h > 0:
                 r = math.sqrt(value / (math.pi * h))
        
        if r is not None and h is not None and r > 0 and h > 0:
            self._properties['radius'].value = r
            self._properties['height'].value = h
            self._recalculate()
            return True
            
        return False

    def _recalculate(self):
        r = self._properties['radius'].value
        h = self._properties['height'].value
        if r is None or h is None:
            return
            
        metrics = CylinderSolidService.compute_metrics(r, h)
        self._properties['circumference'].value = metrics.circumference
        self._properties['base_area'].value = metrics.base_area
        self._properties['lateral_area'].value = metrics.lateral_area
        self._properties['surface_area'].value = metrics.surface_area
        self._properties['volume'].value = metrics.volume
        
        self._result = CylinderSolidService.build(r, h)

    def clear(self):
        """
        Clear logic.
        
        """
        for p in self._properties.values():
            p.value = None
        self._result = None

    def payload(self) -> Optional[SolidPayload]:
        """
        Payload logic.
        
        Returns:
            Result of payload operation.
        """
        return self._result.payload if self._result else None

    def metadata(self) -> dict[str, float]:
        """
        Metadata logic.
        
        Returns:
            Result of metadata operation.
        """
        if not self._result:
            return {}
        return cast(dict[str, float], self._result.payload.metadata)

    def metrics(self) -> Optional[CylinderMetrics]:
        """
        Metrics logic.
        
        Returns:
            Result of metrics operation.
        """
        return self._result.metrics if self._result else None