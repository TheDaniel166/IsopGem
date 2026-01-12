"""
History Entry — ADR-011

Represents a single entry in the calculation history.
Each entry captures the full state: Declaration, Verdict, Result, and timestamp.

Reference: wiki/01_blueprints/decisions/ADR-011_unified_geometry_viewer.md
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from canon_dsl.ast import Declaration
    from canon_dsl.findings import Verdict
    from canon_dsl.realizers import RealizeResult

logger = logging.getLogger(__name__)


@dataclass
class HistoryEntry:
    """
    Single entry in calculation history.
    
    Each entry represents a complete calculation cycle:
    Declaration → Validation → Realization
    
    Entries are immutable once created. Restoring an entry creates
    a new entry with the same declaration, preserving history.
    
    Attributes:
        declaration: The Canon declaration that was validated
        verdict: The validation verdict (pass/fail/warnings)
        result: The realization result (if validation passed)
        timestamp: When this entry was created
        signature: SHA-256 signature of the declaration (first 16 chars)
        notes: Optional user notes for this calculation
        custom_title: Optional user-defined title (overrides declaration title)
    """
    
    declaration: Any  # Declaration
    verdict: Any  # Verdict
    result: Optional[Any] = None  # RealizeResult
    timestamp: datetime = field(default_factory=datetime.now)
    signature: str = ""
    notes: str = ""
    custom_title: str = ""  # User-defined title for renaming
    
    def __post_init__(self):
        """Compute signature if not provided."""
        if not self.signature and self.declaration is not None:
            self.signature = self._compute_signature()
    
    def _compute_signature(self) -> str:
        """
        Compute SHA-256 signature from declaration.
        
        Only hashes the forms and their params (the actual geometry parameters),
        NOT metadata like title (which may contain timestamps).
        This ensures the same calculation always produces the same signature,
        allowing notes to persist across sessions.
        """
        try:
            from dataclasses import asdict
            # Only hash the forms data, not title/metadata which may vary
            forms = getattr(self.declaration, 'forms', [])
            if forms:
                forms_data = []
                for form in forms:
                    form_dict = asdict(form) if hasattr(form, '__dataclass_fields__') else {}
                    # Only include kind and params for deterministic signature
                    forms_data.append({
                        'kind': getattr(form, 'kind', ''),
                        'params': form_dict.get('params', {}),
                    })
                sig_str = json.dumps(forms_data, sort_keys=True, default=str)
            else:
                # Fallback: hash the whole declaration
                decl_dict = asdict(self.declaration)
                sig_str = json.dumps(decl_dict, sort_keys=True, default=str)
            return hashlib.sha256(sig_str.encode()).hexdigest()[:16]
        except Exception as e:
            logger.warning(f"Failed to compute signature: {e}")
            return hashlib.sha256(str(id(self.declaration)).encode()).hexdigest()[:16]
    
    @property
    def is_valid(self) -> bool:
        """Return True if the validation passed (no blocking findings)."""
        if self.verdict is None:
            return False
        return getattr(self.verdict, "ok", False)
    
    @property
    def has_warnings(self) -> bool:
        """Return True if validation passed but with warnings."""
        if self.verdict is None:
            return False
        if not self.is_valid:
            return False
        # Check if there are non-blocking findings
        findings = getattr(self.verdict, "findings", [])
        return len(findings) > 0
    
    @property
    def short_signature(self) -> str:
        """Return first 8 characters of signature for display."""
        return self.signature[:8] if self.signature else "????????"
    
    @property
    def form_type(self) -> str:
        """Return the primary form type from the declaration."""
        if self.declaration is None:
            return "Unknown"
        forms = getattr(self.declaration, "forms", [])
        if forms:
            return getattr(forms[0], "kind", "Unknown")
        return "Unknown"
    
    @property
    def title(self) -> str:
        """Return the custom title if set, otherwise the declaration title."""
        if self.custom_title:
            return self.custom_title
        if self.declaration is None:
            return "Untitled"
        return getattr(self.declaration, "title", "Untitled")
    
    @property
    def status_icon(self) -> str:
        """Return emoji icon for validation status."""
        if self.verdict is None:
            return "⏳"  # Pending
        if self.is_valid:
            if self.has_warnings:
                return "⚠"  # Warnings
            return "✓"  # Passed
        return "✗"  # Failed
    
    @property
    def status_text(self) -> str:
        """Return human-readable status text."""
        if self.verdict is None:
            return "Pending"
        if self.is_valid:
            if self.has_warnings:
                return "Passed with warnings"
            return "Passed"
        return "Failed"
    
    @property
    def time_string(self) -> str:
        """Return formatted timestamp for display."""
        return self.timestamp.strftime("%H:%M:%S")
    
    @property
    def date_string(self) -> str:
        """Return formatted date for display."""
        return self.timestamp.strftime("%Y-%m-%d")
    
    @property
    def full_timestamp(self) -> str:
        """Return full ISO timestamp."""
        return self.timestamp.isoformat()
    
    def get_findings_summary(self) -> str:
        """Return a summary of findings."""
        if self.verdict is None:
            return "No verdict"
        
        findings = getattr(self.verdict, "findings", [])
        if not findings:
            return "No findings"
        
        # Count by severity
        from collections import Counter
        severities = Counter()
        for f in findings:
            sev = getattr(f, "severity", None)
            if sev:
                severities[sev.name] += 1
            else:
                severities["UNKNOWN"] += 1
        
        parts = []
        for sev, count in severities.items():
            parts.append(f"{count} {sev.lower()}")
        
        return ", ".join(parts) if parts else "No findings"
    
    def get_canonical_params(self) -> dict[str, Any]:
        """Extract canonical parameters from the declaration."""
        if self.declaration is None:
            return {}
        
        forms = getattr(self.declaration, "forms", [])
        if forms:
            return dict(getattr(forms[0], "params", {}))
        return {}
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert to a JSON-serializable dictionary.
        
        For session export and persistence.
        """
        from dataclasses import asdict
        
        result_dict: dict[str, Any] = {
            "signature": self.signature,
            "timestamp": self.full_timestamp,
            "form_type": self.form_type,
            "title": self.title,
            "custom_title": self.custom_title,
            "status": self.status_text,
            "notes": self.notes,
        }
        
        # Include declaration summary
        if self.declaration is not None:
            try:
                result_dict["declaration"] = asdict(self.declaration)
            except Exception:
                result_dict["declaration"] = {"title": self.title}
        
        # Include verdict summary
        if self.verdict is not None:
            result_dict["verdict"] = {
                "ok": self.is_valid,
                "findings_count": len(getattr(self.verdict, "findings", [])),
                "summary": self.get_findings_summary(),
            }
        
        return result_dict
    
    def __str__(self) -> str:
        """String representation for debugging."""
        return f"HistoryEntry({self.short_signature} | {self.form_type} | {self.status_text} | {self.time_string})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"HistoryEntry(signature={self.short_signature!r}, "
            f"form_type={self.form_type!r}, "
            f"valid={self.is_valid}, "
            f"timestamp={self.timestamp!r})"
        )
