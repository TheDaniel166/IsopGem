"""Utilities for parsing documents into verses by number."""
import re
from typing import List, Dict, Any, Optional


def parse_verses(text: str, allow_inline: bool = True) -> List[Dict[str, Any]]:
    """Parse the given plain text into numbered verses.

    Recognizes lines that start with an Arabic numeral followed by optional punctuation.
    Falls back to header-based parsing if no numeric verses are found.
    Returns a list of dicts {number, start, end, text}
    """
    if not text:
        return []

    # Try numeric parsing first
    verses = _parse_numeric_verses(text, allow_inline)
    
    # Fallback to header-based parsing if no numeric verses found
    if not verses:
        verses = parse_by_headers(text)
    
    return verses


def _parse_numeric_verses(text: str, allow_inline: bool = True) -> List[Dict[str, Any]]:
    verses: List[Dict[str, Any]] = []

    if not text:
        return verses

    # Pattern matches a numeric verse marker that may be at the start of the string,
    # at the start of a line, or following whitespace (inline numbering).
    # We'll capture the number in group 1 and use m.end() to locate where the verse text begins.
    # Match if the digit is at the start of the document, at a line start,
    # or follows whitespace or common sentence-ending punctuation.
    # Find all candidate numbers using a permissive pattern so we can apply heuristics later
    pattern = re.compile(r"(\d+)\s*(?:[\.:\)\-]?\s*)")
    candidate_matches = list(pattern.finditer(text))

    if not candidate_matches:
        return verses

    # Build candidate list: (num, start, end, match)
    candidates = []
    for m in candidate_matches:
        try:
            num = int(m.group(1))
        except Exception:
            continue
        candidates.append({
            'num': num,
            'start': m.start(),
            'end': m.end(),
            'match': m,
        })

    if not candidates:
        return verses

    # Partition: markers at beginning of string or start of line are strong indicators
    line_start_candidates = []
    inline_candidates = []
    for c in candidates:
        s = c['start']
        is_line_start = s == 0 or text[s - 1] in {'\n', '\r'}
        c['line_start'] = is_line_start
        if is_line_start:
            line_start_candidates.append(c)
        else:
            inline_candidates.append(c)

    # Further heuristics for inline candidates:
    # - If the first non-space char after the marker is uppercase (likely start of sentence), accept
    # - Or, if the candidate participates in a sequence with adjacent numbers (e.g., 1,2,3), accept
    def next_non_space_char(s_idx: int) -> Optional[str]:
        """
        Next non space char logic.
        
        Args:
            s_idx: Description of s_idx.
        
        Returns:
            Result of next_non_space_char operation.
        """
        idx = s_idx
        while idx < len(text) and text[idx].isspace():
            idx += 1
        if idx < len(text):
            return text[idx]
        return None

    # Build number->candidate index map
    num_map = {c['num']: c for c in candidates}
    accepted_inline = []
    for c in inline_candidates:
        # Check char following marker for uppercase letter
        nxt = next_non_space_char(c['end'])
        if nxt and nxt.isalpha() and nxt.isupper():
            accepted_inline.append(c)
            continue
        # Accept if sequential neighbors exist (num+1 or num-1)
        if c['num'] - 1 in num_map or c['num'] + 1 in num_map:
            accepted_inline.append(c)

    if allow_inline:
        accepted = sorted(line_start_candidates + accepted_inline, key=lambda x: x['start'])
    else:
        accepted = sorted(line_start_candidates, key=lambda x: x['start'])

    if not accepted:
        return verses

    # Convert accepted candidates to verses
    for i, c in enumerate(accepted):
        text_start = c['end']
        end = accepted[i + 1]['start'] if i + 1 < len(accepted) else len(text)
        verse_text = text[text_start:end].strip()
        verses.append({
            'number': c['num'],
            'start': text_start,
            'end': end,
            'text': verse_text,
            'marker_start': c['start'],
            'marker_end': c['end'],
            'is_line_start': c.get('line_start', False),
            'is_inline': not c.get('line_start', False),
        })

    return verses


def _is_likely_header(line: str) -> bool:
    """Heuristic to detect if a line is likely a section header.
    
    Headers are typically:
    - Short (< 50 chars)
    - Standalone (not part of a long paragraph)
    - Capitalized, title-case, or non-Latin script
    
    Args:
        line: The line to evaluate
        
    Returns:
        True if line appears to be a header
    """
    stripped = line.strip()
    
    # Empty lines are not headers
    if not stripped:
        return False
    
    # Very short lines (1-2 words) are likely headers
    word_count = len(stripped.split())
    if word_count <= 2 and len(stripped) < 50:
        # Check if it's capitalized or non-Latin
        if stripped[0].isupper() or not stripped[0].isascii():
            return True
    
    # Lines with non-Latin scripts (Greek, Hebrew, Arabic, etc.)
    # that are reasonably short
    if len(stripped) < 80:
        # Check for Unicode ranges:
        # Greek: 0x0370-0x03FF
        # Hebrew: 0x0590-0x05FF
        # Arabic: 0x0600-0x06FF
        for char in stripped:
            code = ord(char)
            if (0x0370 <= code <= 0x03FF or  # Greek
                0x0590 <= code <= 0x05FF or  # Hebrew
                0x0600 <= code <= 0x06FF):   # Arabic
                return True
    
    return False


def parse_by_headers(text: str) -> List[Dict[str, Any]]:
    """Fallback parser for documents with section headers instead of numbers.
    
    Detects standalone header lines and treats each header+paragraph pair
    as a pseudo-verse, numbered sequentially (1, 2, 3...).
    
    Args:
        text: Document text to parse
        
    Returns:
        List of verse dicts with sequential numbering
    """
    verses: List[Dict[str, Any]] = []
    
    if not text:
        return verses
    
    lines = text.split('\n')
    
    # Find potential headers
    header_indices = []
    for i, line in enumerate(lines):
        if _is_likely_header(line):
            header_indices.append(i)
    
    # If we found no headers, return empty
    if not header_indices:
        return verses
    
    # Extract header+content pairs
    verse_num = 1
    for i, header_idx in enumerate(header_indices):
        # Determine where this section ends (next header or end of doc)
        next_header_idx = header_indices[i + 1] if i + 1 < len(header_indices) else len(lines)
        
        # Extract header and content
        header = lines[header_idx].strip()
        content_lines = lines[header_idx + 1:next_header_idx]
        content = '\n'.join(content_lines).strip()
        
        # Skip if no content (header at end of doc)
        if not content:
            continue
        
        # Calculate character positions in original text
        chars_before_header = sum(len(lines[j]) + 1 for j in range(header_idx))  # +1 for \n
        header_start = chars_before_header
        header_end = header_start + len(lines[header_idx])
        
        # Content starts after the header line
        content_start = header_end + 1  # +1 for newline after header
        
        # Calculate end of content
        chars_in_section = sum(len(lines[j]) + 1 for j in range(header_idx + 1, next_header_idx))
        content_end = content_start + chars_in_section
        
        # CRITICAL: Include header in the verse text so it appears in interlinear view
        # and gets processed by language detection
        full_text = f"{header}\n{content}"
        
        verses.append({
            'number': verse_num,
            'start': header_start,  # Start at the header, not after it
            'end': content_end,
            'text': full_text,  # Include header + content
            'marker_start': header_start,
            'marker_end': header_end,
            'is_line_start': True,
            'is_inline': False,
            'header': header,  # Still store header separately as metadata
        })
        
        verse_num += 1
    
    return verses