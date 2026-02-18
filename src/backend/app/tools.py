from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from .config import settings
from .models import Coordinates, Incident, LineString, Route, SafetyAnalysis
from .services.geocoding import GeocodingError, geocode_location
from .services.osrm import OsrmError, generate_routes
from .services.queries import (
    fetch_emergency_phones,
    fetch_incidents,
    fetch_traffic_stop_count,
    is_within_campus,
)
from .services.ranking import build_ranked_routes, rank_routes
from .services.safety import (
    analyze_route_safety,
    apply_temporal_weight,
    apply_time_multiplier,
    calculate_base_score,
    infrastructure_adjustment_components,
    patrol_frequency_label,
)
from .utils import parse_request_time, risk_level_label

logger = logging.getLogger("campus_dispatch")


def require_tool_auth(request: Request) -> None:
    if not settings.tool_api_key:
        return

    provided_key = request.headers.get("X-Tool-Api-Key")
    auth_header = request.headers.get("Authorization", "")
    bearer = auth_header.replace("Bearer ", "", 1) if auth_header.startswith("Bearer ") else ""

    if provided_key == settings.tool_api_key or bearer == settings.tool_api_key:
        return

    raise HTTPException(status_code=401, detail="Unauthorized")


router = APIRouter(prefix="/tools", tags=["Tools"], dependencies=[Depends(require_tool_auth)])


class GeocodeInput(BaseModel):
    location_name: str


class ValidateInput(BaseModel):
    coordinates: Coordinates


class RoutesInput(BaseModel):
    origin: Coordinates
    destination: Coordinates
    alternatives: int | None = None


class CrimeInput(BaseModel):
    route_geometry: LineString
    radius_m: int = 500
    days_back: int = 30


class TrafficInput(BaseModel):
    route_geometry: LineString
    radius_m: int = 500
    days_back: int = 90


class InfrastructureInput(BaseModel):
    route_geometry: LineString
    radius_m: int = 100


class LightingSegment(BaseModel):
    geometry: LineString
    quality: str = "moderate"


class Building(BaseModel):
    name: str
    type: str
    location: Coordinates


class InfrastructurePayload(BaseModel):
    emergency_phones: list[Coordinates] = Field(default_factory=list)
    lighting_segments: list[LightingSegment] = Field(default_factory=list)
    sidewalks: list[LineString] = Field(default_factory=list)
    buildings: list[Building] = Field(default_factory=list)
    lighting_quality: str = "moderate"
    patrol_frequency: str = "moderate"


class RiskInput(BaseModel):
    incidents: list[Incident] = Field(default_factory=list)
    infrastructure: InfrastructurePayload
    time: str = "current"
    user_mode: str = "student"


class RankInput(BaseModel):
    routes: list[Route]
    safety_analyses: list[SafetyAnalysis]
    priority: str = "safety"
    time: str = "current"


@router.post("/geocode")
async def geocode_tool(payload: GeocodeInput):
    try:
        return geocode_location(payload.location_name)
    except GeocodingError as exc:
        logger.warning("Geocoding failed", exc_info=exc)
        raise HTTPException(status_code=400, detail="Geocoding failed") from exc


@router.post("/validate")
async def validate_tool(payload: ValidateInput) -> dict:
    return {"within_campus": is_within_campus(payload.coordinates)}


@router.post("/routes")
async def routes_tool(payload: RoutesInput) -> dict:
    try:
        routes = generate_routes(payload.origin, payload.destination, payload.alternatives)
        return {"routes": [route.model_dump() for route in routes]}
    except OsrmError as exc:
        logger.warning("OSRM route generation failed", exc_info=exc)
        raise HTTPException(status_code=502, detail="Routing service unavailable") from exc


@router.post("/crime")
async def crime_tool(payload: CrimeInput) -> dict:
    incidents = fetch_incidents(payload.route_geometry, payload.radius_m, payload.days_back)
    return {"incidents": [incident.model_dump() for incident in incidents]}


@router.post("/traffic")
async def traffic_tool(payload: TrafficInput) -> dict:
    stop_count = fetch_traffic_stop_count(payload.route_geometry, payload.radius_m, payload.days_back)
    patrol = patrol_frequency_label(stop_count)
    return {
        "location_area": "campus",
        "stop_count": stop_count,
        "time_distribution": {},
        "patrol_frequency": patrol,
    }


@router.post("/infrastructure")
async def infrastructure_tool(payload: InfrastructureInput) -> dict:
    phones = fetch_emergency_phones(payload.route_geometry, payload.radius_m)
    return {
        "emergency_phones": [phone.model_dump() for phone in phones],
        "lighting_segments": [],
        "sidewalks": [],
        "buildings": [],
        "lighting_quality": "moderate",
    }


@router.post("/risk")
async def risk_tool(payload: RiskInput) -> dict:
    try:
        current_time = parse_request_time(payload.time)
    except Exception:
        current_time = datetime.now(timezone.utc)

    incidents = payload.incidents
    infra = payload.infrastructure

    base_score = calculate_base_score(incidents)
    temporal_score = apply_temporal_weight(incidents, current_time)
    time_multiplier = 2.0 if current_time.hour >= 22 or current_time.hour < 6 else 1.0
    time_adjusted = apply_time_multiplier(temporal_score, current_time)

    components = infrastructure_adjustment_components(
        emergency_phones=len(infra.emergency_phones),
        lighting_quality=infra.lighting_quality,
        patrol_frequency=infra.patrol_frequency,
    )
    final_score = max(0.0, min(100.0, time_adjusted + components["total_adjustment"]))

    analysis = analyze_route_safety(
        incidents=incidents,
        emergency_phones=len(infra.emergency_phones),
        lighting_quality=infra.lighting_quality,
        patrol_frequency=infra.patrol_frequency,
        user_mode=payload.user_mode,
        current_time=current_time,
    )

    return {
        "risk_score": final_score,
        "risk_level": risk_level_label(final_score),
        "analysis": analysis.model_dump(),
        "breakdown": {
            "base_score": base_score,
            "temporal_adjustment": temporal_score - base_score,
            "time_of_day_multiplier": time_multiplier,
            "infrastructure_adjustment": components["total_adjustment"],
            "patrol_adjustment": components["patrol_adjustment"],
        },
    }


@router.post("/rank")
async def rank_tool(payload: RankInput) -> dict:
    try:
        current_time = parse_request_time(payload.time)
    except Exception:
        current_time = datetime.now(timezone.utc)

    ranked_indices = rank_routes(
        payload.routes,
        payload.safety_analyses,
        payload.priority,
        current_hour=current_time.hour,
    )
    ranked_routes = build_ranked_routes(payload.routes, payload.safety_analyses, ranked_indices)
    return {"routes": [route.model_dump() for route in ranked_routes]}
