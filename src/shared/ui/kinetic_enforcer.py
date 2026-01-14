"""Global Kinetic Enforcer — The Spirit of the Button.

This service acts as a global event filter that monitors all QPushButtons in the application.
It applies the Visual Liturgy's Kinetic Aura (glow effect) automatically on hover,
sparing the developer from manually inheriting custom classes.
"""
"""
SHARED JUSTIFICATION:
- RATIONALE: Core Infrastructure (UI)
- USED BY: Internal shared/ modules only (1 references)
- CRITERION: 2 (Essential for app to function)
"""


from PyQt6.QtCore import QObject, QEvent, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import QPushButton, QGraphicsDropShadowEffect, QApplication
from PyQt6.QtGui import QColor
from shared.ui.theme import COLORS

class KineticEnforcer(QObject):
    """
    A global event filter that enchants every QPushButton with the Kinetic Aura.
    It reads the 'archetype' dynamic property to determine the aura color.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # No longer tracking animations manually; relying on Qt parenting logic.

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Enter:
            if isinstance(obj, QPushButton) and obj.isEnabled():
                self._ignite_aura(obj)
        elif event.type() == QEvent.Type.Leave:
            if isinstance(obj, QPushButton) and obj.isEnabled():
                self._extinguish_aura(obj)
                
        return super().eventFilter(obj, event)

    def _ignite_aura(self, button: QPushButton):
        """Apply and animate the shadow effect."""
        # 1. Determine Archetype (fallback to magus)
        archetype = button.property("archetype") or "magus"
        target_color = self._resolve_color(str(archetype))
        
        # 2. Get or Create Effect
        effect = button.graphicsEffect()
        if not isinstance(effect, QGraphicsDropShadowEffect):
            effect = QGraphicsDropShadowEffect(button)
            effect.setOffset(0, 0)
            # Constant geometry to prevent layout thrashing
            effect.setBlurRadius(20) 
            # Start transparent
            start_color = QColor(target_color)
            start_color.setAlpha(0)
            effect.setColor(start_color)
            button.setGraphicsEffect(effect)
            
        # 3. Animate Opacity (Alpha)
        # We animate from current color to target color (opacity 255 typically, or theme defined)
        self._animate_aura_color(effect, target_color)

    def _extinguish_aura(self, button: QPushButton):
        """Fade out the shadow effect."""
        effect = button.graphicsEffect()
        if isinstance(effect, QGraphicsDropShadowEffect):
            current_color = effect.color()
            target_transparent = QColor(current_color)
            target_transparent.setAlpha(0)
            self._animate_aura_color(effect, target_transparent)

    def _animate_aura_color(self, effect, target_color):
        """Animate the shadow color to the target."""
        # CRITICAL FIX: Parent the animation to the effect (or button)
        # Previously parented to 'self' (Enforcer), which kept the animation alive
        # after the button/effect was destroyed, causing Segmentation Faults.
        anim = QPropertyAnimation(effect, b"color", effect) 
        anim.setStartValue(effect.color())
        anim.setEndValue(target_color)
        anim.setDuration(150) 
        anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _resolve_color(self, archetype: str) -> QColor:
        """Resolve archetype color from theme palette with magus fallback."""
        hex_color = COLORS.get(archetype, COLORS["magus"])
        return QColor(hex_color)