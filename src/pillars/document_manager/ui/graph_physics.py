"""
Graph Physics Engine for Mindscape.
Implements a Force-Directed Graph layout algorithm (Fruchterman-Reingold inspired).
"""
import math
from PyQt6.QtCore import QPointF
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class PhysicsNode:
    id: int
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    mass: float = 1.0
    radius: float = 80.0 # Interaction radius (approx half width)
    fixed: bool = False # If true, physics won't move it (e.g. being dragged)

@dataclass
class PhysicsEdge:
    source_id: int
    target_id: int
    length: float = 250.0 # Desired length
    stiffness: float = 0.05

class GraphPhysics:
    def __init__(self):
        self.nodes: Dict[int, PhysicsNode] = {}
        self.edges: List[PhysicsEdge] = []
        
        # Constants
        self.REPULSION = 400000.0 # Reduced from 800k to calm explosive starts
        self.DAMPING = 0.65      # Heavy friction (0.85 -> 0.65) to stop sliding
        self.MAX_SPEED = 12.0     # Cap speed (50 -> 12) for gentle movement
        self.center_force = 0.01 # Weaker gravity to center
        
    def add_node(self, node_id: int, x: float, y: float, mass: float = 1.0):
        if node_id not in self.nodes:
            self.nodes[node_id] = PhysicsNode(id=node_id, x=x, y=y, mass=mass)
            
    def remove_node(self, node_id: int):
        if node_id in self.nodes:
            del self.nodes[node_id]
        # Remove associated edges
        self.edges = [e for e in self.edges if e.source_id != node_id and e.target_id != node_id]
            
    def add_edge(self, source_id: int, target_id: int, length: float = 250.0, stiffness: float = 0.05):
        # Avoid duplicate edges
        for e in self.edges:
            if (e.source_id == source_id and e.target_id == target_id) or \
               (e.source_id == target_id and e.target_id == source_id):
                   return
                   
        self.edges.append(PhysicsEdge(source_id, target_id, length, stiffness))
        
    def clear(self):
        self.nodes.clear()
        self.edges.clear()
        
    def set_position(self, node_id: int, x: float, y: float):
        if node_id in self.nodes:
            self.nodes[node_id].x = x
            self.nodes[node_id].y = y
            self.nodes[node_id].vx = 0
            self.nodes[node_id].vy = 0
            
    def set_fixed(self, node_id: int, is_fixed: bool):
        if node_id in self.nodes:
            self.nodes[node_id].fixed = is_fixed
            if is_fixed:
                self.nodes[node_id].vx = 0
                self.nodes[node_id].vy = 0

    def tick(self, dt: float = 0.016):
        """Step the simulation."""
        
        # 1. Apply Repulsion (Node vs Node)
        node_ids = list(self.nodes.keys())
        for i in range(len(node_ids)):
            n1 = self.nodes[node_ids[i]]
            
            # Center Gravity (Pull to 0,0)
            dist_center = math.sqrt(n1.x*n1.x + n1.y*n1.y) or 1.0
            n1.vx -= (n1.x / dist_center) * self.center_force * dist_center
            n1.vy -= (n1.y / dist_center) * self.center_force * dist_center
            
            for j in range(i + 1, len(node_ids)):
                n2 = self.nodes[node_ids[j]]
                
                dx = n1.x - n2.x
                dy = n1.y - n2.y
                dist_sq = dx*dx + dy*dy
                
                if dist_sq < 1: dist_sq = 1 # Avoid div by zero
                
                dist = math.sqrt(dist_sq)
                
                # F = k / dist^2
                force = self.REPULSION / dist_sq
                
                fx = (dx / dist) * force
                fy = (dy / dist) * force
                
                if not n1.fixed:
                    n1.vx += fx
                    n1.vy += fy
                if not n2.fixed:
                    n2.vx -= fx
                    n2.vy -= fy
                    
        # 2. Apply Springs (Edges)
        for edge in self.edges:
            if edge.source_id not in self.nodes or edge.target_id not in self.nodes:
                continue
                
            n1 = self.nodes[edge.source_id]
            n2 = self.nodes[edge.target_id]
            
            dx = n2.x - n1.x
            dy = n2.y - n1.y
            dist = math.sqrt(dx*dx + dy*dy) or 1.0
            
            # Hooke's Law: F = k * (current_dist - desired_length)
            displacement = dist - edge.length
            force = edge.stiffness * displacement
            
            fx = (dx / dist) * force
            fy = (dy / dist) * force
            
            if not n1.fixed:
                n1.vx += fx
                n1.vy += fy
            if not n2.fixed:
                n2.vx -= fx
                n2.vy -= fy
                
        # 3. Update Positions (Integration)
        for node in self.nodes.values():
            if node.fixed:
                continue
                
            # Damping
            node.vx *= self.DAMPING
            node.vy *= self.DAMPING
            
            # Speed Limit
            speed = math.sqrt(node.vx*node.vx + node.vy*node.vy)
            if speed > self.MAX_SPEED:
                scale = self.MAX_SPEED / speed
                node.vx *= scale
                node.vy *= scale
                
            node.x += node.vx
            node.y += node.vy
            
    def get_position(self, node_id: int) -> QPointF:
        if node_id in self.nodes:
            return QPointF(self.nodes[node_id].x, self.nodes[node_id].y)
        return QPointF(0, 0)
