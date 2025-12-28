"""
Kamea Symphony Service - The Cinematic Audio Engine.
Generates rich, textured audio using NumPy synthesis, convolution reverb, and stereo panning based on Ditrune nucleation.
"""
import numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve
import io
import tempfile
from typing import Optional, List
import struct

from ..models.symphony_config import SYMPHONY_FAMILIES, SymphonyNucleation, OCTAVE_FREQUENCIES, SCALE_RATIOS

class KameaSymphonyService:
    """
    Cinematic Audio Engine for the Kamea.
    Generates complex, textured audio based on Ditrune Nucleation.
    """
    SAMPLE_RATE = 44100
    
    def __init__(self):
        # Cache impulse response for performance
        """
          init   logic.
        
        """
        self._reverb_impulse = self._generate_reverb_impulse()

    def generate_wav_file(self, nucleation: SymphonyNucleation, duration: float = 4.0) -> str:
        """Generates audio and returns path to a temporary WAV file."""
        audio_data = self._synthesize(nucleation, duration)
        return self._write_wav(audio_data)

    def generate_sequence(self, nucleations: List[SymphonyNucleation], duration: float = 0.5) -> str:
        """Generates a sequence of notes (linear concatenation)."""
        full_audio = np.array([], dtype=np.float64).reshape(0, 2)
        
        for nuc in nucleations:
            segment = self._synthesize(nuc, duration)
            full_audio = np.vstack((full_audio, segment))
            
        return self._write_wav(full_audio)

    def generate_chord(self, nucleations: List[SymphonyNucleation], duration: float = 4.0) -> str:
        """Generates a chord (simultaneous mixing)."""
        if not nucleations:
            return ""
            
        # Synthesize all voices
        voices = [self._synthesize(nuc, duration) for nuc in nucleations]
        
        # Determine max length
        max_len = max(len(v) for v in voices)
        
        # Mix buffer
        mix = np.zeros((max_len, 2))
        
        for v in voices:
            # Pad if shorter
            if len(v) < max_len:
                v = np.pad(v, ((0, max_len - len(v)), (0, 0)))
            mix += v
            
        # Normalize Mix
        # Divide by sqrt of count to maintain energy without massive clipping, 
        # then soft clip
        mix = mix / np.sqrt(len(voices))
        mix = np.tanh(mix * 1.2)
        
        return self._write_wav(mix)

    def _write_wav(self, audio_data: np.ndarray) -> str:
        """Helper to write NumPy float array to 16-bit WAV."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        scaled = np.int16(audio_data * 32767)
        wavfile.write(temp_file.name, self.SAMPLE_RATE, scaled)
        return temp_file.name

    def _synthesize(self, nuc: SymphonyNucleation, duration: float) -> np.ndarray:
        """Core synthesis logic pipeline."""
        # 1. Calculate Base Frequency
        base_freq = OCTAVE_FREQUENCIES[nuc.pyx_count] if nuc.pyx_count < len(OCTAVE_FREQUENCIES) else 261.63
        skin_val = int(nuc.skin, 3)
        freq = base_freq * SCALE_RATIOS[skin_val]

        # 2. Determine Harmonics (Hierarchy)
        fam_config = SYMPHONY_FAMILIES[nuc.core]
        detunes = [0]
        if nuc.hierarchy_class == 'Acolyte':
            detunes = fam_config.detune_acolyte
        elif nuc.hierarchy_class == 'Temple':
            detunes = fam_config.detune_temple

        # 3. Generate Source Audio (Stereo)
        num_samples = int(self.SAMPLE_RATE * duration)
        mix = np.zeros((num_samples, 2)) # Stereo buffer

        for detune in detunes:
            f = freq * (1 + detune)
            layer = self._generate_voice(nuc.core, f, duration)
            
            # Panning Logic based on X coordinate (-13 to 13)
            # Map -13..13 to 0.0..1.0 (Left..Right)
            pan = (nuc.coordinates[0] + 13) / 26.0
            pan = max(0.0, min(1.0, pan))
            
            # Apply Pan (Constant Power)
            left_gain = np.cos(pan * np.pi / 2)
            right_gain = np.sin(pan * np.pi / 2)
            
            # Stack into stereo
            stereo_layer = np.column_stack((layer * left_gain, layer * right_gain))
            mix += stereo_layer

        # 4. FX Rack (Compressor -> Reverb)
        # Soft Clip (Compression approximation)
        mix = np.tanh(mix * 1.5) 
        
        # Convolution Reverb (Wet Mix)
        # We process channels independently
        wet_l = fftconvolve(mix[:, 0], self._reverb_impulse, mode='full')[:num_samples]
        wet_r = fftconvolve(mix[:, 1], self._reverb_impulse, mode='full')[:num_samples]
        
        # Blend (Dry 70% / Wet 30%)
        final_mix = (mix * 0.7) + (np.column_stack((wet_l, wet_r)) * 0.3)
        
        # Final Normalization
        max_val = np.max(np.abs(final_mix))
        if max_val > 0:
            final_mix = final_mix / max_val * 0.9
            
        return final_mix

    def _generate_voice(self, core: str, freq: float, duration: float) -> np.ndarray:
        """Generates the raw waveform based on Family ID."""
        t = np.linspace(0, duration, int(self.SAMPLE_RATE * duration), False)
        
        if core == '00': # Void (Sine Swell + Noise)
            osc = np.sin(2 * np.pi * freq * t)
            noise = np.random.normal(0, 0.1, len(t))
            env = self._envelope(len(t), 1.5, 1.5) # Slow breathe
            return (osc + noise) * env * 0.4

        elif core == '01': # Pulse (Kick/Sine)
            osc = np.sin(2 * np.pi * freq * t) # Pitch drop could be added here
            env = self._envelope(len(t), 0.01, 0.4)
            return osc * env * 0.8

        elif core == '02': # Recoil (Strings - Saw)
            osc = self._sawtooth(freq, t)
            # Lowpass approximation via moving average (simple)
            osc = np.convolve(osc, np.ones(5)/5, mode='same')
            env = self._envelope(len(t), 0.5, 1.0)
            return osc * env * 0.3

        elif core == '10': # Projector (Brass - Saw)
            osc = self._sawtooth(freq, t)
            env = self._envelope(len(t), 0.1, 0.5)
            return osc * env * 0.35

        elif core == '11': # Monolith (Organ)
            osc1 = np.sin(2 * np.pi * freq * t)
            osc2 = np.sin(2 * np.pi * (freq*2) * t) * 0.5
            env = self._envelope(len(t), 0.1, 0.5)
            return (osc1 + osc2) * env * 0.3

        elif core == '12': # Weaver (Woodwinds - Square)
            osc = np.sign(np.sin(2 * np.pi * freq * t))
            env = self._envelope(len(t), 0.2, 0.5)
            return osc * env * 0.2

        elif core == '20': # Receiver (Choir)
            osc = self._sawtooth(freq, t)
            # Simple formant approx (soften edges)
            osc = np.convolve(osc, np.ones(10)/10, mode='same') 
            env = self._envelope(len(t), 1.0, 1.0)
            return osc * env * 0.25

        elif core == '21': # Splicer (Pluck)
            osc = self._triangle(freq, t)
            env = self._envelope(len(t), 0.01, 0.5)
            return osc * env * 0.5

        elif core == '22': # Abyss (Sub)
            osc = np.sin(2 * np.pi * (freq/2) * t)
            env = self._envelope(len(t), 0.5, 2.0)
            return osc * env * 0.6

        return np.zeros_like(t)

    def _envelope(self, length, attack_s, release_s):
        a_samp = int(attack_s * self.SAMPLE_RATE)
        r_samp = int(release_s * self.SAMPLE_RATE)
        s_samp = length - a_samp - r_samp
        if s_samp < 0: s_samp = 0 # Handle short duration
        
        env = np.concatenate([
            np.linspace(0, 1, a_samp),
            np.ones(s_samp),
            np.linspace(1, 0, r_samp)
        ])
        return env[:length] if len(env) > length else np.pad(env, (0, length - len(env)))

    def _sawtooth(self, freq, t):
        return 2 * (t * freq - np.floor(t * freq + 0.5))

    def _triangle(self, freq, t):
        return 2 * np.abs(self._sawtooth(freq, t)) - 1

    def _generate_reverb_impulse(self):
        """Generates a synthetic reverb tail."""
        duration = 2.0
        t = np.linspace(0, duration, int(self.SAMPLE_RATE * duration))
        noise = np.random.standard_normal(len(t))
        decay = np.exp(-3 * t)
        return noise * decay