from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from ..models import Coordinates

class AgentRequest(BaseModel):
    message: str


class AgentWeights(BaseModel):
    risk_weight: float = 0.7
    time_weight: float = 0.3

class IntentOutput(BaseModel):
    destination: str
    origin: Optional[str] = None
    priority: str = "balanced"
    time: str = "current"
    mode: str = "student"
    destination_coords: Optional[Coordinates] = None
    origin_coords: Optional[Coordinates] = None

class RouteAgentInput(BaseModel):
    origin: Coordinates
    destination: Coordinates
    risk_weight: float = 0.7
    time_weight: float = 0.3


class RouteCandidate(BaseModel):
    route_id: str
    geometry: Dict[str, Any]
    edges: List[int]
    eta_minutes: float

class RouteAgentOutput(BaseModel):
    routes: List[RouteCandidate]

class SafetyAgentInput(BaseModel):
    routes: List[Dict[str, Any]]
    time: str = "current"
    mode: str = "student"

class SafetyAgentResult(BaseModel):
    route_id: str
    incident_probability: float
    confidence: float

class SafetyAgentOutput(BaseModel):
    results: List[SafetyAgentResult]

class ContextAgentResult(BaseModel):
    route_id: str
    summary: str

class ContextAgentOutput(BaseModel):
    results: List[ContextAgentResult]

class AgentRouteResponse(BaseModel):
    route_id: str
    eta: float
    risk: float
    confidence: float
    summary: str
    geometry: Dict[str, Any]

class AgentFinalResponse(BaseModel):
    routes: List[AgentRouteResponse]
    explanation: str
