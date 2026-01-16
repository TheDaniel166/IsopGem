"""Pattern detection for cymatics simulation outputs."""
from __future__ import annotations

from typing import List, Tuple

import cv2
import numpy as np
from scipy.signal import find_peaks

from ..models import DetectionMetrics, DetectionResult, SimulationResult


class CymaticsDetectionService:
    """Detects cymatics pattern features from a simulation result."""

    def detect(self, simulation: SimulationResult, nodal_threshold: float = 0.08) -> DetectionResult:
        """Extract metrics and maps from a simulation output."""
        normalized = np.clip(simulation.normalized, 0.0, 1.0)
        gray = (normalized * 255.0).astype(np.uint8)

        edges = cv2.Canny(gray, 60, 140)
        nodal_mask = (normalized < nodal_threshold).astype(np.uint8) * 255

        metrics = DetectionMetrics(
            symmetry_horizontal=self._symmetry(gray, axis=0),
            symmetry_vertical=self._symmetry(gray, axis=1),
            edge_density=float(edges.mean() / 255.0),
            radial_peaks=self._radial_peaks(gray),
            dominant_frequencies=self._dominant_frequencies(gray),
        )

        return DetectionResult(
            metrics=metrics,
            edges=edges,
            nodal_mask=nodal_mask,
        )

    def _symmetry(self, gray: np.ndarray, axis: int) -> float:
        if axis == 0:
            flipped = np.flipud(gray)
        else:
            flipped = np.fliplr(gray)
        diff = np.abs(gray.astype(np.float32) - flipped.astype(np.float32))
        return float(1.0 - np.mean(diff) / 255.0)

    def _radial_peaks(self, gray: np.ndarray) -> List[float]:
        height, width = gray.shape
        yy, xx = np.indices((height, width))
        cx = (width - 1) / 2.0
        cy = (height - 1) / 2.0
        rr = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        rr_int = rr.astype(np.int32)

        summed = np.bincount(rr_int.ravel(), gray.ravel())
        counts = np.bincount(rr_int.ravel())
        radial_profile = summed / np.maximum(counts, 1)

        if len(radial_profile) < 4:
            return []

        peak_scale = float(np.max(radial_profile))
        if peak_scale <= 1e-6:
            return []

        peaks, _ = find_peaks(radial_profile, prominence=peak_scale * 0.1)
        if peaks.size == 0:
            return []

        max_radius = float(np.max(rr_int))
        normalized_peaks = (peaks / max_radius).tolist()
        return normalized_peaks[:6]

    def _dominant_frequencies(self, gray: np.ndarray) -> List[Tuple[float, float, float]]:
        spectrum = np.fft.fftshift(np.fft.fft2(gray.astype(np.float32)))
        magnitude = np.abs(spectrum)
        height, width = magnitude.shape
        center_y = height // 2
        center_x = width // 2
        magnitude[center_y, center_x] = 0.0

        flat = magnitude.ravel()
        if flat.size < 5:
            return []

        top_indices = np.argpartition(flat, -5)[-5:]
        freqs: List[Tuple[float, float, float]] = []
        for idx in top_indices:
            y, x = np.unravel_index(idx, magnitude.shape)
            fx = (x - center_x) / width
            fy = (y - center_y) / height
            freqs.append((float(fx), float(fy), float(magnitude[y, x])))

        freqs.sort(key=lambda item: item[2], reverse=True)
        return freqs[:5]
