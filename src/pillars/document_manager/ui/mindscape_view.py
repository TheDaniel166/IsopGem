
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt, QPointF, pyqtSignal, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QRectF
from PyQt6.QtGui import QPainter, QColor, QBrush, QFont
from pillars.document_manager.services.mindscape_service import mindscape_service_context
from .mindscape_items import MindscapeNodeItem, MindscapeEdgeItem
from .mindscape_theme import GraphTheme
import json

class MindscapeView(QGraphicsView):
    """
    The Plex: A Dynamic, Animated Graph View.
    """
    node_selected = pyqtSignal(int) # Emits ID when a node becomes the Focus
    edge_selected = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Initialize Theme
        self.theme = GraphTheme("Dark") # Default
        
        # Visual Setup
        self.setBackgroundBrush(QBrush(self.theme.get_color("background")))
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        
        # State
        self._items = {}
        self._edges = []
        self.current_focus_id = None
        self._is_animating = False
        self.anim_group = None

    def load_graph(self, focus_id: int):
        """
        Loads the local graph centered on focus_id and animates layout.
        """
        self.current_focus_id = focus_id
        
        # 1. Fetch Data
        with mindscape_service_context() as svc:
            focus, parents, children, jumps = svc.get_local_graph(focus_id)
            
        if not focus:
            return
            
        # Clear old edges (rebuilding them is cheap and safer for now)
        for edge in self._edges:
            self.scene.removeItem(edge)
        self._edges.clear()

        # 2. Reconcile Items (Create missing, reused existing, schedule delete unused)
        # Unpack tuples from Service (NodeDTO, EdgeDTO)
        parent_nodes = [p[0] for p in parents]
        child_nodes = [c[0] for c in children]
        jump_nodes = [j[0] for j in jumps]
        
        active_ids = {focus.id} | {p.id for p in parent_nodes} | {c.id for c in child_nodes} | {j.id for j in jump_nodes}
        
        # Create missing items
        all_node_dtos = [focus] + parent_nodes + child_nodes + jump_nodes
        for node_data in all_node_dtos:
            if node_data.id not in self._items:
                # Pass Theme
                item = MindscapeNodeItem(node_data.id, node_data.title, node_data.type, node_data.icon, self.theme)
                
                # Apply Node Style
                if node_data.appearance:
                    try:
                        style = json.loads(node_data.appearance)
                        item.set_style(style)
                    except:
                        pass
                        
                item.clicked.connect(self._on_node_clicked)
                item.position_changed.connect(self._update_connected_edges) # ESSENTIAL FIX
                self.scene.addItem(item)
                item.setPos(0, 0) # Start at center (will animate)
                item.setOpacity(0) # Fade in
                self._items[node_data.id] = item
        
        # Create Edges
        # Parents -> Focus
        for p_dto, edge_dto in parents:
            if p_dto.id in self._items:
                style = json.loads(edge_dto.appearance) if edge_dto.appearance else None
                self._create_edge(edge_dto.id, self._items[p_dto.id], self._items[focus.id], "parent", style)
                
        # Focus -> Children
        for c_dto, edge_dto in children:
            if c_dto.id in self._items:
                style = json.loads(edge_dto.appearance) if edge_dto.appearance else None
                self._create_edge(edge_dto.id, self._items[focus.id], self._items[c_dto.id], "parent", style)
                
        # Connect Jumps
        for j_dto, edge_dto in jumps:
            if j_dto.id in self._items:
                style = json.loads(edge_dto.appearance) if edge_dto.appearance else None
                self._create_edge(edge_dto.id, self._items[focus.id], self._items[j_dto.id], "jump", style)

        if not focus:
            return

        # 3. Calculate Layout Targets
        targets = self._calculate_layout(focus, parent_nodes, child_nodes, jump_nodes)
        
        # 4. Animate to Targets
        self._animate_layout(targets, active_ids)

    def item_at(self, pos):
        """Wrapper for itemAt that handles different Qt versions/signatures safely."""
        return self.itemAt(pos)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        
        # Check for Edge Selection
        item = self.itemAt(event.pos())
        if hasattr(item, "edge_id"):
            self.edge_selected.emit(item.edge_id)
            # Deselect nodes if edge selected?
            # self.scene.clearSelection() 

    def update_node_visual(self, node_id, style_dict=None, title=None):
        """Live update of node visual without full reload."""
        if node_id in self._items:
            item = self._items[node_id]
            if style_dict is not None:
                item.set_style(style_dict)
            if title is not None:
                item.set_title(title)

    def update_edge_visual(self, edge_id, style_dict=None):
        """Live update of edge visual."""
        # Find item by edge_id
        for edge in self._edges:
            if edge.edge_id == edge_id:
                if style_dict is not None:
                    edge.set_style(style_dict)
                break
            
    def _create_edge(self, edge_id, source, target, rtype, style=None):
        # Pass Theme
        edge = MindscapeEdgeItem(edge_id, source, target, rtype, self.theme)
        if style:
            edge.set_style(style)
        self.scene.addItem(edge)
        self._edges.append(edge)

    def _update_connected_edges(self):
        """Called when a node moves. Brute force update all edges (simple enough for <100 items)."""
        for edge in self._edges:
            edge.update_path()

    def _calculate_layout(self, focus, parents, children, jumps):
        """
        The Brain Layout Algorithm:
        Focus -> (0,0)
        Parents -> Row above (-y)
        Children -> Grid below (+y)
        Jumps -> Columns left/right (+/- x)
        """
        targets = {} # node_id -> QPointF
        
        # Focus
        targets[focus.id] = QPointF(0, 0)
        
        # Parents (Row)
        p_y = -180
        if parents:
            spacing = 180
            start_x = -((len(parents) - 1) * spacing) / 2
            for i, p in enumerate(parents):
                targets[p.id] = QPointF(start_x + i * spacing, p_y)
                
        # Children (Grid)
        c_y_start = 180
        if children:
            cols = 3
            col_spacing = 180
            row_spacing = 100
            for i, c in enumerate(children):
                row = i // cols
                col = i % cols
                # center the row
                row_len = min(cols, len(children) - row*cols)
                row_start_x = -((row_len - 1) * col_spacing) / 2
                
                x = row_start_x + col * col_spacing
                y = c_y_start + row * row_spacing
                targets[c.id] = QPointF(x, y)
                
        # Jumps (Left Column mostly, split if many?)
        # For simplicity: Left side stack
        j_x = -400
        start_y = -100
        spacing = 100
        for i, j in enumerate(jumps):
             targets[j.id] = QPointF(j_x, start_y + i * spacing)
             
        return targets

    def _animate_layout(self, targets, active_ids):
        """
        Animate items to their new targets.
        """
        # 1. Stop existing animations to prevent conflicts
        if self.anim_group:
            self.anim_group.stop()
            for i in range(self.anim_group.animationCount()):
                self.anim_group.takeAnimation(i)
            self.anim_group.clear() # Clear memory
            
        self.anim_group = QParallelAnimationGroup(self) # Parent it to self to prevent GC
        
        # 2. Process Active Items
        for nid, target_pos in targets.items():
            if nid not in self._items: continue
            
            item = self._items[nid]
            item._selected = (nid == self.current_focus_id)
            item.update() # Force repaint of selection state
            
            # POSITION: Add animation
            pos_anim = QPropertyAnimation(item, b"pos")
            pos_anim.setDuration(600)
            pos_anim.setStartValue(item.pos())
            pos_anim.setEndValue(target_pos)
            pos_anim.setEasingCurve(QEasingCurve.Type.OutExpo)
            self.anim_group.addAnimation(pos_anim)
            
            # OPACITY: Only animate if it's currently invisible/fading
            # If it's already visible, ensure it STAYS visible (in case it was fading out)
            if item.opacity() < 0.99:
                op_anim = QPropertyAnimation(item, b"opacity")
                op_anim.setDuration(400)
                op_anim.setStartValue(item.opacity()) # Start from CURRENT, not 0
                op_anim.setEndValue(1)
                self.anim_group.addAnimation(op_anim)
            else:
                item.setOpacity(1) # Force full visibility if not animating
        
        # 3. Process Dead Items (Fade Out)
        for nid, item in list(self._items.items()):
            if nid not in active_ids:
                # Option A: Simple immediate remove (Safest for debugging)
                self.scene.removeItem(item)
                del self._items[nid]

        self.anim_group.start()

    def _on_node_clicked(self, node_id):
        # Allow selecting the focus node too (for Inspector)
        self.node_selected.emit(node_id)
        if node_id != self.current_focus_id:
            self.load_graph(node_id) # Self-drive or let controller do it? Controller better but shortcut here.
 
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.centerOn(0, 0)

    def drawForeground(self, painter, rect):
        """Draw helpful text if the graph is empty."""
        if not self._items:
            painter.setPen(Qt.GlobalColor.white)
            font = QFont("Arial", 16)
            painter.setFont(font)
            
            text = "Right-click to create your first thought."
            
            painter.drawText(QRectF(-200, -50, 400, 100), Qt.AlignmentFlag.AlignCenter, text)
            
        super().drawForeground(painter, rect)
