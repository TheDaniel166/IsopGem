from PyQt5.QtWidgets import QAction


class GematriaActions:
    def __init__(self, main_window):
        self.main_window = main_window
        self.panel_manager = main_window.panel_manager
        self.gematria_tab = main_window.ribbon.gematria_tab
    
    def connect_actions(self):
        # Connect ribbon buttons to panel creation
        self.gematria_tab.calc_button.clicked.connect(
            lambda: self.panel_manager.create_panel('Calculator', 'calculator'))
        self.gematria_tab.history_button.clicked.connect(
            lambda: self.panel_manager.create_panel('History', 'history'))
        self.gematria_tab.reverse_button.clicked.connect(
            lambda: self.panel_manager.create_panel('Reverse Calculate', 'reverse'))
        self.gematria_tab.suggestions_button.clicked.connect(
            lambda: self.panel_manager.create_panel('Phrase Suggestions', 'suggestions'))
        self.gematria_tab.search_button.clicked.connect(
            lambda: self.panel_manager.create_panel('Search', 'search'))
        self.gematria_tab.saved_button.clicked.connect(
            lambda: self.panel_manager.create_panel('Saved', 'saved'))
        self.gematria_tab.text_analysis_button.clicked.connect(
            lambda: self.panel_manager.create_panel('Text Analysis', 'text_analysis'))
