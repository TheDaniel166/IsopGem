
import sys
from unittest.mock import MagicMock

# EXPERIMENTAL PATCH: Mock TQ module to avoid database dependency in prototype
# This prevents the need to install sqlalchemy or modify src/ code for this experiment.
sys.modules["src.pillars.tq.ui.quadset_analysis_window"] = MagicMock()

from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer, QRectF, Qt, QPointF
from PyQt6.QtGui import QColor, QPainter
import math

from experiments.starfield_nexus.star_node import StarNode
from experiments.starfield_nexus.galaxy_background import GalaxyBackground
from experiments.starfield_nexus.data_stream import DataStream

class NexusGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.setBackgroundBrush(QColor("#050510"))
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        
        # Dimensions
        self.scene().setSceneRect(-800, -600, 1600, 1200)
        
        # Background
        self.galaxy = GalaxyBackground(self.scene().sceneRect(), star_count=500)
        self.scene().addItem(self.galaxy)
        
        # State
        self.current_level = "UNIVERSE" # UNIVERSE or SYSTEM
        self.target_node = None
        
        # Nodes (Pillars)
        self.nodes = {}
        self._create_nodes()
        
        # Connections
        self.streams = []
        self._create_connections()
        
        # Animation Loop
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(16) # ~60 FPS
        self.phase = 0.0

    def _create_nodes(self):
        # Layout: Sigil Lattice
        # Center Node: Adyton
        self.nodes['Adyton'] = StarNode("Adyton", 0, 0, size=150)
        
        # Satellites
        self.nodes['Gematria'] = StarNode("Gematria", -300, -100)
        self.nodes['Geometry'] = StarNode("Geometry", 300, -100)
        self.nodes['Astrology'] = StarNode("Astrology", 0, -300)
        self.nodes['TQ'] = StarNode("TQ", 0, 300)
        
        for name, node in self.nodes.items():
            self.scene().addItem(node)
            
        # --- Create Geometry System (Moons) ---
        geo_node = self.nodes['Geometry']
        geo_node.is_moon = False # It is a Star
        
        moons = [
            "Scientific Calc",
            "Esoteric Wisdom",
            "Nested Heptagons",
            "Polygonal Num",
            "Exp. Star",
            "Figurate 3D"
        ]
        
        radius = 200
        angle_step = (2 * math.pi) / len(moons)
        
        for i, moon_name in enumerate(moons):
            angle = i * angle_step
            mx = geo_node.x() + radius * math.cos(angle)
            my = geo_node.y() + radius * math.sin(angle)
            
            moon = StarNode(moon_name, mx, my, size=60)
            moon.is_moon = True
            moon.parent_node = geo_node
            moon.setVisible(False) # Hidden initially
            
            geo_node.children.append(moon)
            self.scene().addItem(moon)

    def _create_connections(self):
        # Connect Center to All
        center = self.nodes['Adyton']
        for name, node in self.nodes.items():
            if name != 'Adyton':
                stream = DataStream(center, node)
                self.scene().addItem(stream)
                self.streams.append(stream)
                
        # Cross Connect (The Braided Bus)
        self.streams.append(DataStream(self.nodes['Gematria'], self.nodes['Astrology']))
        self.scene().addItem(self.streams[-1])

    def _animate(self):
        self.phase += 0.01
        if self.phase > 1.0:
            self.phase = 0.0
            
        for stream in self.streams:
            stream.advance(self.phase)

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if isinstance(item, StarNode):
            self._handle_node_click(item)
        elif self.current_level == "SYSTEM" and item == None:
             # Click void to go back
             self._transition_to_universe()
        
        super().mousePressEvent(event)

    def _handle_node_click(self, node):
        if node.children and self.current_level == "UNIVERSE":
            # Enter System
            self._transition_to_system(node)
        elif node.is_moon:
            print(f"🚀 LAUNCHING TOOL: {node.label}")
            self._launch_tool(node.label)
        else:
            print(f"Selected Pillar: {node.label}")

    def _launch_tool(self, tool_name: str):
        """Launch the actual tool window."""
        # Keep references to windows to prevent garbage collection
        if not hasattr(self, "_active_windows"):
            self._active_windows = []
            
        try:
            window = None
            if tool_name == "Scientific Calc":
                from src.pillars.geometry.ui.advanced_scientific_calculator_window import AdvancedScientificCalculatorWindow
                window = AdvancedScientificCalculatorWindow()
            elif tool_name == "Figurate 3D":
                from src.pillars.geometry.ui.figurate_3d_window import Figurate3DWindow
                window = Figurate3DWindow()
            elif tool_name == "Esoteric Wisdom":
                from src.pillars.geometry.ui.esoteric_wisdom_window import EsotericWisdomWindow
                window = EsotericWisdomWindow()
            elif tool_name == "Nested Heptagons":
                from src.pillars.geometry.ui.nested_heptagons_window import NestedHeptagonsWindow
                window = NestedHeptagonsWindow()
            elif tool_name == "Polygonal Num":
                from src.pillars.geometry.ui.polygonal_number_window import PolygonalNumberWindow
                window = PolygonalNumberWindow()
            elif tool_name == "Exp. Star":
                from src.pillars.geometry.ui.experimental_star_window import ExperimentalStarWindow
                window = ExperimentalStarWindow()
                
            if window:
                window.show()
                self._active_windows.append(window)
                print(f"✅ Window opened: {tool_name}")
            else:
                print(f"⚠️ Unknown tool: {tool_name}")
                
        except Exception as e:
            print(f"❌ Failed to launch {tool_name}: {e}")
            import traceback
            traceback.print_exc()

    def _transition_to_system(self, target_node):
        print(f"🌌 Entering System: {target_node.label}")
        self.current_level = "SYSTEM"
        
        # 1. Hide other Universe Nodes (fade would be better, toggle for now)
        for name, node in self.nodes.items():
            if node != target_node:
                node.setVisible(False)
        
        # 2. Show Moons
        for moon in target_node.children:
            moon.setVisible(True)
            
        # 3. Zoom Camera
        # Center on the node
        self.centerOn(target_node)
        self.scale(2.0, 2.0) # Zoom in 2x

    def _transition_to_universe(self):
        print("🔙 Returning to Universe")
        self.current_level = "UNIVERSE"
        
        # 1. Reset Camera
        self.resetTransform()
        self.centerOn(0, 0)
        
        # 2. Show Universe Nodes
        for name, node in self.nodes.items():
            node.setVisible(True)
            
        # 3. Hide all Moons (brute force iterate all nodes? Or just track current system)
        # For prototype, iterate all Geometry children
        # Ideally we track 'active_system_node'
        geo = self.nodes.get('Geometry')
        if geo:
            for moon in geo.children:
                moon.setVisible(False)

class NexusWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IsopGem: Starfield Nexus Prototype (Fractal Navigation)")
        self.resize(1024, 768)
        
        self.view = NexusGraphicsView()
        self.setCentralWidget(self.view)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NexusWindow()
    window.show()
    sys.exit(app.exec())
