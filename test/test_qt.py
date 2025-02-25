"""
Simple PySide6 test
"""
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
import sys

app = QApplication(sys.argv)
window = QMainWindow()
window.setWindowTitle("Simple Qt Test")
window.setGeometry(100, 100, 200, 100)

button = QPushButton("Click Me!", window)
button.setGeometry(50, 20, 100, 40)

window.show()
app.exec()
