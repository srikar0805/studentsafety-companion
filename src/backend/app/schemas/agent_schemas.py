from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from ..models import Coordinates, CampusLocation, TransportationMode

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
    transportation_mode: TransportationMode = TransportationMode.WALK
    needs_disambiguation: bool = False
    category: Optional[str] = None

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

class LocationOption(BaseModel):
    """A location option for disambiguation"""
    name: str
    address: Optional[str] = None
    coordinates: Coordinates
    distance_meters: Optional[float] = None
    category: str


class AgentDisambiguationResponse(BaseModel):
    """Response when disambiguation is needed"""
    response_type: str = "disambiguation"
    category: str
    question: str
    options: List[LocationOption]


class AgentRouteResponse(BaseModel):
    route_id: str
    eta: float
    risk: float
    confidence: float
    summary: str
    geometry: Dict[str, Any]
    label: str = ""  # "Safest Route (Recommended)", "Fastest Route", "Alternative Route"

class AgentFinalResponse(BaseModel):
    routes: List[AgentRouteResponse]
    explanation: str
    response_type: str = "routes"
