"""
Theme preview widget that shows a diagram of UI elements
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath, QFont
from PyQt6.QtCore import Qt, QPoint, QRect, QSize
from ..theme.manager import ThemeManager

class ThemePreview(QWidget):
    """Widget that shows a live preview of theme elements"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.get_instance()
        self._setup_ui()
        
        # Connect to theme changes
        self.theme_manager.theme_changed.connect(self.update)
        self.theme_manager.custom_theme_updated.connect(self.update)
        
        # Set minimum size
        self.setMinimumSize(500, 400)  # Increase minimum size to ensure visibility
    
    def _setup_ui(self):
        """Set up the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
    
    def paintEvent(self, event):
        """Paint the preview diagram"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get current colors
        colors = self.theme_manager.get_theme_colors()
        
        # Set up fonts
        title_font = QFont("Segoe UI", 10)
        title_font.setBold(True)
        content_font = QFont("Segoe UI", 9)
        
        # Calculate dimensions
        width = self.width()
        height = self.height()
        padding = 40
        element_height = 36
        
        # Create main window area
        window_rect = QRect(padding, padding + 40, width - 2*padding, height - 2*padding - 40)
        
        # Draw window background
        painter.fillRect(window_rect, QColor(colors["window"]))
        
        # Draw window frame
        painter.setPen(QPen(QColor(colors["button"]), 1))
        painter.drawRect(window_rect)
        
        # Draw title bar
        title_rect = QRect(window_rect.x(), window_rect.y(), window_rect.width(), element_height)
        painter.fillRect(title_rect, QColor(colors["button"]))
        
        # Draw title text
        painter.setFont(title_font)
        painter.setPen(QPen(QColor(colors["buttonText"])))
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, "Window Title")
        
        # Draw content area
        content_y = title_rect.bottom() + 1
        content_rect = QRect(window_rect.x(), content_y,
                           window_rect.width(),
                           window_rect.height() - element_height)
        
        # Draw alternating background
        painter.setFont(content_font)
        row_height = 24
        for i in range(0, content_rect.height(), row_height * 2):
            alt_rect = QRect(content_rect.x(), content_y + i,
                           content_rect.width(), row_height)
            painter.fillRect(alt_rect, QColor(colors["alternateBase"]))
        
        # Calculate element positions
        center_x = content_rect.center().x()
        center_y = content_rect.center().y()
        
        # Draw text content
        text_rect = QRect(content_rect.x() + 20, content_rect.y() + 20,
                         content_rect.width() - 40, 100)
        painter.setPen(QPen(QColor(colors["text"])))
        painter.drawText(text_rect, Qt.TextFlag.TextWordWrap,
                        "This is some sample text content showing how text appears "
                        "in your application. The text should be easy to read and "
                        "have good contrast with the background.")
        
        # Draw button
        button_width = 120
        button_x = center_x - button_width/2
        button_y = center_y - element_height/2
        button_rect = QRect(int(button_x), int(button_y),
                          button_width, element_height)
        
        # Draw button shadow
        shadow_rect = button_rect.translated(0, 1)
        painter.fillRect(shadow_rect, QColor(0, 0, 0, 20))
        
        # Draw button background
        painter.setPen(QPen(QColor(colors["button"]).darker(110), 1))
        painter.setBrush(QBrush(QColor(colors["button"])))
        painter.drawRoundedRect(button_rect, 4, 4)
        
        # Draw button text
        painter.setPen(QPen(QColor(colors["buttonText"])))
        painter.drawText(button_rect, Qt.AlignmentFlag.AlignCenter, "Button")
        
        # Draw selection
        selection_width = 120
        selection_x = content_rect.x() + 20
        selection_y = button_rect.bottom() + 40
        selection_rect = QRect(int(selection_x), int(selection_y),
                             selection_width, element_height)
        
        painter.fillRect(selection_rect, QColor(colors["highlight"]))
        painter.setPen(QPen(QColor(colors["highlightedText"])))
        painter.drawText(selection_rect, Qt.AlignmentFlag.AlignCenter, "Selection")
        
        # Draw link
        link_x = content_rect.right() - selection_width - 20
        link_y = selection_y
        link_rect = QRect(int(link_x), int(link_y),
                         selection_width, element_height)
        
        painter.setPen(QPen(QColor(colors["link"])))
        painter.drawText(link_rect, Qt.AlignmentFlag.AlignCenter, "Link")
        
        # Draw labels with arrows
        label_font = QFont("Segoe UI", 9)
        painter.setFont(label_font)
        
        # Helper function to draw labels
        def draw_label(text: str, target_rect: QRect, align_right: bool = False):
            label_width = 100
            label_height = 24
            arrow_length = 40
            
            if align_right:
                label_x = target_rect.left() - label_width - arrow_length
                arrow_start = QPoint(label_x + label_width, target_rect.center().y())
                arrow_end = QPoint(target_rect.left(), target_rect.center().y())
            else:
                label_x = target_rect.right() + arrow_length
                arrow_start = QPoint(label_x, target_rect.center().y())
                arrow_end = QPoint(target_rect.right(), target_rect.center().y())
            
            label_y = target_rect.center().y() - label_height/2
            label_rect = QRect(int(label_x), int(label_y), label_width, label_height)
            
            # Draw arrow
            painter.setPen(QPen(QColor(colors["windowText"]), 1, Qt.PenStyle.DashLine))
            painter.drawLine(arrow_start, arrow_end)
            
            # Draw arrow tip
            tip_size = 4
            if align_right:
                painter.drawLine(arrow_end, arrow_end + QPoint(-tip_size, -tip_size))
                painter.drawLine(arrow_end, arrow_end + QPoint(-tip_size, tip_size))
            else:
                painter.drawLine(arrow_end, arrow_end + QPoint(tip_size, -tip_size))
                painter.drawLine(arrow_end, arrow_end + QPoint(tip_size, tip_size))
            
            # Draw label text
            painter.setPen(QPen(QColor(colors["windowText"])))
            align = Qt.AlignmentFlag.AlignRight if align_right else Qt.AlignmentFlag.AlignLeft
            painter.drawText(label_rect, align | Qt.AlignmentFlag.AlignVCenter, text)
        
        # Draw all labels
        draw_label("Window", window_rect)
        draw_label("Button", button_rect)
        draw_label("Selection", selection_rect)
        draw_label("Link", link_rect, align_right=True)
