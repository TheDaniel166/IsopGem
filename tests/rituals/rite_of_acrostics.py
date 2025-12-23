import sys
import unittest
from unittest.mock import MagicMock

# Adjust path to find modules
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from pillars.gematria.services.acrostic_service import AcrosticService, AcrosticResult

class TestAcrosticService(unittest.TestCase):
    def setUp(self):
        self.service = AcrosticService()
        # Mock the dictionary service to avoid DB calls
        self.service.dictionary_service = MagicMock()
        self.service.dictionary_service.is_word.side_effect = lambda w: w == "JESUS"

    def test_line_acrostic(self):
        """Test standard first letter acrostic on lines."""
        text = """
        Jesus, our Lord
        Eternally saves
        Susie loves him
        Up in heaven
        So much
        """
        results = self.service.find_acrostics(text, check_first=True, check_last=False, mode="Line")
        
        self.assertEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res.found_word, "JESUS")
        self.assertTrue(res.is_valid_word)
        self.assertEqual(len(res.source_indices), 5)

    def test_word_acrostic(self):
        """Test first letter acrostic on words."""
        text = "Just Every Single Universal Soul"
        # First letters: J-E-S-U-S
        
        results = self.service.find_acrostics(text, check_first=True, check_last=False, mode="Word")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].found_word, "JESUS")

    def test_telestich(self):
        """Test last letter telestich."""
        # Need a text where last letters spell something.
        # "Hello Dads"
        # Hello -> O
        # Dads -> S
        # OS
        text = """
        Hello
        Dads
        """
        # Dictionary mock says "OS" is not a word (default False unless JESUS)
        self.service.dictionary_service.is_word.side_effect = lambda w: w == "OS"
        
    def test_substring_search(self):
        """Test finding a valid word hidden in a longer acrostic."""
        # "X JESUS Y"
        text = """
        Xylophone
        Jesus
        Eats
        Soup
        Under
        Stars
        Yak
        """
        # First letters: X J E S U S Y
        # We want to find "JESUS"
        
        results = self.service.find_acrostics(text, check_first=True, check_last=False, mode="Line")
        
        # Should find "JESUS" as a valid word
        found_jesus = any(r.found_word == "JESUS" and r.is_valid_word for r in results)
        self.assertTrue(found_jesus, "Failed to find 'JESUS' substring")
        
        # Might also find "US" if that's a word, but we only mocked JESUS.
        
        # Indices for J-E-S-U-S should be 1, 2, 3, 4, 5 (0-indexed lines)
        jesus_result = next(r for r in results if r.found_word == "JESUS")
        self.assertEqual(jesus_result.source_indices, [1, 2, 3, 4, 5])

if __name__ == '__main__':
    unittest.main()
