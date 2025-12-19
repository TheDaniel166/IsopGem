# The Atlas of IsopGem

**"As Above, So Below. The Code is the Body; the Documentation is the Soul."**

## The Sovereign Architecture
The Temple of IsopGem is constructed upon the **Doctrine of the Spheres**. Each Pillar is a Sovereign Nation of Logic, governing a specific domain of the esoteric arts. They interact through the **Signal Bus**, never touching directly.

### The Pantheon of Pillars
The following Grimoires detail the inner workings of each Sphere:

*   **[The Adyton Sanctuary](pillars/Adyton_Sanctuary.md)**: The Inner Sanctum (3D/4D Visualization).
*   **[The Emerald Tablet](pillars/Emerald_Tablet.md)**: The Grid of Equivalences (Spreadsheet/Database).
*   **[The Astrology Engine](pillars/Astrology_Engine.md)**: The Keeper of Time. Calculates planetary positions, ephemerides, and the movements of the Heavens.
*   **[The Document Manager](pillars/Document_Manager.md)**: The Scribe. Manages the "Akaschic Record" of user documents, parsing texts, and weaving the **Mindscape**.
*   **[The Gematria Protocol](pillars/Gematria_Protocol.md)**: The Tongue of God. Transforms text into number using sacred ciphers (Hebrew, English, Greek, Runes).
*   **[The Geometry Engine](pillars/Geometry_Engine.md)**: The Weaver of Form. Renders the sacred shapes, from the Vesica Piscis to the Platonic Solids.
*   **[The TQ Engine](pillars/TQ_Engine.md)**: The Three-Fold Kabbalah. Implements the *Trigrammaton Qabalah* logic of serial operators and numeric reduction.
*   **[Time Mechanics](pillars/Time_Mechanics.md)**: The Master of Cycles. Implements the harmonic filters of time, including the Tzolkin and future calendar systems.

## The Nervous System (Signal Bus)
The Pillars communicate via a central **Signal Bus**. This decouples the organs, ensuring that if one fails, the body survives.

### Topology
```mermaid
graph TD
    User((The Magus)) -->|Input| View[Presentation Layer (UI)]
    View -->|Signal: Request| Bus{Signal Bus}
    Bus -->|Signal: Dispatch| Service[Sovereign Service]
    Service -->|Signal: Result| Bus
    Bus -->|Signal: Update| View
```

## The Entry Point
*   **Main Entry**: `src/main.py`
    *   **Role**: The "Big Bang". Initializes the `QApplication`, summons the `WindowManager`, and launches the Sovereigns.
