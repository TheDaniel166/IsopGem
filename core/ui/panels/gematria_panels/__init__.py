"""
Gematria panel implementations
"""
from ..registry import get_registry
from databases.gematria.word_repository import WordRepository
import os

# Import panel classes
from .calculator_panel import CalculatorPanel
from .history_panel import HistoryPanel
from .reverse_panel import ReversePanel
from .suggestions_panel import SuggestionsPanel
from .saved_panel import SavedPanel
from .text_analysis_panel import TextAnalysisPanel
from .grid_analysis_panel import GridAnalysisPanel
from .create_cipher_panel import CreateCipherPanel

# Register panel factories
registry = get_registry()
registry.register("calculator", lambda: CalculatorPanel())
registry.register("history", lambda: HistoryPanel())
registry.register("reverse", lambda: ReversePanel())
registry.register("suggestions", lambda: SuggestionsPanel())

# Use a factory function that ensures proper initialization
def create_saved_panel():
    repo = WordRepository()
    panel = SavedPanel(word_repository=repo)
    return panel

registry.register("saved", create_saved_panel)
registry.register("text_analysis", lambda: TextAnalysisPanel())
registry.register("grid_analysis", lambda: GridAnalysisPanel())
registry.register("create_cipher", lambda: CreateCipherPanel())

__all__ = [
    'CalculatorPanel',
    'HistoryPanel',
    'ReversePanel',
    'SuggestionsPanel',
    'SavedPanel',
    'TextAnalysisPanel',
    'GridAnalysisPanel',
    'CreateCipherPanel'
]
