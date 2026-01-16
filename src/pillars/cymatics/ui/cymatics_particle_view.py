"""Particle visualization overlay for cymatics patterns.

Renders particles on top of the cymatics pattern view, showing
settled particles in gold and moving particles in gray.
"""
from __future__ import annotations

from typing import Optional

import numpy as np
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QBrush, QColor, QPainter, QPaintEvent, QPen
from PyQt6.QtWidgets import QWidget

from ..models import ParticleState


class CymaticsParticleView(QWidget):
    """Transparent overlay widget for rendering particles.

    Renders particles from a ParticleState on top of the cymatics
    pattern visualization. Settled particles are drawn in gold,
    moving particles in semi-transparent gray.

    This widget should be overlaid on top of the pattern display
    and sized to match it exactly.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        # Make widget transparent to mouse events
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        # Transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._particles: Optional[ParticleState] = None

        # Visual settings
        self._settled_color = QColor(255, 215, 0, 220)  # Gold
        self._moving_color = QColor(200, 200, 200, 150)  # Gray
        self._particle_radius = 0.8  # Tiny sand-like particles
        self._show_trails = False
        self._trail_length = 5

        # Trail history for motion blur effect
        self._position_history: list[np.ndarray] = []

    def set_particles(self, particles: ParticleState) -> None:
        """Update particle state to render."""
        # Store history for trails
        if self._show_trails and self._particles is not None:
            self._position_history.append(self._particles.positions.copy())
            if len(self._position_history) > self._trail_length:
                self._position_history.pop(0)

        self._particles = particles
        self.update()

    def clear_particles(self) -> None:
        """Clear all particles."""
        self._particles = None
        self._position_history.clear()
        self.update()

    def set_settled_color(self, color: QColor) -> None:
        """Set color for settled particles."""
        self._settled_color = color
        self.update()

    def set_moving_color(self, color: QColor) -> None:
        """Set color for moving particles."""
        self._moving_color = color
        self.update()

    def set_particle_radius(self, radius: float) -> None:
        """Set particle display radius in pixels."""
        self._particle_radius = max(0.5, min(10.0, radius))
        self.update()

    def set_show_trails(self, show: bool) -> None:
        """Enable/disable motion trails."""
        self._show_trails = show
        if not show:
            self._position_history.clear()
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Render particles."""
        if self._particles is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        positions = self._particles.positions
        settled = self._particles.settled

        # Draw trails first (underneath particles)
        if self._show_trails and self._position_history:
            self._draw_trails(painter, w, h)

        # Draw particles
        painter.setPen(Qt.PenStyle.NoPen)

        for i, (pos, is_settled) in enumerate(zip(positions, settled)):
            x = pos[0] * w
            y = pos[1] * h

            if is_settled:
                painter.setBrush(QBrush(self._settled_color))
                radius = self._particle_radius * 1.2  # Settled slightly larger
            else:
                painter.setBrush(QBrush(self._moving_color))
                radius = self._particle_radius

            painter.drawEllipse(QPointF(x, y), radius, radius)

        # Draw statistics overlay
        self._draw_stats(painter)

    def _draw_trails(self, painter: QPainter, w: int, h: int) -> None:
        """Draw fading motion trails for particles."""
        n_frames = len(self._position_history)
        if n_frames == 0:
            return

        for frame_idx, positions in enumerate(self._position_history):
            # Fade alpha based on age
            alpha = int(50 * (frame_idx + 1) / n_frames)
            trail_color = QColor(150, 150, 150, alpha)
            painter.setBrush(QBrush(trail_color))
            painter.setPen(Qt.PenStyle.NoPen)

            # Smaller radius for older positions
            radius = self._particle_radius * 0.5 * (frame_idx + 1) / n_frames

            for pos in positions:
                x = pos[0] * w
                y = pos[1] * h
                painter.drawEllipse(QPointF(x, y), radius, radius)

    def _draw_stats(self, painter: QPainter) -> None:
        """Draw particle statistics in corner."""
        if self._particles is None:
            return

        n_total = len(self._particles.positions)
        n_settled = int(np.sum(self._particles.settled))
        percent = 100 * n_settled / n_total if n_total > 0 else 0

        # Semi-transparent background for text
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 120))
        painter.drawRoundedRect(5, 5, 120, 40, 5, 5)

        # Text
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(10, 20, f"Particles: {n_total}")
        painter.drawText(10, 38, f"Settled: {n_settled} ({percent:.0f}%)")
