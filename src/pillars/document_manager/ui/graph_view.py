"""Graph View for Document Connections (Zettelkasten)."""
import math
import random
from PyQt6.QtWidgets import (
    QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsItem, 
    QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsSimpleTextItem,
    QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QSlider
)
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF, pyqtSignal
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter, QFont
from pillars.document_manager.services.document_service import document_service_context

class NodeItem(QGraphicsEllipseItem):
    """Visual representation of a document node."""
    def __init__(self, doc_id, title, graph_window):
        super().__init__(-20, -20, 40, 40)
        self.doc_id = doc_id
        self.title = title
        self.graph_window = graph_window
        
        # Visuals
        self.setBrush(QBrush(QColor("#3b82f6"))) # Blue
        self.setPen(QPen(Qt.GlobalColor.white, 2))
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | 
                      QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges |
                      QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        
        # Label
        self.label = QGraphicsSimpleTextItem(title, self)
        self.label.setBrush(QBrush(Qt.GlobalColor.black))
        font = QFont("Arial", 10)
        self.label.setFont(font)
        # Center label below node
        rect = self.label.boundingRect()
        self.label.setPos(-rect.width() / 2, 25)
        
        # Physics properties
        self.velocity = QPointF(0, 0)
        self.force = QPointF(0, 0)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.graph_window.item_moved(self)
        return super().itemChange(change, value)

    def mouseDoubleClickEvent(self, event):
        self.graph_window.node_double_clicked(self.doc_id)
        super().mouseDoubleClickEvent(event)

class EdgeItem(QGraphicsLineItem):
    """Visual representation of a link between documents."""
    def __init__(self, source_node, target_node):
        super().__init__()
        self.source_node = source_node
        self.target_node = target_node
        self.setPen(QPen(QColor("#9ca3af"), 2)) # Gray
        self.setZValue(-1) # Behind nodes
        self.update_position()

    def update_position(self):
        self.setLine(
            self.source_node.scenePos().x(), self.source_node.scenePos().y(),
            self.target_node.scenePos().x(), self.target_node.scenePos().y()
        )

class GraphWindow(QMainWindow):
    """Window displaying the document graph."""
    
    document_opened = pyqtSignal(int) # Emits doc_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Knowledge Graph")
        self.resize(1000, 800)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh Graph")
        self.btn_refresh.clicked.connect(self.load_graph)
        controls_layout.addWidget(self.btn_refresh)
        
        self.btn_layout = QPushButton("Toggle Physics")
        self.btn_layout.setCheckable(True)
        self.btn_layout.setChecked(True)
        self.btn_layout.clicked.connect(self.toggle_physics)
        controls_layout.addWidget(self.btn_layout)
        
        controls_layout.addStretch()
        self.main_layout.addLayout(controls_layout)
        
        # Graphics View
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.view.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.main_layout.addWidget(self.view)
        
        # Data
        self.nodes = {} # doc_id -> NodeItem
        self.edges = [] # List of EdgeItem
        
        # Physics Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.apply_forces)
        self.timer.start(30) # ~30 FPS
        
        self.load_graph()

    def load_graph(self):
        self.scene.clear()
        self.nodes.clear()
        self.edges.clear()
        
        try:
            with document_service_context() as service:
                # We need to fetch documents with their links
                # Since outgoing_links is lazy loaded, accessing it will trigger a query
                # But we need to be careful about session management if we pass objects around
                # So we'll just fetch everything here
                all_docs = service.get_all_documents()
                
                # Create Nodes
                for doc in all_docs:
                    node = NodeItem(doc.id, doc.title, self)
                    # Random initial position
                    node.setPos(random.uniform(-300, 300), random.uniform(-300, 300))
                    self.scene.addItem(node)
                    self.nodes[doc.id] = node
                    
                # Create Edges
                for doc in all_docs:
                    if doc.id not in self.nodes:
                        continue
                    
                    source_node = self.nodes[doc.id]
                    
                    for target in doc.outgoing_links:
                        if target.id in self.nodes:
                            target_node = self.nodes[target.id]
                            edge = EdgeItem(source_node, target_node)
                            self.scene.addItem(edge)
                            self.edges.append(edge)
                        
        except Exception as e:
            print(f"Error loading graph: {e}")

    def item_moved(self, item):
        # Update connected edges
        for edge in self.edges:
            if edge.source_node == item or edge.target_node == item:
                edge.update_position()

    def node_double_clicked(self, doc_id):
        self.document_opened.emit(doc_id)

    def toggle_physics(self, checked):
        if checked:
            self.timer.start()
        else:
            self.timer.stop()

    def apply_forces(self):
        """Simple force-directed layout algorithm."""
        if not self.nodes:
            return
            
        # Constants
        REPULSION = 20000
        ATTRACTION = 0.05
        CENTER_GRAVITY = 0.01
        MAX_SPEED = 10
        DAMPING = 0.85
        
        # Reset forces
        for node in self.nodes.values():
            node.force = QPointF(0, 0)
            
        # Repulsion (Node vs Node)
        node_items = list(self.nodes.values())
        for i, n1 in enumerate(node_items):
            for n2 in node_items[i+1:]:
                dx = n1.x() - n2.x()
                dy = n1.y() - n2.y()
                dist_sq = dx*dx + dy*dy
                if dist_sq < 1: dist_sq = 1 # Avoid division by zero
                
                dist = math.sqrt(dist_sq)
                force = REPULSION / dist_sq
                
                fx = (dx / dist) * force
                fy = (dy / dist) * force
                
                n1.force += QPointF(fx, fy)
                n2.force -= QPointF(fx, fy)
                
        # Attraction (Edges)
        for edge in self.edges:
            n1 = edge.source_node
            n2 = edge.target_node
            
            dx = n1.x() - n2.x()
            dy = n1.y() - n2.y()
            
            # Hooke's Law
            n1.force -= QPointF(dx * ATTRACTION, dy * ATTRACTION)
            n2.force += QPointF(dx * ATTRACTION, dy * ATTRACTION)
            
        # Center Gravity (Keep graph centered)
        for node in self.nodes.values():
            node.force -= QPointF(node.x() * CENTER_GRAVITY, node.y() * CENTER_GRAVITY)
            
        # Apply Velocity and Position
        total_kinetic_energy = 0
        for node in self.nodes.values():
            if node.isSelected(): # Don't move selected nodes
                node.velocity = QPointF(0, 0)
                continue
                
            node.velocity += node.force
            node.velocity *= DAMPING
            
            # Limit speed
            speed = math.sqrt(node.velocity.x()**2 + node.velocity.y()**2)
            if speed > MAX_SPEED:
                node.velocity *= (MAX_SPEED / speed)
                
            node.setPos(node.pos() + node.velocity)
            total_kinetic_energy += speed
            
        # Stop simulation if stable (optional, but keeps CPU usage down)
        if total_kinetic_energy < 0.5 and len(self.nodes) > 0:
             # self.timer.stop() # Keep running for interactivity
             pass

