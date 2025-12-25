"""Modern UI theme and styling for IsopGem application.

Aligned with Visual Liturgy v2.2 - "The Codex of IsopGem"
"""

# ═══════════════════════════════════════════════════════════════════════════════
# The Alchemical Spectrum (Visual Liturgy §2)
# ═══════════════════════════════════════════════════════════════════════════════

COLORS = {
    # ─────────────────────────────────────────────────────────────────────────
    # The Structure (Tones)
    # ─────────────────────────────────────────────────────────────────────────
    'void': '#0f172a',           # The Unknown - Headers, High-contrast text
    'stone': '#334155',          # The Physical - Body text, Scrollbar handles
    'marble': '#f1f5f9',         # The Tablet - Panel Backgrounds (Soft, non-reflective)
    'light': '#ffffff',          # The Illumination - Input Fields (Where intent is inscribed)
    'ash': '#cbd5e1',            # The Boundary - Borders, Dividers
    'cloud': '#f8fafc',          # The Substrate - Background behind panels
    
    # ─────────────────────────────────────────────────────────────────────────
    # The Catalysts (Semantic Button Colors)
    # ─────────────────────────────────────────────────────────────────────────
    'magus': '#8b5cf6',          # Mystic Violet - Transmute / Execute
    'magus_hover': '#a78bfa',
    'seeker': '#f59e0b',         # Alchemical Gold - Uncover / Reveal
    'seeker_hover': '#fbbf24',
    'scribe': '#10b981',         # Emerald - Preserve / Etch
    'scribe_hover': '#34d399',
    'destroyer': '#ef4444',      # Crimson - Purge / Banish
    'destroyer_hover': '#f87171',
    'navigator': '#64748b',      # Void Slate - Traverse
    'navigator_hover': '#94a3b8',
    
    # ─────────────────────────────────────────────────────────────────────────
    # Focus & Status
    # ─────────────────────────────────────────────────────────────────────────
    'focus': '#3b82f6',          # Azure - Focus ring color
    'success': '#10b981',        # Emerald
    'warning': '#f59e0b',        # Gold
    'error': '#ef4444',          # Crimson
    'info': '#3b82f6',           # Azure
    
    # ─────────────────────────────────────────────────────────────────────────
    # Legacy Aliases (for backward compatibility)
    # ─────────────────────────────────────────────────────────────────────────
    'primary': '#8b5cf6',        # Magus Violet
    'primary_hover': '#7c3aed',
    'primary_pressed': '#6d28d9',
    'primary_light': '#ede9fe',
    
    'accent': '#10b981',         # Scribe Emerald
    'accent_hover': '#059669',
    'accent_pressed': '#047857',
    
    'background': '#f8fafc',     # Cloud (Substrate)
    'background_alt': '#f1f5f9', # Marble
    'surface': '#f1f5f9',        # Marble (panels, cards)
    'surface_hover': '#e2e8f0',
    
    'text_primary': '#0f172a',   # Void
    'text_secondary': '#475569', # Stone
    'text_disabled': '#94a3b8',  # Mist
    
    'border': '#cbd5e1',         # Ash
    'border_focus': '#3b82f6',   # Azure
}


def get_app_stylesheet() -> str:
    """
    Get the complete application stylesheet.
    
    Returns:
        QSS stylesheet string
    """
    return f"""
    /* Global styles */
    * {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    }}
    
    QMainWindow, QDialog, QWidget {{
        background-color: {COLORS['background']};
        color: {COLORS['text_primary']};
    }}
    
    /* Buttons */
    QPushButton {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 11pt;
        font-weight: 500;
        min-height: 36px;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS['primary_hover']};
    }}
    
    QPushButton:pressed {{
        background-color: {COLORS['primary_pressed']};
    }}
    
    QPushButton:disabled {{
        background-color: {COLORS['border']};
        color: {COLORS['text_disabled']};
    }}
    
    QPushButton:flat {{
        background-color: transparent;
        color: {COLORS['text_primary']};
    }}
    
    QPushButton:flat:hover {{
        background-color: {COLORS['surface_hover']};
    }}
    
    /* Input fields */
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background-color: {COLORS['surface']};
        border: 2px solid {COLORS['border']};
        border-radius: 6px;
        padding: 8px 12px;
        color: {COLORS['text_primary']};
        font-size: 11pt;
        selection-background-color: {COLORS['primary_light']};
    }}
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {COLORS['border_focus']};
        outline: none;
    }}
    
    QLineEdit:disabled, QTextEdit:disabled {{
        background-color: {COLORS['background_alt']};
        color: {COLORS['text_disabled']};
    }}
    
    /* Combo boxes */
    QComboBox {{
        background-color: {COLORS['surface']};
        border: 2px solid {COLORS['border']};
        border-radius: 6px;
        padding: 8px 12px;
        min-height: 36px;
        color: {COLORS['text_primary']};
    }}
    
    QComboBox:hover {{
        border-color: {COLORS['border_focus']};
    }}
    
    QComboBox::drop-down {{
        border: none;
        padding-right: 8px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid {COLORS['text_secondary']};
        margin-right: 8px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {COLORS['surface']};
        border: 2px solid {COLORS['border']};
        border-radius: 6px;
        selection-background-color: {COLORS['primary_light']};
        selection-color: {COLORS['primary']};
        padding: 4px;
    }}
    
    /* Checkboxes */
    QCheckBox {{
        color: {COLORS['text_primary']};
        spacing: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {COLORS['border']};
        border-radius: 4px;
        background-color: {COLORS['surface']};
    }}
    
    QCheckBox::indicator:hover {{
        border-color: {COLORS['border_focus']};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {COLORS['primary']};
        border-color: {COLORS['primary']};
        image: none;
    }}
    
    /* Lists and Trees */
    QListView, QTreeView {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        color: {COLORS['text_primary']};
        outline: none;
    }}
    
    QListView::item, QTreeView::item {{
        padding: 4px;
        border-bottom: 1px solid transparent;
    }}
    
    QListView::item:selected, QTreeView::item:selected {{
        background-color: {COLORS['primary_light']};
        color: {COLORS['primary']};
        border: none;
    }}

    QListView::item:hover, QTreeView::item:hover {{
        background-color: {COLORS['surface_hover']};
    }}

    /* File dialogs use system native styling - no custom QSS needed */

    /* Tables */
    QTableWidget {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        gridline-color: {COLORS['border']};
        selection-background-color: {COLORS['primary_light']};
        selection-color: {COLORS['primary']};
    }}
    
    QTableWidget::item {{
        padding: 8px;
        border-bottom: 1px solid {COLORS['border']};
    }}
    
    QTableWidget::item:selected {{
        background-color: {COLORS['primary_light']};
        color: {COLORS['primary']};
    }}
    
    QHeaderView::section {{
        background-color: {COLORS['background_alt']};
        padding: 10px 8px;
        border: none;
        border-bottom: 2px solid {COLORS['border']};
        border-right: 1px solid {COLORS['border']};
        font-weight: 600;
        color: {COLORS['text_primary']};
    }}
    
    QTableWidget::item:alternate {{
        background-color: {COLORS['background_alt']};
    }}
    
    /* Tab widget - Main Navigation */
    QTabWidget::pane {{
        border: none;
        background-color: {COLORS['surface']};
    }}
    
    QTabWidget::tab-bar {{
        alignment: left;
    }}
    
    QTabBar {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #1e293b, stop:1 #334155);
    }}
    
    QTabBar::tab {{
        background: transparent;
        color: #94a3b8;
        border: none;
        border-left: 3px solid transparent;
        padding: 14px 24px;
        margin: 0;
        font-size: 11pt;
        font-weight: 500;
        min-width: 120px;
        text-align: left;
    }}
    
    QTabBar::tab:selected {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(59, 130, 246, 0.2), stop:1 transparent);
        color: #ffffff;
        border-left: 3px solid #3b82f6;
        font-weight: 600;
    }}
    
    QTabBar::tab:hover:!selected {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(148, 163, 184, 0.15), stop:1 transparent);
        color: #e2e8f0;
        border-left: 3px solid #64748b;
    }}
    
    QTabBar::tab:first {{
        border-top-left-radius: 0;
    }}
    
    QTabBar::tab:last {{
        border-bottom-left-radius: 0;
    }}
    
    /* Scroll bars */
    QScrollBar:vertical {{
        background-color: {COLORS['background_alt']};
        width: 12px;
        border-radius: 6px;
        margin: 0;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {COLORS['border']};
        border-radius: 6px;
        min-height: 30px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['text_disabled']};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QScrollBar:horizontal {{
        background-color: {COLORS['background_alt']};
        height: 12px;
        border-radius: 6px;
        margin: 0;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {COLORS['border']};
        border-radius: 6px;
        min-width: 30px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {COLORS['text_disabled']};
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    
    /* Labels */
    QLabel {{
        color: {COLORS['text_primary']};
        background-color: transparent;
    }}
    
    /* Splitter */
    QSplitter::handle {{
        background-color: {COLORS['border']};
    }}
    
    QSplitter::handle:horizontal {{
        width: 2px;
    }}
    
    QSplitter::handle:vertical {{
        height: 2px;
    }}
    
    /* Message boxes */
    QMessageBox {{
        background-color: {COLORS['surface']};
    }}
    
    /* Tooltips */
    QToolTip {{
        background-color: {COLORS['text_primary']};
        color: white;
        border: none;
        border-radius: 4px;
        padding: 6px 10px;
        font-size: 10pt;
    }}
    """


def get_accent_button_style() -> str:
    """Get style for accent/success buttons."""
    return f"""
        background-color: {COLORS['accent']};
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 11pt;
        font-weight: 500;
        min-height: 36px;
    """


def get_accent_button_hover_style() -> str:
    """Get hover style for accent buttons."""
    return f"""
        QPushButton {{
            background-color: {COLORS['accent']};
        }}
        QPushButton:hover {{
            background-color: {COLORS['accent_hover']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['accent_pressed']};
        }}
    """


def get_card_style() -> str:
    """Get style for card-like containers."""
    return f"""
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 16px;
    """


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
