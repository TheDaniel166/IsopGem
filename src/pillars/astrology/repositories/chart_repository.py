"""Persistence helpers for astrology chart records."""
from __future__ import annotations

from typing import List, Optional, Sequence

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.chart_record import AstrologyChart, ChartCategory, ChartTag


class ChartRepository:
    """High level CRUD helpers for astrology charts."""

    def __init__(self, session: Session):
        self._session = session

    # ------------------------------------------------------------------
    # Creation / updates
    # ------------------------------------------------------------------
    def create_chart(
        self,
        *,
        name: str,
        description: Optional[str],
        chart_type: str,
        include_svg: bool,
        house_system: Optional[str],
        event_timestamp,
        timezone_offset: float,
        location_label: str,
        latitude: float,
        longitude: float,
        elevation: Optional[float],
        request_payload,
        result_payload,
        categories: Sequence[str],
        tags: Sequence[str],
    ) -> AstrologyChart:
        chart = AstrologyChart(
            name=name,
            description=description,
            chart_type=chart_type,
            include_svg=include_svg,
            house_system=house_system,
            event_timestamp=event_timestamp,
            timezone_offset=timezone_offset,
            location_label=location_label,
            latitude=latitude,
            longitude=longitude,
            elevation=elevation,
            request_payload=request_payload,
            result_payload=result_payload,
        )
        self._session.add(chart)
        chart.categories = self._resolve_categories(categories)
        chart.tags = self._resolve_tags(tags)
        self._session.commit()
        self._session.refresh(chart)
        return chart

    def get_chart(self, chart_id: int) -> Optional[AstrologyChart]:
        return (
            self._session.query(AstrologyChart)
            .filter(AstrologyChart.id == chart_id)
            .one_or_none()
        )

    def list_recent(self, limit: int = 20) -> List[AstrologyChart]:
        return (
            self._session.query(AstrologyChart)
            .order_by(AstrologyChart.event_timestamp.desc())
            .limit(limit)
            .all()
        )

    def search(
        self,
        *,
        text: Optional[str] = None,
        categories: Optional[Sequence[str]] = None,
        tags: Optional[Sequence[str]] = None,
        limit: int = 50,
    ) -> List[AstrologyChart]:
        query = self._session.query(AstrologyChart)

        if text:
            like = f"%{text.lower()}%"
            query = query.filter(
                func.lower(AstrologyChart.name).like(like)
                | func.lower(AstrologyChart.location_label).like(like)
            )

        if categories:
            for category in categories:
                query = query.filter(
                    AstrologyChart.categories.any(func.lower(ChartCategory.name) == category.lower())
                )

        if tags:
            for tag in tags:
                query = query.filter(
                    AstrologyChart.tags.any(func.lower(ChartTag.name) == tag.lower())
                )

        return query.order_by(AstrologyChart.event_timestamp.desc()).limit(limit).all()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _resolve_categories(self, names: Sequence[str]) -> List[ChartCategory]:
        return self._resolve_terms(ChartCategory, names)

    def _resolve_tags(self, names: Sequence[str]) -> List[ChartTag]:
        return self._resolve_terms(ChartTag, names)

    def _resolve_terms(self, model, names: Sequence[str]):
        normalized = [name.strip() for name in names if name.strip()]
        if not normalized:
            return []

        existing = (
            self._session.query(model)
            .filter(func.lower(model.name).in_([name.lower() for name in normalized]))
            .all()
        )
        existing_map = {item.name.lower(): item for item in existing}

        resolved: List = []
        for name in normalized:
            key = name.lower()
            if key in existing_map:
                resolved.append(existing_map[key])
            else:
                instance = model(name=name)
                self._session.add(instance)
                resolved.append(instance)
        return resolved
