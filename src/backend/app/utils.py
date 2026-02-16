from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable
from dateutil import parser

from .models import Coordinates, LineString


def parse_request_time(value: str) -> datetime:
    if value.strip().lower() == "current":
        return datetime.now(timezone.utc)
    parsed = parser.parse(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def linestring_to_wkt(line: LineString) -> str:
    parts = [f"{lon} {lat}" for lon, lat in line.coordinates]
    return f"LINESTRING({', '.join(parts)})"


def to_coordinates(point: tuple[float, float]) -> Coordinates:
    lon, lat = point
    return Coordinates(latitude=lat, longitude=lon)


def normalize_incident_type(value: str | None) -> str:
    if not value:
        return "Unknown"
    return value.strip().title()


def risk_level_label(score: float) -> str:
    if score <= 20:
        return "Very Safe"
    if score <= 40:
        return "Safe"
    if score <= 60:
        return "Moderate"
    if score <= 80:
        return "Caution"
    return "High Risk"


def build_waypoints(coords: Iterable[Coordinates]) -> list[Coordinates]:
    return list(coords)
