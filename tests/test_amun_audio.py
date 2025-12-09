import sys
import unittest
import wave
import os

# Add project root to path
sys.path.append("/home/burkettdaniel927/projects/isopgem/src")

from pillars.tq.services.amun_audio_service import AmunAudioService

class TestAmunAudioService(unittest.TestCase):
        
    def test_wave_generation(self):
        """Test that generate_wave_file creates a valid WAV file."""
        freq = 440.0
        mod = 2.0
        amp = 0.8
        
        path = AmunAudioService.generate_wave_file(freq, mod, amplitude=amp, duration=0.1)
        
        self.assertTrue(os.path.exists(path), "File should exist")
        self.assertTrue(path.endswith('.wav'), "File should be .wav")
        
        # Check header
        with wave.open(path, 'r') as w:
            self.assertEqual(w.getnchannels(), 1)
            self.assertEqual(w.getframerate(), 44100)
            self.assertEqual(w.getsampwidth(), 2)
            frames = w.getnframes()
            self.assertEqual(frames, int(44100 * 0.1))
            
        # Clean up
        os.remove(path)

    def test_silence(self):
        """Test 0 frequency generates silence."""
        path = AmunAudioService.generate_wave_file(0, 0, duration=0.1)
        
        with wave.open(path, 'r') as w:
            data = w.readframes(100)
            # Should be all null bytes
            self.assertEqual(data, b'\x00' * 200) # 100 frames * 2 bytes
            
        os.remove(path)

if __name__ == '__main__':
    unittest.main()
