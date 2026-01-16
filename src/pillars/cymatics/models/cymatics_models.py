"""Data models for Cymatics simulation and detection."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Tuple

import numpy as np


class PlateShape(Enum):
    """Supported plate boundary geometries for cymatics simulation."""

    RECTANGULAR = auto()
    CIRCULAR = auto()
    HEXAGONAL = auto()
    HEPTAGONAL = auto()
    CUSTOM_POLYGON = auto()


class ColorGradient(Enum):
    """Predefined color gradient options for visualization."""

    GRAYSCALE = auto()
    HEAT_MAP = auto()
    OCEAN = auto()
    PLASMA = auto()
    VIRIDIS = auto()
    CUSTOM = auto()


class PlateMaterial(Enum):
    """Plate material types with rigorous physical properties.
    
    Based on classical wave mechanics and Kirchhoff plate theory:
    - Wave speed: v = √(Y/ρ) where Y = Young's Modulus, ρ = density
    - Angular frequency: ω = (πv/L)√(n² + m²) for mode (n,m)
    - Flexural rigidity: D = Yh³/(12(1-ν²))
    
    Properties stored as: (name, Y_modulus_GPa, density_kg_m3, poisson_ratio, 
                          thickness_mm, resonance_quality, uniformity)
    
    References:
    - Chladni, E.F.F. (1787) - Brass plate experiments
    - Kirchhoff (1850) - Biharmonic operator for rigid plates
    - Jenny, H. (1967) - Material uniformity effects
    """
    
    # METALS - High Young's modulus, excellent uniformity
    
    STEEL = (
        "Steel (Mild)",
        200.0,      # Y: Young's Modulus in GPa
        7850.0,     # ρ: Density in kg/m³
        0.30,       # ν: Poisson's ratio
        2.0,        # h: Thickness in mm
        0.85,       # Resonance quality (0-1, acoustic clarity)
        0.95,       # Uniformity (0-1, homogeneity)
    )
    
    BRASS = (
        "Brass (Chladni's Choice)",
        100.0,      # Y: Lower than steel
        8500.0,     # ρ: Denser than steel
        0.34,       # ν: Higher Poisson ratio
        2.0,        # h: Standard thickness
        0.95,       # Resonance: Excellent (Chladni preferred this!)
        0.90,       # Uniformity: Very good
    )
    
    ALUMINUM = (
        "Aluminum (6061-T6)",
        69.0,       # Y: Much lower modulus
        2700.0,     # ρ: Very light
        0.33,       # ν: Similar to brass
        3.0,        # h: Thicker to compensate for softness
        0.80,       # Resonance: Good but less clear
        0.92,       # Uniformity: Excellent
    )
    
    COPPER = (
        "Copper (Pure)",
        120.0,      # Y: Moderate
        8960.0,     # ρ: Dense
        0.34,       # ν: Standard for metals
        2.0,        # h: Standard
        0.88,       # Resonance: Warm, clear
        0.88,       # Uniformity: Good
    )
    
    # GLASS - Very stiff, brittle, crystalline
    
    GLASS = (
        "Glass (Soda-lime)",
        70.0,       # Y: Moderate stiffness
        2500.0,     # ρ: Medium density
        0.24,       # ν: Low Poisson (brittle)
        5.0,        # h: Thick to prevent breaking
        0.98,       # Resonance: Crystalline, pure tone
        0.99,       # Uniformity: Near-perfect (isotropic)
    )
    
    # WOOD - Anisotrop ic, high damping (grain-dependent)
    
    WOOD_OAK = (
        "Oak (Across Grain)",
        11.0,       # Y: Low modulus (perpendicular to grain)
        750.0,      # ρ: Lightweight
        0.40,       # ν: High for wood
        6.0,        # h: Thicker for rigidity
        0.50,       # Resonance: Muted, warm
        0.60,       # Uniformity: Poor (grain patterns, knots)
    )
    
    WOOD_MAPLE = (
        "Maple (Tonewood)",
        12.5,       # Y: Slightly stiffer than oak
        700.0,      # ρ: Light
        0.42,       # ν: Wood typical
        6.0,        # h: Standard
        0.65,       # Resonance: Better than oak (used in instruments)
        0.70,       # Uniformity: Better selection
    )
    
    # SYNTHETIC
    
    ACRYLIC = (
        "Acrylic (PMMA)",
        3.2,        # Y: Very low (polymer)
        1180.0,     # ρ: Light plastic
        0.37,       # ν: Polymer typical
        5.0,        # h: Thick for stiffness
        0.70,       # Resonance: Decent clarity
        0.95,       # Uniformity: Manufactured, very uniform
    )
    
    # STONE - Ancient, very stiff
    
    MARBLE = (
        "Marble (Carrara)",
        60.0,       # Y: High for stone
        2700.0,     # ρ: Dense
        0.25,       # ν: Brittle like glass
        10.0,       # h: Very thick (heavy)
        0.92,       # Resonance: Deep, clear, ancient
        0.85,       # Uniformity: Natural variation (veins)
    )
    
    # ═══════════════════════════════════════════════════════════
    # SACRED METALS - Temple acoustics, alchemical resonances
    # ═══════════════════════════════════════════════════════════
    
    GOLD = (
        "Gold (Aurum - Temple Bells)",
        79.0,       # Y: Soft, ductile (lowest of metals)
        19320.0,    # ρ: VERY dense (heaviest common metal)
        0.42,       # ν: High Poisson (ductile)
        1.5,        # h: Thin (expensive!)
        0.98,       # Resonance: Perfect, long decay
        0.99,       # Uniformity: Pure metal, near-perfect
    )
    
    SILVER = (
        "Silver (Argentum - Lunar Mirror)",
        83.0,       # Y: Slightly stiffer than gold
        10490.0,    # ρ: Dense but lighter than gold
        0.37,       # ν: Metallic standard
        1.5,        # h: Thin
        0.97,       # Resonance: Crystalline, bright
        0.98,       # Uniformity: Pure metal
    )
    
    ELECTRUM = (
        "Electrum (Au-Ag Alloy - Solar-Lunar)",
        81.0,       # Y: Interpolated between Au/Ag
        14900.0,    # ρ: Average of gold and silver
        0.39,       # ν: Intermediate
        1.5,        # h: Thin
        0.97,       # Resonance: Balanced synthesis
        0.98,       # Uniformity: Alloyed metal
    )
    
    # ═══════════════════════════════════════════════════════════
    # CRYSTALLINE - Piezoelectric, ultra-low damping
    # ═══════════════════════════════════════════════════════════
    
    QUARTZ_CRYSTAL = (
        "Quartz Crystal (SiO₂ - Piezoelectric)",
        95.0,       # Y: Very stiff (along major axis)
        2650.0,     # ρ: Crystalline silica
        0.17,       # ν: Very low (anisotropic, brittle)
        8.0,        # h: Thick for strength
        0.9999,     # Resonance: ULTRA-pure (Q-factor > 10,000)
        0.999,      # Uniformity: Perfect crystal lattice
    )
    
    SAPPHIRE = (
        "Sapphire (Al₂O₃ - Corundum)",
        345.0,      # Y: Extremely hard (second to diamond)
        3980.0,     # ρ: Dense oxide
        0.27,       # ν: Brittle ceramic
        6.0,        # h: Moderately thick
        0.999,      # Resonance: Pure, minimal losses
        0.995,      # Uniformity: Synthetic crystal perfection
    )
    
    DIAMOND = (
        "Diamond (Carbon Lattice - Ultimate)",
        1050.0,     # Y: HIGHEST known (stiffer than anything)
        3520.0,     # ρ: Surprisingly light for stiffness
        0.20,       # ν: Very brittle
        3.0,        # h: Thin (expensive!)
        0.9999,     # Resonance: Perfect (theoretical Q → ∞)
        1.0,        # Uniformity: Absolute perfection
    )
    
    def __init__(
        self,
        display_name: str,
        youngs_modulus_gpa: float,
        density_kg_m3: float,
        poisson_ratio: float,
        thickness_mm: float,
        resonance_quality: float,
        uniformity: float,
    ):
        """Initialize material with rigorous physical constants.
        
        Args:
            display_name: Human-readable material name
            youngs_modulus_gpa: Y in GPa (stiffness/elasticity)
            density_kg_m3: ρ in kg/m³ (mass per unit volume)
            poisson_ratio: ν, dimensionless (lateral strain ratio, 0.0-0.5)
            thickness_mm: h in mm (plate thickness)
            resonance_quality: 0-1, acoustic clarity (0=dead, 1=pure)
            uniformity: 0-1, material homogeneity (Jenny's observation)
        """
        self.display_name = display_name
        self.youngs_modulus_gpa = youngs_modulus_gpa
        self.density_kg_m3 = density_kg_m3
        self.poisson_ratio = poisson_ratio
        self.thickness_mm = thickness_mm
        self.resonance_quality = resonance_quality
        self.uniformity = uniformity
        
        # Computed properties (physics-derived)
        self._compute_derived_properties()
    
    def _compute_derived_properties(self) -> None:
        """Calculate derived physical properties from base constants.
        
        Following classical wave mechanics:
        1. Wave speed: v = √(Y/ρ)
        2. Flexural rigidity: D = Yh³/(12(1-ν²))
        3. Normalized wave speed (steel = 1.0 reference)
        """
        import math
        
        # Convert units for calculation
        Y_pa = self.youngs_modulus_gpa * 1e9  # GPa → Pa
        h_m = self.thickness_mm * 1e-3         # mm → m
        
        # 1. Wave speed: v = √(Y/ρ)  [m/s]
        self.wave_speed_m_s = math.sqrt(Y_pa / self.density_kg_m3)
        
        # 2. Flexural rigidity: D = Yh³/(12(1-ν²))  [N⋅m]
        self.flexural_rigidity = (
            Y_pa * h_m**3 / (12 * (1 - self.poisson_ratio**2))
        )
        
        # 3. Normalized wave speed (steel as reference = 1.0)
        # Steel: v ≈ 5046 m/s
        steel_wave_speed = math.sqrt(200e9 / 7850)  # ~5046 m/s
        self.wave_speed_factor = self.wave_speed_m_s / steel_wave_speed
        
        # 4. Damping estimate (inverse of resonance quality)
        # High resonance = low damping
        self.damping_factor = 1.0 - self.resonance_quality


@dataclass(slots=True)
class SimulationParams:
    """Configuration for a cymatics simulation run.

    Supports both manual mode selection and frequency-based input,
    multiple plate shapes, and visualization options.
    """

    # Grid resolution
    grid_size: int = 220

    # Manual mode selection
    mode_m: int = 2
    mode_n: int = 3
    secondary_m: int = 3
    secondary_n: int = 4
    mix: float = 0.35
    damping: float = 0.0

    # Frequency-based input (alternative to manual modes)
    frequency_hz: float = 440.0
    use_frequency_mode: bool = False

    # Plate shape configuration
    plate_shape: PlateShape = PlateShape.RECTANGULAR
    custom_polygon_vertices: List[Tuple[float, float]] = field(default_factory=list)

    # Plate material properties
    plate_material: PlateMaterial = PlateMaterial.STEEL

    # Visualization options
    color_gradient: ColorGradient = ColorGradient.GRAYSCALE
    custom_gradient_stops: List[Tuple[float, Tuple[int, int, int, int]]] = field(
        default_factory=list
    )
    show_3d_surface: bool = False

    # Particle simulation
    enable_particles: bool = False
    particle_count: int = 2000
    particle_speed: float = 0.5


@dataclass
class ParticleState:
    """State for particle simulation on nodal lines.

    Particles move toward amplitude minima (nodal lines) and settle
    when they reach low-amplitude regions, simulating sand on a
    vibrating Chladni plate.
    """

    positions: np.ndarray  # Shape: (N, 2) - x, y coordinates in [0, 1]
    velocities: np.ndarray  # Shape: (N, 2) - vx, vy
    settled: np.ndarray  # Shape: (N,) - boolean mask for settled particles


@dataclass(slots=True)
class SimulationResult:
    """Simulation output with normalized view data.

    Extended to support 3D visualization and particle simulation.
    """

    field: np.ndarray
    normalized: np.ndarray
    params: SimulationParams
    timestamp: float

    # Optional: height map for 3D surface rendering
    height_map: Optional[np.ndarray] = None

    # Optional: particle state for sand simulation
    particles: Optional[ParticleState] = None

    # Optional: boundary mask for particle collision (True = valid region)
    boundary_mask: Optional[np.ndarray] = None


@dataclass
class CymaticsPreset:
    """Saveable preset configuration for cymatics parameters.

    Stored as JSON in ~/.config/isopgem/cymatics_presets/
    """

    name: str
    params: SimulationParams
    description: str = ""
    version: int = 1
    created_at: float = 0.0
    tags: List[str] = field(default_factory=list)


@dataclass(slots=True)
class DetectionMetrics:
    """Extracted pattern metrics from a simulation image."""
    symmetry_horizontal: float
    symmetry_vertical: float
    edge_density: float
    radial_peaks: List[float] = field(default_factory=list)
    dominant_frequencies: List[Tuple[float, float, float]] = field(default_factory=list)


@dataclass(slots=True)
class DetectionResult:
    """Detection output including derived maps."""
    metrics: DetectionMetrics
    edges: np.ndarray
    nodal_mask: np.ndarray
