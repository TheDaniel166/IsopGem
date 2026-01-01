"""Navigation Signal Bus for decoupled window launching.

This module provides a centralized signal bus that allows any pillar to
request the opening of any other window WITHOUT importing the target
window class directly. This prevents sovereignty violations.

Usage:
    # In any UI file (no pillar imports needed):
    from shared.signals import navigation_bus
    
    # Request a window by key - WindowManager handles the actual import
    navigation_bus.request_window.emit("quadset_analysis", {"initial_value": 42})

The WindowManager subscribes to this bus and performs lazy imports based
on the window_key, preserving pillar sovereignty.
"""
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Dict, Any


class NavigationBus(QObject):
    """
    PyQt Signal Bus for cross-pillar window navigation.
    
    Signals:
        request_window: Emitted when a window should be opened.
            Args:
                window_key (str): Identifier for the window type
                params (dict): Parameters to pass to the window
    """
    
    # Signal: (window_key: str, params: Dict[str, Any])
    request_window = pyqtSignal(str, dict)
    
    # Signal for returning data from opened window to requestor
    # (request_id: str, window_key: str, data: Any)
    window_response = pyqtSignal(str, str, object)
    
    # Signal: (key_id: int, word: str)
    # Broadcast when a lexicon key is updated (enriched, added, etc.)
    lexicon_updated = pyqtSignal(int, str)
    
    def __init__(self):
        """
          init   logic.
        
        """
        super().__init__()
        self._handlers: Dict[str, callable] = {}
    
    def emit_navigation(self, window_key: str, params: Dict[str, Any] = None):
        """
        Convenience method to request a window.
        
        Args:
            window_key: Identifier for the target window
            params: Optional parameters for the window
        """
        self.request_window.emit(window_key, params or {})


# Global singleton instance
# All pillars import this same instance
navigation_bus = NavigationBus()


# Window registry - maps window keys to lazy import info
# This avoids importing actual window classes until needed
WINDOW_REGISTRY: Dict[str, Dict[str, Any]] = {
    # Gematria Pillar
    "gematria_calculator": {
        "module": "pillars.gematria.ui.gematria_calculator_window",
        "class": "GematriaCalculatorWindow",
        "allow_multiple": True,
    },
    "saved_calculations": {
        "module": "pillars.gematria.ui.saved_calculations_window",
        "class": "SavedCalculationsWindow",
        "allow_multiple": False,
    },
    "batch_calculator": {
        "module": "pillars.gematria.ui.batch_calculator_window",
        "class": "GreatHarvestWindow",
        "allow_multiple": True,
    },
    "els_search": {
        "module": "pillars.gematria.ui.els_search_window",
        "class": "ELSSearchWindow",
        "allow_multiple": True,
    },
    "chain_results": {
        "module": "pillars.gematria.ui.chain_results_window",
        "class": "ChainResultsWindow",
        "allow_multiple": True,
    },
    "acrostics": {
        "module": "pillars.gematria.ui.acrostics_window",
        "class": "AcrosticsWindow",
        "allow_multiple": True,
    },
    "chiastic": {
        "module": "pillars.gematria.ui.chiastic_window",
        "class": "ChiasticWindow",
        "allow_multiple": True,
    },
    "text_analysis": {
        "module": "pillars.gematria.ui.text_analysis.main_window",
        "class": "ExegesisWindow",
        "allow_multiple": True,
    },
    "holy_book_teacher": {
        "module": "pillars.gematria.ui.holy_book_teacher_window",
        "class": "HolyBookTeacherWindow",
        "allow_multiple": True,
    },
    
    # TQ Pillar
    "quadset_analysis": {
        "module": "pillars.tq.ui.quadset_analysis_window",
        "class": "QuadsetAnalysisWindow",
        "allow_multiple": True,
    },
    "geometric_transitions": {
        "module": "pillars.tq.ui.geometric_transitions_window",
        "class": "GeometricTransitionsWindow",
        "allow_multiple": True,
    },
    "geometric_transitions_3d": {
        "module": "pillars.tq.ui.geometric_transitions_3d_window",
        "class": "GeometricTransitions3DWindow",
        "allow_multiple": True,
    },
    "conrune_pair_finder": {
        "module": "pillars.tq.ui.conrune_pair_finder_window",
        "class": "ConrunePairFinderWindow",
        "allow_multiple": True,
    },
    "transitions": {
        "module": "pillars.tq.ui.transitions_window",
        "class": "TransitionsWindow",
        "allow_multiple": True,
    },
    
    # Correspondences Pillar
    "emerald_tablet": {
        "module": "pillars.correspondences.ui.correspondence_hub",
        "class": "CorrespondenceHub",
        "allow_multiple": False,
    },
    "spreadsheet": {
        "module": "pillars.correspondences.ui.spreadsheet_view",
        "class": "SpreadsheetView",
        "allow_multiple": True,
    },
    
    # Document Manager Pillar
    "document_editor": {
        "module": "pillars.document_manager.ui.document_editor_window",
        "class": "DocumentEditorWindow",
        "allow_multiple": True,
    },
    "mindscape": {
        "module": "pillars.document_manager.ui.mindscape_window",
        "class": "MindscapeWindow",
        "allow_multiple": False,
    },
    "akaschic_record": {
        "module": "pillars.document_manager.ui.document_library",
        "class": "DocumentLibrary",
        "allow_multiple": False,
    },
    
    # Geometry Pillar
    "geometry_hub": {
        "module": "pillars.geometry.ui.geometry_hub",
        "class": "GeometryHub",
        "allow_multiple": False,
    },
    "geometry_3d": {
        "module": "pillars.geometry.ui.geometry3d.window3d",
        "class": "Geometry3DWindow",
        "allow_multiple": True,
    },
    "figurate_3d": {
        "module": "pillars.geometry.ui.figurate_3d_window",
        "class": "Figurate3DWindow",
        "allow_multiple": True,
    },
    "polygonal_number": {
        "module": "pillars.geometry.ui.polygonal_number_window",
        "class": "PolygonalNumberWindow",
        "allow_multiple": True,
    },
    
    # Astrology Pillar
    "differential_natal": {
        "module": "pillars.astrology.ui.differential_natal_window",
        "class": "DifferentialNatalWindow",
        "allow_multiple": True,
    },
    
    # Time Mechanics Pillar
    "zodiacal_circle": {
        "module": "pillars.time_mechanics.ui.zodiacal_circle_window",
        "class": "ZodiacalCircleWindow",
        "allow_multiple": True,
    },
    
    # Holy Key Pillar (Unified Window - sovereign interface)
    "lexicon_manager": {
        "module": "pillars.tq_lexicon.ui.unified_lexicon_window",
        "class": "UnifiedLexiconWindow",
        "allow_multiple": False,
    },
}


def get_window_info(window_key: str) -> Dict[str, Any]:
    """
    Get registration info for a window key.
    
    Args:
        window_key: The window identifier
        
    Returns:
        Dictionary with module, class, and allow_multiple settings
        
    Raises:
        KeyError: If window_key is not registered
    """
    if window_key not in WINDOW_REGISTRY:
        raise KeyError(f"Unknown window key: {window_key}. "
                      f"Available keys: {list(WINDOW_REGISTRY.keys())}")
    return WINDOW_REGISTRY[window_key]