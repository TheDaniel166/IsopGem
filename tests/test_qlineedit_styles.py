#!/usr/bin/env python3
"""Test script to isolate QLineEdit stylesheet issues."""

import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit

def test_basic_qlineedit():
    """Test 1: Basic QLineEdit with no stylesheet."""
    print("Test 1: Basic QLineEdit (no stylesheet)")
    app = QApplication(sys.argv)
    widget = QWidget()
    layout = QVBoxLayout(widget)
    
    edit = QLineEdit()
    edit.setPlaceholderText("Basic test")
    layout.addWidget(edit)
    
    print("✓ Test 1 passed\n")

def test_valid_stylesheet():
    """Test 2: QLineEdit with valid stylesheet."""
    print("Test 2: QLineEdit with valid stylesheet")
    app = QApplication(sys.argv)
    widget = QWidget()
    layout = QVBoxLayout(widget)
    
    edit = QLineEdit()
    edit.setStyleSheet("""
        QLineEdit {
            background-color: white;
            border: 1px solid #cbd5e1;
            border-radius: 12px;
            padding: 10px;
            color: black;
        }
    """)
    layout.addWidget(edit)
    
    print("✓ Test 2 passed\n")

def test_invalid_background():
    """Test 3: QLineEdit with invalid 'background:' property."""
    print("Test 3: QLineEdit with INVALID 'background:' property")
    app = QApplication(sys.argv)
    widget = QWidget()
    layout = QVBoxLayout(widget)
    
    edit = QLineEdit()
    edit.setStyleSheet("""
        QLineEdit {
            background: white;
            border: 1px solid #cbd5e1;
        }
    """)
    layout.addWidget(edit)
    
    print("✓ Test 3 completed (check for parse errors above)\n")

def test_geometry_liturgy_styles():
    """Test 4: Use actual liturgy styles from geometry."""
    print("Test 4: Using actual geometry liturgy styles")
    sys.path.insert(0, 'src')
    
    from pillars.geometry.ui.liturgy_styles import LiturgyInputs
    
    app = QApplication(sys.argv)
    widget = QWidget()
    layout = QVBoxLayout(widget)
    
    edit1 = QLineEdit()
    edit1.setStyleSheet(LiturgyInputs.vessel())
    edit1.setPlaceholderText("Vessel style")
    layout.addWidget(edit1)
    
    edit2 = QLineEdit()
    edit2.setStyleSheet(LiturgyInputs.vessel_readonly())
    edit2.setPlaceholderText("Vessel readonly style")
    layout.addWidget(edit2)
    
    print("✓ Test 4 passed\n")

if __name__ == "__main__":
    print("="*60)
    print("QLineEdit Stylesheet Test Suite")
    print("="*60 + "\n")
    
    try:
        test_basic_qlineedit()
    except Exception as e:
        print(f"❌ Test 1 failed: {e}\n")
    
    try:
        test_valid_stylesheet()
    except Exception as e:
        print(f"❌ Test 2 failed: {e}\n")
    
    try:
        test_invalid_background()
    except Exception as e:
        print(f"❌ Test 3 failed: {e}\n")
    
    try:
        test_geometry_liturgy_styles()
    except Exception as e:
        print(f"❌ Test 4 failed: {e}\n")
    
    print("="*60)
    print("Test suite complete")
    print("="*60)
