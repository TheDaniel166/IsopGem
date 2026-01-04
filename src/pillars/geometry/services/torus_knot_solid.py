"""Torus Knot solid math utilities and calculator."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ..shared.solid_payload import SolidLabel, SolidPayload
from .solid_geometry import (
    Vec3,
    vec_add,
    vec_cross,
    vec_normalize,
    vec_scale,
    edges_from_faces,
    vec_sub,
    vec_length
)
from .solid_property import SolidProperty


@dataclass(frozen=True)
class TorusKnotMetrics:
    """
    Torus Knot Metrics class definition.
    
    """
    p: int
    q: int
    major_radius: float
    minor_radius: float
    tube_radius: float
    arc_length: float
    approx_surface_area: float
    approx_volume: float


@dataclass(frozen=True)
class TorusKnotSolidResult:
    """
    Torus Knot Solid Result class definition.
    
    """
    payload: SolidPayload
    metrics: TorusKnotMetrics


@dataclass
class TorusKnotMeshConfig:
    """
    Torus Knot Mesh Config class definition.
    
    """
    tubular_segments: int = 120  # Reduced for filled rendering performance
    radial_segments: int = 10    # Reduced for filled rendering performance


class TorusKnotSolidService:
    """Generates payloads for (p,q) torus knot solids."""

    @staticmethod
    def build(
        p: int = 2,
        q: int = 3,
        major_radius: float = 3.0,
        minor_radius: float = 1.0,
        tube_radius: float = 0.4,
        config: TorusKnotMeshConfig = None
    ) -> TorusKnotSolidResult:
        """
        Build logic.
        
        Args:
            p: Description of p.
            q: Description of q.
            major_radius: Description of major_radius.
            minor_radius: Description of minor_radius.
            tube_radius: Description of tube_radius.
            config: Description of config.
        
        Returns:
            Result of build operation.
        """
        if major_radius <= 0 or minor_radius <= 0 or tube_radius <= 0:
            raise ValueError("Radii must be positive")
        if config is None:
            config = TorusKnotMeshConfig()

        metrics = TorusKnotSolidService._compute_metrics(p, q, major_radius, minor_radius, tube_radius)
        
        vertices, faces = TorusKnotSolidService._generate_mesh(p, q, major_radius, minor_radius, tube_radius, config)
        edges = edges_from_faces(faces)
        
        labels = [
            SolidLabel(text=f"P={p}, Q={q}", position=(0.0, major_radius + minor_radius + tube_radius, 0.0)),
        ]

        payload = SolidPayload(
            vertices=vertices,
            edges=edges,
            faces=faces,
            labels=labels,
            metadata={
                'p': p,
                'q': q,
                'major_radius': metrics.major_radius,
                'minor_radius': metrics.minor_radius,
                'tube_radius': metrics.tube_radius,
                'arc_length': metrics.arc_length,
                'surface_area': metrics.approx_surface_area,
                'volume': metrics.approx_volume,
            },
            suggested_scale=major_radius + minor_radius + tube_radius,
        )
        return TorusKnotSolidResult(payload=payload, metrics=metrics)

    @staticmethod
    def _compute_metrics(p: int, q: int, R: float, r: float, tube_r: float) -> TorusKnotMetrics:
        # Arc length is an integral, approximate numerically
        # L = Integral of |r'(t)| dt from 0 to 2pi
        # Simple numerical integration
        n_steps = 1000
        length = 0.0
        _dt = (2 * math.pi) / n_steps
        
        # Curve:
        # x = (R + r cos(qt)) cos(pt)
        # y = (R + r cos(qt)) sin(pt)
        # z = r sin(qt)
        
        prev_p = TorusKnotSolidService._curve_point(0, p, q, R, r)
        for i in range(1, n_steps + 1):
            t = (i / n_steps) * 2 * math.pi
            curr_p = TorusKnotSolidService._curve_point(t, p, q, R, r)
            dist = vec_length(vec_sub(curr_p, prev_p))
            length += dist
            prev_p = curr_p

        # Torus Volume ~ Length * (pi * tube_r^2)
        # Torus Area ~ Length * (2 * pi * tube_r)
        
        return TorusKnotMetrics(
            p=p,
            q=q,
            major_radius=R,
            minor_radius=r,
            tube_radius=tube_r,
            arc_length=length,
            approx_surface_area=length * (2 * math.pi * tube_r),
            approx_volume=length * (math.pi * (tube_r ** 2)),
        )

    @staticmethod
    def _curve_point(t: float, p: int, q: int, R: float, r: float) -> Vec3:
        # r_val = R + r * cos(q*t)
        r_val = R + r * math.cos(q * t)
        
        # x = r_val * cos(p*t)
        x = r_val * math.cos(p * t)
        
        # y = r_val * sin(p*t)
        y = r_val * math.sin(p * t)
        
        # z = r * sin(q*t)
        # Wait, usually z comes out of the R plane? 
        # Yes, standard torus parameterization axis is Z.
        z = r * math.sin(q * t)
        return (x, y, z)

    @staticmethod
    def _generate_mesh(p: int, q: int, R: float, r: float, tube_r: float, config: TorusKnotMeshConfig) -> Tuple[List[Vec3], List[Tuple[int, ...]]]:
        vertices = []
        faces = []
        
        segments = config.tubular_segments
        radial_seg = config.radial_segments
        
        # 1. Compute curve points & tangents using forward difference or analytical derivative
        _curve_frames = [] # List of (pos, T, N, B)
        
        # Calculate points for 0 to 2pi (inclusive to find total twist)
        total_steps = segments
        points = []
        tangents = []
        
        for i in range(total_steps + 1):
            t = (i / total_steps) * 2 * math.pi
            pos = TorusKnotSolidService._curve_point(t, p, q, R, r)
            points.append(pos)
            
            # Analytical derivative for T is better, but numerical is fine for now
            # Central difference or forward
            t_next = (t + 0.0001)
            pos_next = TorusKnotSolidService._curve_point(t_next, p, q, R, r)
            tangent = vec_normalize(vec_sub(pos_next, pos))
            tangents.append(tangent)

        # 2. Parallel Transport First Pass
        # Initial Frame at i=0
        T0 = tangents[0]
        # Robust initial Normal: use simplified heuristic or arbitrary axis
        # If T is up, use X. If T is X, use Y.
        if abs(T0[2]) < 0.9:
            up = (0, 0, 1)
        else:
            up = (1, 0, 0)
        N0 = vec_normalize(vec_cross(T0, up))
        B0 = vec_normalize(vec_cross(T0, N0))
        
        _current_N = N0
        parallel_frames = [(points[0], T0, N0, B0)]
        
        for i in range(1, total_steps + 1):
            _prev_pos, prev_T, prev_N,_ prev_B = parallel_frames[-1]  # type: ignore[reportUnknownVariableType, reportUnusedVariable]
            curr_pos = points[i]
            curr_T = tangents[i]
            
            # Transport prev_N to current frame
            # Axis of rotation A = prev_T x curr_T
            axis = vec_cross(prev_T, curr_T)  # type: ignore[reportUndefinedVariable, reportUnknownArgumentType]
            
            # If collinear (straight line), just update T
            if vec_length(axis) < 1e-9:
                curr_N = prev_N
            else:
                 axis = vec_normalize(axis)
                 # Angle between tangents
                 dot = prev_T[0]*curr_T[0] + prev_T[1]*curr_T[1] + prev_T[2]*curr_T[2]  # type: ignore[reportUndefinedVariable, reportUnknownVariableType]
                 # Clamp for safety
                 phi = math.acos(max(-1.0, min(1.0, dot)))
                 
                 # Rotate prev_N around axis by phi
                 # Rodrigues rotation formula
                 # v_rot = v cos(phi) + (k x v) sin(phi) + k (k . v) (1 - cos(phi))
                 cos_phi = math.cos(phi)
                 sin_phi = math.sin(phi)
                 k_cross_v = vec_cross(axis, prev_N)
                 k_dot_v = axis[0]*prev_N[0] + axis[1]*prev_N[1] + axis[2]*prev_N[2]  # type: ignore[reportUndefinedVariable, reportUnknownVariableType]
                 
                 term1 = vec_scale(prev_N, cos_phi)
                 term2 = vec_scale(k_cross_v, sin_phi)
                 term3 = vec_scale(axis, k_dot_v * (1 - cos_phi))
                 
                 curr_N = vec_add(vec_add(term1, term2), term3)
                 curr_N = vec_normalize(curr_N)

            # Re-orthogonalize to ensure perfect N-T orthogonality
            # N = N - (N . T) * T
            dot_val = curr_N[0]*curr_T[0] + curr_N[1]*curr_T[1] + curr_N[2]*curr_T[2]
            curr_N = vec_sub(curr_N, vec_scale(curr_T, dot_val))
            curr_N = vec_normalize(curr_N)
            
            curr_B = vec_normalize(vec_cross(curr_T, curr_N))
            
            parallel_frames.append((curr_pos, curr_T, curr_N, curr_B))

        # 3. Calculate Correction Twist Angle
        # Compare frame at 2pi (index segments) with frame at 0
        # They are at the same spatial point.
        first_N = parallel_frames[0][2]
        last_N = parallel_frames[segments][2]
        
        # Angle alpha between first_N and last_N (in the plane normal to T)
        # We can use atan2(det, dot) where det = (first_N x last_N) . T
        cross_Ns = vec_cross(first_N, last_N)
        T_end = parallel_frames[segments][1]
        det = cross_Ns[0]*T_end[0] + cross_Ns[1]*T_end[1] + cross_Ns[2]*T_end[2]
        dot = first_N[0]*last_N[0] + first_N[1]*last_N[1] + first_N[2]*last_N[2]
        
        total_twist = math.atan2(det, dot)
        
        # 4. Generate Final Twisted Frames & Vertices
        for i in range(segments):
            pos, _T, N_transport, B_transport = parallel_frames[i]  # type: ignore[reportUnknownVariableType, reportUnusedVariable]
            
            # Twist adjustment
            # We want to distribute -total_twist over the length
            theta = -(total_twist * (i / segments))
            
            cos_theta = math.cos(theta)
            sin_theta = math.sin(theta)
            
            # Rotate N, B around T
            # N_final = N cos + B sin
            # B_final = -N sin + B cos
            
            N_final_x = N_transport[0]*cos_theta + B_transport[0]*sin_theta
            N_final_y = N_transport[1]*cos_theta + B_transport[1]*sin_theta
            N_final_z = N_transport[2]*cos_theta + B_transport[2]*sin_theta
            N_final = (N_final_x, N_final_y, N_final_z)
            
            B_final_x = -N_transport[0]*sin_theta + B_transport[0]*cos_theta
            B_final_y = -N_transport[1]*sin_theta + B_transport[1]*cos_theta
            B_final_z = -N_transport[2]*sin_theta + B_transport[2]*cos_theta
            B_final = (B_final_x, B_final_y, B_final_z)
            
            # Generate Tube Ring
            for j in range(radial_seg):
                angle = (j / radial_seg) * 2 * math.pi
                cos_a = math.cos(angle)
                sin_a = math.sin(angle)
                
                off_x = vec_scale(N_final, tube_r * cos_a)
                off_y = vec_scale(B_final, tube_r * sin_a)
                offset = vec_add(off_x, off_y)
                
                vertex = vec_add(pos, offset)
                vertices.append(vertex)
                
        # 5. Generate Faces
        for i in range(segments):
            next_i = (i + 1) % segments
            
            for j in range(radial_seg):
                next_j = (j + 1) % radial_seg
                
                idx_bl = i * radial_seg + j
                idx_br = next_i * radial_seg + j
                idx_tr = next_i * radial_seg + next_j
                idx_tl = i * radial_seg + next_j
                
                faces.append((idx_bl, idx_br, idx_tr, idx_tl))

        return vertices, faces


class TorusKnotSolidCalculator:
    """Torus Knot calculator."""

    def __init__(
        self,
        p: int = 2,
        q: int = 3,
        major_radius: float = 3.0,
        minor_radius: float = 1.0,
        tube_radius: float = 0.4,
    ):
        """
          init   logic.
        
        Args:
            p: Description of p.
            q: Description of q.
            major_radius: Description of major_radius.
            minor_radius: Description of minor_radius.
            tube_radius: Description of tube_radius.
        
        """
        self._properties = {
            'p': SolidProperty('P (Lobes)', 'p', 'int', 1.0),
            'q': SolidProperty('Q (Twists)', 'q', 'int', 1.0),
            'major_radius': SolidProperty('Major Radius (R)', 'major_radius', 'units', 10.0),
            'minor_radius': SolidProperty('Minor Radius (r)', 'minor_radius', 'units', 10.0),
            'tube_radius': SolidProperty('Tube Radius', 'tube_radius', 'units', 10.0),
            
            # Read-only metrics
            'arc_length': SolidProperty('Arc Length', 'arc_length', 'units', 0.0, editable=False),
            'surface_area': SolidProperty('Approx. Surface Area', 'surface_area', 'units²', 0.0, editable=False),
            'volume': SolidProperty('Approx. Volume', 'volume', 'units³', 0.0, editable=False),
        }
        
        self.set_property('p', float(p))
        self.set_property('q', float(q))
        self.set_property('major_radius', major_radius)
        self.set_property('minor_radius', minor_radius)
        self.set_property('tube_radius', tube_radius)
        
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
        if value is not None and value <= 0 and key not in ('p', 'q'):
            return False
            
        prop = self._properties.get(key)
        if not prop:
            return False
            
        if key in ('p', 'q'):
             # Ensure integer
             prop.value = float(int(value)) if value else 0.0
        else:
             prop.value = value
             
        self._recalculate()
        return True

    def _recalculate(self):
        p = int(self._properties['p'].value or 2)
        q = int(self._properties['q'].value or 3)
        R = self._properties['major_radius'].value
        r = self._properties['minor_radius'].value
        tube_r = self._properties['tube_radius'].value
        
        if R is None or r is None or tube_r is None:
            return

        metrics = TorusKnotSolidService._compute_metrics(p, q, R, r, tube_r)
        
        self._properties['arc_length'].value = metrics.arc_length
        self._properties['surface_area'].value = metrics.approx_surface_area
        self._properties['volume'].value = metrics.approx_volume
        
        self._result = TorusKnotSolidService.build(p, q, R, r, tube_r)

    def clear(self):
        # Reset to defaults
        # self.__init__() # Actually cleaner to just clear values?
        # But UI expects None?
        """
        Clear logic.
        
        """
        pass

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