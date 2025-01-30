from PyQt5.QtWidgets import (QDialog, QMenu, QPushButton, QAction, QFileDialog,
                            QVBoxLayout, QHBoxLayout, QSpinBox, QLabel, 
                            QDialogButtonBox, QColorDialog, QGraphicsView,
                            QGraphicsScene, QGraphicsPixmapItem, QFormLayout,
                            QCheckBox, QComboBox)
from PyQt5.QtGui import (QImage, QTextImageFormat, QTransform, QPainter,
                        QPixmap, QColor, QPen)
from PyQt5.QtCore import Qt, QRectF, QPointF, QSizeF
import os
from PyQt5.QtWidgets import QApplication

class ImageHandler:
    def __init__(self, editor):
        self.editor = editor
        self.resize_handles_visible = False
        self.current_handle = None
        self.handle_rects = {}
        
    def setup_image_actions(self):
        """Create image-related actions and menus"""
        # Create image button and menu
        image_button = QPushButton("Image")
        image_menu = QMenu()
        image_button.setMenu(image_menu)
        
        # Add image actions
        image_menu.addAction(self.create_action("Insert from File...", self.insert_image))
        image_menu.addAction(self.create_action("Insert from URL...", self.insert_image_from_url))
        
        image_menu.addSeparator()
        
        # Image manipulation options
        image_menu.addAction(self.create_action("Resize...", self.resize_selected_image))
        image_menu.addAction(self.create_action("Reset Size", self.reset_image_size))
        image_menu.addAction(self.create_action("Properties...", self.show_image_properties))
        
        # Rotation submenu
        rotate_menu = image_menu.addMenu("Rotate")
        rotate_menu.addAction(self.create_action("Rotate Left", lambda: self.rotate_image(-90)))
        rotate_menu.addAction(self.create_action("Rotate Right", lambda: self.rotate_image(90)))
        rotate_menu.addAction(self.create_action("Flip Horizontal", self.flip_image_horizontal))
        rotate_menu.addAction(self.create_action("Flip Vertical", self.flip_image_vertical))
        
        # Border submenu
        border_menu = image_menu.addMenu("Borders")
        border_menu.addAction(self.create_action("Add Border...", self.add_image_border))
        border_menu.addAction(self.create_action("Remove Border", self.remove_image_border))
        
        image_menu.addAction(self.create_action("Crop...", self.crop_image))
        
        # Add resize handles toggle
        self.resize_handles_action = self.create_action(
            "Show Resize Handles",
            self.toggle_resize_handles,
            checkable=True
        )
        image_menu.addAction(self.resize_handles_action)
        
        return image_button

    def create_action(self, text, slot, shortcut=None, checkable=False):
        """Helper to create an action"""
        action = QAction(text, self.editor)
        action.triggered.connect(slot)
        if shortcut:
            action.setShortcut(shortcut)
        if checkable:
            action.setCheckable(True)
        return action

    def insert_image(self):
        """Insert image from file"""
        file_name, _ = QFileDialog.getOpenFileName(
            self.editor,
            "Insert Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp *.svg *.ico)"
        )
        
        if file_name:
            self.insert_image_from_file(file_name)

    def insert_image_from_file(self, file_path):
        """Insert image from file path"""
        image = QImage(file_path)
        if not image.isNull():
            cursor = self.editor.editor.textCursor()
            image_format = QTextImageFormat()
            
            # Handle SVG files differently
            if file_path.lower().endswith('.svg'):
                # Convert SVG to PNG for better compatibility
                temp_path = f"{file_path}_converted.png"
                image.save(temp_path, "PNG")
                file_path = temp_path
            
            image_format.setName(file_path)
            
            # Set reasonable default size while maintaining aspect ratio
            max_width = 800
            max_height = 600
            if image.width() > max_width or image.height() > max_height:
                scaled = image.scaled(max_width, max_height, 
                                    Qt.KeepAspectRatio, 
                                    Qt.SmoothTransformation)
                image = scaled
            
            image_format.setWidth(image.width())
            image_format.setHeight(image.height())
            
            # Store original size and rotation
            image_format.setProperty(1, image.width())
            image_format.setProperty(2, image.height())
            image_format.setProperty(3, 0)  # Rotation angle
            
            cursor.insertImage(image_format)

    def rotate_image(self, angle):
        """Rotate the selected image"""
        cursor = self.editor.editor.textCursor()
        if cursor.charFormat().isImageFormat():
            image_format = cursor.charFormat().toImageFormat()
            file_path = image_format.name()
            
            image = QImage(file_path)
            transform = QTransform().rotate(angle)
            rotated = image.transformed(transform, Qt.SmoothTransformation)
            
            temp_path = f"{file_path}_rotated.png"
            rotated.save(temp_path)
            
            new_format = QTextImageFormat()
            new_format.setName(temp_path)
            new_format.setWidth(rotated.width())
            new_format.setHeight(rotated.height())
            
            # Set exact rotation angle
            new_format.setProperty(3, angle)  # Store exact angle
            
            # Preserve original dimensions
            new_format.setProperty(1, image_format.property(1))
            new_format.setProperty(2, image_format.property(2))
            
            cursor.mergeCharFormat(new_format)
            self.editor.editor.setTextCursor(cursor)  # Update cursor
            QApplication.processEvents()  # Ensure UI updates

    def flip_image_horizontal(self):
        """Flip image horizontally"""
        cursor = self.editor.editor.textCursor()
        self._flip_image(True, False)

    def flip_image_vertical(self):
        """Flip image vertically"""
        cursor = self.editor.editor.textCursor()
        self._flip_image(False, True)

    def _flip_image(self, horizontal, vertical):
        """Internal method to flip image"""
        cursor = self.editor.editor.textCursor()
        if cursor.charFormat().isImageFormat():
            image_format = cursor.charFormat().toImageFormat()
            file_path = image_format.name()
            
            image = QImage(file_path)
            flipped = image.mirrored(horizontal, vertical)
            
            temp_path = f"{file_path}_flipped.png"
            flipped.save(temp_path)
            
            new_format = QTextImageFormat()
            new_format.setName(temp_path)
            new_format.setWidth(flipped.width())
            new_format.setHeight(flipped.height())
            
            cursor.mergeCharFormat(new_format)

    def add_image_border(self):
        """Add border to image"""
        cursor = self.editor.editor.textCursor()
        if cursor.charFormat().isImageFormat():
            dialog = ImageBorderDialog(self.editor)
            if dialog.exec_() == QDialog.Accepted:
                border_settings = dialog.get_border_settings()
                self.apply_image_border(cursor, border_settings)

    def apply_image_border(self, cursor, settings):
        """Apply border to image"""
        image_format = cursor.charFormat().toImageFormat()
        file_path = image_format.name()
        
        image = QImage(file_path)
        
        # Create new image with border
        bordered = QImage(
            image.width() + 2 * settings['width'],
            image.height() + 2 * settings['width'],
            QImage.Format_ARGB32
        )
        bordered.fill(settings['color'])
        
        # Draw original image in center
        painter = QPainter(bordered)
        painter.drawImage(settings['width'], settings['width'], image)
        painter.end()
        
        # Save and update
        temp_path = f"{file_path}_bordered.png"
        bordered.save(temp_path)
        
        new_format = QTextImageFormat()
        new_format.setName(temp_path)
        new_format.setWidth(bordered.width())
        new_format.setHeight(bordered.height())
        
        cursor.mergeCharFormat(new_format)

    def remove_image_border(self):
        """Remove border from image"""
        cursor = self.editor.editor.textCursor()
        if cursor.charFormat().isImageFormat():
            image_format = cursor.charFormat().toImageFormat()
            file_path = image_format.name()
            
            # Load original image and update format
            image = QImage(file_path)
            new_format = QTextImageFormat()
            new_format.setName(file_path)
            new_format.setWidth(image.width())
            new_format.setHeight(image.height())
            
            cursor.mergeCharFormat(new_format)

    def crop_image(self):
        """Show image cropping dialog"""
        cursor = self.editor.editor.textCursor()
        if cursor.charFormat().isImageFormat():
            dialog = ImageCropDialog(self.editor, cursor.charFormat().toImageFormat())
            if dialog.exec_() == QDialog.Accepted:
                self.apply_image_crop(cursor, dialog.get_crop_rect())

    def apply_image_crop(self, cursor, crop_rect):
        """Apply crop to image"""
        image_format = cursor.charFormat().toImageFormat()
        file_path = image_format.name()
        
        image = QImage(file_path)
        cropped = image.copy(crop_rect)
        
        temp_path = f"{file_path}_cropped.png"
        cropped.save(temp_path)
        
        new_format = QTextImageFormat()
        new_format.setName(temp_path)
        new_format.setWidth(cropped.width())
        new_format.setHeight(cropped.height())
        
        cursor.mergeCharFormat(new_format)

    def toggle_resize_handles(self, checked):
        """Toggle visibility of image resize handles"""
        self.resize_handles_visible = checked
        if not checked:
            self.clear_resize_handles()
        else:
            self.update_resize_handles()
        self.editor.viewport().update()

    def update_resize_handles(self):
        """Update resize handles for all images"""
        if not self.resize_handles_visible:
            return
            
        self.handle_rects = {}
        cursor = self.editor.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        
        while not cursor.atEnd():
            format = cursor.charFormat()
            if format.isImageFormat():
                image_format = format.toImageFormat()
                rect = self.editor.editor.document().documentLayout().blockBoundingRect(cursor.block())
                pos = rect.topLeft()
                size = QSizeF(image_format.width(), image_format.height())
                
                # Create handle rectangles
                handle_size = 8
                handles = {
                    'top-left': QRectF(pos.x(), pos.y(), handle_size, handle_size),
                    'top-right': QRectF(pos.x() + size.width() - handle_size, pos.y(), handle_size, handle_size),
                    'bottom-left': QRectF(pos.x(), pos.y() + size.height() - handle_size, handle_size, handle_size),
                    'bottom-right': QRectF(pos.x() + size.width() - handle_size, pos.y() + size.height() - handle_size, handle_size, handle_size)
                }
                self.handle_rects[cursor.position()] = handles
                
            cursor.movePosition(QTextCursor.NextCharacter)

    def clear_resize_handles(self):
        """Clear all resize handles"""
        self.handle_rects = {}
        self.current_handle = None
        self.editor.viewport().update()

    def handle_mouse_press(self, event):
        """Handle mouse press for resize handles"""
        if self.resize_handles_visible:
            pos = event.pos()
            for position, handles in self.handle_rects.items():
                for handle_pos, rect in handles.items():
                    if rect.contains(pos):
                        self.current_handle = (position, handle_pos)
                        return True
        return False

    def handle_mouse_move(self, event):
        """Handle mouse move for image resizing"""
        if self.current_handle:
            position, handle_pos = self.current_handle
            cursor = self.editor.editor.textCursor()
            cursor.setPosition(position)
            
            if cursor.charFormat().isImageFormat():
                image_format = cursor.charFormat().toImageFormat()
                rect = self.editor.editor.document().documentLayout().blockBoundingRect(cursor.block())
                delta = event.pos() - rect.topLeft()
                
                # Calculate new size based on handle position and mouse movement
                new_width = image_format.width()
                new_height = image_format.height()
                
                if 'right' in handle_pos:
                    new_width = max(10, delta.x())
                if 'bottom' in handle_pos:
                    new_height = max(10, delta.y())
                    
                # Update image size
                new_format = QTextImageFormat()
                new_format.setName(image_format.name())
                new_format.setWidth(new_width)
                new_format.setHeight(new_height)
                cursor.mergeCharFormat(new_format)
                
                self.update_resize_handles()
                return True
        return False

    def handle_mouse_release(self):
        """Handle mouse release for resize handles"""
        if self.current_handle:
            self.current_handle = None
            return True
        return False

    def insert_image_from_url(self):
        """Insert image from URL"""
        # TODO: Implement URL image insertion
        pass

    def resize_selected_image(self):
        """Show resize dialog for selected image"""
        cursor = self.editor.editor.textCursor()
        if cursor.charFormat().isImageFormat():
            self.show_image_properties(cursor)

    def show_image_properties(self, cursor):
        """Show image properties dialog"""
        cursor = self.editor.editor.textCursor()
        image_format = cursor.charFormat().toImageFormat()
        
        # Get current dimensions with safety checks
        current_width = max(1, int(image_format.width()))
        current_height = max(1, int(image_format.height()))
        
        dialog = QDialog(self.editor)
        dialog.setWindowTitle("Image Properties")
        layout = QFormLayout(dialog)
        
        # Size inputs
        width_spin = QSpinBox()
        width_spin.setRange(1, 2000)
        width_spin.setValue(current_width)
        
        height_spin = QSpinBox()
        height_spin.setRange(1, 2000)
        height_spin.setValue(current_height)
        
        # Maintain aspect ratio checkbox
        aspect_ratio = QCheckBox("Maintain aspect ratio")
        aspect_ratio.setChecked(True)
        
        # Calculate aspect ratio with safety check
        try:
            original_ratio = current_width / current_height
        except ZeroDivisionError:
            original_ratio = 1.0  # Default to square if invalid dimensions
        
        # Connect size change signals
        def update_height():
            if aspect_ratio.isChecked():
                try:
                    new_height = max(1, int(width_spin.value() / original_ratio))
                    height_spin.blockSignals(True)
                    height_spin.setValue(new_height)
                    height_spin.blockSignals(False)
                except (ZeroDivisionError, ValueError):
                    pass  # Ignore invalid calculations
        
        def update_width():
            if aspect_ratio.isChecked():
                try:
                    new_width = max(1, int(height_spin.value() * original_ratio))
                    width_spin.blockSignals(True)
                    width_spin.setValue(new_width)
                    width_spin.blockSignals(False)
                except (ZeroDivisionError, ValueError):
                    pass  # Ignore invalid calculations
        
        width_spin.valueChanged.connect(update_height)
        height_spin.valueChanged.connect(update_width)
        
        # Alignment options
        alignment = QComboBox()
        alignment.addItems(["Left", "Center", "Right"])
        current_alignment = self.get_image_alignment(cursor)
        alignment.setCurrentText(current_alignment)
        
        # Add to layout
        layout.addRow("Width:", width_spin)
        layout.addRow("Height:", height_spin)
        layout.addRow(aspect_ratio)
        layout.addRow("Alignment:", alignment)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            # Update image format
            new_format = QTextImageFormat()
            new_format.setName(image_format.name())
            new_format.setWidth(width_spin.value())
            new_format.setHeight(height_spin.value())
            
            # Preserve properties
            new_format.setProperty(1, image_format.property(1))
            new_format.setProperty(2, image_format.property(2))
            new_format.setProperty(3, image_format.property(3))
            
            cursor.mergeCharFormat(new_format)
            
            # Apply alignment
            block_format = QTextBlockFormat()
            if alignment.currentText() == "Left":
                block_format.setAlignment(Qt.AlignLeft)
            elif alignment.currentText() == "Center":
                block_format.setAlignment(Qt.AlignCenter)
            else:
                block_format.setAlignment(Qt.AlignRight)
            cursor.mergeBlockFormat(block_format)

    def get_image_alignment(self, cursor):
        """Get current image alignment"""
        alignment = cursor.blockFormat().alignment()
        if alignment == Qt.AlignLeft:
            return "Left"
        elif alignment == Qt.AlignCenter:
            return "Center"
        else:
            return "Right"

    def reset_image_size(self):
        """Reset image to original size"""
        cursor = self.editor.editor.textCursor()
        if cursor.charFormat().isImageFormat():
            image_format = cursor.charFormat().toImageFormat()
            
            # Get original size from stored properties
            original_width = image_format.property(1)
            original_height = image_format.property(2)
            
            if original_width and original_height:
                # Create new format with original dimensions
                new_format = QTextImageFormat()
                new_format.setName(image_format.name())
                new_format.setWidth(original_width)
                new_format.setHeight(original_height)
                
                # Preserve other properties
                new_format.setProperty(1, original_width)
                new_format.setProperty(2, original_height)
                new_format.setProperty(3, image_format.property(3) or 0)  # Rotation
                
                cursor.mergeCharFormat(new_format)

    def insert_image_at_position(self, file_path, pos):
        """Insert image at the specified position"""
        cursor = self.editor.editor.cursorForPosition(pos)
        image = QImage(file_path)
        if not image.isNull():
            image_format = QTextImageFormat()
            image_format.setName(file_path)
            
            # Set reasonable default size
            max_width = 800
            if image.width() > max_width:
                image = image.scaledToWidth(max_width, Qt.SmoothTransformation)
            
            image_format.setWidth(image.width())
            image_format.setHeight(image.height())
            
            # Store original size and rotation
            image_format.setProperty(1, image.width())
            image_format.setProperty(2, image.height())
            image_format.setProperty(3, 0)  # Rotation angle
            
            cursor.insertImage(image_format)

    def handle_drag_enter(self, event):
        """Handle drag enter events"""
        if event.mimeData().hasUrls() or event.mimeData().hasImage():
            event.acceptProposedAction()

    def handle_drop(self, event):
        """Handle drop events"""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith(
                    ('.png', '.jpg', '.jpeg', '.bmp', '.gif', 
                     '.tiff', '.webp', '.svg', '.ico')):
                    self.insert_image_at_position(file_path, event.pos())
        elif event.mimeData().hasImage():
            image = QImage(event.mimeData().imageData())
            if not image.isNull():
                temp_path = os.path.join(os.path.expanduser('~'), '.temp_image.png')
                image.save(temp_path)
                self.insert_image_at_position(temp_path, event.pos())
                os.remove(temp_path)
        event.acceptProposedAction()

class ImageBorderDialog(QDialog):
    """Dialog for image border settings"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Image Border")
        layout = QVBoxLayout(self)
        
        # Border width
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Width:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 50)
        self.width_spin.setValue(1)
        width_layout.addWidget(self.width_spin)
        layout.addLayout(width_layout)
        
        # Border color
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        self.color_button = QPushButton()
        self.color_button.setFixedSize(50, 20)
        self.border_color = QColor(Qt.black)
        self.update_color_button()
        self.color_button.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_button)
        layout.addLayout(color_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def update_color_button(self):
        """Update color button appearance"""
        style = f'background-color: {self.border_color.name()}'
        self.color_button.setStyleSheet(style)

    def choose_color(self):
        """Show color picker dialog"""
        color = QColorDialog.getColor(self.border_color, self)
        if color.isValid():
            self.border_color = color
            self.update_color_button()

    def get_border_settings(self):
        """Get the border settings"""
        return {
            'width': self.width_spin.value(),
            'color': self.border_color
        }

class ImageCropDialog(QDialog):
    """Dialog for image cropping"""
    def __init__(self, parent, image_format):
        super().__init__(parent)
        self.image_format = image_format
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Crop Image")
        self.setMinimumSize(400, 300)
        layout = QVBoxLayout(self)
        
        # Create graphics scene and view
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        layout.addWidget(self.view)
        
        # Load and display image
        self.image = QImage(self.image_format.name())
        pixmap = QPixmap.fromImage(self.image)
        self.scene.addPixmap(pixmap)
        
        # Add crop rectangle
        pen = QPen(Qt.red, 2, Qt.SolidLine)
        self.crop_rect = self.scene.addRect(
            0, 0, self.image.width(), self.image.height(),
            pen
        )
        self.crop_rect.setFlag(QGraphicsItem.ItemIsMovable)
        self.crop_rect.setFlag(QGraphicsItem.ItemIsSelectable)
        
        # Add resize handles
        self.setup_resize_handles()
        
        # Add aspect ratio lock option
        ratio_layout = QHBoxLayout()
        self.lock_ratio = QCheckBox("Lock Aspect Ratio")
        self.lock_ratio.setChecked(True)
        ratio_layout.addWidget(self.lock_ratio)
        layout.addLayout(ratio_layout)
        
        # Add buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Fit view to image
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        
    def setup_resize_handles(self):
        """Add resize handles to crop rectangle"""
        self.handles = []
        handle_size = 10
        
        # Create handles at corners and edges
        positions = [
            (0, 0), (0.5, 0), (1, 0),
            (0, 0.5), (1, 0.5),
            (0, 1), (0.5, 1), (1, 1)
        ]
        
        for x, y in positions:
            handle = self.scene.addRect(0, 0, handle_size, handle_size)
            handle.setFlag(QGraphicsItem.ItemIsMovable)
            handle.setFlag(QGraphicsItem.ItemIsSelectable)
            handle.setBrush(Qt.white)
            handle.setPen(QPen(Qt.black))
            self.handles.append(handle)
            
            # Position handle
            pos = self.crop_rect.rect()
            handle.setPos(
                pos.x() + pos.width() * x - handle_size/2,
                pos.y() + pos.height() * y - handle_size/2
            )
            
    def get_crop_rect(self):
        """Get the selected crop rectangle"""
        return self.crop_rect.rect().toRect()

    def resizeEvent(self, event):
        """Handle dialog resize"""
        super().resizeEvent(event)
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    # ... (continued in next message due to length)

    # ... other image-related methods 