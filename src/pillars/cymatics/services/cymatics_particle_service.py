"""Particle simulation service for cymatics sand visualization.

Simulates particles (like sand or salt) accumulating at nodal lines
on a vibrating plate, mimicking real Chladni figure experiments.
"""
from __future__ import annotations

from typing import Optional
import numpy as np
from scipy import ndimage

from ..models import ParticleState


class CymaticsParticleService:
    """Simulates particles accumulating at nodal lines.

    Particles experience force proportional to the negative gradient
    of the amplitude field, causing them to drift toward regions of
    low amplitude (nodal lines) where they eventually settle.

    This mimics the physics of sand particles on a vibrating Chladni
    plate, which accumulate at the nodal lines where the plate
    displacement is minimal.
    """

    def __init__(self, seed: int | None = None):
        """Initialize particle service.

        Args:
            seed: Optional random seed for reproducible particle positions
        """
        self._rng = np.random.default_rng(seed)

    def initialize_particles(
        self,
        count: int,
        grid_size: int,
        distribution: str = "uniform",
        boundary_mask: Optional[np.ndarray] = None,
    ) -> ParticleState:
        """Initialize particles within the plate boundary."""
        positions_list = []
        
        # Limit iterations to avoid infinite loops if mask is too small
        max_iter = 100
        iteration = 0

        while len(positions_list) < count and iteration < max_iter:
            iteration += 1
            # Generate candidates (extra to account for rejection)
            if hasattr(self, '_rng'):
                candidates = self._rng.random((count * 2, 2))
            else:
                candidates = np.random.rand(count * 2, 2)

            if boundary_mask is not None:
                # Map [0, 1] to grid coordinates
                x_idx = np.floor(candidates[:, 0] * (grid_size - 1)).astype(int)
                y_idx = np.floor(candidates[:, 1] * (grid_size - 1)).astype(int)
                
                # Clip to safe range
                x_idx = np.clip(x_idx, 0, grid_size - 1)
                y_idx = np.clip(y_idx, 0, grid_size - 1)
                
                # Filter by mask (Vectorized)
                # Note: boundary_mask indices are [y, x]
                valid = boundary_mask[y_idx, x_idx]
                candidates = candidates[valid]

            positions_list.extend(candidates.tolist())

        # If we failed to find enough valid spots, fill remainder with center
        if len(positions_list) < count:
            remaining = count - len(positions_list)
            center_fill = np.full((remaining, 2), 0.5)
            positions_list.extend(center_fill.tolist())

        positions = np.array(positions_list[:count])
        velocities = np.zeros_like(positions)
        settled = np.zeros(count, dtype=bool)

        return ParticleState(
            positions=positions,
            velocities=velocities,
            settled=settled,
        )

    def update_particles(
        self,
        state: ParticleState,
        field: np.ndarray,
        dt: float = 0.016,
        speed: float = 0.5,
        settle_threshold: float = 0.03,
        damping: float = 0.92,
        noise: float = 0.02,
        boundary_mask: Optional[np.ndarray] = None,
    ) -> ParticleState:
        """Update particle positions based on field gradient, with boundary clipping."""
        if state.positions.shape[0] == 0:
            return state

        grid_size = field.shape[0]  # Assume square grid

        # Compute potential as abs(field) to move towards nodes (zeros)
        potential = np.abs(field)

        # Compute gradients of potential
        grad_y, grad_x = np.gradient(potential)

        # Particle positions in grid coordinates (float)
        x = state.positions[:, 0] * (grid_size - 1)
        y = state.positions[:, 1] * (grid_size - 1)

        # Interpolate gradients at particle positions
        force_x = ndimage.map_coordinates(grad_x, [y, x], order=1, mode='nearest')
        force_y = ndimage.map_coordinates(grad_y, [y, x], order=1, mode='nearest')

        # Force = -grad(potential) to move towards lower potential (nodal lines)
        force = np.stack((-force_x, -force_y), axis=1)  # (N, 2)

        # Normalize and scale force
        mag = np.linalg.norm(force, axis=1, keepdims=True)
        # Avoid division by zero
        force = np.where(mag > 1e-6, force / mag * speed, 0)

        # Update velocities with force and friction
        # Use friction damping from user code (0.95) or passed parameter? 
        # User code had hardcoded 0.95
        new_vel = state.velocities + force * dt
        new_vel *= 0.95  # Friction damping to prevent perpetual motion

        # Update positions
        new_pos = state.positions + new_vel * dt

        # Boundary handling
        if boundary_mask is not None:
            # First, clip to [0,1] to prevent out-of-bounds
            new_pos = np.clip(new_pos, 0, 1)

            # Compute grid indices for new positions
            x_idx = np.floor(new_pos[:, 0] * (grid_size - 1)).astype(int)
            y_idx = np.floor(new_pos[:, 1] * (grid_size - 1)).astype(int)

            # Clamp indices to valid range
            x_idx = np.clip(x_idx, 0, grid_size - 1)
            y_idx = np.clip(y_idx, 0, grid_size - 1)

            # Check if outside the plate shape
            # Note: boundary_mask indices are [y, x]
            outside = ~boundary_mask[y_idx, x_idx]

            # For particles outside, revert position and reflect velocity with energy loss
            new_pos[outside] = state.positions[outside]
            new_vel[outside] = -new_vel[outside] * 0.8  # Bounce with 20% energy loss

        # Calculate settled status (low velocity check)
        velocity_mag = np.linalg.norm(new_vel, axis=1)
        settled = velocity_mag < 0.1

        # Return updated state
        return ParticleState(
            positions=new_pos,
            velocities=new_vel,
            settled=settled,
        )


    def reset_settled(self, state: ParticleState) -> ParticleState:
        """Reset settled status for all particles.

        Useful when simulation parameters change significantly.
        """
        return ParticleState(
            positions=state.positions.copy(),
            velocities=state.velocities.copy(),
            settled=np.zeros(len(state.positions), dtype=bool),
        )

    def get_statistics(self, state: ParticleState) -> dict:
        """Get particle simulation statistics.

        Returns:
            Dictionary with particle stats
        """
        n_total = len(state.positions)
        n_settled = int(np.sum(state.settled))
        avg_velocity = float(np.mean(np.linalg.norm(state.velocities, axis=1)))

        return {
            "total": n_total,
            "settled": n_settled,
            "moving": n_total - n_settled,
            "settled_percent": 100 * n_settled / n_total if n_total > 0 else 0,
            "avg_velocity": avg_velocity,
        }
