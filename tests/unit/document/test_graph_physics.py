
import pytest
import math
from pillars.document_manager.ui.graph_physics import GraphPhysics

def test_physics_initialization():
    physics = GraphPhysics()
    assert len(physics.nodes) == 0
    assert len(physics.edges) == 0

def test_add_remove_node():
    physics = GraphPhysics()
    physics.add_node(1, 0, 0)
    assert 1 in physics.nodes
    assert physics.nodes[1].x == 0
    assert physics.nodes[1].y == 0
    
    physics.remove_node(1)
    assert 1 not in physics.nodes

def test_repulsion():
    """Two nodes should push each other away."""
    physics = GraphPhysics()
    physics.add_node(1, -10, 0)
    physics.add_node(2, 10, 0)
    
    # Tick
    physics.tick(0.016)
    
    n1 = physics.nodes[1]
    n2 = physics.nodes[2]
    
    # N1 should move Left (-x), N2 Right (+x)
    assert n1.vx < 0
    assert n2.vx > 0
    
def test_spring_attraction():
    """Connected nodes far apart should pull together."""
    physics = GraphPhysics()
    physics.add_node(1, -500, 0)
    physics.add_node(2, 500, 0)
    physics.add_edge(1, 2, length=100, stiffness=0.1)
    
    physics.tick(0.016)
    
    n1 = physics.nodes[1]
    n2 = physics.nodes[2]
    
    # N1 should move Right (+), N2 Left (-)
    assert n1.vx > 0
    assert n2.vx < 0
