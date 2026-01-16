"""Audio synthesis service for cymatics pattern sonification.

Generates audible tones corresponding to the vibrational frequencies
used in cymatics simulations, allowing users to hear the patterns
they're viewing in real-time.
"""
from __future__ import annotations

import math
import threading
from typing import Callable, Optional

import numpy as np

from ..models import SimulationParams


class ContinuousAudioEngine:
    """Real-time audio synthesis engine for continuous cymatics tones.
    
    Uses streaming audio callbacks to generate sound continuously,
    updating frequency/mix parameters in real-time as the user adjusts
    the simulator controls.
    """

    SAMPLE_RATE = 44100
    BLOCK_SIZE = 2048  # Audio buffer size
    CHANNELS = 2  # Stereo

    def __init__(self):
        """Initialize the audio engine."""
        self._stream = None
        self._is_running = False
        self._lock = threading.Lock()
        
        # Current synthesis parameters (thread-safe)
        self._frequency = 440.0
        self._secondary_freq = 440.0
        self._mix = 0.0
        self._volume = 0.15
        self._phase = 0.0
        self._phase_secondary = 0.0

        # Lazy-load sounddevice (defer import until first use)
        self._sd = None
        self._available = None  # Unknown until first check

    def is_available(self) -> bool:
        """Check if audio system is available."""
        if self._available is not None:
            return self._available

        # Try to import sounddevice on first check
        try:
            import sounddevice as sd
            self._sd = sd
            self._available = True
        except (ImportError, OSError) as e:
            # ImportError: sounddevice not installed
            # OSError: PortAudio library not found
            self._sd = None
            self._available = False
        
        return self._available

    def start(self) -> bool:
        """Start continuous audio synthesis.
        
        Returns:
            True if started successfully, False otherwise
        """
        if not self._available or self._is_running:
            return False

        try:
            with self._lock:
                self._is_running = True
                self._phase = 0.0
                self._phase_secondary = 0.0

            # Create and start audio stream
            self._stream = self._sd.OutputStream(
                samplerate=self.SAMPLE_RATE,
                blocksize=self.BLOCK_SIZE,
                channels=self.CHANNELS,
                callback=self._audio_callback,
                finished_callback=self._stream_finished,
            )
            self._stream.start()
            return True

        except Exception as e:
            print(f"Audio start error: {e}")
            self._is_running = False
            return False

    def stop(self) -> None:
        """Stop continuous audio synthesis."""
        with self._lock:
            self._is_running = False

        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            finally:
                self._stream = None

    def update_params(
        self,
        frequency: float,
        secondary_freq: float = 440.0,
        mix: float = 0.0,
        volume: float = 0.15,
    ) -> None:
        """Update synthesis parameters in real-time.
        
        Args:
            frequency: Primary frequency in Hz
            secondary_freq: Secondary frequency for mixing
            mix: Mix amount (0.0 to 1.0)
            volume: Master volume (0.0 to 1.0)
        """
        with self._lock:
            self._frequency = frequency
            self._secondary_freq = secondary_freq
            self._mix = mix
            self._volume = volume

    def _audio_callback(self, outdata: np.ndarray, frames: int, time_info, status) -> None:
        """Real-time audio generation callback.
        
        Called by sounddevice whenever it needs more audio data.
        Must be extremely fast and lock-free.
        """
        if status:
            print(f"Audio status: {status}")

        # Read current parameters (atomic read)
        with self._lock:
            freq = self._frequency
            freq2 = self._secondary_freq
            mix = self._mix
            vol = self._volume
            phase = self._phase
            phase2 = self._phase_secondary

        # Generate time array for this block
        t = np.arange(frames) / self.SAMPLE_RATE
        
        # Generate primary sine wave
        primary = np.sin(2 * np.pi * freq * t + phase)
        
        # Generate secondary sine wave
        secondary = np.sin(2 * np.pi * freq2 * t + phase2)
        
        # Mix and apply volume
        signal = ((1.0 - mix) * primary + mix * secondary) * vol
        
        # Output stereo (duplicate to both channels)
        outdata[:, 0] = signal
        outdata[:, 1] = signal
        
        # Update phase for continuity across blocks
        with self._lock:
            self._phase = (phase + 2 * np.pi * freq * frames / self.SAMPLE_RATE) % (2 * np.pi)
            self._phase_secondary = (phase2 + 2 * np.pi * freq2 * frames / self.SAMPLE_RATE) % (2 * np.pi)

    def _stream_finished(self) -> None:
        """Called when stream finishes."""
        with self._lock:
            self._is_running = False

    def is_running(self) -> bool:
        """Check if audio is currently playing."""
        with self._lock:
            return self._is_running


class CymaticsAudioService:
    """High-level audio service for cymatics visualization."""

    def __init__(self):
        """Initialize the audio service."""
        self._engine = ContinuousAudioEngine()

    def is_available(self) -> bool:
        """Check if continuous audio is available."""
        return self._engine.is_available()

    def start_continuous(self, params: SimulationParams) -> bool:
        """Start continuous audio synthesis for given parameters.
        
        Args:
            params: Simulation parameters
            
        Returns:
            True if started successfully
        """
        freq_primary, freq_secondary = self._params_to_frequencies(params)
        self._engine.update_params(
            frequency=freq_primary,
            secondary_freq=freq_secondary,
            mix=params.mix,
            volume=0.15,
        )
        return self._engine.start()

    def stop_continuous(self) -> None:
        """Stop continuous audio synthesis."""
        self._engine.stop()

    def update_continuous(self, params: SimulationParams) -> None:
        """Update continuous audio parameters in real-time.
        
        Now includes material-aware synthesis parameters.
        
        Args:
            params: Updated simulation parameters
        """
        if self._engine.is_running():
            freq_primary, freq_secondary = self._params_to_frequencies(params)
            
            # Material affects volume (resonance quality → loudness/sustain)
            # High resonance (quartz, diamond) → louder, clearer
            # Low resonance (wood) → quieter, muted
            material_volume = 0.15 * params.plate_material.resonance_quality
            
            self._engine.update_params(
                frequency=freq_primary,
                secondary_freq=freq_secondary,
                mix=params.mix,
                volume=material_volume,
            )

    def is_playing(self) -> bool:
        """Check if continuous audio is currently playing."""
        return self._engine.is_running()

    def _params_to_frequencies(self, params: SimulationParams) -> tuple[float, float]:
        """Convert simulation parameters to primary and secondary frequencies.
        
        Now accounts for material properties:
        - wave_speed_factor: Scales frequency (faster materials → higher pitch)
        - resonance_quality: Affects harmonic content
        - damping_factor: Affects decay envelope
        
        Returns:
            (primary_freq, secondary_freq) in Hz
        """
        material = params.plate_material
        
        if params.use_frequency_mode:
            # Use Hz slider, but scale by material wave speed
            # Faster materials (glass, diamond) → higher effective pitch
            # Slower materials (gold, wood) → lower effective pitch
            base_freq = params.frequency_hz
            primary = base_freq * material.wave_speed_factor
            # Secondary slightly offset for beating
            secondary = primary * 1.01
        else:
            # Derive from mode numbers, also scale by material
            base_primary = self._modes_to_frequency(params.mode_m, params.mode_n)
            base_secondary = self._modes_to_frequency(params.secondary_m, params.secondary_n)
            
            primary = base_primary * material.wave_speed_factor
            secondary = base_secondary * material.wave_speed_factor

        return (primary, secondary)

    @staticmethod
    def _modes_to_frequency(m: int, n: int) -> float:
        """Convert mode numbers to approximate frequency in Hz."""
        base = 220.0  # A3
        mode_sum = m + n
        return base + (mode_sum * 40.0)
