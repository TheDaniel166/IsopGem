from PyQt6.QtWidgets import QColorDialog, QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QObject

class StyleHandler(QObject):
    """
    Handles all styling operations for the Spreadsheet (Borders, Fonts, Colors, Align).
    Extracted from SpreadsheetWindow.
    """
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self._border_settings = {"style": "solid", "width": 1, "color": "#000000"}
        
        # UI Elements managed by handler (optional, but keep references if needed)
        self.border_menu = None
        self.border_actions = []

    @property
    def model(self):
        """Always fetch current model from window to avoid stale references."""
        return self.window.model

    @property
    def view(self):
        """Always fetch view from window."""
        return self.window.view

    def setup_border_menu(self):
        """Creates and returns the Border Menu Actions for the Toolbar."""
        self.border_menu = QMenu(self.window)
        self.border_actions = []
        
        actions_data = [
            ("All Borders", "all"),
            ("No Borders", "none"),
            ("Outside Borders", "outside"),
            ("Top Border", "top"),
            ("Bottom Border", "bottom"),
            ("Left Border", "left"),
            ("Right Border", "right"),
        ]
        
        for name, key in actions_data:
            act = QAction(name, self.window)
            act.triggered.connect(lambda checked, k=key: self.apply_borders(k))  # type: ignore[reportUnknownArgumentType, reportUnknownLambdaType, reportUnknownMemberType]
            self.border_menu.addAction(act)
            self.border_actions.append(act)
            
        self.border_menu.addSeparator()
        
        # Color
        act_color = QAction("Line Color...", self.window)
        act_color.triggered.connect(self.pick_border_color)
        self.border_menu.addAction(act_color)
        
        # Style & Width Submenus
        style_menu = self.border_menu.addMenu("Line Style")
        width_menu = self.border_menu.addMenu("Line Width")
        
        for s in ["solid", "dash", "dot"]:
            a = QAction(s.title(), self.window)
            a.triggered.connect(lambda checked, style=s: self.set_border_style(style))  # type: ignore[reportUnknownArgumentType, reportUnknownLambdaType, reportUnknownMemberType]
            style_menu.addAction(a)
            
        for w in [1, 2, 3, 4, 5]:
            a = QAction(f"{w}px", self.window)
            a.triggered.connect(lambda checked, width=w: self.set_border_width(width))  # type: ignore[reportUnknownArgumentType, reportUnknownLambdaType, reportUnknownMemberType]
            width_menu.addAction(a)
            
        return self.border_menu, self.border_actions, style_menu, width_menu

    # --- Border Logic ---
    def set_border_style(self, style):
        self._border_settings["style"] = style
        self.update_selected_borders()

    def set_border_width(self, width):
        self._border_settings["width"] = width
        self.update_selected_borders()

    def pick_border_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self._border_settings["color"] = color.name()
            self.update_selected_borders()

    def apply_borders(self, border_type):
        from ..spreadsheet_view import BorderRole
        from ...services.border_engine import BorderEngine
        
        indexes = self.view.selectionModel().selectedIndexes()  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
        if not indexes: return
        
        updates = BorderEngine.calculate_borders(
            self.model, indexes, border_type, self._border_settings, BorderRole  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
        )
        
        if not updates: return
        
        self.model.undo_stack.beginMacro(f"Set Border {border_type}")  # type: ignore[reportUnknownMemberType]
        try:
            for idx, new_borders in updates:
                self.model.setData(idx, new_borders, BorderRole)
        finally:
            self.model.undo_stack.endMacro()  # type: ignore[reportUnknownMemberType]

    def update_selected_borders(self):
        """Smart update existing borders with new settings."""
        from ..spreadsheet_view import BorderRole
        from ...services.border_engine import BorderEngine
        
        indexes = self.view.selectionModel().selectedIndexes()  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
        if not indexes: return

        updates = BorderEngine.update_existing_borders(
            self.model, indexes, self._border_settings, BorderRole  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
        )
        
        if not updates: return

        self.model.undo_stack.beginMacro("Update Border Style")  # type: ignore[reportUnknownMemberType]
        try:
            for idx, new_borders in updates:
                self.model.setData(idx, new_borders, BorderRole)
        finally:
            self.model.undo_stack.endMacro()  # type: ignore[reportUnknownMemberType]

    # --- Generic Formatting ---
    def apply_cell_property(self, role, value, description):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        indexes = self.view.selectionModel().selectedIndexes()  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
        if not indexes: return

        self.model.undo_stack.beginMacro(description)  # type: ignore[reportUnknownMemberType]
        try:
            for idx in indexes:
                if idx.isValid():
                    self.model.setData(idx, value, role)
        finally:
            self.model.undo_stack.endMacro()  # type: ignore[reportUnknownMemberType]

    # --- Public API for Window/Toolbar signals ---

    def apply_style(self, style_type, checked):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        mapping = {
            "bold": ("bold", checked),
            "italic": ("italic", checked),
            "underline": ("underline", checked)
        }
        if style_type in mapping:
            self.apply_cell_property(Qt.ItemDataRole.FontRole, mapping[style_type], f"Apply {style_type}")

    def apply_align(self, align):
        self.apply_cell_property(Qt.ItemDataRole.TextAlignmentRole, align, f"Align {align}")
        
    def set_font_family(self, font):
        self.apply_cell_property(Qt.ItemDataRole.FontRole, ("font_family", font.family()), f"Font Family {font.family()}")  # type: ignore[reportUnknownMemberType]

    def set_font_size(self, size):
        self.apply_cell_property(Qt.ItemDataRole.FontRole, ("font_size", size), f"Font Size {size}")

    def pick_color(self, target):
        color = QColorDialog.getColor()
        if not color.isValid(): return
        
        if target == "background":
            self.apply_cell_property(Qt.ItemDataRole.BackgroundRole, color, "Set Background Color")
        elif target == "text":
            self.apply_cell_property(Qt.ItemDataRole.ForegroundRole, color, "Set Text Color")
