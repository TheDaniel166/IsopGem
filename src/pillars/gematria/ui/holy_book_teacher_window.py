"""Dialog for teaching the Holy Book parser and saving curated verses."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, cast

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QMainWindow,
    QDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtWidgets import QHeaderView, QProgressDialog
from PyQt6.QtWidgets import QMenu, QInputDialog
from PyQt6.QtGui import QAction, QKeySequence

# QShortcut moved between Qt modules across versions (try both)
try:
    from PyQt6.QtWidgets import QShortcut  # type: ignore
except Exception:
    from PyQt6.QtGui import QShortcut  # type: ignore

from shared.services.document_manager.verse_teacher_service import verse_teacher_service_context
from pathlib import Path
import os
import logging
logger = logging.getLogger(__name__)


class HolyBookTeacherWindow(QMainWindow):
    """Lightweight workspace for reviewing and saving verse runs."""

    verses_saved = pyqtSignal()

    def __init__(
        self,
        document_id: int,
        document_title: str,
        allow_inline: bool = True,
        parent=None,
    ) -> None:
        """
          init   logic.
        
        Args:
            document_id: Description of document_id.
            document_title: Description of document_title.
            allow_inline: Description of allow_inline.
            parent: Description of parent.
        
        Returns:
            Result of __init__ operation.
        """
        super().__init__(parent)
        self.document_id = document_id
        self.document_title = document_title or "Document"
        self.allow_inline = allow_inline
        self._current_payload: Optional[Dict[str, Any]] = None
        # Undo/redo stacks (store copies of the verses list plus description)
        self._undo_stack: List[Tuple[List[Dict[str, Any]], str]] = []
        self._redo_stack: List[Tuple[List[Dict[str, Any]], str]] = []
        self._undo_limit = 5

        self.setWindowTitle("Holy Book Teacher")
        self.setMinimumSize(960, 640)

        self._build_ui()
        self._load_payload()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        title = QLabel(f"📖 Holy Book Teacher — {self.document_title}")
        title.setStyleSheet("font-size: 18pt; font-weight: 600; color: #1e293b;")
        # Create a horizontal title row so a small help button can sit on the right
        title_row = QHBoxLayout()
        title_row.addWidget(title)
        title_row.addStretch()
        help_btn = QPushButton("?")
        help_btn.setFixedSize(28, 28)
        help_btn.setToolTip("Help: Holy Book Teacher")
        help_btn.clicked.connect(self._open_help_dialog)
        title_row.addWidget(help_btn)
        layout.addLayout(title_row)

        control_row = QHBoxLayout()
        self.inline_checkbox = QCheckBox("Allow inline markers")
        self.inline_checkbox.setChecked(self.allow_inline)
        self.inline_checkbox.stateChanged.connect(self._on_inline_toggled)
        control_row.addWidget(self.inline_checkbox)
        control_row.addStretch()
        layout.addLayout(control_row)

        self.source_label = QLabel("Loading verse data…")
        self.source_label.setStyleSheet("color: #475569; font-size: 10pt;")
        layout.addWidget(self.source_label)

        table_group = QGroupBox("Verse Preview")
        table_layout = QVBoxLayout(table_group)
        self.verses_table = QTableWidget(0, 7)
        self.verses_table.setHorizontalHeaderLabels([
            "#",
            "Status",
            "Start",
            "End",
            "Source",
            "Conf",
            "Text",
        ])
        header = self.verses_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        self.verses_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.verses_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.verses_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.verses_table.customContextMenuRequested.connect(self._on_table_context_menu)
        self.verses_table.itemSelectionChanged.connect(self._on_table_selection_changed)
        # Allow double-click to open a verse editor for that row
        self.verses_table.cellDoubleClicked.connect(self._on_table_double_clicked)
        table_layout.addWidget(self.verses_table)
        layout.addWidget(table_group)

        anomalies_group = QGroupBox("Parser Findings")
        anomalies_layout = QVBoxLayout(anomalies_group)
        self.anomaly_view = QTextEdit()
        self.anomaly_view.setReadOnly(True)
        self.anomaly_view.setStyleSheet("font-family: monospace; font-size: 10pt;")
        anomalies_layout.addWidget(self.anomaly_view)
        layout.addWidget(anomalies_group)

        form_group = QGroupBox("Save Options")
        form_layout = QGridLayout(form_group)
        form_layout.addWidget(QLabel("Notes:"), 0, 0)
        self.notes_input = QLineEdit()
        form_layout.addWidget(self.notes_input, 0, 1)
        layout.addWidget(form_group)

        button_row = QHBoxLayout()
        self.reload_curated_btn = QPushButton("Reload Curated")
        self.reload_curated_btn.clicked.connect(self._load_payload)
        button_row.addWidget(self.reload_curated_btn)
        self.run_parser_btn = QPushButton("Run Fresh Parser")
        self.run_parser_btn.clicked.connect(lambda: self._load_payload(from_parser=True))
        button_row.addWidget(self.run_parser_btn)
        button_row.addStretch()
        self.save_btn = QPushButton("💾 Save As Curated")
        self.save_btn.clicked.connect(self._save_current_payload)
        # Undo / Redo
        self.undo_btn = QPushButton("↺ Undo")
        self.undo_btn.clicked.connect(self._undo)
        self.undo_btn.setEnabled(False)
        button_row.addWidget(self.undo_btn)
        self.redo_btn = QPushButton("↻ Redo")
        self.redo_btn.clicked.connect(self._redo)
        self.redo_btn.setEnabled(False)
        button_row.addWidget(self.redo_btn)
        # Add a lightweight history view and keyboard shortcuts
        from PyQt6.QtWidgets import QListWidget
        self.history_view = QListWidget()
        # Keyboard shortcuts for Undo/Redo
        undo_sc = QShortcut(QKeySequence("Ctrl+Z"), self)
        undo_sc.activated.connect(self._undo)
        redo_sc = QShortcut(QKeySequence("Ctrl+Y"), self)
        redo_sc.activated.connect(self._redo)
        redo_sc2 = QShortcut(QKeySequence("Ctrl+Shift+Z"), self)
        redo_sc2.activated.connect(self._redo)
        self.history_view.setMaximumHeight(120)
        layout.addWidget(self.history_view)
        button_row.addWidget(self.save_btn)
        
        # Index to Concordance button
        self.index_btn = QPushButton("📚 Index to Concordance")
        self.index_btn.setToolTip("Index all words from curated verses into the TQ Lexicon concordance")
        self.index_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #047857);
                color: white;
                border: 1px solid #065f46;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #047857, stop:1 #059669);
            }
        """)
        self.index_btn.clicked.connect(self._index_to_concordance)
        button_row.addWidget(self.index_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_row.addWidget(close_btn)
        layout.addLayout(button_row)

    def _on_inline_toggled(self):
        self.allow_inline = self.inline_checkbox.isChecked()
        self._load_payload(from_parser=True)

    def _load_payload(self, from_parser: bool = False):
        self._set_loading(True)
        try:
            with verse_teacher_service_context() as service:
                if from_parser:
                    payload = service.generate_parser_run(
                        self.document_id,
                        allow_inline=self.allow_inline,
                        apply_rules=True,
                    )
                else:
                    payload = service.get_or_parse_verses(
                        self.document_id,
                        allow_inline=self.allow_inline,
                        apply_rules=True,
                    )
        except Exception as exc:
            self._set_loading(False)
            QMessageBox.critical(self, "Error", f"Failed to load verses:\n{exc}")
            return
        self._current_payload = payload
        self._render_payload(payload)
        # Reset undo/redo stacks when a new payload is loaded
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._update_undo_buttons()
        self._update_history_display()
        self._update_undo_buttons()
        self._set_loading(False)

    def _set_loading(self, loading: bool):
        for btn in (self.reload_curated_btn, self.run_parser_btn, self.save_btn):
            btn.setEnabled(not loading)

    def _render_payload(self, payload: Optional[Dict[str, Any]]):
        if payload is None:
            payload = {"verses": [], "source": "parser", "anomalies": {}, "rules_applied": []}
        verses = payload.get("verses", []) or []
        source = payload.get("source", "parser")
        info_parts = [f"Source: {source}", f"Verses: {len(verses)}"]
        rules_hit = payload.get("rules_applied") or []
        if rules_hit:
            info_parts.append(f"Rules applied: {len(rules_hit)}")
        self.source_label.setText(" · ".join(info_parts))
        self._populate_table(verses)
        self._render_anomalies(payload.get("anomalies"))

    def _populate_table(self, verses: List[Dict[str, Any]]):
        # Clear existing contents to avoid reusing previous QTableWidgetItem instances
        self.verses_table.clearContents()
        self.verses_table.setRowCount(len(verses))
        for row, verse in enumerate(verses):
            items = [
                str(verse.get("number", "")),
                verse.get("status", ""),
                str(verse.get("start", "")),
                str(verse.get("end", "")),
                verse.get("source_type", ""),
                f"{verse.get('confidence', 0):.2f}",
                (verse.get("text", "") or "")[:160],
            ]
            for col, text in enumerate(items):
                cell = QTableWidgetItem(text)
                cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                # Attach verse object to the first column so the row carries its data
                if col == 0:
                    # Use Qt.UserRole to avoid interfering with display text
                    cell.setData(Qt.ItemDataRole.UserRole, verse)
                self.verses_table.setItem(row, col, cell)
            # Store full verse object on row for easy retrieval (already attached to column 0)
            self.verses_table.setRowHeight(row, 28)

    def _render_anomalies(self, anomalies: Optional[Dict[str, Any]]):
        if not anomalies:
            self.anomaly_view.setPlainText("No anomalies detected.")
            return
        parts: List[str] = []
        duplicates = anomalies.get("duplicates") or []
        missing = anomalies.get("missing_numbers") or []
        overlaps = anomalies.get("overlaps") or []
        if duplicates:
            parts.append(f"Duplicate numbers: {duplicates}")
        if missing:
            parts.append(f"Missing numbers: {missing}")
        if overlaps:
            formatted = [f"{item.get('previous')}→{item.get('current')}" for item in overlaps]  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
            parts.append(f"Overlaps: {formatted}")
        if not parts:
            parts.append("No anomalies detected.")
        self.anomaly_view.setPlainText("\n".join(parts))

    def _save_current_payload(self):
        if not self._current_payload or not self._current_payload.get("verses"):
            QMessageBox.information(self, "Nothing to Save", "No verse data is available to store.")
            return
        notes = self.notes_input.text().strip() or None
        try:
            with verse_teacher_service_context() as service:
                service.save_curated_verses(
                    document_id=self.document_id,
                    verses=self._current_payload.get("verses", []),
                    actor="teacher-ui",
                    notes=notes,
                )
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Failed to save curated verses:\n{exc}")
            return
        QMessageBox.information(self, "Saved", "Curated verses stored successfully.")
        self.notes_input.clear()
        self.verses_saved.emit()
        self._load_payload(from_parser=False)

    # --------------------
    # Table context actions
    # --------------------
    def _on_table_context_menu(self, pos):
        item = self.verses_table.itemAt(pos)
        if not item:
            return
        row = item.row()
        menu = QMenu(self)
        confirm_action = QAction("Confirm", self)
        confirm_action.triggered.connect(lambda: self._confirm_verse(row))
        menu.addAction(confirm_action)
        edit_action = QAction("Edit Text", self)
        edit_action.triggered.connect(lambda: self._edit_verse(row))
        menu.addAction(edit_action)
        merge_action = QAction("Merge with Next", self)
        merge_action.triggered.connect(lambda: self._merge_next(row))
        menu.addAction(merge_action)
        split_action = QAction("Split at Offset", self)
        split_action.triggered.connect(lambda: self._split_verse(row))
        menu.addAction(split_action)
        renumber_action = QAction("Renumber", self)
        renumber_action.triggered.connect(lambda: self._renumber_verse(row))
        menu.addAction(renumber_action)
        ignore_action = QAction("Ignore Verse", self)
        ignore_action.triggered.connect(lambda: self._ignore_verse(row))
        menu.addAction(ignore_action)
        rule_action = QAction("Create Rule From This", self)
        rule_action.triggered.connect(lambda: self._create_rule_from_row(row))
        menu.addAction(rule_action)
        jump_action = QAction("Jump to Document", self)
        jump_action.triggered.connect(lambda: self._jump_to_document(row))
        menu.addAction(jump_action)
        set_start_action = QAction("Set Start from Editor Selection", self)
        set_start_action.triggered.connect(lambda: self._set_start_from_selection(row))
        menu.addAction(set_start_action)
        set_end_action = QAction("Set End from Editor Selection", self)
        set_end_action.triggered.connect(lambda: self._set_end_from_selection(row))
        menu.addAction(set_end_action)
        vp = self.verses_table.viewport()
        if vp is not None:
            menu.exec(vp.mapToGlobal(pos))

    def _on_table_double_clicked(self, row: int, col: int):
        """Open modal VerseEditorDialog for the clicked row."""
        from PyQt6.QtWidgets import QDialog

        verse = self._get_verse(row)
        if not verse:
            return
        dialog = VerseEditorDialog(verse=verse, row=row, parent=self, teacher=self)
        # After dialog is accepted/closed, refresh view to ensure up-to-date
        dialog.exec()
        dialog.exec()

    def _get_verse(self, row: int) -> Optional[Dict[str, Any]]:
        try:
            verses = (self._current_payload or {}).get('verses', [])
            if not isinstance(verses, list):
                return None
            return verses[row]
        except Exception:
            return None

    def _set_verse_text(self, row: int, new_text: str, commit: bool = False):
        """Set the verse text for a row and push undo state.

        Args:
            row: Row index
            new_text: New verse text
            commit: Whether to save curated verses (call _save_current_payload) - default False
        """
        verse = self._get_verse(row)
        if not verse:
            return
        # Push undo state
        self._push_undo_state(description=f"Edit verse {verse.get('number')}")
        verse['text'] = new_text
        self._save_verses_and_refresh(commit=commit)

    def _save_verses_and_refresh(self, commit: bool = False):
        # Re-render and optionally save to DB
        self._render_payload(self._current_payload)
        if commit:
            self._save_current_payload()
        # Clear redo stack when new change persisted (prevents redoing old states)
        self._redo_stack.clear()
        self._update_undo_buttons()
        self._update_history_display()

    def _confirm_verse(self, row: int):
        verse = self._get_verse(row)
        if not verse:
            return
        self._push_undo_state(description=f"Confirm verse {verse.get('number')}")
        verse['status'] = 'confirmed'
        self._save_verses_and_refresh(commit=False)

    def _edit_verse(self, row: int):
        verse = self._get_verse(row)
        if not verse:
            return
        new_text, ok = QInputDialog.getMultiLineText(self, f"Edit Verse {verse.get('number')}", "Text:", verse.get('text', ''))
        if not ok:
            return
        self._push_undo_state(description=f"Edit verse {verse.get('number')}")
        verse['text'] = new_text
        # Optionally, keep start/end offsets unchanged; user can adjust them with renumber/split
        self._save_verses_and_refresh(commit=False)

    def _merge_next(self, row: int):
        verses = (self._current_payload or {}).get('verses', [])
        if row < 0 or row >= len(verses) - 1:
            return
        cur = verses[row]
        nxt = verses[row + 1]
        self._push_undo_state(description=f"Merge verse {cur.get('number')} + {nxt.get('number')}")
        cur['text'] = (cur.get('text', '') or '') + ' ' + (nxt.get('text', '') or '')
        cur['end'] = nxt.get('end')
        # Remove next verse
        del verses[row + 1]
        # renumber subsequent verses if needed
        self._save_verses_and_refresh(commit=False)

    def _split_verse(self, row: int):
        verse = self._get_verse(row)
        if not verse:
            return
        start = verse.get('start', 0)
        end = verse.get('end', 0)
        # Ask user for split offset (absolute or relative), make it relative for simplicity
        rel, ok = QInputDialog.getInt(self, "Split Verse", "Split position (characters from verse start):", min=1, value=(end - start) // 2)
        if not ok:
            return
        # Validate
        split_at = start + rel
        if split_at <= start or split_at >= end:
            QMessageBox.warning(self, "Invalid split", "Split position must be within the verse range.")
            return
        # Modify current verse and insert new verse after
        verses = (self._current_payload or {}).get('verses', [])
        cur_text = verse.get('text', '')
        # Determine split index within verse text by character count
        local_index = rel
        left_text = cur_text[:local_index].rstrip()
        right_text = cur_text[local_index:].lstrip()
        self._push_undo_state(description=f"Split verse {verse.get('number')} at {rel}")
        verse['text'] = left_text
        old_end = verse['end']
        verse['end'] = split_at
        new_verse = {
            'number': int(verse.get('number') or 0) + 1,
            'text': right_text,
            'start': split_at,
            'end': old_end,
            'marker_start': split_at,
            'marker_end': split_at,
            'status': 'inserted',
            'confidence': 0.9,
            'source_type': 'teacher',
            'rule_id': None,
            'notes': '',
        }
        verses.insert(row + 1, new_verse)
        # Shift numbers for following verses
        for i in range(row + 2, len(verses)):
            verses[i]['number'] = verses[i].get('number', 0) + 1
        self._save_verses_and_refresh(commit=False)

    def _renumber_verse(self, row: int):
        verse = self._get_verse(row)
        if not verse:
            return
        new_num, ok = QInputDialog.getInt(self, "Renumber Verse", "New verse number:", value=verse.get('number', 0))
        if not ok:
            return
        self._push_undo_state(description=f"Renumber verse {verse.get('number')} -> {new_num}")
        verse['number'] = new_num
        self._save_verses_and_refresh(commit=False)

    def _ignore_verse(self, row: int):
        verse = self._get_verse(row)
        if not verse:
            return
        self._push_undo_state(description=f"Ignore verse {verse.get('number')}")
        verse['status'] = 'ignored'
        self._save_verses_and_refresh(commit=False)

    def _jump_to_document(self, row: int):
        verse = self._get_verse(row)
        if not verse:
            return
        parent = self.parent()
        try:
            from pillars.gematria.ui.text_analysis_window import TextAnalysisWindow as _TextAnalysisWindow
        except Exception:
            _TextAnalysisWindow = None
        if _TextAnalysisWindow is not None and isinstance(parent, _TextAnalysisWindow):
            try:
                parent._jump_to_range(int(verse.get('start') or 0), int(verse.get('end') or 0))  # type: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess, reportUnknownMemberType]
            except Exception:
                pass

    def _set_start_from_selection(self, row: int):
        parent = self.parent()
        try:
            from pillars.gematria.ui.text_analysis_window import TextAnalysisWindow as _TextAnalysisWindow
        except Exception:
            _TextAnalysisWindow = None
        if not parent or _TextAnalysisWindow is None or not isinstance(parent, _TextAnalysisWindow):
            QMessageBox.information(self, 'No Editor', 'Main editor not available')
            return
        cursor = parent.text_display.textCursor()  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]
        if cursor.hasSelection():
            start = min(cursor.selectionStart(), cursor.selectionEnd())  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportUnknownVariableType]
            verse = self._get_verse(row)
            if verse:
                self._push_undo_state(description=f"Set start for {verse.get('number')} to {start}")
                verse['start'] = start
                verse['marker_start'] = start
                self._save_verses_and_refresh(commit=False)
        else:
            QMessageBox.information(self, 'No Selection', 'Select a range in the main editor to set start')

    def _set_end_from_selection(self, row: int):
        parent = self.parent()
        try:
            from pillars.gematria.ui.text_analysis_window import TextAnalysisWindow as _TextAnalysisWindow
        except Exception:
            _TextAnalysisWindow = None
        if not parent or _TextAnalysisWindow is None or not isinstance(parent, _TextAnalysisWindow):
            QMessageBox.information(self, 'No Editor', 'Main editor not available')
            return
        cursor = parent.text_display.textCursor()  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]
        if cursor.hasSelection():
            end = max(cursor.selectionStart(), cursor.selectionEnd())  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportUnknownVariableType]
            verse = self._get_verse(row)
            if verse:
                self._push_undo_state(description=f"Set end for {verse.get('number')} to {end}")
                verse['end'] = end
                verse['marker_end'] = end
                self._save_verses_and_refresh(commit=False)
        else:
            QMessageBox.information(self, 'No Selection', 'Select a range in the main editor to set end')

    def _open_help_dialog(self):
        try:
            root = Path(__file__).resolve().parents[4]
            help_path = root / 'docs' / 'features' / 'HOLY_BOOK_TEACHER_HELP.md'
            if not help_path.exists():
                raise FileNotFoundError(str(help_path))
            text = help_path.read_text(encoding='utf-8')
        except Exception:
            text = (
                "Holy Book Teacher Help is not available in the expected docs folder.\n"
                "Please check repository documentation or create the file at `docs/features/HOLY_BOOK_TEACHER_HELP.md`."
            )
        dlg = QDialog(self)
        dlg.setWindowTitle("Holy Book Teacher Help")
        dlg.setMinimumSize(800, 600)
        layout = QVBoxLayout(dlg)
        info = QTextEdit()
        info.setReadOnly(True)
        info.setPlainText(text)
        layout.addWidget(info)
        btn = QPushButton("Close")
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn)
        dlg.exec()

    def _create_rule_from_row(self, row: int):
        verse = self._get_verse(row)
        if not verse:
            return
        # Ask for before/after patterns via input dialogs
        before, ok1 = QInputDialog.getText(self, "Rule: Pattern Before", "Regex that must appear before the marker (optional):")
        if not ok1:
            return
        after, ok2 = QInputDialog.getText(self, "Rule: Pattern After", "Regex that must appear after the marker (optional):")
        if not ok2:
            return
        action, ok3 = QInputDialog.getItem(self, "Rule Action", "Action:", ["suppress", "promote", "renumber", "note"], 0, False)
        if not ok3:
            return
        params = {}
        if action == 'renumber':
            target, ok4 = QInputDialog.getInt(self, "Renumber Target", "Target verse number:", value=verse.get('number', 0))
            if not ok4:
                return
            params['target_number'] = target
        elif action == 'note':
            note_text, ok4 = QInputDialog.getMultiLineText(self, "Note", "Note to attach:", "")
            if not ok4:
                return
            params['note'] = note_text
        # Persist the rule via service
        try:
            with verse_teacher_service_context() as svc:
                svc.record_rule(
                    scope_type='document',
                    scope_value=str(self.document_id),
                    action=action,
                    description=f"Created from verse {verse.get('number')}",
                    pattern_before=before or None,
                    pattern_after=after or None,
                    parameters=params,
                    priority=10,
                    enabled=True,
                )
        except Exception as exc:
            QMessageBox.critical(self, "Rule Error", f"Failed to create rule:\n{exc}")
            return
        QMessageBox.information(self, "Rule Created", "Rule created and stored for this document.")
        # Re-run to show rule effects
        self._load_payload(from_parser=True)
        # Clear redo/undo stacks when a rule is created — it changes parser behavior
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._update_undo_buttons()

    def _on_table_selection_changed(self):
        # Highlight selection in main editor (single selection only)
        model = self.verses_table.selectionModel()
        if not model:
            return
        rows = model.selectedRows()
        if not rows:
            return
        row = rows[0].row()
        verse = self._get_verse(row)
        if not verse:
            return
        parent = self.parent()
        # Avoid circular-laden import at top-level; import only for runtime checks
        try:
            from pillars.gematria.ui.text_analysis_window import TextAnalysisWindow as _TextAnalysisWindow
        except Exception:
            _TextAnalysisWindow = None
        if _TextAnalysisWindow is not None and isinstance(parent, _TextAnalysisWindow):
            try:
                parent._jump_to_range(int(verse.get('start') or 0), int(verse.get('end') or 0))  # type: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess, reportUnknownMemberType]
            except Exception:
                pass

    def _capture_state_copy(self) -> List[Dict[str, Any]]:
        """Return a deep copy of the current verses list for undo/redo stacks."""
        import copy
        verses = self._current_payload.get('verses', []) if self._current_payload else []
        return copy.deepcopy(verses)

    def _push_undo_state(self, description: str = "Edit"):
        """Push current verses to undo stack and enforce limit; clear redo stack on new change."""
        state = self._capture_state_copy()
        if not state:
            return
        self._undo_stack.append((state, description))
        if len(self._undo_stack) > self._undo_limit:
            # drop the oldest state
            self._undo_stack.pop(0)
        # any new change invalidates redo history
        self._redo_stack.clear()
        self._update_undo_buttons()
        self._update_history_display()

    def _undo(self):
        if not self._undo_stack:
            return
        # push current state onto redo
        self._redo_stack.append((self._capture_state_copy(), "Undid"))
        last, _desc = self._undo_stack.pop()
        if self._current_payload is None:
            self._current_payload = {"verses": []}
        self._current_payload['verses'] = last
        self._render_payload(self._current_payload)
        self._update_undo_buttons()
        self._update_history_display()

    def _redo(self):
        if not self._redo_stack:
            return
        # push current onto undo
        self._undo_stack.append((self._capture_state_copy(), "Redo"))
        state, _desc = self._redo_stack.pop()
        if self._current_payload is None:
            self._current_payload = {"verses": []}
        self._current_payload['verses'] = state
        self._render_payload(self._current_payload)
        self._update_undo_buttons()
        self._update_history_display()

    def _update_undo_buttons(self):
        self.undo_btn.setEnabled(bool(self._undo_stack))
        self.redo_btn.setEnabled(bool(self._redo_stack))
        self._update_history_display()

    def _update_history_display(self):
        # Show the last N actions (most recent on top)
        if not hasattr(self, 'history_view'):
            return
        self.history_view.clear()
        # Display undo stack (most recent last -> invert)
        for _s, desc in reversed(self._undo_stack[-self._undo_limit:]):
            self.history_view.addItem(desc)
        # Show a delimiter and redo stack count for clarity
        if self._redo_stack:
            self.history_view.addItem(f"---- Redo available: {len(self._redo_stack)} ----")

    # --- Concordance Indexing ---
    
    def _index_to_concordance(self):
        """Index all words from curated verses to the TQ Lexicon concordance."""
        if not self._current_payload or not self._current_payload.get('verses'):
            QMessageBox.warning(
                self, 
                "No Verses", 
                "No curated verses available. Save verses first before indexing."
            )
            return
        
        # Check if already indexed
        from shared.repositories.lexicon.key_database import KeyDatabase
        db = KeyDatabase()
        already_indexed = db.is_document_indexed(self.document_id)
        
        reindex = False
        if already_indexed:
            reply = QMessageBox.question(
                self,
                "Already Indexed",
                f"'{self.document_title}' is already indexed.\n\n"
                "Do you want to re-index? This will clear existing occurrences for this document.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            reindex = True
        
        # Create progress dialog
        verses = self._current_payload.get('verses', [])
        self.progress_dlg = QProgressDialog(
            f"Indexing {len(verses)} verses...",
            "Cancel",
            0,
            len(verses),
            self
        )
        self.progress_dlg.setWindowTitle("Indexing to Concordance")
        self.progress_dlg.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dlg.setMinimumDuration(0)
        self.progress_dlg.setValue(0)
        
        # Start worker
        self.index_worker = ConcordanceIndexWorker(self.document_id, reindex=reindex)
        self.index_worker.progress.connect(self._on_index_progress)
        self.index_worker.finished.connect(self._on_index_finished)
        self.index_worker.error.connect(self._on_index_error)
        self.index_worker.start()
        
    def _on_index_progress(self, current, total, message):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        if hasattr(self, 'progress_dlg') and self.progress_dlg:
            self.progress_dlg.setMaximum(total)
            self.progress_dlg.setValue(current)
            self.progress_dlg.setLabelText(message)
            
    def _on_index_finished(self, result):
        if hasattr(self, 'progress_dlg') and self.progress_dlg:
            self.progress_dlg.close()
        
        # Show results
        if result.errors:
            error_summary = "\n".join(result.errors[:5])
            if len(result.errors) > 5:
                error_summary += f"\n... and {len(result.errors) - 5} more errors"
        else:
            error_summary = "No errors."
        
        QMessageBox.information(
            self,
            "Indexing Complete",
            f"Concordance indexing complete for '{result.document_title}':\n\n"
            f"• Verses processed: {result.total_verses}\n"
            f"• Words indexed: {result.total_words}\n"
            f"• New keys added: {result.new_keys_added}\n"
            f"• Occurrences recorded: {result.occurrences_added}\n\n"
            f"{error_summary}"
        )
        
    def _on_index_error(self, error_msg):
        if hasattr(self, 'progress_dlg') and self.progress_dlg:
            self.progress_dlg.close()
        QMessageBox.critical(self, "Indexing Error", f"Failed to index document:\n{error_msg}")


class VerseEditorDialog(QDialog):
    """Standalone dialog for editing a verse and invoking common tools from HolyBookTeacherWindow."""

    def __init__(self, verse: Dict[str, Any], row: int, teacher: HolyBookTeacherWindow, parent=None):
        """
          init   logic.
        
        Args:
            verse: Description of verse.
            row: Description of row.
            teacher: Description of teacher.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.verse = verse
        self.row = row
        self.teacher = teacher
        self.setWindowTitle(f"Verse Editor — {verse.get('number')}")
        self.setMinimumSize(800, 400)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        header_layout = QHBoxLayout()
        header_label = QLabel(f"Verse {self.verse.get('number')} — {self.verse.get('status', '')}")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(self.verse.get('text', ''))
        self.text_edit.setMinimumHeight(200)
        layout.addWidget(self.text_edit)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Save Text")
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)
        confirm_btn = QPushButton("✅ Confirm")
        confirm_btn.clicked.connect(self._on_confirm)
        btn_layout.addWidget(confirm_btn)
        merge_btn = QPushButton("🔗 Merge With Next")
        merge_btn.clicked.connect(self._on_merge_next)
        btn_layout.addWidget(merge_btn)
        split_btn = QPushButton("✂️ Split")
        split_btn.clicked.connect(self._on_split)
        btn_layout.addWidget(split_btn)
        renumber_btn = QPushButton("🔢 Renumber")
        renumber_btn.clicked.connect(self._on_renumber)
        btn_layout.addWidget(renumber_btn)
        ignore_btn = QPushButton("🚫 Ignore")
        ignore_btn.clicked.connect(self._on_ignore)
        btn_layout.addWidget(ignore_btn)
        jump_btn = QPushButton("➡️ Jump to Document")
        jump_btn.clicked.connect(self._on_jump)
        btn_layout.addWidget(jump_btn)
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def _on_save(self):
        new_text = self.text_edit.toPlainText().strip()
        self.teacher._set_verse_text(self.row, new_text, commit=False)
        QMessageBox.information(self, "Saved", "Verse text updated")

    def _on_confirm(self):
        self.teacher._confirm_verse(self.row)
        QMessageBox.information(self, "Confirmed", "Verse confirmed")
        self.accept()

    def _on_merge_next(self):
        self.teacher._merge_next(self.row)
        QMessageBox.information(self, "Merged", "Verse merged with next")
        self.accept()

    def _on_split(self):
        # Delegate to parent which will prompt for split options
        self.teacher._split_verse(self.row)
        self.accept()

    def _on_renumber(self):
        self.teacher._renumber_verse(self.row)
        self.accept()

    def _on_ignore(self):
        self.teacher._ignore_verse(self.row)
        self.accept()

    def _on_jump(self):
        self.teacher._jump_to_document(self.row)


# --- Concordance Indexing Worker ---

from PyQt6.QtCore import QThread, pyqtSignal as Signal

class ConcordanceIndexWorker(QThread):
    """Background worker for indexing a document to the concordance."""
    progress = Signal(int, int, str)
    finished = Signal(object)  # IndexingResult
    error = Signal(str)
    
    def __init__(self, document_id: int, reindex: bool = False):
        super().__init__()
        self.document_id = document_id
        self.reindex = reindex
        
    def run(self):
        try:
            from shared.services.lexicon.concordance_indexer_service import ConcordanceIndexerService
            indexer = ConcordanceIndexerService()
            result = indexer.index_from_verse_teacher(
                document_id=self.document_id,
                progress_callback=self._emit_progress,
                reindex=self.reindex
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
            
    def _emit_progress(self, current, total, message):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        self.progress.emit(current, total, message)