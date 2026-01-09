import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.append("/home/burkettdaniel927/projects/isopgem/src")

from pillars.tq.models.amun_sound import AmunSoundCalculator

class TestAmunSoundCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = AmunSoundCalculator()

    def test_zero_ditrune(self):
        """Test Value 0 (000000) -> Reversed 000000"""
        # 0 -> 000000 -> Reversed 000000
        result = self.calc.calculate_signature(0)
        self.assertEqual(result['meta']['ternary'], "000000")
        
        c1 = result['channels'][1]
        self.assertEqual(c1['pair'], (0, 0))
        self.assertEqual(c1['bigram_value'], 0)
        # Ratio for 0 is now 1.0 (Base Void)
        self.assertEqual(c1['ratio'], 1.0) 
        self.assertEqual(c1['interval'], "Base Void")
        # Octave Map for 0 is 0.25 ("Sub-Bass")
        self.assertEqual(c1['octave_plane'], "Sub-Bass")

    def test_one_ditrune(self):
        """Test Value 1 (000001) -> Reversed 100000"""
        # 1 -> "000001" (Old) -> "100000" (New Reversed)
        # Ch1 (Bottom/Top) -> Index 0 and 5 -> (1, 0)
        # Bigram 3 (1-0 is 3 in Lookup) -> Tenor (2.0x)
        result = self.calc.calculate_signature(1)
        self.assertEqual(result['meta']['ternary'], "100000")
        
        c1 = result['channels'][1]
        self.assertEqual(c1['pair'], (1, 0))
        self.assertEqual(c1['bigram_value'], 3) 
        self.assertEqual(c1['octave_plane'], "Tenor")

    def test_octave_shift_cosmic(self):
        """Test Value forcing Radiance Plane (Bigram 8 in Ch1)"""
        # Need Ch1 pair to be (2,2) -> Bigram 8
        # (2,2) -> Rev String "200002" -> Base "200002"
        # 2*3^5 + 2*3^0 = 486 + 2 = 488
        
        result = self.calc.calculate_signature(488)
        c1 = result['channels'][1]
        self.assertEqual(c1['pair'], (2, 2))
        self.assertEqual(c1['bigram_value'], 8)
        self.assertEqual(c1['octave_plane'], "Radiance")
        
        # Check Freq Multiplier (Bigram 8 -> 64x)
        # Ch2 Pair: Idx 1=0, Idx 4=0 -> (0,0) -> Bigram 0 -> Ratio 1.0
        c2 = result['channels'][2]
        self.assertEqual(c2['bigram_value'], 0)
        # Freq should be 97.0 * 1.0 * 64.0
        self.assertEqual(c2['output_freq'], 97.0 * 64.0)

    def test_three_ditrune(self):
        """Test Value 3 (000010) -> Reversed 010000"""
        # 3 -> "000010" -> "010000"
        # Ch1 (0,0) -> 0
        # Ch2 (Pitch) -> Idx 1 & 4 -> (1, 0)
        # Bigram 1*3+0 = 3 -> Ratio 1.25
        # Freq = 97 * 1.25 = 121.25
        result = self.calc.calculate_signature(3)
        self.assertEqual(result['meta']['ternary'], "010000")
        
        c2 = result['channels'][2]
        self.assertEqual(c2['bigram_value'], 3)
        # Old: 121.25 (1x). New: Ch1 is (0,0) -> SubBass (0.25x)
        # 97.0 * 1.25 * 0.25 = 30.3125
        self.assertEqual(c2['output_freq'], 30.3125)

if __name__ == '__main__':
    unittest.main()
