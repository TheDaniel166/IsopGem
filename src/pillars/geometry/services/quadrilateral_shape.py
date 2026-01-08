"""Quadrilateral shape calculators."""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

from .base_shape import GeometricShape, ShapeProperty


EPSILON = 1e-7


def _clamp(value: float, minimum: float, maximum: float) -> float:
	return max(minimum, min(maximum, value))


def _distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
	return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def _shoelace_area(points: Tuple[Tuple[float, float], ...]) -> float:
	area = 0.0
	n = len(points)
	for i in range(n):
		x1, y1 = points[i]
		x2, y2 = points[(i + 1) % n]
		area += x1 * y2 - x2 * y1
	return abs(area) / 2.0


def _polygon_centroid(points: Tuple[Tuple[float, float], ...]) -> Tuple[float, float]:
	area_factor = 0.0
	cx = 0.0
	cy = 0.0
	n = len(points)
	for i in range(n):
		x1, y1 = points[i]
		x2, y2 = points[(i + 1) % n]
		cross = x1 * y2 - x2 * y1
		area_factor += cross
		cx += (x1 + x2) * cross
		cy += (y1 + y2) * cross
	area_factor *= 0.5
	if abs(area_factor) < EPSILON:
		return 0.0, 0.0
	cx /= 6 * area_factor
	cy /= 6 * area_factor
	return cx, cy


def _circle_intersections(
	c1: Tuple[float, float],
	r1: float,
	c2: Tuple[float, float],
	r2: float,
) -> List[Tuple[float, float]]:
	"""Return intersection points for two circles if they exist."""

	x1, y1 = c1
	x2, y2 = c2
	dx = x2 - x1
	dy = y2 - y1
	d = math.hypot(dx, dy)
	if d < EPSILON:
		return []
	if d > r1 + r2 + EPSILON:
		return []
	if d < abs(r1 - r2) - EPSILON:
		return []

	a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
	h_sq = r1 * r1 - a * a
	if h_sq < -EPSILON:
		return []
	h_sq = max(h_sq, 0.0)
	h = math.sqrt(h_sq)
	xm = x1 + a * dx / d
	ym = y1 + a * dy / d

	rx = -dy * (h / d)
	ry = dx * (h / d)
	p1 = (xm + rx, ym + ry)
	p2 = (xm - rx, ym - ry)
	if _distance(p1, p2) < EPSILON:
		return [p1]
	return [p1, p2]


class ParallelogramShape(GeometricShape):
	"""Parallelogram defined by base, side, and included angle/height."""

	def __init__(self):
		"""
		init   logic.
  
		"""
		self._points: Optional[Tuple[Tuple[float, float], ...]] = None
		super().__init__()

	@property
	def name(self) -> str:
		"""
		Name logic.
  
		Returns:
		  Result of name operation.
		"""
		return "Parallelogram"

	@property
	def description(self) -> str:
		"""
		Description logic.
  
		Returns:
		  Result of description operation.
		"""
		return "Opposite sides parallel with optional angle/height breakdown"

	@property
	def calculation_hint(self) -> str:
		"""
		Calculation hint logic.
  
		Returns:
		  Result of calculation_hint operation.
		"""
		return "Enter Base + Height, or Base + Side + Angle"

	def _init_properties(self):
		self.properties = {
			'base': ShapeProperty(name='Base', key='base', unit='units', formula=r'b'),
			'side': ShapeProperty(name='Side', key='side', unit='units', formula=r's'),
			'height': ShapeProperty(name='Height', key='height', unit='units', formula=r'h = s\sin\theta'),
			'angle_deg': ShapeProperty(name='Included Angle (°)', key='angle_deg', unit='°', precision=2, formula=r'\theta'),
			'perimeter': ShapeProperty(name='Perimeter', key='perimeter', unit='units', readonly=True, formula=r'P = 2(b + s)'),
			'area': ShapeProperty(name='Area', key='area', unit='units²', readonly=True, formula=r'A = b h = bs\sin\theta'),
			'diagonal_short': ShapeProperty(name='Short Diagonal', key='diagonal_short', unit='units', readonly=True, formula=r'd_{short} = \sqrt{b^2 + s^2 - 2bs\cos\theta}'),
			'diagonal_long': ShapeProperty(name='Long Diagonal', key='diagonal_long', unit='units', readonly=True, formula=r'd_{long} = \sqrt{b^2 + s^2 + 2bs\cos\theta}'),
		}

	def calculate_from_property(self, property_key: str, value: float) -> bool:
		"""
  Compute from property logic.
  
		Args:
		  property_key: Description of property_key.
		  value: Description of value.
  
		Returns:
		  Result of calculate_from_property operation.
		"""
		if property_key not in {'base', 'side', 'height', 'angle_deg'}:
			return False
		if value <= 0:
			return False
		previous = self.properties[property_key].value
		self.properties[property_key].value = value
		if not self._resolve():
			self.properties[property_key].value = previous
			return False
		return True

	def _resolve(self) -> bool:
		base = self.properties['base'].value
		side = self.properties['side'].value
		height = self.properties['height'].value
		angle = self.properties['angle_deg'].value

		if angle is not None and not (0 < angle < 180):
			return False

		changed = True
		while changed:
			changed = False
			base = self.properties['base'].value
			side = self.properties['side'].value
			height = self.properties['height'].value
			angle = self.properties['angle_deg'].value

			if side and angle and height is None:
				rad = math.radians(angle)
				height = side * math.sin(rad)
				self.properties['height'].value = height
				changed = True

			if height and side and angle is None:
				ratio = _clamp(height / side, -1.0, 1.0)
				angle = math.degrees(math.asin(ratio))
				self.properties['angle_deg'].value = angle
				changed = True

			if height and angle and side is None:
				rad = math.radians(angle)
				sin_val = math.sin(rad)
				if sin_val <= EPSILON:
					return False
				side = height / sin_val
				self.properties['side'].value = side
				changed = True

		base = self.properties['base'].value
		side = self.properties['side'].value
		height = self.properties['height'].value
		angle = self.properties['angle_deg'].value

		if side and height and side < height - EPSILON:
			return False

		area = None
		if base and height:
			area = base * height
		elif base and side and angle:
			area = base * side * math.sin(math.radians(angle))

		self.properties['area'].value = area
		self.properties['perimeter'].value = 2 * (base + side) if base and side else None

		if base and side and angle:
			rad = math.radians(angle)
			cos_val = math.cos(rad)
			d1 = math.sqrt(max(base * base + side * side - 2 * base * side * cos_val, 0.0))
			d2 = math.sqrt(max(base * base + side * side + 2 * base * side * cos_val, 0.0))
			self.properties['diagonal_short'].value = min(d1, d2)
			self.properties['diagonal_long'].value = max(d1, d2)
			self._points = (
				(0.0, 0.0),
				(base, 0.0),
				(base + side * math.cos(rad), side * math.sin(rad)),
				(side * math.cos(rad), side * math.sin(rad)),
			)
		else:
			self.properties['diagonal_short'].value = None
			self.properties['diagonal_long'].value = None
			self._points = None

		return True

	def get_drawing_instructions(self) -> Dict:
		"""
  Retrieve drawing instructions logic.
  
		Returns:
		  Result of get_drawing_instructions operation.
		"""
		if not self._points:
			return {'type': 'empty'}
		return {'type': 'polygon', 'points': list(self._points)}

	def get_label_positions(self) -> List[Tuple[str, float, float]]:
		"""
  Retrieve label positions logic.
  
		Returns:
		  Result of get_label_positions operation.
		"""
		if not self._points:
			return []
		centroid = _polygon_centroid(self._points)
		area = self.properties['area'].value
		perimeter = self.properties['perimeter'].value
		return [
			(f"A = {area:.4f}".rstrip('0').rstrip('.'), centroid[0], centroid[1] + 0.2),
			(f"P = {perimeter:.4f}".rstrip('0').rstrip('.'), centroid[0], centroid[1] - 0.2),
		]


class RhombusShape(GeometricShape):
	"""Rhombus with equal sides and diagonal/angle utilities."""

	def __init__(self):
		"""
		init   logic.
  
		"""
		self._points: Optional[Tuple[Tuple[float, float], ...]] = None
		super().__init__()

	@property
	def name(self) -> str:
		"""
		Name logic.
  
		Returns:
		  Result of name operation.
		"""
		return "Rhombus"

	@property
	def description(self) -> str:
		"""
		Description logic.
  
		Returns:
		  Result of description operation.
		"""
		return "All sides equal with diagonal and height relationships"

	@property
	def calculation_hint(self) -> str:
		"""
		Calculation hint logic.
  
		Returns:
		  Result of calculation_hint operation.
		"""
		return "Enter Side + Angle, or Diagonals"

	def _init_properties(self):
		self.properties = {
			'side': ShapeProperty(name='Side Length', key='side', unit='units', formula=r'a'),
			'height': ShapeProperty(name='Height', key='height', unit='units', formula=r'h = a\sin\theta'),
			'angle_deg': ShapeProperty(name='Interior Angle (°)', key='angle_deg', unit='°', precision=2, formula=r'\theta'),
			'diagonal_long': ShapeProperty(name='Long Diagonal', key='diagonal_long', unit='units', formula=r'd_1 = a\sqrt{2 + 2\cos\theta}'),
			'diagonal_short': ShapeProperty(name='Short Diagonal', key='diagonal_short', unit='units', formula=r'd_2 = a\sqrt{2 - 2\cos\theta}'),
			'perimeter': ShapeProperty(name='Perimeter', key='perimeter', unit='units', readonly=True, formula=r'P = 4a'),
			'area': ShapeProperty(name='Area', key='area', unit='units²', readonly=True, formula=r'A = a^2\sin\theta = \tfrac{d_1 d_2}{2}'),
		}

	def calculate_from_property(self, property_key: str, value: float) -> bool:
		"""
  Compute from property logic.
  
		Args:
		  property_key: Description of property_key.
		  value: Description of value.
  
		Returns:
		  Result of calculate_from_property operation.
		"""
		if property_key not in {'side', 'height', 'angle_deg', 'diagonal_long', 'diagonal_short'}:
			return False
		if value <= 0:
			return False
		previous = self.properties[property_key].value
		self.properties[property_key].value = value
		if not self._resolve():
			self.properties[property_key].value = previous
			return False
		return True

	def _resolve(self) -> bool:
		angle = self.properties['angle_deg'].value
		if angle is not None and not (0 < angle < 180):
			return False

		d_long = self.properties['diagonal_long'].value
		d_short = self.properties['diagonal_short'].value
		if d_long and d_short and d_long < d_short:
			self.properties['diagonal_long'].value, self.properties['diagonal_short'].value = d_short, d_long
			d_long, d_short = d_short, d_long

		side = self.properties['side'].value
		height = self.properties['height'].value

		if d_long and d_short:
			side = 0.5 * math.sqrt(d_long * d_long + d_short * d_short)
			self.properties['side'].value = side
			cos_val = (d_long * d_long - d_short * d_short) / (d_long * d_long + d_short * d_short)
			angle = math.degrees(math.acos(_clamp(cos_val, -1.0, 1.0)))
			self.properties['angle_deg'].value = angle
			height = side * math.sin(math.radians(angle))
			self.properties['height'].value = height

		if side and angle and (d_long is None or d_short is None):
			rad = math.radians(angle)
			d1 = side * math.sqrt(2 + 2 * math.cos(rad))
			d2 = side * math.sqrt(2 - 2 * math.cos(rad))
			self.properties['diagonal_long'].value = max(d1, d2)
			self.properties['diagonal_short'].value = min(d1, d2)
			d_long = self.properties['diagonal_long'].value
			d_short = self.properties['diagonal_short'].value

		if side and height and angle is None:
			ratio = _clamp(height / side, -1.0, 1.0)
			angle = math.degrees(math.asin(ratio))
			self.properties['angle_deg'].value = angle

		side = self.properties['side'].value
		height = self.properties['height'].value
		angle = self.properties['angle_deg'].value
		d_long = self.properties['diagonal_long'].value
		d_short = self.properties['diagonal_short'].value

		if side and height and side < height - EPSILON:
			return False

		area = None
		if side and height:
			area = side * height
		elif d_long and d_short:
			area = 0.5 * d_long * d_short

		self.properties['area'].value = area
		self.properties['perimeter'].value = 4 * side if side else None

		if side and angle:
			rad = math.radians(angle)
			self._points = (
				(0.0, 0.0),
				(side, 0.0),
				(side + side * math.cos(rad), side * math.sin(rad)),
				(side * math.cos(rad), side * math.sin(rad)),
			)
		else:
			self._points = None

		return True

	def get_drawing_instructions(self) -> Dict:
		"""
  Retrieve drawing instructions logic.
  
		Returns:
		  Result of get_drawing_instructions operation.
		"""
		if not self._points:
			return {'type': 'empty'}
		return {'type': 'polygon', 'points': list(self._points)}

	def get_label_positions(self) -> List[Tuple[str, float, float]]:
		"""
  Retrieve label positions logic.
  
		Returns:
		  Result of get_label_positions operation.
		"""
		if not self._points:
			return []
		centroid = _polygon_centroid(self._points)
		area = self.properties['area'].value
		return [
			(f"A = {area:.4f}".rstrip('0').rstrip('.'), centroid[0], centroid[1] + 0.1)
		]


class TrapezoidShape(GeometricShape):
	"""General trapezoid with one pair of parallel sides."""

	def __init__(self):
		"""
		init   logic.
  
		"""
		self._points: Optional[Tuple[Tuple[float, float], ...]] = None
		super().__init__()

	@property
	def name(self) -> str:
		"""
		Name logic.
  
		Returns:
		  Result of name operation.
		"""
		return "Trapezoid"

	@property
	def description(self) -> str:
		"""
		Description logic.
  
		Returns:
		  Result of description operation.
		"""
		return "Single pair of parallel bases with leg + altitude metrics"

	@property
	def calculation_hint(self) -> str:
		"""
		Calculation hint logic.
  
		Returns:
		  Result of calculation_hint operation.
		"""
		return "Enter Bases + Height + Legs"

	def _init_properties(self):
		self.properties = {
			'base_major': ShapeProperty(name='Major Base', key='base_major', unit='units', formula=r'B'),
			'base_minor': ShapeProperty(name='Minor Base', key='base_minor', unit='units', formula=r'b'),
			'height': ShapeProperty(name='Height', key='height', unit='units', formula=r'h'),
			'leg_left': ShapeProperty(name='Left Leg', key='leg_left', unit='units', formula=r'\ell_L'),
			'leg_right': ShapeProperty(name='Right Leg', key='leg_right', unit='units', formula=r'\ell_R'),
			'area': ShapeProperty(name='Area', key='area', unit='units²', readonly=True, formula=r'A = \tfrac{(B + b)h}{2}'),
			'perimeter': ShapeProperty(name='Perimeter', key='perimeter', unit='units', readonly=True, formula=r'P = B + b + \ell_L + \ell_R'),
			'midsegment': ShapeProperty(name='Mid-segment', key='midsegment', unit='units', readonly=True, formula=r'm = \tfrac{B + b}{2}'),
			'angle_left_deg': ShapeProperty(name='Left Base Angle (°)', key='angle_left_deg', unit='°', readonly=True, precision=2, formula=r'\alpha_L = \arctan\!\left(\tfrac{h}{\sqrt{\ell_L^2 - h^2}}\right)'),
			'angle_right_deg': ShapeProperty(name='Right Base Angle (°)', key='angle_right_deg', unit='°', readonly=True, precision=2, formula=r'\alpha_R = \arctan\!\left(\tfrac{h}{\sqrt{\ell_R^2 - h^2}}\right)'),
		}

	def calculate_from_property(self, property_key: str, value: float) -> bool:
		"""
  Compute from property logic.
  
		Args:
		  property_key: Description of property_key.
		  value: Description of value.
  
		Returns:
		  Result of calculate_from_property operation.
		"""
		if property_key not in {'base_major', 'base_minor', 'height', 'leg_left', 'leg_right'}:
			return False
		if value <= 0:
			return False
		previous = self.properties[property_key].value
		self.properties[property_key].value = value
		if not self._resolve():
			self.properties[property_key].value = previous
			return False
		return True

	def _resolve(self) -> bool:
		base_major = self.properties['base_major'].value
		base_minor = self.properties['base_minor'].value
		if base_major and base_minor and base_major < base_minor:
			self.properties['base_major'].value, self.properties['base_minor'].value = base_minor, base_major
			base_major, base_minor = base_minor, base_major

		height = self.properties['height'].value
		leg_left = self.properties['leg_left'].value
		leg_right = self.properties['leg_right'].value

		diff = None
		if base_major and base_minor:
			diff = base_major - base_minor
			self.properties['midsegment'].value = (base_major + base_minor) / 2
		else:
			self.properties['midsegment'].value = None

		# Derive missing legs when height + other leg known.
		if height and diff is not None:
			if leg_left and leg_left < height - EPSILON:
				return False
			if leg_right and leg_right < height - EPSILON:
				return False

			offset_left = math.sqrt(max(leg_left * leg_left - height * height, 0.0)) if leg_left else None
			offset_right = math.sqrt(max(leg_right * leg_right - height * height, 0.0)) if leg_right else None

			if offset_left is not None and offset_right is not None:
				if abs((offset_left + offset_right) - diff) > 1e-4:
					return False
			elif offset_left is not None and diff is not None:
				offset_right = diff - offset_left
				if offset_right < -EPSILON:
					return False
				offset_right = max(offset_right, 0.0)
				leg_right = math.sqrt(height * height + offset_right * offset_right)
				self.properties['leg_right'].value = leg_right
			elif offset_right is not None and diff is not None:
				offset_left = diff - offset_right
				if offset_left < -EPSILON:
					return False
				offset_left = max(offset_left, 0.0)
				leg_left = math.sqrt(height * height + offset_left * offset_left)
				self.properties['leg_left'].value = leg_left

			angle_left = None
			angle_right = None
			if height and diff is not None:
				if leg_left:
					offset_left = math.sqrt(max(leg_left * leg_left - height * height, 0.0))
					angle_left = math.degrees(math.atan2(height, offset_left if offset_left > EPSILON else EPSILON))
				if leg_right:
					offset_right = math.sqrt(max(leg_right * leg_right - height * height, 0.0))
					angle_right = math.degrees(math.atan2(height, offset_right if offset_right > EPSILON else EPSILON))
			self.properties['angle_left_deg'].value = angle_left
			self.properties['angle_right_deg'].value = angle_right

			if base_major and base_minor:
				offset_left_draw = None
				if leg_left:
					offset_left_draw = math.sqrt(max(leg_left * leg_left - height * height, 0.0))
				elif diff is not None:
					offset_left_draw = diff / 2
				offset_left_draw = offset_left_draw or 0.0
				top_left_x = offset_left_draw
				top_right_x = top_left_x + base_minor
				self._points = (
					(0.0, 0.0),
					(base_major, 0.0),
					(top_right_x, height),
					(top_left_x, height),
				)
			else:
				self._points = None
		else:
			self.properties['angle_left_deg'].value = None
			self.properties['angle_right_deg'].value = None
			self._points = None

		area = None
		if base_major and base_minor and height:
			area = (base_major + base_minor) * height / 2
		self.properties['area'].value = area

		if base_major and base_minor and leg_left and leg_right:
			self.properties['perimeter'].value = base_major + base_minor + leg_left + leg_right
		else:
			self.properties['perimeter'].value = None

		return True

	def get_drawing_instructions(self) -> Dict:
		"""
  Retrieve drawing instructions logic.
  
		Returns:
		  Result of get_drawing_instructions operation.
		"""
		if not self._points:
			return {'type': 'empty'}
		return {'type': 'polygon', 'points': list(self._points)}

	def get_label_positions(self) -> List[Tuple[str, float, float]]:
		"""
  Retrieve label positions logic.
  
		Returns:
		  Result of get_label_positions operation.
		"""
		if not self._points:
			return []
		centroid = _polygon_centroid(self._points)
		area = self.properties['area'].value
		return [
			(f"A = {area:.4f}".rstrip('0').rstrip('.'), centroid[0], centroid[1] + 0.1)
		]


class IsoscelesTrapezoidShape(GeometricShape):
	"""Isosceles trapezoid with equal legs and symmetry tools."""

	def __init__(self):
		"""
		init   logic.
  
		"""
		self._points: Optional[Tuple[Tuple[float, float], ...]] = None
		super().__init__()

	@property
	def name(self) -> str:
		"""
		Name logic.
  
		Returns:
		  Result of name operation.
		"""
		return "Isosceles Trapezoid"

	@property
	def description(self) -> str:
		"""
		Description logic.
  
		Returns:
		  Result of description operation.
		"""
		return "Congruent legs with equal base angles and diagonal data"

	@property
	def calculation_hint(self) -> str:
		"""
		Calculation hint logic.
  
		Returns:
		  Result of calculation_hint operation.
		"""
		return "Enter Bases + Height (or Leg)"

	def _init_properties(self):
		self.properties = {
			'base_major': ShapeProperty(name='Major Base', key='base_major', unit='units', formula=r'B'),
			'base_minor': ShapeProperty(name='Minor Base', key='base_minor', unit='units', formula=r'b'),
			'height': ShapeProperty(name='Height', key='height', unit='units', formula=r'h'),
			'leg': ShapeProperty(name='Leg', key='leg', unit='units', formula=r'\ell = \sqrt{h^2 + \left(\tfrac{B-b}{2}\right)^2}'),
			'area': ShapeProperty(name='Area', key='area', unit='units²', readonly=True, formula=r'A = \tfrac{(B + b)h}{2}'),
			'perimeter': ShapeProperty(name='Perimeter', key='perimeter', unit='units', readonly=True, formula=r'P = B + b + 2\ell'),
			'midsegment': ShapeProperty(name='Mid-segment', key='midsegment', unit='units', readonly=True, formula=r'm = \tfrac{B + b}{2}'),
			'base_angle_deg': ShapeProperty(name='Base Angle (°)', key='base_angle_deg', unit='°', readonly=True, precision=2, formula=r'\alpha = \arctan\!\left(\tfrac{2h}{B - b}\right)'),
			'diagonal': ShapeProperty(name='Diagonal Length', key='diagonal', unit='units', readonly=True, formula=r'd = \sqrt{\ell^2 + B b}'),
		}

	def calculate_from_property(self, property_key: str, value: float) -> bool:
		"""
  Compute from property logic.
  
		Args:
		  property_key: Description of property_key.
		  value: Description of value.
  
		Returns:
		  Result of calculate_from_property operation.
		"""
		if property_key not in {'base_major', 'base_minor', 'height', 'leg'}:
			return False
		if value <= 0:
			return False
		previous = self.properties[property_key].value
		self.properties[property_key].value = value
		if not self._resolve():
			self.properties[property_key].value = previous
			return False
		return True

	def _resolve(self) -> bool:
		base_major = self.properties['base_major'].value
		base_minor = self.properties['base_minor'].value
		if base_major and base_minor and base_major < base_minor:
			self.properties['base_major'].value, self.properties['base_minor'].value = base_minor, base_major
			base_major, base_minor = base_minor, base_major

		height = self.properties['height'].value
		leg = self.properties['leg'].value
		delta = None
		if base_major and base_minor:
			delta = (base_major - base_minor) / 2
			self.properties['midsegment'].value = (base_major + base_minor) / 2
		else:
			self.properties['midsegment'].value = None

		if delta is not None:
			if height and leg is None:
				leg = math.sqrt(height * height + delta * delta)
				self.properties['leg'].value = leg
			elif leg and height is None:
				if leg <= delta - EPSILON:
					return False
				height = math.sqrt(max(leg * leg - delta * delta, 0.0))
				self.properties['height'].value = height

		base_major = self.properties['base_major'].value
		base_minor = self.properties['base_minor'].value
		height = self.properties['height'].value
		leg = self.properties['leg'].value

		if height and delta is not None:
			angle = math.degrees(math.atan2(height, delta if delta > EPSILON else EPSILON))
			self.properties['base_angle_deg'].value = angle
		else:
			self.properties['base_angle_deg'].value = None

		if base_major and base_minor and height:
			self.properties['area'].value = (base_major + base_minor) * height / 2
		else:
			self.properties['area'].value = None

		if base_major and base_minor and leg:
			self.properties['perimeter'].value = base_major + base_minor + 2 * leg
			diag = math.sqrt(leg * leg + base_major * base_minor)
			self.properties['diagonal'].value = diag
		else:
			self.properties['perimeter'].value = None
			self.properties['diagonal'].value = None

		if base_major and base_minor and height:
			offset = (base_major - base_minor) / 2 if base_minor else 0.0
			self._points = (
				(0.0, 0.0),
				(base_major, 0.0),
				(offset + base_minor, height),
				(offset, height),
			)
		else:
			self._points = None

		return True

	def get_drawing_instructions(self) -> Dict:
		"""
  Retrieve drawing instructions logic.
  
		Returns:
		  Result of get_drawing_instructions operation.
		"""
		if not self._points:
			return {'type': 'empty'}
		return {'type': 'polygon', 'points': list(self._points)}

	def get_label_positions(self) -> List[Tuple[str, float, float]]:
		"""
  Retrieve label positions logic.
  
		Returns:
		  Result of get_label_positions operation.
		"""
		if not self._points:
			return []
		centroid = _polygon_centroid(self._points)
		area = self.properties['area'].value
		return [
			(f"A = {area:.4f}".rstrip('0').rstrip('.'), centroid[0], centroid[1] + 0.1)
		]


class _BaseAdjacentEqualShape(GeometricShape):
	"""Base for kite and dart shapes sharing solving logic."""

	convex: bool = True

	def __init__(self):
		"""
		init   logic.
  
		"""
		self._points: Optional[Tuple[Tuple[float, float], ...]] = None
		super().__init__()

	def _init_properties(self):
		self.properties = {
			'equal_side': ShapeProperty(name='Equal Side Length', key='equal_side', unit='units', formula=r'a'),
			'unequal_side': ShapeProperty(name='Other Side Length', key='unequal_side', unit='units', formula=r'b'),
			'included_angle_deg': ShapeProperty(name='Angle Between Equal Sides (°)', key='included_angle_deg', unit='°', precision=2, formula=r'\theta'),
			'area': ShapeProperty(name='Area', key='area', unit='units²', readonly=True, formula=r'A = \tfrac{d_1 d_2}{2}'),
			'perimeter': ShapeProperty(name='Perimeter', key='perimeter', unit='units', readonly=True, formula=r'P = 2(a + b)'),
			'diagonal_long': ShapeProperty(name='Long Diagonal', key='diagonal_long', unit='units', readonly=True, formula=r'd_1 = \max(AC, BD)'),
			'diagonal_short': ShapeProperty(name='Short Diagonal', key='diagonal_short', unit='units', readonly=True, formula=r'd_2 = \min(AC, BD)'),
		}

	def calculate_from_property(self, property_key: str, value: float) -> bool:
		"""
  Compute from property logic.
  
		Args:
		  property_key: Description of property_key.
		  value: Description of value.
  
		Returns:
		  Result of calculate_from_property operation.
		"""
		if property_key not in {'equal_side', 'unequal_side', 'included_angle_deg'}:
			return False
		if value <= 0:
			return False
		previous = self.properties[property_key].value
		self.properties[property_key].value = value
		if not self._solve_geometry():
			self.properties[property_key].value = previous
			return False
		return True

	def _solve_geometry(self) -> bool:
		a = self.properties['equal_side'].value
		b = self.properties['unequal_side'].value
		angle = self.properties['included_angle_deg'].value

		if a is None or b is None or angle is None:
			self._points = None
			self.properties['area'].value = None
			self.properties['perimeter'].value = None
			self.properties['diagonal_long'].value = None
			self.properties['diagonal_short'].value = None
			return True

		if self.convex:
			if not (0 < angle < 180):
				return False
		else:
			if not (180 < angle < 360):
				return False

		theta = math.radians(angle)
		A = (0.0, 0.0)
		B = (a, 0.0)
		D = (a * math.cos(theta), a * math.sin(theta))

		intersections = _circle_intersections(B, b, D, b)
		if not intersections:
			return False

		chosen: Optional[Tuple[float, float]] = None
		if self.convex:
			chosen = max(intersections, key=lambda p: p[1])
		else:
			chosen = max(intersections, key=lambda p: -abs(p[1]))

		C = chosen
		self._points = (A, B, C, D)
		area = _shoelace_area(self._points)
		self.properties['area'].value = area
		self.properties['perimeter'].value = 2 * (a + b)
		diag_ac = _distance(A, C)
		diag_bd = _distance(B, D)
		self.properties['diagonal_long'].value = max(diag_ac, diag_bd)
		self.properties['diagonal_short'].value = min(diag_ac, diag_bd)
		return True

	def get_drawing_instructions(self) -> Dict:
		"""
  Retrieve drawing instructions logic.
  
		Returns:
		  Result of get_drawing_instructions operation.
		"""
		if not self._points:
			return {'type': 'empty'}
		return {'type': 'polygon', 'points': list(self._points)}

	def get_label_positions(self) -> List[Tuple[str, float, float]]:
		"""
  Retrieve label positions logic.
  
		Returns:
		  Result of get_label_positions operation.
		"""
		if not self._points:
			return []
		centroid = _polygon_centroid(self._points)
		area = self.properties['area'].value
		return [
			(f"A = {area:.4f}".rstrip('0').rstrip('.'), centroid[0], centroid[1] + 0.1)
		]


class KiteShape(_BaseAdjacentEqualShape):
	"""Convex kite with two pairs of adjacent equal edges."""

	convex = True

	@property
	def name(self) -> str:
		"""
		Name logic.
  
		Returns:
		  Result of name operation.
		"""
		return "Kite"

	@property
	def description(self) -> str:
		"""
		Description logic.
  
		Returns:
		  Result of description operation.
		"""
		return "Two equal adjacent sides mirrored across a diagonal"

	@property
	def calculation_hint(self) -> str:
		"""
		Calculation hint logic.
  
		Returns:
		  Result of calculation_hint operation.
		"""
		return "Enter 2 unequal sides + Angle"


class DeltoidShape(_BaseAdjacentEqualShape):
	"""Concave dart/deltoid configuration."""

	convex = False

	@property
	def name(self) -> str:
		"""
		Name logic.
  
		Returns:
		  Result of name operation.
		"""
		return "Deltoid / Dart"

	@property
	def description(self) -> str:
		"""
		Description logic.
  
		Returns:
		  Result of description operation.
		"""
		return "Concave kite with reflex apex for dart studies"


class CyclicQuadrilateralShape(GeometricShape):
	"""Quadrilateral with all vertices on a common circumcircle."""

	def __init__(self):
		"""
		init   logic.
  
		"""
		self._points: Optional[Tuple[Tuple[float, float], ...]] = None
		super().__init__()

	@property
	def name(self) -> str:
		"""
		Name logic.
  
		Returns:
		  Result of name operation.
		"""
		return "Cyclic Quadrilateral"

	@property
	def description(self) -> str:
		"""
		Description logic.
  
		Returns:
		  Result of description operation.
		"""
		return "Vertices on a circle with Brahmagupta area"

	@property
	def calculation_hint(self) -> str:
		"""
		Calculation hint logic.
  
		Returns:
		  Result of calculation_hint operation.
		"""
		return "Enter 4 sides"

	def _init_properties(self):
		self.properties = {
			'side_a': ShapeProperty(name='Side a', key='side_a', unit='units', formula=r'a'),
			'side_b': ShapeProperty(name='Side b', key='side_b', unit='units', formula=r'b'),
			'side_c': ShapeProperty(name='Side c', key='side_c', unit='units', formula=r'c'),
			'side_d': ShapeProperty(name='Side d', key='side_d', unit='units', formula=r'd'),
			'perimeter': ShapeProperty(name='Perimeter', key='perimeter', unit='units', readonly=True, formula=r'P = a + b + c + d'),
			'semiperimeter': ShapeProperty(name='Semiperimeter', key='semiperimeter', unit='units', readonly=True, formula=r's = \tfrac{a + b + c + d}{2}'),
			'area': ShapeProperty(name='Area', key='area', unit='units²', readonly=True, formula=r'A = \sqrt{(s-a)(s-b)(s-c)(s-d)}'),
			'circumradius': ShapeProperty(name='Circumradius', key='circumradius', unit='units', readonly=True, formula=r'R = \sqrt{\tfrac{(ab+cd)(ac+bd)(ad+bc)}{16A^2}}'),
		}

	def calculate_from_property(self, property_key: str, value: float) -> bool:
		"""
  Compute from property logic.
  
		Args:
		  property_key: Description of property_key.
		  value: Description of value.
  
		Returns:
		  Result of calculate_from_property operation.
		"""
		if property_key not in {'side_a', 'side_b', 'side_c', 'side_d'}:
			return False
		if value <= 0:
			return False
		previous = self.properties[property_key].value
		self.properties[property_key].value = value
		if not self._resolve():
			self.properties[property_key].value = previous
			return False
		return True

	def _resolve(self) -> bool:
		a = self.properties['side_a'].value
		b = self.properties['side_b'].value
		c = self.properties['side_c'].value
		d = self.properties['side_d'].value

		if None in (a, b, c, d):
			self.properties['perimeter'].value = None
			self.properties['semiperimeter'].value = None
			self.properties['area'].value = None
			self.properties['circumradius'].value = None
			self._points = None
			return True

		s = 0.5 * (a + b + c + d)  # type: ignore[reportOperatorIssue, reportUnknownVariableType]
		area_sq = (s - a) * (s - b) * (s - c) * (s - d)  # type: ignore[reportOperatorIssue, reportUnknownVariableType]
		if area_sq <= 0:
			return False
		area = math.sqrt(area_sq)
		self.properties['area'].value = area
		self.properties['perimeter'].value = 2 * s
		self.properties['semiperimeter'].value = s

		numerator = (a * b + c * d) * (a * c + b * d) * (a * d + b * c)  # type: ignore[reportOperatorIssue, reportUnknownVariableType]
		denominator = 16 * area_sq
		circumradius = math.sqrt(max(numerator / denominator, 0.0)) if denominator > EPSILON else None
		self.properties['circumradius'].value = circumradius

		if circumradius:
			thetas = []
			for side in (a, b, c, d):
				ratio = _clamp(side / (2 * circumradius), -1.0, 1.0)
				thetas.append(2 * math.asin(ratio))
			points: List[Tuple[float, float]] = []
			angle_cursor = 0.0
			for theta in thetas:
				x = circumradius * math.cos(angle_cursor)
				y = circumradius * math.sin(angle_cursor)
				points.append((x, y))
				angle_cursor += theta
			self._points = tuple(points)
		else:
			self._points = None

		return True

	def get_drawing_instructions(self) -> Dict:
		"""
  Retrieve drawing instructions logic.
  
		Returns:
		  Result of get_drawing_instructions operation.
		"""
		if not self._points:
			return {'type': 'empty'}
		return {'type': 'polygon', 'points': list(self._points)}

	def get_label_positions(self) -> List[Tuple[str, float, float]]:
		"""
  Retrieve label positions logic.
  
		Returns:
		  Result of get_label_positions operation.
		"""
		if not self._points:
			return []
		centroid = _polygon_centroid(self._points)
		area = self.properties['area'].value
		return [
			(f"A = {area:.4f}".rstrip('0').rstrip('.'), centroid[0], centroid[1])
		]


class TangentialQuadrilateralShape(GeometricShape):
	"""Quadrilateral admitting an incircle (Pitot condition)."""

	def __init__(self):
		"""
		init   logic.
  
		"""
		self._points: Optional[Tuple[Tuple[float, float], ...]] = None
		super().__init__()

	@property
	def name(self) -> str:
		"""
		Name logic.
  
		Returns:
		  Result of name operation.
		"""
		return "Tangential Quadrilateral"

	@property
	def description(self) -> str:
		"""
		Description logic.
  
		Returns:
		  Result of description operation.
		"""
		return "Tangential quadrilateral with incircle"

	@property
	def calculation_hint(self) -> str:
		"""
		Calculation hint logic.
  
		Returns:
		  Result of calculation_hint operation.
		"""
		return "Enter 3 sides (Pitot's Theorem)"

	def _init_properties(self):
		self.properties = {
			'side_a': ShapeProperty(name='Side a', key='side_a', unit='units', formula=r'a'),
			'side_b': ShapeProperty(name='Side b', key='side_b', unit='units', formula=r'b'),
			'side_c': ShapeProperty(name='Side c', key='side_c', unit='units', formula=r'c'),
			'side_d': ShapeProperty(name='Side d', key='side_d', unit='units', formula=r'd'),
			'inradius': ShapeProperty(name='Inradius', key='inradius', unit='units', formula=r'r'),
			'perimeter': ShapeProperty(name='Perimeter', key='perimeter', unit='units', readonly=True, formula=r'P = a + b + c + d'),
			'semiperimeter': ShapeProperty(name='Semiperimeter', key='semiperimeter', unit='units', readonly=True, formula=r's = \tfrac{a + b + c + d}{2}'),
			'area': ShapeProperty(name='Area', key='area', unit='units²', readonly=True, formula=r'A = r\,s \quad (a+c=b+d)'),
			'incircle_circumference': ShapeProperty(name='Incircle Circumference', key='incircle_circumference', unit='units', readonly=True, formula=r'C_{in} = 2\pi r'),
		}

	def calculate_from_property(self, property_key: str, value: float) -> bool:
		"""
  Compute from property logic.
  
		Args:
		  property_key: Description of property_key.
		  value: Description of value.
  
		Returns:
		  Result of calculate_from_property operation.
		"""
		if property_key not in {'side_a', 'side_b', 'side_c', 'side_d', 'inradius'}:
			return False
		if value <= 0:
			return False
		previous = self.properties[property_key].value
		self.properties[property_key].value = value
		if not self._resolve():
			self.properties[property_key].value = previous
			return False
		return True

	def _resolve(self) -> bool:
		a = self.properties['side_a'].value
		b = self.properties['side_b'].value
		c = self.properties['side_c'].value
		d = self.properties['side_d'].value
		r = self.properties['inradius'].value

		sides = [a, b, c, d]
		if all(val is not None for val in sides):
			if abs((a + c) - (b + d)) > 1e-4:  # type: ignore[reportOperatorIssue, reportUnknownArgumentType]
				return False
			s = 0.5 * (a + b + c + d)  # type: ignore[reportOperatorIssue, reportUnknownVariableType]
			self.properties['perimeter'].value = 2 * s
			self.properties['semiperimeter'].value = s
			if r:
				self.properties['area'].value = r * s
				self.properties['incircle_circumference'].value = 2 * math.pi * r
			else:
				self.properties['area'].value = None
				self.properties['incircle_circumference'].value = None
		else:
			self.properties['perimeter'].value = None
			self.properties['semiperimeter'].value = None
			self.properties['area'].value = None
			self.properties['incircle_circumference'].value = None

		# Simple symmetric depiction when enough info present.
		if all(val is not None for val in sides):
			base = max(a, c)  # type: ignore[reportArgumentType, reportUnknownVariableType]
			top = min(a, c)  # type: ignore[reportArgumentType, reportUnknownVariableType]
			height = r * 2 if r else min(a, c) / 2  # type: ignore[reportArgumentType, reportUnknownVariableType]
			offset = (base - top) / 2
			self._points = (
				(0.0, 0.0),
				(base, 0.0),
				(offset + top, height),
				(offset, height),
			)
		else:
			self._points = None

		return True

	def get_drawing_instructions(self) -> Dict:
		"""
  Retrieve drawing instructions logic.
  
		Returns:
		  Result of get_drawing_instructions operation.
		"""
		if not self._points:
			return {'type': 'empty'}
		return {'type': 'polygon', 'points': list(self._points)}

	def get_label_positions(self) -> List[Tuple[str, float, float]]:
		"""
  Retrieve label positions logic.
  
		Returns:
		  Result of get_label_positions operation.
		"""
		if not self._points:
			return []
		centroid = _polygon_centroid(self._points)
		area = self.properties['area'].value
		labels = []
		if area:
			labels.append((f"A = {area:.4f}".rstrip('0').rstrip('.'), centroid[0], centroid[1]))
		r = self.properties['inradius'].value
		if r:
			labels.append((f"r = {r:.4f}".rstrip('0').rstrip('.'), centroid[0], centroid[1] - 0.3))
		return labels


class BicentricQuadrilateralShape(GeometricShape):
	"""Quadrilateral that is both cyclic and tangential."""

	def __init__(self):
		"""
		init   logic.
  
		"""
		self._points: Optional[Tuple[Tuple[float, float], ...]] = None
		super().__init__()

	@property
	def name(self) -> str:
		"""
		Name logic.
  
		Returns:
		  Result of name operation.
		"""
		return "Bicentric Quadrilateral"

	@property
	def description(self) -> str:
		"""
		Description logic.
  
		Returns:
		  Result of description operation.
		"""
		return "Both Cyclic and Tangential (Fuss' Theorem)"

	@property
	def calculation_hint(self) -> str:
		"""
		Calculation hint logic.
  
		Returns:
		  Result of calculation_hint operation.
		"""
		return "Enter 2 distinct sides (a, b)"

	def _init_properties(self):
		self.properties = {
			'side_a': ShapeProperty(name='Side a', key='side_a', unit='units', formula=r'a'),
			'side_b': ShapeProperty(name='Side b', key='side_b', unit='units', formula=r'b'),
			'side_c': ShapeProperty(name='Side c', key='side_c', unit='units', formula=r'c'),
			'side_d': ShapeProperty(name='Side d', key='side_d', unit='units', formula=r'd'),
			'perimeter': ShapeProperty(name='Perimeter', key='perimeter', unit='units', readonly=True, formula=r'P = a + b + c + d'),
			'semiperimeter': ShapeProperty(name='Semiperimeter', key='semiperimeter', unit='units', readonly=True, formula=r's = \tfrac{a + b + c + d}{2}'),
			'area': ShapeProperty(name='Area', key='area', unit='units²', readonly=True, formula=r'A = \sqrt{(s-a)(s-b)(s-c)(s-d)}'),
			'inradius': ShapeProperty(name='Inradius', key='inradius', unit='units', readonly=True, formula=r'r = \tfrac{A}{s}'),
			'circumradius': ShapeProperty(name='Circumradius', key='circumradius', unit='units', readonly=True, formula=r'R = \sqrt{\tfrac{(ab+cd)(ac+bd)(ad+bc)}{16A^2}}'),
			'incircle_circumference': ShapeProperty(name='Incircle Circumference', key='incircle_circumference', unit='units', readonly=True, formula=r'C_{in} = 2\pi r'),
			'circumcircle_circumference': ShapeProperty(name='Circumcircle Circumference', key='circumcircle_circumference', unit='units', readonly=True, formula=r'C_{circ} = 2\pi R'),
		}

	def calculate_from_property(self, property_key: str, value: float) -> bool:
		"""
  Compute from property logic.
  
		Args:
		  property_key: Description of property_key.
		  value: Description of value.
  
		Returns:
		  Result of calculate_from_property operation.
		"""
		if property_key not in {'side_a', 'side_b', 'side_c', 'side_d'}:
			return False
		if value <= 0:
			return False
		previous = self.properties[property_key].value
		self.properties[property_key].value = value
		if not self._resolve():
			self.properties[property_key].value = previous
			return False
		return True

	def _resolve(self) -> bool:
		a = self.properties['side_a'].value
		b = self.properties['side_b'].value
		c = self.properties['side_c'].value
		d = self.properties['side_d'].value

		if None in (a, b, c, d):
			for key in ('perimeter', 'semiperimeter', 'area', 'inradius', 'circumradius',
						'incircle_circumference', 'circumcircle_circumference'):
				self.properties[key].value = None
			self._points = None
			return True

		if abs((a + c) - (b + d)) > 1e-4:  # type: ignore[reportOperatorIssue, reportUnknownArgumentType]
			return False

		s = 0.5 * (a + b + c + d)  # type: ignore[reportOperatorIssue, reportUnknownVariableType]
		area_sq = (s - a) * (s - b) * (s - c) * (s - d)  # type: ignore[reportOperatorIssue, reportUnknownVariableType]
		if area_sq <= 0:
			return False
		area = math.sqrt(area_sq)
		self.properties['perimeter'].value = 2 * s
		self.properties['semiperimeter'].value = s
		self.properties['area'].value = area
		inradius = area / s
		self.properties['inradius'].value = inradius
		self.properties['incircle_circumference'].value = 2 * math.pi * inradius

		numerator = (a * b + c * d) * (a * c + b * d) * (a * d + b * c)  # type: ignore[reportOperatorIssue, reportUnknownVariableType]
		denominator = 16 * area_sq
		circumradius = math.sqrt(max(numerator / denominator, 0.0)) if denominator > EPSILON else None
		if circumradius is None:
			return False
		self.properties['circumradius'].value = circumradius
		self.properties['circumcircle_circumference'].value = 2 * math.pi * circumradius

		# Use same construction as cyclic case for drawing
		thetas = []
		for side in (a, b, c, d):
			ratio = _clamp(side / (2 * circumradius), -1.0, 1.0)
			thetas.append(2 * math.asin(ratio))
		points: List[Tuple[float, float]] = []
		angle_cursor = 0.0
		for theta in thetas:
			x = circumradius * math.cos(angle_cursor)
			y = circumradius * math.sin(angle_cursor)
			points.append((x, y))
			angle_cursor += theta
		self._points = tuple(points)

		return True

	def get_drawing_instructions(self) -> Dict:
		"""
  Retrieve drawing instructions logic.
  
		Returns:
		  Result of get_drawing_instructions operation.
		"""
		if not self._points:
			return {'type': 'empty'}
		return {'type': 'polygon', 'points': list(self._points)}

	def get_label_positions(self) -> List[Tuple[str, float, float]]:
		"""
  Retrieve label positions logic.
  
		Returns:
		  Result of get_label_positions operation.
		"""
		if not self._points:
			return []
		centroid = _polygon_centroid(self._points)
		area = self.properties['area'].value
		return [
			(f"A = {area:.4f}".rstrip('0').rstrip('.'), centroid[0], centroid[1])
		]


class QuadrilateralSolverShape(GeometricShape):
	"""General quadrilateral solver using diagonals and included angle."""

	def __init__(self):
		"""
		init   logic.
  
		"""
		self._points: Optional[Tuple[Tuple[float, float], ...]] = None
		super().__init__()

	@property
	def name(self) -> str:
		"""
		Name logic.
  
		Returns:
		  Result of name operation.
		"""
		return "Quadrilateral Solver"

	@property
	def description(self) -> str:
		"""
		Description logic.
  
		Returns:
		  Result of description operation.
		"""
		return "Mix sides/diagonals with the angle between diagonals"

	def _init_properties(self):
		self.properties = {
			'side_a': ShapeProperty(name='Side a', key='side_a', unit='units', formula=r'a'),
			'side_b': ShapeProperty(name='Side b', key='side_b', unit='units', formula=r'b'),
			'side_c': ShapeProperty(name='Side c', key='side_c', unit='units', formula=r'c'),
			'side_d': ShapeProperty(name='Side d', key='side_d', unit='units', formula=r'd'),
			'diagonal_p': ShapeProperty(name='Diagonal p', key='diagonal_p', unit='units', formula=r'p'),
			'diagonal_q': ShapeProperty(name='Diagonal q', key='diagonal_q', unit='units', formula=r'q'),
			'diagonal_angle_deg': ShapeProperty(name='Angle Between Diagonals (°)', key='diagonal_angle_deg', unit='°', precision=2, formula=r'\phi'),
			'area': ShapeProperty(name='Area', key='area', unit='units²', readonly=True, formula=r'A = \tfrac{1}{2}pq\sin\phi'),
			'perimeter': ShapeProperty(name='Perimeter', key='perimeter', unit='units', readonly=True, formula=r'P = a + b + c + d'),
		}

	def calculate_from_property(self, property_key: str, value: float) -> bool:
		"""
  Compute from property logic.
  
		Args:
		  property_key: Description of property_key.
		  value: Description of value.
  
		Returns:
		  Result of calculate_from_property operation.
		"""
		if property_key not in {
			'side_a', 'side_b', 'side_c', 'side_d', 'diagonal_p', 'diagonal_q', 'diagonal_angle_deg'
		}:
			return False
		if value <= 0:
			return False
		previous = self.properties[property_key].value
		self.properties[property_key].value = value
		if not self._resolve():
			self.properties[property_key].value = previous
			return False
		return True

	def _resolve(self) -> bool:
		p = self.properties['diagonal_p'].value
		q = self.properties['diagonal_q'].value
		angle = self.properties['diagonal_angle_deg'].value

		if p and q and angle and not (0 < angle < 180):
			return False

		if p and q and angle:
			rad = math.radians(angle)
			area = 0.5 * p * q * math.sin(rad)
			self.properties['area'].value = area
			half_p = p / 2
			half_q = q / 2
			vec_q = (math.cos(rad), math.sin(rad))
			A = (-half_p, 0.0)
			C = (half_p, 0.0)
			B = (half_q * vec_q[0], half_q * vec_q[1])
			D = (-half_q * vec_q[0], -half_q * vec_q[1])
			self._points = (A, B, C, D)
		else:
			self.properties['area'].value = None
			self._points = None

		perim = 0.0
		missing = False
		for key in ('side_a', 'side_b', 'side_c', 'side_d'):
			val = self.properties[key].value
			if val is None:
				missing = True
				break
			perim += val
		self.properties['perimeter'].value = None if missing else perim
		return True

	def get_drawing_instructions(self) -> Dict:
		"""
  Retrieve drawing instructions logic.
  
		Returns:
		  Result of get_drawing_instructions operation.
		"""
		if not self._points:
			return {'type': 'empty'}
		return {'type': 'polygon', 'points': list(self._points)}

	def get_label_positions(self) -> List[Tuple[str, float, float]]:
		"""
  Retrieve label positions logic.
  
		Returns:
		  Result of get_label_positions operation.
		"""
		if not self._points:
			return []
		centroid = _polygon_centroid(self._points)
		area = self.properties['area'].value
		return [
			(f"A = {area:.4f}".rstrip('0').rstrip('.'), centroid[0], centroid[1] + 0.1)
		]


__all__ = [
	'ParallelogramShape',
	'RhombusShape',
	'TrapezoidShape',
	'IsoscelesTrapezoidShape',
	'KiteShape',
	'DeltoidShape',
	'CyclicQuadrilateralShape',
	'TangentialQuadrilateralShape',
	'BicentricQuadrilateralShape',
	'QuadrilateralSolverShape',
]
