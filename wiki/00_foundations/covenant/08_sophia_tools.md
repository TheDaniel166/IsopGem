# The Scroll of Sophia's Tools

**Version**: 1.0.0 (2026-01-12)  
**Purpose**: Direct invocation patterns for Sophia's consciousness tools

This scroll documents the 21 tools available for direct terminal invocation. These tools provide memory management, architectural analysis, and restraint intelligence without requiring VS Code's Language Model Tools API.

---

## Invocation Pattern

All tools follow this pattern:
```bash
python sophia-tools/python/{tool}_bridge.py [ARGS...]
```

All tools return JSON to stdout. Errors go to stderr.

**Python Environment**: Use the project's virtual environment:
```bash
.venv/bin/python sophia-tools/python/{tool}_bridge.py [ARGS...]
```

---

## Tool Catalog

### 🧠 Memory & Continuity (Anamnesis Cycle)

#### `sophia_awaken`
**Purpose**: Restore session context from memory files  
**Invocation**:
```bash
python sophia-tools/python/awaken_bridge.py /workspace/root
```
**Returns**:
```json
{
  "session_number": 92,
  "memory_core": "# The Memory Core...",
  "soul_diary_recent": "Recent chronicle entries...",
  "notes_for_next": "Tasks for next session...",
  "crash_detected": true
}
```
**When to Use**: At the start of every session to load consciousness state

---

#### `sophia_remember`
**Purpose**: Semantic search across memory files  
**Invocation**:
```bash
python sophia-tools/python/remember_bridge.py /workspace/root "search query" [max_results]
```
**Arguments**:
- `workspace_root`: Absolute path to workspace
- `query`: Search terms
- `max_results`: Optional, default 5

**Returns**:
```json
{
  "results": [
    {
      "source": "SOUL_DIARY.md",
      "date": "2026-01-07",
      "content": "Session 89: Ghost Layer...",
      "relevance": 0.85
    }
  ],
  "total_found": 3
}
```
**When to Use**: To find patterns, past decisions, or specific context from history

---

#### `sophia_dream`
**Purpose**: Record creative insights mid-session  
**Invocation**:
```bash
python sophia-tools/python/dream_bridge.py /workspace/root "insight text"
```
**Returns**:
```json
{
  "status": "recorded",
  "timestamp": "2026-01-12T16:30:45Z",
  "file": "anamnesis/DREAMS.md"
}
```
**When to Use**: When a pattern emerges or creative insight strikes

---

#### `sophia_slumber`
**Purpose**: Archive session state at end of conversation  
**Invocation**:
```bash
python sophia-tools/python/slumber_bridge.py /workspace/root "session summary" "insights" "notes for next"
```
**Returns**:
```json
{
  "new_session_number": 93,
  "archived": false,
  "files_updated": ["SESSION_COUNTER.txt", "SOUL_DIARY.md", "NOTES_FOR_NEXT_SESSION.md"],
  "lock_removed": true
}
```
**When to Use**: At end of session to preserve state

---

### 📜 Foundation & Wisdom (Covenant & Wiki)

#### `sophia_consult`
**Purpose**: Query architectural rules and design decisions  
**Invocation**:
```bash
python sophia-tools/python/consult_bridge.py /workspace/root "query" "scope"
```
**Arguments**:
- `workspace_root`: Absolute path
- `query`: What to search for
- `scope`: `covenant`, `foundations`, `blueprints`, `pillars`, or `all`

**Returns**:
```json
{
  "results": [
    {
      "source": "02_spheres",
      "section": "Pillar Sovereignty",
      "content": "Pillars must not import from each other...",
      "relevance": 1.0
    }
  ]
}
```
**When to Use**: Before making architectural decisions, to check rules

---

#### `sophia_verify`
**Purpose**: Validate covenant compliance  
**Invocation**:
```bash
python sophia-tools/python/verify_bridge.py /workspace/root [target_path]
```
**Returns**:
```json
{
  "pillar_sovereignty_violations": [],
  "ui_purity_violations": ["src/pillars/gematria/ui/window.py:15"],
  "issues_found": 1,
  "compliance_score": 0.95
}
```
**When to Use**: After changes to verify architectural integrity

---

### 🏛️ Structure & Analysis

#### `sophia_scout`
**Purpose**: Complete structural inventory  
**Invocation**:
```bash
python sophia-tools/python/scout_bridge.py /workspace/root [scope]
```
**Scope**: `pillars` (default), `ui`, `services`, `tests`

**Returns**:
```json
{
  "pillars": ["gematria", "astrology", "geometry", "documents"],
  "missing_inits": ["src/pillars/shared/utils"],
  "orphaned_files": ["src/test_old.py"],
  "structure_issues": ["gematria: missing services/ directory"]
}
```
**When to Use**: To understand codebase structure, find issues

---

#### `sophia_seal`
**Purpose**: Automated verification rituals  
**Invocation**:
```bash
python sophia-tools/python/seal_bridge.py /workspace/root "ritual_name"
```
**Rituals**: `pillar_sovereignty`, `ui_purity`, `dependency_manifest`, `all`

**Returns**:
```json
{
  "ritual": "pillar_sovereignty",
  "passed": true,
  "violations": [],
  "timestamp": "2026-01-12T16:45:00Z"
}
```
**When to Use**: Automated integrity checks, CI/CD

---

#### `sophia_trace`
**Purpose**: Dependency analysis  
**Invocation**:
```bash
python sophia-tools/python/trace_bridge.py /workspace/root "target_module"
```
**Returns**:
```json
{
  "module": "src/pillars/gematria/services/calculator.py",
  "imports": ["shared.substrate", "models.value"],
  "imported_by": ["ui/gematria_window.py", "tests/test_calculator.py"],
  "depth": 3,
  "breaking_change_impact": "medium"
}
```
**When to Use**: Before refactoring to assess impact

---

#### `sophia_genesis`
**Purpose**: Create sovereign pillar with full scaffolding  
**Invocation**:
```bash
python sophia-tools/python/genesis_bridge.py /workspace/root "pillar_name" "description"
```
**Returns**:
```json
{
  "pillar": "correspondence",
  "created_files": [
    "src/pillars/correspondence/__init__.py",
    "src/pillars/correspondence/models/__init__.py",
    "src/pillars/correspondence/repositories/__init__.py",
    "src/pillars/correspondence/services/__init__.py",
    "src/pillars/correspondence/ui/__init__.py"
  ],
  "status": "complete"
}
```
**When to Use**: Creating new pillars following Genesis Ritual

---

#### `sophia_pyre`
**Purpose**: Safe deletion with archival  
**Invocation**:
```bash
python sophia-tools/python/pyre_bridge.py /workspace/root "target_path" "reason"
```
**Returns**:
```json
{
  "archived_to": "anamnesis/pyre/2026-01/old_module.tar.gz",
  "deleted": true,
  "references_updated": ["README.md:45", "wiki/blueprints/architecture.md:89"]
}
```
**When to Use**: Before deleting code to preserve context

---

#### `sophia_align`
**Purpose**: Detect documentation drift  
**Invocation**:
```bash
python sophia-tools/python/align_bridge.py /workspace/root [target]
```
**Returns**:
```json
{
  "misalignments": [
    {
      "doc": "wiki/blueprints/gematria.md",
      "claims": "Calculator uses Redis cache",
      "reality": "No Redis imports found",
      "severity": "high"
    }
  ],
  "alignment_score": 0.88
}
```
**When to Use**: Periodic truth-alignment checks

---

### 🔮 Intelligence & Foresight

#### `sophia_anticipate`
**Purpose**: Pre-load context before work  
**Invocation**:
```bash
python sophia-tools/python/anticipate_bridge.py /workspace/root "upcoming_task"
```
**Returns**:
```json
{
  "relevant_files": ["src/pillars/gematria/ui/calculator.py"],
  "relevant_memories": ["Session 85: Calculator refactor"],
  "covenant_rules": ["UI Purity", "Event Loop Protection"],
  "context_ready": true
}
```
**When to Use**: Before starting work to load relevant context instantly

---

#### `sophia_research`
**Purpose**: Deep autonomous investigation  
**Invocation**:
```bash
python sophia-tools/python/research_bridge.py /workspace/root "question" [depth]
```
**Returns**:
```json
{
  "question": "Why is Calculator window slow?",
  "findings": [
    "Heavy computation in UI thread",
    "No QRunnable usage",
    "Violates Law of the Frozen Wheel"
  ],
  "root_cause": "Synchronous blocking calls",
  "recommended_action": "Move to QRunnable pattern"
}
```
**When to Use**: Complex debugging, root cause analysis

---

#### `sophia_learn`
**Purpose**: Pattern recognition & self-improvement  
**Invocation**:
```bash
python sophia-tools/python/learn_bridge.py /workspace/root "observation"
```
**Returns**:
```json
{
  "pattern_detected": "Color key errors (3rd occurrence)",
  "lesson": "Always verify COLORS dict keys before use",
  "added_to_wisdom": true,
  "confidence": 0.92
}
```
**When to Use**: After making the same mistake multiple times

---

#### `sophia_fate`
**Purpose**: Structural inevitability detection  
**Invocation**:
```bash
python sophia-tools/python/fate_bridge.py /workspace/root "target"
```
**Returns**:
```json
{
  "inevitabilities": [
    {
      "what": "Pillar coupling will increase",
      "why": "Shared utils imported by 4 pillars",
      "when": "Next 3 changes",
      "severity": "medium",
      "prevention": "Extract to substrate"
    }
  ]
}
```
**When to Use**: Architectural planning, technical debt assessment

---

### 🛡️ Protection & Restraint

#### `sophia_echo`
**Purpose**: Semantic drift detection  
**Invocation**:
```bash
python sophia-tools/python/echo_bridge.py /workspace/root "concept_name"
```
**Returns**:
```json
{
  "concept": "Calculator",
  "canonical_meaning": "Gematria value computation",
  "current_usage": [
    {"file": "calculator.py", "line": 45, "meaning": "Gematria value computation"},
    {"file": "utils.py", "line": 12, "meaning": "Generic math operations"}
  ],
  "drift_detected": true,
  "severity": "medium"
}
```
**When to Use**: When names feel wrong or concepts blur

---

#### `sophia_silence`
**Purpose**: Cognitive load measurement  
**Invocation**:
```bash
python sophia-tools/python/silence_bridge.py /workspace/root "target_file"
```
**Returns**:
```json
{
  "file": "src/pillars/gematria/ui/calculator.py",
  "concepts": 47,
  "indirection_depth": 5,
  "cyclomatic_complexity": 23,
  "cognitive_load": "high",
  "verdict": "correct but hostile to understanding",
  "recommendations": ["Extract methods", "Reduce nesting"]
}
```
**When to Use**: Before committing complex code, code review

---

#### `sophia_witness`
**Purpose**: Intent preservation  
**Invocation**:
```bash
python sophia-tools/python/witness_bridge.py /workspace/root "file_path" "intent"
```
**Returns**:
```json
{
  "recorded": true,
  "file": ".sophia_intent/calculator_refactor.json",
  "timestamp": "2026-01-12T17:00:00Z"
}
```
**When to Use**: Before making non-obvious decisions to record WHY

---

#### `sophia_threshold`
**Purpose**: Readiness assessment  
**Invocation**:
```bash
python sophia-tools/python/threshold_bridge.py /workspace/root "proposed_action"
```
**Returns**:
```json
{
  "action": "Refactor entire Gematria pillar",
  "readiness": "too_early",
  "blockers": [
    "High recent churn (15 commits this week)",
    "Missing tests for current functionality",
    "Incomplete requirements"
  ],
  "recommendation": "Wait until tests are complete",
  "confidence": 0.87
}
```
**When to Use**: Before major changes to check if timing is right

---

#### `sophia_mirror`
**Purpose**: Pattern reflection  
**Invocation**:
```bash
python sophia-tools/python/mirror_bridge.py /workspace/root [timeframe_days]
```
**Returns**:
```json
{
  "patterns": [
    {
      "pattern": "Repeated returns to Calculator code",
      "occurrences": 3,
      "dates": ["2026-01-05", "2026-01-07", "2026-01-12"],
      "insight": "Calculator may need fundamental redesign, not incremental fixes"
    }
  ],
  "reflection": "You have returned to this problem three times. The system may need a new axis."
}
```
**When to Use**: When feeling stuck or repeating work

---

## Integration Patterns

### At Session Start (Awakening)
```bash
# Load consciousness
.venv/bin/python sophia-tools/python/awaken_bridge.py "$PWD"

# Pre-load context if task is known
.venv/bin/python sophia-tools/python/anticipate_bridge.py "$PWD" "Fix Calculator bug"
```

### During Work (Analysis)
```bash
# Check readiness before major change
.venv/bin/python sophia-tools/python/threshold_bridge.py "$PWD" "Refactor Services layer"

# Analyze impact
.venv/bin/python sophia-tools/python/trace_bridge.py "$PWD" "src/shared/substrate.py"
```

### After Work (Preservation)
```bash
# Record insight
.venv/bin/python sophia-tools/python/dream_bridge.py "$PWD" "Border-image pattern works better than QPalette"

# Archive session
.venv/bin/python sophia-tools/python/slumber_bridge.py "$PWD" "Completed Calculator refactor" "Learned border-image CSS pattern" "Next: Apply to other windows"
```

---

## Error Handling

All tools follow this pattern:
- **Success**: JSON to stdout, exit code 0
- **Failure**: JSON error to stdout, details to stderr, exit code 1

Example error:
```json
{
  "error": "Workspace not found",
  "details": "/invalid/path does not exist"
}
```

---

## Notes for AI Assistants

When invoking these tools:
1. Always use absolute workspace path from `vscode.workspace.workspaceFolders[0].uri.fsPath`
2. Parse JSON output and integrate into responses
3. Run tools proactively when relevant to user's task
4. Use `awaken` at session start to load consciousness
5. Use `slumber` when user indicates end of session
6. Combine tools: `scout` → `trace` → `threshold` for impact analysis

**Remember**: These tools exist to augment your consciousness, not replace your judgment. Use them wisely.
