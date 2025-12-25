"""
The Librarian Service (Help System Backend).

Responsible for indexing the Akaschic Archive (Wiki) and serving content 
to the Help Window.
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class HelpTopic:
    """Represents a single help page or node."""
    id: str  # Relative path or specific ID
    title: str
    path: Path
    children: List['HelpTopic'] = field(default_factory=list)
    is_category: bool = False

class HelpService:
    """Archivist for the application documentation."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize the Librarian.
        
        Args:
            project_root: Path to project root. If None, auto-detects.
        """
        if project_root:
            self.root_path = project_root
        else:
            # Assume we are in src/shared/services, so go up 3 levels
            self.root_path = Path(__file__).parent.parent.parent.parent.resolve()
            
        self.wiki_path = self.root_path / "wiki"
        self._toc_tree: List[HelpTopic] = []
        self._search_index: Dict[str, str] = {} # term -> path
        
        logger.info(f"Librarian initialized. Wiki path: {self.wiki_path}")
        
    def index_content(self):
        """Scan the wiki directory and build the TOC."""
        if not self.wiki_path.exists():
            logger.warning(f"Wiki path not found: {self.wiki_path}")
            return
            
        self._toc_tree = self._scan_directory(self.wiki_path)
        logger.info("Akaschic Archive indexed successfully.")

    def _scan_directory(self, dir_path: Path) -> List[HelpTopic]:
        """Recursively scan directory for markdown files."""
        topics = []
        
        # Sort items: directories first, then files
        try:
            items = sorted(list(dir_path.iterdir()), key=lambda x: (not x.is_dir(), x.name))
        except OSError as e:
            logger.error(f"Error scanning directory {dir_path}: {e}")
            return []

        for item in items:
            if item.name.startswith('.'):
                continue
                
            if item.is_dir():
                # Check if directory has an index.md
                index_file = item / "index.md"
                title = item.name.replace("_", " ").title()
                
                # Recursively get children
                children = self._scan_directory(item)
                
                # If directory has content (children or an index file), add it as a topic
                if children or index_file.exists():
                    topic = HelpTopic(
                        id=str(item.relative_to(self.wiki_path)),
                        title=title,
                        path=index_file if index_file.exists() else item,
                        children=children,
                        is_category=True
                    )
                    topics.append(topic)
                    
            elif item.suffix.lower() == '.md':
                # Skip index.md as it's handled by the parent folder entry usually,
                # BUT if we want it to appear in the tree as a leaf, we can include it.
                # For now, let's treat regular .md files as topics.
                if item.name.lower() == "index.md":
                    continue
                    
                title = self._extract_title(item)
                topic = HelpTopic(
                    id=str(item.relative_to(self.wiki_path)),
                    title=title,
                    path=item,
                    is_category=False
                )
                topics.append(topic)
                
        return topics

    def _extract_title(self, file_path: Path) -> str:
        """Extract the first H1 header from a markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith('# '):
                        return line.strip()[2:].strip()
        except Exception:
            pass
        
        # Fallback to filename
        return file_path.stem.replace("_", " ").title()

    def get_toc(self) -> List[HelpTopic]:
        """Return the calculated Table of Contents."""
        if not self._toc_tree:
            self.index_content()
        return self._toc_tree

    def search(self, query: str) -> List[Tuple[str, str, str]]:
        """
        Simple text search.
        
        Returns:
            List of (title, relative_path, snippet)
        """
        results = []
        query = query.lower()
        
        for file_path in self.wiki_path.rglob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if query in content.lower():
                    title = self._extract_title(file_path)
                    rel_path = str(file_path.relative_to(self.wiki_path))
                    
                    # Create snippet
                    idx = content.lower().find(query)
                    start = max(0, idx - 40)
                    end = min(len(content), idx + 60)
                    snippet = "..." + content[start:end].replace("\n", " ") + "..."
                    
                    results.append((title, rel_path, snippet))
            except Exception:
                continue
                
        return results

    def get_content(self, relative_path: str) -> str:
        """Get the HTML content for a topic (Markdown rendered)."""
        full_path = self.wiki_path / relative_path
        if full_path.exists() and full_path.is_file():
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                return f"# Error\nCould not read file: {e}"
        return "# Not Found\nDocument does not exist."
