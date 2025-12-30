"""Nested Heptagons Service - Golden Trisection Calculator.

This module calculates properties of three nested regular heptagons
based on the Golden Trisection ratios discovered in heptagonal geometry.

The three heptagons are related by sacred ratios:
- Outer to Middle: scaled by (ρ × σ)
- Middle to Inner: scaled by α

Constants:
- Σ (SIGMA) = 2.24697960371747 (Long diagonal in unit-edge heptagon)
- Ρ (RHO) = 1.80193773580484 (Short diagonal in unit-edge heptagon)  
- α (ALPHA) = 0.246979603717467 (Nested heptagon edge ratio)
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
    
    The system is driven by the middle heptagon's edge length.
    All other values are derived from this using the sacred ratios.
    """
    
    # Golden Trisection Constants
    SIGMA = 2.24697960371747   # Σ - Long diagonal ratio
    RHO = 1.80193773580484     # Ρ - Short diagonal ratio
    ALPHA = 0.246979603717467  # α - Nesting ratio (inner/middle)
    
    # Number of sides (fixed for heptagons)
    SIDES = 7
    
    def __init__(self, middle_edge_length: float = 1.0):
        """Initialize the service with the middle heptagon edge length.
        
        Args:
            middle_edge_length: Edge length of the middle heptagon
        """
        self._middle_edge = max(0.01, middle_edge_length)
        self._orientation = "vertex_top"  # or "side_top"
    
    @property
    def middle_edge(self) -> float:
        """Get the current middle edge length."""
        return self._middle_edge
    
    @middle_edge.setter
    def middle_edge(self, value: float) -> None:
        """Set the middle edge length."""
        self._middle_edge = max(0.01, value)
    
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
    # Edge Length Calculations
    # ─────────────────────────────────────────────────────────────────
    
    def outer_edge(self) -> float:
        """Calculate outer heptagon edge length.
        
        E_outer = E_middle × RHO × SIGMA
        """
        return self._middle_edge * self.RHO * self.SIGMA
    
    def inner_edge(self) -> float:
        """Calculate inner heptagon edge length.
        
        E_inner = E_middle × ALPHA
        """
        return self._middle_edge * self.ALPHA
    
    # ─────────────────────────────────────────────────────────────────
    # Set From Different Properties
    # ─────────────────────────────────────────────────────────────────
    
    def set_from_outer_edge(self, outer_edge: float) -> None:
        """Set state from outer edge length."""
        self._middle_edge = outer_edge / (self.RHO * self.SIGMA)
    
    def set_from_inner_edge(self, inner_edge: float) -> None:
        """Set state from inner edge length."""
        self._middle_edge = inner_edge / self.ALPHA
    
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
    
    def outer_properties(self) -> HeptagonProperties:
        """Get complete properties for the outer heptagon."""
        edge = self.outer_edge()
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
    
    def middle_properties(self) -> HeptagonProperties:
        """Get complete properties for the middle heptagon."""
        edge = self._middle_edge
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
    
    def inner_properties(self) -> HeptagonProperties:
        """Get complete properties for the inner heptagon."""
        edge = self.inner_edge()
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
    
    def outer_vertices(self) -> List[Point2D]:
        """Get vertices of the outer heptagon."""
        return self._vertices(self._circumradius(self.outer_edge()))
    
    def middle_vertices(self) -> List[Point2D]:
        """Get vertices of the middle heptagon."""
        return self._vertices(self._circumradius(self._middle_edge))
    
    def inner_vertices(self) -> List[Point2D]:
        """Get vertices of the inner heptagon."""
        return self._vertices(self._circumradius(self.inner_edge()))
    
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
