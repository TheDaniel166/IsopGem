from PySide6.QtWidgets import (QWidget, QHBoxLayout, QGroupBox, 
                              QVBoxLayout, QPushButton)

class GematriaTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        
        # Word/Phrase Calculator group
        calc_group = QGroupBox("Word/Phrase Calculator")
        calc_layout = QVBoxLayout()
        calc_group.setLayout(calc_layout)
        
        # Store button references
        self.calc_button = QPushButton("Calculate Value")
        self.breakdown_button = QPushButton("Word Breakdown")
        self.reverse_button = QPushButton("Reverse Calculate")
        self.suggest_button = QPushButton("Phrase Suggestions")
        
        calc_layout.addWidget(self.calc_button)
        calc_layout.addWidget(self.breakdown_button)
        calc_layout.addWidget(self.reverse_button)
        calc_layout.addWidget(self.suggest_button)
        
        # Number Search group
        search_group = QGroupBox("Number Search")
        search_layout = QVBoxLayout()
        search_group.setLayout(search_layout)
        
        self.value_search_button = QPushButton("Value Search")
        self.pattern_search_button = QPushButton("Pattern Search")
        self.relation_button = QPushButton("Relationship Finder")
        
        search_layout.addWidget(self.value_search_button)
        search_layout.addWidget(self.pattern_search_button)
        search_layout.addWidget(self.relation_button)
        
        # Custom Cipher group
        cipher_group = QGroupBox("Custom Cipher")
        cipher_layout = QVBoxLayout()
        cipher_group.setLayout(cipher_layout)
        
        self.create_cipher_button = QPushButton("Create Cipher")
        self.edit_cipher_button = QPushButton("Edit Cipher")
        self.import_export_button = QPushButton("Import/Export")
        
        cipher_layout.addWidget(self.create_cipher_button)
        cipher_layout.addWidget(self.edit_cipher_button)
        cipher_layout.addWidget(self.import_export_button)
        
        # Text Analysis group
        analysis_group = QGroupBox("Text Analysis")
        analysis_layout = QVBoxLayout()
        analysis_group.setLayout(analysis_layout)
        
        self.grid_button = QPushButton("Grid Placement")
        self.els_button = QPushButton("ELS Tools")
        self.heatmap_button = QPushButton("Heat Maps")
        
        analysis_layout.addWidget(self.grid_button)
        analysis_layout.addWidget(self.els_button)
        analysis_layout.addWidget(self.heatmap_button)
        
        # Add all groups to layout
        layout.addWidget(calc_group)
        layout.addWidget(search_group)
        layout.addWidget(cipher_group)
        layout.addWidget(analysis_group)
        self.setLayout(layout)
