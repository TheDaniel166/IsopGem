from typing import Dict, List, Tuple, Optional, cast, Union

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt, QPointF, pyqtSignal, QTimer, QRectF, QRunnable, QThreadPool, QPoint
from PyQt6.QtGui import QPainter, QBrush, QFont, QMouseEvent, QWheelEvent
from pillars.document_manager.services.mindscape_service import mindscape_service_context, MindNodeDTO, MindEdgeDTO
from .mindscape_items import MindscapeNodeItem, MindscapeEdgeItem
from .mindscape_theme import GraphTheme
from .graph_physics import GraphPhysics
import json
import random

class MindscapeView(QGraphicsView):
    """
    The Plex: A Dynamic, Living Graph View.
    Powered by a Force-Directed Physics Engine.
    """
    node_selected = pyqtSignal(int)
    edge_selected = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        
        # Initialize Theme
        self.theme = GraphTheme("Dark")
        
        # Visual Setup
        self.setBackgroundBrush(QBrush(self.theme.get_color("background")))
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        # Physics Engine (disabled for now)
        self.physics = GraphPhysics()
        self.physics_enabled = False
        
        # Simulation Loop
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._physics_tick)
        self.timer.start(24) # redraw edges even with physics disabled
        self.thread_pool: QThreadPool = QThreadPool.globalInstance() or QThreadPool()
        
        # State
        self._items: Dict[int, MindscapeNodeItem] = {}
        self._edges: List[MindscapeEdgeItem] = []
        self.current_focus_id = None
        self._dragged_node_id = None

    def load_graph(self, focus_id: int, keep_existing: bool = False):
        """
        Loads the local graph and initializes physics.
        keep_existing: If True, adds to current view instead of clearing.
        """
        self.current_focus_id = focus_id
        
        with mindscape_service_context() as svc:
            focus, parents_raw, children_raw, jumps_raw, siblings_raw = svc.get_local_graph(focus_id)

        parents: List[Tuple[MindNodeDTO, MindEdgeDTO]] = cast(List[Tuple[MindNodeDTO, MindEdgeDTO]], parents_raw)
        children: List[Tuple[MindNodeDTO, MindEdgeDTO]] = cast(List[Tuple[MindNodeDTO, MindEdgeDTO]], children_raw)
        jumps: List[Tuple[MindNodeDTO, MindEdgeDTO]] = cast(List[Tuple[MindNodeDTO, MindEdgeDTO]], jumps_raw)
        siblings: List[Tuple[MindNodeDTO, MindEdgeDTO]] = cast(List[Tuple[MindNodeDTO, MindEdgeDTO]], siblings_raw)
            
        if not focus:
            return
            
        # 1. Sync Logic: Identify Keep vs Remove
        # Current active IDs
        parent_ids = {p.id for p, _ in parents}
        child_ids = {c.id for c, _ in children}
        jump_ids = {j.id for j, _ in jumps}
        sibling_ids = {s.id for s, _ in siblings}
        active_ids = {focus.id} | parent_ids | child_ids | jump_ids | sibling_ids
        
        # Remove dead items (Unless keeping)
        if not keep_existing:
            for nid in list(self._items.keys()):
                if nid not in active_ids:
                    # Fade out or just remove for now
                    self._scene.removeItem(self._items[nid])
                    del self._items[nid]
                    self.physics.remove_node(nid)
            
            # Clear edges only if resetting (rebuild is cheap)
            for edge in self._edges:
                self._scene.removeItem(edge)
            self._edges.clear()
            self.physics.edges.clear()
        
        # 2. Add/Update Nodes
        
        # 2. Add/Update Nodes
        all_node_tuples: List[Tuple[MindNodeDTO, Optional[MindEdgeDTO]]] = [(focus, None)]
        all_node_tuples += [(node, edge) for node, edge in parents]
        all_node_tuples += [(node, edge) for node, edge in children]
        all_node_tuples += [(node, edge) for node, edge in jumps]
        all_node_tuples += [(node, edge) for node, edge in siblings]
        
        for n_dto, edge_dto in all_node_tuples:
            if n_dto.id not in self._items:
                # Pass Theme and Content
                item = MindscapeNodeItem(
                    n_dto.id, 
                    n_dto.title, 
                    n_dto.type, 
                    n_dto.icon, 
                    content=n_dto.content, 
                    theme=self.theme
                )
                if n_dto.appearance:
                    try: item.set_style(json.loads(n_dto.appearance))
                    except: pass
                
                item.clicked.connect(self._on_node_clicked)
                self._scene.addItem(item)
                self._items[n_dto.id] = item
                
                # Initial Placement Strategy
                saved_pos = None
                if n_dto.appearance:
                    try:
                        app_data = json.loads(n_dto.appearance)
                        if "pos" in app_data:
                            saved_pos = app_data["pos"]
                    except: pass

                if saved_pos:
                    x, y = saved_pos[0], saved_pos[1]
                elif n_dto.id == focus.id:
                     x, y = 0, 0 # Center
                elif n_dto.id in parent_ids:
                    x, y = 0, -200 + random.uniform(-100, 100)
                elif n_dto.id in child_ids:
                    x, y = random.uniform(-200, 200), 200 + random.uniform(0, 100)
                elif n_dto.id in sibling_ids:
                    x, y = 260 + random.uniform(40, 160), random.uniform(-120, 120)  # Siblings to the right
                else:
                    x, y = random.uniform(-400, -200), random.uniform(-200, 200)
                    
                self.physics.add_node(n_dto.id, x, y)
                item.setPos(x, y)
            else:
                # Just Ensure Physics knows about it (if it was dormant?)
                # We assume existing items are already in physics
                 pass

        # 3. Create Edges
        # Only rebuild physics edges when resetting; preserve when keeping existing.
        if not keep_existing:
            self.physics.edges.clear() # Rebuild physics edges to match view
        
        existing_edge_ids = {e.edge_id for e in self._edges}

        def add_link(source_id: int, target_id: int, rtype: str, edge_id: int, appearance_json: Optional[str] = None):
            if source_id in self._items and target_id in self._items:
                if edge_id in existing_edge_ids:
                    return
                # View Edge
                style = json.loads(appearance_json) if appearance_json else None
                edge_item = MindscapeEdgeItem(edge_id, self._items[source_id], self._items[target_id], rtype, self.theme)
                if style: edge_item.set_style(style)
                self._scene.addItem(edge_item)
                self._edges.append(edge_item)
                
                # Physics Edge
                length = 320.0 if rtype == "jump" else 280.0
                stiff = 0.02 if rtype == "jump" else 0.025
                self.physics.add_edge(source_id, target_id, length, stiff)

        # Parents -> Focus
        for p_dto, e_dto in parents:
            add_link(p_dto.id, focus.id, "parent", e_dto.id, e_dto.appearance)
            
        # Focus -> Children
        for c_dto, e_dto in children:
            add_link(focus.id, c_dto.id, "parent", e_dto.id, e_dto.appearance)
            
        # Jumps
        for j_dto, e_dto in jumps:
            add_link(focus.id, j_dto.id, "jump", e_dto.id, e_dto.appearance)

        # Siblings (parent -> sibling edges already encoded in edge DTO)
        for s_dto, e_dto in siblings:
            add_link(e_dto.source_id, e_dto.target_id, "parent", e_dto.id, e_dto.appearance)

        # Fix the Focus node briefly to stabilize layout?
        # self.physics.set_fixed(focus_id, True)

    def item_at(self, pos: Union[QPointF, QPoint]):
        """Wrapper for itemAt that handles different Qt versions/signatures safely."""
        if isinstance(pos, QPointF):
            return self.itemAt(pos.toPoint())
        return self.itemAt(pos)

    
    def mousePressEvent(self, event: Optional[QMouseEvent]):
        if event is None:
            return
        item = self.item_at(event.pos())
        self._press_pos = event.pos()
        self._clicked_item_id = None
        
        # Handle Node Dragging
        if isinstance(item, MindscapeNodeItem):
            self._dragged_node_id = item.node_id
            self._clicked_item_id = item.node_id
            self.physics.set_fixed(item.node_id, True)
            self.setDragMode(QGraphicsView.DragMode.NoDrag) # Disable pan while dragging node
        # Handle Edge Selection
        elif isinstance(item, MindscapeEdgeItem):
             self.edge_selected.emit(item.edge_id)
        else:
             self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
             
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: Optional[QMouseEvent]):
        if event is None:
            return
        if self._dragged_node_id:
            # Map mouse to scene
            scene_pos = self.mapToScene(event.pos())
            self.physics.set_position(self._dragged_node_id, scene_pos.x(), scene_pos.y())
            if not self.physics_enabled:
                # Update edge visuals immediately when physics is off
                for edge in self._edges:
                    edge.update_path()
        
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: Optional[QMouseEvent]):
        if event is None:
            return
        if self._dragged_node_id:
            # Save new position to DB
            node_id = self._dragged_node_id
            pos = self.physics.get_position(node_id)
            self._persist_position_async(node_id, pos.x(), pos.y())

            # Keep the node anchored where released; zero velocity to prevent drift
            self.physics.set_position(node_id, pos.x(), pos.y())
            self.physics.set_fixed(node_id, False)
            self._dragged_node_id = None
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            if not self.physics_enabled:
                for edge in self._edges:
                    edge.update_path()
            
        # Click Detection (Press & Release roughly same spot)
        if self._clicked_item_id:
            dist = (event.pos() - self._press_pos).manhattanLength()
            if dist < 15: # Increased tolerance
                # Treated as Click
                self._on_node_clicked(self._clicked_item_id)
            self._clicked_item_id = None
            
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event: Optional[QWheelEvent]):
        """Zoom with mouse wheel."""
        if event is None:
            return
        zoom_in_factor = 1.1
        zoom_out_factor = 1 / zoom_in_factor

        # Save the scene pos under the mouse (AnchorUnderMouse handles most, but let's be safe)
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        # Check limits (0.1x to 10x)
        current_scale = self.transform().m11() # Horizontal scale
        
        if zoom_factor > 1 and current_scale > 5.0: return # Max zoom
        if zoom_factor < 1 and current_scale < 0.1: return # Min zoom
            
        self.scale(zoom_factor, zoom_factor)

    def update_node_visual(self, node_id, style_dict=None, title=None):
        """Live update of node visual without full reload."""
        if node_id in self._items:
            item = self._items[node_id]
            if style_dict is not None: item.set_style(style_dict)
            if title is not None: item.set_title(title)

    def update_edge_visual(self, edge_id, style_dict=None):
        """Live update of edge visual."""
        for edge in self._edges:
            if edge.edge_id == edge_id:
                if style_dict is not None: edge.set_style(style_dict)
                break
            
    def _physics_tick(self):
        """Called every frame to update visuals. Physics motion can be disabled."""
        # Adaptive throttling for large graphs
        node_count = len(self._items)
        if node_count > 200:
            self.timer.setInterval(40)
        else:
            self.timer.setInterval(24)

        if self.physics_enabled:
            self.physics.tick()
            # Sync Items to Physics
            for nid, item in self._items.items():
                pos = self.physics.get_position(nid)
                item.setPos(pos)

        # Always keep edges in sync with current node positions
        for edge in self._edges:
            edge.update_path()

    def _on_node_clicked(self, node_id):
        # Allow selecting the focus node too (for Inspector)
        self.node_selected.emit(node_id)
        if node_id != self.current_focus_id:
            self.load_graph(node_id) # Self-drive or let controller do it? Controller better but shortcut here.
 
    def resizeEvent(self, event):
        super().resizeEvent(event)

    def drawForeground(self, painter: Optional[QPainter], rect: QRectF):
        """Draw helper text when empty and highlight the current focus."""
        if painter is None:
            return
        if not self._items:
            painter.setPen(Qt.GlobalColor.white)
            font = QFont("Arial", 16)
            painter.setFont(font)
            text = "Right-click to create your first thought."
            painter.drawText(QRectF(-200, -50, 400, 100), Qt.AlignmentFlag.AlignCenter, text)
            return

        if self.current_focus_id is None or self.current_focus_id not in self._items:
            super().drawForeground(painter, rect)
            return

        painter.setPen(Qt.GlobalColor.white)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        center = self._items[self.current_focus_id].scenePos()
        painter.drawEllipse(center, 80, 80)
        super().drawForeground(painter, rect)

    def _persist_position_async(self, node_id: int, x: float, y: float):
        """Offload position persistence to a worker to keep UI fluid."""

        class _PersistTask(QRunnable):
            def run(self):
                try:
                    with mindscape_service_context() as svc:
                        svc.update_node_position(node_id, x, y)
                except Exception as exc:  # pragma: no cover - defensive logging only
                    print(f"Error saving node position: {exc}")

        self.thread_pool.start(_PersistTask())
