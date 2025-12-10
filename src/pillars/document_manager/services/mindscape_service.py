
"""
Mindscape 3.0 Service Layer
Handles the "Living Graph" traversal logic.
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from contextlib import contextmanager
from shared.database import get_db_session
from pillars.document_manager.models.mindscape import MindNode, MindEdge, MindEdgeType
from dataclasses import dataclass
from typing import Optional
import json

@dataclass
class MindNodeDTO:
    id: int
    title: str
    type: str
    content: Optional[str] = None
    tags: Optional[str] = None # JSON list
    appearance: Optional[str] = None # JSON dict
    metadata_payload: Optional[str] = None # JSON dict
    icon: Optional[str] = None
    
    @classmethod
    def from_orm(cls, node: MindNode):
        if not node:
            return None
        return cls(
            id=node.id,
            title=node.title,
            type=node.type,
            content=node.content,
            tags=node.tags,
            appearance=node.appearance,
            metadata_payload=node.metadata_payload,
            icon=node.icon
        )

@dataclass
class MindEdgeDTO:
    id: int
    source_id: int
    target_id: int
    relation_type: str
    appearance: Optional[str] = None # JSON dict

    @classmethod
    def from_orm(cls, edge: MindEdge):
        if not edge:
            return None
        return cls(
            id=edge.id,
            source_id=edge.source_id,
            target_id=edge.target_id,
            relation_type=edge.relation_type,
            appearance=edge.appearance
        )

class MindscapeService:
    def __init__(self, db: Session):
        self.db = db

    def create_node(self, title: str, type: str = "concept", content: str = None, tags: list = None, appearance: dict = None, metadata_payload: dict = None, icon: str = None) -> MindNodeDTO:
        """Create a new thought atom."""
        node = MindNode(
            title=title,
            type=type,
            content=content,
            tags=json.dumps(tags) if tags else "[]",
            appearance=json.dumps(appearance) if appearance else None,
            metadata_payload=json.dumps(metadata_payload) if metadata_payload else None,
            icon=icon
        )
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)
        return MindNodeDTO.from_orm(node)
        
    def update_node(self, node_id: int, data: dict) -> MindNodeDTO:
        """Update node details."""
        node = self.db.query(MindNode).get(node_id)
        if not node:
            return None
            
        if "title" in data:
            node.title = data["title"]
        if "content" in data:
            node.content = data["content"]
        if "tags" in data:
            node.tags = json.dumps(data["tags"])
        if "appearance" in data:
            node.appearance = json.dumps(data["appearance"])
        if "metadata_payload" in data:
             node.metadata_payload = json.dumps(data["metadata_payload"])
             
             
        self.db.commit()
        self.db.refresh(node)
        return MindNodeDTO.from_orm(node)

    def update_node_style(self, node_id: int, appearance: dict):
        node = self.db.query(MindNode).get(node_id)
        if node:
            node.appearance = json.dumps(appearance)
            self.db.commit()

    def update_node_position(self, node_id: int, x: float, y: float):
        """Update just the position in the appearance blob."""
        node = self.db.query(MindNode).get(node_id)
        if node:
            try:
                data = json.loads(node.appearance) if node.appearance else {}
            except:
                data = {}
            
            data["pos"] = [round(x, 1), round(y, 1)]
            node.appearance = json.dumps(data)
            self.db.commit()
            
    def wipe_database(self):
        """NUCLEAR OPTION: Delete ALL mindscape data."""
        # 1. Delete all edges first (foreign keys)
        self.db.query(MindEdge).delete()
        # 2. Delete all nodes
        self.db.query(MindNode).delete()
        self.db.commit()

    def update_edge_style(self, edge_id: int, appearance: dict):
        edge = self.db.query(MindEdge).get(edge_id)
        if edge:
            edge.appearance = json.dumps(appearance)
            self.db.commit()
            
    def get_edge(self, edge_id: int) -> MindEdgeDTO:
        """Fetch a single edge."""
        edge = self.db.query(MindEdge).get(edge_id)
        return MindEdgeDTO.from_orm(edge) if edge else None

    def get_edge(self, edge_id: int) -> MindEdgeDTO:
        """Fetch a single edge."""
        edge = self.db.query(MindEdge).get(edge_id)
        return MindEdgeDTO.from_orm(edge) if edge else None

    def find_node_by_document_id(self, doc_id: int) -> Optional[MindNodeDTO]:
        """Find a node linked to a specific document."""
        # SQLite JSON search (Basic string match is safer across versions than json_extract)
        # Search for '"document_id": <ID>' or '"document_id":<ID>'
        # Given we dump with default separators, it's usually "document_id": 123
        pattern = f'%"document_id": {doc_id}%' 
        node = self.db.query(MindNode).filter(
            MindNode.type == "document",
            MindNode.metadata_payload.like(pattern)
        ).first()
        return MindNodeDTO.from_orm(node) if node else None

    def update_edge(self, edge_id: int, data: dict) -> MindEdgeDTO:
        """Update edge details."""
        edge = self.db.query(MindEdge).get(edge_id)
        if not edge:
            return None
            
        if "relation_type" in data:
            edge.relation_type = data["relation_type"]
        if "appearance" in data:
            edge.appearance = json.dumps(data["appearance"])
            
        self.db.commit()
        self.db.refresh(edge)
        return MindEdgeDTO.from_orm(edge)

    def link_nodes(self, source_id: int, target_id: int, relation_type: str = "parent") -> MindEdge:
        """Link two nodes. If Parent, Source is Parent of Target."""
        edge = MindEdge(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type
        )
        self.db.add(edge)
        self.db.commit()
        self.db.refresh(edge)
        return edge

    def get_local_graph(self, focus_id: int):
        """
        The Core "Brain" Algorithm.
        Fetches the 'Plex' centered on focus_id.
        Returns:
            focus_node: MindNodeDTO
            parents: List[Tuple[MindNodeDTO, MindEdgeDTO]]
            children: List[Tuple[MindNodeDTO, MindEdgeDTO]]
            jumps: List[Tuple[MindNodeDTO, MindEdgeDTO]]
        """
        focus_node = self.db.query(MindNode).get(focus_id)
        if not focus_node:
            return None, [], [], []

        # 1. Parents
        # Join MindNode on SourceID where TargetID = Focus
        # We need the Edge object too.
        parent_results = self.db.query(MindNode, MindEdge).join(
            MindEdge, MindNode.id == MindEdge.source_id
        ).filter(
            MindEdge.target_id == focus_id,
            MindEdge.relation_type == MindEdgeType.PARENT.value
        ).all()
        
        parents = [(MindNodeDTO.from_orm(n), MindEdgeDTO.from_orm(e)) for n, e in parent_results]

        # 2. Children
        # Join MindNode on TargetID where SourceID = Focus
        child_results = self.db.query(MindNode, MindEdge).join(
            MindEdge, MindNode.id == MindEdge.target_id
        ).filter(
            MindEdge.source_id == focus_id,
            MindEdge.relation_type == MindEdgeType.PARENT.value
        ).all()
        
        children = [(MindNodeDTO.from_orm(n), MindEdgeDTO.from_orm(e)) for n, e in child_results]

        # 3. Jumps
        # This is trickier with OR.
        # Find edges where (Source=Focus OR Target=Focus) AND Type=Jump
        jump_edges = self.db.query(MindEdge).filter(
            or_(MindEdge.source_id == focus_id, MindEdge.target_id == focus_id),
            MindEdge.relation_type == MindEdgeType.JUMP.value
        ).all()
        
        jumps = []
        for e in jump_edges:
            other_id = e.target_id if e.source_id == focus_id else e.source_id
            other_node = self.db.query(MindNode).get(other_id)
            if other_node:
                jumps.append((MindNodeDTO.from_orm(other_node), MindEdgeDTO.from_orm(e)))

        return (
            MindNodeDTO.from_orm(focus_node),
            parents,
            children,
            jumps
        )

    def delete_node(self, node_id: int) -> Optional[MindNodeDTO]:
        """
        Deletes a node and its edges.
        Returns a suggested 'Fallback' node to focus on (Parent > Child > Jump > Root).
        """
        node = self.db.query(MindNode).get(node_id)
        if not node:
            return None

        # Determine Fallback before deletion
        # 1. Parent?
        parent_edge = self.db.query(MindEdge).filter(
            MindEdge.target_id == node_id,
            MindEdge.relation_type == MindEdgeType.PARENT.value
        ).first()
        
        fallback_id = None
        if parent_edge:
            fallback_id = parent_edge.source_id
        else:
            # 2. Child?
            child_edge = self.db.query(MindEdge).filter(
                MindEdge.source_id == node_id,
                MindEdge.relation_type == MindEdgeType.PARENT.value
            ).first()
            if child_edge:
                fallback_id = child_edge.target_id
            else:
                # 3. Jump (Linked via source or target)?
                jump_edge = self.db.query(MindEdge).filter(
                    or_(MindEdge.source_id == node_id, MindEdge.target_id == node_id),
                    MindEdge.relation_type == MindEdgeType.JUMP.value
                ).first()
                if jump_edge:
                    fallback_id = jump_edge.source_id if jump_edge.target_id == node_id else jump_edge.target_id

        # Delete Associated Edges
        self.db.query(MindEdge).filter(
            or_(MindEdge.source_id == node_id, MindEdge.target_id == node_id)
        ).delete()
        
        # Delete Node
        self.db.delete(node)
        self.db.commit()
        
        # Fetch Fallback
        if fallback_id:
            fallback = self.db.query(MindNode).get(fallback_id)
            return MindNodeDTO.from_orm(fallback)
        
        # 4. Any other node (Root)
        return self.get_home_node()

    def get_home_node(self) -> Optional[MindNodeDTO]:
        """
        Get the 'Root' or first node.
        Returns None if graph is empty (Blank Canvas).
        """
        node = self.db.query(MindNode).order_by(MindNode.id.asc()).first()
        return MindNodeDTO.from_orm(node) if node else None

@contextmanager
def mindscape_service_context():
    """Provide a transactional scope for Mindscape operations."""
    with get_db_session() as db:
        yield MindscapeService(db)
