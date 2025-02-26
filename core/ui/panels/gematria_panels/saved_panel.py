"""
Saved Gematria Values Panel implementation
"""
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, 
    QLineEdit, QListWidget, QListWidgetItem, QComboBox, QCheckBox,
    QSpinBox, QMenu, QMessageBox, QInputDialog, QDialog, QColorDialog,
    QApplication, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, 
    QGridLayout
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QIcon, QPixmap, QCursor

import logging
import os
from core.ui.panels.base.panel import BasePanel
from databases.gematria.word_repository import WordRepository
from core.gematria.cipher_manager import CipherManager

logger = logging.getLogger(__name__)

class SavedPanel(BasePanel):
    """Panel for managing saved gematria values"""
    
    def __init__(self, parent=None, word_repository=None):
        """Initialize the SavedPanel"""
        # Initialize the word_repository before calling super().__init__
        # to ensure it's available during setup_ui
        self._word_repository = None
        
        super().__init__(parent)
        self.setWindowTitle("Saved Values")
        
        # Initialize repositories
        self.word_repository = word_repository or WordRepository()
        self.cipher_manager = CipherManager()
        self.cipher_manager.load_all_ciphers()
        
        # Connect signals first
        self.connect_signals()
        
        # Then load initial data
        self.load_ciphers()
        
        # Load initial results after initialization
        QApplication.processEvents()
        self.perform_search()
        
    @property
    def word_repository(self):
        """Get the word repository"""
        if self._word_repository is None:
            self._word_repository = WordRepository()
        return self._word_repository
        
    @word_repository.setter
    def word_repository(self, value):
        """Set the word repository"""
        self._word_repository = value

    def setup_ui(self):
        """Set up the saved values panel UI"""
        # Guard against multiple initialization
        if hasattr(self, 'initialized') and self.initialized:
            logger.debug("Saved panel UI already initialized, skipping setup")
            return
            
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("Search Saved Calculations")
        header.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
        """)
        
        # Search section
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter text or value...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        
        # Add cipher filter dropdown
        self.cipher_filter = QComboBox()
        self.cipher_filter.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                min-width: 150px;
            }
        """)
        
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.perform_search)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.cipher_filter)
        search_layout.addWidget(self.search_button)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:hover {
                background: #f0f0f0;
            }
        """)
        
        # Enable context menu for results list
        self.results_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.results_list.customContextMenuRequested.connect(self.show_context_menu)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666;")
        
        # Add to main layout
        layout.addWidget(header)
        layout.addLayout(search_layout)
        layout.addWidget(self.results_list)  # Add results list
        layout.addWidget(self.status_label)  # Add status label
        
        # Add Advanced Filters section
        filter_group = QGroupBox("Advanced Filters")
        filter_layout = QGridLayout()
        
        # Value Range Filter
        self.value_range_check = QCheckBox("Value Range")
        self.min_value = QSpinBox()
        self.max_value = QSpinBox()
        self.min_value.setRange(0, 99999)
        self.max_value.setRange(0, 99999)
        self.min_value.setEnabled(False)
        self.max_value.setEnabled(False)
        
        # Date Filter
        self.date_range = QComboBox()
        self.date_range.addItems([
            "Any time",
            "Past day",
            "Past week",
            "Past month",
            "Custom..."
        ])
        
        # Categories Filter
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.load_categories()
        
        # Tags Filter
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Enter tags (comma separated)")
        
        # Layout for filters
        filter_layout.addWidget(QLabel("Value Range:"), 0, 0)
        filter_layout.addWidget(self.value_range_check, 0, 1)
        filter_layout.addWidget(self.min_value, 0, 2)
        filter_layout.addWidget(QLabel("to"), 0, 3)
        filter_layout.addWidget(self.max_value, 0, 4)
        
        filter_layout.addWidget(QLabel("Date:"), 1, 0)
        filter_layout.addWidget(self.date_range, 1, 1, 1, 4)
        
        filter_layout.addWidget(QLabel("Category:"), 2, 0)
        filter_layout.addWidget(self.category_filter, 2, 1, 1, 4)
        
        filter_layout.addWidget(QLabel("Tags:"), 3, 0)
        filter_layout.addWidget(self.tags_input, 3, 1, 1, 4)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Add category management section
        category_group = QGroupBox("Category Management")
        category_layout = QVBoxLayout()
        
        # Category creation
        create_layout = QHBoxLayout()
        self.new_category_input = QLineEdit()
        self.new_category_input.setPlaceholderText("New category name...")
        self.category_color = QPushButton("Pick Color")
        self.category_color.clicked.connect(self._pick_category_color)
        self.add_category_btn = QPushButton("Add Category")
        self.add_category_btn.clicked.connect(self.add_new_category)
        
        create_layout.addWidget(self.new_category_input)
        create_layout.addWidget(self.category_color)
        create_layout.addWidget(self.add_category_btn)
        
        # Category assignment
        assign_layout = QHBoxLayout()
        self.assign_category_btn = QPushButton("Assign Category")
        self.assign_category_btn.clicked.connect(self.assign_category_to_selected)
        self.remove_category_btn = QPushButton("Remove Category")
        self.remove_category_btn.clicked.connect(self.remove_category_from_selected)
        
        assign_layout.addWidget(self.assign_category_btn)
        assign_layout.addWidget(self.remove_category_btn)
        
        # Add Edit Categories button
        edit_layout = QHBoxLayout()
        self.edit_categories_btn = QPushButton("Edit Categories")
        self.edit_categories_btn.clicked.connect(self.show_category_editor)
        edit_layout.addWidget(self.edit_categories_btn)
        
        category_layout.addLayout(create_layout)
        category_layout.addLayout(assign_layout)
        category_layout.addLayout(edit_layout)
        
        category_group.setLayout(category_layout)
        
        layout.addWidget(category_group)
        
        # Add Import/Export section
        import_export_group = QGroupBox("Import/Export")
        import_export_layout = QHBoxLayout()
        
        self.import_button = QPushButton("Import Values")
        self.export_button = QPushButton("Export Values")
        
        import_export_layout.addWidget(self.import_button)
        import_export_layout.addWidget(self.export_button)
        
        import_export_group.setLayout(import_export_layout)
        layout.addWidget(import_export_group)
        
        # Connect signals
        self.value_range_check.stateChanged.connect(self._toggle_value_range)
        self.import_button.clicked.connect(self.import_saved_values)
        self.export_button.clicked.connect(self.export_saved_values)
        
        self.content_layout.addLayout(layout)
        self.initialized = True

    def add_sample_data(self):
        """Add sample data to the saved values table"""
        sample_data = [
            ("DIVINE LIGHT", "English Ordinal", "111", "Spiritual illumination"),
            ("SACRED WISDOM", "English Ordinal", "137", "Connection to ancient knowledge"),
            ("COSMIC BALANCE", "English Reduction", "63", "Harmony of universal forces"),
            ("", "Hebrew Gematria", "441", "Hebrew word for 'truth'"),
            ("ENLIGHTENMENT", "English Ordinal", "163", "Spiritual awakening"),
        ]
        
        for phrase, cipher, value, notes in sample_data:
            row = self.saved_table.rowCount()
            self.saved_table.insertRow(row)
            
            self.saved_table.setItem(row, 0, QTableWidgetItem(phrase))
            self.saved_table.setItem(row, 1, QTableWidgetItem(cipher))
            self.saved_table.setItem(row, 2, QTableWidgetItem(value))
            self.saved_table.setItem(row, 3, QTableWidgetItem(notes))
            
    def add_new(self):
        """Add a new saved value"""
        # This would open a dialog to add a new value
        logger.info("Add new value functionality would be implemented here")
        
    def delete_selected(self):
        """Delete selected saved values"""
        selected_rows = set()
        for item in self.saved_table.selectedItems():
            selected_rows.add(item.row())
            
        # Remove rows in reverse order to avoid index issues
        for row in sorted(selected_rows, reverse=True):
            self.saved_table.removeRow(row)
            
    def export_saved(self):
        """Export saved values to a file"""
        # This would be implemented to export to CSV or other format
        logger.info("Export saved values functionality would be implemented here")

    def load_ciphers(self):
        """Load all available ciphers into the filter dropdown"""
        # Clear and add "All Ciphers" option
        self.cipher_filter.clear()
        self.cipher_filter.addItem("All Ciphers")
        
        # Add built-in ciphers
        built_in_ciphers = [
            'TQ English',
            'Hebrew Standard',
            'Hebrew Gadol',
            'Greek'
        ]
        self.cipher_filter.addItems(built_in_ciphers)
        
        # Add separator and custom ciphers
        if self.cipher_manager.get_cipher_names():
            self.cipher_filter.insertSeparator(len(built_in_ciphers) + 1)
            for cipher_name in self.cipher_manager.get_cipher_names():
                self.cipher_filter.addItem(f"Custom: {cipher_name}")

    def _toggle_value_range(self, state):
        """Enable/disable value range inputs"""
        self.min_value.setEnabled(bool(state))
        self.max_value.setEnabled(bool(state))
        
    def load_categories(self):
        """Load categories from database"""
        categories = self.word_repository.get_categories()
        for category in categories:
            self.category_filter.addItem(category['name'])
            
    def perform_search(self):
        """Enhanced search with filters"""
        search_text = self.search_input.text()
        selected_cipher = self.cipher_filter.currentText()
        
        # Handle custom cipher format
        if selected_cipher.startswith("Custom: "):
            selected_cipher = selected_cipher[8:]  # Remove "Custom: " prefix
        
        # Build search criteria
        criteria = {
            'text': search_text,
            'cipher': None if selected_cipher == "All Ciphers" else selected_cipher,
            'value_range': None,
            'date_range': None,
            'category': None,
            'tags': []
        }
        
        # Add value range if enabled
        if self.value_range_check.isChecked():
            criteria['value_range'] = (self.min_value.value(), self.max_value.value())
            
        # Add date range
        date_selection = self.date_range.currentText()
        if date_selection != "Any time":
            criteria['date_range'] = date_selection
            
        # Add category
        if self.category_filter.currentText() != "All Categories":
            criteria['category'] = self.category_filter.currentText()
            
        # Add tags
        if self.tags_input.text().strip():
            criteria['tags'] = [tag.strip() for tag in self.tags_input.text().split(',')]
        
        # Debug info
        print(f"Search criteria: {criteria}")
            
        # Perform search
        try:
            # Try advanced search first
            results = self.word_repository.advanced_search(criteria)
            print(f"Search returned {len(results)} results")
            
            # If no results and no specific criteria, fall back to get all words
            if not results and not any([search_text, 
                                       selected_cipher != "All Ciphers", 
                                       self.value_range_check.isChecked(),
                                       date_selection != "Any time",
                                       self.category_filter.currentText() != "All Categories",
                                       self.tags_input.text().strip()]):
                print("No specific search criteria, getting all words")
                results = self.word_repository.get_all_words()
                print(f"Get all words returned {len(results)} results")
                
            self.display_results(results)
        except Exception as e:
            import traceback
            print(f"Error performing search: {e}")
            print(traceback.format_exc())
            self.status_label.setText(f"Error: {str(e)}")
            self.results_list.clear()

    def display_results(self, results):
        """Display search results in the results list"""
        # Clear previous results
        self.results_list.clear()
        
        if not results:
            self.status_label.setText("No matches found")
            return
        
        print(f"Displaying {len(results)} results")
            
        # Add results to list widget
        for result in results:
            try:
                # Handle different result formats
                if len(result) >= 3:
                    if len(result) >= 4:
                        text, value, cipher, category = result
                    else:
                        text, value, cipher = result
                        category = None
                        
                    # Create display text
                    display_text = f"{text} ({value} in {cipher})"
                    print(f"Adding result: {display_text}")
                    
                    item = QListWidgetItem(display_text)
                    
                    # Get categories for this phrase
                    try:
                        categories = self.word_repository.get_phrase_categories(text, cipher)
                        if categories:
                            # Set tooltip with all categories
                            category_names = ", ".join(cat[0] for cat in categories)
                            item.setToolTip(f"Categories: {category_names}")
                            
                            # Set color based on first category
                            item.setForeground(QColor(categories[0][1]))
                        else:
                            item.setToolTip("No categories")
                            item.setForeground(QColor("#000000"))
                    except Exception as e:
                        print(f"Error getting categories for {text}: {e}")
                        item.setToolTip("Error loading categories")
                        item.setForeground(QColor("#000000"))
                        
                    self.results_list.addItem(item)
                else:
                    print(f"Skipping invalid result format: {result}")
            except Exception as e:
                print(f"Error displaying result {result}: {e}")
            
        # Update status
        self.status_label.setText(f"Found {self.results_list.count()} matches")

    def _pick_category_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.category_color.setStyleSheet(f"background-color: {color.name()}")
            self.current_category_color = color.name()

    def add_new_category(self):
        """Add a new category"""
        name = self.new_category_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Category name cannot be empty")
            return
            
        color = getattr(self, 'current_category_color', "#808080")
        if self.word_repository.add_category(name, color):
            # Refresh categories in UI
            self.load_categories()
            # Refresh current display to show updated colors
            self.perform_search()
            self.new_category_input.clear()
            QMessageBox.information(self, "Success", f"Added category: {name}")
        else:
            QMessageBox.warning(self, "Error", f"Failed to add category: {name}")

    def assign_category_to_selected(self):
        selected_items = self.results_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Please select a phrase first")
            return
            
        category = self.category_filter.currentText()
        if category == "All Categories":
            QMessageBox.warning(self, "Error", "Please select a specific category")
            return
            
        for item in selected_items:
            # Parse text and cipher from item text
            text = item.text().split(" (")[0]
            cipher = item.text().split("in ")[1].rstrip(")")
            
            if self.word_repository.assign_category(text, cipher, category):
                # Update item display
                current_tooltip = item.toolTip()
                categories = self.word_repository.get_phrase_categories(text, cipher)
                new_tooltip = "Categories: " + ", ".join(cat[0] for cat in categories)
                item.setToolTip(new_tooltip)
                
                # Add visual indicator
                item.setForeground(QColor(self.word_repository.get_category_color(category)))

    def remove_category_from_selected(self):
        selected_items = self.results_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Please select a phrase first")
            return
            
        category = self.category_filter.currentText()
        if category == "All Categories":
            QMessageBox.warning(self, "Error", "Please select a specific category")
            return
            
        for item in selected_items:
            text = item.text().split(" (")[0]
            cipher = item.text().split("in ")[1].rstrip(")")
            
            if self.word_repository.remove_category(text, cipher, category):
                # Update item display
                categories = self.word_repository.get_phrase_categories(text, cipher)
                if categories:
                    new_tooltip = "Categories: " + ", ".join(cat[0] for cat in categories)
                    item.setToolTip(new_tooltip)
                    # Update color to first remaining category
                    item.setForeground(QColor(categories[0][1]))
                else:
                    item.setToolTip("")
                    item.setForeground(QColor("#000000"))  # Reset to default color

    def show_context_menu(self, position):
        """Show context menu for right-clicked phrase"""
        item = self.results_list.itemAt(position)
        if not item:
            return
            
        menu = QMenu()
        
        # Get text and cipher from item
        text = item.text().split(" (")[0]
        cipher = item.text().split("in ")[1].rstrip(")")
        
        # Categories submenu
        categories_menu = QMenu("Assign Category")
        categories = self.word_repository.get_categories()
        
        # Add all available categories
        for category in categories:
            action = categories_menu.addAction(category['name'])
            # Use lambda with default argument to avoid late binding
            action.triggered.connect(
                lambda checked, c=category['name']: self.assign_category_to_phrase(text, cipher, c)
            )
        
        # Add separator and "New Category" option
        if categories:
            categories_menu.addSeparator()
        categories_menu.addAction("New Category...", lambda: self.create_category_for_phrase(text, cipher))
        
        menu.addMenu(categories_menu)
        
        # Get current categories for this phrase
        current_categories = self.word_repository.get_phrase_categories(text, cipher)
        if current_categories:
            remove_menu = QMenu("Remove Category")
            for cat_name, cat_color, _ in current_categories:
                action = remove_menu.addAction(cat_name)
                action.triggered.connect(
                    lambda checked, c=cat_name: self.remove_category_from_phrase(text, cipher, c)
                )
            menu.addMenu(remove_menu)
        
        menu.addSeparator()
        
        # Copy options
        copy_menu = QMenu("Copy")
        copy_menu.addAction("Copy Text", lambda: QApplication.clipboard().setText(text))
        copy_menu.addAction("Copy Value", lambda: QApplication.clipboard().setText(
            item.text().split("(")[1].split(")")[0]
        ))
        menu.addMenu(copy_menu)
        
        # Delete option
        menu.addSeparator()
        menu.addAction("Delete", lambda: self.delete_phrase(text, cipher))
        
        menu.exec(self.results_list.viewport().mapToGlobal(position))

    def assign_category_to_phrase(self, text, cipher, category):
        """Assign a category to a specific phrase"""
        if self.word_repository.assign_category(text, cipher, category):
            self.update_item_display(text, cipher)
            QMessageBox.information(self, "Success", f"Added category '{category}' to phrase")
        else:
            QMessageBox.warning(self, "Error", "Failed to assign category")

    def create_category_for_phrase(self, text, cipher):
        """Create a new category and assign it to the phrase"""
        name, ok = QInputDialog.getText(self, "New Category", "Enter category name:")
        if ok and name.strip():
            color = QColorDialog.getColor()
            if color.isValid():
                if self.word_repository.add_category(name, color.name()):
                    self.load_categories()  # Refresh category list
                    self.assign_category_to_phrase(text, cipher, name)
                else:
                    QMessageBox.warning(self, "Error", "Failed to create category")

    def remove_category_from_phrase(self, text, cipher, category):
        """Remove a category from a specific phrase"""
        if self.word_repository.remove_category(text, cipher, category):
            self.update_item_display(text, cipher)
            QMessageBox.information(self, "Success", f"Removed category '{category}' from phrase")
        else:
            QMessageBox.warning(self, "Error", "Failed to remove category")

    def update_item_display(self, text, cipher):
        """Update the display of an item after category changes"""
        # Find the item in the list
        for i in range(self.results_list.count()):
            item = self.results_list.item(i)
            if text in item.text() and cipher in item.text():
                # Update categories display
                categories = self.word_repository.get_phrase_categories(text, cipher)
                if categories:
                    new_tooltip = "Categories: " + ", ".join(cat[0] for cat in categories)
                    item.setToolTip(new_tooltip)
                    # Update color to first category's color
                    item.setForeground(QColor(categories[0][1]))
                else:
                    item.setToolTip("")
                    item.setForeground(QColor("#000000"))
                break

    def delete_phrase(self, text, cipher):
        """Delete a phrase from saved words"""
        reply = QMessageBox.question(
            self, 
            "Confirm Delete",
            f"Are you sure you want to delete this phrase?\n\n{text}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.word_repository.delete_word(text, cipher):
                # Remove from list
                for i in range(self.results_list.count()):
                    item = self.results_list.item(i)
                    if text in item.text() and cipher in item.text():
                        self.results_list.takeItem(i)
                        break
                QMessageBox.information(self, "Success", "Phrase deleted successfully")
            else:
                QMessageBox.warning(self, "Error", "Failed to delete phrase")

    def show_category_editor(self):
        """Show dialog to edit existing categories"""
        menu = QMenu(self)
        categories = self.word_repository.get_categories()
        
        for category in categories:
            action = menu.addAction(category['name'])
            # Set color indicator in the menu
            pixmap = QPixmap(16, 16)
            pixmap.fill(QColor(category['color']))
            action.setIcon(QIcon(pixmap))
            action.triggered.connect(
                lambda checked, c=category: self.edit_category(c)
            )
            
        if not categories:
            menu.addAction("No categories available").setEnabled(False)
            
        menu.exec(QCursor.pos())

    def edit_category(self, category):
        """Edit an existing category"""
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit Category: {category['name']}")
        layout = QVBoxLayout()
        
        # Name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        name_input = QLineEdit(category['name'])
        name_layout.addWidget(name_input)
        layout.addLayout(name_layout)
        
        # Color button
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        color_btn = QPushButton()
        color_btn.setFixedSize(50, 25)
        current_color = category['color']
        color_btn.setStyleSheet(f"background-color: {current_color};")
        
        def pick_color():
            color = QColorDialog.getColor(QColor(current_color))
            if color.isValid():
                color_btn.setStyleSheet(f"background-color: {color.name()};")
                color_btn.color = color.name()
                
        color_layout.addWidget(color_btn)
        color_btn.clicked.connect(pick_color)
        color_btn.color = current_color
        layout.addLayout(color_layout)
        
        # Preview
        preview = QLabel("Preview")
        preview.setStyleSheet(f"""
            color: {current_color};
            font-size: 14px;
            padding: 5px;
            border: 1px solid {current_color};
            border-radius: 3px;
        """)
        layout.addWidget(preview)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # Connect buttons
        save_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name = name_input.text().strip()
            new_color = color_btn.color
            
            if not new_name:
                QMessageBox.warning(self, "Error", "Category name cannot be empty")
                return
                
            if self.word_repository.update_category(category['name'], new_name, new_color):
                # Refresh categories in UI
                self.load_categories()
                # Refresh current display to show updated colors
                self.perform_search()
                QMessageBox.information(self, "Success", "Category updated successfully")
            else:
                QMessageBox.warning(self, "Error", "Failed to update category")

    def connect_signals(self):
        """Connect UI signals to their handlers"""
        # Search connections
        self.search_button.clicked.connect(self.perform_search)
        self.search_input.returnPressed.connect(self.perform_search)
        
        # Value range checkbox
        self.value_range_check.stateChanged.connect(self._toggle_value_range)
        
        # Category management
        # These are already connected in setup_ui
        # self.category_color.clicked.connect(self._pick_category_color)
        # self.add_category_btn.clicked.connect(self.add_new_category)
        # self.assign_category_btn.clicked.connect(self.assign_category_to_selected)
        # self.remove_category_btn.clicked.connect(self.remove_category_from_selected)
        # self.edit_categories_btn.clicked.connect(self.show_category_editor)
        
        # Context menu
        # This is already connected in setup_ui
        # self.results_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # self.results_list.customContextMenuRequested.connect(self.show_context_menu)
        
        # Import/Export
        # These are already connected in setup_ui
        # self.import_button.clicked.connect(self.import_saved_values)
        # self.export_button.clicked.connect(self.export_saved_values)

    def import_saved_values(self):
        """Import saved values from a JSON file"""
        from PyQt6.QtWidgets import QFileDialog
        import json
        import os
        
        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Saved Values",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Validate format
            if not isinstance(data, list):
                QMessageBox.warning(self, "Error", "Invalid file format")
                return
                
            # Import each entry
            imported_count = 0
            for entry in data:
                # Check required fields
                if not all(key in entry for key in ['text', 'value', 'cipher']):
                    continue
                    
                # Add to repository
                if self.word_repository.add_word(
                    entry['text'],
                    entry['value'],
                    entry['cipher'],
                    entry.get('tags', []),
                    entry.get('notes', '')
                ):
                    imported_count += 1
                    
            # Refresh display
            self.perform_search()
            QMessageBox.information(
                self, 
                "Import Complete", 
                f"Successfully imported {imported_count} entries"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import: {str(e)}")
            logger.error(f"Import error: {str(e)}")
            
    def export_saved_values(self):
        """Export saved values to a JSON file"""
        from PyQt6.QtWidgets import QFileDialog
        import json
        import os
        
        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Saved Values",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
            
        # Add .json extension if not present
        if not file_path.lower().endswith('.json'):
            file_path += '.json'
            
        try:
            # Get all saved values
            all_values = self.word_repository.get_all_words()
            
            # Format for export
            export_data = []
            for text, value, cipher, date_added in all_values:
                # Get categories and tags
                categories = self.word_repository.get_phrase_categories(text, cipher)
                tags = self.word_repository.get_phrase_tags(text, cipher)
                notes = self.word_repository.get_phrase_notes(text, cipher)
                
                export_data.append({
                    'text': text,
                    'value': value,
                    'cipher': cipher,
                    'date_added': date_added,
                    'categories': [cat[0] for cat in categories],
                    'tags': tags,
                    'notes': notes
                })
                
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
                
            QMessageBox.information(
                self, 
                "Export Complete", 
                f"Successfully exported {len(export_data)} entries to {os.path.basename(file_path)}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")
            logger.error(f"Export error: {str(e)}")
