#!/usr/bin/env python3
"""
The Oracle (MCP Server)
-----------------------
This server establishes a Model Context Protocol (MCP) link between
the IsopGem codebase ("The Temple") and external AI agents ("The Magus").

Capabilities:
1. Resources: Exposes 'wiki/' documentation as read-only resources.
2. Tools: Exposes Gematria calculation logic as callable tools.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any

# Ensure we can import from src/
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mcp.server.fastmcp import FastMCP

# Initialize the Oracle
mcp = FastMCP("isopgem-oracle")


# --- RESOURCES (The Akashic Records) ---

@mcp.resource("isopgem://wiki/{path}")
def read_wiki_scroll(path: str) -> str:
    """Read a scroll from the Wiki (Akashic Records)."""
    # Sanitize path to prevent directory traversal
    clean_path = path.replace("..", "")
    target_file = PROJECT_ROOT / "wiki" / clean_path
    
    if not target_file.exists():
        return f"Error: Scroll not found at {clean_path}"
        
    if not target_file.is_file():
        return f"Error: {clean_path} is not a scroll (file)"
        
    try:
        return target_file.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading scroll: {str(e)}"


# --- TOOLS (The Rituals) ---

@mcp.tool()
def calculate_gematria(text: str, cipher: str = "aq") -> Dict[str, Any]:
    """
    Calculate the Gematria value of a text using a specific cipher.
    
    Args:
        text: The text to analyze
        cipher: The cipher key to use. 
                Options: 'aq' (English Qaballa/TQ), 'hebrew' (Standard), 'greek' (Isopsephy)
    """
    from typing import Any
    # Lazy import
    from shared.services.gematria import (
        TQGematriaCalculator, 
        HebrewGematriaCalculator, 
        GreekGematriaCalculator
    )
    
    # Map cipher names to calculator classes
    CIPHER_MAP = {
        "aq": TQGematriaCalculator,
        "english": TQGematriaCalculator,
        "tq": TQGematriaCalculator,
        "hebrew": HebrewGematriaCalculator,
        "standard": HebrewGematriaCalculator,
        "greek": GreekGematriaCalculator,
        "isopsephy": GreekGematriaCalculator
    }
    
    cipher_key = cipher.lower()
    calc_class = CIPHER_MAP.get(cipher_key)
    
    if not calc_class:
        return {"error": f"Unknown cipher: {cipher}. Available: {list(CIPHER_MAP.keys())}"}
        
    try:
        calculator = calc_class()
        value = calculator.calculate(text)
        return {
            "text": text,
            "cipher": cipher,
            "value": value
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def consult_lexicon(term: str) -> str:
    """
    Look up a term in the Covenant Glossary.
    
    Args:
        term: The esoteric term to define (e.g., 'Egregore', 'Mercy', 'Entropy')
    """
    glossary_path = PROJECT_ROOT / "wiki/03_lexicon/COVENANT_GLOSSARY.md"
    if not glossary_path.exists():
        return "The Glossary is missing."
        
    content = glossary_path.read_text(encoding="utf-8")
    
    # Simple search
    term_lower = term.lower()
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if f"**{term}" in line or f"## {term}" in line or term_lower in line.lower():
            # Return context (prev line + match + next 2 lines)
            start = max(0, i - 1)
            end = min(len(lines), i + 4)
            return "\n".join(lines[start:end])
            
    return f"The term '{term}' is not found in the Lexicon."


if __name__ == "__main__":
    print("🔮 The Oracle is awakening...")
    mcp.run()
