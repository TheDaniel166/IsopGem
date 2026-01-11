"""
Canon DSL — Findings and Verdict structures.

This module defines the structures for validation results,
including findings (individual issues) and verdicts (overall result).

Reference: Hermetic Geometry Canon v1.0, Article IX
Reference: Canon DSL Implementation Spec v0.2, Section 6
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Severity(Enum):
    """
    Severity levels for Canon findings.
    
    FATAL: Cannot realize; fundamental Canon violation
    ERROR: Invalid unless overridden (treated as FATAL in v0.2)
    WARN: Admissible but questionable/incomplete declaration
    INFO: Advisory information
    """
    
    FATAL = "fatal"
    ERROR = "error"
    WARN = "warn"
    INFO = "info"
    
    def blocks_realization(self) -> bool:
        """Returns True if this severity prevents realization."""
        return self in (Severity.FATAL, Severity.ERROR)


@dataclass(frozen=True)
class Finding:
    """
    A single validation finding.
    
    Findings represent issues discovered during Canon validation.
    Each finding references specific Canon articles and provides
    actionable information.
    
    Attributes:
        severity: How serious this finding is
        rule_id: Stable rule identifier (e.g., "CANON-V-ORIENTATION-REQUIRED")
        message: Human-readable description
        articles: Canon article references (e.g., ["V.4.5", "XII.6"])
        subject_ids: Form/relation/trace IDs involved
        suggested_fix: Optional guidance for resolution
        context: Additional context data
    
    Canon References:
        - Findings cite specific Canon articles to enable traceability
    """
    
    severity: Severity
    rule_id: str
    message: str
    articles: list[str] = field(default_factory=list)
    subject_ids: list[str] = field(default_factory=list)
    suggested_fix: Optional[str] = None
    context: dict = field(default_factory=dict)
    
    def __str__(self) -> str:
        articles_str = ", ".join(self.articles) if self.articles else "—"
        subjects_str = ", ".join(self.subject_ids) if self.subject_ids else "—"
        return (
            f"[{self.severity.value.upper()}] {self.rule_id}\n"
            f"  Message: {self.message}\n"
            f"  Canon Refs: {articles_str}\n"
            f"  Subjects: {subjects_str}"
        )


@dataclass
class Verdict:
    """
    The result of Canon validation.
    
    A Verdict aggregates all findings and provides an overall
    determination of whether realization may proceed.
    
    Attributes:
        ok: True if realization may proceed (no FATAL/ERROR findings)
        findings: All findings from validation
        declaration_title: Title of the validated declaration
        canon_version: Version of the Canon used for validation
    
    Canon References:
        - IX: Canonical Tests
        - X.1: Code is an instrument (validation gates realization)
    """
    
    ok: bool
    findings: list[Finding] = field(default_factory=list)
    declaration_title: str = ""
    canon_version: str = "1.0"
    
    @classmethod
    def passing(cls, declaration_title: str = "", findings: list[Finding] | None = None) -> Verdict:
        """Create a passing verdict."""
        return cls(
            ok=True,
            findings=findings or [],
            declaration_title=declaration_title,
        )
    
    @classmethod
    def failing(cls, findings: list[Finding], declaration_title: str = "") -> Verdict:
        """Create a failing verdict."""
        return cls(
            ok=False,
            findings=findings,
            declaration_title=declaration_title,
        )
    
    def fatal_count(self) -> int:
        """Count FATAL findings."""
        return sum(1 for f in self.findings if f.severity == Severity.FATAL)
    
    def error_count(self) -> int:
        """Count ERROR findings."""
        return sum(1 for f in self.findings if f.severity == Severity.ERROR)
    
    def warn_count(self) -> int:
        """Count WARN findings."""
        return sum(1 for f in self.findings if f.severity == Severity.WARN)
    
    def info_count(self) -> int:
        """Count INFO findings."""
        return sum(1 for f in self.findings if f.severity == Severity.INFO)
    
    def blocking_findings(self) -> list[Finding]:
        """Return findings that block realization."""
        return [f for f in self.findings if f.severity.blocks_realization()]
    
    def summary(self) -> str:
        """Generate a human-readable summary."""
        status = "✓ PASSED" if self.ok else "✗ FAILED"
        lines = [
            f"Canon Validation Verdict: {status}",
            f"Declaration: {self.declaration_title or '(untitled)'}",
            f"Canon Version: {self.canon_version}",
            f"Findings: {len(self.findings)} total",
            f"  FATAL: {self.fatal_count()}",
            f"  ERROR: {self.error_count()}",
            f"  WARN:  {self.warn_count()}",
            f"  INFO:  {self.info_count()}",
        ]
        
        if self.blocking_findings():
            lines.append("\nBlocking Issues:")
            for f in self.blocking_findings():
                lines.append(f"  - [{f.severity.value.upper()}] {f.rule_id}: {f.message}")
        
        return "\n".join(lines)
    
    def __str__(self) -> str:
        return self.summary()
