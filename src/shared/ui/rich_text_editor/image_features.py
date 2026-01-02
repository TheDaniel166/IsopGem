"""Image management features for RichTextEditor."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QSpinBox,
    QDialogButtonBox, QFileDialog, QWidget, QTextEdit,
    QMenu, QMessageBox, QLabel, QPushButton, QHBoxLayout,
    QSlider, QCheckBox, QGroupBox, QSizePolicy, QScrollArea,
    QComboBox, QRubberBand, QStyle, QStyleOption
)
from PyQt6.QtGui import (
    QTextCursor, QTextImageFormat, QIcon, QAction,
    QPixmap, QImage, QTextDocument, QPainter
)
from PyQt6.QtCore import Qt, QBuffer, QByteArray, QIODevice, QUrl, QRect, QPoint, pyqtSignal, QSize, QObject, QThread, QRectF
import qtawesome as qta
import os
import uuid
from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from .image_gateway import ImageGateway


class CropPreviewLabel(QLabel):
    """Preview label that supports drag-to-crop selection."""

    selection_changed = pyqtSignal(QRect)  # Emits normalized rect relative to display_rect

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
        self.display_rect = QRect()
        self.origin = QPoint()
        self.selection_relative = None # QRectF (0..1, 0..1) relative to display_rect
        self.pending_selection = QRect()
        self._is_dragging = False

    def set_display_rect(self, rect: QRect):
        self.display_rect = rect
        if self.selection_relative:
            # Re-project selection
            w = rect.width()
            h = rect.height()
            rx = self.selection_relative.x()
            ry = self.selection_relative.y()
            rw = self.selection_relative.width()
            rh = self.selection_relative.height()
            
            new_rect = QRect(
                rect.x() + int(rx * w),
                rect.y() + int(ry * h),
                int(rw * w),
                int(rh * h)
            )
            self.rubber_band.setGeometry(new_rect)
            self.rubber_band.show()
            self.pending_selection = new_rect
        else:
            self.rubber_band.hide()

    def clear_selection(self):
        self.selection_relative = None
        self.pending_selection = QRect()
        self.rubber_band.hide()

    def has_selection(self) -> bool:
        return self.selection_relative is not None

    def get_selection(self) -> QRect:
        if not self.selection_relative or not self.display_rect:
            return QRect()
        
        # We need to return rect relative to the image pixel origin (0,0 of the image visual)
        # Mouse events generate selection in Widget coords
        # display_rect is the rect of the image in Widget coords
        
        # Calculate rect in widget coords from relative
        w = self.display_rect.width()
        h = self.display_rect.height()
        rx = self.selection_relative.x()
        ry = self.selection_relative.y()
        rw = self.selection_relative.width()
        rh = self.selection_relative.height()
        
        widget_rect = QRect(
            self.display_rect.x() + int(rx * w),
            self.display_rect.y() + int(ry * h),
            int(rw * w),
            int(rh * h)
        )
        
        # Translate to be relative to display_rect top-left
        normalized = QRect(widget_rect)
        normalized.translate(-self.display_rect.left(), -self.display_rect.top())
        return normalized

    def mousePressEvent(self, event):  # type: ignore[override]
        """
        Mousepressevent logic.
        
        Args:
            event: Description of event.
        
        """
        if not self.display_rect.contains(event.pos()):
            return
        self._is_dragging = True
        self.origin = event.pos()
        self.rubber_band.setGeometry(QRect(self.origin, QPoint()))
        self.rubber_band.show()

    def mouseMoveEvent(self, event):  # type: ignore[override]
        """
        Mousemoveevent logic.
        
        Args:
            event: Description of event.
        
        """
        if self._is_dragging and self.rubber_band.isVisible():
            rect = QRect(self.origin, event.pos()).normalized()
            self.rubber_band.setGeometry(rect)

    def mouseReleaseEvent(self, event):  # type: ignore[override]
        """
        Mousereleaseevent logic.
        
        Args:
            event: Description of event.
        
        """
        self._is_dragging = False
        if self.rubber_band.isVisible():
            rect = self.rubber_band.geometry().normalized()
            selection = rect.intersected(self.display_rect)
            if selection.isValid() and selection.width() > 1 and selection.height() > 1:
                self.rubber_band.setGeometry(selection)
                self.pending_selection = selection
                
                # Calculate relative
                if self.display_rect.width() > 0 and self.display_rect.height() > 0:
                    rx = (selection.x() - self.display_rect.x()) / self.display_rect.width()
                    ry = (selection.y() - self.display_rect.y()) / self.display_rect.height()
                    rw = selection.width() / self.display_rect.width()
                    rh = selection.height() / self.display_rect.height()
                    self.selection_relative = QRectF(rx, ry, rw, rh)
                
                # Normalize logic for signal
                normalized = QRect(selection)
                normalized.translate(-self.display_rect.left(), -self.display_rect.top())
                self.selection_changed.emit(normalized)
            else:
                self.clear_selection()
                self.selection_changed.emit(QRect())

    def paintEvent(self, event):
        """Explicitly draw pixmap at calculated display_rect to ensure sync."""
        # Draw standard widget background
        painter = QPainter(self)
        opt = QStyleOption()
        opt.initFrom(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)
        
        # Draw pixmap if exists
        if self.display_rect.isValid() and self.pixmap() and not self.pixmap().isNull():
            painter.drawPixmap(self.display_rect.topLeft(), self.pixmap())


class ImagePropertiesDialog(QDialog):
    """Dialog for quick width/height edits after insertion."""
    def __init__(self, fmt: QTextImageFormat, parent=None):
        """
          init   logic.
        
        Args:
            fmt: Description of fmt.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setWindowTitle("Image Properties")
        self.fmt = fmt
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 4000)
        self.width_spin.setValue(int(self.fmt.width()))
        form.addRow("Width:", self.width_spin)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 4000)
        self.height_spin.setValue(int(self.fmt.height()))
        form.addRow("Height:", self.height_spin)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def apply_to_format(self, fmt: QTextImageFormat):
        """
        Apply to format logic.
        
        Args:
            fmt: Description of fmt.
        
        """
        fmt.setWidth(self.width_spin.value())
        fmt.setHeight(self.height_spin.value())


class ImageLoaderWorker(QObject):
    """Worker to load images off the main thread."""
    finished = pyqtSignal(object)  # Emits (Pillow Image, Error String)

    def __init__(self, path):
        """
          init   logic.
        
        Args:
            path: Description of path.
        
        """
        super().__init__()
        self.path = path

    def run(self):
        """
        Execute logic.
        
        """
        try:
            from PIL import Image
            img = Image.open(self.path).convert("RGBA")
            # Force load data while in thread
            img.load() 
            self.finished.emit((img, None))
        except Exception as e:
            self.finished.emit((None, str(e)))

class ImageEditorDialog(QDialog):
    """Modal image editor using Pillow before insertion."""

    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setWindowTitle("Edit & Insert Image")
        self.orig_image = None  # Pillow Image
        self.base_image = None  # Geometry-applied image
        self.current_image = None  # With brightness/contrast
        self.aspect_locked = True
        self.loader_thread = None
        self.zoom_level = None # None = Fit, float = scale
        self._setup_ui()

    def set_image(self, pil_image):
        """Pre-load an existing image for editing."""
        if pil_image.mode != "RGBA":
             pil_image = pil_image.convert("RGBA")
        self.orig_image = pil_image
        self.base_image = pil_image.copy()
        self.current_image = pil_image.copy()  # Ensure current_image is set
        
        # Sync UI
        self._sync_size_spins()
        self.btn_ok.setEnabled(True)
        self.controls_box.setEnabled(True)
        self._update_preview()
        
        self.lbl_file.setText("Editing Image")

    def _setup_ui(self):
        # 2-Pane Layout: Left=Controls, Right=Viewport
        self.resize(1000, 700) # Default larger size
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- LEFT PANEL: CONTROLS ---
        left_panel = QWidget()
        left_panel.setFixedWidth(320)
        left_panel.setStyleSheet("background-color: #f8fafc; border-right: 1px solid #e2e8f0; color: #1e2937;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(15, 15, 15, 15)
        
        # Adjustments Group
        self.controls_box = QGroupBox("Adjustments")
        # Reuse existing structure but compact
        ctrl_layout = QVBoxLayout()
        ctrl_layout.setSpacing(8)
        
        # Size
        size_row = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 8000)
        self.width_spin.valueChanged.connect(self._on_width_changed)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 8000)
        self.height_spin.valueChanged.connect(self._on_height_changed)
        self.chk_lock = QCheckBox("Lock")
        self.chk_lock.setChecked(True)
        self.chk_lock.stateChanged.connect(self._on_lock_changed)
        size_row.addWidget(QLabel("W:"))
        size_row.addWidget(self.width_spin)
        size_row.addWidget(QLabel("H:"))
        size_row.addWidget(self.height_spin)
        size_row.addWidget(self.chk_lock)
        ctrl_layout.addLayout(size_row)
        
        # Rotate
        rot_row = QHBoxLayout()
        btn_rot_l = QPushButton("-90°")
        btn_rot_l.clicked.connect(lambda: self._rotate(-90))
        btn_rot_r = QPushButton("+90°")
        btn_rot_r.clicked.connect(lambda: self._rotate(90))
        btn_flip_h = QPushButton("Flip H")
        btn_flip_h.clicked.connect(self._flip_h)
        btn_flip_v = QPushButton("Flip V")
        btn_flip_v.clicked.connect(self._flip_v)
        rot_row.addWidget(btn_rot_l)
        rot_row.addWidget(btn_rot_r)
        rot_row.addWidget(btn_flip_h)
        rot_row.addWidget(btn_flip_v)
        ctrl_layout.addLayout(rot_row)
        
        # Sliders
        def add_slider(label, attr):
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 200) if "Sharpness" in label else slider.setRange(10, 300)
            if "Saturation" in label or "Sharpness" in label: slider.setRange(0, 300)
            slider.setValue(100)
            slider.valueChanged.connect(self._update_preview)
            setattr(self, attr, slider)
            row.addWidget(slider)
            ctrl_layout.addLayout(row)

        add_slider("Brightness", "slider_brightness")
        add_slider("Contrast", "slider_contrast")
        add_slider("Saturation", "slider_saturation")
        add_slider("Sharpness", "slider_sharpness")
        
        # Filter
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Filter:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "None", "--- Color ---", "Grayscale", "Sepia", "Warm", "Cool", "Vintage", "Invert",
            "--- Blur/Sharp ---", "Blur", "Sharpen", "Emboss", "Find Edges", 
            "--- Auto ---", "Auto Contrast"
        ])
        self.filter_combo.currentTextChanged.connect(self._update_preview)
        filter_row.addWidget(self.filter_combo)
        ctrl_layout.addLayout(filter_row)
        
        # Reset
        btn_reset = QPushButton("Reset All")
        btn_reset.clicked.connect(self._reset_image)
        ctrl_layout.addWidget(btn_reset)
        
        self.controls_box.setLayout(ctrl_layout)
        self.controls_box.setEnabled(False) # Default disabled
        left_layout.addWidget(self.controls_box)
        
        # Layout Group
        layout_box = QGroupBox("Layout on Insert")
        l_layout = QVBoxLayout()
        self.display_combo = QComboBox()
        self.display_combo.addItems(["100%", "75%", "50%", "25%"])
        l_layout.addWidget(QLabel("Display Size:"))
        l_layout.addWidget(self.display_combo)
        
        self.align_combo = QComboBox()
        self.align_combo.addItems(["Left", "Center", "Right"])
        l_layout.addWidget(QLabel("Alignment:"))
        l_layout.addWidget(self.align_combo)
        
        # Margins (compact)
        margin_grid = QHBoxLayout()
        self.margin_left = QSpinBox(); self.margin_left.setSuffix("px")
        self.margin_right = QSpinBox(); self.margin_right.setSuffix("px")
        self.margin_top = QSpinBox(); self.margin_top.setSuffix("px")
        self.margin_bottom = QSpinBox(); self.margin_bottom.setSuffix("px")
        margin_grid.addWidget(QLabel("L:")); margin_grid.addWidget(self.margin_left)
        margin_grid.addWidget(QLabel("R:")); margin_grid.addWidget(self.margin_right)
        margin_grid.addWidget(QLabel("T:")); margin_grid.addWidget(self.margin_top)
        margin_grid.addWidget(QLabel("B:")); margin_grid.addWidget(self.margin_bottom)
        l_layout.addLayout(margin_grid)
        
        layout_box.setLayout(l_layout)
        left_layout.addWidget(layout_box)
        
        # Buttons
        left_layout.addStretch()
        self.btn_ok = QPushButton("Insert") # Rename OK to Insert for clarity
        self.btn_ok.clicked.connect(self.accept)
        self.btn_ok.setEnabled(False)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.btn_ok)
        btn_row.addWidget(btn_cancel)
        left_layout.addLayout(btn_row)
        
        main_layout.addWidget(left_panel)
        
        # --- RIGHT PANEL: PREVIEW ---
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: #111827; color: #f3f4f6;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # Toolbar
        toolbar = QHBoxLayout()
        self.btn_choose = QPushButton("Change Image")
        self.btn_choose.clicked.connect(self._choose_image)
        self.btn_choose.setStyleSheet("background: #4b5563; border: none; padding: 5px 10px; border-radius: 4px;")
        
        self.lbl_file = QLabel("No file")
        self.lbl_file.setStyleSheet("color: #9ca3af;")
        
        toolbar.addWidget(self.lbl_file)
        toolbar.addWidget(self.btn_choose)
        
        self.lbl_loading = QLabel("Loading...")
        self.lbl_loading.setVisible(False)
        self.lbl_loading.setStyleSheet("color: #3b82f6; font-weight: bold; margin-left: 10px;")
        toolbar.addWidget(self.lbl_loading)
        
        toolbar.addStretch()
        
        # Zoom
        toolbar.addWidget(QLabel("Zoom:"))
        btn_fit = QPushButton("Fit")
        btn_fit.setToolTip("Fit image to view")
        btn_fit.clicked.connect(self._zoom_fit)
        btn_fit.setStyleSheet("background: #374151; padding: 4px 8px; border-radius: 4px;")
        
        btn_100 = QPushButton("100%")
        btn_100.clicked.connect(self._zoom_100)
        btn_100.setStyleSheet("background: #374151; padding: 4px 8px; border-radius: 4px;")
        
        toolbar.addWidget(btn_fit)
        toolbar.addWidget(btn_100)
        
        right_layout.addLayout(toolbar)
        
        # Viewport
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True) # Start in Fit mode
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setStyleSheet("border: 1px solid #374151; background: #000000;")
        
        self.preview_label = CropPreviewLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.selection_changed.connect(self._on_crop_selection_changed)
        
        self.scroll_area.setWidget(self.preview_label)
        right_layout.addWidget(self.scroll_area)
        
        # Crop Widget
        self.crop_widget = QWidget()
        crop_layout = QHBoxLayout(self.crop_widget)
        self.lbl_crop_info = QLabel("Crop Selection")
        btn_apply = QPushButton("Apply Crop")
        btn_apply.setStyleSheet("background: #10b981; color: white;")
        btn_apply.clicked.connect(self._apply_pending_crop)
        btn_cancel_crop = QPushButton("X")
        btn_cancel_crop.clicked.connect(self._cancel_crop_selection)
        crop_layout.addWidget(self.lbl_crop_info)
        crop_layout.addWidget(btn_apply)
        crop_layout.addWidget(btn_cancel_crop)
        self.crop_widget.setVisible(False)
        self.crop_widget.setStyleSheet("background: #1f2937; border-top: 1px solid #374151; padding: 5px;")
        right_layout.addWidget(self.crop_widget)
        
        main_layout.addWidget(right_panel, stretch=1)
        
    def _zoom_fit(self):
        self.zoom_level = None
        self.scroll_area.setWidgetResizable(True)
        self._update_preview()
        
    def _zoom_100(self):
        self.zoom_level = 1.0
        self.scroll_area.setWidgetResizable(False) # Allow resize to be dictated by content
        self._update_preview()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if event.oldSize() == event.size():
            return
        if self.zoom_level is None:
            self._update_preview()

    # --- UI handlers ---
    def _choose_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            None,  # Use None for independent top-level window
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.tif *.tiff *.webp)"
        )
        if not file_path:
            return
        try:
            from PIL import Image
        except ImportError:
            QMessageBox.critical(self, "Missing dependency", "Pillow is required for image editing. Please install pillow.")
            return

        # Start loading in background
        self.btn_choose.setEnabled(False)
        self.lbl_loading.setVisible(True)
        self.lbl_loading.setText(f"Loading {os.path.basename(file_path)}...")
        
        self.worker = ImageLoaderWorker(file_path)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_image_loaded)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        
        # Save reference to keep alive
        self.loader_thread = self.thread
        self.lbl_file.setText(os.path.basename(file_path))

    def _on_image_loaded(self, result):
        img, error = result
        self.btn_choose.setEnabled(True)
        self.lbl_loading.setVisible(False)
        
        if error:
            QMessageBox.critical(self, "Load failed", f"Could not open image:\n{error}")
            return
            
        if img:
            self.orig_image = img
            self.base_image = img.copy()
            self._sync_size_spins()
            self.btn_ok.setEnabled(True)
            self.controls_box.setEnabled(True)
            self._update_preview()

    def _on_width_changed(self, value: int):
        if not self.base_image:
            return
        if self.aspect_locked:
            ratio = self.base_image.height / self.base_image.width
            new_h = max(1, int(value * ratio))
            self.height_spin.blockSignals(True)
            self.height_spin.setValue(new_h)
            self.height_spin.blockSignals(False)
        self._apply_resize()

    def _on_height_changed(self, value: int):
        if not self.base_image:
            return
        if self.aspect_locked:
            ratio = self.base_image.width / self.base_image.height
            new_w = max(1, int(value * ratio))
            self.width_spin.blockSignals(True)
            self.width_spin.setValue(new_w)
            self.width_spin.blockSignals(False)
        self._apply_resize()

    def _on_lock_changed(self, state):
        self.aspect_locked = state == Qt.CheckState.Checked

    def _apply_resize(self):
        if not self.base_image:
            return
        try:
            from PIL import Image
        except ImportError:
            return
        new_w = self.width_spin.value()
        new_h = self.height_spin.value()
        self.base_image = self.base_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self._update_preview()

    def _on_crop_selection_changed(self, rect: QRect):
        """Called when user draws/changes a crop selection."""
        if not self.base_image:
            self.crop_widget.setVisible(False)
            return
        
        if not rect.isValid() or rect.width() <= 1 or rect.height() <= 1:
            # Selection was cleared or invalid
            self.crop_widget.setVisible(False)
            return
        
        disp_rect = getattr(self, "_last_display_rect", None)
        if not disp_rect or disp_rect.width() == 0 or disp_rect.height() == 0:
            self.crop_widget.setVisible(False)
            return
            self.crop_widget.setVisible(False)
            return
        
        # Calculate actual pixel dimensions of the crop
        scale_x = self.base_image.width / disp_rect.width()
        scale_y = self.base_image.height / disp_rect.height()
        crop_w = max(1, int(rect.width() * scale_x))
        crop_h = max(1, int(rect.height() * scale_y))
        
        # Show crop confirmation UI
        self.lbl_crop_info.setText(f"Crop to {crop_w} x {crop_h} px")
        self.crop_widget.setVisible(True)

    def _apply_pending_crop(self):
        """Apply the pending crop selection."""
        if not self.base_image or not self.preview_label.has_selection():
            self.crop_widget.setVisible(False)
            return
        
        rect = self.preview_label.get_selection()
        disp_rect = getattr(self, "_last_display_rect", None)
        if not disp_rect or disp_rect.width() == 0 or disp_rect.height() == 0:
            self.crop_widget.setVisible(False)
            return
        
        scale_x = self.base_image.width / disp_rect.width()
        scale_y = self.base_image.height / disp_rect.height()
        x = max(0, int(rect.left() * scale_x))
        y = max(0, int(rect.top() * scale_y))
        w = max(1, int(rect.width() * scale_x))
        h = max(1, int(rect.height() * scale_y))
        
        self._apply_crop_rect(x, y, w, h)
        self.preview_label.clear_selection()
        self.crop_widget.setVisible(False)

    def _cancel_crop_selection(self):
        """Cancel the pending crop selection."""
        self.preview_label.clear_selection()
        self.crop_widget.setVisible(False)

    def _apply_crop_rect(self, x: int, y: int, w: int, h: int):
        if not self.base_image:
            return
        img_w, img_h = self.base_image.size
        x = min(max(0, x), img_w - 1)
        y = min(max(0, y), img_h - 1)
        w = min(w, img_w - x)
        h = min(h, img_h - y)
        if w <= 1 or h <= 1:
            return
        self.base_image = self.base_image.crop((x, y, x + w, y + h))
        self._sync_size_spins()
        self._update_preview()

    def _rotate(self, degrees: int):
        if not self.base_image:
            return
        self.base_image = self.base_image.rotate(degrees, expand=True)
        self._sync_size_spins()
        self._update_preview()

    def _flip_h(self):
        if not self.base_image:
            return
        from PIL import ImageOps
        self.base_image = ImageOps.mirror(self.base_image)
        self._update_preview()

    def _flip_v(self):
        if not self.base_image:
            return
        from PIL import ImageOps
        self.base_image = ImageOps.flip(self.base_image)
        self._update_preview()

    def _reset_image(self):
        if not self.orig_image:
            return
        self.base_image = self.orig_image.copy()
        self.slider_brightness.setValue(100)
        self.slider_contrast.setValue(100)
        self.slider_saturation.setValue(100)
        self.slider_sharpness.setValue(100)
        self.filter_combo.setCurrentIndex(0)
        self._sync_size_spins()
        self._update_preview()

    # --- Preview pipeline ---
    def _update_preview(self):
        if not self.base_image:
            return
        try:
            from PIL import ImageEnhance, ImageFilter, ImageOps
        except ImportError:
            return
        img = self.base_image.copy()
        
        # Apply brightness
        b_factor = self.slider_brightness.value() / 100.0
        if b_factor != 1.0:
            img = ImageEnhance.Brightness(img).enhance(b_factor)
        
        # Apply contrast
        c_factor = self.slider_contrast.value() / 100.0
        if c_factor != 1.0:
            img = ImageEnhance.Contrast(img).enhance(c_factor)
        
        # Apply saturation
        s_factor = self.slider_saturation.value() / 100.0
        if s_factor != 1.0:
            img = ImageEnhance.Color(img).enhance(s_factor)
        
        # Apply sharpness slider
        sh_factor = self.slider_sharpness.value() / 100.0
        if sh_factor != 1.0:
            img = ImageEnhance.Sharpness(img).enhance(sh_factor)
        
        # Apply selected filter
        img = self._apply_filter(img)
        
        self.current_image = img
        self._set_preview_pixmap(img)

    def _apply_filter(self, img):
        """Apply the selected filter to the image."""
        try:
            from PIL import ImageFilter, ImageOps, Image
        except ImportError:
            return img
        
        filter_name = self.filter_combo.currentText()
        
        # Skip separator items
        if filter_name.startswith("---") or filter_name == "None":
            return img
        
        # Ensure we have RGBA for consistent processing
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        
        # Color Effects
        if filter_name == "Grayscale":
            # Convert to grayscale while preserving alpha
            r, g, b, a = img.split()
            gray = img.convert("L")
            img = Image.merge("RGBA", (gray, gray, gray, a))
        
        elif filter_name == "Sepia":
            img = self._apply_sepia(img)
        
        elif filter_name == "Warm":
            img = self._apply_color_shift(img, r_shift=20, b_shift=-20)
        
        elif filter_name == "Cool":
            img = self._apply_color_shift(img, r_shift=-20, b_shift=20)
        
        elif filter_name == "Vintage":
            img = self._apply_vintage(img)
        
        elif filter_name == "Invert":
            r, g, b, a = img.split()
            rgb = Image.merge("RGB", (r, g, b))
            rgb = ImageOps.invert(rgb)
            r, g, b = rgb.split()
            img = Image.merge("RGBA", (r, g, b, a))
        
        elif filter_name == "Posterize":
            r, g, b, a = img.split()
            rgb = Image.merge("RGB", (r, g, b))
            rgb = ImageOps.posterize(rgb, 4)
            r, g, b = rgb.split()
            img = Image.merge("RGBA", (r, g, b, a))
        
        elif filter_name == "Solarize":
            r, g, b, a = img.split()
            rgb = Image.merge("RGB", (r, g, b))
            rgb = ImageOps.solarize(rgb, threshold=128)
            r, g, b = rgb.split()
            img = Image.merge("RGBA", (r, g, b, a))
        
        # Blur & Smooth
        elif filter_name == "Blur":
            img = img.filter(ImageFilter.BLUR)
        
        elif filter_name == "Gaussian Blur":
            img = img.filter(ImageFilter.GaussianBlur(radius=2))
        
        elif filter_name == "Box Blur":
            img = img.filter(ImageFilter.BoxBlur(radius=2))
        
        elif filter_name == "Smooth":
            img = img.filter(ImageFilter.SMOOTH)
        
        elif filter_name == "Smooth More":
            img = img.filter(ImageFilter.SMOOTH_MORE)
        
        # Sharpen & Detail
        elif filter_name == "Sharpen":
            img = img.filter(ImageFilter.SHARPEN)
        
        elif filter_name == "Detail":
            img = img.filter(ImageFilter.DETAIL)
        
        elif filter_name == "Edge Enhance":
            img = img.filter(ImageFilter.EDGE_ENHANCE)
        
        elif filter_name == "Edge Enhance More":
            img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
        
        elif filter_name == "Unsharp Mask":
            img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        
        # Artistic
        elif filter_name == "Emboss":
            img = img.filter(ImageFilter.EMBOSS)
        
        elif filter_name == "Contour":
            img = img.filter(ImageFilter.CONTOUR)
        
        elif filter_name == "Find Edges":
            img = img.filter(ImageFilter.FIND_EDGES)
        
        # Auto Adjustments
        elif filter_name == "Auto Contrast":
            r, g, b, a = img.split()
            rgb = Image.merge("RGB", (r, g, b))
            rgb = ImageOps.autocontrast(rgb)
            r, g, b = rgb.split()
            img = Image.merge("RGBA", (r, g, b, a))
        
        elif filter_name == "Equalize":
            r, g, b, a = img.split()
            rgb = Image.merge("RGB", (r, g, b))
            rgb = ImageOps.equalize(rgb)
            r, g, b = rgb.split()
            img = Image.merge("RGBA", (r, g, b, a))
        
        return img

    def _apply_sepia(self, img):
        """Apply sepia tone effect."""
        from PIL import Image
        r, g, b, a = img.split()
        
        # Sepia matrix transformation
        def sepia_pixel(r, g, b):
            """
            Sepia pixel logic.
            
            Args:
                r: Description of r.
                g: Description of g.
                b: Description of b.
            
            """
            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
            tb = int(0.272 * r + 0.534 * g + 0.131 * b)
            return min(255, tr), min(255, tg), min(255, tb)
        
        pixels = list(zip(r.getdata(), g.getdata(), b.getdata()))
        new_r, new_g, new_b = [], [], []
        for pr, pg, pb in pixels:
            sr, sg, sb = sepia_pixel(pr, pg, pb)
            new_r.append(sr)
            new_g.append(sg)
            new_b.append(sb)
        
        r.putdata(new_r)
        g.putdata(new_g)
        b.putdata(new_b)
        return Image.merge("RGBA", (r, g, b, a))

    def _apply_color_shift(self, img, r_shift=0, g_shift=0, b_shift=0):
        """Shift color channels by specified amounts."""
        from PIL import Image
        r, g, b, a = img.split()
        
        def shift_channel(channel, shift):
            """
            Shift channel logic.
            
            Args:
                channel: Description of channel.
                shift: Description of shift.
            
            """
            return channel.point(lambda x: max(0, min(255, x + shift)))
        
        if r_shift:
            r = shift_channel(r, r_shift)
        if g_shift:
            g = shift_channel(g, g_shift)
        if b_shift:
            b = shift_channel(b, b_shift)
        
        return Image.merge("RGBA", (r, g, b, a))

    def _apply_vintage(self, img):
        """Apply vintage/retro effect."""
        from PIL import ImageEnhance, Image
        
        # Reduce saturation
        img = ImageEnhance.Color(img).enhance(0.7)
        # Add warm tint
        img = self._apply_color_shift(img, r_shift=15, g_shift=5, b_shift=-10)
        # Slight contrast boost
        img = ImageEnhance.Contrast(img).enhance(1.1)
        # Add slight fade (reduce overall contrast toward center gray)
        r, g, b, a = img.split()
        
        def fade(x):
            """
            Fade logic.
            
            Args:
                x: Description of x.
            
            """
            return int(x * 0.9 + 25)
        
        r = r.point(fade)
        g = g.point(fade)
        b = b.point(fade)
        return Image.merge("RGBA", (r, g, b, a))

    def _set_preview_pixmap(self, pil_img):
        data = pil_img.tobytes("raw", "RGBA")
        qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888).copy()
        pix = QPixmap.fromImage(qimg)
        
        if self.zoom_level is None:
             # Fit mode: Scale to viewport size
             avail = self.scroll_area.viewport().size()
             # Subtract a small margin
             avail = QSize(max(10, avail.width() - 20), max(10, avail.height() - 20))
             target_size = pix.size().scaled(avail, Qt.AspectRatioMode.KeepAspectRatio)
             disp_pix = pix.scaled(target_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        else:
             # Zoom mode: Scale by factor
             target_size = pix.size() * self.zoom_level
             disp_pix = pix.scaled(target_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
             
        self.preview_label.setPixmap(disp_pix)
        
        # Calculate display rect logic for crop
        # If fit, rect is centered in viewport?
        # preview_label alignment is center.
        # But for crop math, we need rect relative to label.
        
        # If preview_label.resizable is True (Fit), label size == viewport size approx.
        # Pixmap is centered.
        
        # If Zoom, label size == pixmap size.
        
        label_w = self.preview_label.width()
        label_h = self.preview_label.height()
        pix_w = disp_pix.width()
        pix_h = disp_pix.height()
        
        offset_x = max(0, (label_w - pix_w) // 2)
        offset_y = max(0, (label_h - pix_h) // 2)
        
        disp_rect = QRect(offset_x, offset_y, pix_w, pix_h)
        self._last_display_rect = disp_rect
        self.preview_label.set_display_rect(disp_rect)

    def _sync_size_spins(self):
        if not self.base_image:
            return
        self.width_spin.blockSignals(True)
        self.height_spin.blockSignals(True)
        self.width_spin.setValue(self.base_image.width)
        self.height_spin.setValue(self.base_image.height)
        self.width_spin.blockSignals(False)
        self.height_spin.blockSignals(False)

    # --- Output ---
    def get_final_qimage(self):
        """
        Retrieve final qimage logic.
        
        Returns:
            Result of get_final_qimage operation.
        """
        if not self.current_image:
            return None
        data = self.current_image.tobytes("raw", "RGBA")
        return QImage(data, self.current_image.width, self.current_image.height, QImage.Format.Format_RGBA8888).copy()

    def get_final_bytes_png(self):
        """
        Retrieve final bytes png logic.
        
        Returns:
            Result of get_final_bytes_png operation.
        """
        if not self.current_image:
            return None
        from io import BytesIO
        buf = BytesIO()
        self.current_image.save(buf, format="PNG")
        return buf.getvalue()


class ImageInsertFeature(QObject):
    """
    Manages image insertion flow: Pick -> Edit -> Persist -> Insert.
    
    Delegates persistence and insertion plumbing to ImageGateway.
    """
    
    def __init__(self, editor: QTextEdit, parent: QWidget, gateway: "ImageGateway"):
        super().__init__(parent)
        self.editor = editor
        self.gateway = gateway
        self.action_insert_image = None
    
    def create_toolbar_action(self) -> QAction:
        """Return the insert image action for the toolbar."""
        self.action_insert_image = QAction("Image", self.editor)
        self.action_insert_image.setIcon(qta.icon("fa5s.image", color="#1e293b"))
        self.action_insert_image.triggered.connect(self.insert_image)
        return self.action_insert_image

    def insert_image(self):
        """
        Execute the insert image flow.
        
        1. Open ImageEditorDialog (which handles file picking internally)
        2. On accept, get final image bytes and options
        3. Persist via gateway
        4. Insert via gateway
        """
        # Parent to the active top-level window to ensure it appears above everything
        from PyQt6.QtWidgets import QApplication
        parent_widget = QApplication.activeWindow()

        dialog = ImageEditorDialog(parent_widget)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get final processed image data (as PNG bytes)
            img_data = dialog.get_final_bytes_png()
            if not img_data:
                return

            # Persist: Get canonical URL
            # Persist always returns a persistent ID (docimg://) or fallback
            url, resource_name = self.gateway.persist_image(img_data, "PNG")

            # Register live resource for instant display
            final_qimage = dialog.get_final_qimage()
            if final_qimage:
                self.gateway.register_resource(url, final_qimage)

            # Build format
            fmt = QTextImageFormat()
            fmt.setName(resource_name)
            
            # Apply layout options from dialog
            width = dialog.width_spin.value()
            height = dialog.height_spin.value()
            
            # Apply scaling factor if one was selected
            factor = self._display_factor(dialog)
            if factor != 1.0:
                width = int(width * factor)
                height = int(height * factor)
                
            fmt.setWidth(width)
            fmt.setHeight(height)
            
            # Insert via gateway
            self.gateway.insert_image_at_cursor(fmt)
            
            # Handle alignment (requires block format logic)
            align = self._parse_alignment(dialog)
            if align:
                cursor = self.editor.textCursor()
                block_fmt = cursor.blockFormat()
                block_fmt.setAlignment(align)
                # Apply margins if any
                block_fmt.setLeftMargin(dialog.margin_left.value())
                block_fmt.setRightMargin(dialog.margin_right.value())
                block_fmt.setTopMargin(dialog.margin_top.value())
                block_fmt.setBottomMargin(dialog.margin_bottom.value())
                cursor.mergeBlockFormat(block_fmt)

    def _parse_alignment(self, dialog: "ImageEditorDialog"):
        txt = dialog.align_combo.currentText()
        if txt == "Left": return Qt.AlignmentFlag.AlignLeft
        if txt == "Right": return Qt.AlignmentFlag.AlignRight
        if txt == "Center": return Qt.AlignmentFlag.AlignCenter
        return None

    def _display_factor(self, dialog: "ImageEditorDialog"):
        txt = dialog.display_combo.currentText()
        if txt == "100%": return 1.0
        if txt == "75%": return 0.75
        if txt == "50%": return 0.50
        if txt == "25%": return 0.25
        return 1.0


class ImageEditFeature(QObject):
    """
    Manages post-insertion image editing (properties, resizing).
    
    Delegates resolution and replacement to ImageGateway.
    """
    
    def __init__(self, editor: QTextEdit, parent: QWidget, gateway: "ImageGateway"):
        super().__init__(parent)
        self.editor = editor
        self.gateway = gateway
        self.action_props = QAction("Image Properties...", self.editor)
        self.action_props.triggered.connect(self._edit_image_properties)
        self.action_props.setIcon(qta.icon("fa5s.sliders-h", color="#1e293b"))
        
        self.action_edit = QAction("Edit Image", self.editor)
        self.action_edit.triggered.connect(self.edit_image)
        self.action_edit.setIcon(qta.icon("fa5s.pen", color="#1e293b"))

    def extend_context_menu(self, menu: QMenu):
        """Add image actions to context menu if an image is selected."""
        cursor = self.editor.textCursor()
        
        # Check if cursor is on an image or near one
        fmt_before = cursor.charFormat()
        is_img_before = fmt_before.isImageFormat()
        
        cursor_after = QTextCursor(cursor)
        cursor_after.movePosition(QTextCursor.MoveOperation.Right)
        fmt_after = cursor_after.charFormat()
        is_img_after = fmt_after.isImageFormat()
        
        if is_img_before or is_img_after:
            menu.addSeparator()
            menu.addAction(self.action_edit)
            menu.addAction(self.action_props)
    
    def edit_image(self) -> None:
        """Full image editor (Crop, Rotate, Filter)."""
        if not self.gateway:
            return
            
        qimg, name_url, fmt = self.gateway.get_selected_image()
        if not qimg or not fmt:
            return

        # Convert QImage to PIL for the dialog
        try:
            from PIL import Image
            from io import BytesIO
            data = self.gateway.qimage_to_bytes(qimg)
            pil_img = Image.open(BytesIO(data))
        except Exception as e:
            return

        dialog = ImageEditorDialog(self.parent())
        dialog.set_image(pil_img)
        
        # Configure dialog initial size/params if needed?
        # Creating a new dialog instance resets state, which is fine.
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get resulting image (modified)
            final_qimg = dialog.get_final_qimage()
            if final_qimg:
                # Persist as new resource
                new_url, name = self.gateway.persist_image(
                    self.gateway.qimage_to_bytes(final_qimg), "PNG"
                )
                
                # Register resource
                self.gateway.register_resource(new_url, final_qimg)
                
                # Create format
                new_fmt = QTextImageFormat()
                new_fmt.setName(new_url.toString())
                # Should we preserve original width/height if not resized?
                # Dialog handles resize, so we trust dialog's result?
                # But dialog.get_final_qimage() has the final dimensions.
                new_fmt.setWidth(final_qimg.width())
                new_fmt.setHeight(final_qimg.height())
                
                self.gateway.replace_image_at_cursor(new_fmt)

    def _edit_image_properties(self):
        """Edit properties of the currently selected image."""
        cursor = self.editor.textCursor()
        
        # Smart selection of image near cursor
        fmt_before = cursor.charFormat()
        target_fmt = None
        
        if fmt_before.isImageFormat():
            target_fmt = fmt_before.toImageFormat()
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor)
        else:
             cursor_after = QTextCursor(cursor)
             cursor_after.movePosition(QTextCursor.MoveOperation.Right)
             fmt_after = cursor_after.charFormat()
             if fmt_after.isImageFormat():
                 target_fmt = fmt_after.toImageFormat()
                 cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor)
        
        if not target_fmt or not target_fmt.isValid():
            return

        dialog = ImagePropertiesDialog(target_fmt, self.editor)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Apply changes to the format object (in memory)
            dialog.apply_to_format(target_fmt)
            
            # Apply back to document
            # We must use the editor's cursor to ensure undo/redo stack works
            edit_cursor = self.editor.textCursor()
            # Logic to select the image again (or assume our previous move logic was reliable enough logic for current cursor?)
            # The 'cursor' variable above was local. We need to reproduce the selection on the main cursor or use the one we moved if it's attached?
            # textCursor() returns a copy.
            
            # Simplified: Use the selection strategies again on the actual editor cursor
            current_cursor = self.editor.textCursor()
            f_before = current_cursor.charFormat()
            if f_before.isImageFormat():
                current_cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor)
            else:
                 c_after = QTextCursor(current_cursor)
                 c_after.movePosition(QTextCursor.MoveOperation.Right)
                 if c_after.charFormat().isImageFormat():
                     current_cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor)
            
            # Merge the updated format
            current_cursor.mergeCharFormat(target_fmt)
            self.editor.setTextCursor(current_cursor)
