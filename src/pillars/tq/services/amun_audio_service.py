"""
Amun Audio Service - The Symphonic Synthesizer.
Generates WAV audio files from Amun Sound signatures using additive synthesis with orchestral archetypes.
"""
import wave
import math
import struct
import os
import tempfile
import random


class AmunAudioService:
    """Service for generating Amun Sound Signatures as WAV files."""

    @staticmethod
    @staticmethod
    def generate_wave_file(freq: float, attack: float = 0.1, release: float = 0.5, layers: int = 1, detune: float = 0.0, audio_type: str = 'Standard') -> str:
        """
        Generate a temporary WAV file using Additive Synthesis (Symphonic Engine).
        """
        # Feature: Percussive/Plucked types enforce short duration if needed
        if audio_type in ['Percussive', 'Plucked']:
            # Ensure nice tail but crisp
            pass 
            
        # Duration determined by envelope
        duration = attack + release + 0.2 # Buffer
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
            path = temp.name
            
        with wave.open(path, 'w') as wav_file:
            wav_file.setnchannels(2)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            
            data = AmunAudioService._synthesize_data(freq, attack, release, layers, detune, n_samples, sample_rate, audio_type)
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
                # Legacy/Transition logic
                # We expect params in `sig['parameters']` now.
                if 'parameters' in sig:
                    p = sig['parameters']
                    freq = p.get('freq', 261.63)
                    atk = p.get('attack', 0.1)
                    rel = p.get('release', 0.5)
                    layers = p.get('layers', 1)
                    detune = p.get('detune', 0)
                    audio_type = p.get('audio_type', 'Standard')
                else:
                    # Fallback
                    freq = 261.63
                    atk, rel = 0.1, 0.5
                    layers, detune = 1, 0
                    audio_type = 'Standard'
                
                # Note Duration logic for Sequencer?
                # Sequencer usually wants fixed BPM. 
                # For Symphonic, notes might overlap (Tail).
                # For now, we cut to note_duration or allow tail?
                # Let's render full envelope but overlap? 
                # Simple: Render to n_samples determined by note_duration, 
                # but if Envelope is longer, we might clip.
                # Let's adjust n_samples to be max(note_duration, atk+rel)
                # ensuring full sound.
                # BUT generate_sequence appends linearly.
                # So we must stick to note_duration for rhythm.
                
                # Re-calc n_samples for this specific note's envelope?
                # No, sequence enforces grid.
                # We'll stick to n_samples_per_note limits, effectively "choking" long notes.
                
                note_data = AmunAudioService._synthesize_data(freq, atk, rel, layers, detune, n_samples_per_note, sample_rate, audio_type)
                full_data.extend(note_data)
                
            wav_file.writeframes(full_data)
            
        return path

    @staticmethod
    def _synthesize_data(freq: float, attack: float, release: float, layers: int, detune: float, n_samples: int, sample_rate: int, audio_type: str = 'Standard') -> bytes:
        """Internal Additive Synthesis Logic with Archetype support."""
        if freq == 0:
            return b'\x00\x00' * n_samples * 2
            
        data = bytearray()
        
        # Archetype Specific Variables
        base_waveform = 'saw' # Default
        if audio_type == 'Ambient': 
            base_waveform = 'sine'
        elif audio_type == 'Reedy':
            base_waveform = 'square'
        elif audio_type == 'Brassy':
            base_waveform = 'brass' # Saw + Tri
            
        # Overrides for Percussive
        if audio_type == 'Percussive':
            attack = 0.01 # Force snap
            
        # Scaling Factor to prevent clipping with multiple layers
        # Base volume 0.3, divided by sqrt(layers) roughly?
        # JS: baseVol = 0.3 / Sqrt(layers)
        base_vol = 0.3 / math.sqrt(layers) if layers > 0 else 0.3
        
        # Boost Ambient/Bass
        if audio_type in ['Ambient', 'Bass']:
            base_vol *= 1.2
            
        max_amp_val = 32767.0
        
        two_pi = 2 * math.pi
        
        # Pre-calc phase increments for active layers to save trig calls?
        # We handle loop inside.
        
        for i in range(n_samples):
            t = i / sample_rate
            
            # 1. Calculate Envelope (Linear A/R)
            env = 0.0
            if t < attack:
                env = t / attack
            elif t < (attack + release):
                # Release phase: From 1.0 down to 0
                rel_pos = t - attack
                env = 1.0 - (rel_pos / release)
            else:
                env = 0.0
                
            if env < 0: env = 0
            
            # Optimization: If Silent via Envelope, skip synthesis
            if env <= 0.001 and t > attack:
                l_val, r_val = 0, 0
                data.extend(struct.pack('<hh', 0, 0))
                continue
                
            # 2. Layering Logic (Additive)
            val = 0.0
            
            # Layer 1: Fundamental
            phase_main = two_pi * freq * t
            
            if base_waveform == 'sine':
                val += math.sin(phase_main)
            elif base_waveform == 'square':
                val += 1.0 if math.sin(phase_main) >= 0 else -1.0
            else: # Saw / Brass
                saw = ((phase_main / two_pi) % 1.0) * 2.0 - 1.0
                if base_waveform == 'brass':
                    # Mix Triangle
                    tri = (2.0 / math.pi) * math.asin(math.sin(phase_main))
                    val += 0.6 * saw + 0.4 * tri
                else:
                    val += saw

            # Percussive Noise Burst
            if audio_type == 'Percussive' and t < 0.05:
                # Add white noise decay
                noise = random.uniform(-1.0, 1.0)
                noise_env = 1.0 - (t / 0.05)
                val += noise * noise_env
                
            # Sub Oscillator for Bass/Pulse
            if audio_type in ['Bass', 'Pulse', 'Ambient']:
                 phase_sub = two_pi * (freq * 0.5) * t
                 val += 0.5 * math.sin(phase_sub)
            
            # Additional Layers (Chorus/Stacking)
            if layers > 1:
                # Layer 2: Detuned (Chorus)
                mult = 2.0 ** (detune / 1200.0)
                
                p_plus = two_pi * (freq * mult) * t
                p_minus = two_pi * (freq / mult) * t
                
                w_p = math.sin(p_plus) if base_waveform == 'sine' else ((p_plus / two_pi) % 1.0) * 2.0 - 1.0
                w_m = math.sin(p_minus) if base_waveform == 'sine' else ((p_minus / two_pi) % 1.0) * 2.0 - 1.0
                
                val += (w_p * 0.7) + (w_m * 0.7)
                
            if layers > 4:
                # Layer 3: Octave Up
                p_oct = two_pi * (freq * 2.0) * t
                tri = (2.0 / math.pi) * math.asin(math.sin(p_oct))
                if audio_type == 'Reedy':
                    # Square octave
                    sq_oct = 1.0 if math.sin(p_oct) >= 0 else -1.0
                    val += sq_oct * 0.5
                else:
                    val += tri * 0.5
                
            if layers > 6 and audio_type != 'Bass':
                # Layer 4: Perfect 5th
                p_5th = two_pi * (freq * 1.5) * t
                saw_5 = ((p_5th / two_pi) % 1.0) * 2.0 - 1.0
                val += saw_5 * 0.4
                
            if layers > 10:
                # Layer 6: High Shimmer
                p_high = two_pi * (freq * 3.0) * t
                val += math.sin(p_high) * 0.2
                
            # Apply Envelope and Volume
            final_sample = val * base_vol * env * max_amp_val
            
            # Clip
            final_val = max(-32767, min(32767, int(final_sample)))
            
            # Write Stereo (Dual Mono)
            data.extend(struct.pack('<hh', final_val, final_val))
            
        return data
