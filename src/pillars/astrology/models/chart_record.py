"""SQLAlchemy models for persisting astrology charts."""
from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from shared.database import Base


chart_category_links = Table(
    "chart_category_links",
    Base.metadata,
    Column("chart_id", ForeignKey("astrology_charts.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", ForeignKey("chart_categories.id", ondelete="CASCADE"), primary_key=True),
)

chart_tag_links = Table(
    "chart_tag_links",
    Base.metadata,
    Column("chart_id", ForeignKey("astrology_charts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("chart_tags.id", ondelete="CASCADE"), primary_key=True),
)


class AstrologyChart(Base):
    """
    Astrology Chart class definition.
    
    """
    __tablename__ = "astrology_charts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    chart_type = Column(String(64), default="Radix", nullable=False)
    include_svg = Column(Boolean, default=True)
    house_system = Column(String(8), nullable=True)

    event_timestamp = Column(DateTime(timezone=True), nullable=False)
    timezone_offset = Column(Float, nullable=False)
    location_label = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation = Column(Float, nullable=True)

    request_payload = Column(JSON, nullable=False)
    result_payload = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    categories = relationship(
        "ChartCategory",
        secondary=chart_category_links,
        back_populates="charts",
        lazy="joined",
    )
    tags = relationship(
        "ChartTag",
        secondary=chart_tag_links,
        back_populates="charts",
        lazy="joined",
    )


class ChartCategory(Base):
    """
    Chart Category class definition.
    
    """
    __tablename__ = "chart_categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, nullable=False, index=True)

    charts = relationship(
        "AstrologyChart",
        secondary=chart_category_links,
        back_populates="categories",
    )


class ChartTag(Base):
    """
    Chart Tag class definition.
    
    """
    __tablename__ = "chart_tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, nullable=False, index=True)

    charts = relationship(
        "AstrologyChart",
        secondary=chart_tag_links,
        back_populates="tags",
    )