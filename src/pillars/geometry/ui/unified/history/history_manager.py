"""
Declaration History Manager — ADR-011

Manages calculation history with full undo/redo support and session export.
The history is the "memory" of the Unified Geometry Viewer.

Reference: wiki/01_blueprints/decisions/ADR-011_unified_geometry_viewer.md
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Callable, Optional

from PyQt6.QtCore import QObject, pyqtSignal

from .history_entry import HistoryEntry

logger = logging.getLogger(__name__)


class DeclarationHistory(QObject):
    """
    Manages calculation history with undo/redo.
    
    The history maintains a linear sequence of HistoryEntry objects.
    Undo/redo navigate this sequence without modifying it.
    New entries after an undo truncate the "future" (standard undo behavior).
    
    Signals:
        history_changed: Emitted when history is modified (new entry, undo, redo)
        current_changed: Emitted when current index changes
        
    Attributes:
        max_entries: Maximum number of entries to keep (oldest are pruned)
    """
    
    # Signals
    history_changed = pyqtSignal()  # Emitted on any history change
    current_changed = pyqtSignal(object)  # Emits current HistoryEntry or None
    entry_added = pyqtSignal(object)  # Emits newly added HistoryEntry
    
    def __init__(self, max_entries: int = 50, parent: Optional[QObject] = None):
        """
        Initialize the history manager.
        
        Args:
            max_entries: Maximum entries to retain (default 50)
            parent: Optional Qt parent
        """
        super().__init__(parent)
        self._entries: list[HistoryEntry] = []
        self._current_index: int = -1
        self._max_entries = max_entries
        
        logger.info(f"DeclarationHistory initialized (max_entries={max_entries})")
    
    # ─────────────────────────────────────────────────────────────────
    # Properties
    # ─────────────────────────────────────────────────────────────────
    
    @property
    def count(self) -> int:
        """Return the number of entries in history."""
        return len(self._entries)
    
    @property
    def current_index(self) -> int:
        """Return the index of the current entry (-1 if empty)."""
        return self._current_index
    
    @property
    def current_entry(self) -> Optional[HistoryEntry]:
        """Return the current history entry, or None if empty."""
        if 0 <= self._current_index < len(self._entries):
            return self._entries[self._current_index]
        return None
    
    @property
    def can_undo(self) -> bool:
        """Return True if undo is possible."""
        return self._current_index > 0
    
    @property
    def can_redo(self) -> bool:
        """Return True if redo is possible."""
        return self._current_index < len(self._entries) - 1
    
    @property
    def is_empty(self) -> bool:
        """Return True if history is empty."""
        return len(self._entries) == 0
    
    # ─────────────────────────────────────────────────────────────────
    # Core Operations
    # ─────────────────────────────────────────────────────────────────
    
    def push(
        self,
        declaration: Any,  # Declaration
        verdict: Any,  # Verdict
        result: Optional[Any] = None,  # RealizeResult
        notes: str = "",
        skip_history: bool = False,  # If True, don't add to history
    ) -> Optional[HistoryEntry]:
        """
        Add a new entry to history.
        
        If we are not at the end of history (i.e., user has undone),
        this truncates the "future" entries (standard undo behavior).
        
        Args:
            declaration: The Canon declaration
            verdict: The validation verdict
            result: The realization result (if validation passed)
            notes: Optional user notes
            skip_history: If True, don't add to history (for initial load)
            
        Returns:
            The newly created HistoryEntry, or None if skip_history=True
        """
        if skip_history:
            logger.debug("Skipping history entry (initial load)")
            return None
        
        # Create the entry
        entry = HistoryEntry(
            declaration=declaration,
            verdict=verdict,
            result=result,
            timestamp=datetime.now(),
            notes=notes,
        )
        
        # Apply any saved metadata (notes/custom_title) from previous session
        self.apply_metadata_to_entry(entry)
        
        # Truncate future if we've undone
        if self._current_index < len(self._entries) - 1:
            future_count = len(self._entries) - self._current_index - 1
            self._entries = self._entries[:self._current_index + 1]
            logger.info(f"Truncated {future_count} future entries")
        
        # Add the new entry
        self._entries.append(entry)
        self._current_index = len(self._entries) - 1
        
        # Prune if over limit
        if len(self._entries) > self._max_entries:
            pruned = len(self._entries) - self._max_entries
            self._entries = self._entries[pruned:]
            self._current_index -= pruned
            logger.info(f"Pruned {pruned} oldest entries")
        
        logger.info(f"History push: {entry.short_signature} ({entry.form_type})")
        
        # Persist metadata after each push
        self._save_metadata()
        
        # Emit signals
        self.entry_added.emit(entry)
        self.current_changed.emit(entry)
        self.history_changed.emit()
        
        return entry
    
    def undo(self) -> Optional[HistoryEntry]:
        """
        Move to the previous entry in history.
        
        Returns:
            The previous HistoryEntry, or None if at the beginning
        """
        if not self.can_undo:
            logger.info("Undo: already at beginning")
            return None
        
        self._current_index -= 1
        entry = self._entries[self._current_index]
        
        logger.info(f"Undo to: {entry.short_signature}")
        
        self.current_changed.emit(entry)
        self.history_changed.emit()
        
        return entry
    
    def redo(self) -> Optional[HistoryEntry]:
        """
        Move to the next entry in history.
        
        Returns:
            The next HistoryEntry, or None if at the end
        """
        if not self.can_redo:
            logger.info("Redo: already at end")
            return None
        
        self._current_index += 1
        entry = self._entries[self._current_index]
        
        logger.info(f"Redo to: {entry.short_signature}")
        
        self.current_changed.emit(entry)
        self.history_changed.emit()
        
        return entry
    
    def goto(self, index: int) -> Optional[HistoryEntry]:
        """
        Jump to a specific index in history.
        
        Args:
            index: Target index (0-based)
            
        Returns:
            The HistoryEntry at that index, or None if invalid
        """
        if not (0 <= index < len(self._entries)):
            logger.warning(f"Invalid history index: {index}")
            return None
        
        if index == self._current_index:
            return self._entries[index]
        
        self._current_index = index
        entry = self._entries[index]
        
        logger.info(f"History goto: index {index} ({entry.short_signature})")
        
        self.current_changed.emit(entry)
        self.history_changed.emit()
        
        return entry
    
    def goto_signature(self, signature: str) -> Optional[HistoryEntry]:
        """
        Jump to an entry by its signature.
        
        Args:
            signature: Full or partial signature to match
            
        Returns:
            The matching HistoryEntry, or None if not found
        """
        for i, entry in enumerate(self._entries):
            if entry.signature.startswith(signature):
                return self.goto(i)
        
        logger.warning(f"No entry found with signature: {signature}")
        return None
    
    def clear(self) -> None:
        """Clear all history entries."""
        count = len(self._entries)
        self._entries.clear()
        self._current_index = -1
        
        logger.info(f"History cleared ({count} entries)")
        
        self.current_changed.emit(None)
        self.history_changed.emit()
    
    def remove(self, index: int) -> bool:
        """
        Remove a specific entry from history.
        
        Args:
            index: Index of the entry to remove
            
        Returns:
            True if entry was removed, False if index invalid
        """
        if not (0 <= index < len(self._entries)):
            return False
        
        entry = self._entries[index]
        sig = entry.short_signature
        
        # Remove the entry
        del self._entries[index]
        
        # Adjust current index if needed
        if self._current_index >= len(self._entries):
            self._current_index = len(self._entries) - 1
        elif self._current_index > index:
            self._current_index -= 1
        
        logger.info(f"Removed history entry {sig} at index {index}")
        
        # Persist metadata after removal
        self._save_metadata()
        
        self.history_changed.emit()
        self.current_changed.emit(self.current_entry)
        
        return True
    
    # ─────────────────────────────────────────────────────────────────
    # Query Operations
    # ─────────────────────────────────────────────────────────────────
    
    def get_entry(self, index: int) -> Optional[HistoryEntry]:
        """Get entry at a specific index without changing current."""
        if 0 <= index < len(self._entries):
            return self._entries[index]
        return None
    
    def set_current_notes(self, notes: str) -> bool:
        """
        Update the notes on the current history entry.
        
        Args:
            notes: The new notes text (can include rich text/HTML)
            
        Returns:
            True if notes were updated, False if no current entry
        """
        if self.current_entry is not None:
            # HistoryEntry is a dataclass, we can modify notes directly
            object.__setattr__(self.current_entry, 'notes', notes)
            logger.debug(f"Updated notes for entry {self.current_entry.short_signature}")
            self._save_metadata()  # Persist notes
            return True
        return False
    
    def get_current_notes(self) -> str:
        """Get notes from the current history entry."""
        if self.current_entry is not None:
            return self.current_entry.notes
        return ""
    
    def set_notes_by_signature(self, signature: str, notes: str) -> bool:
        """
        Update notes for an entry by signature.

        Args:
            signature: The entry's signature (full or partial)
            notes: The new notes text

        Returns:
            True if notes were updated, False if entry not found
        """
        entry = self.get_entry_by_signature(signature)
        if entry is not None:
            object.__setattr__(entry, 'notes', notes)
            logger.debug(f"Updated notes for entry {entry.short_signature}")
            self._save_metadata()  # Persist notes
            self.history_changed.emit()  # Refresh UI to show notes indicator
            return True
        return False
    
    def set_custom_title_by_index(self, index: int, custom_title: str) -> bool:
        """
        Update custom_title for an entry by index.
        
        Args:
            index: The entry index
            custom_title: The new custom title
            
        Returns:
            True if title was updated, False if entry not found
        """
        entry = self.get_entry(index)
        if entry is not None:
            object.__setattr__(entry, 'custom_title', custom_title)
            logger.debug(f"Updated custom_title for entry {entry.short_signature} to '{custom_title}'")
            self._save_metadata()  # Persist title
            self.history_changed.emit()  # Refresh UI
            return True
        return False
    
    def get_entry_by_signature(self, signature: str) -> Optional[HistoryEntry]:
        """Find entry by signature without changing current."""
        for entry in self._entries:
            if entry.signature.startswith(signature):
                return entry
        return None
    
    def get_timeline(self) -> list[HistoryEntry]:
        """
        Return all entries in chronological order (oldest first).
        
        Returns a copy to prevent external modification.
        """
        return list(self._entries)
    
    def get_timeline_reversed(self) -> list[HistoryEntry]:
        """
        Return all entries in reverse chronological order (newest first).
        """
        return list(reversed(self._entries))
    
    def get_recent(self, count: int = 10) -> list[HistoryEntry]:
        """Return the N most recent entries (newest first)."""
        return list(reversed(self._entries[-count:]))
    
    def find_entries(
        self,
        predicate: Callable[[HistoryEntry], bool]
    ) -> list[HistoryEntry]:
        """
        Find all entries matching a predicate.
        
        Args:
            predicate: Function that returns True for matching entries
            
        Returns:
            List of matching entries (chronological order)
        """
        return [e for e in self._entries if predicate(e)]
    
    def find_by_form_type(self, form_type: str) -> list[HistoryEntry]:
        """Find all entries of a specific form type."""
        return self.find_entries(lambda e: e.form_type == form_type)
    
    def find_valid_entries(self) -> list[HistoryEntry]:
        """Find all entries that passed validation."""
        return self.find_entries(lambda e: e.is_valid)
    
    def find_failed_entries(self) -> list[HistoryEntry]:
        """Find all entries that failed validation."""
        return self.find_entries(lambda e: not e.is_valid)
    
    # ─────────────────────────────────────────────────────────────────
    # Export / Import
    # ─────────────────────────────────────────────────────────────────
    
    def export_session(self) -> dict[str, Any]:
        """
        Export full session as a JSON-serializable dictionary.
        
        Returns:
            Dictionary with session metadata and all entries
        """
        return {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "current_index": self._current_index,
            "entries_count": len(self._entries),
            "entries": [e.to_dict() for e in self._entries],
        }
    
    def export_session_json(self, indent: int = 2) -> str:
        """
        Export session as formatted JSON string.
        
        Args:
            indent: JSON indentation (default 2)
            
        Returns:
            JSON string
        """
        return json.dumps(self.export_session(), indent=indent, default=str)
    
    def get_statistics(self) -> dict[str, Any]:
        """
        Return statistics about the history.
        
        Returns:
            Dictionary with counts, form types, validity stats
        """
        if not self._entries:
            return {
                "total": 0,
                "valid": 0,
                "failed": 0,
                "form_types": {},
            }
        
        from collections import Counter
        
        valid_count = sum(1 for e in self._entries if e.is_valid)
        form_types = Counter(e.form_type for e in self._entries)
        
        return {
            "total": len(self._entries),
            "valid": valid_count,
            "failed": len(self._entries) - valid_count,
            "form_types": dict(form_types),
            "oldest": self._entries[0].full_timestamp if self._entries else None,
            "newest": self._entries[-1].full_timestamp if self._entries else None,
        }
    
    # ─────────────────────────────────────────────────────────────────
    # Comparison Support
    # ─────────────────────────────────────────────────────────────────
    
    def get_comparison_pair(
        self,
        index_a: int,
        index_b: int
    ) -> Optional[tuple[HistoryEntry, HistoryEntry]]:
        """
        Get two entries for comparison.
        
        Args:
            index_a: First entry index
            index_b: Second entry index
            
        Returns:
            Tuple of (entry_a, entry_b) or None if invalid indices
        """
        entry_a = self.get_entry(index_a)
        entry_b = self.get_entry(index_b)
        
        if entry_a is None or entry_b is None:
            return None
        
        return (entry_a, entry_b)
    
    def compare_entries(
        self,
        entry_a: HistoryEntry,
        entry_b: HistoryEntry
    ) -> dict[str, Any]:
        """
        Compare two history entries.
        
        Returns:
            Dictionary with comparison data
        """
        params_a = entry_a.get_canonical_params()
        params_b = entry_b.get_canonical_params()
        
        # Find changed parameters
        all_keys = set(params_a.keys()) | set(params_b.keys())
        param_changes = {}
        for key in all_keys:
            val_a = params_a.get(key)
            val_b = params_b.get(key)
            if val_a != val_b:
                param_changes[key] = {"from": val_a, "to": val_b}
        
        return {
            "signature_a": entry_a.signature,
            "signature_b": entry_b.signature,
            "form_type_same": entry_a.form_type == entry_b.form_type,
            "validity_same": entry_a.is_valid == entry_b.is_valid,
            "param_changes": param_changes,
            "time_delta_seconds": (entry_b.timestamp - entry_a.timestamp).total_seconds(),
        }
    
    # ─────────────────────────────────────────────────────────────────
    # Magic Methods
    # ─────────────────────────────────────────────────────────────────
    
    def __len__(self) -> int:
        """Return number of entries."""
        return len(self._entries)
    
    def __getitem__(self, index: int) -> HistoryEntry:
        """Get entry by index (raises IndexError if out of range)."""
        return self._entries[index]
    
    def __iter__(self):
        """Iterate over entries (chronological order)."""
        return iter(self._entries)
    
    def __bool__(self) -> bool:
        """Return True if history has entries."""
        return len(self._entries) > 0
    
    def __str__(self) -> str:
        """String representation."""
        return f"DeclarationHistory({len(self._entries)} entries, current={self._current_index})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"DeclarationHistory(count={len(self._entries)}, "
            f"current_index={self._current_index}, "
            f"max_entries={self._max_entries})"
        )
    
    # ─────────────────────────────────────────────────────────────────
    # Metadata Persistence
    # ─────────────────────────────────────────────────────────────────
    
    def set_metadata_file(self, filepath: str) -> None:
        """
        Set the file path for persisting notes and custom titles.
        
        Args:
            filepath: Path to the JSON file for metadata storage
        """
        self._metadata_file = filepath
        self._load_metadata()
    
    def _save_metadata(self) -> None:
        """Save notes and custom titles to the metadata file."""
        if not hasattr(self, '_metadata_file') or not self._metadata_file:
            return
        
        try:
            # Build metadata dict keyed by signature
            metadata: dict[str, dict[str, str]] = {}
            for entry in self._entries:
                if entry.notes or entry.custom_title:
                    metadata[entry.signature] = {
                        "notes": entry.notes,
                        "custom_title": entry.custom_title,
                    }
            
            # Save to file
            import os
            os.makedirs(os.path.dirname(self._metadata_file), exist_ok=True)
            with open(self._metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            logger.debug(f"Saved metadata for {len(metadata)} entries to {self._metadata_file}")
        except Exception as e:
            logger.warning(f"Failed to save metadata: {e}")
    
    def _load_metadata(self) -> None:
        """Load notes and custom titles from the metadata file."""
        if not hasattr(self, '_metadata_file') or not self._metadata_file:
            return
        
        try:
            import os
            if not os.path.exists(self._metadata_file):
                logger.debug(f"No metadata file at {self._metadata_file}")
                self._loaded_metadata = {}
                return
            
            with open(self._metadata_file, 'r', encoding='utf-8') as f:
                self._loaded_metadata = json.load(f)
            
            logger.info(f"Loaded metadata for {len(self._loaded_metadata)} entries from {self._metadata_file}")
            
            # Apply to any existing entries
            self._apply_loaded_metadata()
        except Exception as e:
            logger.warning(f"Failed to load metadata: {e}")
            self._loaded_metadata = {}
    
    def _apply_loaded_metadata(self) -> None:
        """Apply loaded metadata to current entries."""
        if not hasattr(self, '_loaded_metadata') or not self._loaded_metadata:
            return
        
        for entry in self._entries:
            if entry.signature in self._loaded_metadata:
                meta = self._loaded_metadata[entry.signature]
                if meta.get('notes') and not entry.notes:
                    object.__setattr__(entry, 'notes', meta['notes'])
                if meta.get('custom_title') and not entry.custom_title:
                    object.__setattr__(entry, 'custom_title', meta['custom_title'])
    
    def apply_metadata_to_entry(self, entry: HistoryEntry) -> None:
        """Apply any saved metadata to a newly added entry."""
        if not hasattr(self, '_loaded_metadata') or not self._loaded_metadata:
            return
        
        if entry.signature in self._loaded_metadata:
            meta = self._loaded_metadata[entry.signature]
            if meta.get('notes') and not entry.notes:
                object.__setattr__(entry, 'notes', meta['notes'])
            if meta.get('custom_title') and not entry.custom_title:
                object.__setattr__(entry, 'custom_title', meta['custom_title'])
            logger.debug(f"Applied saved metadata to entry {entry.short_signature}")