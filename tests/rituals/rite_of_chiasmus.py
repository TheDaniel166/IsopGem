import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from pillars.gematria.services.chiasmus_service import ChiasmusService

# Mock calculator for testing
class MockCalculator:
    def calculate(self, word: str) -> int:
        if word.upper() in ["A", "a"]: return 1
        if word.upper() in ["B", "b"]: return 2
        if word.upper() in ["C", "c"]: return 3
        if word.upper() in ["H", "h"]: return 8
        if word.upper() in ["I", "i"]: return 9
        if word == "AB": return 3 # 1+2
        return 0

class TestChiasmus(unittest.TestCase):
    def setUp(self):
        self.service = ChiasmusService()
        self.calc = MockCalculator()

    def test_basic_chiasmus(self):
        # A - B - C - B - A
        text = "A B C B A"
        patterns = self.service.scan_text(text, self.calc, max_depth=10)
        
        self.assertEqual(len(patterns), 1)
        p = patterns[0]
        self.assertIsNotNone(p.center_index)
        self.assertEqual(p.source_units[2], "C") # Center
        self.assertEqual(p.depth, 2)

    def test_even_chiasmus(self):
        # A - B - B - A
        text = "A B B A"
        patterns = self.service.scan_text(text, self.calc, max_depth=10)
        self.assertEqual(len(patterns), 1)
        p = patterns[0]
        self.assertIsNone(p.center_index)
        self.assertEqual(p.depth, 2)
        
    def test_depth_limit(self):
        # A - B - C - B - A is depth 2.
        # If we limit to max_depth=1, we should get depth 1 (B-C-B)
        text = "A B C B A"
        patterns = self.service.scan_text(text, self.calc, max_depth=1)
        self.assertEqual(len(patterns), 1)
        p = patterns[0]
        self.assertEqual(p.depth, 1)
        self.assertEqual(p.source_units[0], "B") # Should start at B
        
    def test_gematria_match(self):
        # H(8) matches H(8).
        text = "H I H"
        patterns = self.service.scan_text(text, self.calc, max_depth=5)
        self.assertTrue(len(patterns) > 0)
        
        # Test distinct words with same value
        text = "AB C C AB"
        # AB = 3. C = 3.
        patterns = self.service.scan_text(text, self.calc, max_depth=5)
        self.assertTrue(len(patterns) > 0)
        
        # Find the max depth pattern (the even one)
        pattern_values = [p.values for p in patterns]
        self.assertIn([3, 3, 3, 3], pattern_values)

if __name__ == '__main__':
    unittest.main()
