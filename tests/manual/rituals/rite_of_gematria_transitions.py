# Mocking everything heavy before any imports
import sys
from unittest.mock import MagicMock

# Create a list of all potentially problematic modules
mocks = [
    'shared.database',
    'pillars.gematria.services',
    'pillars.gematria.models',
    'pillars.gematria.services.calculation_service',
    'pillars.correspondences.ui.correspondence_hub',
    'pillars.tq.ui.quadset_analysis_window',
    'pillars.document_manager.ui.document_editor_window',
    'pillars.document_manager.ui.mindscape_window',
    'pillars.document_manager.services.notebook_service',
    'pillars.document_manager.ui.mindscape_page',
    'shared.ui',
]

for m in mocks:
    sys.modules[m] = MagicMock()

# Now we can safely import just the window
# We need to ensure the parent modules are available
from src.pillars.gematria.ui.gematria_calculator_window import GematriaCalculatorWindow

def verify_presence():
    # We don't even need QApplication if we don't instantiate
    # But let's check the attributes on the class level or a dummy instance
    
    # Check if methods are defined in the class
    methods = [
        '_on_total_context_menu',
        '_send_to_quadset',
        '_send_to_rtf_editor',
        '_ms_insert_current',
        '_ms_insert_existing',
        '_ms_create_page',
        '_ms_new_notebook',
        '_ms_new_section',
        '_ms_add_note'
    ]
    
    missing = []
    for m in methods:
        if not hasattr(GematriaCalculatorWindow, m):
            missing.append(m)
            
    if missing:
        print(f"FAILED: Missing methods: {missing}")
        sys.exit(1)
    else:
        print("SUCCESS: All transition methods are present in GematriaCalculatorWindow.")

if __name__ == "__main__":
    verify_presence()
