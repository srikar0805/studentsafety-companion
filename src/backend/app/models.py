from __future__ import annotations

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    latitude: float
    longitude: float


class LineString(BaseModel):
    type: Literal["LineString"] = "LineString"
    coordinates: list[tuple[float, float]]


class Route(BaseModel):
    id: str
    geometry: LineString
    distance_meters: float
    duration_seconds: float
    waypoints: list[Coordinates]


class Incident(BaseModel):
    id: str
    type: str
    location: Coordinates
    date: datetime
    description: str | None = None
    severity: Literal["low", "medium", "high"] | None = None


class SafetyTip(BaseModel):
    type: Literal["warning", "advisory"]
    message: str
    trigger_crime: str


class SafetyAnalysis(BaseModel):
    risk_score: float
    risk_level: Literal["Very Safe", "Safe", "Moderate", "Caution", "High Risk"]
    incident_count: int
    recent_incidents: list[Incident]
    emergency_phones: int
    lighting_quality: Literal["good", "moderate", "poor"]
    patrol_frequency: Literal["high", "moderate", "low"]
    actionable_tips: list[SafetyTip]
    concerns: list[str]
    positives: list[str]
    contributing_factors: list[str]


class RankedRoute(BaseModel):
    rank: int
    route: Route
    safety_analysis: SafetyAnalysis
    duration_minutes: int
    distance_meters: int
    safety_improvement_percent: int
    time_tradeoff_minutes: int
    explanation: str


class Recommendation(BaseModel):
    routes: list[RankedRoute]
    primary_recommendation: RankedRoute
    explanation: str
    comparison: str


class RouteRequest(BaseModel):
    origin: Coordinates | str
    destination: Coordinates | str
    user_mode: Literal["student", "community"] = "student"
    priority: Literal["safety", "speed", "balanced"] = "safety"
    time: str = "current"
    concerns: list[str] = Field(default_factory=list)
    force_refresh: bool = False


class ErrorResponse(BaseModel):
    error: bool = True
    error_code: str
    user_message: str
    suggestions: list[str]
    retry_after: int | None = None


class RoutesResponse(BaseModel):
    request_id: str
    recommendation: Recommendation
    incidents: list[Incident]
    emergency_phones: list[Coordinates]
