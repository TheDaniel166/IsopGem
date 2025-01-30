import sys
import os
import math
from unittest.mock import MagicMock

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock Gematria panels
gematria_panels = [
    'ui.workspace.gematria.calculator_panel',
    'ui.workspace.gematria.text_analysis_panel',
    'ui.workspace.gematria.history_panel',
    'ui.workspace.gematria.reverse_panel',
    'ui.workspace.gematria.suggestions_panel',
    'ui.workspace.gematria.saved_panel',
    'ui.workspace.gematria.search_results_panel',
    'ui.workspace.gematria.analysis_results_panel',
    'ui.workspace.gematria.create_cipher_panel',
    'ui.workspace.document_manager.categories.category_panel'
]

for module in gematria_panels:
    sys.modules[module] = MagicMock()

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from main_window import MainWindow

def test_centered_polygon_visualization():
    """Test centered polygon visualization point counts and layout"""
    
    app = QApplication(sys.argv)
    main_window = MainWindow()
    quadset_panel = main_window.panel_manager._create_panel_content("quadset_analysis")

    # Test 12-sided centered polygon sequence
    sequence_tests = {
        # position: (total_points, points_per_layer)
        1: (13, [1, 12]),
        2: (37, [1, 12, 24]),
        3: (73, [1, 12, 24, 36]),
        4: (121, [1, 12, 24, 36, 48])
    }

    for position, (expected_total, layers) in sequence_tests.items():
        print(f"\nTesting 12-sided centered polygon position {position}")
        
        quadset_panel.show_geometry_visualization(
            "Centered Polygonal",
            f"centered 12-gonal(n={position})"
        )
        
        window = next(iter(main_window.auxiliary_window_manager.windows.values()))
        content = window.widget()
        
        # Count points by layer
        points_by_layer = []
        margin = 1  # Allow small margin for float comparison
        
        for layer_index in range(position + 1):
            layer_points = 0
            radius = layer_index * content.radius_step
            
            for item in content.scene.items():
                if type(item).__name__ == 'QGraphicsEllipseItem':
                    center = item.rect().center()
                    point_radius = (center.x()**2 + center.y()**2)**0.5
                    if abs(point_radius - radius) <= margin:
                        layer_points += 1
            
            points_by_layer.append(layer_points)
            print(f"Layer {layer_index}: {layer_points} points")
        
        # Verify counts
        assert points_by_layer == layers, \
            f"Wrong points per layer: got {points_by_layer}, expected {layers}"
        
        main_window.auxiliary_window_manager.close_all_windows()

    main_window.close()

if __name__ == '__main__':
    test_centered_polygon_visualization() 