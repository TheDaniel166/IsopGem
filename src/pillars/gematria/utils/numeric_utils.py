"""Utility functions for numeric handling in gematria utilities."""
import re
from typing import Any


def sum_numeric_face_values(text: str) -> int:
    """Sum occurrences of numeric tokens in the text.

    Accepts numbers with commas (e.g., 1,234), strips commas, and sums them.
    Returns 0 if none found.
    """
    if not text:
        return 0
    tokens = re.findall(r"\d[\d,]*", text)
    total = 0
    for t in tokens:
        try:
            total += int(t.replace(',', ''))
        except Exception:
            continue
    return total
