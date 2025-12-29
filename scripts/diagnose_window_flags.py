
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import Qt

class TestWindow(QWidget):
    def __init__(self, name, flags, parent=None):
        super().__init__(parent)
        self.setWindowTitle(name)
        self.setup_ui(name)
        
        # Apply Flags
        if flags:
            self.setWindowFlags(flags)
            
    def setup_ui(self, text):
        layout = QVBoxLayout(self)
        label = QLabel(text)
        label.setWordWrap(True)
        layout.addWidget(label)
        self.resize(300, 200)

app = QApplication(sys.argv)

# Main Window
main_win = QMainWindow()
main_win.setWindowTitle("MAIN WINDOW (The Sun)")
main_win.resize(600, 400)
main_win.show()

# Test 1: StaysOnTop Hint (Unparented)
# Theory: Should float above everything, move freely.
w1 = TestWindow(
    "1. StaysOnTop (Unparented)", 
    Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint
)
w1.show()

# Test 2: Tool (Unparented)
# Theory: Should float above parent (if parented) or act as palette. Unparented might behave like normal window or float.
w2 = TestWindow(
    "2. Qt.Tool (Unparented)",
    Qt.WindowType.Tool
)
w2.show()

# Test 3: Transient Parent (The Control)
# Theory: Floats above Main, but locks to monitor.
w3 = TestWindow(
    "3. Transient Parent",
    Qt.WindowType.Window
)
w3.setWindowFlags(Qt.WindowType.Window) # Reset to standard
w3.setParent(main_win, Qt.WindowType.Window)
w3.show()

print("Launching Diagnosis...")
sys.exit(app.exec())
