"""Domain models for Chart Interpretation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass(slots=True)
class RichInterpretationContent:
    """Rich structured content for an interpretation."""
    text: str  # Main body text (backward compatibility)
    archetype: Optional[str] = None
    essence: Optional[str] = None
    shadow: Optional[str] = None
    gift: Optional[str] = None
    alchemical_process: Optional[str] = None
    keywords: List[str] = field(default_factory=list)

@dataclass(slots=True)
class InterpretationSegment:
    """A single segment of an interpretation report."""
    title: str
    content: RichInterpretationContent
    tags: List[str] = field(default_factory=list)
    weight: float = 1.0

@dataclass(slots=True)
class InterpretationReport:
    """A complete interpretation report for a chart."""
    chart_name: str
    segments: List[InterpretationSegment] = field(default_factory=list)

    def add_segment(self, title: str, content: RichInterpretationContent | str, tags: Optional[List[str]] = None, weight: float = 1.0) -> None:
        """Add a segment to the report."""
        if tags is None:
            tags = []
            
        if isinstance(content, str):
            rich_content = RichInterpretationContent(text=content)
        else:
            rich_content = content
            
        self.segments.append(InterpretationSegment(title, rich_content, tags, weight))

    def to_markdown(self) -> str:
        """Render the report as a Markdown string."""
        md = [f"# Interpretation for {self.chart_name}"]
        for segment in self.segments:
            md.append(f"## {segment.title}")
            c = segment.content
            
            if c.archetype:
                md.append(f"**Archetype:** {c.archetype}")
            
            md.append(c.text)
            
            if c.essence:
                md.append(f"\n**Essence:** {c.essence}")
            if c.shadow:
                md.append(f"**Shadow:** {c.shadow}")
            if c.gift:
                md.append(f"**Gift:** {c.gift}")
            
            md.append("")
        return "\n".join(md)
