import wave
import math
import struct
import os
import tempfile
import random


class AmunAudioService:
    """Service for generating Amun Sound Signatures as WAV files."""

    @staticmethod
    def generate_wave_file(freq: float, amplitude: float = 0.5, duration: float = 1.0, waveform: str = 'sine') -> str:
        """
        Generate a temporary WAV file using AM synthesis.
        """
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        
        fd, path = tempfile.mkstemp(suffix='.wav')
        os.close(fd)
        
        with wave.open(path, 'w') as wav_file:
            wav_file.setnchannels(2)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            
            data = AmunAudioService._synthesize_data(freq, amplitude, n_samples, sample_rate, waveform)
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
            wav_file.setnchannels(2)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            
            full_data = bytearray()
            
            for sig in signatures:
                ch2 = sig['channels'][2]
                ch3 = sig['channels'][3]
                ch1 = sig['channels'][1]
                
                # Green Channel -> Dynamics (Amplitude)
                # amp = ch2.get('value', 127) / 254.0 # Fallback mapping if not pre-calc?
                # Actually SoundCalculator returns 'dynamics_amp' in parameters.
                # Let's check the new structure.
                # params = sig['parameters']
                # freq = params['pitch_freq']
                # amp = params['dynamics_amp']
                # waveform = params['waveform']
                
                # Adapting to new structure if present, else fallback
                if 'parameters' in sig:
                    freq = sig['parameters']['pitch_freq']
                    amp = sig['parameters']['dynamics_amp']
                    waveform = sig['parameters']['waveform']
                else:
                    # Legacy fallback
                    freq = ch2['output_freq']
                    amp = ch1.get('output_amp', 0.5)
                    waveform = ch2.get('waveform', 'sine')
                
                note_data = AmunAudioService._synthesize_data(freq, amp, n_samples_per_note, sample_rate, waveform)
                full_data.extend(note_data)
                
            wav_file.writeframes(full_data)
            
        return path

    @staticmethod
    def _synthesize_data(freq: float, amplitude: float, n_samples: int, sample_rate: int, waveform: str = 'sine') -> bytes:
        """Internal synthesis logic (Stereo)."""
        if freq == 0:
            return b'\x00\x00' * n_samples * 2 # Times 2 for stereo
            
        data = bytearray()
        max_vol = 32767 * amplitude
        two_pi = 2 * math.pi
        

                
        # No Pan (Mono for now, or Center Stereo)
        # Spec didn't specify Panning, just Pitch/Dynamics/Timbre.
        # We'll output stereo file with equal L/R for compatibility.
        r_gain = 0.5
        l_gain = 0.5
        

        for i in range(n_samples):
            t = i / sample_rate
            
            # 1. Generate Waveform (Carrier)
            # 1. Generate Waveform (Carrier) based on 9-State Nucleation Engine
            phase = two_pi * freq * t
            
            if waveform == 'sine':
                # Void (Sine)
                carrier = math.sin(phase)
                
            elif waveform == 'sine_sub':
                # Deep Water (Sine + Sub)
                carrier = math.sin(phase) + 0.5 * math.sin(phase * 0.5)
                carrier /= 1.5 
                
            elif waveform == 'triangle':
                # Wood (Triangle)
                carrier = (2.0 / math.pi) * math.asin(math.sin(phase))
                
            elif waveform == 'chorus':
                # Liquid (Triangle + Detuned Triangle)
                tri1 = (2.0 / math.pi) * math.asin(math.sin(phase))
                tri2 = (2.0 / math.pi) * math.asin(math.sin(phase * 1.01))
                carrier = (tri1 + tri2) / 2.0
                
            elif waveform == 'square':
                # Solid (Square)
                carrier = 1.0 if math.sin(phase) >= 0 else -1.0
                
            elif waveform == 'vibrato':
                # Vibrating (Pulse Width / Nasal)
                # 25% Duty Cycle
                norm_phase = (phase / two_pi) % 1.0
                carrier = 1.0 if norm_phase < 0.25 else -1.0
                
            elif waveform == 'sawtooth':
                # Plasma (Sawtooth)
                carrier = ((t * freq) % 1.0) * 2.0 - 1.0
                
            elif waveform == 'dissonant':
                # Friction (Distortion)
                # Overdriven Sine mapped to hard clip
                raw = math.sin(phase) * 3.0
                carrier = max(-1.0, min(1.0, raw))
                
            elif waveform == 'noise':
                # Fire (White Noise)
                carrier = random.uniform(-1.0, 1.0)
                
            else:
                # Fallback
                carrier = math.sin(phase)
            
            # Simple Amplitude
            sample_val = carrier * max_vol
            
            # Stereo positioning
            l_val = sample_val * l_gain
            r_val = sample_val * r_gain
            
            # Clip
            l_val = max(-32767, min(32767, l_val))
            r_val = max(-32767, min(32767, r_val))
            
            # Pack Interleaved (L, R)
            data.extend(struct.pack('<hh', int(l_val), int(r_val)))
            
        return data

