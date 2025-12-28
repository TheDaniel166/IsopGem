"""
Mindscape Theme - The Visual Palette.
Color and font palettes for Dark, Light, and Egyptian graph themes.
"""
from PyQt6.QtGui import QColor, QFont

PALETTES = {
    "Dark": {
        "background": "#1e1e2e",
        "node_concept": "#3b82f6",  # Blue
        "node_system": "#ef4444",   # Red
        "node_jump": "#8b5cf6",     # Purple
        "node_document": "#10b981", # Emerald
        "node_default": "#64748b",  # Slate
        "node_gradient_start": "#282832",
        "node_gradient_end": "#0a0a14",
        "edge_parent": "#64a0d2",   # Electric Blue
        "edge_jump": "#8282d2",     # Purple-ish
        "text_main": "#ffffff",
        "glow_hover": "#ffffff",    # With alpha in logic
        "glow_selected": "#6496ff"
    },
    "Light": {
        "background": "#f8fafc",
        "node_concept": "#2563eb",  # Darker Blue
        "node_system": "#dc2626",   # Darker Red
        "node_jump": "#7c3aed",     # Darker Purple
        "node_document": "#059669", # Darker Emerald
        "node_default": "#475569",
        "node_gradient_start": "#ffffff",
        "node_gradient_end": "#e2e8f0",
        "edge_parent": "#3b82f6",
        "edge_jump": "#8b5cf6",
        "text_main": "#1e293b",     # Dark Slate
        "glow_hover": "#3b82f6",
        "glow_selected": "#2563eb"
    },
    "Egyptian": {
        "background": "#1c1917",    # Warm Black (Stone)
        "node_concept": "#eab308",  # Gold
        "node_system": "#f43f5e",   # Rose
        "node_jump": "#06b6d4",     # Cyan (Nile)
        "node_document": "#84cc16", # Lime
        "node_default": "#78716c",  # Stone
        "node_gradient_start": "#292524",
        "node_gradient_end": "#1c1917",
        "edge_parent": "#d6b560",   # Gold
        "edge_jump": "#0891b2",     # Cyan
        "text_main": "#fef3c7",     # Amber White
        "glow_hover": "#fcd34d",    # Gold Glow
        "glow_selected": "#fbbf24"
    }
}

class GraphTheme:
    """
    Graph Theme class definition.
    
    Attributes:
        mode: Description of mode.
        palette: Description of palette.
    
    """
    def __init__(self, mode: str = "Dark") -> None:
        """
          init   logic.
        
        Args:
            mode: Description of mode.
        
        Returns:
            Result of __init__ operation.
        """
        self.mode = mode
        self.palette = PALETTES.get(mode, PALETTES["Dark"])

    def set_mode(self, mode: str) -> None:
        """
        Configure mode logic.
        
        Args:
            mode: Description of mode.
        
        Returns:
            Result of set_mode operation.
        """
        if mode in PALETTES:
            self.mode = mode
            self.palette = PALETTES[mode]

    def get_color(self, key: str) -> QColor:
        """
        Retrieve color logic.
        
        Args:
            key: Description of key.
        
        Returns:
            Result of get_color operation.
        """
        hex_code = self.palette.get(key, "#ff00ff") # Magenta default for error
        return QColor(hex_code)

    def get_font(self, style="body") -> QFont:
        # We could map styles to specific fonts here
        """
        Retrieve font logic.
        
        Args:
            style: Description of style.
        
        Returns:
            Result of get_font operation.
        """
        if self.mode == "Egyptian":
            font = QFont("Georgia", 10) # Serif for ancient feel
        else:
            font = QFont("Arial", 10)   # Sans for modern
            
        if style == "header":
            font.setBold(True)
            font.setPointSize(12)
        elif style == "bold":
            font.setBold(True)
            
        return font