"""Cymatics simulator window for visual standing-wave patterns.

Enhanced version with Visual Liturgy alignment:
- Multiple plate shapes (rectangular, circular, hexagonal)
- Hz frequency input mode
- Color gradient visualization
- 3D surface view toggle
- Particle simulation
- Image/GIF export
- Preset save/load
"""
from __future__ import annotations

from typing import Optional

import numpy as np
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QImage, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


from shared.ui import WindowManager
from shared.ui.theme import COLORS

from ..models import (
    ColorGradient,
    CymaticsPreset,
    ParticleState,
    PlateShape,
    SimulationParams,
    SimulationResult,
)
from ..services import (
    BUILTIN_PRESETS,
    CymaticsAudioService,
    CymaticsExportService,
    CymaticsGradientService,
    CymaticsParticleService,
    CymaticsPresetService,
    CymaticsSessionStore,
    CymaticsSimulationService,
)
from .cymatics_3d_view import Cymatics3DView
from .cymatics_particle_view import CymaticsParticleView


class CymaticsSimulatorWindow(QMainWindow):
    """Visual simulator for cymatics patterns with advanced features."""

    # Mapping from combo box index to enum
    PLATE_SHAPES = [
        (PlateShape.RECTANGULAR, "Rectangular"),
        (PlateShape.CIRCULAR, "Circular (Chladni)"),
        (PlateShape.HEXAGONAL, "Hexagonal"),
        (PlateShape.HEPTAGONAL, "Heptagonal"),
    ]

    COLOR_GRADIENTS = [
        (ColorGradient.GRAYSCALE, "Grayscale"),
        (ColorGradient.HEAT_MAP, "Heat Map"),
        (ColorGradient.OCEAN, "Ocean"),
        (ColorGradient.PLASMA, "Plasma"),
        (ColorGradient.VIRIDIS, "Viridis"),
    ]

    def __init__(self, window_manager: Optional[WindowManager] = None, parent=None):
        super().__init__(parent)
        self.window_manager = window_manager
        self.setWindowTitle("Cymatics Simulator")
        self.setMinimumSize(1200, 800)

        # Services
        self._simulator = CymaticsSimulationService()
        self._gradient_service = CymaticsGradientService()
        self._particle_service = CymaticsParticleService()
        self._preset_service = CymaticsPresetService()
        self._export_service = CymaticsExportService()
        self._audio_service = CymaticsAudioService()

        # Animation timer
        self._timer = QTimer(self)
        self._timer.setInterval(45)
        self._timer.timeout.connect(self._advance_animation)

        # State
        self._phase = 0.0
        self._last_qimage: Optional[QImage] = None
        self._last_result: Optional[SimulationResult] = None
        self._particle_state: Optional[ParticleState] = None
        self._last_shape = PlateShape.RECTANGULAR  # Track shape changes for particle reset

        self._build_ui()
        self._render()

    def _build_ui(self) -> None:
        """Build the main UI following the Three-Pane Trinity pattern."""
        central = QWidget()
        central.setStyleSheet(f"background-color: {COLORS['marble']};")
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # The Trinity: Parameters | Viewport | Controls
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        self.splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {COLORS['ash']};
            }}
        """)

        # Left Pane: Input Parameters
        self.input_pane = self._build_input_pane()
        
        # Center Pane: Viewport
        self.viewport_pane = self._build_visualization_panel()
        
        # Right Pane: Controls & Actions
        self.controls_pane = self._build_controls_pane()

        self.splitter.addWidget(self.input_pane)
        self.splitter.addWidget(self.viewport_pane)
        self.splitter.addWidget(self.controls_pane)

        # Initial Sizes - 25% | 50% | 25%
        self.splitter.setSizes([350, 700, 350])
        self.splitter.setCollapsible(0, True)
        self.splitter.setCollapsible(2, True)

        main_layout.addWidget(self.splitter)

    def _build_input_pane(self) -> QWidget:
        """Build the left input parameters pane with Visual Liturgy styling."""
        # Outer container
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['marble']};
                border: 1px solid {COLORS['ash']};
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border-right: none;
            }}
        """)

        # Scroll area inside
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: {COLORS['marble']};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['ash']};
                border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {COLORS['mist']};
            }}
        """)

        # Content widget
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header = QLabel("Input Parameters")
        header.setStyleSheet(f"""
            color: {COLORS['void']};
            font-size: 16pt;
            font-weight: 700;
        """)
        layout.addWidget(header)

        desc = QLabel("Configure wave modes, frequency, and plate geometry")
        desc.setStyleSheet(f"color: {COLORS['stone']}; font-size: 9pt;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Sections - INPUT PARAMETERS ONLY
        layout.addWidget(self._build_frequency_section())
        layout.addWidget(self._build_modes_section())
        layout.addWidget(self._build_shape_section())

        layout.addStretch()

        scroll.setWidget(content)

        # Layout for container
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(scroll)

        return container

    def _build_section_frame(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        """Create a styled section frame with title."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['light']};
                border: 1px solid {COLORS['ash']};
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: {COLORS['void']};
            font-size: 11pt;
            font-weight: 600;
        """)
        layout.addWidget(title_label)

        return frame, layout

    def _build_frequency_section(self) -> QFrame:
        """Build frequency input section."""
        frame, layout = self._build_section_frame("Frequency Input")

        # Toggle
        self._use_freq_mode = QCheckBox("Use Frequency (Hz) instead of modes")
        self._use_freq_mode.setStyleSheet(f"color: {COLORS['stone']};")
        self._use_freq_mode.toggled.connect(self._toggle_freq_mode)
        layout.addWidget(self._use_freq_mode)

        # Frequency row
        freq_row = QHBoxLayout()
        freq_row.setSpacing(12)

        self._freq_slider = QSlider(Qt.Orientation.Horizontal)
        self._freq_slider.setRange(20, 2000)
        self._freq_slider.setValue(440)
        self._freq_slider.setEnabled(False)
        self._freq_slider.valueChanged.connect(self._on_freq_changed)
        self._freq_slider.setStyleSheet(self._get_slider_style())

        self._freq_label = QLabel("440 Hz")
        self._freq_label.setStyleSheet(f"""
            color: {COLORS['void']};
            font-weight: 600;
            min-width: 70px;
        """)

        freq_row.addWidget(self._freq_slider, 1)
        freq_row.addWidget(self._freq_label)
        layout.addLayout(freq_row)

        return frame

    def _build_modes_section(self) -> QFrame:
        """Build wave modes section."""
        frame, layout = self._build_section_frame("Wave Modes")

        # Create controls
        self._mode_m = self._styled_spin_box(1, 12, 2)
        self._mode_n = self._styled_spin_box(1, 12, 3)
        self._secondary_m = self._styled_spin_box(1, 12, 3)
        self._secondary_n = self._styled_spin_box(1, 12, 4)
        self._mix = self._styled_double_box(0.0, 1.0, 0.35, 0.05)
        self._damping = self._styled_double_box(0.0, 6.0, 0.0, 0.1)
        self._grid_size = self._styled_spin_box(80, 420, 220, step=20)

        # Grid layout for modes
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        grid.addWidget(self._field_label("Mode M"), 0, 0)
        grid.addWidget(self._mode_m, 0, 1)
        grid.addWidget(self._field_label("Mode N"), 0, 2)
        grid.addWidget(self._mode_n, 0, 3)

        grid.addWidget(self._field_label("Sec. M"), 1, 0)
        grid.addWidget(self._secondary_m, 1, 1)
        grid.addWidget(self._field_label("Sec. N"), 1, 2)
        grid.addWidget(self._secondary_n, 1, 3)

        grid.addWidget(self._field_label("Mix"), 2, 0)
        grid.addWidget(self._mix, 2, 1)
        grid.addWidget(self._field_label("Damping"), 2, 2)
        grid.addWidget(self._damping, 2, 3)

        grid.addWidget(self._field_label("Grid Size"), 3, 0)
        grid.addWidget(self._grid_size, 3, 1)

        layout.addLayout(grid)
        return frame

    def _build_shape_section(self) -> QFrame:
        """Build plate shape section."""
        frame, layout = self._build_section_frame("Plate Geometry")

        # Shape selector
        shape_label = QLabel("Shape:")
        shape_label.setStyleSheet(f"color: {COLORS['stone']}; font-size: 10pt;")
        layout.addWidget(shape_label)

        self._shape_combo = QComboBox()
        for shape, name in self.PLATE_SHAPES:
            self._shape_combo.addItem(name, shape)
        self._shape_combo.setStyleSheet(self._get_combo_style())
        self._shape_combo.currentIndexChanged.connect(self._render)
        layout.addWidget(self._shape_combo)

        # Material selector
        material_label = QLabel("Material:")
        material_label.setStyleSheet(f"color: {COLORS['stone']}; font-size: 10pt; margin-top: 8px;")
        layout.addWidget(material_label)

        self._material_combo = QComboBox()
        # Import PlateMaterial here
        from ..models import PlateMaterial
        for material in PlateMaterial:
            # Add material with tooltip showing properties
            self._material_combo.addItem(material.display_name, material)
            tooltip = (
                f"Y = {material.youngs_modulus_gpa:.1f} GPa | "
                f"ρ = {material.density_kg_m3:.0f} kg/m³\n"
                f"v = {material.wave_speed_m_s:.0f} m/s | "
                f"Resonance: {material.resonance_quality:.0%}"
            )
            self._material_combo.setItemData(
                self._material_combo.count() - 1,
                tooltip,
                Qt.ItemDataRole.ToolTipRole
            )
        self._material_combo.setStyleSheet(self._get_combo_style())
        self._material_combo.currentIndexChanged.connect(self._render)
        self._material_combo.setToolTip("Physical material affects wave speed and resonance")
        layout.addWidget(self._material_combo)

        return frame

    def _build_visualization_section(self) -> QFrame:
        """Build visualization options section."""
        frame, layout = self._build_section_frame("Visualization")

        # Color gradient
        row = QHBoxLayout()
        row.setSpacing(12)
        row.addWidget(self._field_label("Colors"))

        self._gradient_combo = QComboBox()
        for gradient, name in self.COLOR_GRADIENTS:
            self._gradient_combo.addItem(name, gradient)
        self._gradient_combo.setCurrentIndex(3)  # Plasma default
        self._gradient_combo.setStyleSheet(self._get_combo_style())
        self._gradient_combo.currentIndexChanged.connect(self._render)
        row.addWidget(self._gradient_combo, 1)

        layout.addLayout(row)

        # 3D toggle
        self._show_3d = QCheckBox("Show 3D Surface")
        self._show_3d.setStyleSheet(f"color: {COLORS['stone']};")
        self._show_3d.toggled.connect(self._toggle_3d_view)
        layout.addWidget(self._show_3d)

        return frame

    def _build_particles_section(self) -> QFrame:
        """Build particle simulation section."""
        frame, layout = self._build_section_frame("Particle Simulation")

        self._enable_particles = QCheckBox("Enable Particles")
        self._enable_particles.setStyleSheet(f"color: {COLORS['stone']};")
        self._enable_particles.toggled.connect(self._toggle_particles)
        layout.addWidget(self._enable_particles)

        # Count row
        row = QHBoxLayout()
        row.setSpacing(12)
        row.addWidget(self._field_label("Count"))
        self._particle_count = self._styled_spin_box(100, 5000, 2000, step=100)
        row.addWidget(self._particle_count, 1)
        layout.addLayout(row)

        self._reset_particles_btn = QPushButton("Reset Particles")
        self._reset_particles_btn.setStyleSheet(self._get_ghost_button_style())
        self._reset_particles_btn.clicked.connect(self._reset_particles)
        self._reset_particles_btn.setEnabled(False)
        layout.addWidget(self._reset_particles_btn)

        return frame

    def _build_actions_section(self) -> QFrame:
        """Build main action buttons."""
        frame, layout = self._build_section_frame("Actions")

        row = QHBoxLayout()
        row.setSpacing(12)

        self._generate_btn = QPushButton("Generate")
        self._generate_btn.setStyleSheet(self._get_primary_button_style())
        self._generate_btn.clicked.connect(self._render)
        row.addWidget(self._generate_btn)

        self._animate_btn = QPushButton("Animate")
        self._animate_btn.setCheckable(True)
        self._animate_btn.setStyleSheet(self._get_secondary_button_style())
        self._animate_btn.toggled.connect(self._toggle_animation)
        row.addWidget(self._animate_btn)

        layout.addLayout(row)

        # Play Sound button (toggleable for continuous audio)
        self._play_sound_btn = QPushButton("🔊 Play Sound")
        self._play_sound_btn.setCheckable(True)
        self._play_sound_btn.setStyleSheet(self._get_secondary_button_style())
        self._play_sound_btn.toggled.connect(self._toggle_audio)
        layout.addWidget(self._play_sound_btn)

        return frame

    def _build_export_section(self) -> QFrame:
        """Build export and preset section."""
        frame, layout = self._build_section_frame("Export & Presets")

        # Export row
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self._export_image_btn = QPushButton("Save Image")
        self._export_image_btn.setStyleSheet(self._get_ghost_button_style())
        self._export_image_btn.clicked.connect(self._export_image)
        row1.addWidget(self._export_image_btn)

        self._export_gif_btn = QPushButton("Export GIF")
        self._export_gif_btn.setStyleSheet(self._get_ghost_button_style())
        self._export_gif_btn.clicked.connect(self._export_gif)
        row1.addWidget(self._export_gif_btn)

        layout.addLayout(row1)

        # Preset row
        row2 = QHBoxLayout()
        row2.setSpacing(12)

        self._save_preset_btn = QPushButton("Save Preset")
        self._save_preset_btn.setStyleSheet(self._get_ghost_button_style())
        self._save_preset_btn.clicked.connect(self._save_preset)
        row2.addWidget(self._save_preset_btn)

        self._load_preset_btn = QPushButton("Load Preset")
        self._load_preset_btn.setStyleSheet(self._get_ghost_button_style())
        self._load_preset_btn.clicked.connect(self._load_preset)
        row2.addWidget(self._load_preset_btn)

        layout.addLayout(row2)
        return frame

    def _build_visualization_panel(self) -> QWidget:
        """Build the center visualization panel."""
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['void']};
                border: none;
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Stacked widget for 2D/3D views
        self._view_stack = QStackedWidget()

        # 2D view container
        self._2d_container = QWidget()
        self._2d_container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(self._2d_container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_label.setStyleSheet("background: transparent;")
        container_layout.addWidget(self._image_label, 1)

        # Particle overlay
        self._particle_view = CymaticsParticleView(self._image_label)
        self._particle_view.hide()

        self._view_stack.addWidget(self._2d_container)

        # 3D view
        self._3d_view = Cymatics3DView()
        self._view_stack.addWidget(self._3d_view)

        layout.addWidget(self._view_stack, 1)

        # Status bar
        self._status_label = QLabel("Ready.")
        self._status_label.setStyleSheet(f"""
            color: {COLORS['mist']};
            font-size: 10pt;
            padding: 8px;
            background-color: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
        """)
        layout.addWidget(self._status_label)

        return panel

    def _build_controls_pane(self) -> QWidget:
        """Build the right controls & actions pane."""
        # Outer container
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['marble']};
                border: 1px solid {COLORS['ash']};
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                border-left: none;
            }}
        """)

        # Scroll area inside
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: {COLORS['marble']};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['ash']};
                border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {COLORS['mist']};
            }}
        """)

        # Content widget
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header = QLabel("Controls & Output")
        header.setStyleSheet(f"""
            color: {COLORS['void']};
            font-size: 16pt;
            font-weight: 700;
        """)
        layout.addWidget(header)

        desc = QLabel("Visualization, rendering, and export tools")
        desc.setStyleSheet(f"color: {COLORS['stone']}; font-size: 9pt;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Sections - CONTROLS & ACTIONS
        layout.addWidget(self._build_visualization_section())
        layout.addWidget(self._build_particles_section())
        layout.addWidget(self._build_actions_section())

        layout.addStretch()

        layout.addWidget(self._build_export_section())

        scroll.setWidget(content)

        # Layout for container
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(scroll)

        return container

    # ─────────────────────────────────────────────────────────────────
    # Styling helpers
    # ─────────────────────────────────────────────────────────────────

    def _field_label(self, text: str) -> QLabel:
        """Create a styled field label."""
        label = QLabel(text)
        label.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 10pt;
        """)
        return label

    def _styled_spin_box(
        self, minimum: int, maximum: int, value: int, step: int = 1
    ) -> QSpinBox:
        """Create a styled spin box."""
        widget = QSpinBox()
        widget.setRange(minimum, maximum)
        widget.setSingleStep(step)
        widget.setValue(value)
        widget.setStyleSheet(self._get_input_style())
        return widget

    def _styled_double_box(
        self, minimum: float, maximum: float, value: float, step: float
    ) -> QDoubleSpinBox:
        """Create a styled double spin box."""
        widget = QDoubleSpinBox()
        widget.setDecimals(2)
        widget.setRange(minimum, maximum)
        widget.setSingleStep(step)
        widget.setValue(value)
        widget.setStyleSheet(self._get_input_style())
        return widget

    def _get_input_style(self) -> str:
        """Get input field style."""
        return f"""
            QSpinBox, QDoubleSpinBox {{
                background-color: {COLORS['light']};
                border: 1px solid {COLORS['ash']};
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 10pt;
                color: {COLORS['void']};
                min-height: 32px;
            }}
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 2px solid {COLORS['focus']};
            }}
        """

    def _get_combo_style(self) -> str:
        """Get combo box style."""
        return f"""
            QComboBox {{
                background-color: {COLORS['light']};
                border: 1px solid {COLORS['ash']};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 10pt;
                color: {COLORS['void']};
                min-height: 36px;
            }}
            QComboBox:focus {{
                border: 2px solid {COLORS['focus']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['light']};
                border: 1px solid {COLORS['ash']};
                border-radius: 8px;
                selection-background-color: {COLORS['primary_light']};
            }}
        """

    def _get_slider_style(self) -> str:
        """Get slider style."""
        return f"""
            QSlider::groove:horizontal {{
                background: {COLORS['ash']};
                height: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {COLORS['magus']};
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {COLORS['magus_hover']};
            }}
        """

    def _get_primary_button_style(self) -> str:
        """Get primary button style (Magus archetype)."""
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['magus']}, stop:1 {COLORS['magus_dark']});
                color: {COLORS['light']};
                border: 1px solid {COLORS['magus_border']};
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 11pt;
                font-weight: 600;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['magus_hover']}, stop:1 {COLORS['magus']});
            }}
            QPushButton:pressed {{
                background: {COLORS['magus_dark']};
            }}
        """

    def _get_secondary_button_style(self) -> str:
        """Get secondary button style (Navigator archetype)."""
        return f"""
            QPushButton {{
                background-color: {COLORS['marble']};
                color: {COLORS['stone']};
                border: 1px solid {COLORS['ash']};
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 11pt;
                font-weight: 500;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_hover']};
                border-color: {COLORS['stone']};
            }}
            QPushButton:checked {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['scribe']}, stop:1 {COLORS['scribe_dark']});
                color: {COLORS['light']};
                border-color: {COLORS['scribe_border']};
            }}
        """

    def _get_ghost_button_style(self) -> str:
        """Get ghost button style."""
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['stone']};
                border: 1px solid {COLORS['ash']};
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 10pt;
                min-height: 36px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_hover']};
                border-color: {COLORS['stone']};
            }}
            QPushButton:disabled {{
                color: {COLORS['mist']};
                border-color: {COLORS['ash']};
            }}
        """

    # ─────────────────────────────────────────────────────────────────
    # Event handlers
    # ─────────────────────────────────────────────────────────────────

    def _toggle_freq_mode(self, enabled: bool) -> None:
        """Toggle between frequency and manual mode selection."""
        self._freq_slider.setEnabled(enabled)
        self._mode_m.setEnabled(not enabled)
        self._mode_n.setEnabled(not enabled)
        self._secondary_m.setEnabled(not enabled)
        self._secondary_n.setEnabled(not enabled)
        self._render()

    def _on_freq_changed(self, value: int) -> None:
        """Update frequency label and preview derived modes."""
        self._freq_label.setText(f"{value} Hz")
        if self._use_freq_mode.isChecked():
            params = self._get_current_params()
            m, n = self._simulator.hz_to_modes(value, params)
            self._status_label.setText(f"Frequency {value} Hz → modes ({m}, {n})")
            self._render()

    def _toggle_3d_view(self, enabled: bool) -> None:
        """Switch between 2D and 3D visualization."""
        if enabled:
            self._view_stack.setCurrentIndex(1)
            self._particle_view.hide()
        else:
            self._view_stack.setCurrentIndex(0)
            if self._enable_particles.isChecked():
                self._particle_view.show()
        self._render()

    def _toggle_particles(self, enabled: bool) -> None:
        """Enable/disable particle simulation."""
        self._reset_particles_btn.setEnabled(enabled)
        if enabled:
            self._reset_particles()
            if not self._show_3d.isChecked():
                self._particle_view.show()
        else:
            self._particle_view.hide()
            self._particle_state = None

    def _reset_particles(self) -> None:
        """Reset particle positions."""
        count = self._particle_count.value()
        grid_size = self._grid_size.value()
        # Pass boundary mask from last result if available
        mask = self._last_result.boundary_mask if self._last_result else None
        self._particle_state = self._particle_service.initialize_particles(
            count, grid_size, distribution="uniform", boundary_mask=mask
        )
        self._particle_view.set_particles(self._particle_state)

    def _toggle_animation(self, enabled: bool) -> None:
        """Start/stop animation."""
        if enabled:
            self._timer.start()
            self._animate_btn.setText("Pause")
        else:
            self._timer.stop()
            self._animate_btn.setText("Animate")

    def _advance_animation(self) -> None:
        """Advance animation by one frame."""
        self._phase += 0.15
        self._render()

    def _toggle_audio(self, enabled: bool) -> None:
        """Toggle continuous audio synthesis on/off."""
        if not self._audio_service.is_available():
            self._play_sound_btn.setChecked(False)
            self._status_label.setText("⚠️ Audio not available (install sounddevice: pip install sounddevice)")
            return

        if enabled:
            # Start continuous audio
            params = self._get_current_params()
            if self._audio_service.start_continuous(params):
                self._play_sound_btn.setText("🔊 Audio ON")
                self._status_label.setText("🔊 Continuous audio active")
            else:
                self._play_sound_btn.setChecked(False)
                self._status_label.setText("❌ Failed to start audio")
        else:
            # Stop continuous audio
            self._audio_service.stop_continuous()
            self._play_sound_btn.setText("🔊 Play Sound")
            self._status_label.setText("Audio stopped")

    # ─────────────────────────────────────────────────────────────────
    # Rendering
    # ─────────────────────────────────────────────────────────────────

    def _get_current_params(self) -> SimulationParams:
        """Build SimulationParams from current UI state."""
        return SimulationParams(
            grid_size=self._grid_size.value(),
            mode_m=self._mode_m.value(),
            mode_n=self._mode_n.value(),
            secondary_m=self._secondary_m.value(),
            secondary_n=self._secondary_n.value(),
            mix=self._mix.value(),
            damping=self._damping.value(),
            frequency_hz=self._freq_slider.value(),
            use_frequency_mode=self._use_freq_mode.isChecked(),
            plate_shape=self._shape_combo.currentData(),
            plate_material=self._material_combo.currentData(),
            color_gradient=self._gradient_combo.currentData(),
            show_3d_surface=self._show_3d.isChecked(),
            enable_particles=self._enable_particles.isChecked(),
            particle_count=self._particle_count.value(),
            # particle_speed uses default 0.5 from SimulationParams
        )

    def _render(self) -> None:
        """Render the current simulation."""
        params = self._get_current_params()
        
        # Auto-reset particles if shape changed (ensures they conform to new boundary)
        if params.plate_shape != self._last_shape and self._enable_particles.isChecked():
            self._reset_particles()
        self._last_shape = params.plate_shape
        
        result = self._simulator.simulate(params, phase=self._phase)
        self._last_result = result
        CymaticsSessionStore.set_last_simulation(result)

        # Update 2D view
        gradient = self._gradient_combo.currentData()
        self._last_qimage = self._gradient_service.to_qimage(
            result.normalized, gradient
        )
        self._refresh_scaled_image()

        # Update 3D view if visible
        if self._show_3d.isChecked():
            self._3d_view.set_result(result)
            self._3d_view.set_gradient(gradient)

        # Update particles
        if self._enable_particles.isChecked() and self._particle_state is not None:
            self._particle_state = self._particle_service.update_particles(
                self._particle_state,
                result.field,
                dt=0.045,
                speed=params.particle_speed,
                boundary_mask=result.boundary_mask,
            )
            self._particle_view.set_particles(self._particle_state)

        # Update status
        if params.use_frequency_mode:
            m, n = self._simulator.hz_to_modes(params.frequency_hz, params)
            status = f"{params.plate_shape.name} | {params.frequency_hz:.0f} Hz → ({m},{n})"
        else:
            status = f"{params.plate_shape.name} | modes ({params.mode_m},{params.mode_n})"
        self._status_label.setText(status)

        # Update continuous audio if active
        if self._audio_service.is_playing():
            self._audio_service.update_continuous(params)

    def _refresh_scaled_image(self) -> None:
        """Scale and display the current image."""
        if self._last_qimage is None:
            return

        pixmap = QPixmap.fromImage(self._last_qimage)
        target_size = self._image_label.size()
        if target_size.width() < 10 or target_size.height() < 10:
            return

        scaled = pixmap.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._image_label.setPixmap(scaled)

        # Fix: Set particle overlay to cover the full label from (0,0) relative to the label
        # Using geometry() gives parent-relative coords (includes margins), but we need local coords
        from PyQt6.QtCore import QRect
        self._particle_view.setGeometry(QRect(0, 0, self._image_label.width(), self._image_label.height()))

    # ─────────────────────────────────────────────────────────────────
    # Export and Presets
    # ─────────────────────────────────────────────────────────────────

    def _export_image(self) -> None:
        """Export current pattern as image."""
        if self._last_result is None:
            QMessageBox.warning(self, "Export", "No pattern to export.")
            return

        gradient = self._gradient_combo.currentData()
        path = self._export_service.export_image(self, self._last_result, gradient)
        if path:
            QMessageBox.information(self, "Export", f"Image saved to:\n{path}")

    def _export_gif(self) -> None:
        """Export animation as GIF."""
        params = self._get_current_params()
        gradient = self._gradient_combo.currentData()

        def render_frame(phase: float) -> np.ndarray:
            result = self._simulator.simulate(params, phase=phase)
            return result.normalized

        try:
            path = self._export_service.export_gif(
                self,
                render_frame,
                gradient,
                frame_count=60,
                fps=30,
            )
            if path:
                QMessageBox.information(self, "Export", f"GIF saved to:\n{path}")
        except RuntimeError as e:
            QMessageBox.warning(self, "Export Error", str(e))

    def _save_preset(self) -> None:
        """Save current parameters as preset."""
        name, ok = QInputDialog.getText(self, "Save Preset", "Preset name:")
        if not ok or not name.strip():
            return

        desc, _ = QInputDialog.getText(
            self, "Save Preset", "Description (optional):"
        )

        preset = CymaticsPreset(
            name=name.strip(),
            params=self._get_current_params(),
            description=desc,
        )

        self._preset_service.save_preset(preset)
        QMessageBox.information(self, "Preset Saved", f"Preset '{name}' saved.")

    def _load_preset(self) -> None:
        """Load a saved preset."""
        user_presets = self._preset_service.list_presets()
        builtin_names = [p.name for p in BUILTIN_PRESETS]

        all_presets = user_presets + ["─── Built-in ───"] + builtin_names

        if not user_presets and not builtin_names:
            QMessageBox.information(self, "Load Preset", "No presets available.")
            return

        name, ok = QInputDialog.getItem(
            self,
            "Load Preset",
            "Select preset:",
            all_presets,
            0,
            False,
        )
        if not ok or not name or name.startswith("───"):
            return

        preset = self._preset_service.load_preset(name)

        if preset is None:
            for bp in BUILTIN_PRESETS:
                if bp.name == name:
                    preset = bp
                    break

        if preset is None:
            QMessageBox.warning(self, "Load Preset", f"Preset '{name}' not found.")
            return

        self._apply_preset(preset)

    def _apply_preset(self, preset: CymaticsPreset) -> None:
        """Apply a preset to the UI."""
        p = preset.params

        self._grid_size.setValue(p.grid_size)
        self._mode_m.setValue(p.mode_m)
        self._mode_n.setValue(p.mode_n)
        self._secondary_m.setValue(p.secondary_m)
        self._secondary_n.setValue(p.secondary_n)
        self._mix.setValue(p.mix)
        self._damping.setValue(p.damping)
        self._freq_slider.setValue(int(p.frequency_hz))
        self._use_freq_mode.setChecked(p.use_frequency_mode)

        for i, (shape, _) in enumerate(self.PLATE_SHAPES):
            if shape == p.plate_shape:
                self._shape_combo.setCurrentIndex(i)
                break

        for i, (gradient, _) in enumerate(self.COLOR_GRADIENTS):
            if gradient == p.color_gradient:
                self._gradient_combo.setCurrentIndex(i)
                break

        self._render()
        self._status_label.setText(f"Loaded preset: {preset.name}")

    # ─────────────────────────────────────────────────────────────────
    # Qt event overrides
    # ─────────────────────────────────────────────────────────────────

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._refresh_scaled_image()

    def closeEvent(self, event) -> None:
        self._timer.stop()
        super().closeEvent(event)
