from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QGroupBox
)
from core.tq_operations.base_converter import BaseConverter
from core.tq_operations.transitions import Transitions
from PyQt5.QtCore import pyqtSignal

class PairTransitionsPanel(QWidget):
    # Add signal for sending number to quadset analysis
    send_to_quadset = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.base_converter = BaseConverter()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Input section
        input_group = QGroupBox("Input Numbers")
        input_layout = QHBoxLayout()
        
        # First number input
        self.num1_input = QLineEdit()
        self.num1_input.setPlaceholderText("Enter first decimal number")
        
        # Second number input
        self.num2_input = QLineEdit()
        self.num2_input.setPlaceholderText("Enter second decimal number")
        
        # Analyze button
        analyze_btn = QPushButton("Analyze")
        analyze_btn.clicked.connect(self.perform_analysis)
        
        input_layout.addWidget(self.num1_input)
        input_layout.addWidget(self.num2_input)
        input_layout.addWidget(analyze_btn)
        input_group.setLayout(input_layout)
        
        # Results section
        results_group = QGroupBox("Pair Analysis")
        results_layout = QVBoxLayout()
        
        # Labels for displaying results
        self.num1_ternary = QLabel("First number (ternary):")
        self.num2_ternary = QLabel("Second number (ternary):")
        self.transition = QLabel("Transition:")
        
        # Add button to send transition to quadset
        self.send_transition_btn = QPushButton("Analyze Transition in Quadset")
        self.send_transition_btn.clicked.connect(self.send_transition_to_quadset)
        self.send_transition_btn.setEnabled(False)  # Disabled until analysis is done
        
        results_layout.addWidget(self.num1_ternary)
        results_layout.addWidget(self.num2_ternary)
        results_layout.addWidget(self.transition)
        results_layout.addWidget(self.send_transition_btn)
        results_group.setLayout(results_layout)
        
        # Trinity of Triads section
        trinity_group = QGroupBox("Trinity of Triads")
        trinity_layout = QVBoxLayout()
        
        self.sum_label = QLabel("Sum:")
        self.diff_label = QLabel("Difference:")
        self.sum_diff_transition = QLabel("Sum ↔ Difference Transition:")
        
        # Add buttons to send sum/diff transition to quadset
        self.send_sum_diff_btn = QPushButton("Analyze Sum-Difference Transition in Quadset")
        self.send_sum_diff_btn.clicked.connect(self.send_sum_diff_to_quadset)
        self.send_sum_diff_btn.setEnabled(False)  # Disabled until analysis is done
        
        trinity_layout.addWidget(self.sum_label)
        trinity_layout.addWidget(self.diff_label)
        trinity_layout.addWidget(self.sum_diff_transition)
        trinity_layout.addWidget(self.send_sum_diff_btn)
        trinity_group.setLayout(trinity_layout)
        
        # Add all sections to main layout
        layout.addWidget(input_group)
        layout.addWidget(results_group)
        layout.addWidget(trinity_group)
        layout.addStretch()
        
        self.setLayout(layout)

    def perform_analysis(self):
        try:
            # Get decimal inputs
            num1 = int(self.num1_input.text())
            num2 = int(self.num2_input.text())
            
            # Convert to ternary
            ternary1 = self.base_converter.to_base_3(num1)
            ternary2 = self.base_converter.to_base_3(num2)
            
            # Ensure equal length by padding
            max_len = max(len(ternary1), len(ternary2))
            ternary1 = ternary1.zfill(max_len)
            ternary2 = ternary2.zfill(max_len)
            
            # Display ternary numbers
            self.num1_ternary.setText(f"First number (ternary): {ternary1}")
            self.num2_ternary.setText(f"Second number (ternary): {ternary2}")
            
            # Get and display transition
            trans_ter, trans_dec = Transitions.get_pair_transitions(ternary1, ternary2)
            self.transition.setText(f"Transition: {trans_ter} (ternary) = {trans_dec} (decimal)")
            
            # Calculate and display sum and difference
            sum_dec = num1 + num2
            diff_dec = abs(num1 - num2)
            
            sum_ter = self.base_converter.to_base_3(sum_dec)
            diff_ter = self.base_converter.to_base_3(diff_dec)
            
            self.sum_label.setText(f"Sum: {sum_dec} (decimal) = {sum_ter} (ternary)")
            self.diff_label.setText(f"Difference: {diff_dec} (decimal) = {diff_ter} (ternary)")
            
            # Get transition between sum and difference
            max_len = max(len(sum_ter), len(diff_ter))
            sum_ter = sum_ter.zfill(max_len)
            diff_ter = diff_ter.zfill(max_len)
            
            sum_diff_trans_ter, sum_diff_trans_dec = Transitions.get_pair_transitions(sum_ter, diff_ter)
            self.sum_diff_transition.setText(
                f"Sum ↔ Difference Transition: {sum_diff_trans_ter} (ternary) = {sum_diff_trans_dec} (decimal)")
            
            # Store the decimal values for sending to quadset
            self.transition_decimal = trans_dec
            self.sum_diff_transition_decimal = sum_diff_trans_dec
            
            # Enable the send buttons
            self.send_transition_btn.setEnabled(True)
            self.send_sum_diff_btn.setEnabled(True)
            
        except ValueError as e:
            self.clear_results()
            self.transition.setText("Error: Please enter valid decimal numbers")
        except Exception as e:
            self.clear_results()
            self.transition.setText(f"Error: {str(e)}")
            self.transition_decimal = None
            self.sum_diff_transition_decimal = None
            self.send_transition_btn.setEnabled(False)
            self.send_sum_diff_btn.setEnabled(False)

    def send_transition_to_quadset(self):
        if hasattr(self, 'transition_decimal') and self.transition_decimal is not None:
            self.send_to_quadset.emit(self.transition_decimal)

    def send_sum_diff_to_quadset(self):
        if hasattr(self, 'sum_diff_transition_decimal') and self.sum_diff_transition_decimal is not None:
            self.send_to_quadset.emit(self.sum_diff_transition_decimal)

    def clear_results(self):
        """Clear all result labels"""
        self.num1_ternary.setText("First number (ternary):")
        self.num2_ternary.setText("Second number (ternary):")
        self.transition.setText("Transition:")
        self.sum_label.setText("Sum:")
        self.diff_label.setText("Difference:")
        self.sum_diff_transition.setText("Sum ↔ Difference Transition:")
        self.send_transition_btn.setEnabled(False)
        self.send_sum_diff_btn.setEnabled(False)
        self.transition_decimal = None
        self.sum_diff_transition_decimal = None 