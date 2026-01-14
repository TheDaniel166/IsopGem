"""
Feature Interface for RichTextEditor.

This protocol defines how features interact with the monolithic editor,
enabling a shift from hardcoded dependencies to dependency injection.
"""
from typing import Optional, Any, TYPE_CHECKING
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QObject

if TYPE_CHECKING:
    from .editor import RichTextEditor


class EditorFeature(QObject):
    """
    Abstract base class for RichTextEditor plugins.
    
    Features should implement this interface to be injectable into the editor.
    """
    
    def __init__(self, parent_editor: 'RichTextEditor'):
        """
        Initialize the feature with the orchestrator instance.
        
        Args:
            parent_editor: The RichTextEditor instance (orchestrator).
                           Access the raw QTextEdit via parent_editor.editor.
        """
        super().__init__(parent_editor)
        self.orchestrator = parent_editor
        self.editor = parent_editor.editor  # The actual text edit widget

    def initialize(self) -> None:
        """
        Perform post-init setup.
        
        Use this to connect signals, create internal dialogs, or register
        keyboard shortcuts. This is called after the editor is fully verified.
        """
        pass

    def extend_context_menu(self, menu: QMenu, pos: Any = None) -> None:
        """
        Add actions to the editor's context menu.
        
        Args:
            menu: The QMenu being built.
            pos: The cursor position (optional).
        """
        pass
        
    def name(self) -> str:
        """
        Return the unique identifier for this feature.
        
        Used for the internal registry (e.g. 'table_feature').
        Defaults to the class name in snake_case.
        """
        import re
        name = self.__class__.__name__
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
