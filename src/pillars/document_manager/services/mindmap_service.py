"""Service layer for mindmaps (nodes/edges, multi-map support)."""
from __future__ import annotations
from typing import Iterable, Optional, cast
from contextlib import contextmanager
from sqlalchemy.orm import Session
from shared.database import get_db_session
from pillars.document_manager.models.mindmap import Mindmap, MindmapNode, MindmapEdge


class MindmapService:
    def __init__(self, db: Session):
        self.db = db

    # --- Mindmap CRUD ---
    def list_maps(self):
        return self.db.query(Mindmap).order_by(Mindmap.name).all()

    def create_map(self, name: str, description: str | None = None) -> Mindmap:
        m = Mindmap(name=name, description=description or "")
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return m

    def rename_map(self, map_id: int, name: str, description: Optional[str] = None) -> Optional[Mindmap]:
        m = self.db.get(Mindmap, map_id)
        if not m:
            return None
        m.name = name  # type: ignore[assignment]
        if description is not None:
            m.description = description  # type: ignore[assignment]
        self.db.commit()
        self.db.refresh(m)
        return m

    def delete_map(self, map_id: int) -> bool:
        m = self.db.get(Mindmap, map_id)
        if not m:
            return False
        self.db.delete(m)
        self.db.commit()
        return True

    def get_map(self, map_id: int) -> Optional[Mindmap]:
        return self.db.get(Mindmap, map_id)

    # --- Nodes ---
    def add_node(self, map_id: int, **kwargs) -> MindmapNode:
        node = MindmapNode(map_id=map_id, **kwargs)
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)
        return node

    def update_node(self, node_id: int, **kwargs) -> Optional[MindmapNode]:
        node = self.db.get(MindmapNode, node_id)
        if not node:
            return None
        for k, v in kwargs.items():
            setattr(node, k, v)
        self.db.commit()
        self.db.refresh(node)
        return node

    def delete_node(self, node_id: int) -> bool:
        node = self.db.get(MindmapNode, node_id)
        if not node:
            return False
        # Delete edges attached to this node
        self.db.query(MindmapEdge).filter(
            (MindmapEdge.source_id == node_id) | (MindmapEdge.target_id == node_id)
        ).delete(synchronize_session=False)
        self.db.delete(node)
        self.db.commit()
        return True

    def update_node_positions(self, map_id: int, positions: Iterable[tuple[int, float, float, float]]):
        """Bulk update node positions (x,y,z). positions is iterable of (node_id, x, y, z)."""
        node_map: dict[int, MindmapNode] = {int(cast(int, n.id)): n for n in self.db.query(MindmapNode).filter(MindmapNode.map_id == map_id)}
        for node_id, x, y, z in positions:
            node = node_map.get(int(node_id))
            if node is not None and not bool(node.pinned):
                node.x = float(x)  # type: ignore[assignment]
                node.y = float(y)  # type: ignore[assignment]
                node.z = float(z)  # type: ignore[assignment]
        self.db.commit()

    # --- Edges ---
    def add_edge(self, map_id: int, source_id: int, target_id: int, **kwargs) -> MindmapEdge:
        edge = MindmapEdge(map_id=map_id, source_id=source_id, target_id=target_id, **kwargs)
        self.db.add(edge)
        self.db.commit()
        self.db.refresh(edge)
        return edge

    def update_edge(self, edge_id: int, **kwargs) -> Optional[MindmapEdge]:
        edge = self.db.get(MindmapEdge, edge_id)
        if not edge:
            return None
        for k, v in kwargs.items():
            setattr(edge, k, v)
        self.db.commit()
        self.db.refresh(edge)
        return edge

    def delete_edge(self, edge_id: int) -> bool:
        edge = self.db.get(MindmapEdge, edge_id)
        if not edge:
            return False
        self.db.delete(edge)
        self.db.commit()
        return True

    # --- Bulk load ---
    def get_map_graph(self, map_id: int):
        nodes = self.db.query(MindmapNode).filter(MindmapNode.map_id == map_id).all()
        edges = self.db.query(MindmapEdge).filter(MindmapEdge.map_id == map_id).all()
        return nodes, edges


@contextmanager
def mindmap_service_context():
    """Yield a MindmapService backed by a managed DB session."""
    with get_db_session() as db:
        yield MindmapService(db)
