"""Catalyst Button Styles — Visual Liturgy v2.2 §10.

This module provides reusable button style functions for the five Catalyst archetypes.
Import these in any UI file to maintain consistent styling across the Temple.
"""


def get_seeker_style() -> str:
    """The Seeker (Gold) — Reveals hidden knowledge, uncovers, searches."""
    return """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f59e0b, stop:1 #d97706);
            border: 1px solid #b45309;
            color: #0f172a; /* Void */
            font-size: 11pt;
            font-weight: 700;
            border-radius: 8px;
            padding: 0 24px;
            min-height: 48px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fbbf24, stop:1 #f59e0b);
        }
        QPushButton:focus {
            outline: none;
            border: 2px solid #3b82f6; /* Azure focus ring */
        }
        QPushButton:pressed {
            background: #d97706;
        }
        QPushButton:disabled {
            background-color: #fef3c7;
            border: 1px solid #fcd34d;
            color: #92400e;
        }
    """


def get_magus_style() -> str:
    """The Magus (Violet) — Transmutes, executes, primary action."""
    return """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #7c3aed);
            border: 1px solid #6d28d9;
            color: white;
            font-size: 11pt;
            font-weight: 700;
            border-radius: 8px;
            padding: 0 24px;
            min-height: 48px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #a78bfa, stop:1 #8b5cf6);
        }
        QPushButton:focus {
            outline: none;
            border: 2px solid #3b82f6;
        }
        QPushButton:pressed {
            background: #7c3aed;
        }
        QPushButton:disabled {
            background-color: #ede9fe;
            border: 1px solid #c4b5fd;
            color: #7c3aed;
        }
    """


def get_scribe_style() -> str:
    """The Scribe (Emerald) — Preserves, etches, saves."""
    return """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #059669);
            border: 1px solid #047857;
            color: white;
            font-size: 11pt;
            font-weight: 600;
            border-radius: 8px;
            padding: 0 20px;
            min-height: 48px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #34d399, stop:1 #10b981);
        }
        QPushButton:focus {
            outline: none;
            border: 2px solid #3b82f6;
        }
        QPushButton:pressed {
            background: #059669;
        }
        QPushButton:disabled {
            background-color: #d1fae5;
            border: 1px solid #6ee7b7;
            color: #047857;
        }
    """


def get_destroyer_style() -> str:
    """The Destroyer (Crimson) — Purges, banishes, deletes."""
    return """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ef4444, stop:1 #b91c1c);
            border: 1px solid #991b1b;
            color: white;
            font-size: 11pt;
            font-weight: 600;
            border-radius: 8px;
            padding: 0 20px;
            min-height: 48px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f87171, stop:1 #ef4444);
        }
        QPushButton:focus {
            outline: none;
            border: 2px solid #3b82f6;
        }
        QPushButton:pressed {
            background: #b91c1c;
        }
        QPushButton:disabled {
            background-color: #fee2e2;
            border: 1px solid #fca5a5;
            color: #991b1b;
        }
    """


def get_navigator_style() -> str:
    """The Navigator (Void Slate) — Traverses, refreshes, secondary action."""
    return """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #64748b, stop:1 #475569);
            border: 1px solid #334155;
            color: white;
            font-size: 11pt;
            font-weight: 600;
            border-radius: 8px;
            padding: 0 20px;
            min-height: 48px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #94a3b8, stop:1 #64748b);
        }
        QPushButton:focus {
            outline: none;
            border: 2px solid #3b82f6;
        }
        QPushButton:pressed {
            background: #475569;
        }
        QPushButton:disabled {
            background-color: #e2e8f0;
            border: 1px solid #cbd5e1;
            color: #64748b;
        }
    """


def get_filter_chip_style() -> str:
    """Filter chip button style with Magus Violet checked state."""
    return """
        QPushButton {
            border: 1px solid #cbd5e1;
            border-radius: 16px;
            padding: 8px 16px;
            background: #ffffff;
            color: #0f172a;
            font-size: 11pt;
            font-weight: 600;
            min-height: 32px;
        }
        QPushButton:checked {
            background: #8b5cf6;
            color: white;
            border-color: #7c3aed;
        }
        QPushButton:hover {
            background: #f1f5f9;
            border-color: #94a3b8;
        }
        QPushButton:checked:hover {
            background: #a78bfa;
        }
    """
