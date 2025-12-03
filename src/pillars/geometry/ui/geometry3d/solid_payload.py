"""Backward-compatible shim re-exporting shared solid payload types."""

from ...shared.solid_payload import Edge, Face, SolidLabel, SolidPayload, Vec3

__all__ = [
    'Edge',
    'Face',
    'SolidLabel',
    'SolidPayload',
    'Vec3',
]
