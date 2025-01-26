from PyQt5.QtWidgets import (QTabWidget, QWidget, QHBoxLayout,
                            QGroupBox, QPushButton)
from .file_tab import FileTab
from .home_tab import HomeTab

class RibbonWidget(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setTabPosition(QTabWidget.North)
        self.init_ui()

    def init_ui(self):
        # Create and store tab references
        self.file_tab = FileTab()
        self.home_tab = HomeTab()
        self.gematria_tab = GematriaTab()
        
        # Add ribbon tabs
        self.addTab(self.file_tab, "File")
        self.addTab(self.home_tab, "Home")
        self.addTab(self.gematria_tab, "Gematria")

class GematriaTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        
        # Word/Phrase group
        word_group = QGroupBox("Word/Phrase")
        word_layout = QHBoxLayout()
        
        self.calc_button = QPushButton("Calculate")
        self.history_button = QPushButton("History")
        self.reverse_button = QPushButton("Reverse Calculate")
        self.suggestions_button = QPushButton("Phrase Suggestions")
        
        word_layout.addWidget(self.calc_button)
        word_layout.addWidget(self.history_button)
        word_layout.addWidget(self.reverse_button)
        word_layout.addWidget(self.suggestions_button)
        
        word_group.setLayout(word_layout)
        
        # Number Search group
        number_group = QGroupBox("Number Search")
        number_layout = QHBoxLayout()
        
        self.search_button = QPushButton("Search")
        self.saved_button = QPushButton("Saved")
        self.text_analysis_button = QPushButton("Text Analysis")
        
        number_layout.addWidget(self.search_button)
        number_layout.addWidget(self.saved_button)
        number_layout.addWidget(self.text_analysis_button)
        
        number_group.setLayout(number_layout)
        
        # Add groups to main layout
        layout.addWidget(word_group)
        layout.addWidget(number_group)
        layout.addStretch()
        
        self.setLayout(layout)
