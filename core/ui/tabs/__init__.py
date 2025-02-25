"""
Application-specific tab implementations
"""
from .home_tab import HomeTab
from .ai_tab import AIToolsTab

# Register all tabs
TABS = [
    HomeTab,
    AIToolsTab
]
