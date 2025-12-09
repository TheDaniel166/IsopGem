import wave
import math
import struct
import os
import tempfile

class AmunAudioService:
    """Service for generating Amun Sound Signatures as WAV files."""

    @staticmethod
    def generate_wave_file(freq: float, mod_rate: float, amplitude: float = 0.5, duration: float = 3.0) -> str:
        """
        Generate a temporary WAV file using AM synthesis.
        """
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        
        fd, path = tempfile.mkstemp(suffix='.wav')
        os.close(fd)
        
        with wave.open(path, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            
            data = AmunAudioService._synthesize_data(freq, mod_rate, amplitude, n_samples, sample_rate)
            wav_file.writeframes(data)
            
        return path

    @staticmethod
    def generate_sequence(signatures: list, note_duration: float = 1.0) -> str:
        """
        Generate a single WAV file from a sequence of signatures.
        
        Args:
            signatures: List of full signature dictionaries (output of calculate_signature).
            note_duration: Duration of each note in seconds.
            
        Returns:
            Path to temporary WAV file.
        """
        sample_rate = 44100
        n_samples_per_note = int(sample_rate * note_duration)
        
        fd, path = tempfile.mkstemp(suffix='.wav')
        os.close(fd)
        
        with wave.open(path, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            
            full_data = bytearray()
            
            for sig in signatures:
                # Extract parameters
                ch2 = sig['channels'][2]
                ch3 = sig['channels'][3]
                ch1 = sig['channels'][1]
                
                freq = ch2['output_freq']
                mod_rate = ch3['output_rate']
                amp = ch1.get('output_amp', 0.5)
                
                note_data = AmunAudioService._synthesize_data(freq, mod_rate, amp, n_samples_per_note, sample_rate)
                full_data.extend(note_data)
                
            wav_file.writeframes(full_data)
            
        return path

    @staticmethod
    def _synthesize_data(freq: float, mod_rate: float, amplitude: float, n_samples: int, sample_rate: int) -> bytes:
        """Internal synthesis logic."""
        if freq == 0:
            return b'\x00\x00' * n_samples
            
        data = bytearray()
        max_vol = 32767 * amplitude
        two_pi = 2 * math.pi
        
        for i in range(n_samples):
            t = i / sample_rate
            
            carrier = math.sin(two_pi * freq * t)
            
            if mod_rate > 0:
                modulator = 1.0 + 0.5 * math.sin(two_pi * mod_rate * t)
            else:
                modulator = 1.0
                
            sample_val = carrier * modulator * max_vol
            sample_val = max(-32767, min(32767, sample_val))
            data.extend(struct.pack('<h', int(sample_val)))
            
        return data

