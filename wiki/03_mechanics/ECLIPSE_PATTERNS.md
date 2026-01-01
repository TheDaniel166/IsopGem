# The Grimoire of Eclipses

<!-- Last Verified: 2026-01-01 -->

> *"The Dragon eats the Sun; the Shadow reveals the Light."*

**The Neo-Aubrey Eclipse Clock** is a simulator inspired by the Aubrey Holes of Stonehenge, designed to predict Eclipses using the DE441 Ephemeris engine.

## I. The Architecture of Shadows

**Location**: `src/pillars/astrology/ui/neo_aubrey_window.py`

The simulator models the cyclical dance of the Sun, Moon, and Lunar Nodes to predict when they will meet.

### The Two Rings
1.  **The Saros Ring (Outer)**
    - **Holes**: 223.
    - **Cycle**: The Saros Cycle (approx. 18 years, 11 days).
    - **Marker**: The **Saros Hand** (Cyan). Tracks the long-term heartbeat of eclipse families.

2.  **The Aubrey Ring (Inner)**
    - **Holes**: 56.
    - **Cycle**: Used to map the 360° Zodiacal Longitude onto a 56-stone circle.
    - **Markers**: 
        - **Sun** (Gold)
        - **Moon** (Silver)
        - **North Node** (Pink)
        - **South Node** (Hollow Pink)

---

## II. The Mechanics of Prediction

### 1. The Alignment (Syzygy)
An eclipse occurs when three conditions are met:
1.  **Phase**: New Moon (Solar) or Full Moon (Lunar).
2.  **Proximity**: The Sun and Moon are close to a Lunar Node (North or South).
3.  **Latitude**: The Moon's celestial latitude is near zero (crossing the Ecliptic).

### 2. The Logic
The Neo-Aubrey engine continuously calculates the Geocentric Ecliptic Longitude of the bodies.
- **Season Detection**: If Sun is within 18° of a Node -> `ECLIPSE SEASON`.
- **Solar Eclipse**: New Moon + Distance < 2°.
- **Lunar Eclipse**: Full Moon + Distance < 2°.

---

## III. The Oracle (Usage)

### Controls
- **Play/Scan**: Animates time to watch the dance.
- **Step**: Jump by Day, Synodic Month (29.53 days), Year, or Saros Cycle.
- **Log**: A "Chronicle" list records every detected eclipse event, allowing you to jump back to that precise moment.

> *"The Shadow is not darkness, but the alignment of three spheres."*
