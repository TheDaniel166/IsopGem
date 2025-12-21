"""Reusable Rich Text Editor widget with Ribbon UI."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QComboBox, QFontComboBox, QSpinBox,
    QColorDialog, QMenu, QToolButton, QDialog,
    QLabel, QDialogButtonBox, QFormLayout, QDoubleSpinBox, QMessageBox,
    QSlider, QLineEdit, QStatusBar, QFileDialog, QGridLayout,
    QScrollArea, QFrame, QGroupBox, QPushButton, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QMimeData, QUrl, QMarginsF, QSizeF
from PyQt6.QtGui import (
    QFont, QAction, QIcon, QColor, QTextCharFormat,
    QTextCursor, QTextListFormat, QTextBlockFormat,
    QActionGroup, QBrush, QDesktopServices, QPageSize, QPageLayout
)
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from .table_features import TableFeature
from .image_features import ImageFeature
from .list_features import ListFeature
from .search_features import SearchReplaceFeature
from .ribbon_widget import RibbonWidget
from shared.ui import VirtualKeyboard, get_shared_virtual_keyboard

class SafeTextEdit(QTextEdit):
    """
    A hardened QTextEdit that protects against 'Paste Attacks' (Mars Seal).
    """
    def loadResource(self, type_id: int, url: QUrl):
        """
        Handle custom resource loading, specifically for docimg:// scheme.
        """
        if url.scheme() == "docimg":
            try:
                # Extract image ID
                path = url.path().strip('/')
                host = url.host()
                
                image_id = None
                
                # Case 1: docimg:///123 (Triple slash, stored in path)
                if path and path.isdigit():
                    image_id = int(path)
                
                # Case 2: docimg://123 (Double slash, Qt parses 123 as '0.0.0.123' host)
                elif host:
                    # Check for IP address format 
                    parts = host.split('.')
                    if len(parts) == 4 and all(p.isdigit() for p in parts):
                        # Decode IP to Int: a.b.c.d -> (a<<24) + (b<<16) + (c<<8) + d
                        p = [int(part) for part in parts]
                        image_id = (p[0] << 24) + (p[1] << 16) + (p[2] << 8) + p[3]
                    elif host.isdigit():
                        # Direct integer host (unlikely with QUrl but possible)
                        image_id = int(host)
                
                if image_id is None:
                     print(f"Failed to parse image ID from url: {url.toString()}")
                     return super().loadResource(type_id, url)

                # We need to access the service. 
                # Ideally, the editor should have a callback or access to the service.
                # For now, we'll use a local context, though dependency injection would be cleaner.
                from pillars.document_manager.services.document_service import document_service_context
                
                with document_service_context() as service:
                    result = service.get_image(image_id)
                    if result:
                        data, mime_type = result
                        
                        # Return properly typed resource
                        # For ImageResource, return QVariant(QImage) or QVariant(QPixmap) or QVariant(bytes)
                        # QImage.fromData handles bytes directly
                        from PyQt6.QtGui import QImage
                        image = QImage()
                        image.loadFromData(data)
                        return image
            except Exception as e:
                print(f"Failed to load image resource {url.toString()}: {e}")
                
        return super().loadResource(type_id, url)

    def insertFromMimeData(self, source: QMimeData):
        """
        Override paste behavior to protect against freezing.
        """
        # Threshold: 100,000 chars (approx 20-30 pages of text)
        WARN_THRESHOLD = 100000
        
        if source.hasText():
            text = source.text()
            if len(text) > WARN_THRESHOLD:
                # Mars Warning: Chaos detected
                reply = QMessageBox.warning(
                    self, 
                    "Large Paste Detected",
                    f"You are attempting to paste {len(text):,} characters.\n"
                    "This may temporarily freeze the application.\n\n"
                    "Do you wish to proceed?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
        
        super().insertFromMimeData(source)


class HyperlinkDialog(QDialog):
    """Dialog for inserting or editing a hyperlink."""
    
    def __init__(self, selected_text: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Insert Hyperlink")
        self.setMinimumWidth(400)
        self._setup_ui(selected_text)
    
    def _setup_ui(self, selected_text: str):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.text_input = QLineEdit()
        self.text_input.setText(selected_text)
        self.text_input.setPlaceholderText("Display text (optional)")
        form.addRow("Text to display:", self.text_input)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        form.addRow("URL:", self.url_input)
        
        layout.addLayout(form)
        
        # Hint label
        hint = QLabel("Tip: Select text first to use it as the display text.")
        hint.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(hint)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Focus on URL input
        self.url_input.setFocus()


class HorizontalRuleDialog(QDialog):
    """Dialog for customizing horizontal rule options."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Insert Horizontal Line")
        self.setMinimumWidth(350)
        self.line_color = QColor("#cccccc")
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # Line thickness
        self.thickness_spin = QSpinBox()
        self.thickness_spin.setRange(1, 20)
        self.thickness_spin.setValue(1)
        self.thickness_spin.setSuffix(" px")
        form.addRow("Thickness:", self.thickness_spin)
        
        # Line width
        self.width_spin = QSpinBox()
        self.width_spin.setRange(10, 100)
        self.width_spin.setValue(100)
        self.width_spin.setSuffix("%")
        form.addRow("Width:", self.width_spin)
        
        # Line style
        self.style_combo = QComboBox()
        self.style_combo.addItems(["Solid", "Dashed", "Dotted", "Double"])
        form.addRow("Style:", self.style_combo)
        
        # Line color
        self.color_button = QToolButton()
        self.color_button.setText("Choose Color")
        self.color_button.setStyleSheet(f"background-color: {self.line_color.name()}; min-width: 100px;")
        self.color_button.clicked.connect(self._pick_color)
        form.addRow("Color:", self.color_button)
        
        # Alignment
        self.align_combo = QComboBox()
        self.align_combo.addItems(["Center", "Left", "Right"])
        form.addRow("Alignment:", self.align_combo)
        
        # Margins
        margin_widget = QWidget()
        margin_layout = QHBoxLayout(margin_widget)
        margin_layout.setContentsMargins(0, 0, 0, 0)
        
        self.margin_top_spin = QSpinBox()
        self.margin_top_spin.setRange(0, 100)
        self.margin_top_spin.setValue(10)
        self.margin_top_spin.setSuffix(" px")
        margin_layout.addWidget(QLabel("Top:"))
        margin_layout.addWidget(self.margin_top_spin)
        
        self.margin_bottom_spin = QSpinBox()
        self.margin_bottom_spin.setRange(0, 100)
        self.margin_bottom_spin.setValue(10)
        self.margin_bottom_spin.setSuffix(" px")
        margin_layout.addWidget(QLabel("Bottom:"))
        margin_layout.addWidget(self.margin_bottom_spin)
        
        form.addRow("Margins:", margin_widget)
        
        layout.addLayout(form)
        
        # Preview using a QFrame which respects styling
        layout.addWidget(QLabel("Preview:"))
        self.preview_frame = QWidget()
        self.preview_frame.setMinimumHeight(50)
        self.preview_frame.setStyleSheet("background: white; border: 1px solid #ddd;")
        preview_layout = QVBoxLayout(self.preview_frame)
        preview_layout.setContentsMargins(10, 10, 10, 10)
        
        self.preview_line = QWidget()
        self.preview_line.setFixedHeight(1)
        preview_layout.addWidget(self.preview_line, 0, Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.preview_frame)
        self._update_preview()
        
        # Connect signals for live preview
        self.thickness_spin.valueChanged.connect(self._update_preview)
        self.width_spin.valueChanged.connect(self._update_preview)
        self.style_combo.currentTextChanged.connect(self._update_preview)
        self.align_combo.currentTextChanged.connect(self._update_preview)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _pick_color(self):
        dialog = QColorDialog(self.line_color, self)
        dialog.setWindowTitle("Line Color")
        dialog.setOptions(QColorDialog.ColorDialogOption.DontUseNativeDialog)
        if dialog.exec():
            self.line_color = dialog.currentColor()
            self.color_button.setStyleSheet(f"background-color: {self.line_color.name()}; min-width: 100px;")
            self._update_preview()
    
    def _update_preview(self):
        """Update the preview line widget."""
        color = self.line_color.name()
        thickness = self.thickness_spin.value()
        style = self.style_combo.currentText().lower()
        width_pct = self.width_spin.value()
        align = self.align_combo.currentText()
        
        # Calculate actual width based on preview container
        container_width = self.preview_frame.width() - 20  # minus padding
        if container_width < 100:
            container_width = 300  # default before shown
        line_width = int(container_width * width_pct / 100)
        
        # For double, use border-style: double which needs more height
        if style == "double":
            thickness = max(3, thickness)
        
        # Build border style for QWidget
        border_style = f"{thickness}px {style} {color}"
        
        self.preview_line.setFixedHeight(thickness if style != "double" else thickness)
        self.preview_line.setFixedWidth(line_width)
        self.preview_line.setStyleSheet(f"background: transparent; border-top: {border_style}; border-bottom: none; border-left: none; border-right: none;")
        
        # Update alignment
        preview_layout = self.preview_frame.layout()
        if align == "Left":
            preview_layout.setAlignment(self.preview_line, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        elif align == "Right":
            preview_layout.setAlignment(self.preview_line, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        else:
            preview_layout.setAlignment(self.preview_line, Qt.AlignmentFlag.AlignCenter)
    
    def _get_border_style(self) -> str:
        style_map = {
            "Solid": "solid",
            "Dashed": "dashed",
            "Dotted": "dotted",
            "Double": "double"
        }
        return style_map.get(self.style_combo.currentText(), "solid")
    
    def _get_alignment(self) -> str:
        align_map = {
            "Center": "center",
            "Left": "left",
            "Right": "right"
        }
        return align_map.get(self.align_combo.currentText(), "center")
    
    def get_html(self) -> str:
        """Generate HTML for the horizontal rule using a table (better QTextEdit support)."""
        color = self.line_color.name()
        thickness = self.thickness_spin.value()
        width = self.width_spin.value()
        margin_top = self.margin_top_spin.value()
        margin_bottom = self.margin_bottom_spin.value()
        align = self._get_alignment()
        style = self._get_border_style()
        
        # Use a table-based approach for better QTextEdit compatibility
        align_attr = 'align="center"' if align == "center" else f'align="{align}"'
        
        # For dashed/dotted, we use multiple small cells to simulate
        if style == "dashed":
            # Create dashed effect with repeating colored/transparent pattern
            dash_cells = ''.join([f'<td style="background-color:{color}; width:8px;"></td><td style="width:4px;"></td>' for _ in range(40)])
            return f'''<table {align_attr} width="{width}%" cellspacing="0" cellpadding="0" border="0" style="margin-top:{margin_top}px; margin-bottom:{margin_bottom}px; border-collapse:collapse;">
                <tr style="height:{thickness}px; line-height:{thickness}px; font-size:1px;">{dash_cells}</tr>
            </table>'''
        elif style == "dotted":
            # Create dotted effect with small squares
            dot_cells = ''.join([f'<td style="background-color:{color}; width:{max(2,thickness)}px;"></td><td style="width:{max(2,thickness)}px;"></td>' for _ in range(60)])
            return f'''<table {align_attr} width="{width}%" cellspacing="0" cellpadding="0" border="0" style="margin-top:{margin_top}px; margin-bottom:{margin_bottom}px; border-collapse:collapse;">
                <tr style="height:{max(2,thickness)}px; line-height:{max(2,thickness)}px; font-size:1px;">{dot_cells}</tr>
            </table>'''
        elif style == "double":
            # Create double line with border-top and border-bottom on a single cell
            gap = max(2, thickness)
            return f'''<table {align_attr} width="{width}%" cellspacing="0" cellpadding="0" border="0" style="margin-top:{margin_top}px; margin-bottom:{margin_bottom}px; border-collapse:collapse;">
                <tr><td style="border-top:{thickness}px solid {color}; border-bottom:{thickness}px solid {color}; height:{gap}px; line-height:{gap}px; font-size:1px;"></td></tr>
            </table>'''
        else:
            # Solid line - use border-top on a minimal height cell
            return f'''<table {align_attr} width="{width}%" cellspacing="0" cellpadding="0" border="0" style="margin-top:{margin_top}px; margin-bottom:{margin_bottom}px; border-collapse:collapse;">
                <tr><td style="border-top:{thickness}px solid {color}; height:0; line-height:0; font-size:1px; padding:0;"></td></tr>
            </table>'''


class PageSetupDialog(QDialog):
    """Dialog for page setup options."""
    
    PAGE_SIZES = [
        ("Letter (8.5 x 11 in)", QPageSize.PageSizeId.Letter),
        ("Legal (8.5 x 14 in)", QPageSize.PageSizeId.Legal),
        ("A4 (210 x 297 mm)", QPageSize.PageSizeId.A4),
        ("A3 (297 x 420 mm)", QPageSize.PageSizeId.A3),
        ("A5 (148 x 210 mm)", QPageSize.PageSizeId.A5),
        ("B5 (176 x 250 mm)", QPageSize.PageSizeId.B5),
        ("Executive (7.25 x 10.5 in)", QPageSize.PageSizeId.Executive),
        ("Tabloid (11 x 17 in)", QPageSize.PageSizeId.Tabloid),
    ]
    
    # Margin presets: (name, left, top, right, bottom) in mm
    MARGIN_PRESETS = [
        ("Normal (1 inch)", 25.4, 25.4, 25.4, 25.4),
        ("Narrow (0.5 inch)", 12.7, 12.7, 12.7, 12.7),
        ("Moderate", 19.1, 25.4, 19.1, 25.4),
        ("Wide", 50.8, 25.4, 50.8, 25.4),
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Page Setup")
        self.setMinimumWidth(350)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        size_group = QGroupBox("Paper")
        size_layout = QFormLayout()
        
        self.size_combo = QComboBox()
        for name, _ in self.PAGE_SIZES:
            self.size_combo.addItem(name)
        self.size_combo.setCurrentIndex(2)
        size_layout.addRow("Paper size:", self.size_combo)
        
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItems(["Portrait", "Landscape"])
        size_layout.addRow("Orientation:", self.orientation_combo)
        
        self.margins_combo = QComboBox()
        for name, *_ in self.MARGIN_PRESETS:
            self.margins_combo.addItem(name)
        size_layout.addRow("Margins:", self.margins_combo)
        
        size_group.setLayout(size_layout)
        layout.addWidget(size_group)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_page_size(self) -> QPageSize:
        idx = self.size_combo.currentIndex()
        _, size_id = self.PAGE_SIZES[idx]
        return QPageSize(size_id)
    
    def get_orientation(self) -> QPageLayout.Orientation:
        if self.orientation_combo.currentText() == "Landscape":
            return QPageLayout.Orientation.Landscape
        return QPageLayout.Orientation.Portrait
    
    def get_margins(self) -> QMarginsF:
        idx = self.margins_combo.currentIndex()
        _, left, top, right, bottom = self.MARGIN_PRESETS[idx]
        return QMarginsF(left, top, right, bottom)


class SpecialCharactersDialog(QDialog):
    """Dialog for inserting special characters and symbols."""
    
    CATEGORIES = {
        "Common": "© ® ™ § ¶ † ‡ • ° ± × ÷ ≠ ≤ ≥ ≈ ∞ √ ← → ↑ ↓ ↔",
        "Currency": "$ € £ ¥ ¢ ₹ ₽ ₿ ₩ ₪ ฿",
        "Greek": "Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω",
        "Math": "+ − × ÷ = ≠ < > ≤ ≥ ± ∞ √ ∑ ∏ ∫ ∂ ∇ ∈ ∉ ⊂ ⊃ ∪ ∩ ∧ ∨ ¬",
        "Fractions": "½ ⅓ ⅔ ¼ ¾ ⅕ ⅖ ⅗ ⅘ ⅙ ⅚ ⅛ ⅜ ⅝ ⅞",
        "Super/Sub": "⁰ ¹ ² ³ ⁴ ⁵ ⁶ ⁷ ⁸ ⁹ ⁺ ⁻ ⁿ ₀ ₁ ₂ ₃ ₄ ₅ ₆ ₇ ₈ ₉",
        "Arrows": "← → ↑ ↓ ↔ ↕ ⇐ ⇒ ⇑ ⇓ ⇔ ➔ ➜ ➡ ➢",
        "Shapes": "■ □ ▢ ▲ △ ▼ ▽ ◆ ◇ ○ ● ◐ ◑ ★ ☆",
        "Zodiac": "♈ ♉ ♊ ♋ ♌ ♍ ♎ ♏ ♐ ♑ ♒ ♓",
        "Planets": "☉ ☽ ☿ ♀ ♁ ♂ ♃ ♄ ♅ ♆",
        "Music": "♩ ♪ ♫ ♬ ♭ ♮ ♯",
        "Cards": "♠ ♡ ♢ ♣ ♤ ♥ ♦ ♧",
        "Misc": "☀ ☁ ☂ ☃ ☄ ★ ☆ ☎ ☐ ☑ ☒ ☮ ☯ ☸ ☹ ☺ ☻ ☼ ☽ ☾ ♀ ♂",
    }
    
    char_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Special Characters")
        self.setMinimumSize(450, 350)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        
        for category, chars in self.CATEGORIES.items():
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            
            container = QWidget()
            grid = QGridLayout(container)
            grid.setSpacing(2)
            
            char_list = chars.split()
            cols = 10
            for i, char in enumerate(char_list):
                btn = QPushButton(char)
                btn.setFixedSize(32, 32)
                btn.setFont(QFont("Segoe UI Symbol", 12))
                btn.clicked.connect(lambda checked, c=char: self._on_char_clicked(c))
                grid.addWidget(btn, i // cols, i % cols)
            
            scroll.setWidget(container)
            self.tabs.addTab(scroll, category)
        
        layout.addWidget(self.tabs)
        
        self.selected_label = QLabel("Click a character to insert")
        layout.addWidget(self.selected_label)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
    
    def _on_char_clicked(self, char: str):
        self.selected_label.setText(f"Inserted: {char}")
        self.char_selected.emit(char)


class ExportPdfDialog(QDialog):
    """Dialog for PDF export options."""
    
    PAGE_SIZES = PageSetupDialog.PAGE_SIZES
    MARGIN_PRESETS = PageSetupDialog.MARGIN_PRESETS
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export to PDF")
        self.setMinimumWidth(400)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        file_group = QGroupBox("Output File")
        file_layout = QHBoxLayout()
        
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("Select output file...")
        file_layout.addWidget(self.file_input)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_file)
        file_layout.addWidget(browse_btn)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        page_group = QGroupBox("Page Setup")
        page_layout = QFormLayout()
        
        self.size_combo = QComboBox()
        for name, _ in self.PAGE_SIZES:
            self.size_combo.addItem(name)
        self.size_combo.setCurrentIndex(2)
        page_layout.addRow("Paper size:", self.size_combo)
        
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItems(["Portrait", "Landscape"])
        page_layout.addRow("Orientation:", self.orientation_combo)
        
        self.margins_combo = QComboBox()
        for name, *_ in self.MARGIN_PRESETS:
            self.margins_combo.addItem(name)
        page_layout.addRow("Margins:", self.margins_combo)
        
        page_group.setLayout(page_layout)
        layout.addWidget(page_group)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Export")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _browse_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export PDF", "", "PDF Files (*.pdf)"
        )
        if path:
            if not path.endswith('.pdf'):
                path += '.pdf'
            self.file_input.setText(path)
    
    def get_file_path(self) -> str:
        return self.file_input.text()
    
    def get_page_size(self) -> QPageSize:
        idx = self.size_combo.currentIndex()
        _, size_id = self.PAGE_SIZES[idx]
        return QPageSize(size_id)
    
    def get_orientation(self) -> QPageLayout.Orientation:
        if self.orientation_combo.currentText() == "Landscape":
            return QPageLayout.Orientation.Landscape
        return QPageLayout.Orientation.Portrait
    
    def get_margins(self) -> QMarginsF:
        idx = self.margins_combo.currentIndex()
        _, left, top, right, bottom = self.MARGIN_PRESETS[idx]
        return QMarginsF(left, top, right, bottom)


class RichTextEditor(QWidget):
    """
    A comprehensive rich text editor widget with a Ribbon interface.
    """
    
    # Signal emitted when text changes
    text_changed = pyqtSignal()
    
    # Signal emitted when [[ is typed
    wiki_link_requested = pyqtSignal()
    
    def __init__(self, parent=None, placeholder_text="Start typing...", show_ui=True):
        super().__init__(parent)
        self.virtual_keyboard: VirtualKeyboard | None = None
        
        # Styles Definition
        self.styles = {
            "Normal": {"size": 12, "weight": QFont.Weight.Normal, "family": "Arial"},
            "Title": {"size": 28, "weight": QFont.Weight.Bold, "family": "Arial"},
            "Heading 1": {"size": 24, "weight": QFont.Weight.Bold, "family": "Arial"},
            "Heading 2": {"size": 18, "weight": QFont.Weight.Bold, "family": "Arial"},
            "Heading 3": {"size": 14, "weight": QFont.Weight.Bold, "family": "Arial"},
            "Code": {"size": 10, "weight": QFont.Weight.Normal, "family": "Courier New"},
        }
        
        # Features
        self.search_feature = None # Lazy or init later? better init in setup
        
        self._setup_ui(placeholder_text, show_ui)
        self._init_features() 
        
        # Force LTR by default to prevent auto-detection issues
        self.editor.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        
    def _setup_ui(self, placeholder_text, show_ui):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # --- Ribbon ---
        if show_ui:
            self.ribbon = RibbonWidget()
            layout.addWidget(self.ribbon)
        
        # --- Editor ---
        self.editor = SafeTextEdit()
        self.editor.setPlaceholderText(placeholder_text)
        self.editor.setStyleSheet("""
            QTextEdit {
                border: none;
                padding: 10px; /* Reduced padding for canvas */
                background-color: #fefefe;
                selection-background-color: #bfdbfe;
                selection-color: #1e293b;
                font-size: 11pt;
                line-height: 1.6;
            }
            QScrollBar:vertical {
                background: #f1f5f9;
                width: 10px;
                border-radius: 5px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        self.editor.textChanged.connect(self.text_changed.emit)
        self.editor.textChanged.connect(self._check_wiki_link_trigger)
        self.editor.currentCharFormatChanged.connect(self._update_format_widgets)
        
        # Initialize features that depend on editor
        self.search_feature = SearchReplaceFeature(self.editor, self)
        
        # Context Menu
        self.editor.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.editor.customContextMenuRequested.connect(self._show_context_menu)
        
        layout.addWidget(self.editor)
        
        if show_ui:
            # --- Status Bar with Word Count and Zoom ---
            self.status_bar = QStatusBar()
            self.status_bar.setStyleSheet("""
                QStatusBar {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f8fafc, stop:1 #e2e8f0);
                    border-top: 1px solid #cbd5e1;
                    padding: 2px 8px;
                }
                QStatusBar QLabel {
                    color: #475569;
                    font-size: 9pt;
                }
                QSlider::groove:horizontal {
                    height: 6px;
                    background: #e2e8f0;
                    border-radius: 3px;
                }
                QSlider::handle:horizontal {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff, stop:1 #e2e8f0);
                    border: 1px solid #94a3b8;
                    width: 14px;
                    margin: -4px 0;
                    border-radius: 7px;
                }
                QSlider::handle:horizontal:hover {
                    background: #dbeafe;
                    border-color: #3b82f6;
                }
                QToolButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff, stop:1 #f1f5f9);
                    border: 1px solid #cbd5e1;
                    border-radius: 4px;
                    padding: 3px 8px;
                    color: #475569;
                    font-weight: 500;
                }
                QToolButton:hover {
                    background: #eff6ff;
                    border-color: #93c5fd;
                    color: #1d4ed8;
                }
            """)
            
            # Word count label
            self.word_count_label = QLabel("Words: 0 | Characters: 0")
            self.status_bar.addWidget(self.word_count_label)
            
            # Spacer
            self.status_bar.addWidget(QLabel(""), 1)  # Stretch
            
            # Zoom controls
            zoom_widget = QWidget()
            zoom_layout = QHBoxLayout(zoom_widget)
            zoom_layout.setContentsMargins(0, 0, 0, 0)
            zoom_layout.setSpacing(5)
            
            self.zoom_label = QLabel("100%")
            self.zoom_label.setMinimumWidth(40)
            
            self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
            self.zoom_slider.setRange(25, 400)
            self.zoom_slider.setValue(100)
            self.zoom_slider.setFixedWidth(100)
            self.zoom_slider.valueChanged.connect(self._on_zoom_changed)
            
            btn_zoom_out = QToolButton()
            btn_zoom_out.setText("-")
            btn_zoom_out.clicked.connect(lambda: self.zoom_slider.setValue(max(25, self.zoom_slider.value() - 25)))
            
            btn_zoom_in = QToolButton()
            btn_zoom_in.setText("+")
            btn_zoom_in.clicked.connect(lambda: self.zoom_slider.setValue(min(400, self.zoom_slider.value() + 25)))
            
            btn_zoom_reset = QToolButton()
            btn_zoom_reset.setText("100%")
            btn_zoom_reset.setToolTip("Reset Zoom")
            btn_zoom_reset.clicked.connect(lambda: self.zoom_slider.setValue(100))
            
            zoom_layout.addWidget(btn_zoom_out)
            zoom_layout.addWidget(self.zoom_slider)
            zoom_layout.addWidget(btn_zoom_in)
            zoom_layout.addWidget(self.zoom_label)
            zoom_layout.addWidget(btn_zoom_reset)
            
            self.status_bar.addPermanentWidget(zoom_widget)
            layout.addWidget(self.status_bar)
            
            # Connect text changed to update word count
            self.editor.textChanged.connect(self._update_word_count)
        
        # Keybindings (Available even with show_ui=False)
        self.action_find = QAction("Find", self)
        self.action_find.setShortcut("Ctrl+F")
        self.action_find.triggered.connect(self.search_feature.show_search_dialog)
        self.addAction(self.action_find)
        
        if show_ui:
            # Initialize Ribbon Content (must be after action_find is created)
            self._init_ribbon()

    def insertFromMimeData(self, source):
        """
        Override paste behavior to protect against 'Paste Attacks' (Mars Seal).
        Warns user if pasting massive content that could freeze the UI.
        """
        # Threshold: 100,000 chars (approx 20-30 pages of text)
        WARN_THRESHOLD = 100000
        
        if source.hasText():
            text = source.text()
            if len(text) > WARN_THRESHOLD:
                # Mars Warning: Chaos detected
                reply = QMessageBox.warning(
                    self, 
                    "Large Paste Detected",
                    f"You are attempting to paste {len(text):,} characters.\n"
                    "This may temporarily freeze the application.\n\n"
                    "Do you wish to proceed?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
        
        # Standard Qt behavior if safe or approved
        super().insertFromMimeData(source) # type: ignore

    def _check_wiki_link_trigger(self):
        """Check if the user just typed '[['."""
        cursor = self.editor.textCursor()
        position = cursor.position()
        
        if position < 2:
            return
            
        cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, 2)
        text = cursor.selectedText()
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, 2)
        
        if text == "[[":
            self.wiki_link_requested.emit()

    def _show_context_menu(self, pos):
        """Show context menu with table options if applicable."""
        cursor = self.editor.cursorForPosition(pos)
        self.editor.setTextCursor(cursor)
        
        menu = self.editor.createStandardContextMenu()
        
        if menu is not None:
            if hasattr(self, 'table_feature'):
                self.table_feature.extend_context_menu(menu)
            if hasattr(self, 'image_feature'):
                self.image_feature.extend_context_menu(menu)
            menu.exec(self.editor.mapToGlobal(pos))

    def _init_features(self):
        """Initialize features that don't require the Ribbon UI."""
        # Lists - always needed
        self.list_feature = ListFeature(self.editor, self)
        
        # Note: table_feature and image_feature are initialized in _init_ribbon()
        # when show_ui=True. For headless mode, they can be initialized here:
        if not hasattr(self, 'table_feature') and 'TableFeature' in globals():
            self.table_feature = TableFeature(self.editor, self)
             
        if not hasattr(self, 'image_feature') and 'ImageFeature' in globals():
            self.image_feature = ImageFeature(self.editor, self)

    def show_search(self):
        """Public API for Global Ribbon."""
        # Initialize if strictly needed or assume _init_features did it
        if not hasattr(self, 'search_feature'):
             self.search_feature = SearchReplaceFeature(self.editor, self)
        self.search_feature.show_search_dialog()

    def toggle_list(self, style):
        """Public API for Global Ribbon."""
        if hasattr(self, 'list_feature'):
            self.list_feature.toggle_list(style)

    def set_alignment(self, align):
        """Public API for Global Ribbon."""
        self.editor.setAlignment(align)

    def insert_table(self, rows=3, cols=3):
        """Public API for Global Ribbon."""
        if hasattr(self, 'table_feature'):
             self.table_feature.insert_table(rows, cols)

    def insert_image(self):
        """Public API for Global Ribbon."""
        if hasattr(self, 'image_feature'):
            self.image_feature.insert_image()

    def set_highlight(self, color):
        """Public API for Global Ribbon."""
        fmt = QTextCharFormat()
        fmt.setBackground(color)
        self.editor.mergeCurrentCharFormat(fmt)
    
    def clear_formatting(self):
        """Public API"""
        self._clear_formatting()

    def toggle_strikethrough(self):
        self._toggle_strikethrough()

    def toggle_subscript(self):
        self._toggle_subscript()

    def toggle_superscript(self):
        self._toggle_superscript()

    def _init_ribbon(self):
        """Populate the ribbon with tabs and groups."""
        
        # === TAB: HOME ===
        tab_home = self.ribbon.add_ribbon_tab("Home")
        
        # Group: Clipboard
        grp_clip = tab_home.add_group("Clipboard")
        
        self.action_undo = QAction("Undo", self)
        self.action_undo.setShortcut("Ctrl+Z")
        self.action_undo.triggered.connect(self.editor.undo)
        grp_clip.add_action(self.action_undo)
        
        self.action_redo = QAction("Redo", self)
        self.action_redo.setShortcut("Ctrl+Y")
        self.action_redo.triggered.connect(self.editor.redo)
        grp_clip.add_action(self.action_redo)

        # Group: Styles (New)
        grp_style = tab_home.add_group("Styles")
        self.style_combo = QComboBox()
        self.style_combo.addItems(list(self.styles.keys()))
        self.style_combo.currentTextChanged.connect(self._apply_style)
        self.style_combo.setMinimumWidth(120)
        grp_style.add_widget(self.style_combo)

        # Group: Font
        grp_font = tab_home.add_group("Font")
        
        # Font Row 1: Combo boxes
        font_box = QWidget()
        font_layout = QHBoxLayout(font_box)
        font_layout.setContentsMargins(0,0,0,0)
        
        self.font_combo = QFontComboBox()
        self.font_combo.setMaximumWidth(150)
        self.font_combo.currentFontChanged.connect(self.editor.setCurrentFont)
        font_layout.addWidget(self.font_combo)
        
        self.size_combo = QComboBox()
        self.size_combo.setEditable(True)
        self.size_combo.setMaximumWidth(60)
        sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]
        self.size_combo.addItems([str(s) for s in sizes])
        self.size_combo.setCurrentText("12")
        self.size_combo.textActivated.connect(self._set_font_size)
        font_layout.addWidget(self.size_combo)
        
        grp_font.add_widget(font_box)
        
        # Font Row 2: Buttons (Bold, Italic, Underline)
        self.action_bold = QAction("B", self)
        self.action_bold.setCheckable(True)
        self.action_bold.setShortcut("Ctrl+B")
        self.action_bold.triggered.connect(self._toggle_bold)
        self.action_bold.setFont(QFont("serif", weight=QFont.Weight.Bold))
        grp_font.add_action(self.action_bold, Qt.ToolButtonStyle.ToolButtonTextOnly) # Compact
        
        self.action_italic = QAction("I", self)
        self.action_italic.setCheckable(True)
        self.action_italic.setShortcut("Ctrl+I")
        self.action_italic.triggered.connect(self.editor.setFontItalic)
        self.action_italic.setFont(QFont("serif", italic=True))
        grp_font.add_action(self.action_italic, Qt.ToolButtonStyle.ToolButtonTextOnly)

        self.action_underline = QAction("U", self)
        self.action_underline.setCheckable(True)
        self.action_underline.setShortcut("Ctrl+U")
        self.action_underline.triggered.connect(self.editor.setFontUnderline)
        grp_font.add_action(self.action_underline, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        # Strikethrough
        self.action_strike = QAction("S", self)
        self.action_strike.setCheckable(True)
        self.action_strike.setToolTip("Strikethrough")
        self.action_strike.triggered.connect(self._toggle_strikethrough)
        # Fallback icon or text if theme icon missing? Text S with strike is hard in plain text
        # Using theme icon
        self.action_strike.setIcon(QIcon.fromTheme("format-text-strikethrough"))
        if self.action_strike.icon().isNull():
            self.action_strike.setText("S̶") 
        grp_font.add_action(self.action_strike)

        # Subscript
        self.action_sub = QAction("Sub", self)
        self.action_sub.setCheckable(True)
        self.action_sub.setToolTip("Subscript")
        self.action_sub.triggered.connect(self._toggle_subscript)
        self.action_sub.setIcon(QIcon.fromTheme("format-text-subscript"))
        if self.action_sub.icon().isNull():
             self.action_sub.setText("X₂")
        grp_font.add_action(self.action_sub)

        # Superscript
        self.action_super = QAction("Sup", self)
        self.action_super.setCheckable(True)
        self.action_super.setToolTip("Superscript")
        self.action_super.triggered.connect(self._toggle_superscript)
        self.action_super.setIcon(QIcon.fromTheme("format-text-superscript"))
        if self.action_super.icon().isNull():
             self.action_super.setText("X²")
        grp_font.add_action(self.action_super)
        
        # Clear Formatting
        self.action_clear = QAction("Clear", self)
        self.action_clear.setToolTip("Clear Formatting")
        self.action_clear.triggered.connect(self._clear_formatting)
        self.action_clear.setIcon(QIcon.fromTheme("format-text-clear")) # or edit-clear
        if self.action_clear.icon().isNull():
             self.action_clear.setText("oslash")
        grp_font.add_action(self.action_clear)
        
        # Colors
        btn_color = QToolButton()
        btn_color.setIcon(QIcon()) # Placeholder for now or text
        btn_color.setText("Color")
        btn_color.setToolTip("Text Color")
        btn_color.clicked.connect(self._pick_color)
        grp_font.add_widget(btn_color)
        
        btn_highlight = QToolButton()
        btn_highlight.setText("High")
        btn_highlight.setToolTip("Highlight")
        btn_highlight.clicked.connect(self._pick_highlight)
        grp_font.add_widget(btn_highlight)
        
        btn_clear = QToolButton()
        btn_clear.setText("No Color")
        btn_clear.setToolTip("Clear Highlight")
        btn_clear.clicked.connect(self._clear_highlight)
        grp_font.add_widget(btn_clear)
        
        # Group: Paragraph
        grp_para = tab_home.add_group("Paragraph")
        
        # Alignment Group (Exclusive)
        align_group = QActionGroup(self)
        
        self.action_align_left = QAction("Left", self)
        self.action_align_left.setCheckable(True)
        self.action_align_left.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignLeft))
        align_group.addAction(self.action_align_left)
        grp_para.add_action(self.action_align_left, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        self.action_align_center = QAction("Center", self)
        self.action_align_center.setCheckable(True)
        self.action_align_center.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignCenter))
        align_group.addAction(self.action_align_center)
        grp_para.add_action(self.action_align_center, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        self.action_align_right = QAction("Right", self)
        self.action_align_right.setCheckable(True)
        self.action_align_right.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignRight))
        align_group.addAction(self.action_align_right)
        grp_para.add_action(self.action_align_right, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        self.action_align_justify = QAction("Justify", self)
        self.action_align_justify.setCheckable(True)
        self.action_align_justify.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignJustify))
        align_group.addAction(self.action_align_justify)
        grp_para.add_action(self.action_align_justify, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        
        grp_para.add_separator()
        
        # Lists & Indentation
        self.list_feature = ListFeature(self.editor, self)
        
        self.action_list_bullet = QAction("• List", self)
        self.action_list_bullet.triggered.connect(lambda: self.list_feature.toggle_list(QTextListFormat.Style.ListDisc))
        grp_para.add_action(self.action_list_bullet, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        self.action_list_number = QAction("1. List", self)
        self.action_list_number.triggered.connect(lambda: self.list_feature.toggle_list(QTextListFormat.Style.ListDecimal))
        grp_para.add_action(self.action_list_number, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        grp_para.add_separator()
        
        self.action_outdent = QAction("<< Out", self)
        self.action_outdent.setToolTip("Decrease Indent")
        self.action_outdent.triggered.connect(self.list_feature.outdent)
        grp_para.add_action(self.action_outdent, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        self.action_indent = QAction("In >>", self)
        self.action_indent.setToolTip("Increase Indent")
        self.action_indent.triggered.connect(self.list_feature.indent)
        grp_para.add_action(self.action_indent, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        grp_para.add_separator()
        
        # Line Spacing dropdown
        self.spacing_combo = QComboBox()
        self.spacing_combo.addItems(["1.0", "1.15", "1.5", "2.0", "2.5", "3.0"])
        self.spacing_combo.setCurrentText("1.0")
        self.spacing_combo.setToolTip("Line Spacing")
        self.spacing_combo.currentTextChanged.connect(self._set_line_spacing)
        self.spacing_combo.setMaximumWidth(60)
        grp_para.add_widget(self.spacing_combo)
        
        # Text Direction (RTL/LTR)
        self.action_rtl = QAction("RTL", self)
        self.action_rtl.setCheckable(True)
        self.action_rtl.setToolTip("Right-to-Left (Hebrew, Arabic)")
        self.action_rtl.triggered.connect(self._toggle_text_direction)
        grp_para.add_action(self.action_rtl, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        # Group: Edit
        grp_edit = tab_home.add_group("Edit")
        # Reuse the action defined in setup_ui which has the shortcut
        grp_edit.add_action(self.action_find, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        # === TAB: INSERT ===
        tab_insert = self.ribbon.add_ribbon_tab("Insert")
        
        # Group: Tables
        grp_tables = tab_insert.add_group("Tables")
        self.table_feature = TableFeature(self.editor, self)
        # Adding the toolbar button from the feature
        # We need to extract the action or just add the widget
        grp_tables.add_widget(self.table_feature.create_toolbar_button())
        
        # Group: Illustrations
        grp_illus = tab_insert.add_group("Illustrations")
        self.image_feature = ImageFeature(self.editor, self)
        grp_illus.add_action(self.image_feature.create_toolbar_action(), Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # Group: Symbols
        grp_sym = tab_insert.add_group("Symbols")
        
        action_kb = QAction("Keyboard", self)
        action_kb.setToolTip("Open Virtual Keyboard (Hebrew, Greek, Esoteric)")
        action_kb.triggered.connect(self._show_virtual_keyboard)
        grp_sym.add_action(action_kb, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # Group: Links
        grp_links = tab_insert.add_group("Links")
        
        action_hyperlink = QAction("Hyperlink", self)
        action_hyperlink.setToolTip("Insert Hyperlink (Ctrl+K)")
        action_hyperlink.setShortcut("Ctrl+K")
        action_hyperlink.triggered.connect(self._insert_hyperlink)
        grp_links.add_action(action_hyperlink, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addAction(action_hyperlink)  # Enable shortcut
        
        # Group: Elements
        grp_elements = tab_insert.add_group("Elements")
        
        action_hr = QAction("Horizontal Line", self)
        action_hr.setToolTip("Insert Horizontal Rule")
        action_hr.triggered.connect(self._insert_horizontal_rule)
        grp_elements.add_action(action_hr, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        action_special = QAction("Special Char", self)
        action_special.setToolTip("Insert Special Characters")
        action_special.triggered.connect(self._show_special_characters)
        grp_elements.add_action(action_special, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # === TAB: PAGE LAYOUT ===
        tab_page = self.ribbon.add_ribbon_tab("Page Layout")
        
        # Group: Page Setup
        grp_page = tab_page.add_group("Page Setup")
        
        action_page_setup = QAction("Page Setup", self)
        action_page_setup.setToolTip("Set page size, orientation, margins")
        action_page_setup.triggered.connect(self._show_page_setup)
        grp_page.add_action(action_page_setup, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # Group: Export
        grp_export = tab_page.add_group("Export")
        
        action_pdf = QAction("Export PDF", self)
        action_pdf.setToolTip("Export document to PDF (Ctrl+Shift+E)")
        action_pdf.setShortcut("Ctrl+Shift+E")
        action_pdf.triggered.connect(self._export_pdf)
        grp_export.add_action(action_pdf, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addAction(action_pdf)
        
        action_print = QAction("Print", self)
        action_print.setToolTip("Print document (Ctrl+P)")
        action_print.setShortcut("Ctrl+P")
        action_print.triggered.connect(self._print_document)
        grp_export.add_action(action_print, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addAction(action_print)
        
        action_preview = QAction("Print Preview", self)
        action_preview.setToolTip("Preview before printing")
        action_preview.triggered.connect(self._print_preview)
        grp_export.add_action(action_preview, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

    def _set_font_size(self, size_str):
        try:
            size = float(size_str)
            self.editor.setFontPointSize(size)
        except ValueError:
            pass

    def _toggle_bold(self):
        font_weight = self.editor.fontWeight()
        if font_weight == QFont.Weight.Bold:
            self.editor.setFontWeight(QFont.Weight.Normal)
        else:
            self.editor.setFontWeight(QFont.Weight.Bold)

    def _toggle_strikethrough(self):
        """Toggle strikethrough formatting."""
        fmt = self.editor.currentCharFormat()
        fmt.setFontStrikeOut(not fmt.fontStrikeOut())
        self.editor.mergeCurrentCharFormat(fmt)

    def _toggle_subscript(self):
        """Toggle subscript, exclusive with superscript."""
        fmt = self.editor.currentCharFormat()
        if fmt.verticalAlignment() == QTextCharFormat.VerticalAlignment.AlignSubScript:
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignNormal)
        else:
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSubScript)
        self.editor.mergeCurrentCharFormat(fmt)

    def _toggle_superscript(self):
        """Toggle superscript, exclusive with subscript."""
        fmt = self.editor.currentCharFormat()
        if fmt.verticalAlignment() == QTextCharFormat.VerticalAlignment.AlignSuperScript:
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignNormal)
        else:
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSuperScript)
        self.editor.mergeCurrentCharFormat(fmt)

    def _clear_formatting(self):
        """
        Reset character formatting to default for the current selection, 
        preserves block formatting.
        """
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            # Create a clean format
            fmt = QTextCharFormat()
            # We can't just use empty fmt because merge won't unset properties.
            # We have to explicitly set default properties.
            
            # Reset Font
            default_font = QFont("Arial", 12)
            fmt.setFont(default_font)
            fmt.setFontWeight(QFont.Weight.Normal)
            fmt.setFontItalic(False)
            fmt.setFontUnderline(False)
            fmt.setFontStrikeOut(False)
            
            # Reset Color
            fmt.setForeground(Qt.GlobalColor.black)
            fmt.setBackground(QBrush(Qt.BrushStyle.NoBrush))
            
            # Reset Alignment
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignNormal)
            
            # Apply
            # setCharFormat applied to selection replaces all char properties
            cursor.setCharFormat(fmt)
            self.editor.setFocus()


    def _pick_color(self):
        """
        Open a color picker to set the text color.
        Uses non-native dialog to avoid linux platform integration issues.
        """
        cursor = self.editor.textCursor()
        # Get current color
        fmt = cursor.charFormat()
        current_color = fmt.foreground().color()
        if not current_color.isValid():
            current_color = Qt.GlobalColor.black
        
        # UX Improvement: If color is Black (Value 0), the picker opens in "The Abyss" (Slider at bottom).
        # We default to Red to force the Value Slider to Max, allowing immediate color selection.
        initial_color = current_color
        if current_color.lightness() == 0:
            initial_color = Qt.GlobalColor.red
            
        dialog = QColorDialog(initial_color, self)
        dialog.setWindowTitle("Select Text Color")
        dialog.setOptions(QColorDialog.ColorDialogOption.ShowAlphaChannel | 
                          QColorDialog.ColorDialogOption.DontUseNativeDialog)
        
        if dialog.exec():
            color = dialog.currentColor()
            if color.isValid():
                # Apply using mergeCharFormat for robustness
                new_fmt = QTextCharFormat()
                new_fmt.setForeground(color)
                self.editor.mergeCurrentCharFormat(new_fmt)
                self.editor.setFocus()

    def _apply_style(self, style_name):
        """Apply a semantic style to the current selection/block."""
        if style_name not in self.styles:
            return
            
        style = self.styles[style_name]
        cursor = self.editor.textCursor()
        
        # If no selection, apply to the entire block (paragraph)
        if not cursor.hasSelection():
            cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        
        
        
        # Fallback to HTML insertion for robust styling if direct formatting fails
        # This is a bit heavier but guarantees the style is applied by the engine parser
        
        
        selected_text = cursor.selectedText()
        # Replace Paragraph Separator with space or nothing, as we are wrapping in block tag
        selected_text = selected_text.replace('\u2029', '')
            
        # Determine tag
        tag = "p"
        if style_name == "Heading 1": tag = "h1"
        elif style_name == "Heading 2": tag = "h2"
        elif style_name == "Heading 3": tag = "h3"
        elif style_name == "Title": tag = "h1" # Title as h1 for now
        elif style_name == "Code": tag = "pre"
        
        # Build HTML with inline style to enforce our specific look (font, size)
        # Note: h1 in Qt might have default margins, we can override if needed
        pt_size = style["size"]
        family = style["family"]
        # font-weight is handled by h1 usually, but we enforce specific
        weight_css = "bold" if style["weight"] == QFont.Weight.Bold else "normal"
        
        # We need to ensure the styling applies. 
        # Using a span inside the block tag often helps Qt parser.
        html = f'<{tag} style="margin-top: 10px; margin-bottom: 5px;"><span style="font-family: {family}; font-size: {pt_size}pt; font-weight: {weight_css};">{selected_text}</span></{tag}>'
        
        self.editor.blockSignals(True)
        cursor.insertHtml(html)
        self.editor.blockSignals(False)
        
        # Update combo boxes manually to reflect the change visually in toolbar
        self.size_combo.setCurrentText(str(style["size"]))
        self.font_combo.setCurrentFont(QFont(style["family"]))

    def _pick_highlight(self):
        cursor = self.editor.textCursor()
        fmt = cursor.charFormat()
        current_bg = fmt.background().color()
        if not current_bg.isValid():
            current_bg = Qt.GlobalColor.white

        dialog = QColorDialog(current_bg, self)
        dialog.setWindowTitle("Select Highlight Color")
        dialog.setOptions(QColorDialog.ColorDialogOption.ShowAlphaChannel | 
                          QColorDialog.ColorDialogOption.DontUseNativeDialog)
                          
        if dialog.exec():
            color = dialog.currentColor()
            if color.isValid():
                new_fmt = QTextCharFormat()
                new_fmt.setBackground(color)
                self.editor.mergeCurrentCharFormat(new_fmt)
                self.editor.setFocus()

    def _clear_highlight(self):
        """Clear the background highlight."""
        self.editor.setTextBackgroundColor(QColor(Qt.GlobalColor.transparent))

    def _on_zoom_changed(self, value: int):
        """Handle zoom slider change."""
        self.zoom_label.setText(f"{value}%")
        # Scale the editor using CSS zoom or font scaling
        # QTextEdit doesn't have native zoom, so we scale via transform
        scale = value / 100.0
        self.editor.setStyleSheet(f"""
            QTextEdit {{
                border: none;
                padding: 40px;
                background-color: white;
                selection-background-color: #bfdbfe;
                selection-color: black;
            }}
        """)
        # Apply zoom via viewport transform
        from PyQt6.QtGui import QTransform
        transform = QTransform()
        transform.scale(scale, scale)
        # Note: QTextEdit doesn't support transforms directly on viewport
        # Alternative: adjust font size proportionally
        # We'll use zoomIn/zoomOut approach
        self.editor.zoomIn(0)  # Reset first
        base_zoom = value - 100
        if base_zoom != 0:
            # zoomIn takes steps, each step is roughly 1 point
            # This is approximate but works well
            steps = base_zoom // 10
            if steps > 0:
                self.editor.zoomIn(steps)
            elif steps < 0:
                self.editor.zoomOut(-steps)

    def _update_word_count(self):
        """Update the word and character count in status bar."""
        text = self.editor.toPlainText()
        char_count = len(text)
        # Word count: split by whitespace, filter empty
        words = [w for w in text.split() if w.strip()]
        word_count = len(words)
        # Paragraph count: split by newlines
        paragraphs = [p for p in text.split('\n') if p.strip()]
        para_count = len(paragraphs) if paragraphs else 0
        
        self.word_count_label.setText(
            f"Words: {word_count:,} | Characters: {char_count:,} | Paragraphs: {para_count:,}"
        )

    def _set_line_spacing(self, spacing_str: str):
        """Set line spacing for the current paragraph."""
        try:
            spacing = float(spacing_str)
        except ValueError:
            return
        
        cursor = self.editor.textCursor()
        block_fmt = cursor.blockFormat()
        
        # Qt uses line height as percentage (100 = single, 150 = 1.5, etc.)
        # Or we can use setLineHeight with specific type
        from PyQt6.QtGui import QTextBlockFormat
        block_fmt.setLineHeight(spacing * 100, QTextBlockFormat.LineHeightTypes.ProportionalHeight.value)
        cursor.setBlockFormat(block_fmt)

    def _toggle_text_direction(self):
        """Toggle between LTR and RTL text direction."""
        cursor = self.editor.textCursor()
        block_fmt = cursor.blockFormat()
        
        current_dir = block_fmt.layoutDirection()
        if current_dir == Qt.LayoutDirection.RightToLeft:
            block_fmt.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            self.action_rtl.setChecked(False)
        else:
            block_fmt.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            self.action_rtl.setChecked(True)
        
        cursor.setBlockFormat(block_fmt)

    def _insert_hyperlink(self):
        """Insert a hyperlink at the current cursor position."""
        cursor = self.editor.textCursor()
        selected_text = cursor.selectedText() if cursor.hasSelection() else ""
        
        dialog = HyperlinkDialog(selected_text, self)
        if dialog.exec():
            url = dialog.url_input.text().strip()
            display_text = dialog.text_input.text().strip() or url
            
            if url:
                # Ensure URL has a scheme
                if not url.startswith(('http://', 'https://', 'mailto:', 'file://')):
                    url = 'https://' + url
                
                # Insert as HTML anchor
                html = f'<a href="{url}">{display_text}</a>'
                cursor.insertHtml(html)

    def _insert_horizontal_rule(self):
        """Insert a horizontal rule at the current cursor position."""
        dialog = HorizontalRuleDialog(self)
        if dialog.exec():
            cursor = self.editor.textCursor()
            # Insert the HR - no need for insertBlock as HR is a block element
            cursor.insertHtml(dialog.get_html())

    def _show_special_characters(self):
        """Show the special characters dialog."""
        if not hasattr(self, '_special_chars_dialog') or self._special_chars_dialog is None:
            self._special_chars_dialog = SpecialCharactersDialog(self)
            self._special_chars_dialog.char_selected.connect(self._insert_special_char)
        self._special_chars_dialog.show()
        self._special_chars_dialog.raise_()

    def _insert_special_char(self, char: str):
        """Insert a special character at cursor position."""
        cursor = self.editor.textCursor()
        cursor.insertText(char)
        self.editor.setFocus()

    def _show_page_setup(self):
        """Show page setup dialog."""
        dialog = PageSetupDialog(self)
        if dialog.exec():
            # Store page settings for later use in printing/export
            self._page_size = dialog.get_page_size()
            self._page_orientation = dialog.get_orientation()
            self._page_margins = dialog.get_margins()
            QMessageBox.information(self, "Page Setup", "Page settings saved for printing/export.")

    def _export_pdf(self):
        """Export document to PDF."""
        dialog = ExportPdfDialog(self)
        if dialog.exec():
            file_path = dialog.get_file_path()
            if not file_path:
                QMessageBox.warning(self, "Export PDF", "Please specify an output file.")
                return
            
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)
            
            # Set page layout
            page_layout = QPageLayout(
                dialog.get_page_size(),
                dialog.get_orientation(),
                dialog.get_margins(),
                QPageLayout.Unit.Millimeter
            )
            printer.setPageLayout(page_layout)
            
            # Print document to PDF
            self.editor.document().print(printer)
            
            QMessageBox.information(self, "Export PDF", f"Document exported to:\n{file_path}")

    def _print_document(self):
        """Print the document."""
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        
        # Apply saved page settings if available
        if hasattr(self, '_page_size'):
            page_layout = QPageLayout(
                self._page_size,
                getattr(self, '_page_orientation', QPageLayout.Orientation.Portrait),
                getattr(self, '_page_margins', QMarginsF(20, 20, 20, 20)),
                QPageLayout.Unit.Millimeter
            )
            printer.setPageLayout(page_layout)
        
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            self.editor.document().print(printer)

    def _print_preview(self):
        """Show print preview dialog."""
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        
        # Apply saved page settings if available
        if hasattr(self, '_page_size'):
            page_layout = QPageLayout(
                self._page_size,
                getattr(self, '_page_orientation', QPageLayout.Orientation.Portrait),
                getattr(self, '_page_margins', QMarginsF(20, 20, 20, 20)),
                QPageLayout.Unit.Millimeter
            )
            printer.setPageLayout(page_layout)
        
        preview = QPrintPreviewDialog(printer, self)
        preview.setMinimumSize(800, 600)
        preview.resize(1000, 750)
        preview.paintRequested.connect(lambda p: self.editor.document().print(p))
        preview.exec()



    def _show_virtual_keyboard(self):
        self.virtual_keyboard = get_shared_virtual_keyboard(self)
        self.virtual_keyboard.set_target_editor(self.editor)
        self.virtual_keyboard.show()
        self.virtual_keyboard.raise_()
        self.virtual_keyboard.activateWindow()

    def _update_format_widgets(self, fmt):
        """Update the ribbon widgets based on the current text format."""
        if not hasattr(self, 'font_combo'):
            return

        # Block signals to prevent triggering changes while updating UI
        self.font_combo.blockSignals(True)
        self.size_combo.blockSignals(True)
        self.action_bold.blockSignals(True)
        self.action_italic.blockSignals(True)
        self.action_underline.blockSignals(True)
        self.action_strike.blockSignals(True)
        self.action_sub.blockSignals(True)
        self.action_super.blockSignals(True)
        self.action_align_left.blockSignals(True)
        self.action_align_center.blockSignals(True)
        self.action_align_right.blockSignals(True)
        self.action_align_justify.blockSignals(True)
        
        self.font_combo.setCurrentFont(fmt.font())
        self.size_combo.setCurrentText(str(int(fmt.fontPointSize())))
        
        self.action_bold.setChecked(fmt.fontWeight() == QFont.Weight.Bold)
        self.action_italic.setChecked(fmt.fontItalic())
        self.action_underline.setChecked(fmt.fontUnderline())
        self.action_strike.setChecked(fmt.fontStrikeOut())
        
        v_align = fmt.verticalAlignment()
        self.action_sub.setChecked(v_align == QTextCharFormat.VerticalAlignment.AlignSubScript)
        self.action_super.setChecked(v_align == QTextCharFormat.VerticalAlignment.AlignSuperScript)
        
        # Alignment
        align = self.editor.alignment()
        if align & Qt.AlignmentFlag.AlignLeft:
            self.action_align_left.setChecked(True)
        elif align & Qt.AlignmentFlag.AlignHCenter:
            self.action_align_center.setChecked(True)
        elif align & Qt.AlignmentFlag.AlignRight:
            self.action_align_right.setChecked(True)
        elif align & Qt.AlignmentFlag.AlignJustify:
            self.action_align_justify.setChecked(True)
        
        self.font_combo.blockSignals(False)
        self.size_combo.blockSignals(False)
        self.action_bold.blockSignals(False)
        self.action_italic.blockSignals(False)
        self.action_underline.blockSignals(False)
        self.action_strike.blockSignals(False)
        self.action_sub.blockSignals(False)
        self.action_super.blockSignals(False)
        self.action_align_left.blockSignals(False)
        self.action_align_center.blockSignals(False)
        self.action_align_right.blockSignals(False)
        self.action_align_justify.blockSignals(False)
        
    # --- Public API ---
    def get_html(self) -> str:
        return self.editor.toHtml()
        
    def set_html(self, html: str):
        self.editor.setHtml(html)
        # Ensure LTR is maintained after setting content
        self.editor.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        
    def get_text(self) -> str:
        return self.editor.toPlainText()
        
    def set_text(self, text: str):
        self.editor.setPlainText(text)
        
    def clear(self):
        self.editor.clear()

    def find_text(self, text: str) -> bool:
        if not text:
            return False
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)
        found = self.editor.find(text)
        if found:
            self.editor.setFocus()
            return True
        return False
