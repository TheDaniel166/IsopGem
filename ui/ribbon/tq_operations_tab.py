from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QPushButton
)

class TQOperationsTab(QWidget):
    def __init__(self, panel_manager):
        super().__init__()
        self.panel_manager = panel_manager
        self.init_ui()

    def init_ui(self):
        # Main horizontal layout
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Base Operations Group
        base_group = QGroupBox("Base Operations")
        base_layout = QVBoxLayout()
        base_layout.setSpacing(2)
        base_layout.setContentsMargins(2, 2, 2, 2)
        
        quadset_btn = QPushButton("Quadset Analysis")
        quadset_btn.clicked.connect(lambda: self.panel_manager.create_panel('quadset_analysis'))
        
        converse_btn = QPushButton("Converse Analysis")
        converse_btn.clicked.connect(lambda: self.panel_manager.create_panel('converse_analysis'))
        
        base_layout.addWidget(quadset_btn)
        base_layout.addWidget(converse_btn)
        base_group.setLayout(base_layout)
        layout.addWidget(base_group)

        # Transitions Group
        transitions_group = QGroupBox("Transitions")
        transitions_layout = QVBoxLayout()
        transitions_layout.setSpacing(2)
        transitions_layout.setContentsMargins(2, 2, 2, 2)
        
        pair_btn = QPushButton("Pair Transitions")
        pair_btn.clicked.connect(lambda: self.panel_manager.create_panel('pair_transitions'))
        
        series_btn = QPushButton("Series Transitions")
        series_btn.clicked.connect(lambda: self.panel_manager.create_panel('series_transitions'))
        
        geometric_btn = QPushButton("Geometric Transitions")
        geometric_btn.clicked.connect(lambda: self.panel_manager.create_panel('geometric_transitions'))
        
        transitions_layout.addWidget(pair_btn)
        transitions_layout.addWidget(series_btn)
        transitions_layout.addWidget(geometric_btn)
        transitions_group.setLayout(transitions_layout)
        layout.addWidget(transitions_group)

        # Aeonic Timing Group
        aeonic_group = QGroupBox("Aeonic Timing")
        aeonic_layout = QVBoxLayout()
        aeonic_layout.setSpacing(2)
        aeonic_layout.setContentsMargins(2, 2, 2, 2)
        
        dance_btn = QPushButton("Dance of Days")
        dance_btn.clicked.connect(lambda: self.panel_manager.create_panel('dance_of_days'))
        
        haad_btn = QPushButton("Thelemic Haad")
        haad_btn.clicked.connect(lambda: self.panel_manager.create_panel('thelemic_haad'))
        
        heptagons_btn = QPushButton("Zodiacal Heptagons")
        heptagons_btn.clicked.connect(lambda: self.panel_manager.create_panel('zodiacal_heptagons'))
        
        aeonic_layout.addWidget(dance_btn)
        aeonic_layout.addWidget(haad_btn)
        aeonic_layout.addWidget(heptagons_btn)
        aeonic_group.setLayout(aeonic_layout)
        layout.addWidget(aeonic_group)

        # Kamea Group
        kamea_group = QGroupBox("Kamea")
        kamea_layout = QVBoxLayout()
        kamea_layout.setSpacing(2)
        kamea_layout.setContentsMargins(2, 2, 2, 2)
        
        maut_btn = QPushButton("Kamea of Ma'ut")
        maut_btn.clicked.connect(lambda: self.panel_manager.create_panel('kamea_of_maut'))
        
        bafomet_btn = QPushButton("Kamea of Bafomet")
        bafomet_btn.clicked.connect(lambda: self.panel_manager.create_panel('kamea_of_bafomet'))
        
        creator_btn = QPushButton("Kamea Creator")
        creator_btn.clicked.connect(lambda: self.panel_manager.create_panel('kamea_creator'))
        
        kamea_layout.addWidget(maut_btn)
        kamea_layout.addWidget(bafomet_btn)
        kamea_layout.addWidget(creator_btn)
        kamea_group.setLayout(kamea_layout)
        layout.addWidget(kamea_group)

        layout.addStretch()
        self.setLayout(layout) 