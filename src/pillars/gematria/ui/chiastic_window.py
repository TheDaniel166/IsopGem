"""Window for the Chiastic TQ Finder tool."""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTextEdit, QPushButton, QSpinBox, QListWidget, 
                             QListWidgetItem, QSplitter, QFrame, QComboBox, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
import logging
from pathlib import Path
from shared.ui import theme
from pillars.gematria.services.chiasmus_service import ChiasmusService
from pillars.gematria.services.tq_calculator import TQGematriaCalculator
from pillars.gematria.services.hebrew_calculator import HebrewGematriaCalculator, HebrewOrdinalCalculator
from pillars.gematria.services.greek_calculator import GreekGematriaCalculator

class ChiasticWindow(QMainWindow):
    """
    Chiastic Window class definition.
    
    Attributes:
        service: Description of service.
        patterns: Description of patterns.
        calculators: Description of calculators.
    
    """
    def __init__(self, window_manager=None, parent=None):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """
          init   logic.
        
        Args:
            window_manager: Description of window_manager.
            parent: Description of parent.
        
        """
        super().__init__(parent=parent)
        self.setWindowTitle("Chiastic TQ Finder")
        self.resize(1000, 700)
        
        # Level 0: The Ghost Layer (Nano Banana substrate)
        possible_paths = [
            Path("src/assets/patterns/chiastic_bg_pattern.png"),
            Path("src/assets/patterns/tq_bg_pattern.png"),
            Path("assets/patterns/tq_bg_pattern.png"),
        ]
        
        bg_path = None
        for p in possible_paths:
            if p.exists():
                bg_path = p
                break
        
        central = QWidget()
        central.setObjectName("CentralContainer")
        self.setCentralWidget(central)
        
        if bg_path:
            logging.debug("Found Ghost Layer pattern at: %s", bg_path)
            abs_path = bg_path.absolute().as_posix()
            central.setStyleSheet(f"""
                QWidget#CentralContainer {{
                    border-image: url("{abs_path}") 0 0 0 0 stretch stretch;
                    border: none;
                    background-color: {theme.COLORS['light']};
                }}
            """)
        else:
            logging.warning("Ghost Layer pattern not found; using fallback color")
            central.setStyleSheet(f"QWidget#CentralContainer {{ background-color: {theme.COLORS['light']}; }}")
        
        self.service = ChiasmusService()
        self.patterns = []
        
        # Status bar for feedback
        from PyQt6.QtWidgets import QStatusBar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(theme.get_status_muted_style())
        
        # Available calculators
        self.calculators = {
            "English TQ": TQGematriaCalculator(),
            "Hebrew Standard": HebrewGematriaCalculator(),
            "Hebrew Ordinal": HebrewOrdinalCalculator(),
            "Greek Isopsephy": GreekGematriaCalculator()
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """
        Setup ui logic.
        
        """
        # Main layout on the central widget
        main_layout = QVBoxLayout(self.centralWidget())
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)  # Visual Liturgy: spacing-md
        
        # --- Top Controls ---
        controls = QHBoxLayout()
        controls.setSpacing(8)  # Visual Liturgy: spacing-sm
        
        # Cipher Selection
        cipher_label = QLabel("Cipher System:")
        cipher_label.setStyleSheet(f"font-weight: 600; color: {theme.COLORS['text_primary']};")
        controls.addWidget(cipher_label)
        self.cipher_combo = QComboBox()
        self.cipher_combo.addItems(list(self.calculators.keys()))
        self.cipher_combo.setMinimumHeight(40)
        self.cipher_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {theme.COLORS['light']};
                border: 2px solid {theme.COLORS['ash']};
                border-radius: 8px;
                padding: 8px;
                color: {theme.COLORS['void']};
                min-height: 40px;
            }}
            QComboBox:focus {{
                border-color: {theme.COLORS['focus']};
            }}
        """)
        controls.addWidget(self.cipher_combo)
        
        controls.addSpacing(16)
        
        # Symmetry Mode Selection
        symmetry_label = QLabel("Symmetry Mode:")
        symmetry_label.setStyleSheet(f"font-weight: 600; color: {theme.COLORS['text_primary']};")
        controls.addWidget(symmetry_label)
        self.symmetry_combo = QComboBox()
        self.symmetry_combo.addItems(["Exact Match", "Fuzzy (±10%)", "Digit Root", "Sum Balance"])
        self.symmetry_combo.setMinimumHeight(40)
        self.symmetry_combo.setToolTip(
            "Exact: Values must match exactly\n"
            "Fuzzy: Values within ±10% tolerance\n"
            "Digit Root: Reduced values (mod 9) match\n"
            "Sum Balance: Total left = total right"
        )
        self.symmetry_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {theme.COLORS['light']};
                border: 2px solid {theme.COLORS['ash']};
                border-radius: 8px;
                padding: 8px;
                color: {theme.COLORS['void']};
                min-height: 40px;
            }}
            QComboBox:focus {{
                border-color: {theme.COLORS['focus']};
            }}
        """)
        controls.addWidget(self.symmetry_combo)
        
        controls.addSpacing(16)
        
        depth_label = QLabel("Mirror Layers:")
        depth_label.setStyleSheet(f"font-weight: 600; color: {theme.COLORS['text_primary']};")
        controls.addWidget(depth_label)
        self.spin_depth = QSpinBox()
        self.spin_depth.setRange(1, 10)
        self.spin_depth.setValue(2) # Default A-B-C-B-A
        self.spin_depth.setToolTip("Minimum nested pairs required\n1 = simple A-B-A\n2 = nested A-B-C-B-A\n3 = A-B-C-D-C-B-A")
        self.spin_depth.setMinimumHeight(40)
        self.spin_depth.setStyleSheet(f"""
            QSpinBox {{
                background-color: {theme.COLORS['light']};
                border: 2px solid {theme.COLORS['ash']};
                border-radius: 8px;
                padding: 8px;
                color: {theme.COLORS['void']};
                min-height: 40px;
            }}
            QSpinBox:focus {{
                border-color: {theme.COLORS['focus']};
            }}
        """)
        controls.addWidget(self.spin_depth)
        
        controls.addSpacing(16)
        
        self.btn_scan = QPushButton("⚖️ Scan for Patterns")
        self.btn_scan.setMinimumHeight(40)  # Visual Liturgy: button height
        theme.set_archetype(self.btn_scan, "seeker")
        self.btn_scan.clicked.connect(self.scan_text)
        controls.addWidget(self.btn_scan)
        
        controls.addStretch()
        main_layout.addLayout(controls)
        
        # --- Splitter Content ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Input & List
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(8, 8, 8, 8)
        left_layout.setSpacing(8)  # Visual Liturgy: spacing-sm
        
        input_label = QLabel("📜 The Text to Mirror")
        input_label.setStyleSheet(theme.get_subtitle_style())
        left_layout.addWidget(input_label)
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Inscribe your text, or summon a document from the archives...")
        self.input_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {theme.COLORS['light']};
                border: 2px solid {theme.COLORS['ash']};
                border-radius: 8px;
                padding: 12px;
                color: {theme.COLORS['void']};
                font-size: 11pt;
            }}
            QTextEdit:focus {{
                border-color: {theme.COLORS['focus']};
            }}
        """)
        left_layout.addWidget(self.input_text)
        
        # Load Document Button
        self.btn_load_doc = QPushButton("📂 Load Document")
        self.btn_load_doc.setMinimumHeight(40)  # Visual Liturgy: button height
        theme.set_archetype(self.btn_load_doc, "navigator")
        self.btn_load_doc.clicked.connect(self.load_document_dialog)
        left_layout.addWidget(self.btn_load_doc)
        
        # Pattern count header
        patterns_header = QHBoxLayout()
        patterns_label = QLabel("🔍 Discovered Patterns")
        patterns_label.setStyleSheet(theme.get_subtitle_style())
        patterns_header.addWidget(patterns_label)
        
        self.pattern_count_label = QLabel("(0)")
        self.pattern_count_label.setStyleSheet(f"font-weight: 700; color: {theme.COLORS['seeker']}; font-size: 12pt;")
        patterns_header.addWidget(self.pattern_count_label)
        patterns_header.addStretch()
        
        left_layout.addLayout(patterns_header)
        self.pattern_list = QListWidget()
        self.pattern_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {theme.COLORS['surface']};
                border: 1px solid {theme.COLORS['border']};
                border-radius: 8px;
                padding: 8px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
            }}
            QListWidget::item:selected {{
                background-color: {theme.COLORS['seeker_soft']};
                color: {theme.COLORS['void']};
            }}
        """)
        self.pattern_list.currentRowChanged.connect(self.display_pattern)
        left_layout.addWidget(self.pattern_list)
        
        splitter.addWidget(left_widget)
        
        # Right: Visualization
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_layout.setSpacing(8)  # Visual Liturgy: spacing-sm
        
        # Visualization header with controls
        viz_header = QHBoxLayout()
        viz_label = QLabel("✨ The Mirror Revealed")
        viz_label.setStyleSheet(theme.get_subtitle_style())
        viz_header.addWidget(viz_label)
        viz_header.addStretch()
        
        self.btn_copy_pattern = QPushButton("📋 Copy")
        self.btn_copy_pattern.setMinimumHeight(32)
        self.btn_copy_pattern.setEnabled(False)
        theme.set_archetype(self.btn_copy_pattern, "navigator")
        self.btn_copy_pattern.clicked.connect(self.copy_current_pattern)
        viz_header.addWidget(self.btn_copy_pattern)
        
        self.btn_export_all = QPushButton("💾 Export All")
        self.btn_export_all.setMinimumHeight(32)
        self.btn_export_all.setEnabled(False)
        theme.set_archetype(self.btn_export_all, "scribe")
        self.btn_export_all.clicked.connect(self.export_all_patterns)
        viz_header.addWidget(self.btn_export_all)
        
        right_layout.addLayout(viz_header)
        self.viz_display = QTextEdit()
        self.viz_display.setReadOnly(True)
        # Set styling for visualization
        self.viz_display.setStyleSheet(f"""
            QTextEdit {{
                font-family: 'Courier New', monospace;
                font-size: 14pt;
                background-color: {theme.COLORS['void']};
                color: {theme.COLORS['light']};
                border: 1px solid {theme.COLORS['border']};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        right_layout.addWidget(self.viz_display)
        
        splitter.addWidget(right_widget)
        
        # Set initial sizes
        splitter.setSizes([400, 600])
        
        main_layout.addWidget(splitter)
        main_layout.addWidget(self.status_bar)
        
        # Initial status
        self.status_bar.showMessage("Ready to scan for chiastic patterns...")

    def load_document_dialog(self):
        """
        Load document dialog logic.
        
        """
        from pillars.gematria.ui.document_selector import DocumentSelectorDialog
        dialog = DocumentSelectorDialog(self)
        if dialog.exec():
            doc_id = dialog.get_selected_doc_id()
            if doc_id:
                self.load_document_text(doc_id)

    def load_document_text(self, doc_id):
        """
        Load document text logic.
        
        Args:
            doc_id: Description of doc_id.
        
        """
        from pillars.gematria.services.document_service import DocumentService
        from PyQt6.QtWidgets import QMessageBox
        
        try:
            service = DocumentService()
            content = service.get_document_content(doc_id)
            if content:
                self.input_text.setText(content)
            else:
                QMessageBox.warning(self, "The Scroll is Empty", "This document contains no text.")
        except Exception as e:
            QMessageBox.critical(self, "The Archives Resist", f"Failed to retrieve document: {str(e)}")

    def scan_text(self):
        """
        Scan text logic.
        
        """
        from PyQt6.QtWidgets import QApplication, QMessageBox
        from PyQt6.QtGui import QCursor
        from PyQt6.QtCore import Qt as QtCore
        
        text = self.input_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "The Scroll is Blank", "Please inscribe text or load a document before scanning.")
            return
            
        depth = self.spin_depth.value()
        cipher_name = self.cipher_combo.currentText()
        symmetry_mode = self.symmetry_combo.currentText()
        calculator = self.calculators.get(cipher_name)
        
        if not calculator:
            QMessageBox.critical(self, "The Oracle is Silent", "No calculator available for the selected cipher.")
            return
        
        # Visual feedback
        self.setCursor(QCursor(QtCore.CursorShape.WaitCursor))
        self.status_bar.showMessage(f"Seeking mirrors using {cipher_name} ({symmetry_mode})...")
        QApplication.processEvents()
        
        try:
            self.patterns = self.service.scan_text(text, calculator, min_depth=depth, max_depth=10, symmetry_mode=symmetry_mode)
            
            self.pattern_list.clear()
            self.viz_display.clear()
            self.btn_copy_pattern.setEnabled(False)
            
            if not self.patterns:
                self.pattern_count_label.setText("(0)")
                self.btn_export_all.setEnabled(False)
                self.pattern_list.addItem("⚠️ No chiastic patterns discovered.")
                self.status_bar.showMessage("Scan complete. No patterns found.")
                return
            
            # Update count
            self.pattern_count_label.setText(f"({len(self.patterns)})")
            self.btn_export_all.setEnabled(True)
            
            # Populate list with pattern type indicators
            from PyQt6.QtGui import QColor
            for i, p in enumerate(self.patterns):
                pattern_type = "⚖️" if p.center_index is not None else "🔄"
                center_word = p.source_units[len(p.left_indices)] if p.center_index is not None else "[Mirror]"
                label = f"{pattern_type} Depth {p.depth} | Center: {center_word}"
                item = QListWidgetItem(label)
                item.setData(Qt.ItemDataRole.UserRole, i)
                # Visual distinction
                if p.center_index is not None:
                    item.setForeground(QColor(theme.COLORS['seeker']))  # Odd patterns (centered)
                else:
                    item.setForeground(QColor(theme.COLORS['magus']))  # Even patterns (mirrored)
                self.pattern_list.addItem(item)
            
            self.status_bar.showMessage(f"✨ {len(self.patterns)} pattern(s) discovered!")
            
        except Exception as e:
            QMessageBox.critical(self, "The Weave Unravels", f"Error during scan: {str(e)}")
            self.status_bar.showMessage("Scan failed.")
        finally:
            self.setCursor(QCursor(QtCore.CursorShape.ArrowCursor))
            
    def display_pattern(self, row):
        """
        Display pattern logic.
        
        Args:
            row: Description of row.
        
        """
        if row < 0 or row >= len(self.patterns):
            self.viz_display.clear()
            self.btn_copy_pattern.setEnabled(False)
            self.status_bar.showMessage("Select a pattern to view its structure...")
            return
            
        pat = self.patterns[row]
        html = self.generate_viz_html(pat)
        self.viz_display.setHtml(html)
        self.btn_copy_pattern.setEnabled(True)
        
        pattern_type = "centered" if pat.center_index is not None else "mirrored"
        self.status_bar.showMessage(f"Viewing {pattern_type} pattern with {pat.depth} layer(s)...")
        
    def copy_current_pattern(self):
        """Copy current pattern visualization to clipboard."""
        from PyQt6.QtWidgets import QApplication
        
        row = self.pattern_list.currentRow()
        if row < 0 or row >= len(self.patterns):
            return
        
        pat = self.patterns[row]
        text_repr = self.generate_text_representation(pat)
        
        clipboard = QApplication.clipboard()
        clipboard.setText(text_repr)
        self.status_bar.showMessage("Pattern copied to clipboard!")
    
    def generate_text_representation(self, p) -> str:
        """Generate plain text representation of pattern."""
        lines = []
        lines.append(f"Chiastic Pattern (Depth {p.depth})")
        lines.append("=" * 40)
        
        indent = 0
        for i in range(len(p.left_indices)):
            word = p.source_units[i]
            val = p.values[i]
            spaces = "  " * indent
            lines.append(f"{spaces}{word} ({val})")
            indent += 1
        
        if p.center_index is not None:
            center_idx_in_units = len(p.left_indices)
            word = p.source_units[center_idx_in_units]
            val = p.values[center_idx_in_units]
            spaces = "  " * indent
            lines.append(f"{spaces}[{word}] ({val}) ← CENTER")
        else:
            spaces = "  " * indent
            lines.append(f"{spaces}═══════ MIRROR ═══════")
            indent -= 1
        
        start_right = len(p.left_indices) + (1 if p.center_index is not None else 0)
        right_units = p.source_units[start_right:]
        right_values = p.values[start_right:]
        
        if p.center_index is not None:
            indent -= 1
        
        for i, word in enumerate(right_units):
            val = right_values[i]
            spaces = "  " * indent
            lines.append(f"{spaces}{word} ({val})")
            indent -= 1
        
        return "\n".join(lines)
    
    def export_all_patterns(self):
        """Export all discovered patterns to a file."""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        
        if not self.patterns:
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Chiastic Patterns",
            "chiastic_patterns.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("CHIASTIC PATTERN ANALYSIS\n")
                f.write(f"Cipher: {self.cipher_combo.currentText()}\n")
                f.write(f"Total Patterns Found: {len(self.patterns)}\n")
                f.write("=" * 60 + "\n\n")
                
                for i, pat in enumerate(self.patterns, 1):
                    f.write(f"\nPATTERN #{i}\n")
                    f.write(self.generate_text_representation(pat))
                    f.write("\n" + "-" * 60 + "\n")
            
            QMessageBox.information(self, "The Archive Receives", f"Patterns exported to:\n{filename}")
            self.status_bar.showMessage(f"Exported {len(self.patterns)} pattern(s) successfully.")
            
        except Exception as e:
            QMessageBox.critical(self, "The Archive Refuses", f"Failed to export patterns:\n{str(e)}")
    
    def generate_viz_html(self, p) -> str:
        """Generates V-shape or Mirror HTML."""
        lines = []
        
        # Colors for layers (from Visual Liturgy)
        colors = [
            theme.COLORS['destroyer'],  # Crimson
            theme.COLORS['scribe'],     # Emerald
            theme.COLORS['seeker'],     # Amber
            theme.COLORS['magus'],      # Violet
            theme.COLORS['seeker_soft'],  # Soft amber
            theme.COLORS['navigator']   # Slate
        ]
        
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
            line = f"{spaces}<span style='color:{theme.COLORS['light']}; background-color: {theme.COLORS['stone']}'><b>{word}</b> ({val})</span>"
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
        start_right = len(p.left_indices) + (1 if p.center_index is not None else 0)  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
        
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