# Qt Widgets - Basic UI components
from PyQt5.QtWidgets import (
    # Layout widgets
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    
    # Basic widgets
    QPushButton,
    QLabel,
    QLineEdit,
    QSpinBox,
    QCheckBox,
    
    # Container widgets
    QGroupBox,
    QTabWidget,
    QScrollArea,
    
    # Dialog widgets
    QMessageBox,
    QInputDialog
)

# Qt Core - Basic functionality
from PyQt5.QtCore import (
    Qt
)

# Local imports - Custom classes
from core.gematria.custom_cipher import CustomCipher
from core.gematria.cipher_manager import CipherManager


class CreateCipherPanel(QWidget):
    """
    Panel for creating and managing custom ciphers.
    Allows setting values for English, Greek, and Hebrew characters.
    """
    def __init__(self):
        super().__init__()
        self.cipher_manager = CipherManager()
        self.cipher = CustomCipher("New Cipher")
        self.cipher.set_case_sensitive(False)  # Set default to case-insensitive
        self.tab_widget = None  # Add this line to store reference
        self.init_ui()
        # Set size to fit content
        self.adjustSize()
        # Set minimum width to ensure all content is visible
        self.setMinimumWidth(800)  # Adjust this value as needed

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Add the main sections
        main_layout.addWidget(self._create_header())
        main_layout.addWidget(self._create_info_section())
        self.tab_widget = self._create_script_tabs()  # Store reference
        main_layout.addWidget(self.tab_widget)
        main_layout.addLayout(self._create_button_bar())
        
        self.setLayout(main_layout)

    def _create_header(self):
        header = QLabel("Create Custom Cipher")
        header.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
        """)
        return header

    def _create_info_section(self):
        info_group = QGroupBox("Cipher Information")
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Top row - Name and Case Sensitivity
        top_row = QHBoxLayout()
        
        # Name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        self.name_input = QLineEdit()
        self.name_input.setText(self.cipher.name)
        self.name_input.setMaximumWidth(200)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        
        # Case sensitivity
        self.case_sensitive = QCheckBox("Case Sensitive")
        self.case_sensitive.setChecked(self.cipher.case_sensitive)
        self.case_sensitive.stateChanged.connect(self.toggle_case_sensitivity)
        
        top_row.addLayout(name_layout)
        top_row.addWidget(self.case_sensitive)
        top_row.addStretch()
        
        # Bottom row - Script Selection
        bottom_row = QHBoxLayout()
        
        # Script toggles
        self.english_active = QCheckBox("English")
        self.greek_active = QCheckBox("Greek")
        self.hebrew_active = QCheckBox("Hebrew")
        
        # Connect toggles to tab enabling/disabling
        self.english_active.stateChanged.connect(lambda state: self._toggle_script_tab("English", state))
        self.greek_active.stateChanged.connect(lambda state: self._toggle_script_tab("Greek", state))
        self.hebrew_active.stateChanged.connect(lambda state: self._toggle_script_tab("Hebrew", state))
        
        bottom_row.addWidget(QLabel("Active Scripts:"))
        bottom_row.addWidget(self.english_active)
        bottom_row.addWidget(self.greek_active)
        bottom_row.addWidget(self.hebrew_active)
        bottom_row.addStretch()
        
        layout.addLayout(top_row)
        layout.addLayout(bottom_row)
        info_group.setLayout(layout)
        info_group.setMaximumHeight(100)
        
        return info_group

    def _toggle_script_tab(self, script_name, state):
        """Handle script activation/deactivation"""
        # Update active scripts in cipher
        script_type = script_name.lower()
        self.cipher.active_scripts[script_type] = bool(state)
        
        # Debug print
        print(f"DEBUG: {script_name} script {'activated' if state else 'deactivated'}")
        print(f"DEBUG: Active scripts: {self.cipher.active_scripts}")
        
        # Recreate tabs to show/hide as needed
        self.refresh_values()

    def _create_script_tabs(self):
        tab_widget = QTabWidget()
        
        # Only add tabs for active scripts
        if self.cipher.active_scripts['english']:
            tab_widget.addTab(self._create_english_tab(), "English")
            
        if self.cipher.active_scripts['greek']:
            tab_widget.addTab(self._create_greek_tab(), "Greek")
            
        if self.cipher.active_scripts['hebrew']:
            tab_widget.addTab(self._create_hebrew_tab(), "Hebrew")
        
        return tab_widget

    def _create_english_tab(self):
        scroll = QScrollArea()
        widget = QWidget()
        layout = QHBoxLayout()
        
        if self.case_sensitive.isChecked():
            # Show separate uppercase and lowercase columns
            # Uppercase (left side)
            upper_group = QGroupBox("Uppercase")
            upper_layout = QGridLayout()
            for i, c in enumerate(range(65, 91)):  # A-Z
                char = chr(c)
                upper_layout.addWidget(QLabel(char), i, 0)
                spin = self._create_value_spinbox(char, 'english')
                upper_layout.addWidget(spin, i, 1)
            upper_group.setLayout(upper_layout)
            
            # Lowercase (right side)
            lower_group = QGroupBox("Lowercase")
            lower_layout = QGridLayout()
            for i, c in enumerate(range(97, 123)):  # a-z
                char = chr(c)
                lower_layout.addWidget(QLabel(char), i, 0)
                spin = self._create_value_spinbox(char, 'english')
                lower_layout.addWidget(spin, i, 1)
            lower_group.setLayout(lower_layout)
            
            layout.addWidget(upper_group)
            layout.addWidget(lower_group)
        else:
            # Show combined single column
            combined_group = QGroupBox("English Alphabet")
            combined_layout = QGridLayout()
            for i, c in enumerate(range(65, 91)):  # A-Z
                char = chr(c)
                lower_char = chr(c + 32)
                combined_layout.addWidget(QLabel(f"{char}/{lower_char}"), i, 0)
                spin = self._create_value_spinbox(char, 'english')
                combined_layout.addWidget(spin, i, 1)
            combined_group.setLayout(combined_layout)
            layout.addWidget(combined_group)
        
        widget.setLayout(layout)
        scroll.setWidget(widget)
        return scroll

    def _create_greek_tab(self):
        scroll = QScrollArea()
        widget = QWidget()
        layout = QHBoxLayout()
        
        greek_upper = 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ'
        greek_lower = 'αβγδεζηθικλμνξοπρστυφχψω'
        
        if self.case_sensitive.isChecked():
            # Show separate uppercase and lowercase columns
            upper_group = QGroupBox("Uppercase")
            upper_layout = QGridLayout()
            for i, char in enumerate(greek_upper):
                upper_layout.addWidget(QLabel(char), i, 0)
                spin = self._create_value_spinbox(char, 'greek')
                upper_layout.addWidget(spin, i, 1)
            upper_group.setLayout(upper_layout)
            
            lower_group = QGroupBox("Lowercase")
            lower_layout = QGridLayout()
            for i, char in enumerate(greek_lower):
                lower_layout.addWidget(QLabel(char), i, 0)
                spin = self._create_value_spinbox(char, 'greek')
                lower_layout.addWidget(spin, i, 1)
            lower_group.setLayout(lower_layout)
            
            layout.addWidget(upper_group)
            layout.addWidget(lower_group)
        else:
            # Show combined single column
            combined_group = QGroupBox("Greek Alphabet")
            combined_layout = QGridLayout()
            for i, (upper, lower) in enumerate(zip(greek_upper, greek_lower)):
                combined_layout.addWidget(QLabel(f"{upper}/{lower}"), i, 0)
                spin = self._create_value_spinbox(upper, 'greek')
                combined_layout.addWidget(spin, i, 1)
            combined_group.setLayout(combined_layout)
            layout.addWidget(combined_group)
        
        widget.setLayout(layout)
        scroll.setWidget(widget)
        return scroll

    def _create_hebrew_tab(self):
        scroll = QScrollArea()
        widget = QWidget()
        layout = QHBoxLayout()
        
        # Regular characters (left side)
        regular_group = QGroupBox("Regular Characters")
        regular_layout = QGridLayout()
        hebrew_chars = 'אבגדהוזחטיכלמנסעפצקרשת'
        for i, char in enumerate(hebrew_chars):
            regular_layout.addWidget(QLabel(char), i, 0)
            spin = self._create_value_spinbox(char, 'hebrew')
            regular_layout.addWidget(spin, i, 1)
        regular_group.setLayout(regular_layout)
        
        # Finals (right side)
        finals_group = QGroupBox("Final Forms")
        finals_layout = QGridLayout()
        finals = 'ךםןףץ'
        for i, char in enumerate(finals):
            finals_layout.addWidget(QLabel(char), i, 0)
            spin = self._create_value_spinbox(char, 'finals')
            finals_layout.addWidget(spin, i, 1)
        finals_group.setLayout(finals_layout)
        
        layout.addWidget(regular_group)
        layout.addWidget(finals_group)
        widget.setLayout(layout)
        scroll.setWidget(widget)
        return scroll

    def _create_value_spinbox(self, char, script_type):
        spin = QSpinBox()
        spin.setRange(0, 9999)
        
        # Set values (all spinboxes should be enabled since we only show active scripts)
        if script_type == 'english':
            spin.setValue(self.cipher.english_values[char])
        elif script_type == 'greek':
            spin.setValue(self.cipher.greek_values[char])
        elif script_type == 'hebrew' or script_type == 'finals':
            if script_type == 'hebrew':
                spin.setValue(self.cipher.hebrew_values[char])
            else:
                spin.setValue(self.cipher.hebrew_finals[char])
                
        spin.valueChanged.connect(lambda v: self.update_value(script_type, char, v))
        return spin

    def _create_button_bar(self):
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save Cipher")
        save_button.setToolTip("Save the current cipher to a JSON file")
        
        load_button = QPushButton("Load Cipher")
        load_button.setToolTip(
            "Load a cipher from JSON file.\n\n"
            "Expected format:\n"
            "{\n"
            '  "name": "My Cipher",\n'
            '  "description": "Description",\n'
            '  "case_sensitive": true/false,\n'
            '  "english_values": {\n'
            '    "A": 1, "B": 2, ...,\n'
            '    "a": 1, "b": 2, ...\n'
            "  },\n"
            '  "greek_values": {\n'
            '    "Α": 1, "Β": 2, ...,\n'
            '    "α": 1, "β": 2, ...\n'
            "  },\n"
            '  "hebrew_values": {\n'
            '    "א": 1, "ב": 2, ...\n'
            "  },\n"
            '  "hebrew_finals": {\n'
            '    "ך": 20, "ם": 40, "ן": 50, "ף": 80, "ץ": 90\n'
            "  }\n"
            "}"
        )
        
        clear_button = QPushButton("Clear All")
        clear_button.setToolTip("Reset all values to 0")
        
        delete_button = QPushButton("Delete Cipher")
        delete_button.setToolTip("Delete a saved cipher")
        
        save_button.clicked.connect(self.save_cipher)
        load_button.clicked.connect(self.load_cipher)
        clear_button.clicked.connect(self.clear_all)
        delete_button.clicked.connect(self.delete_cipher)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(load_button)
        button_layout.addWidget(clear_button)
        button_layout.addWidget(delete_button)
        
        return button_layout

    # Event handlers
    def update_value(self, script_type, char, value):
        # No need to check active scripts here since only active scripts are shown
        self.cipher.set_value(char, value)

    def toggle_case_sensitivity(self, state):
        self.cipher.set_case_sensitive(state == Qt.Checked)
        self.refresh_values()

    def refresh_values(self):
        """Update all UI elements to reflect current cipher values"""
        self.name_input.setText(self.cipher.name)
        self.case_sensitive.setChecked(self.cipher.case_sensitive)
        
        # Update script checkboxes to match cipher state
        self.english_active.setChecked(self.cipher.active_scripts['english'])
        self.greek_active.setChecked(self.cipher.active_scripts['greek'])
        self.hebrew_active.setChecked(self.cipher.active_scripts['hebrew'])
        
        # Replace tab widget
        if self.tab_widget:
            self.tab_widget.hide()
            self.tab_widget.deleteLater()
        
        self.tab_widget = self._create_script_tabs()
        self.layout().insertWidget(2, self.tab_widget)

    def save_cipher(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a cipher name")
            return
            
        self.cipher.name = name
        
        # Set active scripts based on checkboxes
        self.cipher.active_scripts['english'] = self.english_active.isChecked()
        self.cipher.active_scripts['greek'] = self.greek_active.isChecked()
        self.cipher.active_scripts['hebrew'] = self.hebrew_active.isChecked()
        
        if self.cipher_manager.save_cipher(self.cipher):
            QMessageBox.information(self, "Success", f"Cipher '{name}' saved successfully")
        else:
            QMessageBox.critical(self, "Error", f"Failed to save cipher '{name}'")

    def load_cipher(self):
        cipher_names = self.cipher_manager.get_cipher_names()
        if not cipher_names:
            QMessageBox.information(self, "No Ciphers", "No saved ciphers found")
            return
            
        # Debug print to check for duplicates
        print(f"DEBUG: Available ciphers: {cipher_names}")
        
        # Ensure unique items in dialog
        unique_names = list(dict.fromkeys(cipher_names))
        name, ok = QInputDialog.getItem(self, "Load Cipher", 
                                      "Select a cipher to load:",
                                      unique_names, 0, False)
        if ok and name:
            loaded_cipher = self.cipher_manager.load_cipher(name)
            if loaded_cipher:
                print(f"DEBUG: Loaded cipher: {loaded_cipher.name}")  # Debug print
                self.cipher = loaded_cipher
                # Set checkboxes based on active scripts
                self.english_active.setChecked(self.cipher.active_scripts['english'])
                self.greek_active.setChecked(self.cipher.active_scripts['greek'])
                self.hebrew_active.setChecked(self.cipher.active_scripts['hebrew'])
                self.refresh_values()
                QMessageBox.information(self, "Success", f"Cipher '{name}' loaded successfully")
            else:
                QMessageBox.critical(self, "Error", f"Failed to load cipher '{name}'")

    def clear_all(self):
        """Reset the cipher and UI"""
        self.cipher = CustomCipher(self.name_input.text())
        # Reset script checkboxes
        self.english_active.setChecked(False)
        self.greek_active.setChecked(False)
        self.hebrew_active.setChecked(False)
        self.refresh_values()

    def delete_cipher(self):
        cipher_names = self.cipher_manager.get_cipher_names()
        if not cipher_names:
            QMessageBox.information(self, "No Ciphers", "No saved ciphers found")
            return
            
        name, ok = QInputDialog.getItem(self, "Delete Cipher", 
                                      "Select a cipher to delete:",
                                      cipher_names, 0, False)
        if ok and name:
            confirm = QMessageBox.question(self, "Confirm Delete",
                                         f"Are you sure you want to delete cipher '{name}'?",
                                         QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                if self.cipher_manager.delete_cipher(name):
                    QMessageBox.information(self, "Success", f"Cipher '{name}' deleted successfully")
                else:
                    QMessageBox.critical(self, "Error", f"Failed to delete cipher '{name}'")


# TODO: Future Development
# 1. Integration
#    - Add custom ciphers to calculator panel
#    - Integrate with text analysis panel
#    - Add support in reverse calculator
#    - Include in search results panel
#
# 2. Features
#    - Add import/export functionality for sharing ciphers
#    - Add cipher validation and error checking
#    - Add preset cipher templates
#    - Add bulk value assignment tools
#    - Add cipher comparison tools
#
# 3. UI Improvements
#    - Add preview of cipher calculations
#    - Add visual value distribution graph
#    - Add drag-and-drop reordering of characters
#    - Add keyboard shortcuts for common operations
#
# 4. Data Management
#    - Add cipher versioning
#    - Add cipher categories/tags
#    - Add cipher backup/restore
#    - Add cipher merge functionality
#
# 5. Advanced Features
#    - Add custom character support
#    - Add formula-based value assignment
#    - Add cipher analysis tools
#    - Add cipher optimization suggestions