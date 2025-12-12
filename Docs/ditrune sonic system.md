# **The Ditrune Sonic System: A Nucleation-Based Synthesis Engine**

## **1\. Core Philosophy: Acoustic Nucleation**

This system translates a 6-digit Ternary number (the Ditrune) into a complex acoustic event.  
Unlike standard synthesis which treats sound as a single wave, this system treats sound as a "living organism" composed of three concentric layers:

1. **The Outer Shell (Red):** The Physical Body (Mass & Gravity) $\\rightarrow$ **Pitch**  
2. **The Inner Shell (Green):** The Breath (Movement & Life) $\\rightarrow$ **Dynamics/Envelope**  
3. **The Core (Blue):** The Soul (Entropy & Stability) $\\rightarrow$ **Timbre**

## **2\. Input Architecture**

Input: A 6-digit Ditrune (e.g., 210120\)  
Parsing: The Ditrune is split into three mirrored "Bigrams" (pairs of digits).

| Layer | Lines | Channel | Function |
| :---- | :---- | :---- | :---- |
| **Outer** | Lines 1 & 6 | **Red** | Determines the fundamental frequency (Octave). |
| **Inner** | Lines 2 & 5 | **Green** | Determines the amplitude envelope (Attack/Sustain). |
| **Core** | Lines 3 & 4 | **Blue** | Determines the waveform purity (Stability). |

Value Calculation:  
Each Bigram (base-3) is converted to a specific 8-bit Integer (0-254) using the Step Value Table.

| Bigram | Ternary | Step Value (Decimal) | Step Value (Hex) |
| :---- | :---- | :---- | :---- |
| **00** | 0 | **0** | 0x00 |
| **01** | 1 | **37** | 0x25 |
| **02** | 2 | **60** | 0x3C |
| **10** | 3 | **97** | 0x61 |
| **11** | 4 | **134** | 0x86 |
| **12** | 5 | **157** | 0x9D |
| **20** | 6 | **194** | 0xC2 |
| **21** | 7 | **231** | 0xE7 |
| **22** | 8 | **254** | 0xFE |

## **3\. Channel Mapping: The Red Outer Shell (Body)**

Concept: Gravitational Weight.  
Parameter: Pitch / Octave Register.  
Logic: Low values are massive and heavy (Earth). High values are light and ethereal (Air).

| Bigram | Value | Anchor Note | Freq (Hz) | Description |
| :---- | :---- | :---- | :---- | :---- |
| **00** | 0 | **C1** | 32.7 | **Sub-Bass.** Felt in the chest. Thunder. |
| **01** | 37 | **C2** | 65.4 | **Bass.** Deep cello range. Heavy foundation. |
| **02** | 60 | **C3** | 130.8 | **Baritone.** Low male voice. Warmth. |
| **10** | 97 | **G3** | 196.0 | **Tenor.** High male voice range. Bridge. |
| **11** | 134 | **C4** | 261.6 | **Middle C.** The Center. Balanced mass. |
| **12** | 157 | **C5** | 523.2 | **Alto/Soprano.** High female voice. Clear. |
| **20** | 194 | **C6** | 1046.5 | **Treble.** Flute/Whistle. Piercing. |
| **21** | 231 | **C7** | 2093.0 | **High Treble.** Piccolo range. Shimmering. |
| **22** | 254 | **C8** | 4186.0 | **Brilliance.** Edge of musicality. "Light." |

## **4\. Channel Mapping: The Green Inner Shell (Breath)**

Concept: Kinetic Energy.  
Parameter: Amplitude Envelope (ADSR).  
Logic: How does the entity enter the physical world?

| Bigram | Value | Type | Attack Time | Sustain Level | Sonic Behavior |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **00** | 0 | **The Ghost** | Slow (2.0s) | Low (40%) | Fades in from nothing. Dreamy. |
| **01** | 37 | **The Swell** | Med-Slow (1.0s) | Med (60%) | Like a deep breath or ocean wave. |
| **02** | 60 | **The Pad** | Soft (500ms) | High (90%) | Smooth, constant presence. Organ-like. |
| **10** | 97 | **The Bow** | Legato (200ms) | Full (100%) | Connected, singing motion. Violin. |
| **11** | 134 | **The Step** | Walking (50ms) | Full (100%) | Clear start. Piano-like. Balanced. |
| **12** | 157 | **The Pluck** | Fast (10ms) | Low (0%) | Plucked string. Decays immediately (Harp). |
| **20** | 194 | **The Strike** | Instant (1ms) | Med (50%) | Hard impact. Percussive (Drum). |
| **21** | 231 | **The Pulse** | Rhythmic | Pulsing | Tremolo effect. Shaking energy. |
| **22** | 254 | **The Spark** | Glitch | Stutter | Micro-percussion. Electric short-circuit. |

## **5\. Channel Mapping: The Blue Core (Soul)**

Concept: Entropy & Stability.  
Parameter: Timbre (Waveform) & Saturation.  
Logic: The state of the nucleus. Is it ordered (Sine) or chaotic (Noise)?

| Bigram | Value | State | Waveform | Harmonic Content |
| :---- | :---- | :---- | :---- | :---- |
| **00** | 0 | **The Void** | Sine | **Pure.** No harmonics. Cold, hollow. |
| **01** | 37 | **Deep Water** | Sine \+ Sub | **Weighted.** Heavy fundamental. |
| **02** | 60 | **Wood** | Triangle | **Soft.** Odd harmonics only. Flute-like. |
| **10** | 97 | **Liquid** | Triangle \+ Chorus | **Moving.** The sound swims/detunes slightly. |
| **11** | 134 | **Solid** | Square | **Hollow.** Odd harmonics. Clarinet-like. |
| **12** | 157 | **Vibrating** | Pulse Width | **Nasal.** Pinching sound. Oboe-like. |
| **20** | 194 | **Plasma** | Sawtooth | **Buzzy.** All harmonics. Brass/Synth. |
| **21** | 231 | **Friction** | Distortion | **Gritty.** The wave is clipped/torn. |
| **22** | 254 | **Fire** | White Noise | **Chaos.** All frequencies. Hiss/Crash. |

## **6\. Worked Examples**

### **Example A: The "Balanced Crystal"**

**Ditrune:** 22 10 00

1. **Red (Outer) \= 22:** High Treble (C8, \~4000Hz).  
2. **Green (Inner) \= 10:** The Bow (Smooth violin-like entry).  
3. **Blue (Core) \= 00:** The Void (Pure Sine wave).  
* **Result:** A very high, pure, singing glass tone. Like running a wet finger on a crystal rim.

### **Example B: The "Industrial Impact"**

**Ditrune:** 00 20 22

1. **Red (Outer) \= 00:** Sub-Bass (C1, \~32Hz).  
2. **Green (Inner) \= 20:** The Strike (Instant, hard attack).  
3. **Blue (Core) \= 22:** Fire (Noise/Distortion).  
* **Result:** A massive, distorted explosion or kick drum.

### **Example C: The "Walking Robot"**

**Ditrune:** 11 11 11

1. **Red (Outer) \= 11:** Middle C (261Hz).  
2. **Green (Inner) \= 11:** The Step (Standard piano envelope).  
3. **Blue (Core) \= 11:** Solid (Square wave).  
* **Result:** A classic "Video Game" beep. Perfectly centered, 8-bit, and neutral.