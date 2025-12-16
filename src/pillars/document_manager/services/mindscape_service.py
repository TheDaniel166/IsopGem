
"""
Mindscape 3.0 Service Layer
Handles the "Living Graph" traversal logic.
"""
import json
import logging
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, cast

from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from shared.database import get_db_session
from pillars.document_manager.models.mindscape import MindNode, MindEdge, MindEdgeType

logger = logging.getLogger(__name__)

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
        return cls(
            id=cast(int, node.id),
            title=cast(str, node.title),
            type=cast(str, node.type),
            content=cast(Optional[str], node.content),
            tags=cast(Optional[str], node.tags),
            appearance=cast(Optional[str], node.appearance),
            metadata_payload=cast(Optional[str], node.metadata_payload),
            icon=cast(Optional[str], node.icon),
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
        return cls(
            id=cast(int, edge.id),
            source_id=cast(int, edge.source_id),
            target_id=cast(int, edge.target_id),
            relation_type=cast(str, edge.relation_type),
            appearance=cast(Optional[str], edge.appearance),
        )

class MindscapeService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_home_node(self) -> MindNodeDTO:
        """Fetch the first node or create a canonical root if the graph is empty."""
        node = self.db.query(MindNode).order_by(MindNode.id.asc()).first()
        if node:
            return MindNodeDTO.from_orm(node)

        logger.info("Mindscape is empty; forging the Root Thought.")
        root = MindNode(title="Central Thought", type="concept", content="Root of the Mindscape")
        self.db.add(root)
        self.db.commit()
        self.db.refresh(root)
        return MindNodeDTO.from_orm(root)

    def create_node(
        self,
        title: str,
        type: str = "concept",
        content: Optional[str] = None,
        tags: Optional[List[Any]] = None,
        appearance: Optional[Dict[str, Any]] = None,
        metadata_payload: Optional[Dict[str, Any]] = None,
        icon: Optional[str] = None,
        document_id: Optional[int] = None,
    ) -> MindNodeDTO:
        """Create a new thought atom."""
        if appearance is not None and not isinstance(appearance, dict):
            logger.warning("create_node: appearance must be dict; received %s", type(appearance))
            appearance = None
        if metadata_payload is not None and not isinstance(metadata_payload, dict):
            logger.warning("create_node: metadata_payload must be dict; received %s", type(metadata_payload))
            metadata_payload = None

        node_document_id = document_id
        if not node_document_id and metadata_payload and isinstance(metadata_payload, dict):
            node_document_id = metadata_payload.get("document_id")

        node = MindNode(
            title=title,
            type=type,
            content=content,
            tags=json.dumps(tags) if tags else "[]",
            appearance=json.dumps(appearance) if appearance else None,
            metadata_payload=json.dumps(metadata_payload) if metadata_payload else None,
            icon=icon,
            document_id=node_document_id,
        )
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)
        logger.info("Created MindNode id=%s title=%s", node.id, node.title)
        return MindNodeDTO.from_orm(node)
        
    def update_node(self, node_id: int, data: dict) -> Optional[MindNodeDTO]:
        """Update node details."""
        node = self.db.get(MindNode, node_id)
        if not node:
            logger.warning("update_node: node %s not found", node_id)
            return None
            
        if "title" in data:
            node.title = data["title"]
        if "content" in data:
            node.content = data["content"]
        if "tags" in data:
            cast(Any, node).tags = json.dumps(data["tags"])
        if "appearance" in data:
            appearance = data["appearance"]
            if isinstance(appearance, dict):
                cast(Any, node).appearance = json.dumps(appearance)
            else:
                logger.warning("update_node: appearance rejected for node %s (not dict)", node_id)
        if "metadata_payload" in data:
             meta = data["metadata_payload"]
             if isinstance(meta, dict):
                 cast(Any, node).metadata_payload = json.dumps(meta)
                 if "document_id" in meta:
                     cast(Any, node).document_id = meta.get("document_id")
             else:
                 logger.warning("update_node: metadata_payload rejected for node %s (not dict)", node_id)

        if "document_id" in data:
            cast(Any, node).document_id = data["document_id"]
             
             
        self.db.commit()
        self.db.refresh(node)
        logger.info("Updated MindNode id=%s", node.id)
        return MindNodeDTO.from_orm(node)

    def update_node_style(self, node_id: int, appearance: dict):
        node = self.db.get(MindNode, node_id)
        if node:
            if isinstance(appearance, dict):
                cast(Any, node).appearance = json.dumps(appearance)
                self.db.commit()
                logger.info("Updated MindNode style id=%s", node.id)
            else:
                logger.warning("update_node_style: appearance rejected for node %s (not dict)", node_id)
        else:
            logger.warning("update_node_style: node %s not found", node_id)

    def update_node_position(self, node_id: int, x: float, y: float):
        """Update just the position in the appearance blob."""
        node = self.db.get(MindNode, node_id)
        if node:
            try:
                appearance_raw = cast(Optional[str], node.appearance)
                data = json.loads(appearance_raw) if appearance_raw else {}
            except Exception as exc:
                logger.warning("update_node_position: invalid appearance JSON for node %s: %s", node_id, exc)
                data = {}
            
            data["pos"] = [round(x, 1), round(y, 1)]
            cast(Any, node).appearance = json.dumps(data)
            self.db.commit()
            logger.info("Persisted MindNode position id=%s pos=%s", node_id, data["pos"])
        else:
            logger.warning("update_node_position: node %s not found", node_id)
            
    def wipe_database(self):
        """NUCLEAR OPTION: Delete ALL mindscape data."""
        # 1. Delete all edges first (foreign keys)
        self.db.query(MindEdge).delete()
        # 2. Delete all nodes
        self.db.query(MindNode).delete()
        self.db.commit()
        logger.warning("Mindscape database wiped (edges and nodes deleted)")

    # --- Snapshots (Export/Import) ---
    def export_snapshot(self) -> Dict[str, Any]:
        """Export the full mindscape graph to a serializable dict."""
        nodes: List[Dict[str, Any]] = []
        for n in self.db.query(MindNode).all():
            try:
                appearance_raw = cast(Optional[str], n.appearance)
                appearance = json.loads(appearance_raw) if appearance_raw else None
            except Exception:
                appearance = None
            try:
                metadata_raw = cast(Optional[str], n.metadata_payload)
                metadata = json.loads(metadata_raw) if metadata_raw else None
            except Exception:
                metadata = None
            try:
                tags_raw = cast(Optional[str], n.tags)
                tags = json.loads(tags_raw) if tags_raw else []
            except Exception:
                tags = []

            nodes.append({
                "id": n.id,
                "title": n.title,
                "type": n.type,
                "content": n.content,
                "tags": tags,
                "appearance": appearance,
                "metadata_payload": metadata,
                "document_id": n.document_id,
                "icon": n.icon,
            })

        edges: List[Dict[str, Any]] = []
        for e in self.db.query(MindEdge).all():
            try:
                appearance_raw = cast(Optional[str], e.appearance)
                appearance = json.loads(appearance_raw) if appearance_raw else None
            except Exception:
                appearance = None
            edges.append({
                "id": e.id,
                "source_id": e.source_id,
                "target_id": e.target_id,
                "relation_type": e.relation_type,
                "appearance": appearance,
            })

        return {"nodes": nodes, "edges": edges}

    def import_snapshot(self, snapshot: Dict[str, Any], reset: bool = True):
        """Import a snapshot; optionally clears existing graph first."""
        if reset:
            self.wipe_database()

        node_id_map: Dict[int, int] = {}
        nodes = snapshot.get("nodes", []) or []
        edges = snapshot.get("edges", []) or []

        # Create nodes first
        for n in nodes:
            new_node = MindNode(
                title=n.get("title", "Untitled"),
                type=n.get("type", "concept"),
                content=n.get("content"),
                tags=json.dumps(n.get("tags", [])) if n.get("tags") is not None else "[]",
                appearance=json.dumps(n.get("appearance")) if n.get("appearance") else None,
                metadata_payload=json.dumps(n.get("metadata_payload")) if n.get("metadata_payload") else None,
                document_id=n.get("document_id"),
                icon=n.get("icon"),
            )
            self.db.add(new_node)
            self.db.flush()  # get id without full commit yet
            node_id_map[int(n.get("id", new_node.id))] = int(cast(int, new_node.id))

        self.db.commit()

        # Create edges with remapped ids
        for e in edges:
            src_old = e.get("source_id")
            tgt_old = e.get("target_id")
            src_new = node_id_map.get(src_old)
            tgt_new = node_id_map.get(tgt_old)
            if not src_new or not tgt_new:
                continue
            edge = MindEdge(
                source_id=src_new,
                target_id=tgt_new,
                relation_type=e.get("relation_type", MindEdgeType.PARENT.value),
                appearance=json.dumps(e.get("appearance")) if e.get("appearance") else None,
            )
            self.db.add(edge)

        self.db.commit()
        logger.info("Imported mindscape snapshot: %s nodes, %s edges", len(nodes), len(edges))

    def update_edge_style(self, edge_id: int, appearance: dict):
        edge = self.db.get(MindEdge, edge_id)
        if edge:
            if isinstance(appearance, dict):
                cast(Any, edge).appearance = json.dumps(appearance)
                self.db.commit()
                logger.info("Updated MindEdge style id=%s", edge.id)
            else:
                logger.warning("update_edge_style: appearance rejected for edge %s (not dict)", edge_id)
        else:
            logger.warning("update_edge_style: edge %s not found", edge_id)
            
    def get_edge(self, edge_id: int) -> Optional[MindEdgeDTO]:
        """Fetch a single edge."""
        edge = self.db.get(MindEdge, edge_id)
        return MindEdgeDTO.from_orm(edge) if edge else None

    def find_node_by_document_id(self, doc_id: int) -> Optional[MindNodeDTO]:
        """Find a node linked to a specific document."""
        # Prefer SQL JSON extraction when available (SQLite/JSON1).
        try:
            node = (
                self.db.query(MindNode)
                .filter(
                    MindNode.type == "document",
                    MindNode.document_id == doc_id,
                )
                .first()
            )
            if node:
                return MindNodeDTO.from_orm(node)

            node = (
                self.db.query(MindNode)
                .filter(
                    MindNode.type == "document",
                    func.json_extract(MindNode.metadata_payload, "$.document_id") == doc_id,
                )
                .first()
            )
            if node:
                return MindNodeDTO.from_orm(node)
        except Exception as exc:
            logger.warning("find_node_by_document_id: json_extract unavailable, falling back: %s", exc)

        # Fallback scan
        candidates = self.db.query(MindNode).filter(MindNode.type == "document").all()
        for node in candidates:
            metadata_raw = cast(Optional[str], node.metadata_payload)
            if not metadata_raw:
                continue
            try:
                meta = json.loads(metadata_raw)
            except json.JSONDecodeError:
                logger.warning("find_node_by_document_id: invalid metadata JSON on node %s", node.id)
                continue
            if isinstance(meta, dict) and meta.get("document_id") == doc_id:
                return MindNodeDTO.from_orm(node)
        return None

    def update_edge(self, edge_id: int, data: dict) -> Optional[MindEdgeDTO]:
        """Update edge details."""
        edge = self.db.get(MindEdge, edge_id)
        if not edge:
            logger.warning("update_edge: edge %s not found", edge_id)
            return None
            
        if "relation_type" in data:
            edge.relation_type = data["relation_type"]
        if "appearance" in data:
            cast(Any, edge).appearance = json.dumps(data["appearance"])
            
        self.db.commit()
        self.db.refresh(edge)
        logger.info("Updated MindEdge id=%s", edge.id)
        return MindEdgeDTO.from_orm(edge)

    def link_nodes(self, source_id: int, target_id: int, relation_type: str = "parent") -> MindEdgeDTO:
        """Link two nodes. If Parent, Source is Parent of Target."""
        edge = MindEdge(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type
        )
        self.db.add(edge)
        self.db.commit()
        self.db.refresh(edge)
        logger.info("Linked nodes %s -> %s type=%s edge_id=%s", source_id, target_id, relation_type, edge.id)
        return MindEdgeDTO.from_orm(edge)

    def get_local_graph(self, focus_id: int):
        """
        The Core "Brain" Algorithm.
        Fetches the 'Plex' centered on focus_id.
        Returns:
            focus_node: MindNodeDTO
            parents: List[Tuple[MindNodeDTO, MindEdgeDTO]]
            children: List[Tuple[MindNodeDTO, MindEdgeDTO]]
            jumps: List[Tuple[MindNodeDTO, MindEdgeDTO]]
            siblings: List[Tuple[MindNodeDTO, MindEdgeDTO]] (share a parent with focus)
        """
        focus_node = self.db.get(MindNode, focus_id)
        if not focus_node:
            return None, [], [], [], []

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
            src_id = int(cast(int, e.source_id))
            tgt_id = int(cast(int, e.target_id))
            other_id = tgt_id if src_id == focus_id else src_id
            other_node = self.db.get(MindNode, other_id)
            if other_node:
                jumps.append((MindNodeDTO.from_orm(other_node), MindEdgeDTO.from_orm(e)))

        # 4. Siblings (share any parent with focus)
        sibling_edges = []
        for parent_node, parent_edge in parents:
            sib_results = self.db.query(MindNode, MindEdge).join(
                MindEdge, MindNode.id == MindEdge.target_id
            ).filter(
                MindEdge.source_id == parent_node.id,
                MindEdge.relation_type == MindEdgeType.PARENT.value,
                MindEdge.target_id != focus_id,
            ).all()
            sibling_edges.extend(sib_results)

        siblings = [(MindNodeDTO.from_orm(n), MindEdgeDTO.from_orm(e)) for n, e in sibling_edges]

        return (
            MindNodeDTO.from_orm(focus_node),
            parents,
            children,
            jumps,
            siblings,
        )

    def delete_node(self, node_id: int) -> Optional[MindNodeDTO]:
        """
        Deletes a node and its edges.
        Returns a suggested 'Fallback' node to focus on (Parent > Child > Jump > Root).
        """
        node = self.db.get(MindNode, node_id)
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
                    src_id = int(cast(int, jump_edge.source_id))
                    tgt_id = int(cast(int, jump_edge.target_id))
                    fallback_id = src_id if tgt_id == node_id else tgt_id

        # Delete Associated Edges
        self.db.query(MindEdge).filter(
            or_(MindEdge.source_id == node_id, MindEdge.target_id == node_id)
        ).delete()
        
        # Delete Node
        self.db.delete(node)
        self.db.commit()
        
        # Fetch Fallback
        if fallback_id is not None:
            fallback = self.db.get(MindNode, fallback_id)
            return MindNodeDTO.from_orm(fallback) if fallback else None
        
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
