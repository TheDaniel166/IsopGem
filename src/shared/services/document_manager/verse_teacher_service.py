"""Service that powers the Holy Book "teacher" workflow."""
from __future__ import annotations

import json
import re
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Sequence, Tuple

from sqlalchemy.orm import Session

from shared.utils.verse_parser import parse_verses
from shared.models.document_manager.document import Document
from shared.repositories.document_manager.document_repository import DocumentRepository
from shared.repositories.document_manager.document_verse_repository import DocumentVerseRepository
from shared.repositories.document_manager.verse_edit_log_repository import VerseEditLogRepository
from shared.repositories.document_manager.verse_rule_repository import VerseRuleRepository
from shared.database import get_db_session


class VerseTeacherService:
    """Coordinates parser output, curated overrides, and heuristics."""

    def __init__(self, db: Session):
        self.db = db
        self.document_repo = DocumentRepository(db)
        self.verse_repo = DocumentVerseRepository(db)
        self.rule_repo = VerseRuleRepository(db)
        self.log_repo = VerseEditLogRepository(db)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_curated_verses(self, document_id: int, include_ignored: bool = True) -> List[Dict[str, Any]]:
        verses = self.verse_repo.get_by_document(document_id, include_ignored=include_ignored)
        return [self._serialize_stored_verse(v) for v in verses]

    def get_or_parse_verses(
        self,
        document_id: int,
        allow_inline: bool = True,
        apply_rules: bool = True,
    ) -> Dict[str, Any]:
        curated = self.get_curated_verses(document_id)
        if curated:
            return {
                "document_id": document_id,
                "source": "curated",
                "verses": curated,
                "anomalies": self._detect_anomalies(curated),
                "rules_applied": [],
            }
        return self.generate_parser_run(document_id, allow_inline=allow_inline, apply_rules=apply_rules)

    def generate_parser_run(
        self,
        document_id: int,
        allow_inline: bool = True,
        apply_rules: bool = True,
    ) -> Dict[str, Any]:
        document = self._get_document(document_id)
        text = self._extract_plain_text(document)
        raw_verses = parse_verses(text, allow_inline=allow_inline)
        enriched = [self._enrich_parser_row(v) for v in raw_verses]

        rules_applied: List[Dict[str, Any]] = []
        if apply_rules and enriched:
            enriched, rules_applied = self._apply_rules(document, enriched, text)

        anomalies = self._detect_anomalies(enriched)
        return {
            "document_id": document_id,
            "source": "parser",
            "verses": enriched,
            "anomalies": anomalies,
            "rules_applied": rules_applied,
        }

    def save_curated_verses(
        self,
        document_id: int,
        verses: Sequence[Dict[str, Any]],
        actor: str = "system",
        notes: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        stored = self.verse_repo.replace_document_verses(document_id, verses)
        self.log_repo.log(
            document_id=document_id,
            action="replace-verses",
            payload=json.dumps({"count": len(verses), "actor": actor}, ensure_ascii=False),
            notes=notes,
        )
        return [self._serialize_stored_verse(v) for v in stored]

    def record_rule(
        self,
        scope_type: str,
        scope_value: Optional[str],
        action: str,
        description: str = "",
        pattern_before: Optional[str] = None,
        pattern_after: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        priority: int = 0,
        enabled: bool = True,
    ) -> Dict[str, Any]:
        from pillars.document_manager.models import VerseRule

        rule = VerseRule(
            scope_type=scope_type,
            scope_value=scope_value,
            description=description,
            pattern_before=pattern_before,
            pattern_after=pattern_after,
            action=action,
            parameters=json.dumps(parameters or {}, ensure_ascii=False),
            priority=priority,
            enabled=enabled,
        )
        saved = self.rule_repo.save(rule)
        # Ensure PKs/ids are available after save
        try:
            self.db.flush()
        except Exception:
            # Some DB backends may flush on commit; ignore if flush not available
            pass
        document_log_id: Optional[int] = None
        if scope_type == "document" and scope_value is not None:
            try:
                document_log_id = int(scope_value)
            except ValueError:
                document_log_id = None
        self.log_repo.log(
            document_id=document_log_id,
            action="create-rule",
            rule_id=getattr(saved, 'id', None),
            payload=json.dumps({"scope": scope_type, "action": action}, ensure_ascii=False),
        )
        return self._serialize_rule(saved)

    def list_rules_for_document(self, document_id: int) -> List[Dict[str, Any]]:
        document = self._get_document(document_id)
        rules = self._get_applicable_rules(document)
        return [self._serialize_rule(r) for r in rules]

    def list_recent_edits(self, document_id: int, limit: int = 50):
        return self.log_repo.list_recent(document_id, limit=limit)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _get_document(self, doc_id: int) -> Document:
        document = self.document_repo.get(doc_id)
        if not document:
            raise ValueError(f"Document {doc_id} was not found")
        return document

    @staticmethod
    def _extract_plain_text(document: Document) -> str:
        content = str(document.content or document.raw_content or "")
        # Remove simple HTML tags if present to keep SQLAlchemy dependency footprint small.
        if "<" in content and ">" in content:
            content = re.sub(r"<[^>]+>", " ", content)
        return content

    def _enrich_parser_row(self, verse_row: Dict[str, Any]) -> Dict[str, Any]:
        start = verse_row.get("start", 0)
        end = verse_row.get("end", 0)
        confidence = 0.95 if verse_row.get("is_line_start") else 0.65
        return {
            "number": verse_row.get("number"),
            "text": verse_row.get("text", ""),
            "start": start,
            "end": end,
            "marker_start": verse_row.get("marker_start"),
            "marker_end": verse_row.get("marker_end"),
            "status": "auto",
            "confidence": confidence,
            "source_type": "parser",
            "rule_id": None,
            "notes": "",
            "is_line_start": bool(verse_row.get("is_line_start")),
            "is_inline": bool(verse_row.get("is_inline")),
            "length": max(end - start, 0),
        }

    def _apply_rules(
        self,
        document: Document,
        verses: List[Dict[str, Any]],
        text: str,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        rules = self._get_applicable_rules(document)
        if not rules:
            return verses, []

        applied: List[Dict[str, Any]] = []
        for rule in rules:
            if not rule.enabled:
                continue
            for verse in verses:
                if verse.get("status") == "ignored" and rule.action == "suppress":
                    continue
                if not self._rule_matches(rule, text, verse):
                    continue
                self._apply_rule_to_verse(rule, verse)
                applied.append({
                    "rule_id": rule.id,
                    "rule_action": rule.action,
                    "verse_number": verse.get("number"),
                })
                self.rule_repo.increment_hit(rule.id)
        return verses, applied

    def _get_applicable_rules(self, document: Document):
        rules: List[Any] = []
        doc_id = getattr(document, 'id', None)
        rules.extend(self.rule_repo.list_rules("document", str(doc_id) if doc_id is not None else None))
        doc_collection = getattr(document, 'collection', None)
        if doc_collection:
            rules.extend(self.rule_repo.list_rules("collection", doc_collection))
        rules.extend(self.rule_repo.list_rules("global", None))
        return rules

    def _rule_matches(self, rule, text: str, verse: Dict[str, Any]) -> bool:
        before = text[max(0, verse["start"] - 200): verse["start"]]
        after = text[verse["end"]: min(len(text), verse["end"] + 200)]
        before_ok = True
        after_ok = True
        if rule.pattern_before:
            before_ok = re.search(rule.pattern_before, before, re.MULTILINE) is not None
        if rule.pattern_after:
            after_ok = re.search(rule.pattern_after, after, re.MULTILINE) is not None
        return before_ok and after_ok

    def _apply_rule_to_verse(self, rule, verse: Dict[str, Any]):
        params = self._load_rule_parameters(rule)
        action = (rule.action or "").lower()
        if action == "suppress":
            verse["status"] = "ignored"
            verse["source_type"] = "rule"
            verse["rule_id"] = rule.id
        elif action == "promote":
            verse["confidence"] = max(verse.get("confidence", 0.0), 0.98)
            verse["source_type"] = "rule"
            verse["rule_id"] = rule.id
        elif action == "renumber":
            target = params.get("target_number")
            if target is not None:
                verse["number"] = int(target)
                verse["rule_id"] = rule.id
        elif action == "note":
            verse["notes"] = params.get("note", "")
            verse["rule_id"] = rule.id
        # Additional actions can be implemented incrementally.

    @staticmethod
    def _load_rule_parameters(rule) -> Dict[str, Any]:
        try:
            return json.loads(rule.parameters or "{}") if rule.parameters else {}
        except json.JSONDecodeError:
            return {}

    def _detect_anomalies(self, verses: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
        if not verses:
            return {"duplicates": [], "missing_numbers": [], "overlaps": []}

        numbers = [int(v.get("number", 0)) for v in verses if v.get("number") is not None]
        duplicates = self._find_duplicates(numbers)
        missing = self._find_missing_numbers(sorted(set(numbers)))
        overlaps = self._find_overlaps(verses)
        return {"duplicates": duplicates, "missing_numbers": missing, "overlaps": overlaps}

    @staticmethod
    def _find_duplicates(numbers: Sequence[int]) -> List[int]:
        seen = set()
        dupes = set()
        for num in numbers:
            if num in seen:
                dupes.add(num)
            else:
                seen.add(num)
        return sorted(dupes)

    @staticmethod
    def _find_missing_numbers(sorted_numbers: Sequence[int]) -> List[int]:
        missing: List[int] = []
        if len(sorted_numbers) < 2:
            return missing
        prev = sorted_numbers[0]
        for num in sorted_numbers[1:]:
            gap = num - prev
            if gap > 1:
                missing.extend(range(prev + 1, num))
            prev = num
        return missing

    @staticmethod
    def _find_overlaps(verses: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
        overlaps: List[Dict[str, Any]] = []
        ordered = sorted(verses, key=lambda v: (v.get("start", 0), v.get("end", 0)))
        prev = ordered[0]
        for current in ordered[1:]:
            if current.get("start", 0) < prev.get("end", 0):
                overlaps.append({
                    "previous": prev.get("number"),
                    "current": current.get("number"),
                    "start": current.get("start"),
                })
            if current.get("end", 0) > prev.get("end", 0):
                prev = current
        return overlaps

    @staticmethod
    def _serialize_stored_verse(verse_obj) -> Dict[str, Any]:
        return {
            "id": verse_obj.id,
            "document_id": verse_obj.document_id,
            "number": verse_obj.verse_number,
            "text": verse_obj.text,
            "start": verse_obj.start_offset,
            "end": verse_obj.end_offset,
            "status": verse_obj.status,
            "confidence": verse_obj.confidence,
            "source_type": verse_obj.source_type,
            "rule_id": verse_obj.rule_id,
            "notes": verse_obj.notes,
            "extra_data": verse_obj.extra_data,
        }

    @staticmethod
    def _serialize_rule(rule) -> Dict[str, Any]:
        return {
            "id": rule.id,
            "scope_type": rule.scope_type,
            "scope_value": rule.scope_value,
            "description": rule.description,
            "action": rule.action,
            "pattern_before": rule.pattern_before,
            "pattern_after": rule.pattern_after,
            "parameters": VerseTeacherService._load_rule_parameters(rule),
            "priority": rule.priority,
            "enabled": rule.enabled,
            "hit_count": rule.hit_count,
        }


@contextmanager
def verse_teacher_service_context():
    """Yield a `VerseTeacherService` wired to a managed DB session."""
    with get_db_session() as db:
        yield VerseTeacherService(db)
