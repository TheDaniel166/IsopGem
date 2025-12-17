# Document Manager Rich Text Editor Enhancements

<cite>
**Referenced Files in This Document**
- [rich_text_editor.md](file://Docs/architecture/rich_text_editor.md)
- [rich_text_editor.py](file://src/pillars/document_manager/ui/rich_text_editor.py)
- [list_features.py](file://src/pillars/document_manager/ui/list_features.py)
- [table_features.py](file://src/pillars/document_manager/ui/table_features.py)
- [image_features.py](file://src/pillars/document_manager/ui/image_features.py)
- [search_features.py](file://src/pillars/document_manager/ui/search_features.py)
- [ribbon_widget.py](file://src/pillars/document_manager/ui/ribbon_widget.py)
- [document_editor_window.py](file://src/pillars/document_manager/ui/document_editor_window.py)
- [parsers.py](file://src/pillars/document_manager/utils/parsers.py)
- [image_utils.py](file://src/pillars/document_manager/utils/image_utils.py)
- [document.py](file://src/pillars/document_manager/models/document.py)
- [document_service.py](file://src/pillars/document_manager/services/document_service.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)
10. [Appendices](#appendices)

## Introduction
This document describes the enhancements and capabilities of the Document Manager’s Rich Text Editor (RTE) subsystem. The RTE is a reusable PyQt-based widget that augments QTextEdit with a modern “Ribbon” interface and a suite of productivity features including lists, tables, images, hyperlinks, horizontal rules, special characters, page setup, printing, and PDF export. It also integrates tightly with the Document Manager’s persistence layer to support wiki-style linking, search, and image handling.

The goal is to provide both a high-level overview and code-level insights to help developers extend or integrate the editor effectively.

## Project Structure
The RTE resides in the Document Manager pillar and is composed of:
- A central editor widget with a Ribbon UI
- Feature modules for lists, tables, images, and search
- Ribbon infrastructure for organizing actions
- Dialogs for hyperlinks, horizontal rules, page setup, and PDF export
- Integration with the document service and persistence models

```mermaid
graph TB
subgraph "UI Layer"
RTE["RichTextEditor<br/>QTextEdit + Ribbon"]
Ribbon["RibbonWidget<br/>Tabs/Groups"]
ListF["ListFeature"]
TableF["TableFeature"]
ImageF["ImageFeature"]
SearchF["SearchReplaceFeature"]
end
subgraph "Windows"
EditorWin["DocumentEditorWindow"]
end
subgraph "Persistence"
DocModel["Document Model"]
DocSvc["DocumentService"]
Parser["DocumentParser"]
ImgUtils["Image Utils"]
end
RTE --> Ribbon
RTE --> ListF
RTE --> TableF
RTE --> ImageF
RTE --> SearchF
EditorWin --> RTE
DocSvc --> DocModel
DocSvc --> Parser
DocSvc --> ImgUtils
```

**Diagram sources**
- [rich_text_editor.py](file://src/pillars/document_manager/ui/rich_text_editor.py#L520-L1510)
- [list_features.py](file://src/pillars/document_manager/ui/list_features.py#L1-L108)
- [table_features.py](file://src/pillars/document_manager/ui/table_features.py#L1-L798)
- [image_features.py](file://src/pillars/document_manager/ui/image_features.py#L1-L983)
- [search_features.py](file://src/pillars/document_manager/ui/search_features.py#L1-L365)
- [document_editor_window.py](file://src/pillars/document_manager/ui/document_editor_window.py#L1-L339)
- [parsers.py](file://src/pillars/document_manager/utils/parsers.py#L1-L275)
- [image_utils.py](file://src/pillars/document_manager/utils/image_utils.py#L1-L143)
- [document.py](file://src/pillars/document_manager/models/document.py#L1-L71)
- [document_service.py](file://src/pillars/document_manager/services/document_service.py#L1-L330)

**Section sources**
- [rich_text_editor.py](file://src/pillars/document_manager/ui/rich_text_editor.py#L520-L1510)
- [document_editor_window.py](file://src/pillars/document_manager/ui/document_editor_window.py#L1-L339)

## Core Components
- RichTextEditor: Central widget that composes the Ribbon and delegates feature logic to specialized modules. It exposes signals for text changes and wiki-link triggers, and provides public APIs to get/set HTML/text.
- Feature Modules:
  - ListFeature: Bullet/number lists, indentation/outdenting, and list style switching.
  - TableFeature: Table creation, row/column operations, cell properties, borders, and table-wide properties.
  - ImageFeature: Image insertion with a pre-edit dialog (crop, rotate, resize, filters), and post-insertion properties.
  - SearchReplaceFeature: Non-modal find/replace dialog with find-all and replace-all.
- RibbonWidget: A themed tabbed toolbar organizing actions into logical groups.
- Dialogs: Hyperlink, Horizontal Rule, Page Setup, Export PDF, Special Characters, and Print Preview dialogs.
- Persistence Integration: DocumentEditorWindow wires the editor to DocumentService for save/open/export, and uses DocumentParser/ImageUtils for import/export.

**Section sources**
- [rich_text_editor.py](file://src/pillars/document_manager/ui/rich_text_editor.py#L520-L1510)
- [list_features.py](file://src/pillars/document_manager/ui/list_features.py#L1-L108)
- [table_features.py](file://src/pillars/document_manager/ui/table_features.py#L1-L798)
- [image_features.py](file://src/pillars/document_manager/ui/image_features.py#L1-L983)
- [search_features.py](file://src/pillars/document_manager/ui/search_features.py#L1-L365)
- [ribbon_widget.py](file://src/pillars/document_manager/ui/ribbon_widget.py#L1-L237)
- [document_editor_window.py](file://src/pillars/document_manager/ui/document_editor_window.py#L1-L339)

## Architecture Overview
The RTE follows a composition-over-inheritance design. The main widget initializes the Ribbon and feature modules, then delegates functionality to them. The editor emits signals consumed by the parent window (DocumentEditorWindow), which orchestrates persistence and UI actions.

```mermaid
classDiagram
class RichTextEditor {
+signals : text_changed, wiki_link_requested
+get_html() str
+set_html(html : str) void
+get_text() str
+set_text(text : str) void
+clear() void
+find_text(text : str) bool
-_init_ribbon()
-_show_context_menu(pos)
-_update_format_widgets(fmt)
}
class RibbonWidget {
+add_ribbon_tab(title : str) RibbonTab
}
class RibbonTab {
+add_group(title : str) RibbonGroup
}
class RibbonGroup {
+add_action(action, style)
+add_widget(widget)
+add_separator()
}
class ListFeature {
+toggle_list(style)
+indent()
+outdent()
}
class TableFeature {
+create_toolbar_button() QToolButton
+extend_context_menu(menu)
-_insert_table()
-_edit_cell_properties()
}
class ImageFeature {
+create_toolbar_action() QAction
+extend_context_menu(menu)
-_insert_image()
}
class SearchReplaceFeature {
+show_search_dialog()
+find_next(text, case, whole)
+find_all(text, case, whole)
+replace_current(text, new, case, whole)
+replace_all(text, new, case, whole)
}
RichTextEditor --> RibbonWidget : "composition"
RichTextEditor --> ListFeature : "delegation"
RichTextEditor --> TableFeature : "delegation"
RichTextEditor --> ImageFeature : "delegation"
RichTextEditor --> SearchReplaceFeature : "delegation"
```

**Diagram sources**
- [rich_text_editor.py](file://src/pillars/document_manager/ui/rich_text_editor.py#L520-L1510)
- [list_features.py](file://src/pillars/document_manager/ui/list_features.py#L1-L108)
- [table_features.py](file://src/pillars/document_manager/ui/table_features.py#L1-L798)
- [image_features.py](file://src/pillars/document_manager/ui/image_features.py#L1-L983)
- [search_features.py](file://src/pillars/document_manager/ui/search_features.py#L1-L365)
- [ribbon_widget.py](file://src/pillars/document_manager/ui/ribbon_widget.py#L1-L237)

**Section sources**
- [rich_text_editor.md](file://Docs/architecture/rich_text_editor.md#L1-L179)

## Detailed Component Analysis

### RichTextEditor: Ribbon, Styling, and Actions
- Ribbon initialization organizes actions into Home, Insert, and Page Layout tabs with groups for font, paragraph, tables, illustrations, symbols, links, elements, page setup, export, and print.
- Semantic styles (Title, Heading 1–3, Code) are applied by wrapping selected text in appropriate HTML tags with inline styles to ensure consistent rendering.
- Formatting synchronization: On cursor format changes, the Ribbon updates buttons for bold, italic, underline, strikethrough, subscript/superscript, and alignment.
- Page layout actions: Page Setup dialog stores page size/orientation/margins; Export PDF and Print/Preview dialogs use these settings.
- Wiki-link trigger: Detects when the user types two opening brackets and emits a signal to open a link selector dialog.

```mermaid
sequenceDiagram
participant User as "User"
participant Ribbon as "Ribbon (ComboBox)"
participant Editor as "RichTextEditor"
participant Cursor as "QTextCursor"
User->>Ribbon : Select "Heading 1"
Ribbon->>Editor : _apply_style("Heading 1")
Editor->>Cursor : hasSelection?
alt No Selection
Editor->>Cursor : Select Block Under Cursor
end
Editor->>Cursor : insertHtml("<h1>...</h1>")
Editor->>Ribbon : Update Font/Size Combos (Sync)
```

**Diagram sources**
- [rich_text_editor.py](file://src/pillars/document_manager/ui/rich_text_editor.py#L1156-L1204)

**Section sources**
- [rich_text_editor.py](file://src/pillars/document_manager/ui/rich_text_editor.py#L520-L1510)
- [rich_text_editor.md](file://Docs/architecture/rich_text_editor.md#L87-L154)

### ListFeature: Bulleted and Numbered Lists
- Toggles list style for the current selection or block.
- Supports nested indentation by creating sub-lists or increasing block indent.
- Ensures consistent behavior for exiting list mode and resetting paragraph indent.

```mermaid
flowchart TD
Start(["Toggle List"]) --> HasSel{"Has Selection?"}
HasSel --> |No| SelectBlock["Select Block Under Cursor"]
HasSel --> |Yes| Continue["Continue"]
Continue --> InList{"Inside a List?"}
InList --> |Yes| SameStyle{"Same Style?"}
SameStyle --> |Yes| RemoveList["Remove List Association"]
SameStyle --> |No| ChangeStyle["Change List Style"]
InList --> |No| CreateList["Create New List with Style"]
RemoveList --> End(["Done"])
ChangeStyle --> End
CreateList --> End
```

**Diagram sources**
- [list_features.py](file://src/pillars/document_manager/ui/list_features.py#L1-L108)

**Section sources**
- [list_features.py](file://src/pillars/document_manager/ui/list_features.py#L1-L108)

### TableFeature: Tables, Rows, Columns, and Cell Properties
- Provides a toolbar button that opens a contextual menu with insert-row/insert-column, delete-row/delete-column, delete-table, merge/split cells, distribute columns, and properties.
- Offers dialogs for table properties (width, border, cell spacing/padding), cell properties (padding, vertical alignment), and cell border styles (per-side).
- Supports column width constraints and percentage/fixed sizing.

```mermaid
sequenceDiagram
participant User as "User"
participant TableF as "TableFeature"
participant Menu as "Context Menu"
participant Dialog as "Dialogs"
User->>TableF : Click Table Toolbar Button
TableF->>Menu : Show Menu (Insert/Delete/Merge/Split/Props)
User->>Menu : Choose "Insert Row Above"
Menu->>TableF : _insert_row_above()
TableF->>TableF : table.insertRows(...)
Note over TableF : Updates menu state based on cursor position
```

**Diagram sources**
- [table_features.py](file://src/pillars/document_manager/ui/table_features.py#L441-L798)

**Section sources**
- [table_features.py](file://src/pillars/document_manager/ui/table_features.py#L1-L798)

### ImageFeature: Pre-Edit Workflow and Insertion
- Provides an “Edit & Insert Image” action that opens a modal dialog with:
  - Image loader worker to offload decoding to a background thread
  - Crop preview with rubber-band selection and live crop confirmation
  - Adjustments: brightness, contrast, saturation, sharpness, and filters
  - Layout options: display size presets, alignment, and margins
- On accept, inserts the processed image into the document with a UUID resource and applies properties.

```mermaid
sequenceDiagram
participant User as "User"
participant ImageF as "ImageFeature"
participant Dialog as "ImageEditorDialog"
participant Pillow as "PIL"
participant Text as "QTextDocument"
User->>ImageF : Click "Edit & Insert Image"
ImageF->>Dialog : open()
User->>Dialog : Select File
Dialog->>Pillow : Load Image (threaded)
loop User Edits
User->>Dialog : Rotate / Crop / Resize / Filters
Dialog->>Pillow : Process Image
Dialog->>User : Update Preview
end
User->>Dialog : Click OK
Dialog->>ImageF : return processed image
ImageF->>Text : addResource(ImageResource, uuid)
ImageF->>Text : insertImage(size, uuid)
```

**Diagram sources**
- [image_features.py](file://src/pillars/document_manager/ui/image_features.py#L1-L983)

**Section sources**
- [image_features.py](file://src/pillars/document_manager/ui/image_features.py#L1-L983)

### SearchReplaceFeature: Find, Replace, and Navigation
- Non-modal dialog stays on top and supports find-next, find-all, replace-current, and replace-all.
- Highlights matches and lets users click results to navigate to positions.
- Uses QTextDocument find with case-sensitive and whole-word options and wraps around the document.

```mermaid
sequenceDiagram
participant User as "User"
participant SearchF as "SearchReplaceFeature"
participant Dialog as "SearchDialog"
participant Editor as "QTextEdit"
User->>SearchF : show_search_dialog()
SearchF->>Dialog : create/show dialog
User->>Dialog : Enter text + options
Dialog->>SearchF : find_next_requested
SearchF->>Editor : find(text, flags)
alt Not Found
SearchF->>Editor : move to start and retry
end
Dialog->>SearchF : navigate_requested(pos)
SearchF->>Editor : setTextCursor(pos)
```

**Diagram sources**
- [search_features.py](file://src/pillars/document_manager/ui/search_features.py#L1-L365)

**Section sources**
- [search_features.py](file://src/pillars/document_manager/ui/search_features.py#L1-L365)

### RibbonWidget: Themed Tabs and Groups
- Provides a modern, shadowed tabbed interface with styled buttons and comboboxes.
- RibbonTab and RibbonGroup encapsulate layout and labeling for action organization.

**Section sources**
- [ribbon_widget.py](file://src/pillars/document_manager/ui/ribbon_widget.py#L1-L237)

### DocumentEditorWindow: Integration with Persistence and UI
- Hosts the RichTextEditor and wires signals for text changes and wiki-link requests.
- Implements File menu actions: New, Open, Save, Save As, Export PDF.
- Uses DocumentService to persist HTML content and plain text, and to restore images for display.

```mermaid
sequenceDiagram
participant User as "User"
participant Win as "DocumentEditorWindow"
participant Editor as "RichTextEditor"
participant Service as "DocumentService"
User->>Win : Save
Win->>Editor : get_html()/get_text()
Win->>Service : update_document(id, content, raw_content)
Service-->>Win : success
Win-->>User : "Saved"
```

**Diagram sources**
- [document_editor_window.py](file://src/pillars/document_manager/ui/document_editor_window.py#L253-L290)
- [document_service.py](file://src/pillars/document_manager/services/document_service.py#L225-L245)

**Section sources**
- [document_editor_window.py](file://src/pillars/document_manager/ui/document_editor_window.py#L1-L339)
- [document_service.py](file://src/pillars/document_manager/services/document_service.py#L1-L330)

## Dependency Analysis
- Internal dependencies:
  - RichTextEditor depends on feature modules and RibbonWidget.
  - Feature modules depend on Qt GUI types and QText* formats.
  - DocumentEditorWindow depends on RichTextEditor and DocumentService.
- Persistence dependencies:
  - DocumentService uses SQLAlchemy models and repositories.
  - Image handling uses base64 extraction/restoration and database-backed storage.
  - Parsing supports multiple formats (.txt, .html, .docx, .pdf, .rtf) with optional third-party libraries.

```mermaid
graph LR
RTE["RichTextEditor"] --> LF["ListFeature"]
RTE --> TF["TableFeature"]
RTE --> IF["ImageFeature"]
RTE --> SF["SearchReplaceFeature"]
RTE --> RW["RibbonWidget"]
Win["DocumentEditorWindow"] --> RTE
Win --> DS["DocumentService"]
DS --> DM["Document Model"]
DS --> PU["DocumentParser"]
DS --> IU["Image Utils"]
```

**Diagram sources**
- [rich_text_editor.py](file://src/pillars/document_manager/ui/rich_text_editor.py#L520-L1510)
- [document_editor_window.py](file://src/pillars/document_manager/ui/document_editor_window.py#L1-L339)
- [document_service.py](file://src/pillars/document_manager/services/document_service.py#L1-L330)
- [parsers.py](file://src/pillars/document_manager/utils/parsers.py#L1-L275)
- [image_utils.py](file://src/pillars/document_manager/utils/image_utils.py#L1-L143)
- [document.py](file://src/pillars/document_manager/models/document.py#L1-L71)

**Section sources**
- [document_service.py](file://src/pillars/document_manager/services/document_service.py#L1-L330)
- [parsers.py](file://src/pillars/document_manager/utils/parsers.py#L1-L275)
- [image_utils.py](file://src/pillars/document_manager/utils/image_utils.py#L1-L143)
- [document.py](file://src/pillars/document_manager/models/document.py#L1-L71)

## Performance Considerations
- Large paste protection: The editor warns before inserting very large text to prevent UI freezes.
- Replace-all optimization: Temporarily disables updates during bulk replacements to reduce repaint overhead.
- Image processing offloading: Decoding and editing images runs in a background thread to keep the UI responsive.
- Printing/PDF: Uses Qt’s print pipeline; page layout is configurable and cached for subsequent operations.
- Search-all: Iterates the document to collect matches; consider limiting result lists for very large documents.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
- Paste freezes: The SafeTextEdit wrapper prompts before inserting extremely large content. Reduce clipboard size or paste in smaller chunks.
- Table formatting anomalies: TableFeature relies on Qt’s QTextTableFormat. If borders or spacing appear inconsistent, use the Table Properties dialog to normalize widths and styles.
- Image insertion issues: Ensure Pillow is installed for the “Edit & Insert” workflow. If crops fail, verify the selection rectangle is valid and the image is decodable.
- PDF export margins: Use Page Setup to define margins and orientation; Export PDF applies these settings automatically.
- Wiki links: When typing [[, the editor emits a signal; ensure the link selector dialog is reachable and that DocumentService is available to resolve titles.

**Section sources**
- [rich_text_editor.py](file://src/pillars/document_manager/ui/rich_text_editor.py#L24-L53)
- [table_features.py](file://src/pillars/document_manager/ui/table_features.py#L1-L798)
- [image_features.py](file://src/pillars/document_manager/ui/image_features.py#L1-L983)
- [document_editor_window.py](file://src/pillars/document_manager/ui/document_editor_window.py#L1-L339)

## Conclusion
The Document Manager’s Rich Text Editor is a robust, extensible component that brings professional-grade editing to the application. Its modular architecture, comprehensive Ribbon interface, and deep integration with persistence and search enable authors to produce rich documents with tables, images, and structured content. The enhancements outlined here—especially the image pre-edit workflow, table management, and print/export capabilities—make it suitable for advanced documentation scenarios.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### API Surface Summary
- RichTextEditor
  - Signals: text_changed, wiki_link_requested
  - Methods: get_html, set_html, get_text, set_text, clear, find_text
- ListFeature: toggle_list, indent, outdent
- TableFeature: create_toolbar_button, extend_context_menu
- ImageFeature: create_toolbar_action, extend_context_menu
- SearchReplaceFeature: show_search_dialog, find_next, find_all, replace_current, replace_all
- RibbonWidget: add_ribbon_tab, RibbonTab.add_group, RibbonGroup.add_action/add_widget/add_separator

**Section sources**
- [rich_text_editor.py](file://src/pillars/document_manager/ui/rich_text_editor.py#L520-L1510)
- [list_features.py](file://src/pillars/document_manager/ui/list_features.py#L1-L108)
- [table_features.py](file://src/pillars/document_manager/ui/table_features.py#L1-L798)
- [image_features.py](file://src/pillars/document_manager/ui/image_features.py#L1-L983)
- [search_features.py](file://src/pillars/document_manager/ui/search_features.py#L1-L365)
- [ribbon_widget.py](file://src/pillars/document_manager/ui/ribbon_widget.py#L1-L237)