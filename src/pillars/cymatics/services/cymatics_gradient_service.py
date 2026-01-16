"""Color gradient service for cymatics visualization.

Provides color mapping from normalized amplitude values to RGBA colors
using predefined gradient palettes (heat map, ocean, plasma, viridis).
"""
from __future__ import annotations

from typing import List, Tuple

import numpy as np

from ..models import ColorGradient

# Type alias for gradient stop: (position, (R, G, B, A))
GradientStop = Tuple[float, Tuple[int, int, int, int]]


class CymaticsGradientService:
    """Provides color mapping for cymatics amplitude visualization.

    Supports predefined gradients (grayscale, heat map, ocean, plasma, viridis)
    and custom gradient definitions.
    """

    # Predefined gradients as lists of (position, RGBA) stops
    GRADIENTS: dict[ColorGradient, List[GradientStop]] = {
        ColorGradient.GRAYSCALE: [
            (0.0, (0, 0, 0, 255)),
            (1.0, (255, 255, 255, 255)),
        ],
        ColorGradient.HEAT_MAP: [
            (0.0, (0, 0, 0, 255)),  # Black
            (0.2, (128, 0, 128, 255)),  # Purple
            (0.4, (255, 0, 0, 255)),  # Red
            (0.6, (255, 128, 0, 255)),  # Orange
            (0.8, (255, 255, 0, 255)),  # Yellow
            (1.0, (255, 255, 255, 255)),  # White
        ],
        ColorGradient.OCEAN: [
            (0.0, (0, 0, 32, 255)),  # Deep navy
            (0.25, (0, 32, 96, 255)),  # Dark blue
            (0.5, (0, 96, 160, 255)),  # Ocean blue
            (0.75, (0, 160, 200, 255)),  # Teal
            (1.0, (128, 224, 255, 255)),  # Light cyan
        ],
        ColorGradient.PLASMA: [
            (0.0, (13, 8, 135, 255)),  # Deep indigo
            (0.25, (126, 3, 168, 255)),  # Purple
            (0.5, (204, 71, 120, 255)),  # Magenta-coral
            (0.75, (248, 149, 64, 255)),  # Orange
            (1.0, (240, 249, 33, 255)),  # Yellow
        ],
        ColorGradient.VIRIDIS: [
            (0.0, (68, 1, 84, 255)),  # Dark purple
            (0.25, (59, 82, 139, 255)),  # Blue-purple
            (0.5, (33, 145, 140, 255)),  # Teal
            (0.75, (94, 201, 98, 255)),  # Green
            (1.0, (253, 231, 37, 255)),  # Yellow
        ],
    }

    def apply_gradient(
        self,
        normalized: np.ndarray,
        gradient_type: ColorGradient,
        custom_stops: List[GradientStop] | None = None,
    ) -> np.ndarray:
        """Apply color gradient to normalized amplitude data.

        Args:
            normalized: 2D array of values in [0, 1] range
            gradient_type: Which predefined gradient to use
            custom_stops: Optional custom gradient stops (for CUSTOM type)

        Returns:
            RGBA array of shape (H, W, 4) with uint8 values
        """
        if gradient_type == ColorGradient.CUSTOM and custom_stops:
            stops = custom_stops
        elif gradient_type in self.GRADIENTS:
            stops = self.GRADIENTS[gradient_type]
        else:
            stops = self.GRADIENTS[ColorGradient.GRAYSCALE]

        return self._interpolate_gradient(normalized, stops)

    def _interpolate_gradient(
        self, normalized: np.ndarray, stops: List[GradientStop]
    ) -> np.ndarray:
        """Interpolate colors from gradient stops.

        Uses linear interpolation between adjacent stops.
        """
        h, w = normalized.shape
        rgba = np.zeros((h, w, 4), dtype=np.uint8)

        # Ensure stops are sorted by position
        stops = sorted(stops, key=lambda s: s[0])

        # Clamp normalized values to [0, 1]
        values = np.clip(normalized, 0.0, 1.0)

        # Process each gradient segment
        for i in range(len(stops) - 1):
            pos1, color1 = stops[i]
            pos2, color2 = stops[i + 1]

            # Find pixels in this segment
            if i == len(stops) - 2:
                # Last segment includes endpoint
                mask = (values >= pos1) & (values <= pos2)
            else:
                mask = (values >= pos1) & (values < pos2)

            if not np.any(mask):
                continue

            # Calculate interpolation factor for pixels in this segment
            segment_range = pos2 - pos1
            if segment_range > 0:
                t = (values[mask] - pos1) / segment_range
            else:
                t = np.zeros_like(values[mask])

            # Interpolate each color channel
            for c in range(4):
                rgba[mask, c] = (
                    color1[c] * (1.0 - t) + color2[c] * t
                ).astype(np.uint8)

        return rgba

    def get_gradient_colors(
        self, gradient_type: ColorGradient, num_colors: int = 256
    ) -> np.ndarray:
        """Get a palette of colors for the gradient.

        Useful for creating lookup tables or legends.

        Args:
            gradient_type: Which gradient to sample
            num_colors: Number of colors to generate

        Returns:
            Array of shape (num_colors, 4) with RGBA values
        """
        positions = np.linspace(0.0, 1.0, num_colors).reshape(-1, 1)
        positions_2d = positions.reshape(num_colors, 1)
        return self.apply_gradient(positions_2d, gradient_type).reshape(num_colors, 4)

    def to_qimage(
        self,
        normalized: np.ndarray,
        gradient_type: ColorGradient,
        custom_stops: List[GradientStop] | None = None,
    ):
        """Convert normalized field to QImage with gradient coloring.

        Returns a QImage in RGBA format suitable for display.
        """
        from PyQt6.QtGui import QImage

        rgba = self.apply_gradient(normalized, gradient_type, custom_stops)
        h, w = normalized.shape

        # Ensure contiguous memory layout
        rgba = np.ascontiguousarray(rgba)

        # Create QImage from RGBA data
        qimage = QImage(
            rgba.data,
            w,
            h,
            w * 4,  # bytes per line
            QImage.Format.Format_RGBA8888,
        )

        # Return a copy to ensure data lifetime
        return qimage.copy()
