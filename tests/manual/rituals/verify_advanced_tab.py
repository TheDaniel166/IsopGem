
import sys
import unittest
from PyQt6.QtWidgets import QApplication

# Adjust path to find the module
import os
sys.path.append("/home/burkettdaniel927/projects/isopgem")

from src.pillars.astrology.ui.natal_chart_window import NatalChartWindow

class TestAdvancedTab(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create app if it doesn't exist
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def test_advanced_tab_structure(self):
        window = NatalChartWindow()
        
        # Check main tabs count
        self.assertEqual(window.tabs.count(), 4, "Should have 4 main tabs")
        self.assertEqual(window.tabs.tabText(3), "Advanced", "4th tab should be 'Advanced'")
        
        # Access the advanced tab widget
        # The advanced_tab is a QWidget containing the nested QTabWidget
        # We need to find the QTabWidget inside it. 
        # Since we stored it as self.advanced_tabs in window, we can access it if publicly available,
        # but better to check children to simulate real access or check attribute if we made it self.
        
        self.assertTrue(hasattr(window, 'advanced_tabs'), "Window should have 'advanced_tabs' attribute")
        nested_tabs = window.advanced_tabs
        
        self.assertEqual(nested_tabs.count(), 4, "Nested tabs should include 4 items")
        
        expected_labels = ["Fixed Stars", "Arabic Parts", "Midpoints", "Harmonics"]
        for i, label in enumerate(expected_labels):
            self.assertEqual(nested_tabs.tabText(i), label, f"Tab {i} should be {label}")

if __name__ == '__main__':
    unittest.main()
