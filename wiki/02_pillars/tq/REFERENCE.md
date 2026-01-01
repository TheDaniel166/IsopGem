# The Grimoire of TQ (Trigrammaton Qabalah)

<!-- Last Verified: 2026-01-01 -->

> *"Three is the Form of the Formless."*

The **TQ Pillar** is the Chamber of Triangles. It explores the mysteries of Base-3 (Ternary) logic, the Kamea of the Beast, and the sonic properties of number.

---

## I. The Logic of Three (Theory)

Unlike the binary world of silicon, TQ operates on **Ternary Logic** (0, 1, 2).
Central to this is the **Conrune Transformation**:
- `0` → `0` (Neutral remains Neutral)
- `1` → `2` (Positive becomes Negative)
- `2` → `1` (Negative becomes Positive)

This operation allows us to find the "Shadow" of any number.

---

## II. The Quadset Engine

The **Quadset** is the fundamental unit of analysis. For any input number `N`, we generate four aspects:

1.  **Identity (I)**: The number itself.
2.  **Conrune (C)**: The result of applying the Conrune transformation to its ternary form.
3.  **Reversal (R)**: The number read backwards in ternary.
4.  **Conrune of Reversal (CR)**: The conrune applied to the reversal.

**Usage**:
```python
# The QuadsetEngine calculates all four aspects + differentials
result = QuadsetEngine.analyze(156)
print(result.conrune.decimal_value)
```

---

## III. The Kamea of the Night

We map these numbers onto a **27x27 Grid** known as the Kamea.
- **Micro**: The individual cell (0-728).
- **Meso**: The 9x9 sub-grids.
- **Macro**: The 3 regions of the grid.

**Service**: `KameaGridService`
- Loads data from `kamea_baphomet.csv`.
- Provides lookup by coordinate `(x, y)` or value.

---

## IV. The Geometry of Transitions

We map number sequences to geometric forms to find **Transitions**.
- **The Lovely Star**: A heptagram mapping specific number sequences.
- **Platonic Transitions**: Mapping ternary changes across the vertices of solids.

**Service**: `GeometricTransitionService`
- Generates vertex skip patterns.
- Identifies "Families" of transitions.

---

## V. Amun: The Voice of Number

The **Amun Audio Service** converts mathematical ratios into sound.
- **Synthesis**: Additive synthesis using Saw/Square/Sine waves.
- **Signature**: Every number has a unique frequency signature based on its prime factors or TQ properties.

> *"The Number speaks, if one has the ears to hear."*
