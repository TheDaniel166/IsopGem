"""Gematria calculator tool window."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox,
    QMessageBox, QInputDialog, QMenu, QRadioButton
)
from PyQt6.QtCore import Qt
from typing import Dict, List, Optional
from ..services.base_calculator import GematriaCalculator
from ..services import CalculationService
from shared.ui import VirtualKeyboard, get_shared_virtual_keyboard
from shared.ui.window_manager import WindowManager # Should be available via parent typically, but importing for type hint if needed
from .components import ResultsDashboard
from shared.signals.navigation_bus import navigation_bus
from shared.services.document_manager.notebook_service import notebook_service_context
from shared.ui.theme import (
    COLORS,
    apply_tablet_shadow,
    get_subtitle_style,
    get_tablet_style,
    get_title_style,
    set_archetype,
)


class GematriaCalculatorWindow(QMainWindow):
    """Standalone Gematria Calculator window."""
    
    def __init__(self, calculators: List[GematriaCalculator], window_manager: Optional[WindowManager] = None, parent=None):
        """
        Initialize the calculator window.
        
        Args:
            calculators: List of available gematria calculator instances
            parent: Optional parent widget
        """
        super().__init__(parent)
        self.window_manager = window_manager
        self.calculators: Dict[str, GematriaCalculator] = {
            calc.name: calc for calc in calculators
        }
        self.current_calculator: Optional[GematriaCalculator] = calculators[0]
        self.calculation_service = CalculationService()
        
        # Store current calculation
        self.current_text: str = ""
        self.current_value: int = 0
        self.current_breakdown: List[tuple] = []
        
        # Virtual keyboard
        self.virtual_keyboard: Optional[VirtualKeyboard] = None
        self.keyboard_visible: bool = False
        self._current_language: Optional[str] = None
        
        # Stored data for export
        self.last_export_data: Optional[dict] = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the calculator interface."""
        self.setWindowTitle("Logos Abacus")
        self.setMinimumSize(1000, 700)
        
        # Prevent this window from closing the entire application
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)

        # Level 0: The Ghost Layer (Nano Banana substrate)
        from pathlib import Path
        possible_paths = [
            Path("src/assets/patterns/calculator_bg_pattern.png"),
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
            abs_path = bg_path.absolute().as_posix()
            central.setStyleSheet(f"""
                QWidget#CentralContainer {{
                    border-image: url("{abs_path}") 0 0 0 0 stretch stretch;
                    border: none;
                    background-color: {COLORS['light']};
                }}
            """)
        else:
            central.setStyleSheet(f"QWidget#CentralContainer {{ background-color: {COLORS['light']}; }}")
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        from PyQt6.QtWidgets import QSplitter, QFrame
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # --- LEFT PANEL (CONTROL PANEL) ---
        left_panel = QFrame()
        left_panel.setObjectName("ControlPanel")
        left_panel.setMinimumWidth(350)
        left_panel.setMaximumWidth(450)
        left_panel.setStyleSheet(
            f"""
            QFrame#ControlPanel {{
                {get_tablet_style()}
            }}
        """
        )

        # Shadow for Left Panel
        apply_tablet_shadow(left_panel)
        
        l_layout = QVBoxLayout(left_panel)
        l_layout.setContentsMargins(30, 40, 30, 40)
        l_layout.setSpacing(25)
        
        # Header in Left Panel
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)
        
        title_label = QLabel("LOGOS ABACUS")
        title_label.setStyleSheet(get_title_style(28) + "font-weight: 900; letter-spacing: -1px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle_label = QLabel("THE MATHEMATICS OF SOUL")
        subtitle_label.setStyleSheet(
            get_subtitle_style()
            + "font-size: 8pt; font-weight: 700; letter-spacing: 0.3em;"
        )
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        l_layout.addLayout(header_layout)
        
        l_layout.addSpacing(20)
        
        # --- System Selection ---
        system_section = QVBoxLayout()
        system_section.setSpacing(10)
        
        selector_label = QLabel("CALCULATION METHOD")
        selector_label.setStyleSheet(
            f"font-size: 9pt; font-weight: 800; color: {COLORS['mist']}; letter-spacing: 0.1em;"
        )
        system_section.addWidget(selector_label)
        
        self.system_button = QPushButton()
        self.system_button.setMinimumHeight(54)
        self.system_button.setObjectName("SystemButton")
        self.system_button.setStyleSheet(
            f"""
            QPushButton#SystemButton[archetype="navigator"] {{
                text-align: left;
                font-weight: 700;
                font-size: 11pt;
                background-color: {COLORS['light']};
                color: {COLORS['stone']};
                border: 1px solid {COLORS['ash']};
                border-radius: 12px;
                padding: 12px 18px;
            }}
            QPushButton#SystemButton[archetype="navigator"]:hover {{
                background-color: {COLORS['cloud']};
                border: 1px solid {COLORS['focus']};
            }}
            QPushButton#SystemButton[archetype="navigator"]:pressed {{
                background-color: {COLORS['ash']};
            }}
            QPushButton#SystemButton::menu-indicator {{
                subcontrol-position: right center;
                subcontrol-origin: padding;
                right: 15px;
            }}
        """
        )
        set_archetype(self.system_button, "navigator")
        
        # Create the menu
        self.system_menu = QMenu(self)
        self.system_menu.setStyleSheet(
            f"""
            QMenu {{
                background-color: {COLORS['light']};
                border: 1px solid {COLORS['ash']};
                border-radius: 10px;
                padding: 10px 6px;
                margin-top: 6px;
            }}
            QMenu::item {{
                padding: 10px 18px;
                border-radius: 8px;
                color: {COLORS['stone']};
                font-weight: 600;
            }}
            QMenu::item:selected {{
                background-color: {COLORS['focus']};
                color: {COLORS['light']};
            }}
        """
        )
        
        # Hebrew submenu
        hebrew_menu = self.system_menu.addMenu("📖 Hebrew")
        hebrew_menu.addAction("✨ All Methods").triggered.connect(lambda: self._select_calculator("Hebrew_ALL"))
        hebrew_menu.addSeparator()
        for name in list(self.calculators.keys()):
            if "Hebrew" in name:
                action = hebrew_menu.addAction(name.replace("Hebrew ", ""))
                action.triggered.connect(lambda checked, n=name: self._select_calculator(n))  # type: ignore[reportOptionalMemberAccess, reportUnknownArgumentType, reportUnknownLambdaType]

        # Greek submenu
        greek_menu = self.system_menu.addMenu("🔤 Greek")
        greek_menu.addAction("✨ All Methods").triggered.connect(lambda: self._select_calculator("Greek_ALL"))
        greek_menu.addSeparator()
        for name in list(self.calculators.keys()):
            if "Greek" in name:
                action = greek_menu.addAction(name.replace("Greek ", ""))
                action.triggered.connect(lambda checked, n=name: self._select_calculator(n))  # type: ignore[reportOptionalMemberAccess, reportUnknownArgumentType, reportUnknownLambdaType]

        # English submenu
        english_menu = self.system_menu.addMenu("🔡 English")
        english_menu.addAction("✨ All Methods").triggered.connect(lambda: self._select_calculator("English_ALL"))
        english_menu.addSeparator()
        for name in list(self.calculators.keys()):
            if "English" in name or "TQ" in name:
                action = english_menu.addAction(name.replace("English ", ""))
                action.triggered.connect(lambda checked, n=name: self._select_calculator(n))  # type: ignore[reportOptionalMemberAccess, reportUnknownArgumentType, reportUnknownLambdaType]

        # Arabic submenu
        arabic_menu = self.system_menu.addMenu("☪️ Arabic")
        arabic_menu.addAction("✨ All Methods").triggered.connect(lambda: self._select_calculator("Arabic_ALL"))
        arabic_menu.addSeparator()
        for name in list(self.calculators.keys()):
            if "Arabic" in name:
                action = arabic_menu.addAction(name.replace("Arabic ", ""))
                action.triggered.connect(lambda checked, n=name: self._select_calculator(n))  # type: ignore[reportOptionalMemberAccess, reportUnknownArgumentType, reportUnknownLambdaType]

        # Sanskrit submenu
        sanskrit_menu = self.system_menu.addMenu("🕉️ Sanskrit")
        # Direct calculator selection since we only have one for now
        for name in list(self.calculators.keys()):
            if "Sanskrit" in name:
                action = sanskrit_menu.addAction(name.replace("Sanskrit ", ""))
                action.triggered.connect(lambda checked, n=name: self._select_calculator(n))

        self.system_button.setMenu(self.system_menu)
        
        # Set first calculator as default
        first_calc = list(self.calculators.keys())[0]
        self.system_button.setText(first_calc.replace("Hebrew ", "").replace("Greek ", "").replace("English ", ""))
        self.current_calculator = self.calculators[first_calc]
        
        system_section.addWidget(self.system_button)
        l_layout.addLayout(system_section)
        
        # --- Input Section ---
        input_section = QVBoxLayout()
        input_section.setSpacing(10)
        
        input_label = QLabel("ENTER WISDOM")
        input_label.setStyleSheet(
            f"font-size: 9pt; font-weight: 800; color: {COLORS['mist']}; letter-spacing: 0.1em;"
        )
        input_section.addWidget(input_label)
        
        input_row = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("The phrase to measure...")
        self.input_field.setStyleSheet(
            f"""
            QLineEdit {{
                font-size: 15pt;
                min-height: 54px;
                padding: 10px 15px;
                border: 2px solid {COLORS['ash']};
                border-radius: 12px;
                background-color: {COLORS['light']};
                color: {COLORS['void']};
                font-weight: 500;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['focus']};
                background-color: {COLORS['light']};
            }}
        """
        )
        self.input_field.returnPressed.connect(self._calculate)
        input_row.addWidget(self.input_field)
        
        self.keyboard_toggle = QPushButton("⌨️")
        self.keyboard_toggle.setFixedSize(54, 54)
        self.keyboard_toggle.setObjectName("KeyboardToggle")
        self.keyboard_toggle.setStyleSheet(
            """
            QPushButton#KeyboardToggle {
                font-size: 18pt;
            }
        """
        )
        set_archetype(self.keyboard_toggle, "ghost")
        self.keyboard_toggle.clicked.connect(self._toggle_keyboard)
        input_row.addWidget(self.keyboard_toggle)
        
        input_section.addLayout(input_row)
        l_layout.addLayout(input_section)
        
        # Virtual keyboard (popup window)
        self.virtual_keyboard = get_shared_virtual_keyboard(self)
        self.virtual_keyboard.set_target_input(self.input_field)
        
        # --- Actions ---
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(12)
        
        self.calc_button = QPushButton("Calculate Revelation")
        self.calc_button.clicked.connect(self._calculate)
        self.calc_button.setMinimumHeight(64)
        set_archetype(self.calc_button, "magus")
        self.calc_button.setCursor(Qt.CursorShape.PointingHandCursor)
        actions_layout.addWidget(self.calc_button)
        
        self.save_button = QPushButton("💾 Preserve in Chronicle")
        self.save_button.clicked.connect(self._save_calculation)
        self.save_button.setMinimumHeight(54)
        self.save_button.setEnabled(False)
        set_archetype(self.save_button, "scribe")
        self.save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        actions_layout.addWidget(self.save_button)
        l_layout.addLayout(actions_layout)
        
        # Options
        self.show_breakdown_toggle = QRadioButton("Expose Character Breakdown")
        self.show_breakdown_toggle.setStyleSheet(
            f"""
            QRadioButton {{
                color: {COLORS['navigator']};
                font-size: 10pt;
                font-weight: 600;
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
            }}
        """
        )
        self.show_breakdown_toggle.toggled.connect(self._calculate)
        l_layout.addWidget(self.show_breakdown_toggle)
        
        l_layout.addStretch()
        
        # --- RIGHT PANEL (RESULTS PANEL) ---
        right_panel = QFrame()
        right_panel.setObjectName("ResultsPanel")
        right_panel.setStyleSheet(
            f"""
            QFrame#ResultsPanel {{
                background-color: {COLORS['light']};
                border-radius: 24px;
                border: 1px solid {COLORS['border']};
            }}
        """
        )
        
        r_layout = QVBoxLayout(right_panel)
        r_layout.setContentsMargins(0, 0, 0, 0)
        
        self.results_dashboard = ResultsDashboard()
        self.results_dashboard.totalContextMenuRequested.connect(self._on_total_context_menu)
        r_layout.addWidget(self.results_dashboard)
        
        # Add panes to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([400, 600])
        
        self.input_field.setFocus()
    
    def _select_calculator(self, system_name: str):
        """
        Select a calculator system from the menu.
        
        Args:
            system_name: Name of the selected system
        """
        # Handle "All Methods" selections
        if system_name.endswith("_ALL"):
            language = system_name.replace("_ALL", "")
            display_name = f"{language} - All Methods"
            self.system_button.setText("All Methods")
            self.current_calculator = None  # Flag for multi-method mode
            self._current_language = language
            
            # Update keyboard layout
            if self.virtual_keyboard:
                if language == 'Hebrew':
                    self.virtual_keyboard.set_layout('hebrew')
                elif language == 'Greek':
                    self.virtual_keyboard.set_layout('greek_lower')
                elif language == 'Arabic':
                    self.virtual_keyboard.set_layout('arabic')
        else:
            # Display only the method name without language prefix
            display_name = system_name.replace("Hebrew ", "").replace("Greek ", "").replace("English ", "").replace("Arabic ", "").replace("Sanskrit ", "")
            self.system_button.setText(display_name)
            self.current_calculator = self.calculators[system_name]
            self._current_language = None
            
            # Update keyboard layout based on calculator language
            if self.virtual_keyboard:
                if 'Hebrew' in system_name:
                    self.virtual_keyboard.set_layout('hebrew')
                elif 'Greek' in system_name:
                    self.virtual_keyboard.set_layout('greek_lower')
                elif 'Arabic' in system_name:
                    self.virtual_keyboard.set_layout('arabic')
                elif 'Sanskrit' in system_name:
                    self.virtual_keyboard.set_layout('sanskrit')
        
        # Toggle breakdown option based on mode
        self.show_breakdown_toggle.setEnabled(self.current_calculator is not None)
        
        # Clear results when switching systems
        self.results_dashboard.clear()
    
    def _toggle_keyboard(self):
        """Toggle virtual keyboard visibility."""
        if self.virtual_keyboard:
            if self.virtual_keyboard.isVisible():
                self.virtual_keyboard.hide()
            else:
                self.virtual_keyboard.set_target_input(self.input_field)
                self.virtual_keyboard.show()
                self.virtual_keyboard.raise_()
                self.virtual_keyboard.activateWindow()
    
    def _calculate(self):
        """Calculate and display gematria value for current input."""
        text = self.input_field.text()
        
        if not text:
            self.results_dashboard.clear()
            self.save_button.setEnabled(False)
            return
        
        # Check if in "All Methods" mode
        if self.current_calculator is None and self._current_language:
            self._calculate_all_methods(text, self._current_language)
            return

        if self.current_calculator is None:
            # Should never happen, but guard for static analysis and runtime safety
            QMessageBox.warning(self, "Gematria Calculator", "No calculator is active.")
            return
        
        # Calculate total value
        total = self.current_calculator.calculate(text)
        
        # Get breakdown
        breakdown = self.current_calculator.get_breakdown(text)
        
        # Store current calculation
        self.current_text = text
        self.current_value = total
        self.current_breakdown = breakdown
        
        # Enable save button
        self.save_button.setEnabled(True)
        
        # Prepare Export Data (Breakdown)
        rows = []
        if breakdown:
            for _i, (char, val) in enumerate(breakdown):  # type: ignore[reportUnknownArgumentType, reportUnknownVariableType, reportUnusedVariable]
                rows.append([char, str(val)])
            # Add Total Row
            rows.append(["TOTAL", str(total)])
            
        self.last_export_data = {
            "name": f"Gematria_{text}_{self.current_calculator.name}",
            "data": {
                "columns": ["Character", "Value"],
                "data": rows, # Standardizing on 'data' key
                "styles": {} 
            }
        }
        
        # Update Visual Dashboard
        self.results_dashboard.display_results(
            text=text,
            total=total,
            system_name=self.current_calculator.name,
            breakdown=breakdown if self.show_breakdown_toggle.isChecked() else []
        )
    
    def _calculate_all_methods(self, text: str, language: str):
        """Calculate using all methods for a given language.
        
        Args:
            text: The text to calculate
            language: 'Hebrew', 'Greek', or 'English'
        """
        # Get all calculators for this language
        lang_calculators = [
            (name, calc) for name, calc in self.calculators.items()
            if language in name
        ]
        
        if not lang_calculators:
            return
        
        # Prepare Export Data (Comparison)
        columns = ["Method", "Value"]
        rows = []
        
        for name, calc in lang_calculators:
            try:
                value = calc.calculate(text)
                method_name = name.replace(f"{language} ", "")
                rows.append([method_name, value])
            except Exception:
                method_name = name.replace(f"{language} ", "")
                rows.append([method_name, "Error"])
        
        # Update Visual Dashboard
        self.results_dashboard.display_comparison(text, language, rows)
        
        # Store for potential saving
        self.current_text = text
        self.current_value = 0  # No single value in multi-method mode
        self.current_breakdown = []
        
        # Disable save button in all methods mode
        self.save_button.setEnabled(False)
        
        self.last_export_data = {
            "name": f"Gematria_All_{text}",
            "data": {
                "columns": columns,
                "data": rows,
                "styles": {}
            }
        }
    
    def _save_calculation(self):
        """Save the current calculation to the database."""
        if not self.current_text:
            return
        if self.current_calculator is None:
            QMessageBox.warning(self, "Gematria Calculator", "Cannot save while viewing all methods.")
            return
        
        # Create a simple dialog to get notes and tags
        notes, ok = QInputDialog.getMultiLineText(
            self,
            "Save Calculation",
            f"Saving: {self.current_text} = {self.current_value}\n\nNotes (optional):",
            ""
        )
        
        if not ok:
            return
        
        # Get tags
        tags_str, ok = QInputDialog.getText(
            self,
            "Add Tags",
            "Tags (comma-separated, optional):",
            QLineEdit.EchoMode.Normal,
            ""
        )
        
        if not ok:
            tags_str = ""
        
        # Parse tags
        tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        
        # TODO: Add input field for Source information (e.g. Book, Chapter, Verse)
        source = ""
        
        # Save to database
        try:
            record = self.calculation_service.save_calculation(
                text=self.current_text,
                value=self.current_value,
                calculator=self.current_calculator,
                breakdown=self.current_breakdown,
                notes=notes,
                tags=tags,
                source=source  # TODO: Populate from user input
            )
            
            QMessageBox.information(
                self,
                "Saved",
                f"Calculation saved successfully!\n\n{record.text} = {record.value}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save calculation:\n{str(e)}"
            )

    def _send_to_tablet(self):
        """Send current results to Emerald Tablet."""
        if not self.last_export_data:
            return
            
        if not self.window_manager:
            QMessageBox.warning(self, "Integration Error", "Window Manager not linked.")
            return

        # Open Hub using registry-based lookup
        hub = self.window_manager.open_window_by_key("emerald_tablet")
        
        # Send data to hub
        if hub and hasattr(hub, "receive_import"):
            name = self.last_export_data["name"]
            data = self.last_export_data["data"]
            hub.receive_import(name, data)

    def _on_total_context_menu(self, value: int, pos):
        """Build and show the context menu for the total value."""
        menu = QMenu(self)
        
        # Transitions
        menu.addAction("📗 Send to Emerald Tablet", self._send_to_tablet)
        menu.addAction("📐 Send to Quadset Analysis", lambda: self._send_to_quadset(value))
        menu.addAction("📝 Send to RTF Editor", lambda: self._send_to_rtf_editor(value))
        
        # Mindscape Submenu
        ms_menu = menu.addMenu("🧠 Send to MindScape")
        ms_menu.addAction("Insert into Current Page", self._ms_insert_current)
        ms_menu.addAction("Insert into Existing Page...", self._ms_insert_existing)
        ms_menu.addAction("New Page & Insert...", self._ms_create_page)
        ms_menu.addSeparator()
        ms_menu.addAction("Create New Notebook...", self._ms_new_notebook)
        ms_menu.addAction("Create New Section...", self._ms_new_section)
        
        menu.exec(pos)

    def _send_to_quadset(self, value: int):
        """Send current results to Quadset Analysis."""
        navigation_bus.request_window.emit(
            "quadset_analysis",
            {
                "window_manager": self.window_manager,
                "initial_value": value
            }
        )

    def _send_to_rtf_editor(self, value: int):
        """Send results to RTF Editor."""
        if not self.window_manager: return
        win = self.window_manager.open_window_by_key("document_editor")
        if win:
            # Format high-quality summary
            res_str = f"""
            <div style="font-family: 'Segoe UI', sans-serif;">
                <h2 style="color: {COLORS['focus']}; border-bottom: 2px solid {COLORS['focus']}; padding-bottom: 5px;">Gematria Resonance</h2>
                <p><b>Original Text:</b> <span style="font-size: 1.2em; color: {COLORS['void']};">{self.current_text}</span></p>
                <p><b>Numeric Value:</b> <span style="font-size: 1.5em; font-weight: bold; color: {COLORS['focus']};">{value}</span></p>
                <p><b>System Used:</b> <i style="color: {COLORS['stone']};">{self.current_calculator.name if self.current_calculator else "All Methods"}</i></p>
            </div>
            """
            # DocumentEditorWindow uses 'editor' attribute (RichTextEditor)
            if hasattr(win, "editor"):
                win.editor.set_html(res_str)  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            win.raise_()
            win.activateWindow()

    # --- MindScape Transitions ---

    def _find_active_mindscape(self) -> Optional[QMainWindow]:
        """Locate the active Mindscape window via the Window Manager."""
        if not self.window_manager: return None
        # WindowManager usually tracks windows by key
        return self.window_manager.get_window("mindscape")

    def _ms_insert_current(self):
        """Insert total into current Mindscape page."""
        ms = self._find_active_mindscape()
        if not ms or not ms.page or not ms.page.current_doc_id:  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            QMessageBox.warning(self, "MindScape", "No active Mindscape page found. Open a page first.")
            return
        
        self._ms_add_note(ms.page, self.current_value)  # type: ignore[reportAttributeAccessIssue, reportUnknownArgumentType, reportUnknownMemberType]

    def _ms_add_note(self, page_widget, value: int):
        """Add the gematria result as a note to a page."""
        content = f"""
        <h2 style="color: {COLORS['focus']};">Gematria Resonance</h2>
        <p><b>Text:</b> {self.current_text}</p>
        <p><b>Value:</b> <span style="font-size: 1.4em; font-weight: bold;">{value}</span></p>
        <p><b>System:</b> {self.current_calculator.name if self.current_calculator else "All"}</p>
        """
        if hasattr(page_widget, "canvas"):
            # We need to provide x and y coordinates. 
            # (50, 50) is a safe default for a new projection.
            page_widget.canvas.add_note_container(50, 50, content)
            # Auto-save
            if hasattr(page_widget, "save_page"):
                page_widget.save_page()
            QMessageBox.information(self, "MindScape", "Note projected onto the canvas.")

    def _ms_insert_existing(self):
        """Prompt to select an existing page and insert the result."""
        with notebook_service_context() as service:
            notebooks = service.get_notebooks_with_structure()
            page_map = {} # Display String -> doc_id
            
            for nb in notebooks:
                for sec in nb.sections:
                    pages = service.get_section_pages(sec.id)
                    for page in pages:
                        key = f"{nb.title} > {sec.title} > {page.title}"
                        page_map[key] = page.id
            
            if not page_map:
                QMessageBox.warning(self, "MindScape", "No pages found in the library.")
                return
                
            choice, ok = QInputDialog.getItem(
                self, "Select Page", "Choose target page for resonance:",
                sorted(page_map.keys()), 0, False
            )
            
            if ok and choice:
                doc_id = page_map[choice]
                # Open/Get Mindscape
                ms = self.window_manager.open_window_by_key("mindscape")
                if ms:
                    ms.page.load_node(doc_id)  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
                    self._ms_add_note(ms.page, self.current_value)  # type: ignore[reportAttributeAccessIssue, reportUnknownArgumentType, reportUnknownMemberType]
                    ms.raise_()

    def _ms_create_page(self):
        """Prompt for new page details and insert result."""
        with notebook_service_context() as service:
            notebooks = service.get_notebooks_with_structure()
            sec_map = {} # Display String -> sec_id
            
            for nb in notebooks:
                for sec in nb.sections:
                    key = f"{nb.title} > {sec.title}"
                    sec_map[key] = sec.id
                    
            if not sec_map:
                QMessageBox.warning(self, "MindScape", "No sections found. Create a notebook and section first.")
                return
                
            choice, ok = QInputDialog.getItem(
                self, "Select Section", "Choose section for the new page:",
                sorted(sec_map.keys()), 0, False
            )
            
            if not (ok and choice): return
            
            title, ok = QInputDialog.getText(self, "New Page", "Enter page title:", text=f"Resonance - {self.current_text}")
            if not (ok and title): return
            
            sec_id = sec_map[choice]
            new_page = service.create_page(sec_id, title)
            
            # Open and insert
            ms = self.window_manager.open_window_by_key("mindscape")
            if ms:
                ms.tree.load_tree() # Refresh tree to show new page  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
                ms.page.load_node(new_page.id)  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
                self._ms_add_note(ms.page, self.current_value)  # type: ignore[reportAttributeAccessIssue, reportUnknownArgumentType, reportUnknownMemberType]
                ms.raise_()

    def _ms_new_notebook(self):
        """Create a new notebook."""
        title, ok = QInputDialog.getText(self, "New Notebook", "Enter notebook title:")
        if ok and title:
            with notebook_service_context() as service:
                service.create_notebook(title)
            QMessageBox.information(self, "MindScape", f"Notebook '{title}' created.")
            # Refresh Mindscape if open
            ms = self._find_active_mindscape()
            if ms: ms.tree.load_tree()  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]

    def _ms_new_section(self):
        """Create a new section in a chosen notebook."""
        with notebook_service_context() as service:
            notebooks = service.get_notebooks_with_structure()
            nb_map = {nb.title: nb.id for nb in notebooks}
            
            if not nb_map:
                QMessageBox.warning(self, "MindScape", "No notebooks found.")
                return
                
            nb_choice, ok = QInputDialog.getItem(
                self, "Select Notebook", "Choose notebook for the section:",
                sorted(nb_map.keys()), 0, False
            )
            
            if not (ok and nb_choice): return
            
            sec_title, ok = QInputDialog.getText(self, "New Section", "Enter section title:")
            if ok and sec_title:
                service.create_section(nb_map[nb_choice], sec_title)
                QMessageBox.information(self, "MindScape", f"Section '{sec_title}' created.")
                ms = self._find_active_mindscape()
                if ms: ms.tree.load_tree()  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
