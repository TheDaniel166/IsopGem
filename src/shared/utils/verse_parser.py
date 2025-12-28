"""Utilities for parsing documents into verses by number."""
import re
from typing import List, Dict, Any, Optional


def parse_verses(text: str, allow_inline: bool = True) -> List[Dict[str, Any]]:
    """Parse the given plain text into numbered verses.

    Recognizes lines that start with an Arabic numeral followed by optional punctuation.
    Returns a list of dicts {number, start, end, text}
    """
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