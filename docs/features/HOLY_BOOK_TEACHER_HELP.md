# Holy Book Teacher — Help & Documentation

This document explains how to use the Holy Book Teacher window to review, correct, and teach the verse parser for "Holy Books" documents. The goal is to help you curate verse boundaries, create parser rules, and save sequences of verse splits/merges/renames for stable reuse.

## Overview

- The Holy Book Teacher analyzes a document and displays candidate verses detected by the parser or any existing curated verses saved to the database.
- You can inspect verses, edit them, and use a set of tools to adjust verse boundaries and labels.
- Once you are satisfied with the edits, save the curated verses to persist them for that document and to surface them in the Text Analysis view.

## Window Components

- Title bar: The title contains the window name and a small `?` help button which opens this help file.
- Allow inline markers: When checked, the verse parser will accept inline numeric markers as verse starts (permissive parsing). When unchecked, only numbers at the start of a line are counted.
- Verse Preview table: Shows verse number, status, offsets (start/end), source type (`parser` or `teacher`), confidence, and truncated text.
- Parser Findings: Displays anomalies such as duplicate or missing numbers and overlaps.
- Save Options: Lets you add optional notes and save the curated verses.
- Undo/Redo: Limited stack (default 5 history entries) for undo/redo operations; `Ctrl+Z` undoes, `Ctrl+Y` redoes.
- History view: Displays recent undoable actions with short descriptions.

## Per-verse actions (right-click a row)

- Confirm — Mark a verse as `confirmed`. This sets the `status` field of the verse and can be helpful to comment lines that are correct.
- Edit Text — Edit a verse's text manually. After editing text, you may need to adjust the start or end offsets.
- Merge with Next — Join the selected verse and the following verse into a single verse. The end offset of the selected verse will move to the next verse's end.
- Split at Offset — Split the selected verse into two at a specified offset relative to the verse's beginning. This inserts a new verse and optionally renumbers the following verses.
- Renumber — Manually set the verse number for a verse. Useful for fixing wrong numeric markers.
- Ignore Verse — Mark the verse as `ignored`. Ignored verses will be excluded from typical Holy Book counts and saved view unless explicitly requested.
- Create Rule From This — Create a parser rule with optional `pattern_before` and `pattern_after` regex patterns. Supported rule actions include `suppress`, `promote`, `renumber`, and `note`.
- Jump to Document — Focuses the main Text Analysis window and selects the raw range corresponding to the verse.
- Set Start/End from Editor Selection — Use a selection in the main editor to set the start or end offsets for the selected verse.

## Saving & Persistence

- Save As Curated will write the current set of verses to the `document_verses` table and add an audit log entry. These curated verses will override the parser output in subsequent loads for the given document.
- Creating a rule persists it to `verse_rules`; rules can be scoped to this document, or more broadly to a collection or global scope.
- The teacher dialog refreshes the current view after saving.

## Undo/Redo

- The window supports an Undo/Redo stack with a maximum of 5 saved states. Every mutation (Confirm/Edit/Merge/Split/Renumber/Ignore/Set start/Set end) internally pushes the current state onto the Undo stack with a short action description.
- Use `Ctrl+Z` to undo, and `Ctrl+Y` or `Ctrl+Shift+Z` to redo. You can also use the buttons in the UI.

## Rules & Heuristics

- Rules are simple heuristics. A rule consists of:
  - `scope_type` ('document', 'collection', or 'global')
  - `pattern_before` — a regex that must appear in the `n` characters prior to a marker to match
  - `pattern_after` — a regex that must appear after the marker
  - `action` — one of: `suppress` (ignore marker), `promote` (increase confidence), `renumber`, and `note`.
- Typical rule use-cases:
  - Suppress inline numbers that occur as part of text, e.g., a year `182` that appears mid-line.
  - Promote markers that are known to be correct in a document or book (special headers or non-standard punctuation).
  - Apply bulk renumbering for documents where markers are offset by a constant.

## Examples

- Fix an inline number incorrectly detected as a verse:
  1. Right-click the offending verse; choose `Ignore Verse` or `Create Rule From This` with a `pattern_before`/`pattern_after` that matches context.
  2. Save changes with `Save As Curated`.

- Split a verse around a phrase:
  1. Select the verse, right-click → `Split at Offset`. Provide the splitter offset (characters from the start) and confirm.
  2. Verify the split, apply renumber if necessary, then save.

## Pro Tips

- Toggle `Allow inline markers` to test permissive parsing for texts with inline numbering such as modern transcriptions.
- Use `Jump to Document` to visually confirm offsets — the main editor will highlight text ranges so you can precisely set starts and ends.
- Use `Create Rule From This` when you spot a consistent mis-detection; rules make parser runs more reliable across similar documents.
- Keep changes in-memory until you save — experiment freely with Undo/Redo.

## Troubleshooting

- No verses displayed: Check that the document is selected in the main `Text Analysis` window and that it is tagged as a `Holy Book` category or collection.
- Off by a few chars: Choose `Jump to Document`, select text manually, `Set Start/End from Editor Selection` then save.
- Rule not applied: Ensure the `scope_type` (document/collection/global) includes the current document and that regex patterns are correct.

## Contact & Feedback

If you have ideas for more editor functions, rule inference examples, or parser heuristics, please log an issue in the repository and include an example document or a snippet with context so rules can be iterated upon.

Thank you for using the Holy Book Teacher — this tool is intended to help make verse parsing reliable and repeatable across documents and collections.
