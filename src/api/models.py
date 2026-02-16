
from pydantic import BaseModel
from typing import List, Optional, Tuple

class RouteRequest(BaseModel):
    origin: Tuple[float, float] # (lat, lon)
    dest: Tuple[float, float]   # (lat, lon)
    mode: Optional[str] = "safe" # 'safe' or 'shortest'

class RouteResponse(BaseModel):
    path: List[Tuple[float, float]]
    distance: float
    risk_score: float

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    citations: List[str]

class AssetFeature(BaseModel):
    type: str # Feature
    geometry: dict # GeoJSON geometry
    properties: dict

class AssetCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[AssetFeature]
