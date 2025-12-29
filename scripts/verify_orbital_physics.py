
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtCore import Qt
from shared.ui.window_manager import WindowManager
import sys

# Mock Main Window
app = QApplication(sys.argv)
main_win = QMainWindow()
main_win.setWindowTitle("Sun")

# Manager with Orbital Physics
manager = WindowManager(parent=main_win, main_window=main_win)

# Create Satellite
satellite = manager.open_window(
    window_type="test_satellite",
    window_class=QWidget,
    allow_multiple=False
)

# Verification
flags = satellite.windowFlags()
is_on_top = bool(flags & Qt.WindowType.WindowStaysOnTopHint)
parent = satellite.parent()

print(f"Satellite: {satellite}")
print(f"Parent: {parent}")
print(f"Main Window: {main_win}")
print(f"Has WindowStaysOnTopHint: {is_on_top}")

# For Constellation Paradigm:
# 1. Parent MUST be None (for multi-monitor freedom)
# 2. WindowStaysOnTopHint MUST be False (to avoid OS-level locking)
# 3. Z-order is managed by EventFilter (runtime behavior)

if parent is None and not is_on_top:
    print("SUCCESS: Constellation Physics Active. Satellite is free-floating.")
    sys.exit(0)
else:
    print(f"FAILURE: Satellite is bound. Parent={parent}, OnTop={is_on_top}")
    sys.exit(1)
