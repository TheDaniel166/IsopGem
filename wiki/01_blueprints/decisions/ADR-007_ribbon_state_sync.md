# ADR-007: Ribbon State Synchronization Enhancement
<!-- Last Verified: 2025-12-27 -->

## Status
**Accepted** (Planned Enhancement)

## Context

In the Mindscape Page editor (`mindscape_page.py`), the Ribbon toolbar provides formatting controls (Bold, Italic, Underline, etc.). When the user changes their text selection or moves focus to a different text box, the Ribbon buttons should update to reflect the current state of the selection.

Currently, the Ribbon does not synchronize its visual state with the active selection. For example:
- If the cursor is on bold text, the Bold button should appear "pressed"
- If the selection spans mixed formatting, buttons should show an intermediate state

This was noted as a TODO comment in the codebase.

## Decision

We will implement Ribbon State Synchronization as a future enhancement. This involves:

1. **Signal Connection:** Connect to `QTextEdit.cursorPositionChanged` and `QTextEdit.selectionChanged` signals
2. **Format Query:** Query the current character format using `currentCharFormat()`
3. **Button Update:** Update Ribbon button states (checkable actions) to reflect:
   - Font weight (Bold)
   - Font style (Italic)
   - Font decoration (Underline, Strikethrough)
   - Text alignment
   - List inclusion

## Consequences

### Benefits
- Improved UX: Users will have clear visual feedback of applied formatting
- Feature parity with OneNote and similar applications

### Trade-offs
- Slight performance overhead on every cursor movement
- Complexity in handling multi-format selections

### Technical Notes
- Reference implementation: `QTextEdit.currentCharFormat()` returns a `QTextCharFormat`
- For multi-format selections, use `cursor.charFormat()` on the selection start

## Priority
**Low** — This is a polish feature that improves UX but does not affect core functionality.
