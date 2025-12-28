"""Service layer for persisting and retrieving natal chart definitions."""
from __future__ import annotations

from contextlib import AbstractContextManager
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Optional, Sequence

from shared.database import get_db_session

from ..models import AstrologyEvent, ChartRequest, ChartResult, GeoLocation
from ..models.chart_record import AstrologyChart
from ..repositories.chart_repository import ChartRepository


ChartSessionFactory = Callable[[], AbstractContextManager]


@dataclass(slots=True)
class SavedChartSummary:
 """
 Saved Chart Summary class definition.
 
 Attributes:
     todo: Add public attributes.
 """
	chart_id: int
	name: str
	event_timestamp: datetime
	location_label: str
	categories: List[str]
	tags: List[str]
	chart_type: str


@dataclass(slots=True)
class LoadedChart:
 """
 Loaded Chart class definition.
 
 Attributes:
     todo: Add public attributes.
 """
	chart_id: int
	request: ChartRequest
	categories: List[str]
	tags: List[str]
	description: Optional[str]


class ChartStorageService:
	"""High-level persistence facade for natal charts."""

	def __init__(self, session_factory: ChartSessionFactory = get_db_session):
  """
    init   logic.
  
  Args:
      session_factory: Description of session_factory.
  
  """
		self._session_factory = session_factory

	# ------------------------------------------------------------------
	# Public API
	# ------------------------------------------------------------------
	def save_chart(
		self,
		*,
		name: str,
		request: ChartRequest,
		result: ChartResult,
		categories: Sequence[str] = (),
		tags: Sequence[str] = (),
		description: Optional[str] = None,
	) -> int:
  """
  Save chart logic.
  
  Returns:
      Result of save_chart operation.
  """
		payload = self._serialize_request(request)
		result_payload = result.to_dict()
		primary_event = request.primary_event

		with self._session_factory() as session:
			repo = ChartRepository(session)
			record = repo.create_chart(
				name=name,
				description=description,
				chart_type=request.chart_type,
				include_svg=request.include_svg,
				house_system=self._extract_house_system(request),
				event_timestamp=primary_event.timestamp,
				timezone_offset=primary_event.resolved_timezone_offset(),
				location_label=primary_event.location.name,
				latitude=primary_event.location.latitude,
				longitude=primary_event.location.longitude,
				elevation=primary_event.location.elevation,
				request_payload=payload,
				result_payload=result_payload,
				categories=categories,
				tags=tags,
			)
			return record.id

	def list_recent(self, limit: int = 20) -> List[SavedChartSummary]:
  """
  List recent logic.
  
  Args:
      limit: Description of limit.
  
  Returns:
      Result of list_recent operation.
  """
		with self._session_factory() as session:
			repo = ChartRepository(session)
			records = repo.list_recent(limit)
			return [self._to_summary(record) for record in records]

	def search(
		self,
		*,
		text: Optional[str] = None,
		categories: Optional[Sequence[str]] = None,
		tags: Optional[Sequence[str]] = None,
		limit: int = 50,
	) -> List[SavedChartSummary]:
  """
  Search logic.
  
  Returns:
      Result of search operation.
  """
		with self._session_factory() as session:
			repo = ChartRepository(session)
			records = repo.search(text=text, categories=categories, tags=tags, limit=limit)
			return [self._to_summary(record) for record in records]

	def load_chart(self, chart_id: int) -> Optional[LoadedChart]:
  """
  Load chart logic.
  
  Args:
      chart_id: Description of chart_id.
  
  Returns:
      Result of load_chart operation.
  """
		with self._session_factory() as session:
			repo = ChartRepository(session)
			record = repo.get_chart(chart_id)
			if record is None:
				return None
			request = self._deserialize_request(record.request_payload)
			return LoadedChart(
				chart_id=record.id,
				request=request,
				categories=[category.name for category in record.categories],
				tags=[tag.name for tag in record.tags],
				description=record.description,
			)

	# ------------------------------------------------------------------
	# Serialization helpers
	# ------------------------------------------------------------------
	def _serialize_request(self, request: ChartRequest) -> Dict[str, object]:
		return {
			"chart_type": request.chart_type,
			"include_svg": request.include_svg,
			"settings": request.settings,
			"primary_event": self._serialize_event(request.primary_event),
			"reference_event": self._serialize_event(request.reference_event)
			if request.reference_event
			else None,
		}

	def _deserialize_request(self, payload: Dict[str, object]) -> ChartRequest:
		primary_event = self._deserialize_event(payload["primary_event"])
		reference_data = payload.get("reference_event")
		reference_event = (
			self._deserialize_event(reference_data) if reference_data is not None else None
		)
		return ChartRequest(
			primary_event=primary_event,
			chart_type=str(payload.get("chart_type", "Radix")),
			reference_event=reference_event,
			include_svg=bool(payload.get("include_svg", True)),
			settings=payload.get("settings"),
		)

	@staticmethod
	def _serialize_event(event: AstrologyEvent) -> Dict[str, object]:
		return {
			"name": event.name,
			"timestamp": event.timestamp.isoformat(),
			"timezone_offset": event.timezone_offset,
			"metadata": event.metadata,
			"location": {
				"name": event.location.name,
				"latitude": event.location.latitude,
				"longitude": event.location.longitude,
				"elevation": event.location.elevation,
				"country_code": event.location.country_code,
			},
		}

	@staticmethod
	def _deserialize_event(payload: Dict[str, object]) -> AstrologyEvent:
		location_data = payload["location"]
		location = GeoLocation(
			name=location_data["name"],
			latitude=location_data["latitude"],
			longitude=location_data["longitude"],
			elevation=location_data.get("elevation", 0.0),
			country_code=location_data.get("country_code"),
		)
		timestamp = datetime.fromisoformat(payload["timestamp"])
		return AstrologyEvent(
			name=payload["name"],
			timestamp=timestamp,
			location=location,
			timezone_offset=payload.get("timezone_offset"),
			metadata=payload.get("metadata", {}),
		)

	# ------------------------------------------------------------------
	# Internal helpers
	# ------------------------------------------------------------------
	@staticmethod
	def _extract_house_system(request: ChartRequest) -> Optional[str]:
		if not request.settings:
			return None
		astro_cfg = request.settings.get("astrocfg")
		if isinstance(astro_cfg, dict):
			value = astro_cfg.get("houses_system")
			if isinstance(value, str):
				return value
		return None

	@staticmethod
	def _to_summary(record: AstrologyChart) -> SavedChartSummary:
		return SavedChartSummary(
			chart_id=record.id,
			name=record.name,
			event_timestamp=record.event_timestamp,
			location_label=record.location_label,
			categories=[category.name for category in record.categories],
			tags=[tag.name for tag in record.tags],
			chart_type=record.chart_type,
		)