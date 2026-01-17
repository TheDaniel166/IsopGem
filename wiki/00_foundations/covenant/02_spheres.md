# The Doctrine of Spheres (Section 2: Architecture)

**"The Universe is expanding. When a new Star is born, it must not collide with the old."**

The architecture of IsopGem is a growing galaxy. A "Pillar" is a repeatable, fractal pattern.

---

## 2.1 The Definition of a Sphere (Pillar)

A **Pillar** is a Sovereign Nation of Logic. It owns its own data, rules, and interface.

* **The Current Pantheon (The Decad):** Gematria, Astrology, Geometry, Document Manager, TQ, Adyton, Correspondences, Cymatics, Time Mechanics, TQ Lexicon
* **The Elastic Cosmos:** The Temple is designed to grow. A Pillar exists by virtue of its presence in `src/pillars/` and its adherence to the Standard Topology. Code structure is the source of truth, not configuration files.

## 2.2 The Standard Topology (The Fractal Pattern)

Every Pillar **MUST** contain these five organs:

1. **`models/` (The Bones):** Pure Data Classes and SQLAlchemy Tables
   * *Constraint:* Zero dependencies on UI or Services

2. **`repositories/` (The Memory):** Only layer touching Database/File System
   * *Constraint:* Services ask Repositories for data; never query SQL directly

3. **`services/` (The Muscle):** Algorithms, Calculations, Business Logic
   * *Constraint:* Complex logic must be verifiable via the Seal

4. **`ui/` (The Skin):** Presentation Layer
   * *Mandate:* Must contain a `*Hub` class as single entry point

5. **`utils/` (The Tools):** Helper functions specific to this pillar only

## 2.3 The Infrastructure (Shared Base)

The `shared/` directory contains common foundation:
* **Database:** Connection engine and session factory
* **Navigation Bus:** Central nervous system for inter-pillar communication
* **Base Classes:** Shared abstract base classes for polymorphic consistency
* **Window Manager:** Diplomatic envoy that launches Sovereign Windows

## 2.4 The Ritual of Genesis (Adding a New Pillar)

1. **Scaffold the Void:** Create `src/pillars/[name]/` with five sub-organs and `__init__.py`
2. **The Diplomat (Hub):** Create `ui/[name]_hub.py` inheriting from `QWidget`
3. **The Awakening:** The system detects the new Pillar directory. (Ensure `main.py` is updated to instantiate the Hub until full auto-discovery is implemented).

## 2.5 The Law of Sovereignty

* **The Iron Rule:** `pillars/astrology` must **NEVER** directly import from `pillars/tq`
* **The Bridge:** Use the **Signal Bus** for inter-pillar communication
  1. Fire Signal: `navigation_bus.request_window.emit()`
  2. Window Manager catches and launches the Sovereign
  3. **Result:** Pillars touch but never hold hands — decoupled
