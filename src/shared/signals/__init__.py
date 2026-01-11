"""Shared signals package for cross-module communication.

This package provides PyQt signal buses that enable decoupled communication
between pillars without creating import dependencies.
"""
from .navigation_bus import navigation_bus, NavigationBus
from .gematria_bus import gematria_bus, GematriaBus

__all__ = ['navigation_bus', 'NavigationBus', 'gematria_bus', 'GematriaBus']
