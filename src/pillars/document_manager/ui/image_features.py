"""Image management features for RichTextEditor."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QSpinBox,
    QDialogButtonBox, QFileDialog, QWidget, QTextEdit,
    QMenu, QMessageBox, QLabel, QPushButton, QHBoxLayout,
    QSlider, QCheckBox, QGroupBox, QSizePolicy, QScrollArea,
    QComboBox, QRubberBand
)
from PyQt6.QtGui import (
    QTextCursor, QTextImageFormat, QIcon, QAction,
    QPixmap, QImage, QTextDocument
)
from PyQt6.QtCore import Qt, QBuffer, QByteArray, QIODevice, QUrl, QRect, QPoint, pyqtSignal, QSize, QObject, QThread
import os
import uuid


class CropPreviewLabel(QLabel):
    """Preview label that supports drag-to-crop selection."""

    selection_changed = pyqtSignal(QRect)  # Emits normalized rect relative to display_rect

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
        self.display_rect = QRect()
        self.origin = QPoint()
        self.pending_selection = QRect()  # Store the pending crop selection

    def set_display_rect(self, rect: QRect):
        self.display_rect = rect
        # Clear selection when display rect changes (e.g., after other edits)
        self.clear_selection()

    def clear_selection(self):
        """Clear the current crop selection."""
        self.pending_selection = QRect()
        self.rubber_band.hide()

    def has_selection(self) -> bool:
        """Check if there's a valid pending selection."""
        return self.pending_selection.isValid() and self.pending_selection.width() > 1 and self.pending_selection.height() > 1

    def get_selection(self) -> QRect:
        """Get the pending selection rect (normalized to display_rect origin)."""
        return self.pending_selection

    def mousePressEvent(self, event):  # type: ignore[override]
        if not self.display_rect.contains(event.pos()):
            return
        self.origin = event.pos()
        self.rubber_band.setGeometry(QRect(self.origin, QPoint()))
        self.rubber_band.show()

    def mouseMoveEvent(self, event):  # type: ignore[override]
        if self.rubber_band.isVisible():
            rect = QRect(self.origin, event.pos()).normalized()
            self.rubber_band.setGeometry(rect)

    def mouseReleaseEvent(self, event):  # type: ignore[override]
        if self.rubber_band.isVisible():
            rect = self.rubber_band.geometry().normalized()
            selection = rect.intersected(self.display_rect)
            if selection.isValid() and selection.width() > 1 and selection.height() > 1:
                # Keep rubber band visible to show the selection
                self.rubber_band.setGeometry(selection)
                # Normalize to display rect origin for the pending selection
                normalized = QRect(selection)
                normalized.translate(-self.display_rect.left(), -self.display_rect.top())
                self.pending_selection = normalized
                self.selection_changed.emit(normalized)
            else:
                self.rubber_band.hide()
                self.pending_selection = QRect()
                self.selection_changed.emit(QRect())
class ImagePropertiesDialog(QDialog):
    """Dialog for quick width/height edits after insertion."""
    def __init__(self, fmt: QTextImageFormat, parent=None):
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
        fmt.setWidth(self.width_spin.value())
        fmt.setHeight(self.height_spin.value())


class ImageLoaderWorker(QObject):
    """Worker to load images off the main thread."""
    finished = pyqtSignal(object)  # Emits (Pillow Image, Error String)

    def __init__(self, path):
        super().__init__()
        self.path = path

    def run(self):
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
        super().__init__(parent)
        self.setWindowTitle("Edit & Insert Image")
        self.orig_image = None  # Pillow Image
        self.base_image = None  # Geometry-applied image
        self.current_image = None  # With brightness/contrast
        self.aspect_locked = True
        self.loader_thread = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # File row
        file_row = QHBoxLayout()
        self.btn_choose = QPushButton("Choose Image…")
        self.btn_choose.clicked.connect(self._choose_image)
        self.lbl_file = QLabel("No file selected")
        self.lbl_file.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        file_row.addWidget(self.btn_choose)
        file_row.addWidget(self.lbl_file)
        layout.addLayout(file_row)
        
        # Loading indicator
        self.lbl_loading = QLabel("Loading...")
        self.lbl_loading.setVisible(False)
        self.lbl_loading.setStyleSheet("color: #2563eb; font-weight: bold;")
        layout.addWidget(self.lbl_loading)

        # Preview inside scroll area to avoid huge images overflowing
        self.preview_label = CropPreviewLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(320, 240)
        self.preview_label.setStyleSheet("border: 1px solid #ddd; background: #fafafa;")
        self.preview_label.selection_changed.connect(self._on_crop_selection_changed)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.preview_label)
        layout.addWidget(scroll)

        # Crop confirmation row (hidden initially)
        self.crop_row = QHBoxLayout()
        self.lbl_crop_info = QLabel("")
        self.lbl_crop_info.setStyleSheet("color: #2563eb; font-weight: bold;")
        self.btn_apply_crop = QPushButton("Apply Crop")
        self.btn_apply_crop.setStyleSheet("background-color: #22c55e; color: white; font-weight: bold; padding: 5px 15px;")
        self.btn_apply_crop.clicked.connect(self._apply_pending_crop)
        self.btn_cancel_crop = QPushButton("Cancel Selection")
        self.btn_cancel_crop.clicked.connect(self._cancel_crop_selection)
        self.crop_row.addWidget(self.lbl_crop_info)
        self.crop_row.addStretch()
        self.crop_row.addWidget(self.btn_apply_crop)
        self.crop_row.addWidget(self.btn_cancel_crop)
        
        # Create a widget to hold the crop row so we can show/hide it
        self.crop_widget = QWidget()
        self.crop_widget.setLayout(self.crop_row)
        self.crop_widget.setVisible(False)
        layout.addWidget(self.crop_widget)

        controls_box = QGroupBox("Adjustments")
        # Disable controls initially
        self.controls_box = controls_box 
        self.controls_box.setEnabled(False)
        
        controls_layout = QVBoxLayout()

        size_row = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 4000)
        self.width_spin.valueChanged.connect(self._on_width_changed)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 4000)
        self.height_spin.valueChanged.connect(self._on_height_changed)
        self.chk_lock = QCheckBox("Lock aspect")
        self.chk_lock.setChecked(True)
        self.chk_lock.stateChanged.connect(self._on_lock_changed)
        size_row.addWidget(QLabel("W:"))
        size_row.addWidget(self.width_spin)
        size_row.addWidget(QLabel("H:"))
        size_row.addWidget(self.height_spin)
        size_row.addWidget(self.chk_lock)
        controls_layout.addLayout(size_row)

        rot_row = QHBoxLayout()
        btn_rot_left = QPushButton("Rotate -90")
        btn_rot_left.clicked.connect(lambda: self._rotate(-90))
        btn_rot_right = QPushButton("Rotate +90")
        btn_rot_right.clicked.connect(lambda: self._rotate(90))
        btn_flip_h = QPushButton("Flip H")
        btn_flip_h.clicked.connect(self._flip_h)
        btn_flip_v = QPushButton("Flip V")
        btn_flip_v.clicked.connect(self._flip_v)
        rot_row.addWidget(btn_rot_left)
        rot_row.addWidget(btn_rot_right)
        rot_row.addWidget(btn_flip_h)
        rot_row.addWidget(btn_flip_v)
        controls_layout.addLayout(rot_row)

        bright_row = QHBoxLayout()
        bright_row.addWidget(QLabel("Brightness"))
        self.slider_brightness = QSlider(Qt.Orientation.Horizontal)
        self.slider_brightness.setRange(10, 300)
        self.slider_brightness.setValue(100)
        self.slider_brightness.valueChanged.connect(self._update_preview)
        bright_row.addWidget(self.slider_brightness)
        controls_layout.addLayout(bright_row)

        contrast_row = QHBoxLayout()
        contrast_row.addWidget(QLabel("Contrast"))
        self.slider_contrast = QSlider(Qt.Orientation.Horizontal)
        self.slider_contrast.setRange(10, 300)
        self.slider_contrast.setValue(100)
        self.slider_contrast.valueChanged.connect(self._update_preview)
        contrast_row.addWidget(self.slider_contrast)
        controls_layout.addLayout(contrast_row)

        # Saturation slider
        saturation_row = QHBoxLayout()
        saturation_row.addWidget(QLabel("Saturation"))
        self.slider_saturation = QSlider(Qt.Orientation.Horizontal)
        self.slider_saturation.setRange(0, 300)
        self.slider_saturation.setValue(100)
        self.slider_saturation.valueChanged.connect(self._update_preview)
        saturation_row.addWidget(self.slider_saturation)
        controls_layout.addLayout(saturation_row)

        # Sharpness slider
        sharpness_row = QHBoxLayout()
        sharpness_row.addWidget(QLabel("Sharpness"))
        self.slider_sharpness = QSlider(Qt.Orientation.Horizontal)
        self.slider_sharpness.setRange(0, 300)
        self.slider_sharpness.setValue(100)
        self.slider_sharpness.valueChanged.connect(self._update_preview)
        sharpness_row.addWidget(self.slider_sharpness)
        controls_layout.addLayout(sharpness_row)

        # Filter dropdown
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Filter"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "None",
            "--- Color Effects ---",
            "Grayscale",
            "Sepia",
            "Warm",
            "Cool",
            "Vintage",
            "Invert",
            "Posterize",
            "Solarize",
            "--- Blur & Smooth ---",
            "Blur",
            "Gaussian Blur",
            "Box Blur",
            "Smooth",
            "Smooth More",
            "--- Sharpen & Detail ---",
            "Sharpen",
            "Detail",
            "Edge Enhance",
            "Edge Enhance More",
            "Unsharp Mask",
            "--- Artistic ---",
            "Emboss",
            "Contour",
            "Find Edges",
            "--- Auto Adjustments ---",
            "Auto Contrast",
            "Equalize",
        ])
        self.filter_combo.currentTextChanged.connect(self._update_preview)
        filter_row.addWidget(self.filter_combo)
        filter_row.addStretch()
        controls_layout.addLayout(filter_row)

        reset_row = QHBoxLayout()
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.clicked.connect(self._reset_image)
        reset_row.addWidget(self.btn_reset)
        reset_row.addStretch()
        controls_layout.addLayout(reset_row)

        controls_box.setLayout(controls_layout)
        layout.addWidget(controls_box)

        layout_box = QGroupBox("Layout on Insert")
        layout_layout = QVBoxLayout()

        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Display size"))
        self.display_combo = QComboBox()
        self.display_combo.addItems(["100%", "75%", "50%", "25%"])
        self.display_combo.setCurrentIndex(0)
        preset_row.addWidget(self.display_combo)
        preset_row.addStretch()
        layout_layout.addLayout(preset_row)

        align_row = QHBoxLayout()
        align_row.addWidget(QLabel("Alignment"))
        self.align_combo = QComboBox()
        self.align_combo.addItems(["Left", "Center", "Right"])
        align_row.addWidget(self.align_combo)
        align_row.addStretch()
        layout_layout.addLayout(align_row)

        margin_row = QHBoxLayout()
        margin_row.addWidget(QLabel("Left margin"))
        self.margin_left = QSpinBox()
        self.margin_left.setRange(0, 400)
        self.margin_left.setValue(0)
        margin_row.addWidget(self.margin_left)

        margin_row.addWidget(QLabel("Right margin"))
        self.margin_right = QSpinBox()
        self.margin_right.setRange(0, 400)
        self.margin_right.setValue(0)
        margin_row.addWidget(self.margin_right)

        margin_row.addWidget(QLabel("Top margin"))
        self.margin_top = QSpinBox()
        self.margin_top.setRange(0, 400)
        self.margin_top.setValue(0)
        margin_row.addWidget(self.margin_top)

        margin_row.addWidget(QLabel("Bottom margin"))
        self.margin_bottom = QSpinBox()
        self.margin_bottom.setRange(0, 400)
        self.margin_bottom.setValue(0)
        margin_row.addWidget(self.margin_bottom)

        layout_layout.addLayout(margin_row)
        layout_box.setLayout(layout_layout)
        layout.addWidget(layout_box)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.btn_ok = buttons.button(QDialogButtonBox.StandardButton.Ok)
        self.btn_ok.setEnabled(False)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # --- UI handlers ---
    def _choose_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
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
            return int(x * 0.9 + 25)
        
        r = r.point(fade)
        g = g.point(fade)
        b = b.point(fade)
        return Image.merge("RGBA", (r, g, b, a))

    def _set_preview_pixmap(self, pil_img):
        data = pil_img.tobytes("raw", "RGBA")
        qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
        pix = QPixmap.fromImage(qimg)
        avail = self.preview_label.size()
        avail = QSize(int(avail.width() * 0.95), int(avail.height() * 0.95))
        target_size = pix.size().scaled(avail, Qt.AspectRatioMode.KeepAspectRatio)
        disp_pix = pix.scaled(target_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.preview_label.setPixmap(disp_pix)
        # Compute display rect within the label for hit-testing crop selection
        offset_x = max(0, (self.preview_label.width() - target_size.width()) // 2)
        offset_y = max(0, (self.preview_label.height() - target_size.height()) // 2)
        disp_rect = QRect(offset_x, offset_y, target_size.width(), target_size.height())
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
        if not self.current_image:
            return None
        data = self.current_image.tobytes("raw", "RGBA")
        return QImage(data, self.current_image.width, self.current_image.height, QImage.Format.Format_RGBA8888)

    def get_final_bytes_png(self):
        if not self.current_image:
            return None
        from io import BytesIO
        buf = BytesIO()
        self.current_image.save(buf, format="PNG")
        return buf.getvalue()

class ImageFeature:
    """Manages image operations for the RichTextEditor."""
    
    def __init__(self, editor: QTextEdit, parent: QWidget):
        self.editor = editor
        self.parent = parent
        self._init_actions()

    def _init_actions(self):
        self.action_insert = QAction("Edit && Insert Image...", self.parent)
        self.action_insert.setToolTip("Open image editor before inserting")
        self.action_insert.triggered.connect(self._insert_image)
        
        self.action_props = QAction("Image Properties...", self.parent)
        self.action_props.triggered.connect(self._edit_image_properties)

    def create_toolbar_action(self) -> QAction:
        """Return the insert image action for the toolbar."""
        return self.action_insert

    def extend_context_menu(self, menu: QMenu):
        """Add image actions to context menu if applicable."""
        # Check if we are near an image
        cursor = self.editor.textCursor()
        
        # Check char before
        fmt_before = cursor.charFormat()
        is_img_before = fmt_before.isImageFormat()
        
        # Check char after
        cursor_after = QTextCursor(cursor)
        cursor_after.movePosition(QTextCursor.MoveOperation.Right)
        fmt_after = cursor_after.charFormat()
        is_img_after = fmt_after.isImageFormat()
        
        if is_img_before or is_img_after:
            menu.addSeparator()
            menu.addAction(self.action_props)

    def _insert_image(self):
        # Ensure Pillow is available
        try:
            import PIL  # noqa: F401
        except ImportError:
            QMessageBox.critical(self.parent, "Missing dependency", "Pillow is required for image editing. Please install pillow.")
            return

        dialog = ImageEditorDialog(self.parent)
        if not dialog.exec():
            return

        qimg = dialog.get_final_qimage()
        if qimg is None:
            return

        # Persist to a temp PNG so exported HTML has a path; also add as in-memory resource
        png_bytes = dialog.get_final_bytes_png()
        image_id = f"image://edited/{uuid.uuid4().hex}.png"
        temp_dir = os.path.join(os.getcwd(), "saved_documents", ".cache_images")
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}.png")
        try:
            with open(temp_path, "wb") as f:
                f.write(png_bytes)
        except OSError:
            # Best effort; continue with memory resource
            temp_path = None

        doc = self.editor.document()
        doc.addResource(QTextDocument.ResourceType.ImageResource, QUrl(image_id), qimg)

        cursor = self.editor.textCursor()

        # Apply block alignment and margins for the image block
        block_fmt = cursor.blockFormat()
        align_choice = self._parse_alignment(dialog)
        block_fmt.setAlignment(align_choice)
        block_fmt.setLeftMargin(dialog.margin_left.value())
        block_fmt.setRightMargin(dialog.margin_right.value())
        block_fmt.setTopMargin(dialog.margin_top.value())
        block_fmt.setBottomMargin(dialog.margin_bottom.value())
        cursor.mergeBlockFormat(block_fmt)

        factor = self._display_factor(dialog)
        image_fmt = QTextImageFormat()
        image_fmt.setName(temp_path if temp_path else image_id)
        image_fmt.setWidth(qimg.width() * factor)
        image_fmt.setHeight(qimg.height() * factor)
        cursor.insertImage(image_fmt)

    def _parse_alignment(self, dialog: "ImageEditorDialog"):
        text = dialog.align_combo.currentText()
        if text == "Center":
            return Qt.AlignmentFlag.AlignHCenter
        if text == "Right":
            return Qt.AlignmentFlag.AlignRight
        return Qt.AlignmentFlag.AlignLeft

    def _display_factor(self, dialog: "ImageEditorDialog") -> float:
        text = dialog.display_combo.currentText().replace("%", "")
        try:
            val = float(text)
        except ValueError:
            return 1.0
        return max(0.05, min(4.0, val / 100.0))

    def _edit_image_properties(self):
        cursor = self.editor.textCursor()
        
        # Determine which image we are editing and select it
        fmt_before = cursor.charFormat()
        
        cursor_after = QTextCursor(cursor)
        cursor_after.movePosition(QTextCursor.MoveOperation.Right)
        fmt_after = cursor_after.charFormat()
        
        target_fmt = None
        
        if fmt_before.isImageFormat():
            target_fmt = fmt_before.toImageFormat()
            # Select the character before
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor)
        elif fmt_after.isImageFormat():
            target_fmt = fmt_after.toImageFormat()
            # Select the character after
            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor)
            
        if target_fmt:
            dialog = ImagePropertiesDialog(target_fmt, self.parent)
            if dialog.exec():
                dialog.apply_to_format(target_fmt)
                # Apply the updated format to the selection
                # Note: We need to ensure the cursor has the selection we made above
                # But wait, 'cursor' is a copy if we got it from textCursor()?
                # Yes, textCursor() returns a copy. We need to set it back to the editor 
                # OR use the editor's cursor to make the selection.
                
                # Let's do this properly:
                # 1. Create a cursor that selects the image
                # 2. Apply format
                
                edit_cursor = self.editor.textCursor()
                # Re-detect position logic since we are in a new scope/cursor
                # Actually, we can just use the logic we just did but on the editor's cursor
                
                f_before = edit_cursor.charFormat()
                c_after = QTextCursor(edit_cursor)
                c_after.movePosition(QTextCursor.MoveOperation.Right)
                f_after = c_after.charFormat()
                
                if f_before.isImageFormat():
                    edit_cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor)
                elif f_after.isImageFormat():
                    edit_cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor)
                
                # Now apply
                edit_cursor.setCharFormat(target_fmt)
