"""
AI Panel registration
"""
from ..registry import get_registry
from .console_panel import ConsolePanel
from .test_panel import AITestPanel

# Register panel factories
registry = get_registry()
registry.register("Console", lambda: ConsolePanel())
registry.register("AITest", lambda: AITestPanel())

__all__ = ['ConsolePanel', 'AITestPanel']
