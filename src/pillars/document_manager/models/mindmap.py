"""Mindmap models for multi-map 3D mindscape."""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, Index
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from shared.database import Base


class Mindmap(Base):
    __tablename__ = "mindmaps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    nodes = relationship("MindmapNode", cascade="all, delete-orphan", backref="mindmap")
    edges = relationship("MindmapEdge", cascade="all, delete-orphan", backref="mindmap")


class MindmapNode(Base):
    __tablename__ = "mindmap_nodes"

    id = Column(Integer, primary_key=True, index=True)
    map_id = Column(Integer, ForeignKey("mindmaps.id"), index=True, nullable=False)

    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    tags = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    color = Column(String, nullable=True)  # Hex string, e.g., "#3b82f6"
    shape = Column(String, nullable=True)  # e.g., "cube", "tetra", "octa", "dodeca", "icosa", "sphere"

    x = Column(Float, default=0.0)
    y = Column(Float, default=0.0)
    z = Column(Float, default=0.0)
    pinned = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MindmapEdge(Base):
    __tablename__ = "mindmap_edges"

    id = Column(Integer, primary_key=True, index=True)
    map_id = Column(Integer, ForeignKey("mindmaps.id"), index=True, nullable=False)

    source_id = Column(Integer, ForeignKey("mindmap_nodes.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("mindmap_nodes.id"), nullable=False)

    color = Column(String, nullable=True)
    width = Column(Float, default=2.0)
    style = Column(String, default="solid")  # "solid" | "dashed"

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Helpful indexes for loading maps
Index("idx_mindmap_nodes_map", MindmapNode.map_id)
Index("idx_mindmap_edges_map", MindmapEdge.map_id)
