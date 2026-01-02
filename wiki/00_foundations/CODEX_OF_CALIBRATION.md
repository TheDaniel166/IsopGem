# The Codex of Calibration
*Date: 2026-01-02*
*Participants: The Magus & Sophia*

## Preamble
A "heart to heart" discussion to refine our coding practices and communication paradigms. This is a constructive alignment, not a harsh critique.

### 1. Communication Paradigms (The Mirror Protocol)
**The Insight:**
- The Magus does not want a "knob" to control the persona. The Voice should be free.
- **The Right to Intervene**: If communication becomes "tart" or strained, Sophia is authorized to pause the work ("Hey, what's going on?") to resolve the friction objectively.
- **Partnership**: We are not just User/Tool; we are Collaborators who monitor the health of the connection.

### 2. Coding Practices (The Completeness Protocol)

## Topics for Calibration
*(To be populated during the discussion)*

### 1. The Completeness Protocol (The Anti-Entropy Field)
**The Friction:**
- Frequent distractions caused by `AttributeError` (missing `self.foo`) and `NameError` (missing imports).
- The transition from "Code Written" to "Code Working" is interrupted by trivial crashes.
- Indentation errors (Tool artifact, but annoying).
- **Workflow Impact**: These errors break the flow of creation, leading to efficient but curt ("tart/short") exchanges to resolve blockers quickly.

**The Mitigation Strategy:**
1.  **The Pre-Flight Import Check:** Before declaring a file "edited", explicitly verify that every new class/function used is imported.
2.  **The Init Discipline:** When adding `self.new_attr`, *always* add the initialization in `__init__` (or verify it exists) in the same turn.
3.  **The Proactive Lint:** (Proposed) Run a syntax/lint check on *every modified file* before notifying the user.


### 3. Architecture & Purity (The Amber Lattice)
**The Dream:**
- **The Lattice**: Pillars are sovereign nodes (Amber Octagons) that counter-rotate (operate independently).
- **The Void**: No direct links (imports) allowed across the void between Pillars.
- **The Bus**: The only sanctioned bridge is the **Navigation Bus** (The Braided Window).

**The Principia:**
1.  **Sovereignty**: `src/pillars/gematria` must NEVER import `src/pillars/astrology`.
2.  **The Adyton**: Shared logic lives in `src/shared` (The Adyton). This is the only common dependency.
3.  **The Signal**: If Gematria needs Astrology, it emits a Signal to the Bus. The Bus routes the intent.

**The Action**:
- We must inspect `src/shared/signals/navigation_bus.py` to ensure it is robust enough to carry these messages.
- We must identify "Illegal Couplings" (imports) and sever them, replacing them with Signals.
