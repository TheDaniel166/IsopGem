#!/usr/bin/env .venv/bin/python
"""
Debug script to diagnose button styling issues.
Compares ELS Search Window with Gematria Calculator Window.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication, QPushButton
from PyQt6.QtCore import Qt

# Import both windows
from pillars.gematria.ui.els_search_window import ELSSearchWindow
from pillars.gematria.ui.gematria_calculator_window import GematriaCalculatorWindow
from pillars.gematria.services import TQGematriaCalculator
from shared.ui import theme


def inspect_button(button: QPushButton, name: str):
    """Inspect a button's styling properties."""
    print(f"\n{'='*60}")
    print(f"BUTTON: {name}")
    print(f"{'='*60}")
    print(f"Text: {button.text()}")
    print(f"Object Name: {button.objectName()}")
    print(f"Archetype Property: {button.property('archetype')}")
    print(f"Has Inline Stylesheet: {bool(button.styleSheet())}")
    if button.styleSheet():
        print(f"Inline Stylesheet (first 200 chars):\n{button.styleSheet()[:200]}")
    print(f"Parent: {button.parent().__class__.__name__ if button.parent() else 'None'}")
    print(f"Parent has stylesheet: {bool(button.parent().styleSheet()) if button.parent() else 'N/A'}")
    if button.parent() and button.parent().styleSheet():
        print(f"Parent stylesheet (first 200 chars):\n{button.parent().styleSheet()[:200]}")


def inspect_window(window, window_name: str):
    """Inspect a window's stylesheet state."""
    print(f"\n{'#'*60}")
    print(f"WINDOW: {window_name}")
    print(f"{'#'*60}")
    print(f"Window class: {window.__class__.__name__}")
    print(f"Window has stylesheet: {bool(window.styleSheet())}")
    if window.styleSheet():
        print(f"Window stylesheet length: {len(window.styleSheet())} chars")
        print(f"Window stylesheet (first 500 chars):\n{window.styleSheet()[:500]}")
        print(f"\nContains 'QPushButton[archetype': {'QPushButton[archetype' in window.styleSheet()}")
        print(f"Contains 'magus': {'magus' in window.styleSheet()}")
        print(f"Contains 'seeker': {'seeker' in window.styleSheet()}")
    
    # Find all buttons
    buttons = window.findChildren(QPushButton)
    print(f"\nTotal buttons found: {len(buttons)}")
    
    # Inspect first 3 buttons
    for i, btn in enumerate(buttons[:3]):
        inspect_button(btn, f"Button {i+1}")


def main():
    app = QApplication(sys.argv)
    
    # Apply the app stylesheet like main.py does
    print("="*60)
    print("APPLYING APP STYLESHEET")
    print("="*60)
    app.setStyleSheet(theme.get_app_stylesheet())
    print(f"App stylesheet length: {len(app.styleSheet())} chars")
    print(f"Contains 'QPushButton[archetype': {'QPushButton[archetype' in app.styleSheet()}")
    print(f"Contains archetypes: magus={('magus' in app.styleSheet())}, seeker={('seeker' in app.styleSheet())}")
    
    # Create working window (Gematria Calculator)
    calc = TQGematriaCalculator()
    working_window = GematriaCalculatorWindow([calc])
    working_window.show()
    
    # Create problem window (ELS Search)
    problem_window = ELSSearchWindow()
    problem_window.show()
    
    # Inspect both
    inspect_window(working_window, "GEMATRIA CALCULATOR (WORKING)")
    inspect_window(problem_window, "ELS SEARCH (BROKEN)")
    
    print("\n" + "="*60)
    print("DIAGNOSIS COMPLETE")
    print("="*60)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
