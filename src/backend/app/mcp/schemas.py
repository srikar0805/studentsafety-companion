"""
MCP Tool Endpoints

These endpoints are called BY Archia agents (not by the frontend).
Archia tools point to these URLs.
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class RouteToolInput(BaseModel):
    origin: Dict[str, float]  # {latitude: float, longitude: float}
    destination: Dict[str, float]
    risk_weight: float = 0.7
    time_weight: float = 0.3


class RiskToolInput(BaseModel):
    routes: List[Dict[str, Any]]
    time: str = "current"
    mode: str = "student"


class RAGToolInput(BaseModel):
    query: str
    top_k: int = 3


class ShuttleToolInput(BaseModel):
    location: Dict[str, float]
    radius_m: int = 500


class TrafficToolInput(BaseModel):
    geometry: Dict[str, Any]  # LineString
    radius_m: int = 500
    days_back: int = 90
