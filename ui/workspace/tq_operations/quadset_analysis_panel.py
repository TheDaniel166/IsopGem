from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox, QTabWidget, QFrame
)
from PyQt5.QtCore import Qt
from core.tq_operations.base_converter import BaseConverter, TernaryVisualizer
from core.tq_operations.number_properties import NumberProperties
from ui.workspace.tq_operations.geometry_visualizer import GeometryVisualizerDialog

class QuadsetAnalysisPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.base_converter = BaseConverter()
        self.number_properties = NumberProperties()
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

    def format_large_number(self, n):
        """Format large numbers with commas for readability"""
        return f"{n:,}"

    def perform_analysis(self):
        try:
            print("Starting analysis...")
            # Get and validate input
            decimal_num = int(self.number_input.text())
            if decimal_num < 0:
                raise ValueError("Number must be positive")
            if decimal_num > 999999999:
                raise ValueError("Number must be less than 1 billion")
            print(f"Input number: {decimal_num}")
            
            # Convert to ternary - don't pad if longer than 6 digits
            print("Converting to ternary...")
            base_ternary = self.base_converter.to_base_3(decimal_num)
            print(f"Base ternary: {base_ternary}")
            
            if len(base_ternary) < 6:
                base_ternary = base_ternary.zfill(6)
            print(f"Padded ternary: {base_ternary}")
            
            # Calculate all variations
            print("Calculating variations...")
            variations = {
                'Base': base_ternary,
                'Conrune': self.get_conrune(base_ternary),
                'Reune': self.get_reune(base_ternary),
            }
            variations['Conreune'] = self.get_conrune(variations['Reune'])
            print(f"Variations calculated: {variations}")
            
            # Update display for each variation
            print("Updating displays...")
            for name, ternary in variations.items():
                print(f"Processing {name}...")
                # Update ternary label with formatted text
                self.labels[f"{name}_ternary"].setText(f"Ternary: {ternary}")
                
                # Convert to decimal and update label with formatted text
                decimal = self.base_converter.to_decimal(ternary)
                print(f"{name} decimal: {decimal}")
                self.labels[f"{name}_decimal"].setText(f"Decimal: {decimal}")
                
                # Update visualizer
                print(f"Updating visualizer for {name}...")
                self.visualizers[name].display_ternary(ternary)
                
                # Update properties for each number - pass variations dictionary
                print(f"Updating properties for {name}...")
                self.update_properties(name, decimal, variations)
                print(f"Finished processing {name}")
            
            # Update relationships after all numbers are processed
            print("Updating relationships...")
            self.update_relationships(variations)
            print("Analysis complete!")
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            
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
        print(f"Starting property update for {name} with number {decimal_num}")
        layout = self.properties_widgets[name]
        
        # Clear existing properties
        print("Clearing existing properties...")
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            
        # Add properties
        print("Adding new properties...")
        properties = [
            ("Decimal", self.format_large_number(decimal_num)),
        ]
        
        # Optimize factor calculation for large numbers
        if decimal_num < 1000000:  # Only calculate factors for reasonable numbers
            print("Calculating factors...")
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

        print("Creating property labels...")
        for prop_name, value in properties:
            label = QLabel(f"{prop_name}: {value}")
            label.setStyleSheet("""
                QLabel {
                    font-family: monospace;
                    padding: 3px;
                }
            """)
            
            # Make star numbers and centered polygonal numbers clickable
            if prop_name in ["Star Number", "Centered Polygonal"]:
                label.setCursor(Qt.PointingHandCursor)
                label.mousePressEvent = lambda e, p=prop_name, v=value: self.show_geometry_visualization(p, v)
                
            layout.addWidget(label)
        
        layout.addStretch()
        print(f"Property update complete for {name}")

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

    def show_geometry_visualization(self, prop_type, value):
        try:
            if "star" in prop_type.lower():
                # Handle multiple star numbers in the value
                # Format: "Yes - 6-pointed star(n=4), 8-pointed star(n=3)"
                star_parts = value.split("Yes - ")[1].split(", ")
                for star_part in star_parts:
                    try:
                        # Extract points (e.g., "6" from "6-pointed")
                        points = int(star_part.split('-')[0])
                        # Extract position (e.g., "4" from "n=4)")
                        position = int(star_part.split('n=')[1].split(')')[0])
                        
                        dialog = GeometryVisualizerDialog('star', points, position, self)
                        dialog.exec_()
                    except (IndexError, ValueError) as e:
                        print(f"Error parsing star number: {star_part} - {str(e)}")
                        
            elif "centered" in prop_type.lower():
                # Handle multiple centered polygonal numbers
                # Format: "centered 5-gonal(n=3), centered 6-gonal(n=2)"
                centered_parts = value.split(", ")
                for centered_part in centered_parts:
                    try:
                        # Extract points (e.g., "5" from "5-gonal")
                        points = int(centered_part.split('-')[0].split()[-1])
                        # Extract position (e.g., "3" from "n=3)")
                        position = int(centered_part.split('n=')[1].split(')')[0])
                        
                        dialog = GeometryVisualizerDialog('centered_polygon', points, position, self)
                        dialog.exec_()
                    except (IndexError, ValueError) as e:
                        print(f"Error parsing centered polygon: {centered_part} - {str(e)}")
                        
        except Exception as e:
            print(f"Error in geometry visualization: {str(e)}")
            print(f"Property type: {prop_type}")
            print(f"Value: {value}") 