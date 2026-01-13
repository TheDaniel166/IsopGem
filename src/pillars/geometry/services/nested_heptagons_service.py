"""Nested Heptagons Service - Golden Trisection Calculator.

This module calculates properties of N nested regular heptagons (default 7)
based on the Golden Trisection ratios discovered in heptagonal geometry.

The heptagons are nested in a geometric cascade using sacred ratios.
Layer 4 (middle) is the canonical reference; all others scale from it.

Constants:
- Σ (SIGMA) = 2.24697960371747 (Long diagonal in unit-edge heptagon)
- Ρ (RHO) = 1.80193773580484 (Short diagonal in unit-edge heptagon)  
- α (ALPHA) = 0.246979603717467 (Nested heptagon edge ratio)

The sevenfold cascade (layers 1-7, innermost to outermost):
- Layer 1: Innermost (Moon)
- Layer 2: Mercury
- Layer 3: Venus
- Layer 4: Sun (canonical middle)
- Layer 5: Mars
- Layer 6: Jupiter
- Layer 7: Saturn (outermost)
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple


@dataclass(slots=True)
class Point2D:
    """A point in 2D space."""
    x: float
    y: float


@dataclass(slots=True)
class HeptagonProperties:
    """Complete properties of a regular heptagon."""
    edge_length: float
    perimeter: float
    area: float
    short_diagonal: float
    long_diagonal: float
    inradius: float
    circumradius: float
    incircle_circumference: float
    circumcircle_circumference: float


class NestedHeptagonsService:
    """Calculator for nested heptagons using Golden Trisection ratios.
    
    The system is driven by the canonical (middle) heptagon's edge length.
    All other layers are derived using the sacred ratios.
    
    Supports N layers (default 7) numbered 1 (innermost) to N (outermost).
    The canonical layer is layer (N+1)//2 (layer 4 for N=7).
    """
    
    # Golden Trisection Constants
    SIGMA = 2.24697960371747   # Σ - Long diagonal ratio
    RHO = 1.80193773580484     # Ρ - Short diagonal ratio
    ALPHA = 0.246979603717467  # α - Nesting ratio (inner/middle)
    
    # Number of sides (fixed for heptagons)
    SIDES = 7
    
    # Planetary names for 7 layers (innermost to outermost)
    PLANETARY_NAMES = ["Moon", "Mercury", "Venus", "Sun", "Mars", "Jupiter", "Saturn"]
    
    # Alchemical metal names for 7 layers (innermost to outermost)
    METAL_NAMES = ["Silver", "Quicksilver", "Copper", "Gold", "Iron", "Tin", "Lead"]
    
    def __init__(self, num_layers: int = 7, canonical_edge_length: float = 1.0):
        """Initialize the service with N layers.
        
        Args:
            num_layers: Number of nested heptagons (default 7)
            canonical_edge_length: Edge length of the canonical (middle) heptagon
        """
        self._num_layers = max(3, num_layers)
        self._canonical_layer = (self._num_layers + 1) // 2  # Middle layer (4 for N=7)
        self._canonical_edge = max(0.01, canonical_edge_length)
        self._orientation = "vertex_top"  # or "side_top"
    
    @property
    def num_layers(self) -> int:
        """Get the number of layers."""
        return self._num_layers
    
    @property
    def canonical_layer(self) -> int:
        """Get the canonical (middle) layer index."""
        return self._canonical_layer
    
    @property
    def canonical_edge(self) -> float:
        """Get the canonical edge length."""
        return self._canonical_edge
    
    @canonical_edge.setter
    def canonical_edge(self, value: float) -> None:
        """Set the canonical edge length."""
        self._canonical_edge = max(0.01, value)
    
    @property
    def middle_edge(self) -> float:
        """Legacy property: get the canonical (middle) edge length."""
        return self._canonical_edge
    
    @middle_edge.setter
    def middle_edge(self, value: float) -> None:
        """Legacy property: set the canonical (middle) edge length."""
        self._canonical_edge = max(0.01, value)
    
    @property
    def orientation(self) -> str:
        """Get the current orientation."""
        return self._orientation
    
    @orientation.setter
    def orientation(self, value: str) -> None:
        """Set the orientation ('vertex_top' or 'side_top')."""
        if value in ("vertex_top", "side_top"):
            self._orientation = value
    
    # ─────────────────────────────────────────────────────────────────
    # Layer Edge Length Calculations
    # ─────────────────────────────────────────────────────────────────
    
    def _layer_scale_factor(self, layer: int) -> float:
        """Calculate the scale factor for a given layer relative to canonical.
        
        Args:
            layer: Layer number (1 = innermost, N = outermost)
            
        Returns:
            Scale factor to multiply canonical edge by
        """
        steps_from_canonical = layer - self._canonical_layer
        
        if steps_from_canonical == 0:
            return 1.0
        elif steps_from_canonical > 0:
            # Moving outward: multiply by (RHO * SIGMA) per step
            return (self.RHO * self.SIGMA) ** steps_from_canonical
        else:
            # Moving inward: multiply by ALPHA per step  
            return self.ALPHA ** (-steps_from_canonical)
    
    def layer_edge(self, layer: int) -> float:
        """Get the edge length for a specific layer.
        
        Args:
            layer: Layer number (1 = innermost, N = outermost)
        """
        if not 1 <= layer <= self._num_layers:
            raise ValueError(f"Layer {layer} out of range [1, {self._num_layers}]")
        return self._canonical_edge * self._layer_scale_factor(layer)
    
    def set_layer_edge(self, layer: int, edge_length: float) -> None:
        """Set the system state from a specific layer's edge length.
        
        Args:
            layer: Layer number (1 = innermost, N = outermost)
            edge_length: Desired edge length for that layer
        """
        if not 1 <= layer <= self._num_layers:
            raise ValueError(f"Layer {layer} out of range [1, {self._num_layers}]")
        scale = self._layer_scale_factor(layer)
        self._canonical_edge = edge_length / scale
    
    # Legacy methods for 3-layer compatibility
    def outer_edge(self) -> float:
        """Get outermost layer edge (layer N)."""
        return self.layer_edge(self._num_layers)
    
    def inner_edge(self) -> float:
        """Get innermost layer edge (layer 1)."""
        return self.layer_edge(1)
    
    def set_from_outer_edge(self, outer_edge: float) -> None:
        """Set state from outermost layer edge."""
        self.set_layer_edge(self._num_layers, outer_edge)
    
    def set_from_inner_edge(self, inner_edge: float) -> None:
        """Set state from innermost layer edge."""
        self.set_layer_edge(1, inner_edge)
    
    # ─────────────────────────────────────────────────────────────────
    # Base Geometric Formulas
    # ─────────────────────────────────────────────────────────────────
    
    def _circumradius(self, edge: float) -> float:
        """R = edge / (2 × sin(π/n))"""
        return edge / (2 * math.sin(math.pi / self.SIDES))
    
    def _inradius(self, edge: float) -> float:
        """r = edge / (2 × tan(π/n))"""
        return edge / (2 * math.tan(math.pi / self.SIDES))
    
    def _perimeter(self, edge: float) -> float:
        """P = n × edge"""
        return self.SIDES * edge
    
    def _area(self, edge: float) -> float:
        """A = (n/4) × edge² × cot(π/n)"""
        cot = 1 / math.tan(math.pi / self.SIDES)
        return (self.SIDES / 4) * edge * edge * cot
    
    def _short_diagonal(self, edge: float) -> float:
        """Short diagonal = edge × RHO"""
        return edge * self.RHO
    
    def _long_diagonal(self, edge: float) -> float:
        """Long diagonal = edge × SIGMA"""
        return edge * self.SIGMA
    
    # ─────────────────────────────────────────────────────────────────
    # Complete Property Sets
    # ─────────────────────────────────────────────────────────────────
    
    def layer_properties(self, layer: int) -> HeptagonProperties:
        """Get complete properties for a specific layer.
        
        Args:
            layer: Layer number (1 = innermost, N = outermost)
        """
        if not 1 <= layer <= self._num_layers:
            raise ValueError(f"Layer {layer} out of range [1, {self._num_layers}]")
        
        edge = self.layer_edge(layer)
        inradius = self._inradius(edge)
        circumradius = self._circumradius(edge)
        return HeptagonProperties(
            edge_length=edge,
            perimeter=self._perimeter(edge),
            area=self._area(edge),
            short_diagonal=self._short_diagonal(edge),
            long_diagonal=self._long_diagonal(edge),
            inradius=inradius,
            circumradius=circumradius,
            incircle_circumference=2 * math.pi * inradius,
            circumcircle_circumference=2 * math.pi * circumradius,
        )
    
    def all_properties(self) -> List[HeptagonProperties]:
        """Get properties for all layers (ordered innermost to outermost)."""
        return [self.layer_properties(i) for i in range(1, self._num_layers + 1)]
    
    # Legacy methods for 3-layer compatibility
    def outer_properties(self) -> HeptagonProperties:
        """Get properties for outermost layer."""
        return self.layer_properties(self._num_layers)
    
    def middle_properties(self) -> HeptagonProperties:
        """Get properties for canonical (middle) layer."""
        return self.layer_properties(self._canonical_layer)
    
    def inner_properties(self) -> HeptagonProperties:
        """Get properties for innermost layer."""
        return self.layer_properties(1)
    
    # ─────────────────────────────────────────────────────────────────
    # Vertex Calculations
    # ─────────────────────────────────────────────────────────────────
    
    def _vertices(self, circumradius: float) -> List[Point2D]:
        """Calculate vertices for a heptagon with given circumradius."""
        vertices = []
        
        if self._orientation == "vertex_top":
            angle_offset = -math.pi / 2  # Start at top
        else:
            angle_offset = -math.pi / 2 + math.pi / self.SIDES
        
        for i in range(self.SIDES):
            angle = angle_offset + (2 * math.pi * i) / self.SIDES
            x = circumradius * math.cos(angle)
            y = circumradius * math.sin(angle)
            vertices.append(Point2D(x, y))
        
        return vertices
    
    def layer_vertices(self, layer: int) -> List[Point2D]:
        """Get vertices for a specific layer.
        
        Args:
            layer: Layer number (1 = innermost, N = outermost)
        """
        if not 1 <= layer <= self._num_layers:
            raise ValueError(f"Layer {layer} out of range [1, {self._num_layers}]")
        edge = self.layer_edge(layer)
        return self._vertices(self._circumradius(edge))
    
    def all_vertices(self) -> List[List[Point2D]]:
        """Get vertices for all layers (ordered innermost to outermost)."""
        return [self.layer_vertices(i) for i in range(1, self._num_layers + 1)]
    
    # Legacy methods for 3-layer compatibility
    def outer_vertices(self) -> List[Point2D]:
        """Get vertices of the outermost layer."""
        return self.layer_vertices(self._num_layers)
    
    def middle_vertices(self) -> List[Point2D]:
        """Get vertices of the canonical (middle) layer."""
        return self.layer_vertices(self._canonical_layer)
    
    def inner_vertices(self) -> List[Point2D]:
        """Get vertices of the innermost layer."""
        return self.layer_vertices(1)
    
    # ─────────────────────────────────────────────────────────────────
    # Angular Properties
    # ─────────────────────────────────────────────────────────────────
    
    def interior_angle(self) -> float:
        """Interior angle of a regular heptagon in degrees."""
        return (self.SIDES - 2) * 180.0 / self.SIDES  # ≈ 128.57°
    
    def exterior_angle(self) -> float:
        """Exterior angle of a regular heptagon in degrees."""
        return 360.0 / self.SIDES  # ≈ 51.43°
    
    def central_angle(self) -> float:
        """Central angle of a regular heptagon in degrees."""
        return 360.0 / self.SIDES  # ≈ 51.43°
    
    # ─────────────────────────────────────────────────────────────────
    # Bidirectional Property Setters
    # ─────────────────────────────────────────────────────────────────
    
    def set_layer_property(self, layer: int, property_name: str, value: float) -> None:
        """Set system state from any property of any layer (bidirectional solving).
        
        Args:
            layer: Layer number (1 = innermost, N = outermost)
            property_name: Name of property (edge_length, short_diagonal, long_diagonal,
                          circumradius, inradius, perimeter, area, etc.)
            value: Desired value for that property
        """
        if not 1 <= layer <= self._num_layers:
            raise ValueError(f"Layer {layer} out of range [1, {self._num_layers}]")
        
        # Solve for edge length from the given property
        if property_name == "edge_length":
            target_edge = value
        elif property_name == "short_diagonal":
            target_edge = value / self.RHO
        elif property_name == "long_diagonal":
            target_edge = value / self.SIGMA
        elif property_name == "circumradius":
            target_edge = value * 2 * math.sin(math.pi / self.SIDES)
        elif property_name == "inradius":
            target_edge = value * 2 * math.tan(math.pi / self.SIDES)
        elif property_name == "perimeter":
            target_edge = value / self.SIDES
        elif property_name == "area":
            # A = (n/4) × edge² × cot(π/n)  =>  edge = sqrt(4A / (n × cot(π/n)))
            cot = 1 / math.tan(math.pi / self.SIDES)
            target_edge = math.sqrt(4 * value / (self.SIDES * cot))
        elif property_name == "circumcircle_circumference":
            # C = 2πR  =>  R = C/(2π)  =>  edge = 2R×sin(π/n)
            circumradius = value / (2 * math.pi)
            target_edge = circumradius * 2 * math.sin(math.pi / self.SIDES)
        elif property_name == "incircle_circumference":
            # C = 2πr  =>  r = C/(2π)  =>  edge = 2r×tan(π/n)
            inradius = value / (2 * math.pi)
            target_edge = inradius * 2 * math.tan(math.pi / self.SIDES)
        else:
            raise ValueError(f"Unknown property: {property_name}")
        
        # Now set the canonical edge from this layer's target edge
        self.set_layer_edge(layer, target_edge)
