import unittest
from unittest.mock import MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from pillars.gematria.services.acrostic_service import AcrosticService

class TestWordMode(unittest.TestCase):
    def setUp(self):
        self.service = AcrosticService()
        self.service.dictionary_service = MagicMock()
        # Mock dictionary to recognize "HIDDEN"
        self.service.dictionary_service.is_word.side_effect = lambda w: w == "HIDDEN"

    def test_mid_stream_word_acrostic(self):
        """Test finding an acrostic hidden in the middle of a stream of words."""
        # Text: "Intro text here. Happy Iguanas Dance Daily Every Night. Outro text."
        # Hidden: H-I-D-D-E-N
        text = "Intro text here. Happy Iguanas Dance Daily Every Night. Outro text."
        
        results = self.service.find_acrostics(text, check_first=True, check_last=False, mode="Word")
        
        # Should find "HIDDEN"
        found = next((r for r in results if r.found_word == "HIDDEN"), None)
        
        self.assertIsNotNone(found, "Did not find 'HIDDEN' in word stream")
        self.assertTrue(found.is_valid_word)
        # Check source text units
        expected_units = ["Happy", "Iguanas", "Dance", "Daily", "Every", "Night."]
        # Note: input splitting might keep punctuation attached to the unit string, 
        # but extraction logic cleans it for the letter. result.source_text_units stores the original unit.
        self.assertEqual(found.source_text_units, expected_units)

if __name__ == '__main__':
    unittest.main()
