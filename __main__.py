"""
Main entry point for IsopGem
"""
import sys
from PyQt6.QtWidgets import QApplication
from core.ui.base.main_window import MainWindow

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
