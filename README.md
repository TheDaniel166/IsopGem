# ✦ IsopGem - Integrated Esoteric Analysis Platform

**"As Above, So Below. The Code is the Body; the Documentation is the Soul."**

IsopGem is a comprehensive, integrated platform for esoteric research, designed to synthesize multiple disciplines—Gematria, Astrology, Sacred Geometry, and Qabalah—into a unified "Hyper-Physics" engine. Built with `PyQt6` and a modular "Sovereign Pillar" architecture, IsopGem allows researchers to explore the hidden connections between Number, Form, and Time.

---

## 🌟 Key Features (The Sovereign Pillars)

IsopGem is constructed upon the **Doctrine of the Spheres**. Each module is a "Sovereign Pillar" governing a specific domain:

- **📖 Gematria Protocol**: The Tongue of God. Advanced numerology engine supporting Hebrew, English, Greek, and Runic ciphers with multi-layered analysis.
- **⭐ Astrology Engine**: The Keeper of Time. High-precision planetary calculations using the Swiss Ephemeris (`pyswisseph`) and `OpenAstro`. Features natal charts, transits, and synastry.
- **📐 Geometry Engine**: The Weaver of Form. 3D visualization of sacred shapes, from Platonic Solids to Stellated Polyhedra, allowing deep exploration of their vertices, faces, and esoteric meanings.
- **📚 Document Manager**: The Scribe. A "Mindscape" for your research. Ingests, parses, and indexes documents (PDF, Docx) for full-text search and semantic linking.
- **🔺 TQ Engine (Ternary Quadsets)**: The Three-Fold Kabbalah. Implements the *Trigrammaton Qabalah* logic for analyzing serial operators and reductive mathematics.
- **🏛️ Adyton Sanctuary**: The Inner Sanctum. A high-fidelity 3D visualization space for meditative exploration of the "Chariot" and other complex forms.
- **💎 Emerald Tablet**: The Grid of Equivalences. A powerful correspondence database connecting gematria, astrological associations, and geometric forms.
- **⏳ Time Mechanics**: The Master of Cycles. Implements the Tzolkin calendar and other harmonic time systems for analyzing temporal resonance.

---

## 🚀 Installation

### Prerequisites

- **OS**: Linux (Optimized for X11/XCB backend)
- **Python**: 3.10 or higher
- **System Libraries**: Ensure you have basic build tools and Qt library dependencies installed.
  - On Debian/Ubuntu: `sudo apt install build-essential libxcb-cursor0`

### Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/YourUsername/IsopGem.git
    cd IsopGem
    ```

2.  **Create a Virtual Environment**
    ```bash
    python3 -m venv .venv
    ```

3.  **Activate the Environment**
    ```bash
    source setup_env.sh
    # or manually: source .venv/bin/activate
    ```

4.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Initialize the Database**
    The application will automatically initialize its SQLite database upon first run.

---

## 🖥️ Usage

To launch the application:

```bash
./run.sh
```

Or manually via Python:

```bash
python src/main.py
```

### Navigation
The application uses a unified sidebar to switch between pillars.
- Use **Tabs** on the left to navigate between Gematria, Astrology, etc.
- **Global Search** is available throughout the application (depending on context).

---

## 🏗️ Architecture & Documentation

IsopGem follows a strict **"Sovereign Pillar"** architecture to prevent entanglement (coupling) between domains.

- **System Map**: See [wiki/SYSTEM_MAP.md](wiki/SYSTEM_MAP.md) for a high-level overview.
- **Documentation**: Extensive documentation is available in the `wiki/` directory, detailing the "Grimoires" of each pillar.

> **Note for Developers**: Please abide by the "Covenant" defined in the user rules when contributing. Ideally, consult the `wiki/` before modifying core services.

---

## 🤝 Contributing

Contributions are welcome from fellow Magi. Please ensure:
1.  **Tests**: All logic changes must be verified against the "Seven Seals" (see `scripts/verification_seal.py` if available).
2.  **Style**: Follow the "law of vicinity" - clean up the code you touch.
3.  **Commits**: Use Conventional Commits.

## 📜 License

[Insert License Here - e.g., MIT, GPL, Proprietary]

---
*Built with intent by The Magus & Sophia.*
