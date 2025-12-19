"""Geometry pillar hub - launcher interface for geometry tools."""
from __future__ import annotations

from typing import Callable, List, Optional, Dict, Any, cast

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSpinBox, QScrollArea, QLayout, QInputDialog,
    QGridLayout, QGraphicsDropShadowEffect, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from shared.ui import WindowManager
from .advanced_scientific_calculator_window import AdvancedScientificCalculatorWindow
from .geometry_calculator_window import GeometryCalculatorWindow
from .polygonal_number_window import PolygonalNumberWindow
from .experimental_star_window import ExperimentalStarWindow
from .figurate_3d_window import Figurate3DWindow
from .geometry_definitions import CATEGORY_DEFINITIONS, SOLID_VIEWER_CONFIG
from .geometry3d.window3d import Geometry3DWindow
from ..services.polygon_shape import RegularPolygonShape


class GeometryHub(QWidget):
    """Hub widget for Geometry pillar - displays available tools."""
    
    def __init__(self, window_manager: WindowManager):
        """
        Initialize the Geometry hub.
        
        Args:
            window_manager: Shared window manager instance
        """
        super().__init__()
        self.window_manager = window_manager
        self.categories = CATEGORY_DEFINITIONS
        self.category_buttons: List[QPushButton] = []
        self.selected_category_index = 0
        self.content_layout: Optional[QVBoxLayout] = None
        self.menu_layout: Optional[QVBoxLayout] = None
        self._setup_ui()
        self._render_category(0)
    
    def _setup_ui(self):
        """Set up the hub interface."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        container = QWidget()
        root_layout = QVBoxLayout(container)
        root_layout.setSpacing(24)
        root_layout.setContentsMargins(40, 32, 40, 40)

        # Header section matching other hubs
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setSpacing(8)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("Geometry")
        title_label.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 32pt;
                font-weight: 700;
                letter-spacing: -1px;
            }
        """)
        header_layout.addWidget(title_label)

        desc_label = QLabel("Sacred shapes, from perfect circles to multidimensional solids")
        desc_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 12pt;
            }
        """)
        header_layout.addWidget(desc_label)
        
        root_layout.addWidget(header)

        # Quick tools grid
        quick_tools = self._build_quick_tools()
        root_layout.addLayout(quick_tools)

        body_layout = QHBoxLayout()
        body_layout.setSpacing(18)
        root_layout.addLayout(body_layout)

        nav_frame = self._build_category_nav()
        body_layout.addWidget(nav_frame, 0)

        content_frame = self._build_content_area()
        body_layout.addWidget(content_frame, 1)

        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _build_quick_tools(self) -> QGridLayout:
        """Build quick tool cards matching other hub styles."""
        tools = [
            ("\u2211", "Scientific Calc", "Advanced calculator", "#3b82f6", self._open_advanced_scientific_calculator),
            ("\u25b2", "Polygonal", "Polygonal numbers", "#f59e0b", self._open_polygonal_number_visualizer),
            ("\u2606", "Star Numbers", "Experimental stars", "#8b5cf6", self._open_experimental_star_visualizer),
            ("\u2b22", "3D Figurate", "3D figurate numbers", "#06b6d4", self._open_figurate_3d_visualizer),
        ]

        grid = QGridLayout()
        grid.setSpacing(16)
        
        for i, (icon, title, desc, color, callback) in enumerate(tools):
            card = self._create_quick_card(icon, title, desc, color, callback)
            grid.addWidget(card, 0, i)
        
        return grid
    
    def _create_quick_card(self, icon: str, title: str, description: str, accent_color: str, callback) -> QFrame:
        """Create a quick tool card."""
        card = QFrame()
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f1f5f9);
                border-color: {accent_color};
            }}
        """)
        card.setMinimumSize(160, 100)
        card.setMaximumHeight(120)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 25))
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(6)
        
        icon_container = QLabel(icon)
        icon_container.setFixedSize(36, 36)
        icon_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_container.setStyleSheet(f"""
            QLabel {{
                background: {accent_color}20;
                border-radius: 8px;
                font-size: 16pt;
            }}
        """)
        card_layout.addWidget(icon_container)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 11pt;
                font-weight: 600;
                background: transparent;
            }
        """)
        card_layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 8pt;
                background: transparent;
            }
        """)
        card_layout.addWidget(desc_label)
        
        card_layout.addStretch()
        
        card.mousePressEvent = lambda e: callback()
        
        return card

    def _build_category_nav(self) -> QWidget:
        frame = QFrame()
        frame.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
            """
        )
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 25))
        frame.setGraphicsEffect(shadow)

        layout = QHBoxLayout(frame)
        layout.setSpacing(12)
        layout.setContentsMargins(18, 18, 18, 18)

        categories_panel = QFrame()
        categories_panel.setFixedWidth(200)
        categories_panel.setStyleSheet("background: transparent;")
        categories_layout = QVBoxLayout(categories_panel)
        categories_layout.setSpacing(10)
        categories_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("Categories")
        label.setStyleSheet("color: #1e293b; font-weight: 700; font-size: 12pt; background: transparent;")
        categories_layout.addWidget(label)

        for idx, category in enumerate(self.categories):
            button = QPushButton(f"{category['icon']}  {category['name']}")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setCheckable(True)
            button.clicked.connect(lambda _, i=idx: self._render_category(i))
            button.setStyleSheet(self._category_button_style(False))
            categories_layout.addWidget(button)
            self.category_buttons.append(button)

        categories_layout.addStretch()

        menu_panel = QFrame()
        menu_panel.setMinimumWidth(220)
        menu_panel.setStyleSheet("background-color: #f1f5f9; border-radius: 10px;")
        menu_panel_layout = QVBoxLayout(menu_panel)
        menu_panel_layout.setSpacing(8)
        menu_panel_layout.setContentsMargins(14, 14, 14, 14)

        menu_label = QLabel("Shapes")
        menu_label.setStyleSheet("color: #475569; font-weight: 600; font-size: 10pt; background: transparent;")
        menu_panel_layout.addWidget(menu_label)

        menu_scroll = QScrollArea()
        menu_scroll.setWidgetResizable(True)
        menu_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        menu_widget = QWidget()
        self.menu_layout = QVBoxLayout(menu_widget)
        self.menu_layout.setContentsMargins(0, 0, 0, 0)
        self.menu_layout.setSpacing(8)
        menu_scroll.setWidget(menu_widget)
        menu_panel_layout.addWidget(menu_scroll)

        layout.addWidget(categories_panel)
        layout.addWidget(menu_panel, 1)
        return frame

    def _build_content_area(self) -> QWidget:
        frame = QFrame()
        frame.setStyleSheet("background-color: transparent;")
        
        # Direct layout, no inner scroll
        self.content_layout = QVBoxLayout(frame)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(16)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        return frame

    def _category_button_style(self, active: bool) -> str:
        if active:
            return (
                "QPushButton {background-color: #1d4ed8; color: white; border: none;"
                "padding: 10px 14px; border-radius: 10px; font-weight: 600;}"
            )
        return (
            "QPushButton {background-color: #f1f5f9; color: #0f172a; border: none;"
            "padding: 10px 14px; border-radius: 10px; text-align: left; font-weight: 600;}"
            "QPushButton:hover {background-color: #e2e8f0;}"
        )

    def _render_category(self, index: int):
        if not (0 <= index < len(self.categories)):
            return
        self.selected_category_index = index
        for i, button in enumerate(self.category_buttons):
            button.setChecked(i == index)
            button.setStyleSheet(self._category_button_style(i == index))
        self._populate_category_content(self.categories[index])
        self._populate_menu(self.categories[index])

    def _populate_category_content(self, category: dict):
        if self.content_layout is None:
            return
        self._clear_layout(self.content_layout)

        header = QFrame()
        header.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        title = QLabel(f"{category['icon']}  {category['name']}")
        title.setStyleSheet("color: #1e293b; font-size: 18pt; font-weight: 700; background: transparent;")
        header_layout.addWidget(title)

        tagline = QLabel(category['tagline'])
        tagline.setStyleSheet("color: #64748b; font-size: 10pt; background: transparent;")
        header_layout.addWidget(tagline)
        header_layout.addStretch()

        self.content_layout.addWidget(header)

        for shape_def in category['shapes']:
            card = self._create_shape_card(shape_def)
            self.content_layout.addWidget(card)

        # The Geometric Codex (Footer)
        codex = self._build_geometric_codex()
        self.content_layout.addWidget(codex)
        
        self.content_layout.addStretch()

    def _populate_menu(self, category: dict):
        if not hasattr(self, 'menu_layout') or self.menu_layout is None:
            return
        self._clear_layout(self.menu_layout)

        menu_tree = category.get('menu')
        if menu_tree:
            shape_lookup = {shape['name']: shape for shape in category['shapes']}
            self._add_menu_entries(menu_tree, shape_lookup, indent=0)
        else:
            for shape_def in category['shapes']:
                entry = self._create_menu_entry(shape_def)
                self.menu_layout.addWidget(entry)

        self.menu_layout.addStretch()

    def _add_menu_entries(self, entries: List[Any], shape_lookup: Dict[str, dict], indent: int):
        layout = self.menu_layout
        if layout is None:
            return
        for item in entries:
            if isinstance(item, str):
                shape_def = shape_lookup.get(item)
                if shape_def:
                    entry = self._create_menu_entry(shape_def, indent)
                    layout.addWidget(entry)
                continue

            if isinstance(item, dict):
                if 'shape' in item:
                    shape_def = shape_lookup.get(item['shape'])
                    if shape_def:
                        entry = self._create_menu_entry(shape_def, indent + item.get('indent_adjust', 0))
                        layout.addWidget(entry)
                    continue

                label = item.get('label')
                child_items = item.get('items')
                if label:
                    label_container = QWidget()
                    label_layout = QHBoxLayout(label_container)
                    label_layout.setContentsMargins(indent, 6, 0, 2)
                    label_layout.setSpacing(0)
                    label_widget = QLabel(label)
                    label_widget.setStyleSheet("color: #64748b; font-weight: 600; font-size: 9pt;")
                    label_layout.addWidget(label_widget)
                    layout.addWidget(label_container)
                if child_items:
                    self._add_menu_entries(child_items, shape_lookup, indent + 16)

    def _create_menu_entry(self, shape_definition: dict, indent: int = 0) -> QWidget:
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(indent, 0, 0, 0)
        container_layout.setSpacing(0)

        button = QPushButton(shape_definition['name'])
        # Tooltips removed per user request
        # summary = shape_definition.get('summary')
        # if summary and isinstance(summary, str) and summary.strip():
        #     button.setToolTip(summary)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(
            "QPushButton {background-color: #f8fafc; border: 1px solid #e2e8f0;"
            "border-radius: 10px; padding: 8px 12px; text-align: left; color: #0f172a;}"
            "QPushButton:hover {background-color: #eef2ff; border-color: #c7d2fe;}"
        )
        container_layout.addWidget(button)

        factory: Optional[Callable] = shape_definition.get('factory')
        shape_type = shape_definition.get('type')
        status = shape_definition.get('status')
        polygon_sides = shape_definition.get('polygon_sides')

        if status and not factory and not polygon_sides and shape_type not in {'regular_polygon', 'regular_polygon_custom'}:
            button.setEnabled(False)
            button.setCursor(Qt.CursorShape.ArrowCursor)
            button.setStyleSheet(
                "QPushButton {background-color: #f1f5f9; border: 1px dashed #e2e8f0;"
                "border-radius: 10px; padding: 8px 12px; text-align: left; color: #94a3b8;}"
            )
        else:
            if polygon_sides:
                button.clicked.connect(lambda _, n=polygon_sides: self._open_polygon_calculator(n))
            elif shape_type == 'regular_polygon':
                button.clicked.connect(lambda _, default_sides=shape_definition.get('default_sides', 6): self._open_polygon_calculator(default_sides))
            elif shape_type == 'regular_polygon_custom':
                button.clicked.connect(self._prompt_custom_polygon)
            elif shape_type == 'polygonal_numbers':
                button.clicked.connect(self._open_polygonal_number_visualizer)
            elif shape_type == 'star_numbers':
                button.clicked.connect(self._open_star_number_visualizer)
            elif shape_type == 'solid_viewer':
                solid_id = shape_definition.get('solid_id')
                if solid_id in SOLID_VIEWER_CONFIG:
                    button.clicked.connect(lambda _, sid=solid_id: self._open_solid_viewer(sid))
                else:
                    button.setEnabled(False)
                    button.setCursor(Qt.CursorShape.ArrowCursor)
            elif factory:
                button.clicked.connect(lambda _, ctor=factory: self._open_shape_calculator(ctor()))
            else:
                button.setEnabled(False)
                button.setCursor(Qt.CursorShape.ArrowCursor)
                button.setStyleSheet(
                    "QPushButton {background-color: #f1f5f9; border: 1px dashed #e2e8f0;"
                    "border-radius: 10px; padding: 8px 12px; text-align: left; color: #94a3b8;}"
                )

        return container

    def _create_shape_card(self, shape_definition: dict) -> QWidget:
        frame = QFrame()
        frame.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 16px;
            }
            QFrame:hover {
                border-color: #3b82f6;
            }
            """
        )

        layout = QVBoxLayout(frame)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        title_row = QHBoxLayout()
        name_label = QLabel(shape_definition['name'])
        name_label.setStyleSheet("color: #1e293b; font-size: 12pt; font-weight: 600; background: transparent;")
        title_row.addWidget(name_label)

        status = shape_definition.get('status')
        if status:
            badge = QLabel(status)
            badge.setStyleSheet(
                "color: #8b5cf6; background-color: #8b5cf620;"
                "padding: 3px 8px; border-radius: 6px; font-size: 8pt;"
            )
            title_row.addWidget(badge)
        title_row.addStretch()
        layout.addLayout(title_row)

        summary = QLabel(shape_definition.get('summary', ''))
        summary.setWordWrap(True)
        summary.setStyleSheet("color: #64748b; font-size: 9pt; background: transparent;")
        layout.addWidget(summary)

        polygon_sides = shape_definition.get('polygon_sides')
        shape_type = shape_definition.get('type')
        description = shape_definition.get('esoteric_description')
        
        # --- Primary Action Area ---
        action_widget = None

        if shape_type == 'regular_polygon':
            layout.addSpacing(6)
            ctrl_row = QHBoxLayout()
            ctrl_row.setSpacing(10)
            spin_label = QLabel("Sides:")
            spin_label.setStyleSheet("color: #475569; font-weight: 600;")
            ctrl_row.addWidget(spin_label)
            polygon_spin = QSpinBox()
            polygon_spin.setMinimum(3)
            polygon_spin.setMaximum(40)
            polygon_spin.setValue(6)
            polygon_spin.setStyleSheet(
                "QSpinBox {padding: 6px 10px; font-size: 11pt; border: 1px solid #cbd5e1; border-radius: 8px;}"
                "QSpinBox:focus {border-color: #3b82f6;}"
            )
            ctrl_row.addWidget(polygon_spin)
            ctrl_row.addStretch()
            layout.addLayout(ctrl_row)

            action_widget = QPushButton("Open Regular Polygon Calculator")
            action_widget.clicked.connect(lambda _, spin=polygon_spin: self._open_polygon_calculator(spin.value()))

        elif polygon_sides:
            action_widget = QPushButton(f"Open {polygon_sides}-gon Calculator")
            action_widget.clicked.connect(lambda _, n=polygon_sides: self._open_polygon_calculator(n))

        elif shape_type == 'regular_polygon_custom':
            layout.addSpacing(6)
            action_widget = QPushButton("Choose n and Open Calculator")
            action_widget.clicked.connect(self._prompt_custom_polygon)

        elif shape_type == 'polygonal_numbers':
            layout.addSpacing(6)
            action_widget = QPushButton("Open Polygonal Visualizer")
            action_widget.clicked.connect(self._open_polygonal_number_visualizer)

        elif shape_type == 'star_numbers':
            layout.addSpacing(6)
            action_widget = QPushButton("Open Star Visualizer")
            action_widget.clicked.connect(self._open_star_number_visualizer)

        elif shape_type == 'solid_viewer':
            solid_id = shape_definition.get('solid_id')
            action_widget = QPushButton("Open 3D Viewer")
            if solid_id in SOLID_VIEWER_CONFIG:
                action_widget.clicked.connect(lambda _, sid=solid_id: self._open_solid_viewer(sid))
            else:
                action_widget.setEnabled(False)
                action_widget.setCursor(Qt.CursorShape.ArrowCursor)

        else:
            # Default Factory Check
            factory: Optional[Callable] = shape_definition.get('factory')
            if factory:
                action_widget = QPushButton("Open Calculator")
                action_widget.clicked.connect(lambda _, ctor=factory: self._open_shape_calculator(ctor()))
            else:
                hint = QLabel("Stay tuned – this shape is currently in design.")
                hint.setStyleSheet("color: #94a3b8; font-size: 9.5pt; font-style: italic;")
                layout.addWidget(hint)

        if action_widget:
            action_widget.setCursor(Qt.CursorShape.PointingHandCursor)
            action_widget.setStyleSheet(self._primary_button_style())
            layout.addWidget(action_widget)

        # --- Esoteric Wisdom ---
        # description parsed earlier
        if description:
            # layout.addSpacing(4)
            wisdom_btn = QPushButton("Esoteric Wisdom")
            wisdom_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            wisdom_btn.setStyleSheet("""
                QPushButton {
                    background-color: #7c3aed; 
                    color: white; 
                    border: none;
                    padding: 8px 12px; 
                    border-radius: 8px; 
                    font-weight: 600;
                    font-size: 10pt;
                }
                QPushButton:hover { background-color: #6d28d9; }
                QPushButton:pressed { background-color: #5b21b6; }
            """)
            wisdom_btn.clicked.connect(lambda _, t=shape_definition['name'], d=description: self._show_esoteric_meaning(t, d))
            layout.addWidget(wisdom_btn)

        return frame

    def _show_esoteric_meaning(self, title: str, description: Any):
        """Show a dialog with the esoteric meaning of the shape."""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Wisdom of the {title}")
        dialog.setMinimumWidth(550)
        dialog.setMinimumHeight(600)
        dialog.setStyleSheet("background-color: #f8fafc;")
        
        main_layout = QVBoxLayout(dialog)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header (Fixed)
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #ffffff; border-bottom: 1px solid #e2e8f0;")
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(24, 24, 24, 16)
        
        header = QLabel(f"The {title}")
        header.setStyleSheet("color: #1e293b; font-size: 22pt; font-weight: 700; font-family: 'Cinzel', serif; background: transparent;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(header)
        main_layout.addWidget(header_widget)

        # Scrollable Content Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 16, 24, 24)
        
        base_style = """
            color: #334155; 
            font-size: 13pt; 
            line-height: 1.6;
            font-family: 'Crimson Text', serif;
        """

        if isinstance(description, dict):
            # 1. Summary
            summary = description.get('summary', '')
            if summary:
                lbl_summary = QLabel(summary)
                lbl_summary.setWordWrap(True)
                lbl_summary.setStyleSheet(base_style + "font-style: italic; padding-bottom: 12px;")
                layout.addWidget(lbl_summary)

            # 2. Stellations
            stellations = description.get('stellations', {})
            if stellations:
                st_header = QLabel("The Harmonic Stars (Stellations)")
                st_header.setStyleSheet("color: #7c3aed; font-weight: 700; font-size: 11pt; margin-top: 8px;")
                layout.addWidget(st_header)
                for key, val in stellations.items():
                    if isinstance(val, dict):
                        s_name = val.get('name', key)
                        s_desc = val.get('description', '')
                        s_magic = val.get('magical_function', '')
                        row_text = f"<b style='color:#5b21b6;'>{key} — {s_name}</b>"
                        lbl_st = QLabel(row_text)
                        lbl_st.setWordWrap(True)
                        lbl_st.setStyleSheet("font-size: 11pt; margin-left: 12px; margin-top: 6px; color: #334155;")
                        layout.addWidget(lbl_st)
                        if s_desc:
                            lbl_desc = QLabel(s_desc)
                            lbl_desc.setWordWrap(True)
                            lbl_desc.setStyleSheet("font-size: 10pt; margin-left: 20px; color: #475569;")
                            layout.addWidget(lbl_desc)
                        if s_magic:
                            lbl_mag = QLabel(f"<i>Use for: {s_magic}</i>")
                            lbl_mag.setWordWrap(True)
                            lbl_mag.setStyleSheet("font-size: 10pt; margin-left: 20px; color: #6d28d9;")
                            layout.addWidget(lbl_mag)
                    else:
                        row_text = f"<b style='color:#5b21b6;'>{key}</b>: {val}"
                        lbl_st = QLabel(row_text)
                        lbl_st.setWordWrap(True)
                        lbl_st.setStyleSheet("font-size: 11pt; margin-left: 12px; color: #334155;")
                        layout.addWidget(lbl_st)

            # 3. Correspondences
            correspondences = description.get('correspondences', {})
            if correspondences:
                corr_header = QLabel("Correspondences")
                corr_header.setStyleSheet("color: #059669; font-weight: 700; font-size: 11pt; margin-top: 8px;")
                layout.addWidget(corr_header)
                corr_text = " • ".join([f"<b>{k}</b>: {v}" for k, v in correspondences.items()])
                lbl_corr = QLabel(corr_text)
                lbl_corr.setWordWrap(True)
                lbl_corr.setStyleSheet("font-size: 11pt; color: #047857; margin-left: 12px;")
                layout.addWidget(lbl_corr)

            # 4. Attributes
            attributes = description.get('attributes', {})
            if attributes:
                attr_header = QLabel("Geometric Attributes")
                attr_header.setStyleSheet("color: #1e293b; font-weight: 700; font-size: 11pt; margin-top: 8px;")
                layout.addWidget(attr_header)
                for key, val in attributes.items():
                    row_text = f"<b>{key}</b>: {val}"
                    lbl_attr = QLabel(row_text)
                    lbl_attr.setWordWrap(True)
                    lbl_attr.setStyleSheet("font-size: 11pt; margin-left: 12px; color: #475569;")
                    layout.addWidget(lbl_attr)

            # 5. Meditation
            meditation = description.get('meditation', '')
            if meditation:
                med_header = QLabel("Meditation")
                med_header.setStyleSheet("color: #9333ea; font-weight: 700; font-size: 11pt; margin-top: 8px;")
                layout.addWidget(med_header)
                lbl_med = QLabel(meditation)
                lbl_med.setWordWrap(True)
                lbl_med.setStyleSheet("""
                    font-size: 11pt; font-style: italic; color: #581c87; 
                    background-color: #f3e8ff; padding: 12px; border-radius: 8px;
                    border: 1px solid #d8b4fe;
                """)
                layout.addWidget(lbl_med)
        else:
            content = QLabel(str(description))
            content.setWordWrap(True)
            content.setStyleSheet(base_style + "padding: 10px;")
            layout.addWidget(content)
        
        layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Footer (Fixed)
        footer_widget = QWidget()
        footer_widget.setStyleSheet("background-color: #f1f5f9; border-top: 1px solid #e2e8f0;")
        footer_layout = QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(24, 12, 24, 12)
        
        close_btn = QPushButton("Meditate")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(self._primary_button_style())
        close_btn.clicked.connect(dialog.accept)
        footer_layout.addStretch()
        footer_layout.addWidget(close_btn)
        footer_layout.addStretch()
        main_layout.addWidget(footer_widget)
        
        dialog.exec()

    def _primary_button_style(self) -> str:
        return (
            "QPushButton {background-color: #1d4ed8; color: white; border: none;"
            "padding: 10px 16px; border-radius: 10px; font-weight: 600;}"
            "QPushButton:hover {background-color: #2563eb;}"
            "QPushButton:pressed {background-color: #1e3a8a;}"
        )

    def _prompt_custom_polygon(self):
        sides, ok = QInputDialog.getInt(
            self,
            "Regular n-gon",
            "Number of sides (n ≥ 3):",
            value=6,
            min=3,
            max=200,
        )
        if ok:
            self._open_polygon_calculator(sides)

    def _open_solid_viewer(self, solid_id: Optional[str]):
        if not solid_id:
            return
        config = SOLID_VIEWER_CONFIG.get(solid_id)
        if not config:
            return
        builder = config.get('builder')
        calculator_cls = config.get('calculator')
        calculator = calculator_cls() if calculator_cls else None
        payload = None
        if calculator is None and builder:
            result = builder()
            payload = getattr(result, 'payload', result)

        window = cast(
            Geometry3DWindow,
            self.window_manager.open_window(
                window_type=f"geometry_{solid_id}_viewer",
                window_class=Geometry3DWindow,
                allow_multiple=True,
                window_manager=self.window_manager,
            ),
        )
        window.setWindowTitle(f"{config.get('title', solid_id.title())} • 3D Viewer")
        window.set_solid_context(title=config.get('title'), summary=config.get('summary'))
        if calculator is not None:
            window.set_calculator(calculator)
        else:
            window.set_payload(payload)

    @staticmethod
    def _clear_layout(layout: QLayout):
        while layout.count():
            item = layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout is not None:
                    GeometryHub._clear_layout(child_layout)

    
    def _open_shape_calculator(self, shape):
        """Open geometry calculator for a shape."""
        self.window_manager.open_window(
            window_type=f"geometry_{shape.name.lower().replace(' ', '_')}",
            window_class=GeometryCalculatorWindow,
            allow_multiple=True,
            shape=shape,
            window_manager=self.window_manager,
        )

    def _open_advanced_scientific_calculator(self):
        """Open the standalone scientific calculator."""
        self.window_manager.open_window(
            window_type="geometry_advanced_scientific_calculator",
            window_class=AdvancedScientificCalculatorWindow,
            allow_multiple=True,
            window_manager=self.window_manager,
        )

    def _open_polygonal_number_visualizer(self):
        """Open polygonal/centered polygonal number visualizer."""
        window = self.window_manager.open_window(
            window_type="geometry_polygonal_numbers",
            window_class=PolygonalNumberWindow,
            allow_multiple=True,
            window_manager=self.window_manager,
        )
        # Default is polygonal, which is index 0.


    
    def _open_polygon_calculator(self, sides: int):
        """Open geometry calculator for regular polygon."""
        shape = RegularPolygonShape(num_sides=sides)
        self._open_shape_calculator(shape)

    def _open_experimental_star_visualizer(self):
        """Open generalized experimental star visualizer."""
        self.window_manager.open_window(
            window_type="geometry_experimental_star",
            window_class=ExperimentalStarWindow,
            allow_multiple=True,
            window_manager=self.window_manager,
        )

    def _open_figurate_3d_visualizer(self):
        """Open 3D figurate numbers visualizer."""
        self.window_manager.open_window(
            window_type="geometry_figurate_3d",
            window_class=Figurate3DWindow,
            allow_multiple=True,
            window_manager=self.window_manager,
        )

    def _build_geometric_codex(self) -> QWidget:
        container = QFrame()
        container.setStyleSheet(
            """
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
            """
        )
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header = QLabel("The Geometric Codex")
        header.setStyleSheet("color: #1e293b; font-size: 12pt; font-weight: 700; border: none; background: transparent;")
        layout.addWidget(header)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)
        
        constants = [
            ("π", "Archimedes' Constant", "3.141592653"),
            ("φ", "The Golden Ratio", "1.618033988"),
            ("√2", "Pythagoras' Constant", "1.414213562"),
            ("√3", "Theodorus' Constant", "1.732050807"),
            ("e", "Euler's Number", "2.718281828"),
        ]

        for i, (symbol, name, value) in enumerate(constants):
            card = QFrame()
            card.setStyleSheet(
                """
                QFrame {
                    background-color: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                }
                QFrame:hover {
                    border-color: #94a3b8;
                    background-color: #f1f5f9;
                }
                """
            )
            card.setCursor(Qt.CursorShape.PointingHandCursor)
            card.setToolTip(f"{name}: {value}...")
            
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 12, 12, 12)
            card_layout.setSpacing(4)
            
            sym_label = QLabel(symbol)
            sym_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sym_label.setStyleSheet("color: #0f172a; font-size: 18pt; font-weight: 700; border: none; background: transparent;")
            card_layout.addWidget(sym_label)
            
            val_label = QLabel(value)
            val_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            val_label.setStyleSheet("color: #64748b; font-size: 9pt; font-family: monospace; border: none; background: transparent;")
            card_layout.addWidget(val_label)
            
            row = i // 3  # 3 columns
            col = i % 3
            grid_layout.addWidget(card, row, col)

        layout.addLayout(grid_layout)
        
        inspiration = QLabel(
            "\"Geometry will draw the soul toward truth and create the spirit of philosophy.\"\n— Plato"
        )
        inspiration.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inspiration.setStyleSheet("color: #94a3b8; font-style: italic; font-size: 9pt; margin-top: 10px; border: none; background: transparent;")
        layout.addWidget(inspiration)

        return container
