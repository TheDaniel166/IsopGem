# Rich Text Editor Plugin Architecture

**Date:** 2026-01-13
**Status:** Implemented (Phase 1)
**Related Laws:** Law of the Substrate, Sovereignty

## Overview
The Rich Text Editor (RTE) has been refactored from a monolithic orchestrator into an extensible plugin host. This allows features to be injected from external Pillars, enabling better modularity and strict adherence to architectural boundaries.

## Core Concepts

### 1. EditorFeature Interface
All RTE features now inherit from `EditorFeature` (in `feature_interface.py`).
- **Standard Init:** `__init__(self, parent_editor: 'RichTextEditor')`
- **Orchestrator Access:** `self.orchestrator` (The RichTextEditor instance)
- **Editor Access:** `self.editor` (The inner safe wrapper around QTextEdit)
- **Hooks:** `initialize()`, `extend_context_menu(menu, pos)`

### 2. Dependency Injection
`RichTextEditor.__init__` now accepts an optional `features` list.
```python
editor = RichTextEditor(features=[
    MyCustomFeature(parent_editor),
    AnotherFeature(parent_editor)
])
```
If `features` is provided, ONLY those features are loaded.
If `features` is `None` (default), the legacy suite of features is instantiated to maintain backward compatibility.

### 3. Legacy Feature Support
To ensure zero regression during the transition, the `RichTextEditor` maintains a "Legacy Monolith Mode". If no features are injected, it automatically instantiates:
- `EtymologyFeature`
- `TableFeature`
- `MermaidFeature`
- `MathFeature`
- `ShapeFeature`
- `ListFeature`
- `SearchReplaceFeature`
- `SpellFeature`
- `ImageInsertFeature`
- `ImageEditFeature`

All of these features have been refactored to the new interface but are instantiated with `self` (the editor) in the constructor.

## Next Steps (Transition Phase)
1. **Move Files:** Move specialized features (e.g., `MermaidFeature`, `EtymologyFeature`) into their respective Pillars (e.g., `DocumentManager`, `Wiki`).
2. **Update Consumers:** Modify consuming windows (e.g., `WikiWindow`, `GematriaWindow`) to explicitly inject the features they need.
3. **Purify Editor:** Remove the "Legacy Monolith Mode" instantiation block from `RichTextEditor`, making it a pure host that does nothing without plugins.
