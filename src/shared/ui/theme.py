"""Modern UI theme and styling for IsopGem application.

Aligned with Visual Liturgy v2.2 - "The Codex of IsopGem"
"""

# ═══════════════════════════════════════════════════════════════════════════════
# Rule: No widget in ui/ may define hex colors directly. All color must come from COLORS.
# The Alchemical Spectrum (Visual Liturgy §2)
# ═══════════════════════════════════════════════════════════════════════════════

COLORS = {
    # ═══════════════════════════════════════════════════════════════════════════════
    # 1. The Structure (Canon Tones)
    # ═══════════════════════════════════════════════════════════════════════════════
    'void': '#0f172a',           # The Unknown (Headers, High-contrast text)
    'stone': '#334155',          # The Physical (Body text, Scrollbar handles)
    'mist': '#94a3b8',           # The Ephemeral (Disabled text, Placeholders)
    'ash': '#cbd5e1',            # The Boundary (Borders, Dividers)
    'marble': '#f1f5f9',         # The Tablet (Panel Backgrounds)
    'cloud': '#f8fafc',          # The Substrate (Window Background)
    'light': '#ffffff',          # The Illumination (Input Fields - The Vessel)

    # ═══════════════════════════════════════════════════════════════════════════════
    # 2. The Catalysts (Archetypes)
    # ═══════════════════════════════════════════════════════════════════════════════
    # Magus (Violet) - Transmute / Execute
    'magus': '#6d28d9',
    'magus_hover': '#7c3aed',
    'magus_dark': '#5b21b6',
    'magus_border': '#4c1d95',
    'magus_soft': '#ede9fe',
    'magus_mute': '#c4b5fd',

    # Seeker (Gold) - Uncover / Reveal
    'seeker': '#f59e0b',
    'seeker_hover': '#fbbf24',
    'seeker_dark': '#d97706',
    'seeker_border': '#b45309',
    'seeker_soft': '#fef3c7',
    'seeker_text_disabled': '#92400e',
    'seeker_mute': '#fcd34d',

    # Scribe (Emerald) - Preserve / Etch
    'scribe': '#10b981',
    'scribe_hover': '#34d399',
    'scribe_dark': '#059669',
    'scribe_border': '#047857',
    'scribe_soft': '#d1fae5',
    'scribe_text_disabled': '#065f46',
    'scribe_mute': '#6ee7b7',

    # Destroyer (Crimson) - Purge / Banish
    'destroyer': '#ef4444',
    'destroyer_hover': '#f87171',
    'destroyer_dark': '#b91c1c',
    'destroyer_border': '#991b1b',
    'destroyer_soft': '#fee2e2',
    'destroyer_mute': '#fca5a5',

    # Navigator (Slate) - Traverse / Neutral
    'navigator': '#64748b',
    'navigator_hover': '#94a3b8', # Matches Mist
    'navigator_dark': '#475569',
    'navigator_border': '#334155', # Matches Stone
    'navigator_soft': '#e2e8f0',
    'navigator_mute': '#cbd5e1',   # Matches Ash

    # ═══════════════════════════════════════════════════════════════════════════════
    # 3. Focus & Status
    # ═══════════════════════════════════════════════════════════════════════════════
    'focus': '#3b82f6',          # Azure
    'success': '#10b981',        # Scribe
    'warning': '#f59e0b',        # Seeker
    'error': '#ef4444',          # Destroyer
    'info': '#3b82f6',           # Azure

    # ═══════════════════════════════════════════════════════════════════════════════
    # 4. Legacy / Aliases (For Backward Compatibility)
    # ═══════════════════════════════════════════════════════════════════════════════
    'background': '#f8fafc',     # Cloud
    'background_alt': '#f1f5f9', # Marble
    'surface': '#f1f5f9',        # Marble
    'surface_hover': '#e2e8f0',  # Navigator Soft
    
    'text_primary': '#0f172a',   # Void
    'text_secondary': '#334155', # Stone
    'text_disabled': '#94a3b8',  # Mist
    
    'border': '#cbd5e1',         # Ash
    'border_focus': '#3b82f6',   # Focus

    'primary': '#6d28d9',        # Magus
    'primary_hover': '#7c3aed',  # Magus Hover
    'primary_pressed': '#5b21b6',# Magus Dark
    'primary_light': '#ddd6fe',  # Magus Light (Selection)
    
    'accent': '#10b981',         # Scribe
    'accent_hover': '#34d399',   # Scribe Hover
    'accent_pressed': '#059669', # Scribe Dark
}

# ═══════════════════════════════════════════════════════════════════════════════


def get_app_stylesheet() -> str:
    """
    Get the complete application stylesheet.
    
    Returns:
        QSS stylesheet string
    """
    return f"""
    /* Global styles */
    * {{
        /* Codex: Inter-first, with pragmatic fallbacks */
        font-family: 'Inter', 'Roboto', 'Helvetica Neue', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
    }}
    
    QMainWindow, QDialog, QWidget {{
        background-color: {COLORS['cloud']};
        color: {COLORS['void']};
    }}
    
    /* Buttons - Neutral base (semantic meaning requires archetype) */
    QPushButton {{
        background-color: {COLORS['marble']};
        color: {COLORS['stone']};
        border: 1px solid {COLORS['ash']};
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 11pt;
        font-weight: 500;
        min-height: 36px;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS['surface_hover']};
        border-color: {COLORS['stone']};
    }}
    
    QPushButton:pressed {{
        background-color: {COLORS['ash']};
    }}
    
    QPushButton:disabled {{
        background-color: {COLORS['ash']};
        color: {COLORS['mist']};
        border-color: {COLORS['ash']};
    }}
    
    QPushButton:focus {{
        border: 2px solid {COLORS['focus']};
        padding: 7px 15px; /* compensate for thicker focus ring */
    }}

    /* ─────────────────────────────────────────────────────────────────────────
       ARCHETYPE STYLES (Centralized)
       Usage: button.setProperty("archetype", "magus")
       ───────────────────────────────────────────────────────────────────────── */
    
    /* Magus (Violet) - Transmute / Execute */
    QPushButton[archetype="magus"] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['magus']}, stop:1 {COLORS['magus_dark']});
        border: 1px solid {COLORS['magus_border']};
        color: {COLORS['light']}; /* White text works on dark violet */
        font-weight: 700;
        border-radius: 8px;
        font-size: 11pt;
    }}
    QPushButton[archetype="magus"]:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['magus_hover']}, stop:1 {COLORS['magus']});
    }}
    QPushButton[archetype="magus"]:pressed {{
        background: {COLORS['magus_dark']};
    }}
    QPushButton[archetype="magus"]:disabled {{
        background: {COLORS['magus_soft']};
        color: {COLORS['magus']}; /* Dark violet text on light background */
        border: 1px solid {COLORS['magus_mute']};
    }}

    /* Seeker (Gold) - Uncover / Reveal */
    QPushButton[archetype="seeker"] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['seeker']}, stop:1 {COLORS['seeker_dark']});
        border: 1px solid {COLORS['seeker_border']};
        color: {COLORS['void']};
        font-weight: 700;
        border-radius: 8px;
    }}
    QPushButton[archetype="seeker"]:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['seeker_hover']}, stop:1 {COLORS['seeker']});
    }}
    QPushButton[archetype="seeker"]:pressed {{
        background: {COLORS['seeker_dark']};
    }}
    QPushButton[archetype="seeker"]:disabled {{
        background: {COLORS['seeker_soft']};
        color: {COLORS['seeker_text_disabled']};
        border: 1px solid {COLORS['seeker_mute']};
    }}

    /* Scribe (Emerald) - Preserve / Etch */
    QPushButton[archetype="scribe"] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['scribe']}, stop:1 {COLORS['scribe_dark']});
        border: 1px solid {COLORS['scribe_border']};
        color: {COLORS['light']}; /* White text works on dark emerald */
        font-weight: 600;
        border-radius: 8px;
    }}
    QPushButton[archetype="scribe"]:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['scribe_hover']}, stop:1 {COLORS['scribe']});
    }}
    QPushButton[archetype="scribe"]:pressed {{
        background: {COLORS['scribe_dark']};
    }}
    QPushButton[archetype="scribe"]:disabled {{
        background: {COLORS['scribe_soft']};
        color: {COLORS['scribe_dark']}; /* Dark emerald text on light background */
        border: 1px solid {COLORS['scribe_mute']};
    }}

    /* Destroyer (Crimson) - Purge / Banish */
    QPushButton[archetype="destroyer"] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['destroyer']}, stop:1 {COLORS['destroyer_dark']});
        border: 1px solid {COLORS['destroyer_border']};
        color: {COLORS['light']}; /* White text works on dark crimson */
        font-weight: 600;
        border-radius: 8px;
    }}
    QPushButton[archetype="destroyer"]:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['destroyer_hover']}, stop:1 {COLORS['destroyer']});
    }}
    QPushButton[archetype="destroyer"]:pressed {{
        background: {COLORS['destroyer_dark']};
    }}
    QPushButton[archetype="destroyer"]:disabled {{
        background: {COLORS['destroyer_soft']};
        color: {COLORS['destroyer_dark']}; /* Dark crimson text on light background */
        border: 1px solid {COLORS['destroyer_mute']};
    }}

    /* Navigator (Slate) - Adaptive for light/dark contexts */
    /* High-contrast dark buttons for visibility on light surfaces */
    QPushButton[archetype="navigator"] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1e293b, stop:1 #0f172a);
        border: 2px solid #0f172a;
        color: {COLORS['light']};
        font-weight: 600;
        border-radius: 8px;
        min-width: 36px;
        min-height: 36px;
    }}
    QPushButton[archetype="navigator"]:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['stone']}, stop:1 #1e293b);
        border-color: {COLORS['seeker']}; /* Amber glow on hover */
    }}
    QPushButton[archetype="navigator"]:pressed {{
        background: {COLORS['void']};
        border-color: {COLORS['seeker_dark']};
    }}
    QPushButton[archetype="navigator"]:disabled {{
        background: {COLORS['navigator_soft']};
        color: {COLORS['navigator']};
        border: 1px solid {COLORS['navigator_mute']};
    }}

    /* Ghost (Subtle / Non-semantic) */
    QPushButton[archetype="ghost"] {{
        background: transparent;
        border: 1px solid transparent;
        color: {COLORS['stone']};
        font-weight: 500;
        border-radius: 8px;
    }}
    QPushButton[archetype="ghost"]:hover {{
        background: {COLORS['surface_hover']};
        color: {COLORS['void']};
    }}
    QPushButton[archetype="ghost"]:pressed {{
        background: {COLORS['ash']};
    }}
    QPushButton[archetype="ghost"]:disabled {{
        color: {COLORS['mist']};
        background: transparent;
        border-color: transparent;
    }}
    
    QPushButton:flat {{
        background-color: transparent;
        color: {COLORS['void']};
    }}
    
    QPushButton:flat:hover {{
        background-color: {COLORS['surface_hover']};
    }}
    
    /* Input fields (Vessel is Light) */
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background-color: {COLORS['light']};
        border: 2px solid {COLORS['ash']};
        border-radius: 8px; /* Canon radius for vessels */
        padding: 8px 12px;
        min-height: 40px;
        color: {COLORS['void']};
        font-size: 11pt;
        selection-background-color: {COLORS['magus_soft']};
    }}
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border: 2px solid {COLORS['focus']};
        background-color: {COLORS['light']};
    }}
    
    QLineEdit:disabled, QTextEdit:disabled {{
        background-color: {COLORS['marble']};
        color: {COLORS['mist']};
    }}
    
    /* Combo boxes */
    QComboBox {{
        background-color: {COLORS['light']};
        border: 2px solid {COLORS['ash']};
        border-radius: 8px;
        padding: 8px 12px;
        min-height: 40px;
        color: {COLORS['void']};
    }}
    
    QComboBox:hover {{
        border-color: {COLORS['focus']};
    }}
    
    QComboBox::drop-down {{
        border: none;
        padding-right: 8px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid {COLORS['stone']};
        margin-right: 8px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {COLORS['light']};
        border: 2px solid {COLORS['ash']};
        border-radius: 8px;
        selection-background-color: {COLORS['seeker_soft']};
        selection-color: {COLORS['seeker_dark']};
        padding: 4px;
    }}
    
    /* Checkboxes */
    QCheckBox {{
        color: {COLORS['void']};
        spacing: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {COLORS['ash']};
        border-radius: 4px;
        background-color: {COLORS['light']};
    }}
    
    QCheckBox::indicator:hover {{
        border-color: {COLORS['focus']};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {COLORS['magus']};
        border-color: {COLORS['magus']};
        image: none;
    }}
    
    /* Lists and Trees */
    QListView, QTreeView {{
        background-color: {COLORS['light']};
        border: 1px solid {COLORS['ash']};
        border-radius: 8px;
        color: {COLORS['void']};
        outline: none;
    }}
    
    QListView::item, QTreeView::item {{
        padding: 4px;
        border-bottom: 1px solid transparent;
    }}
    
    QListView::item:selected, QTreeView::item:selected {{
        background-color: {COLORS['magus_soft']};
        color: {COLORS['magus']};
        border: none;
    }}

    QListView::item:hover, QTreeView::item:hover {{
        background-color: {COLORS['surface_hover']};
    }}

    /* Tables */
    QTableWidget {{
        background-color: {COLORS['light']};
        border: 1px solid {COLORS['ash']};
        border-radius: 8px;
        gridline-color: {COLORS['ash']};
        selection-background-color: {COLORS['magus_soft']};
        selection-color: {COLORS['magus']};
    }}
    
    QTableWidget::item {{
        padding: 8px;
        border-bottom: 1px solid {COLORS['ash']};
    }}
    
    QTableWidget::item:selected {{
        background-color: {COLORS['magus_soft']};
        color: {COLORS['magus']};
    }}
    
    QHeaderView::section {{
        background-color: {COLORS['marble']};
        padding: 10px 8px;
        border: none;
        border-bottom: 2px solid {COLORS['ash']};
        border-right: 1px solid {COLORS['ash']};
        font-weight: 600;
        color: {COLORS['void']};
    }}
    
    QTableWidget::item:alternate {{
        background-color: {COLORS['marble']};
    }}
    
    /* Tab widget - Celestial Tabs (Light) */
    QTabWidget::pane {{
        border: none;
        background-color: {COLORS['marble']};
    }}
    
    QTabWidget::tab-bar {{
        alignment: left;
    }}
    
    QTabBar {{
        background: {COLORS['marble']};
    }}
    
    QTabBar::tab {{
        background: transparent;
        color: {COLORS['mist']};
        border: none;
        padding: 12px 20px;
        margin: 0;
        font-size: 11pt;
        font-weight: 600;
        min-width: 120px;
        text-align: center;
        border-bottom: 2px solid transparent;
    }}
    
    QTabBar::tab:selected {{
        color: {COLORS['void']};
        border-bottom: 3px solid {COLORS['seeker']}; /* Gold underline per Celestial Tabs */
        background: rgba(0, 0, 0, 0.02);
    }}
    
    QTabBar::tab:hover:!selected {{
        color: {COLORS['stone']};
        border-bottom: 2px solid {COLORS['navigator']};
        background: rgba(0, 0, 0, 0.01);
    }}
    
    QTabBar::tab:first {{
        border-top-left-radius: 8px;
        border-bottom-left-radius: 0;
    }}
    
    QTabBar::tab:last {{
        border-top-right-radius: 8px;
        border-bottom-right-radius: 0;
    }}
    
    /* Scroll bars */
    QScrollBar:vertical {{
        background-color: {COLORS['marble']};
        width: 12px;
        border-radius: 6px;
        margin: 0;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {COLORS['stone']};
        border-radius: 6px;
        min-height: 30px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['mist']};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QScrollBar:horizontal {{
        background-color: {COLORS['marble']};
        height: 12px;
        border-radius: 6px;
        margin: 0;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {COLORS['stone']};
        border-radius: 6px;
        min-width: 30px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {COLORS['mist']};
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    
    /* Labels - CRITICAL: Must be dark text for light mode visibility */
    QLabel {{
        color: {COLORS['void']}; /* Dark text: #0f172a */
        background-color: transparent;
    }}
    
    /* Force dark text for labels in light containers */
    QWidget QLabel, QFrame QLabel, QGroupBox QLabel {{
        color: {COLORS['void']};
    }}
    
    /* GroupBox titles specifically */
    QGroupBox {{
        color: {COLORS['void']};
    }}
    
    /* Splitter */
    QSplitter::handle {{
        background-color: {COLORS['ash']};
    }}
    
    QSplitter::handle:horizontal {{
        width: 2px;
    }}
    
    QSplitter::handle:vertical {{
        height: 2px;
    }}
    
    /* Message boxes */
    QMessageBox {{
        background-color: {COLORS['marble']};
    }}
    
    /* Tooltips */
    QToolTip {{
        background-color: {COLORS['void']};
        color: {COLORS['light']};
        border: none;
        border-radius: 4px;
        padding: 6px 10px;
        font-size: 10pt;
    }}
    """


def get_scrollable_tab_bar_style() -> str:
    """Scoped QSS for the scrollable tab bar (scroll area + horizontal scrollbar)."""
    scrollbar_handle = COLORS['stone']
    scrollbar_bg = COLORS['void']
    return f"""
        QScrollArea#scrollable_tab_area {{
            background: transparent;
            border: none;
        }}
        QScrollBar#scrollable_tab_scrollbar:horizontal {{
            border: none;
            background: {scrollbar_bg};
            height: 12px;
            margin: 0px 0px 0px 0px;
            border-radius: 6px;
        }}
        QScrollBar#scrollable_tab_scrollbar::handle:horizontal {{
            background: {scrollbar_handle};
            min-width: 20px;
            border-radius: 6px;
        }}
        QScrollBar#scrollable_tab_scrollbar::add-line:horizontal,
        QScrollBar#scrollable_tab_scrollbar::sub-line:horizontal {{
            width: 0px;
            border: none;
            background: none;
        }}
        QScrollBar#scrollable_tab_scrollbar::add-page:horizontal,
        QScrollBar#scrollable_tab_scrollbar::sub-page:horizontal {{
            background: none;
        }}
    """


def get_scrollable_tab_button_style(active: bool) -> str:
    """Button style for scrollable tab bar; active uses Seeker underline."""
    active_color = COLORS['seeker']
    text_active = COLORS['light']
    text_dim = COLORS['mist']
    bg_hover = "rgba(255, 255, 255, 0.05)"

    if active:
        return f"""
            QPushButton {{
                color: {text_active};
                background-color: transparent;
                border: none;
                border-bottom: 2px solid {active_color};
                padding: 8px 16px;
                font-weight: bold;
            }}
        """

    return f"""
        QPushButton {{
            color: {text_dim};
            background-color: transparent;
            border: none;
            border-bottom: 2px solid transparent;
            padding: 8px 16px;
        }}
        QPushButton:hover {{
            color: {text_active};
            background-color: {bg_hover};
        }}
    """


def get_exegesis_toolbar_style() -> str:
    """Toolbar styling for Exegesis header (floating panel)."""
    return f"""
        QFrame#FloatingHeader {{
            background-color: {COLORS['light']};
            border: 1px solid {COLORS['border']};
            border-radius: 16px;
        }}
        QLabel {{ font-family: 'Inter'; font-weight: 600; color: {COLORS['text_secondary']}; }}
        QComboBox {{ 
            background: {COLORS['light']}; border: 1px solid {COLORS['border']}; padding: 4px; border-radius: 6px; 
        }}
        QPushButton {{
            background-color: {COLORS['light']}; border: 1px solid {COLORS['border']}; border-radius: 6px; padding: 6px 12px; font-weight: 600; color: {COLORS['text_secondary']};
        }}
        QPushButton:hover {{ background-color: {COLORS['surface_hover']}; border-color: {COLORS['navigator_border']}; }}
    """


def get_exegesis_tab_style() -> str:
    """Tab widget styling for Exegesis floating panels."""
    return f"""
        QTabWidget::pane {{
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            background: {COLORS['surface']};
            top: -1px;
        }}
        QTabBar::tab {{
            background: {COLORS['surface_hover']};
            border: 1px solid {COLORS['border']};
            padding: 8px 16px;
            margin-right: 4px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            color: {COLORS['text_secondary']};
        }}
        QTabBar::tab:selected {{
            background: {COLORS['light']};
            border-color: {COLORS['border']};
            border-bottom-color: {COLORS['light']};
            font-weight: 700;
            color: {COLORS['text_primary']};
        }}
    """


def get_exegesis_group_style(title_top: int = 12) -> str:
    """Group box styling for Exegesis panels."""
    return f"""
        QGroupBox {{
            font-weight: bold;
            font-size: 11pt;
            border: 2px solid {COLORS['border']};
            border-radius: 8px;
            margin-top: {title_top}px;
            padding-top: 12px;
            padding-left: 8px;
            padding-right: 8px;
            color: {COLORS['void']}; /* Dark text for titles */
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px;
            color: {COLORS['void']}; /* Dark text for group title */
        }}
    """


def get_status_muted_style() -> str:
    """Muted status label styling."""
    return f"color: {COLORS['text_secondary']}; font-style: italic; margin-left: 8px;"


def get_card_style() -> str:
    """Get style for compact cards (12px radius, light border)."""
    return f"""
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 16px;
        color: {COLORS['void']}; /* Ensure dark text on light surface */
    """


def get_tablet_style() -> str:
    """Get style for large tablets (24px radius) without shadow."""
    return f"""
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 24px;
        padding: 24px;
        color: {COLORS['void']}; /* Ensure dark text on light surface */
    """


def apply_tablet_shadow(widget):
    """Apply the standard tablet shadow (blur 24, offset 8)."""
    from PyQt6.QtWidgets import QGraphicsDropShadowEffect
    from PyQt6.QtGui import QColor

    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(24)
    shadow.setOffset(0, 8)
    shadow.setColor(QColor(0, 0, 0, 80))
    widget.setGraphicsEffect(shadow)


def set_archetype(widget, name: str):
    """Apply an archetype property and refresh the widget style (avoids Qt polish bugs)."""
    widget.setProperty("archetype", name)
    if widget.style():
        widget.style().unpolish(widget)
        widget.style().polish(widget)


def get_title_style(size: int = 24) -> str:
    """Get style for title labels."""
    return f"""
        color: {COLORS['text_primary']};
        font-size: {size}pt;
        font-weight: 700;
        letter-spacing: -0.5px;
    """


def apply_light_theme(app):
    """
    Apply a consistent light theme to the application using QPalette.
    This overrides system dark mode settings for Qt widgets.
    """
    from PyQt6.QtGui import QPalette, QColor
    from PyQt6.QtWidgets import QApplication

    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#f1f5f9"))       # Marble
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#0f172a"))   # Void
    palette.setColor(QPalette.ColorRole.Base, QColor("#f1f5f9"))         # Marble
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f8fafc")) # Cloud
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#0f172a"))  # Void
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#f8fafc"))  # Cloud
    palette.setColor(QPalette.ColorRole.Text, QColor("#0f172a"))         # Void
    palette.setColor(QPalette.ColorRole.Button, QColor("#f1f5f9"))       # Marble
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#0f172a"))   # Void
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#ef4444"))   # Destroyer Crimson
    palette.setColor(QPalette.ColorRole.Link, QColor("#8b5cf6"))         # Magus Violet
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#8b5cf6"))    # Magus Violet
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))

    app.setPalette(palette)
    app.setStyleSheet(get_app_stylesheet())

def get_subtitle_style() -> str:
    """Get style for subtitle labels."""
    return f"""
        color: {COLORS['text_secondary']};
        font-size: 11pt;
        line-height: 1.5;
    """
