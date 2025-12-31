"""
Mermaid Syntax Highlighter.
Provides color-coded syntax highlighting for Mermaid diagram code.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import (
    QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QTextDocument
)
import re


class MermaidSyntaxHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter for Mermaid diagram syntax.
    Highlights keywords, arrows, strings, comments, and node definitions.
    """
    
    def __init__(self, document: QTextDocument):
        super().__init__(document)
        self._setup_formats()
        self._setup_rules()
    
    def _setup_formats(self):
        """Define text formats for different syntax elements."""
        # Keywords (diagram types)
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#7c3aed"))  # Violet
        self.keyword_format.setFontWeight(QFont.Weight.Bold)
        
        # Subgraph/Section keywords
        self.section_format = QTextCharFormat()
        self.section_format.setForeground(QColor("#0891b2"))  # Cyan
        self.section_format.setFontWeight(QFont.Weight.Bold)
        
        # Arrows and connections
        self.arrow_format = QTextCharFormat()
        self.arrow_format.setForeground(QColor("#ea580c"))  # Orange
        self.arrow_format.setFontWeight(QFont.Weight.Bold)
        
        # Strings (quoted text)
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#16a34a"))  # Green
        
        # Node IDs
        self.node_format = QTextCharFormat()
        self.node_format.setForeground(QColor("#2563eb"))  # Blue
        
        # Labels in brackets/parens
        self.label_format = QTextCharFormat()
        self.label_format.setForeground(QColor("#0f172a"))  # Dark
        
        # Comments
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#94a3b8"))  # Gray
        self.comment_format.setFontItalic(True)
        
        # Numbers
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#c026d3"))  # Fuchsia
        
        # Directives (%%{...}%%)
        self.directive_format = QTextCharFormat()
        self.directive_format.setForeground(QColor("#64748b"))  # Slate
        self.directive_format.setFontItalic(True)
    
    def _setup_rules(self):
        """Define regex patterns for syntax elements."""
        self.rules = []
        
        # Diagram type keywords
        keywords = [
            r'\bgraph\b', r'\bflowchart\b', r'\bsequenceDiagram\b',
            r'\bclassDiagram\b', r'\bstateDiagram\b', r'\bstateDiagram-v2\b',
            r'\berDiagram\b', r'\bpie\b', r'\bgantt\b', r'\bmindmap\b',
            r'\btimeline\b', r'\bgitGraph\b', r'\bc4Context\b',
            r'\bTD\b', r'\bTB\b', r'\bBT\b', r'\bLR\b', r'\bRL\b',
        ]
        for pattern in keywords:
            self.rules.append((re.compile(pattern), self.keyword_format))
        
        # Section/subgraph keywords
        sections = [
            r'\bsubgraph\b', r'\bend\b', r'\bsection\b', r'\bparticipant\b',
            r'\bactor\b', r'\bloop\b', r'\balt\b', r'\belse\b', r'\bopt\b',
            r'\bpar\b', r'\band\b', r'\brect\b', r'\bnote\b', r'\bclass\b',
            r'\bstate\b', r'\b\[\*\]\b', r'\bdirection\b', r'\btitle\b',
            r'\bdateFormat\b', r'\baxisFormat\b', r'\broot\b',
        ]
        for pattern in sections:
            self.rules.append((re.compile(pattern, re.IGNORECASE), self.section_format))
        
        # Arrows and connections
        arrows = [
            r'-->',      # Standard arrow
            r'---',      # Line
            r'-\.-',     # Dotted
            r'--\>',     # Alternate arrow
            r'->>',      # Async arrow
            r'->',       # Simple arrow
            r'<-->',     # Bidirectional
            r'==\>',     # Thick arrow
            r'~~~',      # Wavy
            r'\|\|--o\{', # ER one-to-many
            r'\|\|--\|\{', # ER one-to-one
            r'\|\|--\|\|', # ER
            r'<\|--',    # Class diagram
            r'--\*',     # Composition
            r'--o',      # Aggregation
            r':\s*\w+',  # Relation labels
        ]
        for pattern in arrows:
            self.rules.append((re.compile(pattern), self.arrow_format))
        
        # Strings (double and single quoted)
        self.rules.append((re.compile(r'"[^"]*"'), self.string_format))
        self.rules.append((re.compile(r"'[^']*'"), self.string_format))
        
        # Labels in brackets/braces/parens
        self.rules.append((re.compile(r'\[[^\]]*\]'), self.label_format))
        self.rules.append((re.compile(r'\{[^}]*\}'), self.label_format))
        self.rules.append((re.compile(r'\([^)]*\)'), self.label_format))
        
        # Comments (%% ... or %% to end of line)
        self.rules.append((re.compile(r'%%.*$', re.MULTILINE), self.comment_format))
        
        # Numbers
        self.rules.append((re.compile(r'\b\d+\.?\d*\b'), self.number_format))
        
        # Directives
        self.rules.append((re.compile(r'%%\{.*?\}%%', re.DOTALL), self.directive_format))
    
    def highlightBlock(self, text: str):
        """Apply syntax highlighting to a block of text."""
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)
