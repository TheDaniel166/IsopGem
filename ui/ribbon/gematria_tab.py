from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QGroupBox, QPushButton)

class GematriaTab(QWidget):
    def __init__(self, panel_manager):
        super().__init__()
        self.panel_manager = panel_manager
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        
        # Word/Phrase group
        word_group = QGroupBox("Word/Phrase")
        word_layout = QHBoxLayout()
        
        self.calc_button = QPushButton("Calculate")
        self.calc_button.clicked.connect(
            lambda: self.panel_manager.create_panel('calculator'))
            
        self.history_button = QPushButton("History")
        self.history_button.clicked.connect(
            lambda: self.panel_manager.create_panel('history'))
            
        self.reverse_button = QPushButton("Reverse Calculate")
        self.reverse_button.clicked.connect(
            lambda: self.panel_manager.create_panel('reverse'))
            
        self.suggestions_button = QPushButton("Phrase Suggestions")
        self.suggestions_button.clicked.connect(
            lambda: self.panel_manager.create_panel('suggestions'))
        
        word_layout.addWidget(self.calc_button)
        word_layout.addWidget(self.history_button)
        word_layout.addWidget(self.reverse_button)
        word_layout.addWidget(self.suggestions_button)
        
        word_group.setLayout(word_layout)
        
        # Number Search group
        number_group = QGroupBox("Number Search")
        number_layout = QHBoxLayout()
        
        self.saved_button = QPushButton("Saved")
        self.saved_button.clicked.connect(
            lambda: self.panel_manager.create_panel('saved'))
            
        self.text_analysis_button = QPushButton("Text Analysis")
        self.text_analysis_button.clicked.connect(
            lambda: self.panel_manager.create_panel('text_analysis'))
        
        number_layout.addWidget(self.saved_button)
        number_layout.addWidget(self.text_analysis_button)
        
        number_group.setLayout(number_layout)
        
        # Extra group
        extra_group = QGroupBox("Extra")
        extra_layout = QHBoxLayout()
        
        self.grid_analysis_button = QPushButton("Grid Analysis")
        self.grid_analysis_button.clicked.connect(
            lambda: self.panel_manager.create_panel('grid_analysis'))
            
        self.create_cipher_button = QPushButton("Create Cipher")
        self.create_cipher_button.clicked.connect(
            lambda: self.panel_manager.create_panel('create_cipher'))
            
        extra_layout.addWidget(self.grid_analysis_button)
        extra_layout.addWidget(self.create_cipher_button)
        
        extra_group.setLayout(extra_layout)
        
        # Add groups to main layout
        layout.addWidget(word_group)
        layout.addWidget(number_group)
        layout.addWidget(extra_group)
        layout.addStretch()
        
        self.setLayout(layout)