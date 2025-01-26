from PyQt5.QtWidgets import QDockWidget, QSizePolicy
from PyQt5.QtCore import Qt, QSettings, QSize

from .gematria.text_analysis_panel import TextAnalysisPanel
from .gematria.calculator_panel import CalculatorPanel
from .gematria.history_panel import HistoryPanel
from .gematria.reverse_panel import ReversePanel
from .gematria.suggestions_panel import SuggestionsPanel
from .gematria.search_panel import SearchPanel
from .gematria.saved_panel import SavedPanel

class PanelManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.settings = QSettings('Sourcegraph', 'IsopGem')
        self.panels = {}
        self.panel_positions = {}
        self.panel_counters = {}
        self.default_size = QSize(400, 300)
        self.min_size = QSize(200, 100)
        self.max_size = QSize(1920, 1080)

    def create_panel(self, name, panel_type):
        panel = self._create_new_panel(name, panel_type)
        if panel:
            panel_id = f"{panel_type}_{len(self.panels)}"
            self.panels[panel_id] = panel
            self._position_panel(panel, panel_id)
            panel.show()
            panel.raise_()
            return panel

    def _create_new_panel(self, name, panel_type):
        dock = QDockWidget(name, self.main_window)
        dock.setFeatures(
            QDockWidget.DockWidgetClosable |
            QDockWidget.DockWidgetMovable
        )
        
        # Prevent docking behavior
        dock.setAllowedAreas(Qt.NoDockWidgetArea)
        dock.setTitleBarWidget(dock.titleBarWidget())
        
        # Set size constraints
        dock.setMinimumSize(self.min_size)
        dock.setMaximumSize(self.max_size)
        dock.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        content = self._create_panel_content(panel_type)
        if content:
            dock.setWidget(content)
            dock.setFloating(True)
            dock.resize(self.default_size)
            return dock
        return None

    def _create_panel_content(self, panel_type):
        panel_classes = {
            'calculator': CalculatorPanel,
            'history': HistoryPanel,
            'reverse': ReversePanel,
            'suggestions': SuggestionsPanel,
            'search': SearchPanel,
            'saved': SavedPanel,
            'text_analysis': TextAnalysisPanel
        }
        return panel_classes[panel_type]() if panel_type in panel_classes else None

    def _position_panel(self, panel, panel_type):
        x_offset = 20 * len(self.panels)
        y_offset = 20 * len(self.panels)
        base_x = 200
        base_y = 200
        
        panel.move(base_x + x_offset, base_y + y_offset)
        self.panel_positions[panel_type] = (base_x + x_offset, base_y + y_offset)

    def save_layout(self):
        for panel_type, panel in self.panels.items():
            self.settings.setValue(f'panel_{panel_type}_pos', panel.pos())
            self.settings.setValue(f'panel_{panel_type}_visible', panel.isVisible())
            self.settings.setValue(f'panel_{panel_type}_size', panel.size())

    def restore_layout(self):
        for panel_type, panel in self.panels.items():
            pos = self.settings.value(f'panel_{panel_type}_pos')
            size = self.settings.value(f'panel_{panel_type}_size')
            visible = self.settings.value(f'panel_{panel_type}_visible', False)
            
            if pos:
                panel.move(pos)
            if size:
                panel.resize(size)
            panel.setVisible(visible)

    def close_all_panels(self):
        for panel in self.panels.values():
            panel.close()

    def show_all_panels(self):
        for panel in self.panels.values():
            panel.show()
            panel.raise_()
