
from PyQt6.QtWidgets import QApplication, QPushButton
from PyQt6.QtCore import QObject, QEvent
from shared.ui.kinetic_enforcer import KineticEnforcer
import sys

# Mock application and button
app = QApplication(sys.argv)
btn = QPushButton("Test Button")
btn.setProperty("archetype", "magus")

enforcer = KineticEnforcer()
btn.installEventFilter(enforcer)

# Simulate Enter Event
event_enter = QEvent(QEvent.Type.Enter)
enforcer.eventFilter(btn, event_enter)

# Check if effect is applied
effect = btn.graphicsEffect()
if effect:
    print(f"Effect applied. Blur Radius: {effect.blurRadius()}")
    # We expect 20 constant
    if effect.blurRadius() != 20:
        print("ERROR: Blur radius is not 20!")
        sys.exit(1)
else:
    print("ERROR: No effect applied!")
    sys.exit(1)

# Simulate Leave Event
event_leave = QEvent(QEvent.Type.Leave)
enforcer.eventFilter(btn, event_leave)

print("Verification Successful.")
