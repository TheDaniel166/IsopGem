"""
The Liturgical Styles (Visual Liturgy Implementation).

Centralized style constants following the Visual Liturgy codex.
This module provides consistent styling across all Geometry pillar windows.
"""

# =============================================================================
# THE ALCHEMICAL SPECTRUM (Colors)
# =============================================================================

class LiturgyColors:
    """The Alchemical Spectrum - color constants from Visual Liturgy."""
    
    # Structure (Tones)
    VOID = "#0f172a"       # The Unknown - Headers, High-contrast text
    STONE = "#334155"      # The Physical - Body text
    MARBLE = "#f1f5f9"     # The Tablet - Panel backgrounds
    LIGHT = "#ffffff"      # The Illumination - Input fields
    ASH = "#cbd5e1"        # The Boundary - Borders, Dividers
    CLOUD_SLATE = "#f8fafc"  # The Substrate
    
    # Semantic Colors
    MYSTIC_VIOLET = "#8b5cf6"
    MYSTIC_VIOLET_DARK = "#7c3aed"
    MYSTIC_VIOLET_BORDER = "#6d28d9"
    
    ALCHEMICAL_GOLD = "#f59e0b"
    ALCHEMICAL_GOLD_DARK = "#d97706"
    ALCHEMICAL_GOLD_BORDER = "#b45309"
    
    EMERALD = "#10b981"
    EMERALD_DARK = "#059669"
    EMERALD_BORDER = "#047857"
    
    CRIMSON = "#ef4444"
    CRIMSON_DARK = "#b91c1c"
    CRIMSON_BORDER = "#991b1b"
    
    VOID_SLATE = "#64748b"
    VOID_SLATE_DARK = "#475569"
    VOID_SLATE_BORDER = "#334155"
    
    # Accent colors
    INDIGO_50 = "#eef2ff"
    INDIGO_100 = "#e0e7ff"
    INDIGO_200 = "#c7d2fe"
    INDIGO_700 = "#4338ca"
    INDIGO_900 = "#312e81"

# =============================================================================
# THE GLYPHS (Typography)
# =============================================================================

class LiturgyTypography:
    """Typography constants from Visual Liturgy."""
    
    # Font sizes
    SIGIL_SIZE = "28pt"      # H1 - Pillar Titles
    HEADER_SIZE = "22pt"     # H2 - Tablet Headers
    COMMAND_SIZE = "16pt"    # H3 - Actions & Inputs
    SCRIPTURE_SIZE = "11pt"  # Standard Text
    WHISPER_SIZE = "10pt"    # Tooltips & Meta-data
    
    # Font weights
    SIGIL_WEIGHT = 900       # Black
    HEADER_WEIGHT = 800      # ExtraBold
    COMMAND_WEIGHT = 800     # ExtraBold
    SCRIPTURE_WEIGHT = 400   # Regular
    WHISPER_WEIGHT = 700     # Bold

# =============================================================================
# BUTTON STYLES (The Catalysts)
# =============================================================================

class LiturgyButtons:
    """Button styles following the Catalyst semantics."""
    
    @staticmethod
    def magus() -> str:
        """The Magus - Transmute/Execute actions (Mystic Violet)."""
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #8b5cf6, stop:1 #7c3aed);
                border: 1px solid #6d28d9;
                color: white;
                border-radius: 12px;
                padding: 10px 16px;
                font-weight: 600;
                font-size: 10pt;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #a78bfa, stop:1 #8b5cf6);
            }
            QPushButton:pressed {
                background: #7c3aed;
            }
            QPushButton:disabled {
                background-color: #e2e8f0;
                border: 1px solid #cbd5e1;
                color: #94a3b8;
            }
        """
    
    @staticmethod
    def seeker() -> str:
        """The Seeker - Uncover/Reveal actions (Alchemical Gold)."""
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #f59e0b, stop:1 #d97706);
                border: 1px solid #b45309;
                color: #0f172a;
                border-radius: 12px;
                padding: 10px 16px;
                font-weight: 700;
                font-size: 10pt;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #fbbf24, stop:1 #f59e0b);
            }
            QPushButton:pressed {
                background: #d97706;
            }
        """
    
    @staticmethod
    def scribe() -> str:
        """The Scribe - Preserve/Etch actions (Emerald)."""
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #10b981, stop:1 #059669);
                border: 1px solid #047857;
                color: white;
                border-radius: 12px;
                padding: 10px 16px;
                font-weight: 600;
                font-size: 10pt;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #34d399, stop:1 #10b981);
            }
            QPushButton:pressed {
                background: #059669;
            }
        """
    
    @staticmethod
    def destroyer() -> str:
        """The Destroyer - Purge/Banish actions (Crimson)."""
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #ef4444, stop:1 #b91c1c);
                border: 1px solid #991b1b;
                color: white;
                border-radius: 12px;
                padding: 10px 16px;
                font-weight: 600;
                font-size: 10pt;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #f87171, stop:1 #ef4444);
            }
            QPushButton:pressed {
                background: #b91c1c;
            }
        """
    
    @staticmethod
    def navigator() -> str:
        """The Navigator - Traverse actions (Void Slate)."""
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #64748b, stop:1 #475569);
                border: 1px solid #334155;
                color: white;
                border-radius: 12px;
                padding: 10px 16px;
                font-weight: 600;
                font-size: 10pt;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #94a3b8, stop:1 #64748b);
            }
            QPushButton:pressed {
                background: #475569;
            }
        """
    
    @staticmethod
    def secondary() -> str:
        """Secondary button style for less prominent actions."""
        return """
            QPushButton {
                background-color: #f1f5f9;
                color: #334155;
                border: 1px solid #cbd5e1;
                border-radius: 12px;
                padding: 10px 16px;
                font-weight: 600;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
                border-color: #94a3b8;
            }
            QPushButton:pressed {
                background-color: #cbd5e1;
            }
        """

# =============================================================================
# PANEL STYLES (The Tablets)
# =============================================================================

class LiturgyPanels:
    """Panel and container styles."""
    
    @staticmethod
    def tablet() -> str:
        """The Tablet - Marble panel with liturgical shadow."""
        return """
            QFrame {
                background-color: #f1f5f9;
                border: 1px solid #cbd5e1;
                border-radius: 24px;
            }
        """
    
    @staticmethod
    def calculation_pane() -> str:
        """Left calculation pane styling."""
        return """
            QWidget {
                background-color: #f1f5f9;
            }
        """
    
    @staticmethod
    def viewport_container() -> str:
        """Viewport container with marble background."""
        return """
            QFrame {
                background-color: #f1f5f9;
                border: 1px solid #cbd5e1;
                border-radius: 24px;
            }
        """
    
    @staticmethod
    def controls_pane() -> str:
        """Right controls pane styling."""
        return """
            QWidget {
                background-color: #f1f5f9;
            }
        """

    @staticmethod
    def info_card() -> str:
        """Blue info/help card styling."""
        return """
            QFrame {
                background-color: #eff6ff;
                border: 1px solid #dbeafe;
                border-radius: 16px;
            }
        """

# =============================================================================
# INPUT STYLES (The Vessel)
# =============================================================================

class LiturgyInputs:
    """Input field styles."""
    
    @staticmethod
    def vessel() -> str:
        """The Vessel - Standard input field."""
        return """
            QLineEdit {
                font-size: 11pt;
                padding: 8px 12px;
                border: 1px solid #cbd5e1;
                border-radius: 12px;
                background-color: white;
                color: #0f172a;
            }
            QLineEdit:focus {
                border-color: #8b5cf6;
                border-width: 2px;
                padding: 7px 11px;
            }
        """
    
    @staticmethod
    def vessel_readonly() -> str:
        """Read-only input field."""
        return """
            QLineEdit {
                font-size: 11pt;
                padding: 8px 12px;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                background-color: #f8fafc;
                color: #64748b;
            }
        """
    
    @staticmethod
    def property_card_editable() -> str:
        """Editable property card (amber accent)."""
        return """
            QFrame {
                background-color: #fffbeb;
                border: 1px solid #fcd34d;
                border-radius: 16px;
            }
            QFrame:hover {
                border-color: #fbbf24;
            }
        """
    
    @staticmethod
    def property_card_readonly() -> str:
        """Read-only property card (slate accent)."""
        return """
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
            QFrame:hover {
                border-color: #cbd5e1;
                background-color: #f1f5f9;
            }
        """

    @staticmethod
    def property_card_solved() -> str:
        """Solved property card (green accent)."""
        return """
            QFrame {
                background-color: #f0fdf4;
                border: 1px solid #86efac;
                border-radius: 16px;
            }
        """

# =============================================================================
# TOOLBAR STYLES
# =============================================================================

class LiturgyToolbar:
    """Toolbar and layout control styles."""
    
    @staticmethod
    def bar() -> str:
        """Layout toolbar background."""
        return """
            QFrame {
                background-color: #eef2ff;
                border-bottom: 1px solid #e2e8f0;
            }
        """
    
    @staticmethod
    def toggle_button() -> str:
        """Toggle button for layout controls."""
        return """
            QPushButton {
                background-color: #e0e7ff;
                color: #312e81;
                padding: 8px 14px;
                border: 1px solid #c7d2fe;
                border-radius: 999px;
                font-weight: 600;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #c7d2fe;
            }
            QPushButton:checked {
                background-color: #a5b4fc;
            }
        """

# =============================================================================
# TAB WIDGET STYLES
# =============================================================================

class LiturgyTabs:
    """Tab widget styles."""
    
    @staticmethod
    def standard() -> str:
        """Standard tab widget styling."""
        return """
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                background-color: white;
            }
            QTabBar::tab {
                padding: 8px 16px;
                margin-right: 4px;
                border-radius: 8px;
                color: #64748b;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background: #e0e7ff;
                color: #312e81;
            }
            QTabBar::tab:hover:!selected {
                background: #f1f5f9;
            }
            QTabBar::scroller {
                width: 0px;
            }
            QTabBar QToolButton {
                background: transparent;
                border: none;
                width: 0px;
                height: 0px;
            }
        """

# =============================================================================
# SCROLL AREA STYLES
# =============================================================================

class LiturgyScrollArea:
    """Scroll area styles."""
    
    @staticmethod
    def standard() -> str:
        """Standard scroll area with styled scrollbar."""
        return """
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f5f9;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
        """

# =============================================================================
# MENU STYLES
# =============================================================================

class LiturgyMenus:
    """Menu styles."""
    
    @staticmethod
    def standard() -> str:
        """Standard context menu styling."""
        return """
            QMenu {
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 24px;
                border-radius: 4px;
                color: #0f172a;
            }
            QMenu::item:selected {
                background-color: #f1f5f9;
                color: #0f172a;
            }
            QMenu::separator {
                height: 1px;
                background: #e2e8f0;
                margin: 4px 0;
            }
        """

