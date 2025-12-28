"""Window for the Chiastic TQ Finder tool."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTextEdit, QPushButton, QSpinBox, QListWidget, 
                             QListWidgetItem, QSplitter, QFrame, QComboBox)
from PyQt6.QtCore import Qt
from pillars.gematria.services.chiasmus_service import ChiasmusService
from pillars.gematria.services.tq_calculator import TQGematriaCalculator
from pillars.gematria.services.hebrew_calculator import HebrewGematriaCalculator, HebrewOrdinalCalculator
from pillars.gematria.services.greek_calculator import GreekGematriaCalculator

class ChiasticWindow(QWidget):
    def __init__(self, window_manager=None, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Chiastic TQ Finder")
        self.resize(1000, 700)
        
        self.service = ChiasmusService()
        self.patterns = []
        
        # Available calculators
        self.calculators = {
            "English TQ": TQGematriaCalculator(),
            "Hebrew Standard": HebrewGematriaCalculator(),
            "Hebrew Ordinal": HebrewOrdinalCalculator(),
            "Greek Isopsephy": GreekGematriaCalculator()
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # --- Top Controls ---
        controls = QHBoxLayout()
        
        # Cipher Selection
        controls.addWidget(QLabel("Cipher:"))
        self.cipher_combo = QComboBox()
        self.cipher_combo.addItems(list(self.calculators.keys()))
        controls.addWidget(self.cipher_combo)
        
        controls.addWidget(QLabel("Minimum Depth:"))
        self.spin_depth = QSpinBox()
        self.spin_depth.setRange(1, 10)
        self.spin_depth.setValue(2) # Default A-B-C-B-A
        self.spin_depth.setToolTip("How many mirrored layers required (e.g. 2 = A-B...B-A)")
        controls.addWidget(self.spin_depth)
        
        self.btn_scan = QPushButton("⚖️ Scan for Patterns")
        self.btn_scan.clicked.connect(self.scan_text)
        controls.addWidget(self.btn_scan)
        
        controls.addStretch()
        main_layout.addLayout(controls)
        
        # --- Splitter Content ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Input & List
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0,0,0,0)
        
        left_layout.addWidget(QLabel("Input Text:"))
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Paste text or load document...")
        left_layout.addWidget(self.input_text)
        
        # Load Document Button
        self.btn_load_doc = QPushButton("📂 Load Document")
        self.btn_load_doc.clicked.connect(self.load_document_dialog)
        left_layout.addWidget(self.btn_load_doc)
        
        left_layout.addWidget(QLabel("Found Patterns:"))
        self.pattern_list = QListWidget()
        self.pattern_list.currentRowChanged.connect(self.display_pattern)
        left_layout.addWidget(self.pattern_list)
        
        splitter.addWidget(left_widget)
        
        # Right: Visualization
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0,0,0,0)
        
        right_layout.addWidget(QLabel("Visualization (Mirror Structure):"))
        self.viz_display = QTextEdit()
        self.viz_display.setReadOnly(True)
        # Set styling for visualization
        self.viz_display.setStyleSheet("QTextEdit { font-family: 'Courier New'; font-size: 14pt; }")
        right_layout.addWidget(self.viz_display)
        
        splitter.addWidget(right_widget)
        
        # Set initial sizes
        splitter.setSizes([400, 600])
        
        main_layout.addWidget(splitter)

    def load_document_dialog(self):
        from pillars.gematria.ui.document_selector import DocumentSelectorDialog
        dialog = DocumentSelectorDialog(self)
        if dialog.exec():
            doc_id = dialog.get_selected_doc_id()
            if doc_id:
                self.load_document_text(doc_id)

    def load_document_text(self, doc_id):
        from shared.repositories.document_manager.document_repository import DocumentRepository
        from shared.database import get_db
        from PyQt6.QtWidgets import QMessageBox
        
        try:
            db = next(get_db())
            repo = DocumentRepository(db)
            doc = repo.get(doc_id)
            if doc and doc.content:
                self.input_text.setText(doc.content)
            else:
                QMessageBox.warning(self, "Warning", "Document has no content.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load document: {str(e)}")

    def scan_text(self):
        text = self.input_text.toPlainText()
        if not text:
            return
            
        depth = self.spin_depth.value()
        
        cipher_name = self.cipher_combo.currentText()
        calculator = self.calculators.get(cipher_name)
        
        if not calculator:
            return
            
        self.patterns = self.service.scan_text(text, calculator, depth)
        
        self.pattern_list.clear()
        self.viz_display.clear()
        
        if not self.patterns:
            self.pattern_list.addItem("No patterns found.")
            return
            
        for i, p in enumerate(self.patterns):
            # Create a label for the list
            # "Depth 3: Word...Word"
            center_word = p.source_units[len(p.left_indices)] if p.center_index is not None else "[Mirror]"
            label = f"Depth {p.depth} | Center: {center_word}"
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.pattern_list.addItem(item)
            
    def display_pattern(self, row):
        if row < 0 or row >= len(self.patterns):
            self.viz_display.clear()
            return
            
        pat = self.patterns[row]
        html = self.generate_viz_html(pat)
        self.viz_display.setHtml(html)
        
    def generate_viz_html(self, p) -> str:
        """Generates V-shape or Mirror HTML."""
        lines = []
        
        # Colors for layers
        colors = ["#FF5555", "#55FF55", "#5555FF", "#FFFF55", "#FF55FF", "#55FFFF"]
        
        # A, B, C... 
        # Left side (Outer to Inner)
        indent = 0
        for i in range(len(p.left_indices)):
            color = colors[i % len(colors)]
            word = p.source_units[i]
            val = p.values[i]
            
            # Non-breaking spaces for indent
            spaces = "&nbsp;" * (indent * 4)
            line = f"{spaces}<span style='color:{color}'><b>{word}</b> ({val})</span>"
            lines.append(line)
            indent += 1
            
        # Center
        if p.center_index is not None:
            # Odd length
            center_idx_in_units = len(p.left_indices)
            word = p.source_units[center_idx_in_units]
            val = p.values[center_idx_in_units]
            spaces = "&nbsp;" * (indent * 4)
            line = f"{spaces}<span style='color:white; background-color: #333'><b>{word}</b> ({val})</span>"
            lines.append(line)
        else:
            # Even length - explicit mirror line?
            spaces = "&nbsp;" * (indent * 4)
            lines.append(f"{spaces}======= MIRROR =======")
            indent -= 1 # Step back for the first right element matching the last left
            
        # Right side (Inner to Outer)
        # The source_units list is flat from left to right.
        # But for V-shape, we want to start from the logical "Inner" and go back out?
        # Usually Chiasmus visualization mirrors the top.
        # Top: A
        #      B
        #        Center
        #      B'
        #    A'
        
        # So we need to iterate backwards through right side layers?
        # Right indices in `p` are Outer->Inner order? 
        # No, my logic in service: 
        # `left_idxs` = Outer->Inner.
        # `right_idxs` = Outer->Inner.
        
        # But we want to print the Right side starting from Inner (closest to center) going to Outer.
        # So we reverse `right_indices` (or `p.values` corresponding part) for the print order.
        
        # Let's look at `p.source_units`. It is constructed as `left + center + reversed(right)`.
        # So it is in reading order (A_l, B_l, ... Center ... B_r, A_r).
        
        # Left side printed: 0 to len(left)-1.
        # Center printed.
        # Right side starts at: len(left) + (1 if center else 0).
        start_right = len(p.left_indices) + (1 if p.center_index is not None else 0)
        
        # We want to traverse this remainder of the list.
        # The remainder equates to B_r, A_r (Inner -> Outer).
        # So we can just iterate the remainder of `p.source_units`.
        
        right_units = p.source_units[start_right:]
        right_values = p.values[start_right:]
        
        # Calculate indentation for right side.
        # If odd center, indent was `len(left)`. We start unwinding.
        # If even, we already decremented.
        
        # Actually, if we had A, B, C (indent 0, 1, 2).
        # Center C matches nothing.
        # Then B' (indent 1), A' (indent 0).
        
        if p.center_index is not None:
             indent -= 1
             
        # Iterate right units
        for i, word in enumerate(right_units):
            # Color should match the corresponding left layer.
            # We are going Inner -> Outer.
            # Inner-most layer index is `len(left) - 1`.
            # i=0 (first right unit) corresponds to layer index `len(left) - 1`.
            # i=1 corresponds to `len(left) - 2`.
            
            layer_idx = (len(p.left_indices) - 1) - i
            if layer_idx < 0: layer_idx = 0 # Safety
            
            color = colors[layer_idx % len(colors)]
            val = right_values[i]
            
            spaces = "&nbsp;" * (indent * 4)
            line = f"{spaces}<span style='color:{color}'><b>{word}</b> ({val})</span>"
            lines.append(line)
            indent -= 1
            
        return "<br>".join(lines)
