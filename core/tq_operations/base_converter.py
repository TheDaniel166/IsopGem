from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from pathlib import Path

class BaseConverter:
    """
    A class to handle conversions between decimal (base-10) and base-3 numbers.
    
    Methods:
        to_base_3(decimal_num): Converts a decimal number to base-3
        to_decimal(base3_num): Converts a base-3 number to decimal
        validate_base3(base3_num): Validates if a number is a valid base-3 number
    """
    
    @staticmethod
    def to_base_3(decimal_num):
        """
        Convert a decimal (base-10) number to base-3.
        
        Args:
            decimal_num (int): The decimal number to convert
            
        Returns:
            str: The base-3 representation as a string
            
        Raises:
            ValueError: If input is negative or not an integer
        """
        if not isinstance(decimal_num, int):
            raise ValueError("Input must be an integer")
        if decimal_num < 0:
            raise ValueError("Input must be non-negative")
            
        if decimal_num == 0:
            return "0"
            
        base3 = ""
        num = decimal_num
        
        while num > 0:
            remainder = num % 3
            base3 = str(remainder) + base3
            num //= 3
            
        return base3

    @staticmethod
    def to_decimal(base3_num):
        """
        Convert a base-3 number to decimal (base-10).
        
        Args:
            base3_num (str): The base-3 number as a string
            
        Returns:
            int: The decimal representation
            
        Raises:
            ValueError: If input contains invalid digits for base-3
        """
        if not BaseConverter.validate_base3(base3_num):
            raise ValueError("Invalid base-3 number")
            
        decimal = 0
        power = 0
        
        # Process digits from right to left
        for digit in reversed(base3_num):
            decimal += int(digit) * (3 ** power)
            power += 1
            
        return decimal

    @staticmethod
    def validate_base3(base3_num):
        """
        Validate if a string represents a valid base-3 number.
        
        Args:
            base3_num (str): The number to validate
            
        Returns:
            bool: True if valid base-3 number, False otherwise
        """
        if not isinstance(base3_num, str):
            return False
            
        valid_digits = set('012')
        return all(digit in valid_digits for digit in base3_num)

class TernaryVisualizer(QWidget):
    """
    A widget that visualizes ternary numbers using I Ching-like symbols.
    Each ternary digit (0, 1, 2) is represented by a unique image,
    displayed vertically from top to bottom.
    
    The images are standardized:
    - 0 (broken line): 64x16
    - 1 (solid line): 64x16
    - 2 (double line): 64x16
    
    Will display all digits of a number, regardless of length.
    For numbers less than 6 digits, they will be padded with leading zeros.
    For numbers with 6 or more digits, all digits will be shown.
    """
    
    def __init__(self, parent=None):
        print(f"Creating TernaryVisualizer with parent: {parent.__class__.__name__ if parent else 'None'}")
        super().__init__(parent)
        self.image_path = Path("assets/ternary_lines")
        self.digit_images = {}
        self.init_ui()
        self.load_images()

    def init_ui(self):
        print("Initializing TernaryVisualizer UI")
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.layout.setContentsMargins(10, 10, 10, 10)
        try:
            print("Setting TernaryVisualizer layout")
            self.setLayout(self.layout)
            print("TernaryVisualizer layout set successfully")
        except Exception as e:
            print(f"Error setting TernaryVisualizer layout: {str(e)}")
            import traceback
            traceback.print_exc()

    def load_images(self):
        """Load and cache the ternary digit images"""
        for digit in range(3):
            image_file = self.image_path / f"{digit}.png"
            if image_file.exists():
                pixmap = QPixmap(str(image_file))
                if digit == 0:
                    # Create a new label with fixed size
                    label = QLabel()
                    label.setFixedSize(64, 16)
                    # Center the image in the label
                    label.setAlignment(Qt.AlignCenter)
                    label.setPixmap(pixmap)
                    self.digit_images[str(digit)] = label
                else:
                    # Store pixmap directly for 1 and 2
                    self.digit_images[str(digit)] = pixmap
            else:
                print(f"Warning: Image file not found: {image_file}")

    def display_ternary(self, ternary_str):
        """
        Display a ternary number using the corresponding images.
        Will display all digits, showing the complete number regardless of length.
        
        Args:
            ternary_str (str): The ternary number to display
        """
        self.clear()
        
        # Display all digits without truncation
        for digit in ternary_str:
            if digit in self.digit_images:
                if digit == '0':
                    # Create a new label for each '0' instead of reusing
                    new_label = QLabel()
                    new_label.setFixedSize(64, 16)
                    new_label.setAlignment(Qt.AlignCenter)
                    new_label.setPixmap(self.digit_images[str(digit)].pixmap())
                    new_label.setContentsMargins(0, 0, 0, 0)
                    self.layout.addWidget(new_label)
                else:
                    label = QLabel()
                    label.setPixmap(self.digit_images[digit])
                    label.setFixedSize(64, 16)
                    label.setContentsMargins(0, 0, 0, 0)
                    self.layout.addWidget(label)

    def get_height(self):
        """Get the standard height for all digits"""
        return 16  # All digits are standardized to 16 pixels high

    def get_digit_width(self):
        """Get the standard width for all digits"""
        return 64  # All digits are standardized to 64 pixels wide

    def clear(self):
        """Clear the display"""
        for i in reversed(range(self.layout.count())): 
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget.setParent(None) 