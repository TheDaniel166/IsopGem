# The Setup Ritual: Breathing Life into the Temple

<!-- Last Verified: 2025-12-27 -->

**"Before the Stars can be mapped, the Instrument must be built."**

This guide details the "Zero-to-Hero" process for manifesting a stable IsopGem environment on a fresh machine. Follow these steps with intent to ensure the Temple stands firm.

---

## 1. Sacrificing the Void (Prerequisites)

IsopGem is optimized for **Linux** environments. Before summoning the code, ensure your system possesses the necessary elemental libraries.

### **System Dependencies (Debian/Ubuntu)**
You must install the build-essential tools and the Qt coordinate libraries for the UI to manifest correctly.

```bash
sudo apt update
sudo apt install build-essential libxcb-cursor0 python3-dev
```

---

## 2. The Incantation of Presence (Cloning)

Pull the skeletal structure from the infinite repository.

```bash
git clone https://github.com/TheDaniel166/IsopGem.git
cd IsopGem
```

---

## 3. Breathing Life into the Clay (Venv)

We do not pollute the Global Python Realm. We create a dedicated **Virtual Environment**—a sanctuary for our dependencies.

```bash
python3 -m venv .venv
```

---

## 4. Binding the Guardians (Dependencies)

Invoke the `pip` engine to bind the external libraries to our sanctuary. Use the helper script to ensure the correct pathing.

```bash
# Activate the sanctuary
source setup_env.sh

# Bind the libraries
pip install -r requirements.txt
```

> [!IMPORTANT]
> If `pip install` fails on `pyswisseph`, ensure `python3-dev` and `build-essential` were installed in Step 1.

---

## 5. The First Spark (Launching)

Once the guardians are bound, you may launch the application.

```bash
./run.sh
```

The Temple will automatically initialize a new `isopgem.db` (The SQLite Memory) upon its first breath.

---

## 6. Sustaining the Flow (Helper Scripts)

The Magus has provided scripts to manage the environment without manual toil:

*   `source setup_env.sh`: Activates the venv and sets PYTHONPATH.
*   `./run.sh`: Launches the main application.
*   `./test.sh`: Runs the suite of tests (The Seals).
*   `scripts/pip.sh`: A proxy for `pip` that always targets the `.venv`.

---

**The Ritual is complete. The Temple is manifest.**
