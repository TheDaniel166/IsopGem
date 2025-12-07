"""Mindscape window for multi-map 3D mind mapping (CPU-rendered)."""
from __future__ import annotations

from typing import Optional, Dict, TYPE_CHECKING
import math

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QInputDialog, QMessageBox, QMenu, QFormLayout, QLineEdit, QColorDialog,
    QComboBox, QCheckBox, QDoubleSpinBox, QPushButton, QLabel, QTabWidget
)
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QVector3D, QCursor

from pillars.document_manager.services.mindmap_service import mindmap_service_context
from pillars.document_manager.ui.mindscape_view import MindscapeView, MindNode, MindEdge
from pillars.document_manager.ui.rich_text_editor import RichTextEditor
from pillars.document_manager.utils.mindscape_layout import radial_seed, force_refine

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pillars.document_manager.models.mindmap import MindmapNode, MindmapEdge


class MindscapeWindow(QMainWindow):
    """Mindscape window with map selection, canvas, and basic edit controls."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mindscape")
        self.resize(1200, 800)

        self.current_map_id: Optional[int] = None
        self.node_lookup: Dict[int, "MindmapNode"] = {}
        self.edge_lookup: Dict[int, "MindmapEdge"] = {}

        self._setup_ui()
        self._load_maps()

    # UI -----------------------------------------------------------------
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        self.view = MindscapeView()
        self.view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.view, 3)

        # Sidebar inspector (hidden until selection)
        self.sidebar = QWidget()
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(10, 10, 10, 10)
        self.sidebar_layout.setSpacing(8)

        # Node inspector (tabbed)
        self.node_group = QWidget()
        node_group_layout = QVBoxLayout(self.node_group)
        node_group_layout.setContentsMargins(0, 0, 0, 0)
        self.node_tabs = QTabWidget()

        # Info tab
        info_tab = QWidget()
        info_form = QFormLayout(info_tab)
        self.name_edit = QLineEdit()
        self.category_edit = QLineEdit()
        self.tags_edit = QLineEdit()
        self.notes_editor = RichTextEditor(placeholder_text="Notes...")
        info_form.addRow("Name", self.name_edit)
        info_form.addRow("Category", self.category_edit)
        info_form.addRow("Tags", self.tags_edit)
        info_form.addRow("Notes", self.notes_editor)
        self.node_tabs.addTab(info_tab, "Info")

        # Appearance tab
        appearance_tab = QWidget()
        appearance_form = QFormLayout(appearance_tab)
        self.color_btn = QPushButton("Pick Color")
        self.stroke_color_btn = QPushButton("Pick Border Color")
        self.stroke_width_spin = QDoubleSpinBox(); self.stroke_width_spin.setRange(0.5, 8.0); self.stroke_width_spin.setValue(1.6)
        self.shape_options = ["circle", "square", "triangle", "diamond", "hexagon"]
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(self.shape_options)
        self.pinned_chk = QCheckBox("Pinned")
        appearance_form.addRow("Color", self.color_btn)
        appearance_form.addRow("Border", self.stroke_color_btn)
        appearance_form.addRow("Border Width", self.stroke_width_spin)
        appearance_form.addRow("Shape", self.shape_combo)
        appearance_form.addRow("Pinned", self.pinned_chk)
        self.node_tabs.addTab(appearance_tab, "Appearance")

        node_group_layout.addWidget(self.node_tabs)

        # Buttons row
        self.btn_save_node = QPushButton("Save Node")
        self.btn_del_node = QPushButton("Delete Node")
        self.btn_add_edge = QPushButton("Add Edge from Node")
        self.node_group_buttons = QHBoxLayout()
        self.node_group_buttons.addWidget(self.btn_save_node)
        self.node_group_buttons.addWidget(self.btn_del_node)
        self.node_group_buttons.addWidget(self.btn_add_edge)
        node_group_layout.addLayout(self.node_group_buttons)

        # Edge inspector
        self.edge_group = QWidget()
        edge_form = QFormLayout(self.edge_group)
        self.edge_label = QLabel("Edge")
        self.edge_color_btn = QPushButton("Edge Color")
        self.edge_style = QComboBox(); self.edge_style.addItems(["solid", "dashed"])
        self.edge_width = QDoubleSpinBox(); self.edge_width.setRange(0.5, 10.0); self.edge_width.setValue(2.0)
        self.edge_src_label = QLabel("")
        self.edge_dst_label = QLabel("")
        edge_form.addRow("From", self.edge_src_label)
        edge_form.addRow("To", self.edge_dst_label)
        edge_form.addRow("Color", self.edge_color_btn)
        edge_form.addRow("Width", self.edge_width)
        edge_form.addRow("Style", self.edge_style)
        self.btn_save_edge = QPushButton("Save Edge")
        self.btn_del_edge = QPushButton("Delete Edge")
        edge_buttons = QHBoxLayout()
        edge_buttons.addWidget(self.btn_save_edge)
        edge_buttons.addWidget(self.btn_del_edge)
        edge_form.addRow(edge_buttons)

        self.sidebar_layout.addWidget(QLabel("Inspector"))
        self.sidebar_layout.addWidget(self.node_group)
        self.sidebar_layout.addWidget(self.edge_group)
        self.sidebar.setFixedWidth(340)
        layout.addWidget(self.sidebar, 1)
        self.sidebar.hide()

        self.view.set_selection_changed_callback(self._on_canvas_select)
        self.view.set_edge_selection_changed_callback(self._on_edge_select)
        self.view.set_positions_changed_callback(self._on_positions_changed)

        self._current_node_color = QColor("#3b82f6")
        self._current_node_stroke_color = QColor("#1e3a8a")
        self._current_node_stroke_width = 1.6
        self._current_edge_color = QColor("#9ca3af")
        self.color_btn.setStyleSheet(f"background:{self._current_node_color.name()};")
        self.stroke_color_btn.setStyleSheet(f"background:{self._current_node_stroke_color.name()};")
        self.edge_color_btn.setStyleSheet(f"background:{self._current_edge_color.name()};")

        # Signals
        self.color_btn.clicked.connect(self._pick_node_color)
        self.stroke_color_btn.clicked.connect(self._pick_node_stroke_color)
        self.stroke_width_spin.valueChanged.connect(self._set_node_stroke_width)
        self.edge_color_btn.clicked.connect(self._pick_edge_color)
        self.btn_save_node.clicked.connect(self._save_node)
        self.btn_del_node.clicked.connect(self._delete_node)
        self.btn_add_edge.clicked.connect(self._add_edge)
        self.btn_save_edge.clicked.connect(self._save_edge)
        self.btn_del_edge.clicked.connect(self._delete_edge)

    # Data loading -------------------------------------------------------
    def _load_maps(self):
        with mindmap_service_context() as svc:
            maps = svc.list_maps()
        if not maps:
            return
        if self.current_map_id is None:
            self.current_map_id = int(getattr(maps[0], "id", 0))
        self._load_map_data()

    def _load_map_data(self):
        if self.current_map_id is None:
            return
        with mindmap_service_context() as svc:
            nodes, edges = svc.get_map_graph(self.current_map_id)
        self.node_lookup = {int(getattr(n, "id", 0)): n for n in nodes}
        self.edge_lookup = {int(getattr(e, "id", 0)): e for e in edges}
        self.view.set_selected_node(None)
        self.view.set_selected_edge(None)
        self._hide_sidebar()
        self._refresh_view()

    def _refresh_view(self):
        nodes_vm = []
        for n in self.node_lookup.values():
            node_id = int(getattr(n, "id", 0) or 0)
            color_raw = str(getattr(n, "color", "#3b82f6") or "#3b82f6")
            fill_hex = color_raw
            stroke_hex = None
            if "|" in color_raw:
                parts = color_raw.split("|", 1)
                fill_hex = parts[0] or "#3b82f6"
                stroke_hex = parts[1] or None
            stroke_qcolor = QColor(stroke_hex) if stroke_hex else QColor(fill_hex).darker(140)
            shape = str(getattr(n, "shape", "circle") or "circle").lower()
            if hasattr(self, "shape_options") and shape not in self.shape_options:
                shape = "circle"
            nodes_vm.append(
                MindNode(
                    node_id=node_id,
                    name=str(getattr(n, "name", "")),
                    pos=QVector3D(float(getattr(n, "x", 0.0) or 0.0), float(getattr(n, "y", 0.0) or 0.0), float(getattr(n, "z", 0.0) or 0.0)),
                    color=QColor(fill_hex),
                    stroke_color=stroke_qcolor,
                    pinned=bool(getattr(n, "pinned", False)),
                    shape=shape,
                )
            )

        edges_vm = []
        for e in self.edge_lookup.values():
            edges_vm.append(
                MindEdge(
                    edge_id=int(getattr(e, "id", 0) or 0),
                    source_id=int(getattr(e, "source_id", 0) or 0),
                    target_id=int(getattr(e, "target_id", 0) or 0),
                    color=QColor(str(getattr(e, "color", "#9ca3af") or "#9ca3af")),
                    width=float(getattr(e, "width", 2.0) or 2.0),
                    style=str(getattr(e, "style", "solid") or "solid"),
                )
            )
        self.view.set_data(nodes_vm, edges_vm)
        self.view.fit_scene()

    # Map actions --------------------------------------------------------
    def _create_map(self):
        name, ok = QInputDialog.getText(self, "New Mindmap", "Name:")
        if not ok or not name.strip():
            return
        with mindmap_service_context() as svc:
            svc.create_map(name.strip())
        self.current_map_id = None
        self._load_maps()

    def _rename_map(self):
        map_id = self.current_map_id
        if map_id is None:
            return
        name, ok = QInputDialog.getText(self, "Rename Mindmap", "New name:")
        if not ok or not name.strip():
            return
        with mindmap_service_context() as svc:
            svc.rename_map(map_id, name.strip())
        self._load_maps()

    def _delete_selected(self):
        map_id = self.current_map_id
        if map_id is None:
            return
        if QMessageBox.question(self, "Delete Mindmap", f"Delete mindmap {map_id}?") != QMessageBox.StandardButton.Yes:
            return
        with mindmap_service_context() as svc:
            svc.delete_map(map_id)
        self.current_map_id = None
        self.node_lookup.clear(); self.edge_lookup.clear()
        self.view.set_data([], [])
        self._load_maps()

    def _switch_map(self, map_id: int):
        if map_id == self.current_map_id:
            return
        self.current_map_id = map_id
        self._load_map_data()

    # Node actions -------------------------------------------------------
    def _pick_node_color(self):
        c = QColorDialog.getColor(self._current_node_color, self, "Choose node color")
        if c.isValid():
            self._current_node_color = c
            self.color_btn.setStyleSheet(f"background:{c.name()};")

    def _pick_node_stroke_color(self):
        c = QColorDialog.getColor(self._current_node_stroke_color, self, "Choose border color")
        if c.isValid():
            self._current_node_stroke_color = c
            self.stroke_color_btn.setStyleSheet(f"background:{c.name()};")

    def _set_node_stroke_width(self, val: float):
        self._current_node_stroke_width = float(val)

    def _find_free_position_near(self, anchor: Optional[QVector3D] = None, min_sep_world: float = 0.16, max_steps: int = 120) -> QVector3D:
        """Place new nodes away from overlap using a golden-angle spiral around an anchor."""
        existing = [(float(getattr(n, "x", 0.0) or 0.0), float(getattr(n, "y", 0.0) or 0.0)) for n in self.node_lookup.values()]

        if anchor is None:
            if existing:
                cx = sum(x for x, _ in existing) / len(existing)
                cy = sum(y for _, y in existing) / len(existing)
                anchor = QVector3D(cx, cy, 0.0)
            else:
                anchor = QVector3D(0.0, 0.0, 0.0)

        golden_angle = math.pi * (3 - math.sqrt(5))
        step = min_sep_world
        for k in range(max_steps):
            r = step * math.sqrt(k)
            theta = k * golden_angle
            x = anchor.x() + r * math.cos(theta)
            y = anchor.y() + r * math.sin(theta)
            if all((x - ex) ** 2 + (y - ey) ** 2 >= (min_sep_world ** 2) for ex, ey in existing):
                return QVector3D(x, y, 0.0)
        return anchor

    def _screen_to_world(self, pt: QPointF) -> Optional[QVector3D]:
        try:
            m, scale, pan = self.view._projection_params()  # type: ignore[attr-defined]
            inv_m = m.inverted()[0]
            offset = pt - pan
            world_rot = QVector3D(offset.x() / scale, -offset.y() / scale, 0)
            return inv_m * world_rot
        except Exception:
            return None

    def _add_node(self):
        if self.current_map_id is None:
            return
        name, ok = QInputDialog.getText(self, "Add Node", "Name:")
        if not ok:
            return
        pos = None
        # Try to place near cursor if over the view
        cursor_pos = self.view.mapFromGlobal(QCursor.pos())
        if self.view.rect().contains(cursor_pos):
            world = self._screen_to_world(QPointF(cursor_pos))
            if world is not None:
                pos = self._find_free_position_near(anchor=world)
        if pos is None:
            pos = self._find_free_position_near()
        with mindmap_service_context() as svc:
            node = svc.add_node(
                self.current_map_id,
                name=name or "Node",
                category="",
                tags="",
                notes=self.notes_editor.editor.toHtml() or "",
                color=f"{self._current_node_color.name()}|{self._current_node_stroke_color.name()}|{self._current_node_stroke_width:.2f}",
                shape=self.shape_combo.currentText() or "circle",
                pinned=False,
                x=float(pos.x()),
                y=float(pos.y()),
                z=float(pos.z()),
            )
        self.node_lookup[int(getattr(node, "id", 0))] = node
        self._refresh_view()
        self.view.set_selected_node(int(getattr(node, "id", 0)))
        self._on_canvas_select(int(getattr(node, "id", 0)))

    def _save_node(self):
        if self.current_map_id is None or self.view is None:
            return
        nid = self.view.get_selected_node()
        if nid is None or nid not in self.node_lookup:
            return
        n = self.node_lookup[nid]
        name = self.name_edit.text() or "Node"
        category = self.category_edit.text() or ""
        tags = self.tags_edit.text() or ""
        notes = self.notes_editor.editor.toHtml() or ""
        shape = self.shape_combo.currentText() or "circle"
        pinned = self.pinned_chk.isChecked()
        fill_hex = self._current_node_color.name()
        stroke_hex = self._current_node_stroke_color.name()
        stroke_w = self._current_node_stroke_width
        color_payload = f"{fill_hex}|{stroke_hex}|{stroke_w:.2f}"
        with mindmap_service_context() as svc:
            node = svc.update_node(
                nid,
                name=name,
                category=category,
                tags=tags,
                notes=notes,
                color=color_payload,
                shape=shape,
                pinned=pinned,
            )
        if node:
            self.node_lookup[int(nid)] = node
            self._refresh_view()

    def _delete_node(self):
        nid = self.view.get_selected_node()
        if nid is None:
            QMessageBox.information(self, "Delete Node", "No node selected to delete.")
            return
        with mindmap_service_context() as svc:
            ok = svc.delete_node(int(nid))
        if not ok:
            QMessageBox.warning(self, "Delete Node", "Could not delete node (not found).")
            return
        self.node_lookup.pop(int(nid), None)
        # remove edges referencing the deleted node locally
        self.edge_lookup = {
            int(eid): e
            for eid, e in self.edge_lookup.items()
            if int(getattr(e, "source_id", -1)) != int(nid) and int(getattr(e, "target_id", -1)) != int(nid)
        }
        self.view.set_selected_node(None)
        self.view.set_selected_edge(None)
        # Reload from DB to ensure local cache matches persisted state
        self._load_map_data()
        self._hide_sidebar()

    def _toggle_pin(self):
        nid = self.view.get_selected_node()
        if nid is None or nid not in self.node_lookup:
            return
        node = self.node_lookup[nid]
        new_val = not bool(getattr(node, "pinned", False))
        with mindmap_service_context() as svc:
            updated = svc.update_node(nid, pinned=new_val)
        if updated:
            self.node_lookup[nid] = updated
            self.pinned_chk.setChecked(new_val)
        self._refresh_view()

    # Edge actions -------------------------------------------------------
    def _pick_edge_color(self):
        c = QColorDialog.getColor(self._current_edge_color, self, "Choose edge color")
        if c.isValid():
            self._current_edge_color = c
            self.edge_color_btn.setStyleSheet(f"background:{c.name()};")

    def _add_edge(self):
        if self.current_map_id is None:
            return
        src = self.view.get_selected_node()
        if src is None:
            return
        options = []
        for nid, n in self.node_lookup.items():
            if nid == src:
                continue
            label = f"{getattr(n, 'name', '') or 'Node'} (id:{nid})"
            options.append((label, nid))
        if not options:
            return
        labels = [lbl for lbl, _ in options]
        target_label, ok = QInputDialog.getItem(self, "Add Edge", "Connect to:", labels, editable=False)
        if not ok:
            return
        lookup = {lbl: nid for lbl, nid in options}
        dst = int(lookup.get(str(target_label), -1))
        if dst < 0:
            return
        with mindmap_service_context() as svc:
            edge = svc.add_edge(
                self.current_map_id,
                source_id=src,
                target_id=dst,
                color=self._current_edge_color.name(),
                width=2.0,
                style="solid",
            )
        self.edge_lookup[int(getattr(edge, "id", 0))] = edge
        self._refresh_view()
        self.view.set_selected_edge(int(getattr(edge, "id", 0)))
        self._on_edge_select(int(getattr(edge, "id", 0)))

    def _save_edge(self):
        eid = self.view.get_selected_edge()
        if eid is None or eid not in self.edge_lookup:
            return
        with mindmap_service_context() as svc:
            updated = svc.update_edge(
                eid,
                color=self._current_edge_color.name(),
                width=self.edge_width.value(),
                style=self.edge_style.currentText() or "solid",
            )
        if updated:
            self.edge_lookup[int(eid)] = updated
            self._refresh_view()

    def _delete_edge(self):
        eid = self.view.get_selected_edge()
        if eid is None:
            src = self.view.get_selected_node()
            if src is None:
                return
            # Build choice list of all incident edges (both directions)
            options = []
            for edge_id, e in self.edge_lookup.items():
                sid = int(getattr(e, "source_id", -1))
                tid = int(getattr(e, "target_id", -1))
                if sid != src and tid != src:
                    continue
                sname = getattr(self.node_lookup.get(sid), "name", str(sid)) if self.node_lookup else str(sid)
                tname = getattr(self.node_lookup.get(tid), "name", str(tid)) if self.node_lookup else str(tid)
                label = f"{sname} -> {tname} (id:{edge_id})"
                options.append((label, edge_id))
            if not options:
                return
            labels = [lbl for lbl, _ in options]
            chosen, ok = QInputDialog.getItem(self, "Delete Edge", "Choose edge:", labels, editable=False)
            if not ok:
                return
            lookup = {lbl: edge_id for lbl, edge_id in options}
            eid = int(lookup.get(str(chosen), -1))
            if eid < 0:
                return
        with mindmap_service_context() as svc:
            svc.delete_edge(eid)
        self.edge_lookup.pop(int(eid), None)
        self.view.set_selected_edge(None)
        self._refresh_view()
        if self.view.get_selected_node() is None:
            self._hide_sidebar()

    # Layout -------------------------------------------------------------
    def _auto_layout(self):
        if not self.node_lookup:
            return
        seed = radial_seed([(int(getattr(n, "id", 0)), str(getattr(n, "category", "") or "")) for n in self.node_lookup.values()])
        for nid, pos in seed.items():
            n = self.node_lookup.get(nid)
            if n is not None and not bool(getattr(n, "pinned", False)):
                n.x, n.y, n.z = pos.x(), pos.y(), pos.z()  # type: ignore[assignment]
        self._relax(iterations=80)
        self._bulk_save_positions()
        self._refresh_view()

    def _relax(self, iterations: int = 120):
        if not self.node_lookup:
            return
        positions = {int(getattr(n, "id", 0)): QVector3D(float(getattr(n, "x", 0.0) or 0.0), float(getattr(n, "y", 0.0) or 0.0), float(getattr(n, "z", 0.0) or 0.0)) for n in self.node_lookup.values()}
        pinned = {int(getattr(n, "id", 0)): bool(getattr(n, "pinned", False)) for n in self.node_lookup.values()}
        edges = [(int(getattr(e, "source_id", 0)), int(getattr(e, "target_id", 0))) for e in self.edge_lookup.values()]
        force_refine(positions, edges, pinned, iterations=iterations)
        for nid, vec in positions.items():
            n = self.node_lookup.get(nid)
            if n is not None and not bool(getattr(n, "pinned", False)):
                n.x, n.y, n.z = vec.x(), vec.y(), vec.z()  # type: ignore[assignment]
        self._bulk_save_positions()
        self._refresh_view()

    def _bulk_save_positions(self):
        if self.current_map_id is None:
            return
        moves = [(int(getattr(n, "id", 0)), float(getattr(n, "x", 0.0) or 0.0), float(getattr(n, "y", 0.0) or 0.0), float(getattr(n, "z", 0.0) or 0.0)) for n in self.node_lookup.values()]
        with mindmap_service_context() as svc:
            svc.update_node_positions(self.current_map_id, moves)

    def _on_positions_changed(self, moves):
        # moves: list of tuples node_id, x, y, z
        if self.current_map_id is None:
            return
        filtered = []
        for nid, x, y, z in moves:
            n = self.node_lookup.get(int(nid))
            if n is None or bool(getattr(n, "pinned", False)):
                continue
            n.x, n.y, n.z = float(x), float(y), float(z)  # type: ignore[assignment]
            filtered.append((int(nid), float(x), float(y), float(z)))
        if not filtered:
            return
        with mindmap_service_context() as svc:
            svc.update_node_positions(self.current_map_id, filtered)

    def _on_canvas_select(self, node_id: Optional[int]):
        if node_id is None:
            self._hide_sidebar()
            self.view.set_selected_node(None)
            return
        n = self.node_lookup.get(node_id)
        if not n:
            self._hide_sidebar()
            return
        color_raw = str(getattr(n, "color", "#3b82f6") or "#3b82f6")
        fill_hex = color_raw
        stroke_hex = None
        stroke_w = None
        if "|" in color_raw:
            parts = color_raw.split("|", 2)
            fill_hex = parts[0] or "#3b82f6"
            stroke_hex = parts[1] or None if len(parts) > 1 else None
            if len(parts) > 2:
                try:
                    stroke_w = float(parts[2])
                except ValueError:
                    stroke_w = None
        self._current_node_color = QColor(fill_hex)
        self._current_node_stroke_color = QColor(stroke_hex) if stroke_hex else QColor(fill_hex).darker(140)
        self._current_node_stroke_width = float(stroke_w) if stroke_w is not None else 1.6
        self.color_btn.setStyleSheet(f"background:{self._current_node_color.name()};")
        self.stroke_color_btn.setStyleSheet(f"background:{self._current_node_stroke_color.name()};")
        self.stroke_width_spin.setValue(self._current_node_stroke_width)
        self.name_edit.setText(str(getattr(n, "name", "") or ""))
        self.category_edit.setText(str(getattr(n, "category", "") or ""))
        self.tags_edit.setText(str(getattr(n, "tags", "") or ""))
        self.notes_editor.editor.setHtml(str(getattr(n, "notes", "") or ""))
        shape_val = str(getattr(n, "shape", "circle") or "circle").lower()
        if shape_val not in self.shape_options:
            shape_val = "circle"
        self.shape_combo.setCurrentText(shape_val)
        self.pinned_chk.setChecked(bool(getattr(n, "pinned", False)))
        self._show_node_sidebar()

    def _on_edge_select(self, edge_id: Optional[int]):
        if edge_id is None:
            if self.view.get_selected_node() is None:
                self._hide_sidebar()
            return
        e = self.edge_lookup.get(edge_id) if edge_id is not None else None
        if not e:
            if self.view.get_selected_node() is None:
                self._hide_sidebar()
            return
        self.view.set_selected_edge(edge_id)
        self._current_edge_color = QColor(str(getattr(e, "color", "#9ca3af") or "#9ca3af"))
        self.edge_color_btn.setStyleSheet(f"background:{self._current_edge_color.name()};")
        self.edge_src_label.setText(str(getattr(e, "source_id", "")))
        self.edge_dst_label.setText(str(getattr(e, "target_id", "")))
        self.edge_width.setValue(float(getattr(e, "width", 2.0) or 2.0))
        self.edge_style.setCurrentText(str(getattr(e, "style", "solid") or "solid"))
        self._show_edge_sidebar()

    def _show_node_sidebar(self):
        self.sidebar.show()
        self.node_group.show()
        self.edge_group.hide()

    def _show_edge_sidebar(self):
        self.sidebar.show()
        self.node_group.hide()
        self.edge_group.show()

    def _hide_sidebar(self):
        self.sidebar.hide()

    # Context menu ------------------------------------------------------
    def _show_context_menu(self, point):
        menu = QMenu(self)

        # Map actions
        map_menu = QMenu("Maps", self)
        map_menu.addAction("New Map", self._create_map)
        if self.current_map_id is not None:
            map_menu.addAction("Rename Current", self._rename_map)
            map_menu.addAction("Delete Current", self._delete_selected)
        switch_menu = QMenu("Switch", self)
        map_menu.addMenu(switch_menu)
        with mindmap_service_context() as svc:
            maps = svc.list_maps()
        for m in maps:
            mid = int(getattr(m, "id", 0))
            action = switch_menu.addAction(f"{mid}: {getattr(m, 'name', '')}")
            if action:
                action.triggered.connect(lambda checked=False, map_id=mid: self._switch_map(map_id))
        menu.addMenu(map_menu)

        # Layout actions
        menu.addSeparator()
        menu.addAction("Auto Layout", self._auto_layout)
        menu.addAction("Relax Layout", self._relax)
        menu.addAction("Reset Camera", self.view.reset_camera)

        # Node actions
        menu.addSeparator()
        menu.addAction("Add Node", self._add_node)
        if self.view.get_selected_node() is not None:
            menu.addAction("Edit Node", self._save_node)
            menu.addAction("Delete Node", self._delete_node)
            menu.addAction("Pin/Unpin Node", self._toggle_pin)
            menu.addAction("Add Edge from Selected", self._add_edge)
            menu.addAction("Delete Edge from Selected", self._delete_edge)

        menu.exec(self.view.mapToGlobal(point))

