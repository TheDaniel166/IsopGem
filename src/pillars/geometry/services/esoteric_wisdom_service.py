"""
The Esoteric Wisdom Service (The Oracle of Sacred Forms).

Provides indexed access to the sacred meanings and esoteric descriptions
of geometric forms, following the HelpService pattern.
"""
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class WisdomTopic:
    """Represents a single esoteric entry for a geometric form."""
    id: str                    # Shape name (lookup key)
    title: str                 # Esoteric title
    category: str              # Parent category (Circles, Triangles, etc.)
    keywords: List[str] = field(default_factory=list)
    has_stellations: bool = False


# Category mapping for organizing the TOC
CATEGORY_ORDER = [
    ("Circles & Curves", ["Circle", "Oval (Ellipse)", "Annulus", "Crescent", 
                          "Vesica Piscis", "Rose (Rhodonea Curve)"]),
    ("Triangles", ["Equilateral Triangle", "Right Triangle", "Isosceles Triangle",
                   "Scalene Triangle", "Acute Triangle", "Obtuse Triangle",
                   "Golden Triangle", "30-60-90 Triangle", "Heronian Triangle"]),
    ("Quadrilaterals", ["Square", "Rectangle", "Parallelogram", "Rhombus",
                        "Trapezoid", "Isosceles Trapezoid", "Kite", "Deltoid / Dart",
                        "Cyclic Quadrilateral", "Tangential Quadrilateral", 
                        "Bicentric Quadrilateral"]),
    ("Polygons", ["Regular Pentagon (5-gon)", "Regular Hexagon (6-gon)",
                  "Regular Heptagon (7-gon)", "Regular Octagon (8-gon)",
                  "Regular Nonagon (9-gon)", "Regular Decagon (10-gon)",
                  "Regular Hendecagon (11-gon)", "Regular Dodecagon (12-gon)"]),
    ("Sacred Geometry", ["Vault of Hestia", "Seed of Life"]),
    ("Pyramids", ["Square Pyramid", "Rectangular Pyramid", "Equilateral Triangular Pyramid",
                  "Pentagonal Pyramid", "Hexagonal Pyramid", "Heptagonal Pyramid",
                  "Square Frustum", "Pentagonal Frustum", "Hexagonal Frustum", 
                  "Golden Pyramid"]),
    ("Prisms", ["Prismatic Frustum", "Gyroelongated Square Prism"]),
    ("Antiprisms", ["Triangular Antiprism", "Square Antiprism", "Pentagonal Antiprism",
                    "Hexagonal Antiprism", "Heptagonal Antiprism", "Octagonal Antiprism"]),
    ("Platonic Solids", ["Tetrahedron", "Cube", "Octahedron", "Dodecahedron", "Icosahedron"]),
    ("Archimedean Solids", ["Cuboctahedron", "Truncated Tetrahedron", "Truncated Cube",
                            "Truncated Octahedron", "Rhombicuboctahedron",
                            "Truncated Cuboctahedron", "Icosidodecahedron",
                            "Truncated Dodecahedron", "Truncated Icosahedron",
                            "Truncated Icosidodecahedron", "Rhombicosidodecahedron",
                            "Snub Cube", "Snub Dodecahedron"]),
    ("Curves & Surfaces", ["Sphere", "Cylinder", "Cone", "Torus", "Torus Knot"]),
]


class EsotericWisdomService:
    """The Oracle of Sacred Forms - provides access to esoteric geometry knowledge."""
    
    def __init__(self):
        """Initialize the Wisdom Service."""
        # Lazy import to avoid circular dependency
        from ..ui.esoteric_definitions import ESOTERIC_DEFINITIONS
        self._definitions = ESOTERIC_DEFINITIONS
        self._toc: List[Tuple[str, List[WisdomTopic]]] = []
        self._index_built = False
        logger.info("Esoteric Wisdom Service initialized.")
    
    def _build_index(self):
        """Build the Table of Contents from the definitions."""
        if self._index_built:
            return
        
        self._toc = []
        for category_name, shape_names in CATEGORY_ORDER:
            topics = []
            for shape_name in shape_names:
                if shape_name in self._definitions:
                    defn = self._definitions[shape_name]
                    topic = WisdomTopic(
                        id=shape_name,
                        title=defn.get('title', shape_name),
                        category=category_name,
                        keywords=defn.get('keywords', []),
                        has_stellations='stellations' in defn
                    )
                    topics.append(topic)
            if topics:
                self._toc.append((category_name, topics))
        
        self._index_built = True
        logger.info(f"Wisdom index built: {sum(len(t) for _, t in self._toc)} entries in {len(self._toc)} categories.")
    
    def get_toc(self) -> List[Tuple[str, List[WisdomTopic]]]:
        """
        Get the Table of Contents organized by category.
        
        Returns:
            List of (category_name, list of WisdomTopics)
        """
        self._build_index()
        return self._toc
    
    def get_all_topics(self) -> List[WisdomTopic]:
        """
        Get flat list of all topics.
        
        Returns:
            List of all WisdomTopics
        """
        self._build_index()
        topics = []
        for _, category_topics in self._toc:
            topics.extend(category_topics)
        return topics
    
    def search(self, query: str) -> List[Tuple[str, str, str]]:
        """
        Search across all esoteric definitions.
        
        Args:
            query: Search term
            
        Returns:
            List of (shape_name, title, snippet)
        """
        results = []
        query_lower = query.lower()
        
        for shape_name, defn in self._definitions.items():
            # Search in various fields
            searchable_text = ""
            
            # Title and summary
            searchable_text += defn.get('title', '') + " "
            searchable_text += defn.get('summary', '') + " "
            
            # Keywords
            keywords = defn.get('keywords', [])
            searchable_text += " ".join(keywords) + " "
            
            # Correspondences
            correspondences = defn.get('correspondences', {})
            for k, v in correspondences.items():  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]
                searchable_text += f"{k} {v} "
            
            # Meditation
            searchable_text += defn.get('meditation', '') + " "
            
            # Check for match
            if query_lower in searchable_text.lower():
                title = defn.get('title', shape_name)
                summary = defn.get('summary', '')
                
                # Create snippet
                idx = summary.lower().find(query_lower)  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]
                if idx >= 0:
                    start = max(0, idx - 30)
                    end = min(len(summary), idx + 50)
                    snippet = "..." + summary[start:end] + "..."  # type: ignore[reportArgumentType, reportOperatorIssue, reportUnknownVariableType]
                else:
                    snippet = summary[:80] + "..." if len(summary) > 80 else summary  # type: ignore[reportArgumentType, reportOperatorIssue, reportUnknownVariableType]
                
                results.append((shape_name, title, snippet))
        
        return results
    
    def get_content(self, shape_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the full esoteric content for a shape.
        
        Args:
            shape_name: The shape lookup key
            
        Returns:
            The full definition dict or None if not found
        """
        return self._definitions.get(shape_name)
    
    def get_shape_names(self) -> List[str]:
        """Get list of all shape names with esoteric definitions."""
        return list(self._definitions.keys())


# Singleton instance
_service_instance: Optional[EsotericWisdomService] = None

def get_esoteric_wisdom_service() -> EsotericWisdomService:
    """Get the singleton Esoteric Wisdom Service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = EsotericWisdomService()
    return _service_instance
