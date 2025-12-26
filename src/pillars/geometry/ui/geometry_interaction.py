"""Interaction manager and UI components for geometry windows."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Callable

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QInputDialog, QFrame, 
    QColorDialog, QDoubleSpinBox, QToolButton,
    QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QPoint
from PyQt6.QtGui import QColor, QAction, QIcon

@dataclass
class Connection:
    start_index: int
    end_index: int
    color: QColor
    width: float

@dataclass
class DotGroup:
    name: str
    indices: Set[int] = field(default_factory=set)
    total_value: int = 0
    color: QColor = field(default_factory=lambda: QColor("#3b82f6")) # Default blue highlight

# Color palette for groups (cycling)
GROUP_COLOR_PALETTE = [
    QColor("#3b82f6"),  # Blue
    QColor("#22c55e"),  # Green
    QColor("#f59e0b"),  # Amber
    QColor("#ef4444"),  # Red
    QColor("#8b5cf6"),  # Violet
    QColor("#06b6d4"),  # Cyan
    QColor("#ec4899"),  # Pink
    QColor("#84cc16"),  # Lime
]

class GeometryInteractionManager(QObject):
    """Manages the logic for drawing lines and grouping dots."""
    
    # Signals
    groups_changed = pyqtSignal()   # Emitted when groups are created/modified
    connection_added = pyqtSignal(object) # Emitted with Connection object
    connections_cleared = pyqtSignal()
    mode_changed = pyqtSignal(str) # "view", "draw", "group", "select"
    draw_start_changed = pyqtSignal(object) # Emitted with new start index or None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.groups: Dict[str, DotGroup] = {}
        self.connections: List[Connection] = []
        
        self.active_group_name: Optional[str] = None
        self.drawing_active: bool = False
        self.selection_active: bool = False  # For rectangle selection mode
        self.current_draw_start: Optional[int] = None
        self._group_color_index = 0  # For cycling colors
        
        # Drawing settings
        self.pen_color = QColor("#ef4444") # Red default
        self.pen_width = 0.3

    def create_group(self, name: str) -> str:
        """Create a new group. Returns the actual name used (handles duplicates)."""
        base_name = name
        counter = 1
        while name in self.groups:
            name = f"{base_name} ({counter})"
            counter += 1
        
        # Assign color from palette
        color = GROUP_COLOR_PALETTE[self._group_color_index % len(GROUP_COLOR_PALETTE)]
        self._group_color_index += 1

        self.groups[name] = DotGroup(name=name, color=color)
        self.active_group_name = name
        self.groups_changed.emit()
        return name

    def delete_group(self, name: str):
        if name in self.groups:
            del self.groups[name]
            if self.active_group_name == name:
                self.active_group_name = next(iter(self.groups)) if self.groups else None
            self.groups_changed.emit()

    def add_dot_to_group(self, group_name: str, dot_index: int, value: int = 1):
        if group_name not in self.groups:
            return
        
        group = self.groups[group_name]
        if dot_index not in group.indices:
            group.indices.add(dot_index)
            group.total_value += dot_index
            self.groups_changed.emit()

    def remove_dot_from_group(self, group_name: str, dot_index: int):
        if group_name not in self.groups:
            return
        group = self.groups[group_name]
        if dot_index in group.indices:
            group.indices.remove(dot_index)
            group.total_value -= dot_index
            self.groups_changed.emit()
            
    def toggle_dot_in_group(self, dot_index: int):
        """Toggle dot membership in the ACTIVE group."""
        if not self.active_group_name:
            self.create_group("Group 1")
            
        if self.active_group_name:
            group = self.groups[self.active_group_name]
            if dot_index in group.indices:
                self.remove_dot_from_group(self.active_group_name, dot_index)
            else:
                self.add_dot_to_group(self.active_group_name, dot_index)

    def add_connection(self, start: int, end: int):
        conn = Connection(start, end, self.pen_color, self.pen_width)
        self.connections.append(conn)
        self.connection_added.emit(conn)
    
    def process_draw_click(self, index: int):
        """Handle a click in draw mode: Polyline logic."""
        if self.current_draw_start is None:
            self.current_draw_start = index
            self.draw_start_changed.emit(index)
        elif self.current_draw_start == index:
            self.current_draw_start = None
            self.draw_start_changed.emit(None)
        else:
            print(f"[DEBUG] Manager: connecting {self.current_draw_start} -> {index}")
            self.add_connection(self.current_draw_start, index)
            # Continuous drawing: existing end becomes new start
            self.current_draw_start = index
            self.draw_start_changed.emit(index)

    def clear(self):
        self.groups.clear()
        self.connections.clear()
        self.active_group_name = None
        self.current_draw_start = None
        self.groups_changed.emit()
        self.connections_cleared.emit()
        self.draw_start_changed.emit(None) # Also clear start selection
        
    # ...


class GroupManagementPanel(QWidget):
    """UI for managing dot groups."""
    
    def __init__(self, manager: GeometryInteractionManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self._refreshing_list = False
        self.manager.groups_changed.connect(self._refresh_list)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        header_row = QHBoxLayout()
        label = QLabel("Dot Ensembles")
        label.setStyleSheet("font-family: 'Inter'; font-size: 16pt; font-weight: 800; color: #0f172a;")
        header_row.addWidget(label)
        
        add_btn = QToolButton()
        add_btn.setText("+")
        add_btn.setToolTip("Create new group")
        add_btn.setFixedSize(32, 32)
        add_btn.clicked.connect(self._create_group_prompt)
        add_btn.setStyleSheet("""
            QToolButton {
                background-color: #f1f5f9;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                color: #334155;
                font-weight: bold;
                font-size: 14pt;
            }
            QToolButton:hover {
                background-color: #e2e8f0;
                color: #0f172a;
            }
            QToolButton:pressed {
                background-color: #cbd5e1;
            }
        """)
        header_row.addWidget(add_btn)
        
        layout.addLayout(header_row)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(
            "QListWidget {"
            "    border: 2px solid #e2e8f0;"
            "    border-radius: 12px;"
            "    background: #ffffff;"
            "    padding: 8px;"
            "}"
            "QListWidget::item {"
            "    padding: 8px;"
            "    border-radius: 6px;"
            "    color: #334155;"
            "    font-weight: 600;"
            "}"
            "QListWidget::item:selected {"
            "    background: #f1f5f9;"
            "    color: #0f172a;"
            "    border: 1px solid #cbd5e1;"
            "}"
        )
        self.list_widget.currentItemChanged.connect(self._on_selection_change)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.list_widget)
        
        # Dots in Group section
        dots_header = QLabel("Constituents")
        dots_header.setStyleSheet("font-family: 'Inter'; font-size: 11pt; font-weight: 700; color: #64748b; margin-top: 8px;")
        layout.addWidget(dots_header)
        
        self.dots_list = QListWidget()
        self.dots_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)  # Ctrl+Click
        self.dots_list.setViewMode(QListWidget.ViewMode.IconMode)  # For grid layout
        self.dots_list.setFlow(QListWidget.Flow.LeftToRight)
        self.dots_list.setWrapping(True)
        self.dots_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.dots_list.setSpacing(4)
        self.dots_list.setStyleSheet(
            "QListWidget {"
            "    border: 2px solid #e2e8f0;"
            "    border-radius: 12px;"
            "    background: #ffffff;"
            "    padding: 8px;"
            "}"
            "QListWidget::item {"
            "    padding: 4px 8px;"
            "    border-radius: 4px;"
            "    background: #f1f5f9;"
            "    color: #334155;"
            "}"
            "QListWidget::item:selected {"
            "    background: #3b82f6;"
            "    color: white;"
            "}"
        )
        self.dots_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.dots_list.customContextMenuRequested.connect(self._show_dots_context_menu)
        self.dots_list.setMaximumHeight(120)
        layout.addWidget(self.dots_list)
        
        hint = QLabel("Right Click dots to add/remove from active group.")
        hint.setStyleSheet("color: #94a3b8; font-size: 9pt; font-style: italic;")
        hint.setWordWrap(True)
        layout.addWidget(hint)

    def _create_group_prompt(self):
        name, ok = QInputDialog.getText(self, "New Group", "Group Name:")
        if ok and name:
            self.manager.create_group(name)

    def _refresh_list(self):
        # Disconnect signal to avoid recursion loop
        try:
            self.list_widget.currentItemChanged.disconnect(self._on_selection_change)
        except TypeError:
            pass # Not connected
            
        try:
            self.list_widget.clear()
            
            for name, group in self.manager.groups.items():
                item = QListWidgetItem(f"{name} (Sum: {group.total_value})")
                item.setData(Qt.ItemDataRole.UserRole, name)
                self.list_widget.addItem(item)
                
                if name == self.manager.active_group_name:
                    self.list_widget.setCurrentItem(item)
            
            # Also refresh the dots list
            self._refresh_dots()
        finally:
            self.list_widget.currentItemChanged.connect(self._on_selection_change)

    def _on_selection_change(self, current: QListWidgetItem, previous: QListWidgetItem):
        if self._refreshing_list:
            return
            
        if current:
            name = current.data(Qt.ItemDataRole.UserRole)
            self.manager.active_group_name = name
            self._refresh_dots()

    def _refresh_dots(self):
        """Refresh the dots list for the active group."""
        self.dots_list.clear()
        if not self.manager.active_group_name:
            return
        
        group = self.manager.groups.get(self.manager.active_group_name)
        if not group:
            return
        
        # Sort indices for consistent display
        sorted_indices = sorted(group.indices)
        for idx in sorted_indices:
            item = QListWidgetItem(str(idx))
            item.setData(Qt.ItemDataRole.UserRole, idx)
            self.dots_list.addItem(item)

    def _show_dots_context_menu(self, pos):
        """Context menu for removing dots from group."""
        selected_items = self.dots_list.selectedItems()
        if not selected_items:
            return
        
        menu = QMenu(self)
        remove_action = menu.addAction(f"Remove {len(selected_items)} dot(s) from group")
        
        action = menu.exec(self.dots_list.mapToGlobal(pos))
        
        if action == remove_action:
            for item in selected_items:
                idx = item.data(Qt.ItemDataRole.UserRole)
                if self.manager.active_group_name:
                    self.manager.remove_dot_from_group(self.manager.active_group_name, idx)
            self._refresh_dots()

    def _show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
        
        group_name = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu(self)
        
        rename_action = menu.addAction("Rename")
        delete_action = menu.addAction("Delete")
        
        action = menu.exec(self.list_widget.mapToGlobal(pos))
        
        if action == rename_action:
            self._rename_group(group_name)
        elif action == delete_action:
            self.manager.delete_group(group_name)

    def _rename_group(self, old_name: str):
        from PyQt6.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(self, "Rename Group", "New name:", text=old_name)
        if ok and new_name and new_name != old_name:
            if old_name in self.manager.groups:
                group = self.manager.groups.pop(old_name)
                group.name = new_name
                self.manager.groups[new_name] = group
                if self.manager.active_group_name == old_name:
                    self.manager.active_group_name = new_name
                self.manager.groups_changed.emit()


class ConnectionToolBar(QFrame):
    """Toolbar for drawing settings and appearance controls."""
    
    # Signals for color changes
    dot_color_changed = pyqtSignal(object)   # Emits QColor
    text_color_changed = pyqtSignal(object)  # Emits QColor
    
    def __init__(self, manager: GeometryInteractionManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self._setup_ui()
        self.setStyleSheet("background-color: #f8fafc; border-bottom: 1px solid #e2e8f0;")

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)
        
        # Draw Mode Toggle (Navigator Style)
        self.draw_btn = QPushButton("Inscribe Lines")
        self.draw_btn.setCheckable(True)
        self.draw_btn.clicked.connect(self._toggle_draw_mode)
        self.draw_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #64748b, stop:1 #475569);
                border: 1px solid #334155;
                color: white;
                font-weight: 600;
                border-radius: 12px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #94a3b8, stop:1 #64748b);
            }
            QPushButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #7c3aed); /* Magus when active */
                border: 1px solid #6d28d9;
            }
            """
        )
        layout.addWidget(self.draw_btn)
        
        # Select Mode Toggle
        self.select_btn = QPushButton("Select Points")
        self.select_btn.setCheckable(True)
        self.select_btn.clicked.connect(self._toggle_select_mode)
        self.select_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #64748b, stop:1 #475569);
                border: 1px solid #334155;
                color: white;
                font-weight: 600;
                border-radius: 12px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #94a3b8, stop:1 #64748b);
            }
            QPushButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f59e0b, stop:1 #d97706); /* Seeker when active */
                border: 1px solid #b45309;
                color: #0f172a;
            }
            """
        )
        layout.addWidget(self.select_btn)
        
        layout.addSpacing(16)
        
        # Color
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(32, 32)
        self.color_btn.setStyleSheet(f"background-color: {self.manager.pen_color.name()}; border-radius: 16px; border: 2px solid #e2e8f0;")
        self.color_btn.clicked.connect(self._pick_color)
        
        color_lbl = QLabel("Tincture:")
        color_lbl.setStyleSheet("color: #475569; font-weight: 600;")
        layout.addWidget(color_lbl)
        layout.addWidget(self.color_btn)
        
        # Width
        layout.addSpacing(16)
        width_lbl = QLabel("Stroke:")
        width_lbl.setStyleSheet("color: #475569; font-weight: 600;")
        layout.addWidget(width_lbl)
        
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(0.10, 2.0)
        self.width_spin.setValue(0.3)
        self.width_spin.setSingleStep(0.1)
        self.width_spin.setDecimals(2)
        self.width_spin.valueChanged.connect(self._update_width)
        self.width_spin.setStyleSheet("""
            QDoubleSpinBox {
                padding: 4px;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                background: white;
            }
        """)
        
        layout.addWidget(self.width_spin)
        
        # Separator needs to be visual or just spacing
        layout.addSpacing(32)
        
        # Dot Color
        self.dot_color_btn = QPushButton()
        self.dot_color_btn.setFixedSize(32, 32)
        self._dot_color = QColor("#3b82f6") # Default blue
        self.dot_color_btn.setStyleSheet(f"background-color: {self._dot_color.name()}; border-radius: 16px; border: 2px solid #e2e8f0;")
        self.dot_color_btn.clicked.connect(self._pick_dot_color)
        
        dot_lbl = QLabel("Dot:")
        dot_lbl.setStyleSheet("color: #475569; font-weight: 600;")
        layout.addWidget(dot_lbl)
        layout.addWidget(self.dot_color_btn)
        
        # Text Color
        self.text_color_btn = QPushButton()
        self.text_color_btn.setFixedSize(32, 32)
        self._text_color = QColor("#1e3a5f") # Default dark blue
        self.text_color_btn.setStyleSheet(f"background-color: {self._text_color.name()}; border-radius: 16px; border: 2px solid #e2e8f0;")
        self.text_color_btn.clicked.connect(self._pick_text_color)
        
        text_lbl = QLabel("Sigil:")
        text_lbl.setStyleSheet("color: #475569; font-weight: 600;")
        layout.addWidget(text_lbl)
        layout.addWidget(self.text_color_btn)
        
        layout.addStretch()

    def _toggle_draw_mode(self, checked: bool):
        self.manager.drawing_active = checked
        if checked:
            self.select_btn.setChecked(False)
            self.manager.selection_active = False
        self.manager.mode_changed.emit("draw" if checked else "view")

    def _toggle_select_mode(self, checked: bool):
        self.manager.selection_active = checked
        if checked:
            self.draw_btn.setChecked(False)
            self.manager.drawing_active = False
        self.manager.mode_changed.emit("select" if checked else "view")

    def _pick_color(self):
        color = QColorDialog.getColor(self.manager.pen_color, self, "Line Color")
        if color.isValid():
            self.manager.pen_color = color
            self.color_btn.setStyleSheet(f"background-color: {color.name()}; border-radius: 12px; border: 2px solid white;")

    def _update_width(self, val: float):
        self.manager.pen_width = val

    def _pick_dot_color(self):
        color = QColorDialog.getColor(self._dot_color, self, "Dot Color")
        if color.isValid():
            self._dot_color = color
            self.dot_color_btn.setStyleSheet(f"background-color: {color.name()}; border-radius: 12px; border: 2px solid #cbd5e1;")
            self.dot_color_changed.emit(color)

    def _pick_text_color(self):
        color = QColorDialog.getColor(self._text_color, self, "Text Color")
        if color.isValid():
            self._text_color = color
            self.text_color_btn.setStyleSheet(f"background-color: {color.name()}; border-radius: 12px; border: 2px solid #cbd5e1;")
            self.text_color_changed.emit(color)
