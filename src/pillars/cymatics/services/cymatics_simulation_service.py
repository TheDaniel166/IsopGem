"""Simulation engine for cymatics patterns.

Supports multiple plate shapes (rectangular, circular, hexagonal, custom polygon)
and both manual mode selection and frequency-based input.
"""
from __future__ import annotations

import time
from typing import Tuple

import numpy as np
from scipy.special import jv as bessel_jv

from ..models import PlateShape, SimulationParams, SimulationResult

# Precomputed Bessel function zeros for circular plate modes
# jn_zeros(m, n) gives the nth zero of Bessel function J_m
# We cache these for common mode combinations
_BESSEL_ZEROS_CACHE: dict[Tuple[int, int], float] = {}


def _bessel_zero(m: int, n: int) -> float:
    """Get the nth zero of Bessel function J_m (cached)."""
    key = (m, n)
    if key not in _BESSEL_ZEROS_CACHE:
        # Approximate zeros using McMahon's expansion for large arguments
        # More accurate than scipy.special.jn_zeros for our use case
        from scipy.special import jn_zeros

        try:
            zeros = jn_zeros(m, n)
            _BESSEL_ZEROS_CACHE[key] = float(zeros[-1])
        except Exception:
            # Fallback approximation
            _BESSEL_ZEROS_CACHE[key] = (n + 0.5 * m - 0.25) * np.pi
    return _BESSEL_ZEROS_CACHE[key]


class CymaticsSimulationService:
    """Generates standing-wave patterns for 2D plates.

    Supports rectangular, circular, hexagonal, and custom polygon
    plate geometries with Bessel function modes for circular plates.
    """

    # Frequency-to-mode mapping constants
    FREQ_MIN = 20.0  # Hz - lowest practical cymatics frequency
    FREQ_MAX = 2000.0  # Hz - upper cymatics range
    MODE_MAX = 12  # Maximum mode number

    def hz_to_modes(self, frequency_hz: float, params: "SimulationParams") -> Tuple[int, int]:
        """Map frequency (Hz) to (m, n) mode pair with material correction.
        
        Accounts for material wave speed:
        - Faster materials (glass) reach higher modes at same frequency
        - Slower materials (wood) reach lower modes at same frequency
        
        Args:
            frequency_hz: Driving frequency in Hz
            params: Simulation parameters (contains material)
            
        Returns:
            (m, n) mode numbers that resonate at this frequency for the material
        """
        # Material-corrected frequency
        # Higher wave speed → higher effective frequency → higher modes
        material_factor = params.plate_material.wave_speed_factor
        effective_freq = frequency_hz * material_factor
        
        # Logarithmic mapping to mode numbers
        freq = np.clip(effective_freq, self.FREQ_MIN, self.FREQ_MAX)
        log_ratio = (np.log(freq) - np.log(self.FREQ_MIN)) / (
            np.log(self.FREQ_MAX) - np.log(self.FREQ_MIN)
        )
        total_mode = int(log_ratio * (self.MODE_MAX * 2 - 2)) + 2
        m = max(1, min(self.MODE_MAX, (total_mode + 1) // 2))
        n = max(1, min(self.MODE_MAX, total_mode - m + 1))
        return (m, n)

    def simulate(
        self, params: SimulationParams, phase: float = 0.0
    ) -> SimulationResult:
        """Run a cymatics simulation for the given parameters.

        If use_frequency_mode is True, derives modes from frequency_hz.
        Generates field based on plate_shape setting.
        """
        # Resolve effective modes
        effective_params = self._resolve_params(params)

        # Generate field based on plate shape
        if effective_params.plate_shape == PlateShape.RECTANGULAR:
            field = self._generate_rectangular_field(effective_params, phase)
        elif effective_params.plate_shape == PlateShape.CIRCULAR:
            field = self._generate_circular_field(effective_params, phase)
        elif effective_params.plate_shape == PlateShape.HEXAGONAL:
            field = self._generate_hexagonal_field(effective_params, phase)
        elif effective_params.plate_shape == PlateShape.HEPTAGONAL:
            field = self._generate_heptagonal_field(effective_params, phase)
        elif effective_params.plate_shape == PlateShape.CUSTOM_POLYGON:
            field = self._generate_polygon_field(effective_params, phase)
        else:
            field = self._generate_rectangular_field(effective_params, phase)

        normalized = self._normalize_field(field)

        # Compute height map for 3D visualization if requested
        height_map = field.copy() if params.show_3d_surface else None

        # Generate boundary mask for particle collision detection
        boundary_mask = self._generate_boundary_mask(params, field.shape)

        return SimulationResult(
            field=field,
            normalized=normalized,
            params=params,
            timestamp=time.time(),
            height_map=height_map,
            boundary_mask=boundary_mask,
        )

    def _generate_boundary_mask(
        self, params: SimulationParams, shape: tuple[int, int]
    ) -> np.ndarray:
        """Generate boundary mask for the given plate shape.

        Returns:
            Boolean array where True = valid particle positions
        """
        grid_size = shape[0]

        if params.plate_shape == PlateShape.RECTANGULAR:
            # Rectangular boundary with padding to keep particles away from edges
            # Increased padding to account for aspect ratio letterboxing in display
            mask = np.ones(shape, dtype=bool)
            pad = max(1, int(grid_size * 0.05))  # 5% padding on each side
            mask[:pad, :] = False   # Top border
            mask[-pad:, :] = False  # Bottom border
            mask[:, :pad] = False   # Left border
            mask[:, -pad:] = False  # Right border
            return mask

        elif params.plate_shape == PlateShape.CIRCULAR:
            # Unit circle boundary - centered at (0.5, 0.5) in [0,1] space
            x = np.linspace(0.0, 1.0, grid_size)
            y = np.linspace(1.0, 0.0, grid_size)  # FLIPPED: y=0 at top (row 0)
            xx, yy = np.meshgrid(x, y)
            # Distance from center (0.5, 0.5)
            r = np.sqrt((xx - 0.5)**2 + (yy - 0.5)**2)
            return r <= 0.48  # Radius slightly less than 0.5 for border padding

        elif params.plate_shape == PlateShape.HEXAGONAL:
            # Hexagon boundary - centered at (0.5, 0.5) in [0,1] space
            x = np.linspace(0.0, 1.0, grid_size)
            y = np.linspace(1.0, 0.0, grid_size)  # FLIPPED: y=0 at top
            xx, yy = np.meshgrid(x, y)
            # Shift to center at origin for calculation
            xx_centered = (xx - 0.5) * 2.0  # Map to [-1, +1]
            yy_centered = (yy - 0.5) * 2.0  # Map to [-1, +1]
            mask = self._hexagon_mask(xx_centered, yy_centered, radius=0.90)
            return mask > 0.5  # Convert float mask to boolean

        elif params.plate_shape == PlateShape.HEPTAGONAL:
            # Heptagon boundary - centered at (0.5, 0.5) in [0,1] space
            x = np.linspace(0.0, 1.0, grid_size)
            y = np.linspace(1.0, 0.0, grid_size)  # FLIPPED: y=0 at top
            xx, yy = np.meshgrid(x, y)
            # Shift to center at origin for calculation
            xx_centered = (xx - 0.5) * 2.0  # Map to [-1, +1]
            yy_centered = (yy - 0.5) * 2.0  # Map to [-1, +1]
            mask = self._heptagon_mask(xx_centered, yy_centered, radius=0.90)
            return mask > 0.5  # Convert float mask to boolean

        elif params.plate_shape == PlateShape.CUSTOM_POLYGON:
            # Custom polygon boundary - in [0,1] space
            if params.custom_polygon_vertices and len(params.custom_polygon_vertices) >= 3:
                x = np.linspace(0.0, 1.0, grid_size)
                y = np.linspace(1.0, 0.0, grid_size)  # FLIPPED: y=0 at top
                xx, yy = np.meshgrid(x, y)
                mask = self._polygon_mask(xx, yy, params.custom_polygon_vertices)
                return mask > 0.5
            else:
                # Fallback to padded rectangle if no vertices
                return self._generate_boundary_mask(
                    SimulationParams(plate_shape=PlateShape.RECTANGULAR),
                    shape
                )

        # Default fallback
        return np.ones(shape, dtype=bool)

    def _resolve_params(self, params: SimulationParams) -> SimulationParams:
        """Resolve frequency-based mode selection if enabled."""
        if not params.use_frequency_mode:
            return params

        m, n = self.hz_to_modes(params.frequency_hz, params)
        # Create modified params with derived modes
        # Secondary modes are offset for interesting interference
        return SimulationParams(
            grid_size=params.grid_size,
            mode_m=m,
            mode_n=n,
            secondary_m=min(self.MODE_MAX, m + 1),
            secondary_n=min(self.MODE_MAX, n + 1),
            mix=params.mix,
            damping=params.damping,
            frequency_hz=params.frequency_hz,
            use_frequency_mode=params.use_frequency_mode,
            plate_shape=params.plate_shape,
            custom_polygon_vertices=params.custom_polygon_vertices,
            plate_material=params.plate_material,
            color_gradient=params.color_gradient,
            custom_gradient_stops=params.custom_gradient_stops,
            show_3d_surface=params.show_3d_surface,
            enable_particles=params.enable_particles,
            particle_count=params.particle_count,
            particle_speed=params.particle_speed,
        )

    def _generate_rectangular_field(
        self, params: SimulationParams, phase: float
    ) -> np.ndarray:
        """Original rectangular plate standing wave pattern."""
        grid_size = max(16, int(params.grid_size))
        x = np.linspace(0.0, 1.0, grid_size)
        y = np.linspace(0.0, 1.0, grid_size)
        xx, yy = np.meshgrid(x, y)

        primary = np.sin(params.mode_m * np.pi * xx) * np.sin(
            params.mode_n * np.pi * yy
        )
        secondary = np.sin(params.secondary_m * np.pi * xx) * np.sin(
            params.secondary_n * np.pi * yy
        )

        mix = float(np.clip(params.mix, 0.0, 1.0))
        primary_phase = 0.6 + 0.4 * np.cos(phase)
        secondary_phase = 0.6 + 0.4 * np.cos(1.35 * phase + np.pi / 4.0)
        field = (1.0 - mix) * primary * primary_phase
        field += mix * secondary * secondary_phase

        if params.damping > 0.0:
            field *= self._damping_mask(xx, yy, params.damping)

        return field

    def _generate_circular_field(
        self, params: SimulationParams, phase: float
    ) -> np.ndarray:
        """Circular plate using Bessel functions (true Chladni patterns).

        Uses J_m(k_mn * r) * cos(m * theta) for circular plate vibration
        modes, where k_mn is the nth zero of the Bessel function J_m.
        """
        grid_size = max(16, int(params.grid_size))
        x = np.linspace(-1.0, 1.0, grid_size)
        y = np.linspace(-1.0, 1.0, grid_size)
        xx, yy = np.meshgrid(x, y)

        # Convert to polar coordinates
        r = np.sqrt(xx**2 + yy**2)
        theta = np.arctan2(yy, xx)

        # Primary mode: J_m(k_mn * r) * cos(m * theta)
        m, n = params.mode_m, max(1, params.mode_n)
        k_mn = _bessel_zero(m, n)
        radial_primary = bessel_jv(m, k_mn * r)
        angular_primary = np.cos(m * theta)
        primary = radial_primary * angular_primary

        # Secondary mode for interference
        m2, n2 = params.secondary_m, max(1, params.secondary_n)
        k_mn2 = _bessel_zero(m2, n2)
        radial_secondary = bessel_jv(m2, k_mn2 * r)
        angular_secondary = np.cos(m2 * theta)
        secondary = radial_secondary * angular_secondary

        # Mix and apply time evolution
        mix = float(np.clip(params.mix, 0.0, 1.0))
        primary_phase = 0.6 + 0.4 * np.cos(phase)
        secondary_phase = 0.6 + 0.4 * np.cos(1.35 * phase + np.pi / 4.0)

        field = (1.0 - mix) * primary * primary_phase
        field += mix * secondary * secondary_phase

        # Apply circular boundary (zero outside unit circle)
        field[r > 1.0] = 0.0

        # Optional radial damping
        if params.damping > 0.0:
            field *= np.exp(-params.damping * r**2)

        return field

    def _generate_hexagonal_field(
        self, params: SimulationParams, phase: float
    ) -> np.ndarray:
        """Hexagonal plate with three-fold symmetric modes.

        Uses superposition of three 60-degree rotated sine waves
        to create hexagonal symmetry patterns.
        """
        grid_size = max(16, int(params.grid_size))
        x = np.linspace(-1.0, 1.0, grid_size)
        y = np.linspace(-1.0, 1.0, grid_size)
        xx, yy = np.meshgrid(x, y)

        m, n = params.mode_m, params.mode_n

        # Three-fold symmetric pattern (0°, 60°, 120° rotations)
        angles = [0, np.pi / 3, 2 * np.pi / 3]
        field = np.zeros_like(xx)

        for angle in angles:
            # Rotate coordinates
            rx = xx * np.cos(angle) + yy * np.sin(angle)
            ry = -xx * np.sin(angle) + yy * np.cos(angle)
            # Add wave contribution
            field += np.sin(m * np.pi * (rx + 1) / 2) * np.sin(
                n * np.pi * (ry + 1) / 2
            )

        # Secondary mode with different symmetry
        m2, n2 = params.secondary_m, params.secondary_n
        secondary = np.zeros_like(xx)
        for angle in angles:
            rx = xx * np.cos(angle) + yy * np.sin(angle)
            ry = -xx * np.sin(angle) + yy * np.cos(angle)
            secondary += np.sin(m2 * np.pi * (rx + 1) / 2) * np.sin(
                n2 * np.pi * (ry + 1) / 2
            )

        # Mix and time evolution
        mix = float(np.clip(params.mix, 0.0, 1.0))
        primary_phase = 0.6 + 0.4 * np.cos(phase)
        secondary_phase = 0.6 + 0.4 * np.cos(1.35 * phase + np.pi / 4.0)

        result = (1.0 - mix) * field * primary_phase
        result += mix * secondary * secondary_phase

        # Apply hexagonal boundary mask
        mask = self._hexagon_mask(xx, yy, radius=0.95)
        result *= mask

        if params.damping > 0.0:
            r = np.sqrt(xx**2 + yy**2)
            result *= np.exp(-params.damping * r**2)

        return result

    def _generate_polygon_field(
        self, params: SimulationParams, phase: float
    ) -> np.ndarray:
        """Custom polygon plate with rectangular modes masked to polygon boundary."""
        # Start with rectangular field
        field = self._generate_rectangular_field(params, phase)

        # Apply polygon mask if vertices provided
        if params.custom_polygon_vertices and len(params.custom_polygon_vertices) >= 3:
            grid_size = field.shape[0]
            x = np.linspace(0.0, 1.0, grid_size)
            y = np.linspace(0.0, 1.0, grid_size)
            xx, yy = np.meshgrid(x, y)

            mask = self._polygon_mask(
                xx, yy, params.custom_polygon_vertices
            )
            field *= mask

        return field

    def _hexagon_mask(
        self, xx: np.ndarray, yy: np.ndarray, radius: float = 1.0
    ) -> np.ndarray:
        """Create a hexagonal boundary mask."""
        # Regular hexagon inscribed in circle of given radius
        mask = np.ones_like(xx)
        for i in range(6):
            angle = i * np.pi / 3
            # Normal vector pointing inward
            nx = np.cos(angle)
            ny = np.sin(angle)
            # Distance from center along this direction
            dist = xx * nx + yy * ny
            mask *= (dist < radius * np.cos(np.pi / 6)).astype(float)
        return mask

    def _generate_heptagonal_field(
        self, params: SimulationParams, phase: float
    ) -> np.ndarray:
        """Generating standing wave on 7-sided plate."""
        grid_size = params.grid_size
        x = np.linspace(-1.0, 1.0, grid_size)
        y = np.linspace(1.0, -1.0, grid_size)  # FLIPPED to match visual space
        xx, yy = np.meshgrid(x, y)
        
        # Heptagonal symmetry
        field = np.zeros_like(xx)
        n_symmetry = 7
        
        # RadialBessel-like function approx for polygonal modes
        r = np.sqrt(xx**2 + yy**2)
        theta = np.arctan2(yy, xx)
        
        # Primary mode
        k1 = params.mode_m * 2.5
        m1 = params.mode_n
        radial = np.cos(k1 * r * np.pi) 
        angular = np.cos(m1 * (theta * n_symmetry / 2.0))
        field += radial * angular

        # Secondary mode interference
        k2 = params.secondary_m * 2.5
        m2 = params.secondary_n
        radial2 = np.cos(k2 * r * np.pi)
        angular2 = np.cos(m2 * (theta * n_symmetry / 2.0))
        secondary = radial2 * angular2

        # Mix and phase
        mix = float(np.clip(params.mix, 0.0, 1.0))
        primary_phase = 0.6 + 0.4 * np.cos(phase)
        secondary_phase = 0.6 + 0.4 * np.cos(1.35 * phase + np.pi / 4.0)

        result = (1.0 - mix) * field * primary_phase
        result += mix * secondary * secondary_phase
        
        # Apply heptagonal boundary mask
        mask = self._heptagon_mask(xx, yy, radius=0.95)
        result *= mask
        
        if params.damping > 0.0:
            result *= np.exp(-params.damping * r**2)
            
        return result

    def _heptagon_mask(
        self, xx: np.ndarray, yy: np.ndarray, radius: float = 1.0
    ) -> np.ndarray:
        """Create a heptagonal boundary mask."""
        mask = np.ones_like(xx)
        for i in range(7):
            angle = (i * 2 * np.pi / 7) - (np.pi / 2)  # Start from top? No, let's align point up
            # Actually standard heptagon usually has point up or flat bottom
            # Let's use simple rotation: i * 2pi/7
            angle = i * 2 * np.pi / 7
            
            # Normal vector pointing inward
            nx = np.cos(angle)
            ny = np.sin(angle)
            # Distance from center
            dist = xx * nx + yy * ny
            # Apothem distance
            mask *= (dist < radius * np.cos(np.pi / 7)).astype(float)
        return mask

    def _polygon_mask(
        self,
        xx: np.ndarray,
        yy: np.ndarray,
        vertices: list[Tuple[float, float]],
    ) -> np.ndarray:
        """Create a polygon boundary mask using ray casting."""
        mask = np.zeros_like(xx, dtype=float)
        n = len(vertices)

        for i in range(xx.shape[0]):
            for j in range(xx.shape[1]):
                px, py = xx[i, j], yy[i, j]
                inside = False
                p1x, p1y = vertices[0]
                for k in range(1, n + 1):
                    p2x, p2y = vertices[k % n]
                    if py > min(p1y, p2y):
                        if py <= max(p1y, p2y):
                            if px <= max(p1x, p2x):
                                if p1y != p2y:
                                    xinters = (py - p1y) * (p2x - p1x) / (
                                        p2y - p1y
                                    ) + p1x
                                if p1x == p2x or px <= xinters:
                                    inside = not inside
                    p1x, p1y = p2x, p2y
                mask[i, j] = 1.0 if inside else 0.0

        return mask

    def _normalize_field(self, field: np.ndarray) -> np.ndarray:
        """Normalize field to [0, 1] range based on amplitude."""
        magnitude = np.abs(field)
        peak = float(np.max(magnitude))
        if peak <= 1e-12:
            return magnitude
        return magnitude / peak

    def _damping_mask(
        self, xx: np.ndarray, yy: np.ndarray, damping: float
    ) -> np.ndarray:
        """Create Gaussian radial damping envelope."""
        cx = 0.5
        cy = 0.5
        radius = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        return np.exp(-damping * radius**2)
