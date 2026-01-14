"""
⚠️  GRANDFATHERED VIOLATION - Pre-existing before Law of Substrate (2026-01-13)

SHARED JUSTIFICATION:
- RATIONALE: GRANDFATHERED - Needs manual review
- USED BY: Correspondences, Gematria (2 references)
- CRITERION: Unknown - requires categorization

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md
"""


"""Reusable UI components for Visual Liturgy v2.2."""
from typing import Optional

from PyQt6.QtCore import QSize, Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor

from .catalyst_styles import (
    get_magus_style,
    get_seeker_style,
    get_scribe_style,
    get_destroyer_style,
    get_navigator_style,
)


class CatalystButton(QPushButton):
    """
    A button that implements the Kinetic Liturgy.
    
    Archetypes:
    - Magus: Transmute/Execute (Violet)
    - Seeker: Uncover/Reveal (Gold)
    - Scribe: Preserve/Etch (Emerald)
    - Destroyer: Purge/Banish (Crimson)
    - Navigator: Traverse (Void Slate)
    
    Features:
    - Stylized based on archetype.
    - 'Aura' effect (colored shadow) on hover.
    """
    
    MAGUS = "magus"
    SEEKER = "seeker"
    SCRIBE = "scribe"
    DESTROYER = "destroyer"
    NAVIGATOR = "navigator"
    
    _SHADOW_COLORS = {
        MAGUS: QColor("#6d28d9"),     # Deep Violet
        SEEKER: QColor("#f59e0b"),    # Gold
        SCRIBE: QColor("#10b981"),    # Emerald
        DESTROYER: QColor("#ef4444"), # Crimson
        NAVIGATOR: QColor("#64748b"), # Slate
    }
    
    def __init__(self, text: str, archetype: str = MAGUS, parent=None):
        super().__init__(text, parent)
        self._archetype = archetype
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style()
        self._setup_aura()
        
    def _apply_style(self):
        """Apply QSS based on archetype."""
        if self._archetype == self.MAGUS:
            self.setStyleSheet(get_magus_style())
        elif self._archetype == self.SEEKER:
            self.setStyleSheet(get_seeker_style())
        elif self._archetype == self.SCRIBE:
            self.setStyleSheet(get_scribe_style())
        elif self._archetype == self.DESTROYER:
            self.setStyleSheet(get_destroyer_style())
        elif self._archetype == self.NAVIGATOR:
            self.setStyleSheet(get_navigator_style())
            
    def _setup_aura(self):
        """Initialize the Aura (Shadow) effect."""
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(0) # Start hidden
        self._shadow.setOffset(0, 0)
        self._shadow.setColor(self._SHADOW_COLORS.get(self._archetype, QColor("#000000")))
        self.setGraphicsEffect(self._shadow)
        
        # Animations
        self._anim_in = QPropertyAnimation(self._shadow, b"blurRadius")
        self._anim_in.setDuration(150) # Instant/Swift
        self._anim_in.setStartValue(0)
        self._anim_in.setEndValue(20) # Glow radius
        self._anim_in.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        self._anim_out = QPropertyAnimation(self._shadow, b"blurRadius")
        self._anim_out.setDuration(200)
        self._anim_out.setStartValue(20)
        self._anim_out.setEndValue(0)
        self._anim_out.setEasingCurve(QEasingCurve.Type.OutQuad)
        
    def enterEvent(self, event):
        """Trigger Aura on hover."""
        self._anim_out.stop()
        self._anim_in.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Extinguish Aura on exit."""
        self._anim_in.stop()
        self._anim_out.start()
        super().leaveEvent(event)