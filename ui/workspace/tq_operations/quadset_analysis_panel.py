from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox, QTabWidget, QFrame, QMenu
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from core.tq_operations.base_converter import BaseConverter, TernaryVisualizer
from core.tq_operations.number_properties import NumberProperties
from .geometry.visualizer import GeometryVisualizer
from .geometry.items import GeometryLine
import math
import re

class QuadsetAnalysisPanel(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.base_converter = BaseConverter()
        self.number_properties = NumberProperties()
        self.main_window = main_window  # Store the reference directly
        self.init_ui()

    def init_ui(self):
        # Main vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # Top bar with input and stats
        top_bar = QHBoxLayout()
        input_box = QHBoxLayout()
        input_label = QLabel("Input:")
        self.number_input = QLineEdit()
        analyze_btn = QPushButton("Analyze")
        analyze_btn.clicked.connect(self.perform_analysis)
        self.number_input.returnPressed.connect(self.perform_analysis)
        
        input_box.addWidget(input_label)
        input_box.addWidget(self.number_input)
        input_box.addWidget(analyze_btn)
        
        self.stats_label = QLabel("Last Analysis: None")
        top_bar.addLayout(input_box)
        top_bar.addStretch()
        top_bar.addWidget(self.stats_label)
        
        # Three column layout
        columns_layout = QHBoxLayout()
        
        # Left column - Relations
        relations_group = QGroupBox("Relations")
        relations_layout = QVBoxLayout(relations_group)
        self.relations_labels = {}
        pairs = [('Base', 'Conrune'), ('Base', 'Reune'), ('Base', 'Conreune'),
                ('Conrune', 'Reune'), ('Conrune', 'Conreune'), ('Reune', 'Conreune')]
        
        # Add Differences (Delta) section
        delta_header = QLabel("Differences (Δ):")
        delta_header.setStyleSheet("font-weight: bold;")
        relations_layout.addWidget(delta_header)
        
        for pair in pairs:
            label = QLabel()
            self.relations_labels[f"Δ_{pair[0]}_{pair[1]}"] = label
            relations_layout.addWidget(label)
        
        # Add separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        relations_layout.addWidget(separator)
        
        # Add Sums (Sigma) section
        sigma_header = QLabel("Sums (Σ):")
        sigma_header.setStyleSheet("font-weight: bold;")
        relations_layout.addWidget(sigma_header)
        
        for pair in pairs:
            label = QLabel()
            self.relations_labels[f"Σ_{pair[0]}_{pair[1]}"] = label
            relations_layout.addWidget(label)
            
        relations_layout.addStretch()
        
        # Middle column - Visualizations
        visual_group = QGroupBox("Quadset")
        visual_layout = QGridLayout(visual_group)
        self.labels = {}
        self.visualizers = {}
        positions = ['Base', 'Conrune', 'Reune', 'Conreune']
        
        for i, pos in enumerate(positions):
            row = i // 2 * 2
            col = i % 2
            
            # Container for each position
            container = QVBoxLayout()
            self.labels[f"{pos}_ternary"] = QLabel()
            self.labels[f"{pos}_decimal"] = QLabel()
            self.visualizers[pos] = TernaryVisualizer()
            
            container.addWidget(QLabel(pos))
            container.addWidget(self.labels[f"{pos}_ternary"])
            container.addWidget(self.labels[f"{pos}_decimal"])
            container.addWidget(self.visualizers[pos])
            
            visual_layout.addLayout(container, row, col)
        
        # Right column - Properties
        self.properties_tabs = QTabWidget()
        self.properties_widgets = {}
        
        for pos in positions:
            tab = QWidget()
            layout = QVBoxLayout(tab)
            self.properties_widgets[pos] = layout
            layout.addStretch()
            self.properties_tabs.addTab(tab, pos)
        
        # Add the three columns
        columns_layout.addWidget(relations_group)
        columns_layout.addWidget(visual_group)
        columns_layout.addWidget(self.properties_tabs)
        
        # Add everything to main layout
        main_layout.addLayout(top_bar)
        main_layout.addLayout(columns_layout)
        
        # Add status bar
        self.create_status_bar()

    def format_large_number(self, n):
        """Format large numbers with commas for readability"""
        return f"{n:,}"

    def perform_analysis(self):
        try:
            # Get and validate input
            decimal_num = int(self.number_input.text())
            if decimal_num < 0:
                raise ValueError("Number must be positive")
            if decimal_num > 999999999:
                raise ValueError("Number must be less than 1 billion")
            
            # Convert to ternary - don't pad if longer than 6 digits
            base_ternary = self.base_converter.to_base_3(decimal_num)
            
            if len(base_ternary) < 6:
                base_ternary = base_ternary.zfill(6)
            
            # Calculate all variations
            variations = {
                'Base': base_ternary,
                'Conrune': self.get_conrune(base_ternary),
                'Reune': self.get_reune(base_ternary),
            }
            variations['Conreune'] = self.get_conrune(variations['Reune'])
            
            # Update display for each variation
            for name, ternary in variations.items():
                # Update ternary label with formatted text
                self.labels[f"{name}_ternary"].setText(f"Ternary: {ternary}")
                
                # Convert to decimal and update label with formatted text
                decimal = self.base_converter.to_decimal(ternary)
                self.labels[f"{name}_decimal"].setText(f"Decimal: {decimal}")
                
                # Update visualizer
                self.visualizers[name].display_ternary(ternary)
                
                # Update properties for each number
                self.update_properties(name, decimal, variations)
            
            # Update relationships after all numbers are processed
            self.update_relationships(variations)
            
        except Exception as e:
            for name in ['Base', 'Conrune', 'Reune', 'Conreune']:
                self.labels[f"{name}_ternary"].setText("Error")
                self.labels[f"{name}_decimal"].setText(str(e))
                self.visualizers[name].clear()
                
                # Clear properties
                layout = self.properties_widgets[name]
                for i in reversed(range(layout.count())): 
                    widget = layout.itemAt(i).widget()
                    if widget:
                        widget.setParent(None)
                        
            # Clear relationships
            for label in self.relations_labels.values():
                label.setText("")

    def get_conrune(self, ternary):
        """Convert 1s to 2s and 2s to 1s, leave 0s unchanged"""
        return ''.join('1' if d == '2' else '2' if d == '1' else '0' for d in ternary)

    def get_reune(self, ternary):
        """Reverse the order of digits"""
        return ternary[::-1]

    def clear_all(self):
        """Clear all displays and results"""
        self.number_input.clear()
        for name in ['Base', 'Conrune', 'Reune', 'Conreune']:
            self.labels[f"{name}_ternary"].setText("")
            self.labels[f"{name}_decimal"].setText("")
            self.visualizers[name].clear()
            
            # Clear properties tab
            layout = self.properties_widgets[name]
            for i in reversed(range(layout.count())): 
                layout.itemAt(i).widget().setParent(None)
        
        # Clear relationships
        for label in self.relations_labels.values():
            label.setText("")

    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.perform_analysis()
        elif event.key() == Qt.Key_Escape:
            self.clear_all()

    def update_properties(self, name, decimal_num, variations):
        """Update the properties tab for a given number"""
        layout = self.properties_widgets[name]
        
        # Clear existing properties
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            
        # Add properties
        properties = [
            ("Decimal", self.format_large_number(decimal_num)),
        ]
        
        # Optimize factor calculation for large numbers
        if decimal_num < 1000000:  # Only calculate factors for reasonable numbers
            factors = self.number_properties.get_factors(decimal_num)
            properties.extend([
                ("Factors", ", ".join(map(self.format_large_number, factors))),
                ("Number of Factors", self.format_large_number(len(factors))),
                ("Sum of Factors", self.format_large_number(sum(factors))),
            ])
        else:
            properties.extend([
                ("Factors", "Too large to calculate"),
                ("Number of Factors", "Too large to calculate"),
                ("Sum of Factors", "Too large to calculate"),
            ])
        
        print("Calculating prime status...")
        is_prime = self.number_properties.is_prime(decimal_num)
        if is_prime:
            prime_index = self.number_properties.get_prime_index(decimal_num)
            properties.append(("Is Prime", f"Yes - #{prime_index}"))
        else:
            properties.append(("Is Prime", "No"))
            print("Calculating prime factors...")
            prime_factors = self.number_properties.get_prime_factors(decimal_num)
            properties.append(("Prime Factors", " × ".join(map(str, prime_factors))))

        # Polygonal numbers
        polygonal = self.number_properties.is_polygonal(decimal_num)
        if polygonal:
            poly_str = ", ".join(f"{s}-gonal(n={pos})" for s, pos in polygonal)
            properties.append(("Polygonal", poly_str))

        # Centered polygonal numbers
        centered = self.number_properties.is_centered_polygonal(decimal_num)
        if centered:
            centered_str = ", ".join(f"centered {s}-gonal(n={pos})" for s, pos in centered)
            properties.append(("Centered Polygonal", centered_str))

        # Star number
        star_results = self.number_properties.is_star_number(decimal_num)
        if star_results:
            star_str = ", ".join(f"{points}-pointed star(n={pos})" for points, pos in star_results)
            properties.append(("Star Number", f"Yes - {star_str}"))

        # Palindrome properties
        if str(decimal_num) == str(decimal_num)[::-1]:
            properties.append(("Palindrome", "Yes"))
        else:
            iterations, final = self.number_properties.palindrome_iterations(decimal_num)
            properties.append(("Palindrome", f"No - {iterations} iterations to {final}"))

        # Fibonacci check
        if self.number_properties.is_fibonacci(decimal_num):
            properties.append(("Fibonacci", "Yes"))

        # Happy number
        properties.append(("Happy Number", "Yes" if self.number_properties.is_happy(decimal_num) else "No"))

        # Aliquot sum
        aliquot_sum, abundance, diff = self.number_properties.aliquot_sum(decimal_num)
        properties.append(("Aliquot Sum", f"{aliquot_sum} ({abundance} by {diff})"))

        # Harshad/Niven number
        harshad = self.number_properties.is_harshad(decimal_num)
        if harshad:
            digit_sum, quotient = harshad
            properties.append(("Harshad/Niven", f"Yes - {decimal_num} = {digit_sum} × {quotient}"))
        else:
            properties.append(("Harshad/Niven", "No"))

        # GCD and LCM with other numbers in quadset
        other_numbers = [self.base_converter.to_decimal(v) for v in variations.values() if v != variations[name]]
        for other_num in other_numbers:
            gcd = self.number_properties.gcd(decimal_num, other_num)
            lcm = self.number_properties.lcm(decimal_num, other_num)
            properties.extend([
                (f"GCD with {other_num}", str(gcd)),
                (f"LCM with {other_num}", str(lcm))
            ])

        for prop_name, value in properties:
            label = self.create_property_label(prop_name, value)
            layout.addWidget(label)
        
        layout.addStretch()

    def create_property_label(self, prop_type, value):
        """Create a clickable label for properties that have visualizations."""
        label = QLabel(f"{prop_type}: {value}")
        
        # Make properties clickable if they have visualizations
        if any(x in prop_type.lower() for x in [
            "star", "polygonal", "centered", "triangular", "square"
        ]):
            label.setStyleSheet("QLabel { color: blue; text-decoration: underline; }")
            label.setCursor(Qt.PointingHandCursor)
            label.mousePressEvent = lambda e: self.show_geometry_visualization(prop_type, value)
        
        return label

    def get_digital_root(self, n):
        """Calculate the digital root of a number"""
        while n > 9:
            n = sum(int(d) for d in str(n))
        return n

    def is_perfect_square(self, n):
        """Check if a number is a perfect square"""
        root = int(n ** 0.5)
        return root * root == n

    def update_relationships(self, variations):
        """Update the relationships panel with differences and sums"""
        numbers = {name: self.base_converter.to_decimal(ternary) 
                  for name, ternary in variations.items()}
        
        pairs = [('Base', 'Conrune'), ('Base', 'Reune'), ('Base', 'Conreune'),
                ('Conrune', 'Reune'), ('Conrune', 'Conreune'), ('Reune', 'Conreune')]
        
        style = """
            QLabel {
                font-family: monospace;
                padding: 3px;
            }
        """
        
        for pair in pairs:
            # Calculate and display difference with formatting
            diff = abs(numbers[pair[0]] - numbers[pair[1]])
            self.relations_labels[f"Δ_{pair[0]}_{pair[1]}"].setText(
                f"{pair[0]} ↔ {pair[1]}: {self.format_large_number(diff)}")
            self.relations_labels[f"Δ_{pair[0]}_{pair[1]}"].setStyleSheet(style)
            
            # Calculate and display sum with formatting
            sum_val = numbers[pair[0]] + numbers[pair[1]]
            self.relations_labels[f"Σ_{pair[0]}_{pair[1]}"].setText(
                f"{pair[0]} ↔ {pair[1]}: {self.format_large_number(sum_val)}")
            self.relations_labels[f"Σ_{pair[0]}_{pair[1]}"].setStyleSheet(style)

    def check_widget_hierarchy(self, widget, level=0):
        """Debug method to check widget hierarchy"""
        indent = "  " * level
        print(f"{indent}Widget: {widget.__class__.__name__}")
        if hasattr(widget, 'layout'):
            layout = widget.layout()
            if layout:
                print(f"{indent}Layout: {layout.__class__.__name__}")
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    if item.widget():
                        self.check_widget_hierarchy(item.widget(), level + 1)
                    elif item.layout():
                        print(f"{indent}  Nested layout: {item.layout().__class__.__name__}")

    def update_properties_panel(self, properties):
        """Update the properties panel with the given properties."""
        # Clear existing widgets
        for i in reversed(range(self.properties_layout.count())): 
            self.properties_layout.itemAt(i).widget().setParent(None)
            
        layout = self.properties_layout
        
        for prop_name, value in properties:
            label = QLabel(f"{prop_name}: {value}")
            label.setStyleSheet("""
                QLabel {
                    font-family: monospace;
                    padding: 3px;
                }
            """)
            
            # Make visualization properties clickable
            if any(x in prop_name for x in ["Star", "Polygonal", "Centered"]):
                label.setStyleSheet("""
                    QLabel {
                        font-family: monospace;
                        padding: 3px;
                        color: blue;
                        text-decoration: underline;
                    }
                """)
                label.setCursor(Qt.PointingHandCursor)
                label.mousePressEvent = lambda e, p=prop_name, v=value: self.show_geometry_visualization(p, v)
                
            layout.addWidget(label)
        
        layout.addStretch()

    def show_geometry_visualization(self, prop_type, value):
        """Show geometry visualization for properties in auxiliary window."""
        try:
            if "Star" in prop_type:
                # Handle star numbers
                star_parts = value.split("Yes - ")[1].split(", ")
                if len(star_parts) > 1:
                    menu = QMenu(self)
                    for part in star_parts:
                        sides = int(part.split('-')[0])
                        menu.addAction(f"{sides}-pointed Star", 
                            lambda s=sides: self.main_window.auxiliary_window_manager.create_window(
                                name=f"{s}-pointed Star",
                                window_type="geometry_visualizer",
                                sides=s,
                                layers=1
                            ))
                    menu.exec_(QCursor.pos())
                else:
                    sides = int(star_parts[0].split('-')[0])
                    self.main_window.auxiliary_window_manager.create_window(
                        name=f"{sides}-pointed Star",
                        window_type="geometry_visualizer",
                        sides=sides,
                        layers=1
                    )
                    
            elif "Centered" in prop_type:
                # Handle centered polygonal numbers
                centered_parts = value.split(", ")
                if len(centered_parts) > 1:
                    menu = QMenu(self)
                    for part in centered_parts:
                        sides = int(part.split('-')[0].split()[-1])
                        n = int(part.split('n=')[1].split(')')[0])
                        menu.addAction(f"Centered {sides}-gon (n={n})", 
                            lambda s=sides, l=n: self.main_window.auxiliary_window_manager.create_window(
                                name=f"Centered {s}-gon",
                                window_type="geometry_visualizer",
                                sides=s,
                                layers=l
                            ))
                    menu.exec_(QCursor.pos())
                else:
                    sides = int(centered_parts[0].split('-')[0].split()[-1])
                    n = int(centered_parts[0].split('n=')[1].split(')')[0])
                    self.main_window.auxiliary_window_manager.create_window(
                        name=f"Centered {sides}-gon",
                        window_type="geometry_visualizer",
                        sides=sides,
                        layers=n
                    )
                    
            elif "Polygonal" in prop_type:
                # Handle multiple polygonal numbers
                polygonal_parts = value.split(", ")
                
                if len(polygonal_parts) > 1:
                    menu = QMenu(self)
                    for part in polygonal_parts:
                        # Parse "k-gonal(n=x)" format
                        sides = int(part.split("-")[0])
                        position = int(part.split("n=")[1].split(")")[0])
                        
                        # Create submenu for each polygonal number
                        submenu = QMenu(f"{sides}-gonal number (n={position})", menu)
                        menu.addMenu(submenu)
                        
                        # Add visualization options to submenu
                        submenu.addAction("Show as Centered", 
                            lambda checked=False, s=sides, p=position: 
                            self.main_window.auxiliary_window_manager.create_window(
                                name=f"Centered {s}-gonal Number (n={p})",
                                window_type="geometry_visualizer",
                                sides=s,
                                layers=p
                            ))
                        submenu.addAction("Show as Regular", 
                            lambda checked=False, s=sides, p=position: 
                            self.main_window.auxiliary_window_manager.create_window(
                                name=f"Regular {s}-gonal Number (n={p})",
                                window_type="geometry_visualizer",
                                visualization_type="polygonal",
                                sides=s,
                                n=p
                            ))
                    menu.exec_(QCursor.pos())
                else:
                    # Single polygonal number - parse "k-gonal(n=x)" format
                    sides = int(value.split("-")[0])
                    position = int(value.split("n=")[1].split(")")[0])
                    
                    menu = QMenu(self)
                    menu.addAction("Show as Centered", 
                        lambda checked=False: 
                        self.main_window.auxiliary_window_manager.create_window(
                            name=f"Centered {sides}-gonal Number (n={position})",
                            window_type="geometry_visualizer",
                            sides=sides,
                            layers=position
                        ))
                    menu.addAction("Show as Regular", 
                        lambda checked=False: 
                        self.main_window.auxiliary_window_manager.create_window(
                            name=f"Regular {sides}-gonal Number (n={position})",
                            window_type="geometry_visualizer",
                            visualization_type="polygonal",
                            sides=sides,
                            n=position
                        ))
                    menu.exec_(QCursor.pos())
                
        except Exception as e:
            print(f"Error in geometry visualization: {e}")
            print(f"Property type: {prop_type}")
            print(f"Value: {value}")

    def create_polygon(self, sides, center_pos):
        """Create a regular polygon"""
        self.geometry_visualizer.create_centered_polygon(sides)

    def handle_selection_changed(self):
        """Handle changes in geometry selection"""
        selected_items = self.geometry_visualizer.scene.selectedItems()
        self.update_selection_info(selected_items)
        self.update_button_states(selected_items)

    def update_selection_info(self, selected_items):
        """Update information about selected items"""
        from .geometry.items import GeometryPoint, GeometryLine
        
        points = [item for item in selected_items if isinstance(item, GeometryPoint)]
        lines = [item for item in selected_items if isinstance(item, GeometryLine)]
        
        selection_info = []
        if points:
            point_numbers = [point.number for point in points]
            selection_info.append(f"Selected Points: {', '.join(map(str, point_numbers))}")
        if lines:
            line_info = []
            for line in lines:
                line_info.append(f"{line.start_point.number}-{line.end_point.number}")
            selection_info.append(f"Selected Lines: {', '.join(line_info)}")
            
        self.status_label.setText(" | ".join(selection_info) if selection_info else "No Selection")

    def update_button_states(self, selected_items):
        """Enable/disable buttons based on selection state"""
        from .geometry.items import GeometryPoint, GeometryLine
        
        has_selection = len(selected_items) > 0
        has_points = any(isinstance(item, GeometryPoint) for item in selected_items)
        has_lines = any(isinstance(item, GeometryLine) for item in selected_items)
        
        # Update button states
        if hasattr(self, 'delete_btn'):
            self.delete_btn.setEnabled(has_selection)
        if hasattr(self, 'connect_btn'):
            self.connect_btn.setEnabled(len([item for item in selected_items 
                                           if isinstance(item, GeometryPoint)]) == 2)

    def get_line_connections(self, line):
        """Get all connections for a line"""
        if not isinstance(line, GeometryLine):
            return []
        return [(line.start_num, line.end_num)]

    def remove_line(self, line):
        """Remove a line from the scene and data structures"""
        if line in self.geometry_visualizer.custom_lines:
            self.geometry_visualizer.custom_lines.remove(line)
        elif line in self.geometry_visualizer.pattern_lines:
            self.geometry_visualizer.pattern_lines.remove(line)
        self.geometry_visualizer.scene.removeItem(line)

    def remove_connections(self, connections):
        """Remove connections from the connection tracking"""
        for start_num, end_num in connections:
            if hasattr(self.geometry_visualizer, 'connection_manager'):
                self.geometry_visualizer.connection_manager.remove_connection(start_num, end_num)

    def create_status_bar(self):
        """Create a status bar for selection info"""
        status_layout = QHBoxLayout()
        self.status_label = QLabel("No Selection")
        status_layout.addWidget(self.status_label)
        self.layout().addLayout(status_layout) 