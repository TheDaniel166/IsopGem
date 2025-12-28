
"""
Kamea Math Service - The Pattern Weaver.

Handles complex 3D math and vector calculations for Kamea visualizations,
isolating heavy numpy dependencies from the View layer.
"""
from typing import List, Tuple, Dict
import math

try:
    import numpy as np # type: ignore
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None # type: ignore

class KameaMathService:
    """Service for 3D coordinate calculations and projections."""
    
    def __init__(self):
        # Ternary Offsets for Fractal Construction
        """
          init   logic.
        
        """
        self.offsets = {
            '00': (0, 0),
            '10': (-1, 1), '21': (0, 1), '02': (1, 1),
            '22': (-1, 0), '11': (1, 0),
            '01': (-1, -1), '12': (0, -1), '20': (1, -1)
        }

    def to_ternary(self, n: int) -> str:
        """Convert integer to 6-digit ternary string."""
        if n == 0: return "000000"
        nums = []
        val = n
        while val:
            val, r = divmod(val, 3)
            nums.append(str(r))
        return ''.join(reversed(nums)).zfill(6)

    def calculate_coord(self, ternary: str) -> Tuple[float, float, float, int]:
        """
        Calculates 3D world coordinate for any ternary string.
        Returns: (x, y, z, dim_count/pyx)
        """
        # Parse Quadset Bigrams
        macro = ternary[2:4]
        meso = ternary[1] + ternary[4]
        micro = ternary[0] + ternary[5]
        
        off1 = self.offsets.get(macro, (0,0))
        off2 = self.offsets.get(meso, (0,0))
        off3 = self.offsets.get(micro, (0,0))
        
        # Logic Coords (2D Grid projected on XZ plane)
        gx = (off1[0] * 9) + (off2[0] * 3) + (off3[0] * 1)
        gz = (off1[1] * 9) + (off2[1] * 3) + (off3[1] * 1)
        
        pyx_count = ternary.count('0')
        
        # Map to 3D: X=gx, Y=Height(pyx), Z=gz
        # Y is scaled by 4.0 matching original detailed view logic
        return (float(gx), pyx_count * 4.0, float(gz), pyx_count)

    def project_points(self, 
                      points: List[Tuple[float, float, float]], 
                      rot_x: float, 
                      rot_y: float) -> List[Tuple[float, float, float]]:
        """
        Rotate and project 3D points based on camera angles.
        Returns rotated points (x, y, z) where z is depth.
        """
        if not points:
            return []

        # If numpy is available, use it for speed
        if NUMPY_AVAILABLE and np is not None:
             return self._project_numpy(points, rot_x, rot_y)
        else:
             return self._project_pure(points, rot_x, rot_y)
             
    def _project_numpy(self, points, rot_x, rot_y) -> List[Tuple[float, float, float]]:
        """Fast Vectorized Rotation."""
        cx, sx = math.cos(rot_x), math.sin(rot_x)
        cy, sy = math.cos(rot_y), math.sin(rot_y)
        
        # Matrix: Rotate Y (Yaw) then X (Pitch)
        # However, original code defined:
        # cy, 0, sy
        # sx*sy, cx, -sx*cy
        # -cx*sy, sx, cx*cy ??
        # Original code manual Matrix:
        # [cy, 0, sy],
        # [sx*sy, cx, -sx*cy],
        # [-cx*sy, sx, cx*cy]
        # Wait, the last row should be [-cx*sy, sx, cx*cy] ?? No.
        # Let's match typical rotation matrices.
        # Ry = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
        # Rx = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
        # Rx * Ry = 
        # [cy,          0,   sy]
        # [sx*sy,      cx,  -sx*cy]
        # [-cx*sy,     sx,   cx*cy]  <-- This matches the original code exactly.
        # Note: Original code had: [-cx*sy, sx, cx*cy] at indices [2,0], [2,1], [2,2]
        
        rot_mat = np.array([
            [cy, 0, sy],
            [sx*sy, cx, -sx*cy],
            [-cx*sy, sx, cx*cy]
        ])
        
        pts_array = np.array(points)
        # points shape (N, 3). Matrix shape (3, 3).
        # We want pts @ mat.T or mat @ pts.T
        # Original: rot_mat @ vec. So vec is column?
        # If vec is row (x,y,z), then vec @ rot_mat.T
        
        rotated = pts_array @ rot_mat.T
        return rotated.tolist()

    def _project_pure(self, points, rot_x, rot_y) -> List[Tuple[float, float, float]]:
        """Pure Python Rotation (Fallback)."""
        cx, sx = math.cos(rot_x), math.sin(rot_x)
        cy, sy = math.cos(rot_y), math.sin(rot_y)
        
        # Precompute matrix terms
        m00, m01, m02 = cy, 0.0, sy
        m10, m11, m12 = sx*sy, cx, -sx*cy
        m20, m21, m22 = -cx*sy, sx, cx*cy # Check this term? 
        # Standard Rx*Ry [2,1] is usually sx*0 + cx*sx = cx*sx? 
        # Wait, Rx = [0, sx, cx] row 2? No [0, sx, cx] is row 2 of Rx?
        # Rx = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
        # Ry = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
        # Rx[2] dot Ry col 0: 0*cy + sx*0 + cx*-sy = -cx*sy. Matches m20.
        # Rx[2] dot Ry col 1: 0*0 + sx*1 + cx*0 = sx. Matches m21.
        # Rx[2] dot Ry col 2: 0*sy + sx*0 + cx*cy = cx*cy. Matches m22.
        # OK, Matrix is correct.
        
        result = []
        for x, y, z in points:
            nx = x*m00 + y*m01 + z*m02
            ny = x*m10 + y*m11 + z*m12
            nz = x*m20 + y*m21 + z*m22
            result.append((nx, ny, nz))
        return result