"""
Geometry Calculator Window - The Orchestrator.
Main window combining input, viewport, and controls panes for shape calculations.
"""
import logging
from typing import Optional
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter, QApplication
from PyQt6.QtCore import Qt, QTimer, QSignalBlocker
from PyQt6.QtCore import Qt, QTimer

from ...services.base_shape import GeometricShape
from ..liturgy_styles import LiturgyColors
from .view_model import GeometryViewModel
from .panes.input_pane import InputPane
from .panes.viewport_pane import ViewportPane
from .panes.controls_pane import ControlsPane
from shared.ui import WindowManager
from ....tq.ui.quadset_analysis_window import QuadsetAnalysisWindow


logger = logging.getLogger(__name__)



class GeometryCalculatorWindow(QMainWindow):
    """
    The Orchestrator: Combines View Model and Panes into the Liturgy-compliant window.
    """
    
    def __init__(self, shape: GeometricShape, window_manager: Optional[WindowManager] = None, parent=None):
        """
          init   logic.
        
        Args:
            shape: Description of shape.
            window_manager: Description of window_manager.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.window_manager = window_manager

        self.shape = shape
        self.view_model = GeometryViewModel(shape)
        
        self.setWindowTitle(f"{shape.name} Calculator")
        self.resize(1400, 900) # Divine Proportion-ish
        
        self._setup_ui()
        self._connect_panes()

    def _setup_ui(self):
        # Main Widget
        central_widget = QWidget()
        # Marble background for the whole table
        central_widget.setStyleSheet(f"background-color: {LiturgyColors.MARBLE};")
        self.setCentralWidget(central_widget)
        
        # Main Layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Splitter (The Trinity: Input | Viewport | Controls)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        self.splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {LiturgyColors.ASH};
            }}
        """)
        
        # Panes
        self.input_pane = InputPane(self.view_model)
        self.viewport_pane = ViewportPane(self.view_model)
        self.controls_pane = ControlsPane(self.view_model)
        
        self.splitter.addWidget(self.input_pane)
        self.splitter.addWidget(self.viewport_pane)
        self.splitter.addWidget(self.controls_pane)
        
        # Initial Sizes (Approx 25% | 50% | 25%)
        self.splitter.setSizes([350, 700, 350])
        self.splitter.setCollapsible(0, True)
        self.splitter.setCollapsible(2, True)
        
        main_layout.addWidget(self.splitter)

    def _connect_panes(self):
        """Wire up cross-pane interactions."""
        # Controls Pane -> Viewport
        self.controls_pane.show_labels.toggled.connect(self.viewport_pane.scene.set_labels_visible)
        self.controls_pane.show_axes.toggled.connect(self.viewport_pane.scene.set_axes_visible)
        
        # Toggle Panes (Internal)
        self.controls_pane.hide_btn.clicked.connect(self._toggle_controls_internal)
        
        # Toggle Panes (Viewport Toolbar)
        self.viewport_pane.toggle_input_requested.connect(self._set_input_visible)
        self.viewport_pane.toggle_controls_requested.connect(self._set_controls_visible)

        
        # Interactive Measure
        self.controls_pane.interactive_measure_toggled.connect(
            self.viewport_pane.view.set_measurement_mode
        )
        self.viewport_pane.scene.measurementChanged.connect(
            self.controls_pane.update_measurement_labels
        )
        
        # Output Tools
        self.controls_pane.snapshot_requested.connect(self._handle_snapshot_request)
        self.controls_pane.copy_measurements_requested.connect(self._handle_copy_measurements)
        
        # Theme Selector
        self.controls_pane.theme_changed.connect(self.viewport_pane.scene.apply_theme)
        
        # Measurement Colors
        self.controls_pane.measurement_line_color_changed.connect(
            self.viewport_pane.scene.set_measurement_line_color
        )
        self.controls_pane.measurement_text_color_changed.connect(
            self.viewport_pane.scene.set_measurement_text_color
        )
        
        # Cross-Pillar Integration
        self.input_pane.quadset_analysis_requested.connect(self._handle_quadset_request)


        
    def _handle_snapshot_request(self):
        """Capture viewport and copy to clipboard."""
        # Grab pixmap from the viewport
        pixmap = self.viewport_pane.view.grab()
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(pixmap)
        
        # User-facing feedback without console noise
        self.statusBar().showMessage("Snapshot copied to clipboard", 2000)
        logger.debug("GeometryCalculator: snapshot copied to clipboard")
        
    def _handle_copy_measurements(self):
        """Copy current shape properties to clipboard."""
        props = self.view_model.get_properties()
        lines = [f"{self.shape.name} Properties:"]
        for p in props:
            if p.value is not None:
                lines.append(f"{p.name}: {p.value:.4f} {p.unit}")
        
        text = "\n".join(lines)
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.statusBar().showMessage("Measurements copied to clipboard", 2000)
        logger.debug("GeometryCalculator: measurements copied to clipboard")
        
    def _set_input_visible(self, visible: bool):
        """Toggle input pane visibility."""
        self.input_pane.setVisible(visible)
        # Sync toggle state (block signals to prevent loop if we had bidirectional)
        with QSignalBlocker(self.viewport_pane.btn_input):
            self.viewport_pane.btn_input.setChecked(visible)

    def _set_controls_visible(self, visible: bool):
        """Toggle controls pane visibility."""
        self.controls_pane.setVisible(visible)
        # Sync toggle state
        with QSignalBlocker(self.viewport_pane.btn_controls):
            self.viewport_pane.btn_controls.setChecked(visible)
        
    def _toggle_controls_internal(self):
        """Toggle from internal pane button."""
        new_state = not self.controls_pane.isVisible()
        self._set_controls_visible(new_state)

    def _handle_quadset_request(self, value: float):
        """Open Quadset Analysis window with the value."""
        if not self.window_manager:
            self.statusBar().showMessage("Integration unavailable (WindowManager missing)", 4000)
            logger.warning("GeometryCalculator: WindowManager missing; cannot open quadset analysis")
            return

        logger.info("GeometryCalculator: opening quadset analysis for value=%s", value)
        self.statusBar().showMessage(f"Opening Quadset Analysis for value: {int(value)}", 2000)
        
        # Open the window
        # We use a unique ID per value? Or shared?
        # User implies specialized tool. Let's make it a unique instance for "Analysis" or reuse shared.
        # Reuse 'quadset_analysis' logic? 
        # TQ Hub uses: self.window_manager.open_window("quadset_analysis" ...)
        
        win = self.window_manager.open_window(
            window_type="quadset_analysis",
            window_class=QuadsetAnalysisWindow,
            allow_multiple=False, # Single analysis window? Or allow comparison? Let's check user pref. 
            # Usually analysis takes focus. Let's keep one for now.
            window_manager=self.window_manager 
        )
        
        if win:
            win.raise_()
            win.activateWindow()
            # Set the value
            win.input_field.setText(str(int(value)))  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            # If the window has logic to auto-calc on text change, it will trigger.
            # QuadsetAnalysisWindow has textChanged connected to _on_input_changed.

