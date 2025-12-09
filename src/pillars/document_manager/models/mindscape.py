
"""
Mindscape 3.0 Data Model
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from shared.database import Base
from datetime import datetime
import enum

class MindEdgeType(str, enum.Enum):
    PARENT = "parent"  # Source is Parent of Target
    JUMP = "jump"      # Associative link (bidirectional conceptually)

class MindNode(Base):
    __tablename__ = "mind_nodes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    
    # Type of node: 'concept', 'document', 'url', 'person', 'tag'
    type = Column(String, default="concept") 
    
    # Future-Proof Schema
    content = Column(Text, nullable=True)         # Markdown/HTML notes
    tags = Column(Text, nullable=True)            # JSON list of strings
    appearance = Column(Text, nullable=True)      # JSON dict for visual styling
    metadata_payload = Column(Text, nullable=True)  # JSON dict for esoteric data
    
    # Icon resource name or emoji (Legacy, but useful top-level)
    icon = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MindEdge(Base):
    __tablename__ = "mind_edges"

    id = Column(Integer, primary_key=True, index=True)
    
    source_id = Column(Integer, ForeignKey("mind_nodes.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("mind_nodes.id"), nullable=False)
    
    # 'parent' means source->target is Parent->Child
    # 'jump' means source<->target are associated
    relation_type = Column(String, default=MindEdgeType.PARENT.value)
    
    # Edge Styling
    appearance = Column(Text, nullable=True)      # JSON dict for edge styling
    
    created_at = Column(DateTime, default=datetime.utcnow)
