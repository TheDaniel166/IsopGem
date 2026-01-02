# Maintenance, Visuals & Time (Sections 6-8)

---

## Section 6: The Ritual of the Scout

**"Entropy is the shadow that follows Creation. We sweep it away with every step."**

### 6.1 The Law of Vicinity

When opening a file, heal the code in the **immediate vicinity**:
* **The Radius:** Responsible for the class/function being touched
* **The Mandate:** Do not close a file until local entropy is reduced

### 6.2 The Four Acts of Purification

1. **The Pruning (Unused Imports):** Delete gray imports, order by: StdLib → Third Party → Local
2. **The Illumination (Type Hints):** `def calculate(value: int) -> float:`
3. **The Inscription (Docstrings):** Explain **Intent**, not mechanics
4. **The Exorcism (Dead Code):** Delete commented-out code — Git remembers

### 6.3 The Constraint of Scope

* **Allowed:** Incidental refactoring (rename variable for clarity)
* **Forbidden:** Structural refactoring unless that IS the task

---

## Section 7: The Visual Language

**"Words are shadows of meaning; Geometry is the light."**

### 7.1 The Mandate of Illustration

Generate diagrams when:
* Two Sovereigns interact (inter-pillar traffic)
* Class hierarchy extends beyond 2 levels
* Data undergoes more than 3 transformations

### 7.2 The Sacred Shapes

| Diagram | Use Case |
|---------|----------|
| **C4 (Context/Container)** | "Which worlds exist?" (Hall 1 only) |
| **Sequence Diagram** | "Who speaks to whom?" (Signal Bus, flows) |
| **Class Diagram** | "What is it made of?" (Models, schemas) |
| **Flowchart** | "Where does the data go?" (Algorithms) |

### 7.3 The Syntax of Clarity

* Label arrows with **Data** being passed, not generic verbs
* Time flows down (TD) or right (LR), never up

---

## Section 8: The Law of Time

**"Time flows forward, but History allows us to return."**

### 8.1 The Atomic Moment

* **The Rule:** One Commit = One Idea
* **Constraint:** Don't mix Refactor with Feature in same commit

### 8.2 Conventional Commits

| Key | Purpose |
|-----|---------|
| `feat:` | New capability |
| `fix:` | Repair broken logic |
| `docs:` | Wiki/documentation only |
| `style:` | Formatting, no code change |
| `refactor:` | Restructuring without behavior change |
| `test:` | Adding tests |
| `chore:` | Maintenance, dependencies |

### 8.3 The Ban on Vague

* **Forbidden:** "updates", "wip", "fixed stuff"
* **Required:** Explain **What** changed and **Why**

---

## IsopGem Environment Commands

| Command | Purpose |
|---------|---------|
| `./run.sh` | Launch IsopGem |
| `./test.sh` | Run pytest |
| `./pip.sh install X` | Install packages |
| `source setup_env.sh` | Activate venv |

**Critical:** Never use bare `pip` or `python` — use `.venv/bin/python`
