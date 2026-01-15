"""
Property panel builder for the Unified Geometry Viewer.

Handles:
- Property panel UI structure
- Property input widget creation
- Property value updates and synchronization
- Error display
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from shared.ui.theme import COLORS

if TYPE_CHECKING:
    from ....canon import PropertyDefinition

logger = logging.getLogger(__name__)


class PropertyPanel:
    """Builder and manager for the property input panel."""
    
    def __init__(self):
        """Initialize the property panel builder."""
        self._property_inputs: dict[str, QLineEdit] = {}
        self._property_labels: dict[str, QLabel] = {}
        self._property_layout: Optional[QVBoxLayout] = None
        self._property_error_label: Optional[QLabel] = None
        self._updating_inputs = False
    
    def build(
        self,
        title: str,
        on_formula_clicked: Callable[[str, str], None],
        on_property_changed: Callable[[str], None],
        on_derivation_clicked: Callable[[], None],
        on_value_context_menu: Callable[[QLineEdit, object], None],
    ) -> tuple[QFrame, QVBoxLayout, QPushButton, QLabel]:
        """
        Build the properties panel structure.
        
        Args:
            title: Initial title text
            on_formula_clicked: Callback for formula button (property_name, formula_latex)
            on_property_changed: Callback when property value changes (key)
            on_derivation_clicked: Callback for derivation button
            on_value_context_menu: Callback for value context menu (field, pos)
            
        Returns:
            Tuple of (panel frame, property layout, derivation button, title label)
        """
        panel = QFrame()
        panel.setObjectName("PropertiesPanel")
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        panel.setStyleSheet(f"""
            QFrame#PropertiesPanel {{
                background-color: {COLORS['marble']};
                border: 1px solid {COLORS['ash']};
                border-radius: 8px;
            }}
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Title section with derivation button
        title_row = QHBoxLayout()
        title_row.setSpacing(12)
        
        title_label = QLabel(title)
        title_label.setObjectName("FormTitle")
        title_label.setStyleSheet(f"""
            QLabel#FormTitle {{
                color: {COLORS['void']};
                font-size: 18px;
                font-weight: 600;
            }}
        """)
        title_row.addWidget(title_label)
        title_row.addStretch()
        
        # Derivations button
        derivation_btn = QPushButton("📖")
        derivation_btn.setObjectName("DerivationBtn")
        derivation_btn.setToolTip("View mathematical derivations & commentary")
        derivation_btn.setFixedSize(32, 32)
        derivation_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        derivation_btn.setStyleSheet(f"""
            QPushButton#DerivationBtn {{
                background-color: {COLORS['seeker_soft']};
                color: {COLORS['seeker']};
                border: 1px solid {COLORS['seeker_mute']};
                border-radius: 16px;
                font-size: 16px;
                padding: 0;
            }}
            QPushButton#DerivationBtn:hover {{
                background-color: {COLORS['seeker_mute']};
                border-color: {COLORS['seeker']};
            }}
            QPushButton#DerivationBtn:disabled {{
                background-color: {COLORS['marble']};
                color: {COLORS['mist']};
                border-color: {COLORS['ash']};
            }}
        """)
        derivation_btn.clicked.connect(on_derivation_clicked)
        derivation_btn.setEnabled(False)
        title_row.addWidget(derivation_btn)
        
        layout.addLayout(title_row)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"background-color: {COLORS['ash']};")
        divider.setFixedHeight(1)
        layout.addWidget(divider)
        
        # Properties scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        property_layout = QVBoxLayout(scroll_content)
        property_layout.setContentsMargins(0, 0, 8, 0)
        property_layout.setSpacing(8)
        
        # Placeholder
        placeholder = QLabel("No form selected")
        placeholder.setObjectName("PropertyPlaceholder")
        placeholder.setStyleSheet(f"""
            QLabel#PropertyPlaceholder {{
                color: {COLORS['mist']};
                font-style: italic;
                padding: 20px;
            }}
        """)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        property_layout.addWidget(placeholder)
        
        # Error label (hidden by default)
        error_label = QLabel()
        error_label.setObjectName("PropertyError")
        error_label.setStyleSheet(f"""
            QLabel#PropertyError {{
                color: {COLORS['destroyer']};
                background-color: {COLORS['destroyer_soft']};
                padding: 8px;
                border-radius: 4px;
                font-size: 12px;
            }}
        """)
        error_label.setWordWrap(True)
        error_label.hide()
        property_layout.addWidget(error_label)
        
        property_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll, 1)
        
        # Store references
        self._property_layout = property_layout
        self._property_error_label = error_label
        self._on_formula_clicked = on_formula_clicked
        self._on_property_changed = on_property_changed
        self._on_value_context_menu = on_value_context_menu
        
        return panel, property_layout, derivation_btn, title_label
    
    def rebuild_property_inputs(
        self,
        editable_props: list[PropertyDefinition],
        derived_props: list[PropertyDefinition],
    ) -> None:
        """
        Rebuild property input fields based on property definitions.
        
        Args:
            editable_props: List of editable property definitions
            derived_props: List of derived property definitions
        """
        if not self._property_layout:
            return
        
        # Clear existing inputs
        self._property_inputs.clear()
        self._property_labels.clear()
        
        # Remove all widgets
        while self._property_layout.count() > 0:
            item = self._property_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not editable_props and not derived_props:
            # Show placeholder
            placeholder = QLabel("No form selected")
            placeholder.setStyleSheet(f"color: {COLORS['mist']}; font-style: italic;")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._property_layout.addWidget(placeholder)
            self._property_layout.addStretch()
            return
        
        # Create tabbed interface for Core/Advanced
        property_tabs = QTabWidget()
        property_tabs.setObjectName("PropertyTabs")
        property_tabs.setDocumentMode(True)
        property_tabs.setUsesScrollButtons(False)
        property_tabs.setStyleSheet(f"""
            QTabWidget#PropertyTabs::pane {{
                border: 1px solid {COLORS['ash']};
                border-radius: 8px;
                background-color: {COLORS['cloud']};
            }}
            QTabWidget#PropertyTabs > QTabBar {{
                qproperty-expanding: true;
            }}
            QTabWidget#PropertyTabs QTabBar::scroller {{
                width: 0px;
            }}
            QTabWidget#PropertyTabs QTabBar::tab {{
                padding: 8px 16px;
                margin: 2px;
                font-weight: 600;
                font-size: 11px;
                min-width: 60px;
            }}
            QTabWidget#PropertyTabs QTabBar::tab:selected {{
                background-color: {COLORS['seeker_soft']};
                border-radius: 6px;
                color: {COLORS['seeker_dark']};
            }}
            QTabWidget#PropertyTabs QTabBar::tab:!selected {{
                background-color: {COLORS['marble']};
                color: {COLORS['stone']};
            }}
            QTabWidget#PropertyTabs QTabBar::tab:!selected:hover {{
                background-color: {COLORS['surface_hover']};
            }}
        """)
        
        # Core tab (editable properties)
        self._build_core_tab(property_tabs, editable_props)
        
        # Advanced tab (derived properties)
        self._build_advanced_tab(property_tabs, derived_props)
        
        self._property_layout.addWidget(property_tabs, 1)
        
        # Add error label at the end
        self._property_error_label = QLabel()
        self._property_error_label.setObjectName("PropertyError")
        self._property_error_label.setStyleSheet(f"""
            QLabel#PropertyError {{
                color: {COLORS['destroyer']};
                background-color: {COLORS['destroyer_soft']};
                padding: 8px;
                border-radius: 4px;
                font-size: 12px;
            }}
        """)
        self._property_error_label.setWordWrap(True)
        self._property_error_label.hide()
        self._property_layout.addWidget(self._property_error_label)
    
    def _build_core_tab(
        self,
        property_tabs: QTabWidget,
        editable_props: list[PropertyDefinition],
    ) -> None:
        """Build the Core (editable) properties tab."""
        core_scroll = QScrollArea()
        core_scroll.setWidgetResizable(True)
        core_scroll.setFrameShape(QFrame.Shape.NoFrame)
        core_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        core_widget = QWidget()
        core_layout = QVBoxLayout(core_widget)
        core_layout.setContentsMargins(8, 8, 8, 8)
        core_layout.setSpacing(8)
        
        # Color Legend
        legend_frame = QFrame()
        legend_frame.setObjectName("ColorLegend")
        legend_frame.setStyleSheet(f"""
            QFrame#ColorLegend {{
                background-color: {COLORS['marble']};
                border: 1px solid {COLORS['ash']};
                border-radius: 6px;
                padding: 8px;
            }}
        """)
        legend_layout = QHBoxLayout(legend_frame)
        legend_layout.setContentsMargins(8, 6, 8, 6)
        legend_layout.setSpacing(16)
        
        edit_legend = QLabel("✎ Editable")
        edit_legend.setStyleSheet(f"color: {COLORS['seeker']}; font-size: 10px; font-weight: 600;")
        legend_layout.addWidget(edit_legend)
        
        derived_legend = QLabel("◇ Derived")
        derived_legend.setStyleSheet(f"color: {COLORS['mist']}; font-size: 10px; font-weight: 500;")
        legend_layout.addWidget(derived_legend)
        
        legend_layout.addStretch()
        core_layout.addWidget(legend_frame)
        
        for prop in editable_props:
            is_editable = getattr(prop, 'editable', True)
            widget = self._create_property_widget(prop, editable=is_editable)
            core_layout.addWidget(widget)
        
        core_layout.addStretch()
        core_scroll.setWidget(core_widget)
        property_tabs.addTab(core_scroll, f"Core ({len(editable_props)})")
    
    def _build_advanced_tab(
        self,
        property_tabs: QTabWidget,
        derived_props: list[PropertyDefinition],
    ) -> None:
        """Build the Advanced (derived) properties tab."""
        adv_scroll = QScrollArea()
        adv_scroll.setWidgetResizable(True)
        adv_scroll.setFrameShape(QFrame.Shape.NoFrame)
        adv_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        adv_widget = QWidget()
        adv_layout = QVBoxLayout(adv_widget)
        adv_layout.setContentsMargins(8, 8, 8, 8)
        adv_layout.setSpacing(8)
        
        # Info banner
        info_banner = QFrame()
        info_banner.setStyleSheet(f"""
            background-color: {COLORS['navigator_soft']};
            border: 1px solid {COLORS['ash']};
            border-radius: 6px;
        """)
        info_layout = QHBoxLayout(info_banner)
        info_layout.setContentsMargins(10, 8, 10, 8)
        
        info_icon = QLabel("◇")
        info_icon.setStyleSheet(f"color: {COLORS['mist']}; font-size: 14px;")
        info_layout.addWidget(info_icon)
        
        info_text = QLabel("Derived values — computed from the canonical parameter")
        info_text.setStyleSheet(f"color: {COLORS['stone']}; font-size: 10px;")
        info_layout.addWidget(info_text)
        info_layout.addStretch()
        
        adv_layout.addWidget(info_banner)
        
        # Group by category
        categories: dict[str, list] = {}
        for prop in derived_props:
            cat = getattr(prop, 'category', 'Other')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(prop)
        
        for cat_name, cat_props in categories.items():
            # Category header
            cat_frame = QFrame()
            cat_frame.setStyleSheet(f"""
                background-color: {COLORS['navigator_soft']};
                border-radius: 4px;
                margin-top: 8px;
            """)
            cat_header_layout = QHBoxLayout(cat_frame)
            cat_header_layout.setContentsMargins(8, 4, 8, 4)
            
            cat_label = QLabel(cat_name.upper())
            cat_label.setStyleSheet(f"""
                color: {COLORS['navigator_dark']};
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 1px;
            """)
            cat_header_layout.addWidget(cat_label)
            
            cat_count = QLabel(f"({len(cat_props)})")
            cat_count.setStyleSheet(f"color: {COLORS['mist']}; font-size: 10px;")
            cat_header_layout.addWidget(cat_count)
            cat_header_layout.addStretch()
            
            adv_layout.addWidget(cat_frame)
            
            for prop in cat_props:
                is_editable = getattr(prop, 'editable', False)
                widget = self._create_property_widget(prop, editable=is_editable)
                adv_layout.addWidget(widget)
        
        adv_layout.addStretch()
        adv_scroll.setWidget(adv_widget)
        property_tabs.addTab(adv_scroll, f"Advanced ({len(derived_props)})")
    
    def _create_property_widget(
        self,
        prop: PropertyDefinition,
        editable: bool,
    ) -> QFrame:
        """Create a property input widget with label and input field."""
        frame = QFrame()
        frame.setObjectName(f"PropertyFrame_{prop.key}")
        
        # Visual Liturgy: Color-coded left border
        if editable:
            border_color = COLORS['seeker']
            bg_color = COLORS['light']
        else:
            border_color = COLORS['navigator_mute']
            bg_color = COLORS['marble']
        
        frame.setStyleSheet(f"""
            QFrame#PropertyFrame_{prop.key} {{
                background-color: {bg_color};
                border: 1px solid {COLORS['ash']};
                border-left: 3px solid {border_color};
                border-radius: 8px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)
        
        # Header with label, unit, and edit indicator
        header = QHBoxLayout()
        header.setSpacing(6)
        
        # Icon
        if editable:
            edit_icon = QLabel("✎")
            edit_icon.setStyleSheet(f"color: {COLORS['seeker']}; font-size: 12px;")
            edit_icon.setToolTip("Editable — enter a value to recalculate")
            header.addWidget(edit_icon)
        else:
            lock_icon = QLabel("◇")
            lock_icon.setStyleSheet(f"color: {COLORS['mist']}; font-size: 10px;")
            lock_icon.setToolTip("Derived — computed from canonical parameter")
            header.addWidget(lock_icon)
        
        name_label = QLabel(prop.label)
        name_label.setStyleSheet(f"""
            color: {COLORS['void'] if editable else COLORS['stone']};
            font-weight: {'600' if editable else '500'};
            font-size: 12px;
        """)
        header.addWidget(name_label)
        
        if prop.unit:
            unit_label = QLabel(f"({prop.unit})")
            unit_label.setStyleSheet(f"color: {COLORS['mist']}; font-size: 10px;")
            header.addWidget(unit_label)
        
        # Formula button
        formula = getattr(prop, 'formula', '')
        tooltip = getattr(prop, 'tooltip', '')
        
        if formula or tooltip:
            info_btn = QPushButton("ƒ" if formula else "?")
            info_btn.setFixedSize(18, 18)
            info_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            info_btn.setToolTip(tooltip if tooltip else "Show formula")
            
            if formula:
                info_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['magus_soft']};
                        color: {COLORS['magus']};
                        border: 1px solid {COLORS['magus_mute']};
                        border-radius: 9px;
                        font-weight: 700;
                        font-size: 10px;
                        font-family: serif;
                        padding: 0;
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['magus_mute']};
                        border-color: {COLORS['magus']};
                    }}
                """)
                info_btn.clicked.connect(
                    lambda _, label=prop.label, frm=formula: self._on_formula_clicked(label, frm)
                )
            else:
                info_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['navigator_soft']};
                        color: {COLORS['navigator']};
                        border: 1px solid {COLORS['ash']};
                        border-radius: 9px;
                        font-weight: 700;
                        font-size: 10px;
                        padding: 0;
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['surface_hover']};
                    }}
                """)
            header.addWidget(info_btn)
        
        header.addStretch()
        layout.addLayout(header)
        
        # Input field
        input_field = QLineEdit()
        input_field.setObjectName(f"PropertyInput_{prop.key}")
        input_field.setPlaceholderText("0.0")
        
        if editable:
            input_field.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {COLORS['light']};
                    border: 1px solid {COLORS['ash']};
                    border-radius: 8px;
                    padding: 10px 14px;
                    color: {COLORS['void']};
                    font-size: 11pt;
                    font-family: 'JetBrains Mono', 'Consolas', monospace;
                }}
                QLineEdit:focus {{
                    border: 1px solid {COLORS['seeker']};
                }}
                QLineEdit:hover {{
                    border-color: {COLORS['seeker_mute']};
                }}
            """)
        else:
            input_field.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {COLORS['marble']};
                    border: 1px solid {COLORS['ash']};
                    border-radius: 8px;
                    padding: 10px 14px;
                    color: {COLORS['stone']};
                    font-size: 11pt;
                    font-family: 'JetBrains Mono', 'Consolas', monospace;
                }}
            """)
        
        input_field.setValidator(QDoubleValidator())
        input_field.setReadOnly(not editable)
        
        if editable and not getattr(prop, 'readonly', False):
            input_field.editingFinished.connect(
                lambda key=prop.key: self._on_property_changed(key)
            )
        
        # Context menu
        input_field.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        input_field.customContextMenuRequested.connect(
            lambda pos, field=input_field: self._on_value_context_menu(field, pos)
        )
        
        layout.addWidget(input_field)
        
        self._property_inputs[prop.key] = input_field
        self._property_labels[prop.key] = name_label
        
        return frame
    
    def update_all_property_fields(
        self,
        props: dict[str, float],
        prop_formats: dict[str, str],
    ) -> None:
        """Update all property input fields with new values."""
        if not props:
            return
        
        logger.info(f"Updating {len(self._property_inputs)} input fields from {len(props)} props")
        
        self._updating_inputs = True
        try:
            for key, input_field in self._property_inputs.items():
                if key in props:
                    value = props[key]
                    fmt = prop_formats.get(key, '.6f')
                    formatted = format(value, fmt)
                    input_field.setText(formatted)
        finally:
            self._updating_inputs = False
    
    def show_error(self, message: str) -> None:
        """Show an error message in the properties panel."""
        if self._property_error_label:
            self._property_error_label.setText(message)
            self._property_error_label.show()
    
    def clear_error(self) -> None:
        """Clear any property error message."""
        if self._property_error_label:
            self._property_error_label.hide()
    
    def get_property_input(self, key: str) -> Optional[QLineEdit]:
        """Get a property input field by key."""
        return self._property_inputs.get(key)
    
    def get_all_property_inputs(self) -> dict[str, QLineEdit]:
        """Get all property input fields."""
        return self._property_inputs
    
    def is_updating(self) -> bool:
        """Check if inputs are being updated programmatically."""
        return self._updating_inputs
    
    def set_updating(self, value: bool) -> None:
        """Set the updating state."""
        self._updating_inputs = value
