from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QGridLayout, QScrollArea, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QFont, QColor

class SpiritTile(QFrame):
    """A tile representing a single character and its numeric value."""
    
    def __init__(self, char: str, value: int, parent=None):
        super().__init__(parent)
        self.char = char
        self.value = value
        self._setup_ui()
        
    def _setup_ui(self):
        self.setFixedSize(75, 100)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("""
            SpiritTile {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
            SpiritTile:hover {
                border: 2px solid #3b82f6;
                background-color: #ffffff;
            }
        """)
        
        # Add a subtle shadow that grows on hover if we want to be fancy, 
        # but for now let's just make the shadow blue-ish on hover.
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(4)
        self.shadow.setColor(QColor(0, 0, 0, 25))
        self.setGraphicsEffect(self.shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 12, 5, 12)
        layout.setSpacing(2)
        
        char_label = QLabel(self.char)
        char_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        char_label.setStyleSheet("""
            font-size: 24pt; 
            font-weight: 800; 
            color: #1e293b;
            font-family: 'Inter', 'Segoe UI', sans-serif;
        """)
        layout.addWidget(char_label)
        
        value_label = QLabel(str(self.value))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("""
            font-size: 10pt; 
            color: #64748b; 
            font-weight: 700;
            letter-spacing: 0.05em;
        """)
        layout.addWidget(value_label)

class TotalValueCard(QFrame):
    """A prominent card displaying the total numeric value."""
    
    def __init__(self, value: int, system_name: str = "", parent=None):
        super().__init__(parent)
        self.value = value
        self.system_name = system_name
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._setup_ui()
        
    def _setup_ui(self):
        self.setMinimumHeight(160)
        self.setObjectName("TotalValueCard")
        self.setStyleSheet("""
            QFrame#TotalValueCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #1e293b, stop:1 #0f172a);
                border: 1px solid #334155;
                border-radius: 20px;
            }
        """)
        
        # Add a rich shadow for a floating effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(15, 23, 42, 100))
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(0)
        
        if self.system_name:
            sys_label = QLabel(self.system_name.upper())
            sys_label.setStyleSheet("""
                color: #94a3b8; 
                font-size: 11pt; 
                font-weight: 800; 
                letter-spacing: 0.2em;
            """)
            sys_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(sys_label)
        
        value_label = QLabel(str(self.value))
        value_label.setStyleSheet("""
            color: #fbbf24; 
            font-size: 56pt; 
            font-weight: 900; 
            font-family: 'Inter', sans-serif;
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        title_label = QLabel("TOTAL RESONANCE")
        title_label.setStyleSheet("""
            color: #475569; 
            font-size: 10pt; 
            font-weight: 700;
            letter-spacing: 0.15em;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

class ResultsDashboard(QWidget):
    """A dashboard summarizing the gematria result."""
    
    
    totalContextMenuRequested = pyqtSignal(int, QPoint)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(30)
        self.setStyleSheet("background: transparent;")
        
        # Dashboard starts empty or with a placeholder
        self.placeholder = QLabel("Calculate to see results...")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet("color: #94a3b8; font-size: 14pt; font-style: italic;")
        self.layout.addWidget(self.placeholder)
        
    def clear(self):
        """Clear the dashboard and show the placeholder."""
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.placeholder = QLabel("Calculate to see results...")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet("color: #94a3b8; font-size: 14pt; font-style: italic;")
        self.layout.addWidget(self.placeholder)

    def display_results(self, text: str, total: int, system_name: str, breakdown: list):
        """Update the dashboard with new results."""
        # Clear layout
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Header for the text
        text_label = QLabel(f'"{text}"')
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet("font-size: 16pt; font-weight: 600; color: #334155; margin-bottom: 5px;")
        self.layout.addWidget(text_label)
        
        # Total Value Card
        val_card = TotalValueCard(total, system_name)
        val_card.customContextMenuRequested.connect(
            lambda pos: self.totalContextMenuRequested.emit(total, val_card.mapToGlobal(pos))
        )
        self.layout.addWidget(val_card)
        
        # Breakdown section
        if breakdown:
            breakdown_label = QLabel("CHARACTER BREAKDOWN")
            breakdown_label.setStyleSheet("color: #64748b; font-size: 10pt; font-weight: 700; letter-spacing: 0.1em; margin-top: 10px;")
            self.layout.addWidget(breakdown_label)
            
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.setStyleSheet("background-color: transparent;")
            
            grid_widget = QWidget()
            grid_widget.setStyleSheet("background-color: transparent;")
            grid_layout = QGridLayout(grid_widget)
            grid_layout.setSpacing(12)
            grid_layout.setContentsMargins(0, 5, 0, 5)
            
            cols = 8 # items per row
            for i, (char, val) in enumerate(breakdown):
                tile = SpiritTile(char, val)
                grid_layout.addWidget(tile, i // cols, i % cols)
            
            from PyQt6.QtWidgets import QSpacerItem, QSizePolicy
            grid_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), (len(breakdown) // cols) + 1, 0)
            
            scroll.setWidget(grid_widget)
            self.layout.addWidget(scroll, 1) # Give breakdown the stretch priority
        
        self.layout.addStretch(0)

    def display_comparison(self, text: str, language: str, rows: list):
        """Update the dashboard with comparison results."""
        # Clear layout
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Header for the text
        text_label = QLabel(f'"{text}" ({language})')
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet("font-size: 16pt; font-weight: 600; color: #334155; margin-bottom: 5px;")
        self.layout.addWidget(text_label)
        
        comparison_label = QLabel("ALL METHODS COMPARISON")
        comparison_label.setStyleSheet("color: #64748b; font-size: 10pt; font-weight: 700; letter-spacing: 0.1em; margin-top: 10px;")
        self.layout.addWidget(comparison_label)
        
        # Simple table implementation using a grid or a dedicated widget
        table_container = QFrame()
        table_container.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 12px;")
        t_layout = QVBoxLayout(table_container)
        t_layout.setContentsMargins(15, 15, 15, 15)
        t_layout.setSpacing(8)
        
        # Header Row
        h_layout = QHBoxLayout()
        h_method = QLabel("METHOD")
        h_method.setStyleSheet("font-weight: 700; color: #475569; font-size: 9pt;")
        h_value = QLabel("VALUE")
        h_value.setStyleSheet("font-weight: 700; color: #475569; font-size: 9pt;")
        h_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        h_layout.addWidget(h_method)
        h_layout.addWidget(h_value)
        t_layout.addLayout(h_layout)
        
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #f1f5f9;")
        t_layout.addWidget(line)
        
        for method, value in rows:
            r_layout = QHBoxLayout()
            m_label = QLabel(method)
            m_label.setStyleSheet("color: #1e293b; font-size: 11pt; font-weight: 500;")
            v_label = QLabel(str(value))
            v_label.setStyleSheet("color: #2563eb; font-size: 11pt; font-weight: 700; font-family: 'Courier New';")
            v_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            r_layout.addWidget(m_label)
            r_layout.addWidget(v_label)
            t_layout.addLayout(r_layout)
            
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(table_container)
        
        self.layout.addWidget(scroll, 1)
        self.layout.addStretch(0)
