"""
Amun Audio Service - Meditative Sound Synthesis.

Generates entraining audio from SoundFrame specifications.

The Three Principles of Synthesis:
    1. Pitch - Frequency in Hz (from ditrune position)
    2. Timbre - Waveform type (Sine/Triangle/Sawtooth from Skin)
    3. Entrainment - Amplitude pulse rate (4-13 Hz from Body)
"""
import math
import struct
import tempfile
import wave
from typing import Optional

from ..models.amun_sound import SoundFrame, WaveformSpec


class AmunAudioService:
    """Service for generating entraining audio from SoundFrames."""
    
    SAMPLE_RATE = 44100
    CHANNELS = 2
    SAMPLE_WIDTH = 2  # 16-bit
    MAX_AMP = 32767
    
    @staticmethod
    def generate_from_frame(
        frame: SoundFrame,
        duration: float = 4.0,
        volume: float = 0.5,
    ) -> str:
        """
        Generate a WAV file from a SoundFrame.
        
        Args:
            frame: The SoundFrame containing pitch, timbre, and entrainment.
            duration: Length in seconds.
            volume: Master volume (0.0 to 1.0).
        
        Returns:
            Path to the generated WAV file.
        """
        if not frame.is_audible:
            # Return silence for invisible ditrune
            return AmunAudioService._generate_silence(duration)
        
        samples = AmunAudioService._synthesize_frame(
            frame=frame,
            duration=duration,
            volume=volume,
        )
        
        return AmunAudioService._write_wav(samples)
    
    @staticmethod
    def _synthesize_frame(
        frame: SoundFrame,
        duration: float,
        volume: float,
    ) -> bytes:
        """
        Synthesize entraining audio for a SoundFrame.
        
        Implements:
        - Additive synthesis based on waveform spec
        - Amplitude modulation at entrainment pulse rate
        - Smooth fade in/out
        """
        data = bytearray()
        sample_rate = AmunAudioService.SAMPLE_RATE
        n_samples = int(duration * sample_rate)
        two_pi = 2 * math.pi
        
        # Extract parameters
        freq = frame.frequency
        waveform = frame.waveform
        pulse_rate = frame.pulse_rate
        
        # Fade envelope (avoid clicks)
        fade_time = 0.3  # seconds
        fade_samples = int(fade_time * sample_rate)
        
        for i in range(n_samples):
            t = i / sample_rate
            
            # 1. Generate waveform (additive synthesis)
            wave_val = AmunAudioService._generate_waveform(
                t, freq, waveform, two_pi
            )
            
            # 2. Apply entrainment pulse (amplitude modulation)
            # Pulse oscillates between 0.3 and 1.0 for gentle breathing effect
            pulse_phase = two_pi * pulse_rate * t
            pulse_env = 0.65 + 0.35 * math.sin(pulse_phase)
            
            # 3. Apply fade in/out
            fade_env = 1.0
            if i < fade_samples:
                # Fade in
                fade_env = 0.5 * (1 - math.cos(math.pi * i / fade_samples))
            elif i > n_samples - fade_samples:
                # Fade out
                remaining = n_samples - i
                fade_env = 0.5 * (1 - math.cos(math.pi * remaining / fade_samples))
            
            # 4. Combine
            sample = wave_val * pulse_env * fade_env * volume
            
            # Convert to 16-bit integer
            sample_int = int(sample * AmunAudioService.MAX_AMP)
            sample_int = max(-32767, min(32767, sample_int))
            
            # Stereo (same on both channels)
            data.extend(struct.pack('<hh', sample_int, sample_int))
        
        return bytes(data)
    
    @staticmethod
    def _generate_waveform(
        t: float,
        freq: float,
        waveform: WaveformSpec,
        two_pi: float,
    ) -> float:
        """
        Generate waveform sample using additive synthesis.
        
        Args:
            t: Time in seconds.
            freq: Fundamental frequency in Hz.
            waveform: WaveformSpec with harmonic parameters.
            two_pi: Pre-calculated 2*pi.
        
        Returns:
            Sample value in range [-1, 1].
        """
        val = 0.0
        
        for h in range(1, waveform.max_harmonic + 1):
            # Skip even harmonics for odd-only waveforms
            if waveform.odd_harmonics and h % 2 == 0:
                continue
            
            # Calculate harmonic amplitude with rolloff
            harmonic_amp = 1.0 / (h ** waveform.rolloff_exp)
            
            # Add harmonic
            phase = two_pi * freq * h * t
            val += math.sin(phase) * harmonic_amp
        
        # Normalize to prevent clipping
        # Approximate normalization based on harmonic count
        if waveform.odd_harmonics:
            # Odd harmonics: fewer terms
            norm = 1.0 + 0.1 * waveform.max_harmonic
        else:
            # All harmonics: more terms
            norm = 1.0 + 0.15 * waveform.max_harmonic
        
        return val / norm
    
    @staticmethod
    def _generate_silence(duration: float) -> str:
        """Generate a silent WAV file."""
        sample_rate = AmunAudioService.SAMPLE_RATE
        n_samples = int(duration * sample_rate)
        data = b'\x00\x00\x00\x00' * n_samples  # Stereo silence
        return AmunAudioService._write_wav(data)
    
    @staticmethod
    def _write_wav(samples: bytes) -> str:
        """Write samples to a temporary WAV file."""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            with wave.open(f.name, 'w') as wav:
                wav.setnchannels(AmunAudioService.CHANNELS)
                wav.setsampwidth(AmunAudioService.SAMPLE_WIDTH)
                wav.setframerate(AmunAudioService.SAMPLE_RATE)
                wav.writeframes(samples)
            return f.name
    
    # =========================================================================
    # Convenience Methods
    # =========================================================================
    
    @staticmethod
    def generate_from_decimal(
        decimal: int,
        duration: float = 4.0,
        volume: float = 0.5,
    ) -> str:
        """
        Generate audio from a ditrune decimal value.
        
        Args:
            decimal: Ditrune value (0-728).
            duration: Length in seconds.
            volume: Master volume (0.0 to 1.0).
        
        Returns:
            Path to generated WAV file.
        """
        from ..models.amun_sound import AmunSoundCalculator
        frame = AmunSoundCalculator.calculate_signature(decimal)
        return AmunAudioService.generate_from_frame(frame, duration, volume)
    
    @staticmethod
    def generate_scale(
        ditrunes: list,
        duration_per_note: float = 2.0,
        volume: float = 0.5,
    ) -> str:
        """
        Generate audio for a sequence of ditrunes.
        
        Args:
            ditrunes: List of ditrune decimal values.
            duration_per_note: Duration of each note in seconds.
            volume: Master volume.
        
        Returns:
            Path to generated WAV file.
        """
        from ..models.amun_sound import AmunSoundCalculator
        
        all_samples = bytearray()
        
        for decimal in ditrunes:
            frame = AmunSoundCalculator.calculate_signature(decimal)
            if frame.is_audible:
                samples = AmunAudioService._synthesize_frame(
                    frame=frame,
                    duration=duration_per_note,
                    volume=volume,
                )
                all_samples.extend(samples)
        
        return AmunAudioService._write_wav(bytes(all_samples))
    
    @staticmethod
    def generate_sequence(
        signatures: list,
        note_duration: float = 0.5,
        volume: float = 0.5,
    ) -> str:
        """
        Generate audio for a sequence of legacy signature dicts.
        
        This is a backward-compatibility wrapper for UI code.
        
        Args:
            signatures: List of legacy signature dicts (from calculate_signature_legacy).
            note_duration: Duration of each note in seconds.
            volume: Master volume.
        
        Returns:
            Path to generated WAV file.
        """
        all_samples = bytearray()
        
        for sig in signatures:
            # Get the SoundFrame from the legacy dict
            frame = sig.get('frame')
            if frame is None:
                # Fallback: recalculate from decimal
                from ..models.amun_sound import AmunSoundCalculator
                decimal = sig.get('meta', {}).get('decimal', 0)
                frame = AmunSoundCalculator.calculate_signature(decimal)
            
            if frame.is_audible:
                samples = AmunAudioService._synthesize_frame(
                    frame=frame,
                    duration=note_duration,
                    volume=volume,
                )
                all_samples.extend(samples)
        
        return AmunAudioService._write_wav(bytes(all_samples))
